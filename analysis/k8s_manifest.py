"""Validate and normalize Kubernetes manifests before write/apply."""
from __future__ import annotations

import copy
import os
import shutil
import subprocess
import time
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent


def baseline_hpa_path(hpa_yaml_path: Path) -> Path:
    p = hpa_yaml_path.parent / f"{hpa_yaml_path.stem}.baseline.yaml"
    return p if p.exists() else hpa_yaml_path


def baseline_deployment_path(deployment_yaml_path: Path) -> Path:
    p = deployment_yaml_path.parent / f"{deployment_yaml_path.stem}.baseline.yaml"
    return p if p.exists() else deployment_yaml_path


def up_demo_thin_baseline_paths(
    deployment_yaml_path: Path,
    hpa_yaml_path: Path,
) -> tuple[Path, Path]:
    """Immutable thin web baseline for up_demo (1 repl, low CPU/mem) — not down_demo fat baseline."""
    dep_env = os.environ.get("UP_DEMO_THIN_DEPLOYMENT_YAML", "").strip()
    hpa_env = os.environ.get("UP_DEMO_THIN_HPA_YAML", "").strip()
    if dep_env and hpa_env:
        return Path(dep_env), Path(hpa_env)
    thin_dep = deployment_yaml_path.parent / (
        f"{deployment_yaml_path.stem}.up-demo-thin.baseline.yaml"
    )
    thin_hpa = hpa_yaml_path.parent / f"{hpa_yaml_path.stem}.up-demo-thin.baseline.yaml"
    return thin_dep, thin_hpa


def align_squeeze_hpa_to_deployment_replicas(
    deployment_yaml_path: Path,
    hpa_yaml_path: Path,
) -> bool:
    """Cap HPA min/max to deployment spec.replicas so scale-down is not undone by HPA."""
    if not deployment_yaml_path.exists() or not hpa_yaml_path.exists():
        return False
    try:
        dep_doc = yaml.safe_load(deployment_yaml_path.read_text())
        hpa_doc = yaml.safe_load(hpa_yaml_path.read_text())
    except Exception:
        return False
    if not isinstance(dep_doc, dict) or dep_doc.get("kind") != "Deployment":
        return False
    if not isinstance(hpa_doc, dict) or hpa_doc.get("kind") != "HorizontalPodAutoscaler":
        return False
    repl = int((dep_doc.get("spec") or {}).get("replicas") or 0)
    if repl < 1:
        return False
    spec = hpa_doc.setdefault("spec", {})
    min_r = int(spec.get("minReplicas") or 1)
    max_r = int(spec.get("maxReplicas") or repl)
    new_min = min(min_r, repl)
    new_max = min(max_r, repl)
    changed = new_min != min_r or new_max != max_r
    spec["minReplicas"] = new_min
    spec["maxReplicas"] = new_max
    if changed:
        dump_kw = {
            "sort_keys": False,
            "default_flow_style": False,
            "allow_unicode": True,
        }
        hpa_yaml_path.write_text(yaml.safe_dump(hpa_doc, **dump_kw))
        print(
            f"[squeeze] align HPA to deployment replicas={repl}: "
            f"minReplicas={new_min} maxReplicas={new_max}",
            flush=True,
        )
    return changed


def _metric_v2_ok(metric: object) -> bool:
    if not isinstance(metric, dict):
        return False
    if metric.get("type") != "Resource":
        return False
    res = metric.get("resource")
    if not isinstance(res, dict):
        return False
    target = res.get("target")
    if not isinstance(target, dict):
        return False
    return target.get("type") == "Utilization" and target.get("averageUtilization") is not None


def merge_llm_hpa_onto_baseline(llm_yaml: str, baseline_yaml: str) -> str:
    """Keep baseline HPA shape (autoscaling/v2); copy safe spec fields from the LLM doc."""
    llm_doc = yaml.safe_load(llm_yaml)
    base_doc = yaml.safe_load(baseline_yaml)
    if not isinstance(base_doc, dict) or base_doc.get("kind") != "HorizontalPodAutoscaler":
        return llm_yaml
    if not isinstance(llm_doc, dict) or llm_doc.get("kind") != "HorizontalPodAutoscaler":
        return baseline_yaml
    out = copy.deepcopy(base_doc)
    out.setdefault("apiVersion", "autoscaling/v2")
    out["kind"] = "HorizontalPodAutoscaler"
    lmeta = llm_doc.get("metadata") or {}
    bmeta = out.setdefault("metadata", {})
    for key in ("name", "namespace", "labels", "annotations"):
        if key in lmeta and lmeta[key] is not None:
            bmeta[key] = lmeta[key]
    lspec = llm_doc.get("spec") or {}
    ospec = out.setdefault("spec", {})
    for key in ("minReplicas", "maxReplicas"):
        if key in lspec and lspec[key] is not None:
            ospec[key] = int(lspec[key])
    if isinstance(lspec.get("behavior"), dict):
        ospec["behavior"] = lspec["behavior"]
    metrics = lspec.get("metrics")
    if isinstance(metrics, list) and metrics and all(_metric_v2_ok(m) for m in metrics):
        ospec["metrics"] = metrics
    min_r = int(ospec.get("minReplicas") or 1)
    max_r = int(ospec.get("maxReplicas") or min_r)
    if max_r < min_r:
        ospec["maxReplicas"] = min_r
    return yaml.safe_dump(out, sort_keys=False, default_flow_style=False, allow_unicode=True)


def kubectl_validate_yaml(yaml_text: str, *, repo_root: Path | None = None) -> str | None:
    """Server dry-run via kubectl; return error text or None if valid / kubectl unavailable."""
    if not shutil.which("kubectl"):
        return None
    root = repo_root or REPO_ROOT
    proc = subprocess.run(
        ["kubectl", "apply", "--dry-run=server", "-f", "-"],
        input=yaml_text,
        cwd=root,
        capture_output=True,
        text=True,
    )
    if proc.returncode == 0:
        return None
    return (proc.stderr or proc.stdout or "kubectl dry-run failed").strip()


def sync_managed_yaml_to_observed_scale(
    deployment_yaml_path: Path,
    hpa_yaml_path: Path,
    *,
    live_replicas: int,
    live_replicas_max: int | None = None,
    allow_scale_up: bool = True,
) -> list[str]:
    """
    Align on-disk managed YAML with live scale (HPA often runs above spec.replicas in the file).
    When allow_scale_up=False (DOWN squeeze), only decrease replicas/maxReplicas in the file —
    never rewrite a deliberate cap upward because the cluster briefly scaled up during k6.
    Returns human-readable notes when something was updated.
    """
    notes: list[str] = []
    live = int(live_replicas)
    if live < 1:
        return notes
    live_max = int(live_replicas_max if live_replicas_max is not None else live)
    dump_kw = {
        "default_flow_style": False,
        "sort_keys": False,
        "allow_unicode": True,
    }

    if deployment_yaml_path.exists():
        doc = yaml.safe_load(deployment_yaml_path.read_text())
        if isinstance(doc, dict) and doc.get("kind") == "Deployment":
            spec = doc.setdefault("spec", {})
            old = int(spec.get("replicas") or 0)
            if allow_scale_up:
                target = live
            else:
                target = live if old < 1 else min(old, live)
            if old != target:
                spec["replicas"] = target
                deployment_yaml_path.write_text(yaml.dump(doc, **dump_kw))
                direction = "observed" if allow_scale_up else "observed_down_only"
                notes.append(f"sync.deployment_replicas: {old} -> {target} ({direction})")

    if hpa_yaml_path.exists():
        hpa = yaml.safe_load(hpa_yaml_path.read_text())
        if isinstance(hpa, dict) and hpa.get("kind") == "HorizontalPodAutoscaler":
            spec = hpa.setdefault("spec", {})
            max_r = int(spec.get("maxReplicas") or 0)
            min_r = int(spec.get("minReplicas") or 1)
            if allow_scale_up:
                new_max = max(max_r, live_max, min_r)
            else:
                new_max = min(max_r, live_max) if max_r > 0 else live_max
                new_max = max(min_r, new_max)
            if max_r != new_max:
                spec["maxReplicas"] = new_max
                hpa_yaml_path.write_text(yaml.dump(hpa, **dump_kw))
                direction = "observed_max" if allow_scale_up else "observed_max_down_only"
                notes.append(f"sync.hpa_maxReplicas: {max_r} -> {new_max} ({direction})")
    return notes


def align_llm_deployment_replicas_for_squeeze(
    result: dict,
    experiment: dict,
    *,
    deployment_yaml_path: Path | None = None,
    hpa_yaml_path: Path | None = None,
) -> bool:
    """DOWN + PASS: cap deployment and HPA to live-1 so HPA cannot scale back up during the next test."""
    return cap_squeeze_down_replicas_and_hpa(
        result,
        experiment,
        deployment_yaml_path=deployment_yaml_path,
        hpa_yaml_path=hpa_yaml_path,
    )


def clamp_llm_squeeze_replicas_to_one_step(
    result: dict,
    experiment: dict,
    *,
    deployment_yaml_path: Path | None = None,
    hpa_yaml_path: Path | None = None,
) -> bool:
    """Pure-LLM guard: keep LLM CPU/mem; only enforce replica step <= 1 vs live scale."""
    if bool((experiment.get("failure") or {}).get("failed")):
        return False
    observed = experiment.get("observed") or {}
    live = int(observed.get("replicas") or 0)
    live_max = int(observed.get("replicas_max") or 0)
    live = max(live, live_max)
    if live < 2:
        return False
    target = max(1, live - 1)
    dump_kw = {
        "sort_keys": False,
        "default_flow_style": False,
        "allow_unicode": True,
    }
    changed = False
    notes: list[str] = []

    dep_new = (result.get("deployment_yaml_new") or "").strip()
    dep_doc: dict | None = None
    if dep_new:
        try:
            dep_doc = yaml.safe_load(dep_new)
        except Exception:
            dep_doc = None
    if dep_doc is None and deployment_yaml_path and deployment_yaml_path.exists():
        try:
            dep_doc = yaml.safe_load(deployment_yaml_path.read_text())
        except Exception:
            dep_doc = None
    if isinstance(dep_doc, dict) and dep_doc.get("kind") == "Deployment":
        spec = dep_doc.setdefault("spec", {})
        proposed = int(spec.get("replicas") or live)
        new_rep = proposed
        if proposed >= live:
            new_rep = target
        elif proposed < target:
            new_rep = target
        if new_rep != proposed:
            notes.append(f"deployment.replicas_clamp: llm={proposed} -> {new_rep} (live={live})")
        if new_rep != int(spec.get("replicas") or 0):
            changed = True
        spec["replicas"] = new_rep
        result["deployment_yaml_new"] = yaml.safe_dump(dep_doc, **dump_kw)

    hpa_new = (result.get("hpa_yaml_new") or "").strip()
    hpa_doc: dict | None = None
    if hpa_new:
        try:
            hpa_doc = yaml.safe_load(hpa_new)
        except Exception:
            hpa_doc = None
    if hpa_doc is None and hpa_yaml_path and hpa_yaml_path.exists():
        try:
            hpa_doc = yaml.safe_load(hpa_yaml_path.read_text())
        except Exception:
            hpa_doc = None
    dep_rep = target
    if isinstance(dep_doc, dict):
        dep_rep = int((dep_doc.get("spec") or {}).get("replicas") or target)
    if isinstance(hpa_doc, dict) and hpa_doc.get("kind") == "HorizontalPodAutoscaler":
        spec = hpa_doc.setdefault("spec", {})
        min_r = int(spec.get("minReplicas") or 1)
        max_r = int(spec.get("maxReplicas") or dep_rep)
        new_max = min(max_r, dep_rep)
        new_min = min(min_r, new_max)
        if new_max != max_r or new_min != min_r:
            changed = True
            notes.append(f"hpa.maxReplicas: {max_r} -> {new_max} (match deployment={dep_rep})")
        spec["maxReplicas"] = new_max
        spec["minReplicas"] = new_min
        result["hpa_yaml_new"] = yaml.safe_dump(hpa_doc, **dump_kw)

    if notes:
        ev = list(result.get("evidence") or [])
        ev.append(f"guard.llm_replica_step ({'; '.join(notes)})")
        result["evidence"] = ev
    return changed


def cap_squeeze_down_replicas_and_hpa(
    result: dict,
    experiment: dict,
    *,
    deployment_yaml_path: Path | None = None,
    hpa_yaml_path: Path | None = None,
) -> bool:
    """
    After a PASS with scaling_hint DOWN/HOLD, force spec.replicas and maxReplicas to observed-1
    so the next iteration actually runs with fewer pods (LLM often writes spec.replicas=2 while live=3).
    """
    if experiment.get("analysis_goal") != "efficiency":
        return False
    if experiment.get("mode") != "squeeze":
        return False
    if bool((experiment.get("failure") or {}).get("failed")):
        return False
    hint = experiment.get("scaling_hint")
    if hint not in {"DOWN", "HOLD"}:
        return False

    observed = experiment.get("observed") or {}
    live = int(observed.get("replicas") or 0)
    live_max = int(observed.get("replicas_max") or 0)
    live = max(live, live_max)
    if live < 2:
        return False

    target = max(1, live - 1)  # at most one replica step down per iteration
    dump_kw = {
        "sort_keys": False,
        "default_flow_style": False,
        "allow_unicode": True,
    }
    changed = False
    notes: list[str] = []

    dep_new = (result.get("deployment_yaml_new") or "").strip()
    dep_doc: dict | None = None
    if dep_new:
        try:
            dep_doc = yaml.safe_load(dep_new)
        except Exception:
            dep_doc = None
    if dep_doc is None and deployment_yaml_path and deployment_yaml_path.exists():
        try:
            dep_doc = yaml.safe_load(deployment_yaml_path.read_text())
        except Exception:
            dep_doc = None
    if isinstance(dep_doc, dict) and dep_doc.get("kind") == "Deployment":
        spec = dep_doc.setdefault("spec", {})
        old = int(spec.get("replicas") or live)
        if old < target:
            notes.append(f"deployment.replicas_clamp: llm={old} -> {target} (max one step from live={live})")
        spec["replicas"] = target
        if old != target:
            changed = True
            notes.append(f"deployment.replicas: {old} -> {target}")
        elif live > target:
            meta = dep_doc.setdefault("metadata", {})
            ann = dict(meta.get("annotations") or {})
            ann["squeeze/reconcile-ts"] = str(int(time.time()))
            meta["annotations"] = ann
            changed = True
            notes.append(f"deployment.reconcile: live={live} target={target}")
        result["deployment_yaml_new"] = yaml.safe_dump(dep_doc, **dump_kw)

    hpa_new = (result.get("hpa_yaml_new") or "").strip()
    hpa_doc: dict | None = None
    if hpa_new:
        try:
            hpa_doc = yaml.safe_load(hpa_new)
        except Exception:
            hpa_doc = None
    if hpa_doc is None and hpa_yaml_path and hpa_yaml_path.exists():
        try:
            hpa_doc = yaml.safe_load(hpa_yaml_path.read_text())
        except Exception:
            hpa_doc = None
    if isinstance(hpa_doc, dict) and hpa_doc.get("kind") == "HorizontalPodAutoscaler":
        spec = hpa_doc.setdefault("spec", {})
        min_r = int(spec.get("minReplicas") or 1)
        max_r = int(spec.get("maxReplicas") or target)
        new_max = max(min_r, min(max_r, target))
        spec["maxReplicas"] = new_max
        if max_r != new_max:
            changed = True
            notes.append(f"hpa.maxReplicas: {max_r} -> {new_max}")
        elif live > target:
            meta = hpa_doc.setdefault("metadata", {})
            ann = dict(meta.get("annotations") or {})
            ann["squeeze/reconcile-ts"] = str(int(time.time()))
            meta["annotations"] = ann
            changed = True
            notes.append(f"hpa.reconcile: live={live} target={target}")
        result["hpa_yaml_new"] = yaml.safe_dump(hpa_doc, **dump_kw)

    if changed or notes:
        ev = list(result.get("evidence") or [])
        ev.append(f"guard.squeeze_replica_cap live={live} target={target} ({'; '.join(notes)})")
        result["evidence"] = ev
    return changed


def prepare_hpa_yaml_new(
    hpa_yaml_new: str,
    *,
    hpa_yaml_path: Path,
    repo_root: Path | None = None,
) -> tuple[str, str | None]:
    """
    Parse, merge onto baseline, kubectl-validate.
    Returns (yaml_to_write, warning_or_none). Empty yaml_to_write means reject.
    """
    try:
        yaml.safe_load(hpa_yaml_new)
    except Exception as e:
        return "", f"hpa_yaml_new invalid YAML: {e}"

    baseline_path = baseline_hpa_path(hpa_yaml_path)
    baseline_text = baseline_path.read_text() if baseline_path.exists() else ""
    merged = merge_llm_hpa_onto_baseline(hpa_yaml_new, baseline_text or hpa_yaml_new)

    err = kubectl_validate_yaml(merged, repo_root=repo_root)
    if err:
        return "", f"hpa_yaml_new failed kubectl validation: {err}"
    return merged, None
