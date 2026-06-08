"""Apply current YAMLs with kubectl and wait for rollout."""
import json
import math
import os
import shutil
import subprocess
import time
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent


def _coerce_hpa_file(hpa_yaml_path: Path, repo_root: Path) -> None:
    """Merge/fix HPA on disk before apply (handles prior bad LLM writes)."""
    if not hpa_yaml_path.exists():
        return
    from analysis.k8s_manifest import baseline_hpa_path, prepare_hpa_yaml_new

    prepared, _ = prepare_hpa_yaml_new(
        hpa_yaml_path.read_text(),
        hpa_yaml_path=hpa_yaml_path,
        repo_root=repo_root,
    )
    if prepared:
        hpa_yaml_path.write_text(prepared)
        return
    baseline = baseline_hpa_path(hpa_yaml_path)
    if baseline.exists():
        print("[kubectl] restoring HPA YAML from baseline", flush=True)
        hpa_yaml_path.write_text(baseline.read_text())


def _kubectl_get_json(kind: str, name: str, namespace: str) -> dict:
    out = subprocess.check_output(
        ["kubectl", "-n", namespace, "get", kind, name, "-o", "json"],
        text=True,
    )
    return json.loads(out)


def _kubectl_patch_hpa_replica_cap(
    *,
    hpa_name: str,
    namespace: str,
    max_replicas: int,
) -> None:
    """Merge-patch live HPA so it cannot scale above deployment target (squeeze DOWN)."""
    max_replicas = max(1, int(max_replicas))
    patch = json.dumps(
        {"spec": {"maxReplicas": max_replicas, "minReplicas": min(1, max_replicas)}}
    )
    subprocess.run(
        [
            "kubectl",
            "-n",
            namespace,
            "patch",
            "hpa",
            hpa_name,
            "--type=merge",
            "-p",
            patch,
        ],
        check=True,
    )
    print(
        f"[squeeze] patched hpa/{hpa_name} maxReplicas={max_replicas} (live)",
        flush=True,
    )


def kubectl_apply(
    deployment_yaml_path: Path,
    hpa_yaml_path: Path,
    repo_root: Path | None = None,
    *,
    require_hpa: bool = False,
    align_hpa_to_deployment: bool = True,
) -> None:
    """Apply deployment + HPA together so HPA cannot scale up between two applies."""
    from analysis.k8s_manifest import align_squeeze_hpa_to_deployment_replicas

    root = repo_root or REPO_ROOT
    if hpa_yaml_path.exists():
        _coerce_hpa_file(hpa_yaml_path, root)
        if align_hpa_to_deployment:
            align_squeeze_hpa_to_deployment_replicas(deployment_yaml_path, hpa_yaml_path)
    apply_args = ["kubectl", "apply", "-f", str(deployment_yaml_path)]
    if hpa_yaml_path.exists():
        apply_args.extend(["-f", str(hpa_yaml_path)])
    print("kubectl apply (deployment+hpa)...", flush=True)
    proc = subprocess.run(apply_args, cwd=root, capture_output=True, text=True)
    if proc.returncode == 0:
        if proc.stdout:
            print(proc.stdout.strip(), flush=True)
        return
    err = (proc.stderr or proc.stdout or "kubectl apply failed").strip()
    if require_hpa or hpa_yaml_path.exists():
        raise subprocess.CalledProcessError(proc.returncode, proc.args, proc.stdout, proc.stderr)
    print(f"[kubectl] apply failed (deployment only path): {err}", flush=True)


def _resolve_baseline_yaml_paths(
    deployment_yaml_path: Path,
    hpa_yaml_path: Path,
) -> tuple[Path, Path]:
    from analysis.k8s_manifest import baseline_deployment_path, baseline_hpa_path

    dep_env = os.environ.get("BASELINE_DEPLOYMENT_YAML", "").strip()
    hpa_env = os.environ.get("BASELINE_HPA_YAML", "").strip()
    baseline_dep = Path(dep_env) if dep_env else baseline_deployment_path(deployment_yaml_path)
    baseline_hpa = Path(hpa_env) if hpa_env else baseline_hpa_path(hpa_yaml_path)
    return baseline_dep, baseline_hpa


def reset_managed_web_yaml_to_baseline(
    deployment_yaml_path: Path,
    hpa_yaml_path: Path,
) -> None:
    """Copy immutable baseline YAML onto managed paths (no kubectl)."""
    baseline_dep, baseline_hpa = _resolve_baseline_yaml_paths(
        deployment_yaml_path, hpa_yaml_path
    )
    if not baseline_dep.exists() or not baseline_hpa.exists():
        raise FileNotFoundError(
            f"baseline YAML missing: {baseline_dep} / {baseline_hpa}"
        )
    shutil.copy(baseline_dep, deployment_yaml_path)
    shutil.copy(baseline_hpa, hpa_yaml_path)


def reset_managed_web_yaml_to_up_demo_thin(
    deployment_yaml_path: Path,
    hpa_yaml_path: Path,
) -> None:
    """Copy up_demo thin baseline onto managed paths (no kubectl)."""
    from analysis.k8s_manifest import up_demo_thin_baseline_paths

    thin_dep, thin_hpa = up_demo_thin_baseline_paths(
        deployment_yaml_path, hpa_yaml_path
    )
    if not thin_dep.exists() or not thin_hpa.exists():
        raise FileNotFoundError(
            f"up_demo thin baseline YAML missing: {thin_dep} / {thin_hpa}"
        )
    shutil.copy(thin_dep, deployment_yaml_path)
    shutil.copy(thin_hpa, hpa_yaml_path)


def apply_managed_web_baseline(
    *,
    deployment_yaml_path: Path,
    hpa_yaml_path: Path,
    deployment_name: str,
    namespace: str,
    repo_root: Path | None = None,
    timeout_s: int = 300,
) -> None:
    """Reset managed web YAML from baseline and reconcile live deployment + HPA."""
    root = repo_root or REPO_ROOT
    print(
        "[squeeze-compare] applying managed web baseline (deployment + hpa)...",
        flush=True,
    )
    reset_managed_web_yaml_to_baseline(deployment_yaml_path, hpa_yaml_path)
    _coerce_hpa_file(hpa_yaml_path, root)
    kubectl_apply(
        deployment_yaml_path,
        hpa_yaml_path,
        root,
        align_hpa_to_deployment=False,
    )
    wait_rollout(
        deployment_name=deployment_name,
        namespace=namespace,
        timeout_s=timeout_s,
    )
    yaml_replicas = 0
    try:
        dep_doc = yaml.safe_load(deployment_yaml_path.read_text())
        yaml_replicas = int((dep_doc.get("spec") or {}).get("replicas") or 0)
    except Exception:
        yaml_replicas = 0
    if os.environ.get("SQUEEZE_WAIT_REPLICAS_STEADY", "1").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    ):
        wait_for_deployment_replicas(
            deployment_name=deployment_name,
            namespace=namespace,
            yaml_replicas=yaml_replicas or None,
            timeout_s=timeout_s,
        )
    print("[squeeze-compare] managed web baseline ready.", flush=True)


def ensure_up_demo_thin_baseline(
    *,
    deployment_yaml_path: Path,
    hpa_yaml_path: Path,
    deployment_name: str,
    namespace: str,
    repo_root: Path | None = None,
    timeout_s: int = 300,
) -> None:
    """Reset managed web YAML from up_demo thin baseline (1 repl, 50m/25Mi) and apply.

    Isolated from down_demo fat baseline (5×150m). HPA min=max=1 so iteration 1 at
    high RPS should FAIL and trigger UP-recovery instead of passing on warm fat CPU.
    """
    root = repo_root or REPO_ROOT
    reset_managed_web_yaml_to_up_demo_thin(deployment_yaml_path, hpa_yaml_path)
    print(
        "[up_demo] thin baseline: 1 repl @ 50m/25Mi, HPA min=max=1; kubectl apply...",
        flush=True,
    )
    kubectl_apply(deployment_yaml_path, hpa_yaml_path, root)
    wait_rollout(deployment_name=deployment_name, timeout_s=timeout_s, namespace=namespace)
    wait_single_replica_steady(deployment_name=deployment_name, namespace=namespace, timeout_s=timeout_s)
    print("[up_demo] thin baseline ready.", flush=True)


def apply_hpa_only_baseline(
    *,
    deployment_yaml_path: Path,
    hpa_yaml_path: Path,
    deployment_name: str,
    namespace: str,
    profile: str,
    repo_root: Path | None = None,
    timeout_s: int = 300,
) -> None:
    """Reset web for HPA-only compare: fixed requests; HPA may scale replica count during k6.

    UP profiles: thin deployment (1 repl, low CPU/mem) + scalable HPA (baseline maxReplicas).
    DOWN profiles: fat managed baseline (same as down_demo compare).
    Does not pin HPA min/max to deployment.spec.replicas.
    """
    from analysis.k8s_manifest import baseline_hpa_path, up_demo_thin_baseline_paths

    root = repo_root or REPO_ROOT
    prof = (profile or "").strip()
    is_up = prof in {"up_demo", "up_demo_strict"}
    if is_up:
        thin_dep, _thin_hpa = up_demo_thin_baseline_paths(
            deployment_yaml_path, hpa_yaml_path
        )
        scalable_hpa = baseline_hpa_path(hpa_yaml_path)
        if not thin_dep.exists() or not scalable_hpa.exists():
            raise FileNotFoundError(
                f"HPA-only UP baseline missing: {thin_dep} / {scalable_hpa}"
            )
        shutil.copy(thin_dep, deployment_yaml_path)
        shutil.copy(scalable_hpa, hpa_yaml_path)
        print(
            "[hpa-only] UP baseline: thin deployment (1 repl) + scalable HPA "
            f"(from {scalable_hpa.name}); applying...",
            flush=True,
        )
    else:
        reset_managed_web_yaml_to_baseline(deployment_yaml_path, hpa_yaml_path)
        print(
            "[hpa-only] DOWN baseline: fat deployment + scalable HPA; applying...",
            flush=True,
        )
    _coerce_hpa_file(hpa_yaml_path, root)
    kubectl_apply(
        deployment_yaml_path,
        hpa_yaml_path,
        root,
        align_hpa_to_deployment=False,
    )
    wait_rollout(
        deployment_name=deployment_name,
        timeout_s=timeout_s,
        namespace=namespace,
    )
    print("[hpa-only] baseline ready (HPA may scale during load).", flush=True)


def wait_single_replica_steady(
    *,
    deployment_name: str,
    namespace: str,
    timeout_s: int = 300,
    steady_checks: int = 3,
    check_interval_s: float = 2.0,
) -> None:
    """Wait until deployment + HPA are stably pinned at exactly one replica."""
    hpa_name = f"{deployment_name}-hpa"
    deadline = time.time() + timeout_s
    stable_hits = 0
    attempt = 0
    while time.time() < deadline:
        attempt += 1
        dep = _kubectl_get_json("deployment", deployment_name, namespace)
        hpa = _kubectl_get_json("hpa", hpa_name, namespace)
        dep_spec = (dep.get("spec") or {}).get("replicas")
        dep_status = dep.get("status") or {}
        updated = dep_status.get("updatedReplicas", 0)
        ready = dep_status.get("readyReplicas", 0)
        available = dep_status.get("availableReplicas", 0)
        observed = dep_status.get("observedGeneration")
        generation = dep.get("metadata", {}).get("generation")
        hpa_spec = hpa.get("spec") or {}
        hpa_status = hpa.get("status") or {}
        hpa_min = hpa_spec.get("minReplicas")
        hpa_max = hpa_spec.get("maxReplicas")
        hpa_current = hpa_status.get("currentReplicas")
        hpa_desired = hpa_status.get("desiredReplicas")
        is_steady = (
            dep_spec == 1
            and updated == 1
            and ready == 1
            and available == 1
            and observed == generation
            and hpa_min == 1
            and hpa_max == 1
            and hpa_current == 1
            and hpa_desired == 1
        )
        print(
            "[up_demo] baseline check "
            f"attempt={attempt} dep(spec={dep_spec},updated={updated},ready={ready},avail={available},gen={observed}/{generation}) "
            f"hpa(min={hpa_min},max={hpa_max},current={hpa_current},desired={hpa_desired}) "
            f"steady={is_steady}",
            flush=True,
        )
        if is_steady:
            stable_hits += 1
            if stable_hits >= steady_checks:
                print(
                    f"[up_demo] baseline steady for {stable_hits} consecutive checks; proceeding.",
                    flush=True,
                )
                return
        else:
            stable_hits = 0
        time.sleep(check_interval_s)
    raise TimeoutError(
        f"Timed out waiting for single-replica steady state on deployment/{deployment_name} and hpa/{hpa_name} in ns/{namespace}"
    )


def wait_rollout(
    deployment_name: str,
    timeout_s: int | None = None,
    namespace: str = "default",
) -> None:
    """Block until deployment rollout completes."""
    if timeout_s is None:
        timeout_s = int(os.environ.get("SQUEEZE_ROLLOUT_TIMEOUT_S", "300"))
    print(
        f"kubectl rollout status deployment/{deployment_name} (timeout={timeout_s}s)...",
        flush=True,
    )
    subprocess.run(
        [
            "kubectl",
            "rollout",
            "status",
            f"deployment/{deployment_name}",
            "-n",
            namespace,
            f"--timeout={timeout_s}s",
        ],
        check=True,
    )


def _squeeze_env_truthy(name: str, *, default: str = "1") -> bool:
    return os.environ.get(name, default).strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


def rollout_restart_deployment(
    *,
    deployment_name: str,
    namespace: str,
    timeout_s: int | None = None,
) -> None:
    """Replace all pods for a deployment (fresh containers for observe k6)."""
    if timeout_s is None:
        timeout_s = int(os.environ.get("SQUEEZE_ROLLOUT_TIMEOUT_S", "300"))
    print(
        f"[squeeze] rollout restart deployment/{deployment_name} in ns/{namespace}...",
        flush=True,
    )
    subprocess.run(
        [
            "kubectl",
            "-n",
            namespace,
            "rollout",
            "restart",
            f"deployment/{deployment_name}",
        ],
        check=True,
    )
    wait_rollout(
        deployment_name=deployment_name,
        namespace=namespace,
        timeout_s=timeout_s,
    )


def _replica_steady_checks() -> int:
    try:
        n = int(os.environ.get("SQUEEZE_REPLICA_STEADY_CHECKS", "3"))
    except ValueError:
        n = 3
    return max(2, min(n, 10))


def read_yaml_target_replicas(deployment_yaml_path: Path) -> int:
    try:
        dep_doc = yaml.safe_load(deployment_yaml_path.read_text())
        return int((dep_doc.get("spec") or {}).get("replicas") or 0)
    except Exception:
        return 0


def live_replica_state(
    *,
    deployment_name: str,
    namespace: str,
) -> dict:
    """Snapshot deployment + HPA replica fields from the live cluster."""
    hpa_name = f"{deployment_name}-hpa"
    dep = _kubectl_get_json("deployment", deployment_name, namespace)
    dep_spec = int((dep.get("spec") or {}).get("replicas") or 0)
    dep_status = dep.get("status") or {}
    ready = int(dep_status.get("readyReplicas") or 0)
    updated = int(dep_status.get("updatedReplicas") or 0)
    available = int(dep_status.get("availableReplicas") or 0)
    hpa_current = ready
    hpa_desired = ready
    hpa_max = 0
    try:
        hpa = _kubectl_get_json("hpa", hpa_name, namespace)
        hpa_spec = hpa.get("spec") or {}
        hpa_status = hpa.get("status") or {}
        hpa_current = int(hpa_status.get("currentReplicas") or ready)
        hpa_desired = int(hpa_status.get("desiredReplicas") or hpa_current)
        hpa_max = int(hpa_spec.get("maxReplicas") or 0)
    except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError):
        pass
    return {
        "dep_spec": dep_spec,
        "ready": ready,
        "updated": updated,
        "available": available,
        "hpa_current": hpa_current,
        "hpa_desired": hpa_desired,
        "hpa_max": hpa_max,
    }


def squeeze_yaml_live_replica_drift(
    deployment_yaml_path: Path,
    *,
    deployment_name: str,
    namespace: str,
) -> bool:
    """True when managed YAML replica target does not match live deployment/HPA."""
    target = read_yaml_target_replicas(deployment_yaml_path)
    if target < 1:
        return False
    live = live_replica_state(deployment_name=deployment_name, namespace=namespace)
    if live["dep_spec"] != target:
        return True
    if live["ready"] != target or live["updated"] != target or live["available"] != target:
        return True
    if live["hpa_current"] != target or live["hpa_desired"] != target:
        return True
    if live["hpa_max"] > target:
        return True
    return False


def prepare_squeeze_observe_before_k6(
    *,
    deployment_yaml_path: Path,
    hpa_yaml_path: Path,
    deployment_name: str,
    namespace: str,
    timeout_s: int | None = None,
) -> int:
    """Pin replicas, optionally rollout-restart all pods, wait steady before observe k6."""
    target = pin_observe_replicas_before_k6(
        deployment_yaml_path=deployment_yaml_path,
        hpa_yaml_path=hpa_yaml_path,
        deployment_name=deployment_name,
        namespace=namespace,
        timeout_s=timeout_s,
    )
    if target < 1:
        return target
    if _squeeze_env_truthy("SQUEEZE_ROLLOUT_RESTART_BEFORE_OBSERVE"):
        rollout_restart_deployment(
            deployment_name=deployment_name,
            namespace=namespace,
            timeout_s=timeout_s,
        )
        wait_for_deployment_replicas(
            deployment_name=deployment_name,
            namespace=namespace,
            yaml_replicas=target,
            timeout_s=timeout_s or int(os.environ.get("SQUEEZE_ROLLOUT_TIMEOUT_S", "300")),
            steady_checks=max(3, _replica_steady_checks()),
        )
    return target


def ensure_squeeze_cluster_ready_before_k6(
    *,
    deployment_yaml_path: Path,
    hpa_yaml_path: Path,
    deployment_name: str,
    namespace: str,
    timeout_s: int = 300,
) -> None:
    """Pin deployment+HPA, restart pods, wait steady before observe k6."""
    prepare_squeeze_observe_before_k6(
        deployment_yaml_path=deployment_yaml_path,
        hpa_yaml_path=hpa_yaml_path,
        deployment_name=deployment_name,
        namespace=namespace,
        timeout_s=timeout_s,
    )


def pin_observe_replicas_before_k6(
    *,
    deployment_yaml_path: Path,
    hpa_yaml_path: Path,
    deployment_name: str,
    namespace: str,
    timeout_s: int | None = None,
) -> int:
    """Pin live deployment+HPA to yaml spec.replicas (min=max) before observe/replay k6.

    Prevents HPA scale-up during settle/load so replay measures the saved config.
    Returns the pinned replica target.
    """
    if os.environ.get("SQUEEZE_WAIT_REPLICAS_STEADY", "1").strip().lower() not in (
        "1",
        "true",
        "yes",
        "on",
    ):
        return read_yaml_target_replicas(deployment_yaml_path)
    target = read_yaml_target_replicas(deployment_yaml_path)
    if target < 1:
        return target
    if timeout_s is None:
        timeout_s = int(os.environ.get("SQUEEZE_ROLLOUT_TIMEOUT_S", "300"))
    hpa_name = f"{deployment_name}-hpa"
    pin = json.dumps({"spec": {"maxReplicas": target, "minReplicas": target}})
    subprocess.run(
        [
            "kubectl",
            "-n",
            namespace,
            "patch",
            "hpa",
            hpa_name,
            "--type=merge",
            "-p",
            pin,
        ],
        check=True,
    )
    print(
        f"[squeeze] pinned hpa/{hpa_name} minReplicas=maxReplicas={target}",
        flush=True,
    )
    # Use deployment patch (RBAC: patch/update) — not `kubectl scale` (scale subresource).
    dep_patch = json.dumps({"spec": {"replicas": target}})
    subprocess.run(
        [
            "kubectl",
            "-n",
            namespace,
            "patch",
            "deployment",
            deployment_name,
            "--type=merge",
            "-p",
            dep_patch,
        ],
        check=True,
    )
    print(
        f"[squeeze] patched deployment/{deployment_name} spec.replicas={target}",
        flush=True,
    )
    wait_for_deployment_replicas(
        deployment_name=deployment_name,
        namespace=namespace,
        yaml_replicas=target,
        timeout_s=timeout_s,
        steady_checks=max(3, _replica_steady_checks()),
    )
    return target


def wait_for_deployment_replicas(
    *,
    deployment_name: str,
    namespace: str,
    yaml_replicas: int | None = None,
    timeout_s: int = 300,
    check_interval_s: float = 2.0,
    steady_checks: int | None = None,
) -> None:
    """Wait until live deployment + HPA match spec.replicas (after apply/rollout).

    Uses the cluster deployment spec as source of truth — not on-disk YAML alone —
    so HPA/controller drift (file says 1, live is 2) does not deadlock the wait.
    """
    hpa_name = f"{deployment_name}-hpa"
    deadline = time.time() + timeout_s
    attempt = 0
    target = yaml_replicas or 0
    if yaml_replicas and yaml_replicas > 0:
        print(
            f"[squeeze] replica_wait: yaml spec.replicas={yaml_replicas} "
            f"(will wait for live deployment spec after apply)",
            flush=True,
        )
    intent = yaml_replicas if yaml_replicas and yaml_replicas > 0 else None
    need_hits = steady_checks if steady_checks is not None else _replica_steady_checks()
    stable_hits = 0
    while time.time() < deadline:
        attempt += 1
        dep = _kubectl_get_json("deployment", deployment_name, namespace)
        dep_spec = int((dep.get("spec") or {}).get("replicas") or 0)
        if dep_spec < 1:
            time.sleep(check_interval_s)
            continue
        target = intent if intent is not None else dep_spec
        dep_status = dep.get("status") or {}
        ready = int(dep_status.get("readyReplicas") or 0)
        updated = int(dep_status.get("updatedReplicas") or 0)
        available = int(dep_status.get("availableReplicas") or 0)
        hpa_current = ready
        hpa_desired = ready
        hpa_max = 0
        try:
            hpa = _kubectl_get_json("hpa", hpa_name, namespace)
            hpa_spec = hpa.get("spec") or {}
            hpa_status = hpa.get("status") or {}
            hpa_current = int(hpa_status.get("currentReplicas") or ready)
            hpa_desired = int(hpa_status.get("desiredReplicas") or hpa_current)
            hpa_max = int(hpa_spec.get("maxReplicas") or 0)
            if intent is not None and hpa_max > intent:
                _kubectl_patch_hpa_replica_cap(
                    hpa_name=hpa_name,
                    namespace=namespace,
                    max_replicas=intent,
                )
                hpa_max = intent
        except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError):
            pass
        dep_ok = ready == target and updated == target and available == target
        if intent is not None:
            dep_ok = dep_ok and dep_spec == target
        hpa_capped = hpa_max <= target if hpa_max else True
        # Scale-down: do not proceed while HPA still reports extra pods (e.g. spec=2, current=3).
        hpa_ok = hpa_current == target and hpa_desired == target
        steady = dep_ok and hpa_capped and hpa_ok
        if steady:
            stable_hits += 1
        else:
            stable_hits = 0
        print(
            f"[squeeze] replica_wait attempt={attempt} target={target} "
            f"dep(spec={dep_spec},ready={ready},updated={updated},avail={available}) "
            f"hpa(current={hpa_current},desired={hpa_desired},max={hpa_max}) "
            f"steady={steady} hits={stable_hits}/{need_hits}",
            flush=True,
        )
        if stable_hits >= need_hits:
            print(f"[squeeze] replicas steady at {target}; proceeding.", flush=True)
            return
        time.sleep(check_interval_s)
    raise TimeoutError(
        f"Timed out waiting for steady replicas on deployment/{deployment_name} "
        f"in ns/{namespace} (last target={target})"
    )


def apply_violation_probe_down_step(
    *,
    deployment_yaml_path: Path,
    hpa_yaml_path: Path,
    deployment_name: str,
    namespace: str,
    repo_root: Path | None = None,
) -> bool:
    """Shrink first-container CPU/memory requests+limits, apply, and wait for rollout.

    Used when ``--until-violation`` is set but the optimizer wrote an empty
    ``recommended.diff`` (e.g. telemetry not trustworthy). Without a diff the
    squeeze loop would stop before ever measuring a FAIL; this step applies a
    small deterministic DOWN so the next k6 iteration can still hit ``first_fail``.

    In ``start.py``, this probe is **not** applied for ``squeeze_optimizer=llm`` by
    default (LLM compare arm must use LLM patches only); set env
    ``SQUEEZE_UNTIL_VIOLATION_PROBE_LLM=1`` to opt in.

    Env (optional):
    - ``SQUEEZE_UNTIL_VIOLATION_PROBE_STEP_PCT`` — fraction to remove per probe (default 0.10).
    - ``SQUEEZE_VIOLATION_PROBE_CPU_FLOOR_M`` — min CPU request/limit in millicores (default 50).
    - ``SQUEEZE_VIOLATION_PROBE_MEM_FLOOR_MIB`` — min memory request/limit in Mi (default 32).

    Returns True if deployment YAML changed and apply+rollout succeeded; False if
    no further reduction was possible or paths were invalid.
    """
    root = repo_root or REPO_ROOT
    if not deployment_yaml_path.exists():
        return False
    step = float(os.environ.get("SQUEEZE_UNTIL_VIOLATION_PROBE_STEP_PCT") or "0.10")
    step = max(0.01, min(step, 0.45))
    cpu_floor = int(os.environ.get("SQUEEZE_VIOLATION_PROBE_CPU_FLOOR_M") or "50")
    mem_floor = int(os.environ.get("SQUEEZE_VIOLATION_PROBE_MEM_FLOOR_MIB") or "32")
    factor = 1.0 - step

    dep_doc = yaml.safe_load(deployment_yaml_path.read_text())
    if not dep_doc or dep_doc.get("kind") != "Deployment":
        return False

    spec = dep_doc.setdefault("spec", {})
    tmpl = spec.setdefault("template", {}).setdefault("spec", {})
    containers = tmpl.get("containers") or []
    if not containers:
        return False

    c0 = containers[0]
    res = c0.setdefault("resources", {})
    req = res.setdefault("requests", {})
    lim = res.setdefault("limits", {})

    def scale_millicpu(val: str | int | float | None) -> str | None:
        if val is None:
            return None
        s = str(val).strip()
        if not s:
            return None
        if s.endswith("m"):
            base = int(s[:-1] or "0")
        else:
            # whole cores, e.g. "1"
            try:
                base = int(float(s) * 1000)
            except ValueError:
                return None
        if base <= 0:
            return None
        if base <= cpu_floor:
            return None
        out = max(cpu_floor, int(math.ceil(base * factor)))
        if out >= base:
            return None
        return f"{out}m"

    def scale_mib(val: str | int | float | None) -> str | None:
        if val is None:
            return None
        s = str(val).strip()
        if not s.endswith("Mi"):
            return None
        base = int(s.replace("Mi", "") or "0")
        if base <= 0:
            return None
        if base <= mem_floor:
            return None
        out = max(mem_floor, int(math.ceil(base * factor)))
        if out >= base:
            return None
        return f"{out}Mi"

    changed = False
    for block in (req, lim):
        for key, scaler in (("cpu", scale_millicpu), ("memory", scale_mib)):
            if key not in block:
                continue
            old = block[key]
            new = scaler(old)
            if new is not None and str(old) != new:
                block[key] = new
                changed = True

    if not changed:
        return False

    dump_kw: dict = {
        "default_flow_style": False,
        "sort_keys": False,
        "allow_unicode": True,
    }
    deployment_yaml_path.write_text(yaml.dump(dep_doc, **dump_kw))
    if not hpa_yaml_path.exists():
        print(
            "[squeeze] violation probe: HPA YAML missing; applying deployment only.",
            flush=True,
        )
        print("kubectl apply (deployment only)...", flush=True)
        subprocess.run(
            ["kubectl", "apply", "-f", str(deployment_yaml_path)],
            cwd=root,
            check=True,
        )
    else:
        kubectl_apply(deployment_yaml_path, hpa_yaml_path, root)
    wait_rollout(deployment_name=deployment_name, namespace=namespace)
    print("[squeeze] violation probe DOWN step applied.", flush=True)
    return True


def apply_squeeze_stall_resource_step(
    *,
    deployment_yaml_path: Path,
    hpa_yaml_path: Path,
    deployment_name: str,
    namespace: str,
    repo_root: Path | None = None,
) -> bool:
    """Resource-only DOWN when a PASS iteration had no effective progress (replicas unchanged)."""
    root = repo_root or REPO_ROOT
    if not deployment_yaml_path.exists():
        return False
    step = float(os.environ.get("SQUEEZE_STALL_RESOURCE_STEP_PCT", "0.08"))
    step = max(0.03, min(step, 0.20))
    cpu_floor = int(os.environ.get("SQUEEZE_VIOLATION_PROBE_CPU_FLOOR_M", "50"))
    mem_floor = int(os.environ.get("SQUEEZE_VIOLATION_PROBE_MEM_FLOOR_MIB", "32"))
    factor = 1.0 - step

    dep_doc = yaml.safe_load(deployment_yaml_path.read_text())
    if not dep_doc or dep_doc.get("kind") != "Deployment":
        return False
    file_rep = int((dep_doc.get("spec") or {}).get("replicas") or 1)
    spec = dep_doc.setdefault("spec", {})
    tmpl = spec.setdefault("template", {}).setdefault("spec", {})
    containers = tmpl.get("containers") or []
    if not containers:
        return False
    c0 = containers[0]
    res = c0.setdefault("resources", {})
    req = res.setdefault("requests", {})
    lim = res.setdefault("limits", {})

    def scale_millicpu(val: str | int | float | None) -> str | None:
        if val is None:
            return None
        s = str(val).strip()
        if not s:
            return None
        base = int(s[:-1] or "0") if s.endswith("m") else int(float(s) * 1000)
        if base <= cpu_floor:
            return None
        out = max(cpu_floor, int(math.ceil(base * factor)))
        return None if out >= base else f"{out}m"

    def scale_mib(val: str | int | float | None) -> str | None:
        if val is None:
            return None
        s = str(val).strip()
        if not s:
            return None
        base = int(s[:-2] or "0") if s.upper().endswith("MI") else int(s)
        if base <= mem_floor:
            return None
        out = max(mem_floor, int(math.ceil(base * factor)))
        return None if out >= base else f"{out}Mi"

    changed = False
    for block in (req, lim):
        for key, scaler in (("cpu", scale_millicpu), ("memory", scale_mib)):
            if key not in block:
                continue
            old = block[key]
            new = scaler(old)
            if new is not None and str(old) != new:
                block[key] = new
                changed = True
    if not changed:
        return False

    spec["replicas"] = file_rep
    dump_kw = {"default_flow_style": False, "sort_keys": False, "allow_unicode": True}
    deployment_yaml_path.write_text(yaml.dump(dep_doc, **dump_kw))
    if hpa_yaml_path.exists():
        kubectl_apply(deployment_yaml_path, hpa_yaml_path, root)
    else:
        subprocess.run(
            ["kubectl", "apply", "-f", str(deployment_yaml_path)],
            cwd=root,
            check=True,
        )
    wait_rollout(deployment_name=deployment_name, namespace=namespace)
    ensure_squeeze_cluster_ready_before_k6(
        deployment_yaml_path=deployment_yaml_path,
        hpa_yaml_path=hpa_yaml_path,
        deployment_name=deployment_name,
        namespace=namespace,
    )
    print(f"[squeeze] stall recovery: resource-only DOWN step_pct={step:.3f}", flush=True)
    return True


def apply_recovery_probe_up_step(
    *,
    deployment_yaml_path: Path,
    hpa_yaml_path: Path,
    deployment_name: str,
    namespace: str,
    repo_root: Path | None = None,
) -> bool:
    """Raise first-container CPU/memory requests+limits and relax HPA maxReplicas, then apply.

    Used when ``up_recovery_active`` (e.g. ``up_demo`` after iteration-1 FAIL) but the anchor
    ``recommended.diff`` is empty: without this, the squeeze loop would exit immediately while the
    service is still failing and never apply further capacity.

    Env (optional):
    - ``SQUEEZE_RECOVERY_PROBE_UP_STEP_PCT`` — fractional increase per probe (default 0.15).
    - ``SQUEEZE_RECOVERY_PROBE_CPU_CAP_M`` — cap millicores for requests/limits (default 4000).
    - ``SQUEEZE_RECOVERY_PROBE_MEM_CAP_MIB`` — cap MiB for requests/limits (default 4096).
    """
    root = repo_root or REPO_ROOT
    if not deployment_yaml_path.exists():
        return False
    step = float(os.environ.get("SQUEEZE_RECOVERY_PROBE_UP_STEP_PCT") or "0.15")
    step = max(0.01, min(step, 0.45))
    factor = 1.0 + step
    cpu_cap = int(os.environ.get("SQUEEZE_RECOVERY_PROBE_CPU_CAP_M") or "4000")
    mem_cap = int(os.environ.get("SQUEEZE_RECOVERY_PROBE_MEM_CAP_MIB") or "4096")

    dep_doc = yaml.safe_load(deployment_yaml_path.read_text())
    if not dep_doc or dep_doc.get("kind") != "Deployment":
        return False

    spec = dep_doc.setdefault("spec", {})
    tmpl = spec.setdefault("template", {}).setdefault("spec", {})
    containers = tmpl.get("containers") or []
    if not containers:
        return False

    c0 = containers[0]
    res = c0.setdefault("resources", {})
    req = res.setdefault("requests", {})
    lim = res.setdefault("limits", {})

    def up_millicpu(val: str | int | float | None) -> str | None:
        if val is None:
            return None
        s = str(val).strip()
        if not s:
            return None
        if s.endswith("m"):
            base = int(s[:-1] or "0")
        else:
            try:
                base = int(float(s) * 1000)
            except ValueError:
                return None
        if base <= 0:
            return None
        out = int(math.ceil(base * factor))
        out = min(max(out, base + 1), cpu_cap)
        if out <= base:
            return None
        return f"{out}m"

    def up_mib(val: str | int | float | None) -> str | None:
        if val is None:
            return None
        s = str(val).strip()
        if not s.endswith("Mi"):
            return None
        base = int(s.replace("Mi", "") or "0")
        if base <= 0:
            return None
        out = int(math.ceil(base * factor))
        out = min(max(out, base + 1), mem_cap)
        if out <= base:
            return None
        return f"{out}Mi"

    dep_changed = False
    for block in (req, lim):
        for key, scaler in (("cpu", up_millicpu), ("memory", up_mib)):
            if key not in block:
                continue
            old = block[key]
            new = scaler(old)
            if new is not None and str(old) != new:
                block[key] = new
                dep_changed = True

    hpa_changed = False
    hpa_doc: dict | None = None
    if hpa_yaml_path.exists():
        hpa_doc = yaml.safe_load(hpa_yaml_path.read_text())
        if hpa_doc and hpa_doc.get("kind") == "HorizontalPodAutoscaler":
            hspec = hpa_doc.setdefault("spec", {})
            max_r = int(hspec.get("maxReplicas") or 1)
            delta = max(1, int(math.ceil(max_r * step * 0.5)))
            new_max = max_r + delta
            if new_max <= max_r:
                new_max = max_r + 1
            hspec["maxReplicas"] = new_max
            hpa_changed = True

    if not dep_changed and not hpa_changed:
        return False

    dump_kw: dict = {
        "default_flow_style": False,
        "sort_keys": False,
        "allow_unicode": True,
    }
    deployment_yaml_path.write_text(yaml.dump(dep_doc, **dump_kw))
    if hpa_changed and hpa_doc is not None:
        hpa_yaml_path.write_text(yaml.dump(hpa_doc, **dump_kw))
    if not hpa_yaml_path.exists():
        print(
            "[squeeze] recovery UP probe: HPA YAML missing; applying deployment only.",
            flush=True,
        )
        print("kubectl apply (deployment only)...", flush=True)
        subprocess.run(
            ["kubectl", "apply", "-f", str(deployment_yaml_path)],
            cwd=root,
            check=True,
        )
    else:
        kubectl_apply(deployment_yaml_path, hpa_yaml_path, root)
    wait_rollout(deployment_name=deployment_name, namespace=namespace)
    print("[squeeze] recovery UP probe applied.", flush=True)
    return True


def apply_recommended_diff(
    run_dir: Path,
    deployment_yaml_path: Path,
    hpa_yaml_path: Path,
    deployment_name: str,
    namespace: str,
    repo_root: Path | None = None,
    *,
    allow_empty_diff: bool = False,
) -> None:
    """Apply current deployment/HPA YAMLs via kubectl and wait for rollout."""
    root = repo_root or REPO_ROOT
    diff_path = run_dir / "recommended.diff"
    if (
        not allow_empty_diff
        and diff_path.exists()
        and not diff_path.read_text().strip()
    ):
        raise ValueError("recommended.diff is empty (no YAML changes recommended)")
    kubectl_apply(deployment_yaml_path, hpa_yaml_path, root)
    wait_rollout(deployment_name=deployment_name, namespace=namespace)
    yaml_replicas = 0
    try:
        dep_doc = yaml.safe_load(deployment_yaml_path.read_text())
        yaml_replicas = int((dep_doc.get("spec") or {}).get("replicas") or 0)
    except Exception:
        yaml_replicas = 0
    if yaml_replicas > 0 and hpa_yaml_path.exists():
        hpa_name = f"{deployment_name}-hpa"
        _kubectl_patch_hpa_replica_cap(
            hpa_name=hpa_name,
            namespace=namespace,
            max_replicas=yaml_replicas,
        )
    if os.environ.get("SQUEEZE_WAIT_REPLICAS_STEADY", "1").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    ):
        wait_for_deployment_replicas(
            deployment_name=deployment_name,
            namespace=namespace,
            yaml_replicas=yaml_replicas or None,
        )
        ensure_squeeze_cluster_ready_before_k6(
            deployment_yaml_path=deployment_yaml_path,
            hpa_yaml_path=hpa_yaml_path,
            deployment_name=deployment_name,
            namespace=namespace,
        )
    print("rollout complete.", flush=True)
