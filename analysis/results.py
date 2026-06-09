import json
import math
import os
import shutil
from datetime import date
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

from .api import analyze_with_llm
from .experiment_build import (
    build_experiment_payload,
    format_cpu_millicores,
    format_memory_mib,
    get_config_from_yaml,
)
from .prompts import (
    EFFICIENCY_LLM_ONLY_SQUEEZE_PROMPT,
    EFFICIENCY_SYSTEM_PROMPT,
    SYSTEM_PROMPT,
    build_user_prompt,
    build_vanilla_user_prompt,
    VANILLA_LLM_SQUEEZE_PROMPT,
)
from .results_paths import results_dir as _results_dir_for_repo
from .compare_shared_measure import (
    MEASURED_DEPLOYMENT_YAML,
    MEASURED_HPA_YAML,
    RECOMMENDED_DEPLOYMENT_YAML,
    RECOMMENDED_HPA_YAML,
    load_measured_yaml_for_prompt,
    load_shared_canonical_overrides,
)
from .scaling_policy import attach_scaling_hint

def _results_base() -> Path:
    return _results_dir_for_repo(REPO_ROOT)


DEFAULT_DEPLOYMENT_YAML = REPO_ROOT / "apps" / "service" / "k8s" / "deployment.yaml"
DEFAULT_HPA_YAML = REPO_ROOT / "apps" / "service" / "k8s" / "hpa.yaml"
DEFAULT_PROMETHEUS_URL = "http://localhost:9090"


def _log(msg: str) -> None:
    print(f"[analysis] {msg}")


def _coerce_report_markdown(value) -> str:
    """LLM JSON sometimes returns report as a list of bullets; report.md must be str."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(
            _coerce_report_markdown(item) if isinstance(item, (list, dict)) else str(item)
            for item in value
        )
    if isinstance(value, dict):
        return json.dumps(value, indent=2)
    return str(value)


def _strip_markdown_yaml_fences(text: str) -> str:
    """Remove ```yaml ... ``` wrappers the LLM sometimes puts in JSON string fields."""
    s = (text or "").strip()
    if not s.startswith("```"):
        return s
    lines = s.splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip()


def _normalize_llm_yaml_fields(result: dict) -> None:
    for key in ("deployment_yaml_new", "hpa_yaml_new"):
        raw = result.get(key)
        if isinstance(raw, str) and raw.strip():
            result[key] = _strip_markdown_yaml_fences(raw)


def _observed_summary_from_experiment(experiment: dict) -> dict:
    observed = experiment.get("observed") or {}
    latency = observed.get("latency_ms") or {}
    return {
        "achieved_requests_per_second": observed.get("achieved_requests_per_second"),
        "error_rate": observed.get("error_rate"),
        "latency_ms_p95": latency.get("p95"),
        "latency_ms_p99": latency.get("p99"),
        "cpu_util_pct": observed.get("cpu_util_pct"),
        "mem_util_pct": observed.get("mem_util_pct"),
        "replicas": observed.get("replicas"),
        "replicas_max": observed.get("replicas_max"),
        "oom_kills": observed.get("oom_kills"),
        "cpu_util_to_limit": observed.get("cpu_util_to_limit"),
        "total_requests": observed.get("total_requests"),
    }


def _slo_status_from_experiment(experiment: dict) -> str:
    failure = experiment.get("failure") or {}
    return "FAIL" if failure.get("failed") else "PASS"


def _resolve_yaml_paths(meta: dict | None) -> tuple[Path, Path]:
    deployment_yaml = (meta or {}).get("deployment_yaml")
    hpa_yaml = (meta or {}).get("hpa_yaml")
    dep_path = (REPO_ROOT / deployment_yaml).resolve() if deployment_yaml else DEFAULT_DEPLOYMENT_YAML
    hpa_path = (REPO_ROOT / hpa_yaml).resolve() if hpa_yaml else DEFAULT_HPA_YAML
    return dep_path, hpa_path


def _attach_previous_iteration_context(experiment: dict, meta: dict | None) -> None:
    """Attach prior-iteration summary for same squeeze run when available."""
    if not meta:
        return
    run_label = meta.get("run_label")
    iteration_index = meta.get("iteration_index")
    if not run_label or not iteration_index:
        return
    try:
        idx = int(iteration_index)
    except (TypeError, ValueError):
        return
    if idx <= 1:
        return
    prev_exp_path = _results_base() / str(run_label) / f"iteration-{idx - 1}" / "experiment.json"
    if not prev_exp_path.exists():
        return
    try:
        prev = json.loads(prev_exp_path.read_text())
    except json.JSONDecodeError:
        return
    prev_observed = prev.get("observed") or {}
    prev_cfg = prev.get("config") or {}
    prev_axis = ""
    prev_analysis = (
        _results_base() / str(run_label) / f"iteration-{idx - 1}" / "analysis.json"
    )
    prev_streak = 0
    if prev_analysis.exists():
        try:
            prev_analysis_data = json.loads(prev_analysis.read_text()) or {}
            prev_axis = prev_analysis_data.get("squeeze_down_axis") or ""
            prev_streak = int(prev_analysis_data.get("resource_pass_streak") or 0)
        except (json.JSONDecodeError, TypeError, ValueError):
            prev_axis = ""
            prev_streak = 0
    experiment["_prev_iteration"] = {
        "slo_status": _slo_status_from_experiment(prev),
        "latency_ms_p95": (prev_observed.get("latency_ms") or {}).get("p95"),
        "cpu_util_pct": prev_observed.get("cpu_util_pct"),
        "mem_util_pct": prev_observed.get("mem_util_pct"),
        "deployment_replicas": prev_cfg.get("deployment_replicas"),
        "cpu_request_m": prev_cfg.get("cpu_request_m"),
        "mem_request_mib": prev_cfg.get("mem_request_mib"),
        "squeeze_down_axis": str(prev_axis).strip().lower(),
        "resource_pass_streak": prev_streak,
    }


def _llm_intends_replica_down(result: dict, experiment: dict) -> bool:
    """True when LLM (or fallback) YAML reduces replicas or HPA max below live observation."""
    observed = experiment.get("observed") or {}
    live = int(observed.get("replicas") or 0)
    if live < 2:
        return False
    dep_new = (result.get("deployment_yaml_new") or "").strip()
    if dep_new:
        try:
            doc = yaml.safe_load(dep_new)
            if isinstance(doc, dict) and doc.get("kind") == "Deployment":
                proposed = int((doc.get("spec") or {}).get("replicas") or 0)
                if 0 < proposed < live:
                    return True
        except Exception:
            pass
    hpa_new = (result.get("hpa_yaml_new") or "").strip()
    if hpa_new:
        try:
            hdoc = yaml.safe_load(hpa_new)
            if isinstance(hdoc, dict) and hdoc.get("kind") == "HorizontalPodAutoscaler":
                mx = int((hdoc.get("spec") or {}).get("maxReplicas") or live)
                if mx < live:
                    return True
        except Exception:
            pass
    return False


def _live_replica_drift(experiment: dict) -> bool:
    """Cluster is running more pods than provisioned in config/YAML (HPA overshoot)."""
    observed = experiment.get("observed") or {}
    live = max(
        int(observed.get("replicas") or 0),
        int(observed.get("replicas_max") or 0),
    )
    if live < 2:
        return False
    cfg = experiment.get("config") or {}
    cfg_rep = int(cfg.get("deployment_replicas") or 0)
    return live > cfg_rep > 0


def squeeze_cluster_ahead_of_yaml(experiment: dict) -> bool:
    """Public alias for squeeze loop: live replica count exceeds managed YAML/config."""
    return _live_replica_drift(experiment)


def _yaml_noop_vs_managed_paths(
    result: dict, deployment_yaml_path: Path, hpa_yaml_path: Path
) -> bool:
    """True when LLM YAML matches on-disk managed files (would produce empty diff)."""
    dep_new = (result.get("deployment_yaml_new") or "").strip()
    hpa_new = (result.get("hpa_yaml_new") or "").strip()
    if not dep_new and not hpa_new:
        return True
    if dep_new:
        if not deployment_yaml_path.exists():
            return False
        if dep_new.strip() != deployment_yaml_path.read_text().strip():
            return False
    if hpa_new:
        if not hpa_yaml_path.exists():
            return False
        if hpa_new.strip() != hpa_yaml_path.read_text().strip():
            return False
    return True


def _needs_pure_llm_down_repair(
    result: dict,
    experiment: dict,
    deployment_yaml_path: Path,
    hpa_yaml_path: Path,
) -> bool:
    """One-shot LLM repair when pure squeeze would write an empty diff (not live drift)."""
    if bool(((experiment.get("failure") or {}).get("failed"))):
        return False
    if _live_replica_drift(experiment):
        return False
    return _yaml_noop_vs_managed_paths(result, deployment_yaml_path, hpa_yaml_path)


def _repair_pure_llm_squeeze_down_yaml(
    result: dict,
    experiment: dict,
    deployment_yaml_path: Path,
    hpa_yaml_path: Path,
) -> None:
    """Re-prompt LLM when DOWN PASS would otherwise emit identical/empty YAML."""
    from .k8s_manifest import clamp_llm_squeeze_replicas_to_one_step

    observed = experiment.get("observed") or {}
    live = max(
        int(observed.get("replicas") or 0),
        int(observed.get("replicas_max") or 0),
    )
    target_rep = max(1, live - 1) if live >= 2 else int(live or 1)
    yaml_str = load_current_yaml(deployment_yaml_path, hpa_yaml_path)
    file_rep = int((experiment.get("config") or {}).get("deployment_replicas") or live or 1)
    replica_ok = _llm_replica_down_allowed(experiment)
    prev_axis = ((experiment.get("_prev_iteration") or {}).get("squeeze_down_axis") or "").lower()
    if replica_ok and prev_axis != "replica" and live >= 2:
        repair_tail = (
            f"Return FULL deployment_yaml_new and hpa_yaml_new with spec.replicas={target_rep}, "
            "hpa maxReplicas aligned to that target, and LOWER cpu/memory requests than the current "
            "file."
        )
    else:
        repair_tail = (
            f"Return FULL deployment_yaml_new with spec.replicas={file_rep} unchanged "
            f"(do NOT lower replicas; live={live}) and LOWER cpu/memory requests than the current "
            "file. Align hpa maxReplicas with spec.replicas."
        )
    repair_user = (
        build_user_prompt(experiment, yaml_str, mode="squeeze")
        + "\n\nREPAIR (mandatory): Your previous answer was empty or identical to the on-disk YAML "
        f"while SLO PASS and squeeze-down continues. Live replicas={live}. "
        + repair_tail
        + " The output MUST differ from the current file content."
    )
    repaired = analyze_with_llm(EFFICIENCY_LLM_ONLY_SQUEEZE_PROMPT, repair_user)
    repaired = _postprocess_llm_result(repaired, experiment)
    if (repaired.get("deployment_yaml_new") or "").strip():
        result["deployment_yaml_new"] = repaired["deployment_yaml_new"]
    if (repaired.get("hpa_yaml_new") or "").strip():
        result["hpa_yaml_new"] = repaired["hpa_yaml_new"]
    if (result.get("deployment_yaml_new") or "").strip() or (
        result.get("hpa_yaml_new") or ""
    ).strip():
        clamp_llm_squeeze_replicas_to_one_step(
            result,
            experiment,
            deployment_yaml_path=deployment_yaml_path,
            hpa_yaml_path=hpa_yaml_path,
        )
        ev = list(result.get("evidence") or [])
        ev.append("guard.llm_repair_down_yaml")
        result["evidence"] = ev


def _repair_pure_llm_vetoed_resource_up(
    result: dict,
    experiment: dict,
    deployment_yaml_path: Path,
    hpa_yaml_path: Path,
    *,
    rejected_deployment_yaml: str,
    rejected_hpa_yaml: str,
) -> bool:
    """Re-prompt after PASS squeeze-down illegally raised cpu/mem vs on-disk file."""
    from .k8s_manifest import clamp_llm_squeeze_replicas_to_one_step

    baseline_yaml = load_current_yaml(deployment_yaml_path, hpa_yaml_path)
    rejected_blocks: list[str] = []
    if rejected_deployment_yaml.strip():
        rejected_blocks.append(
            "## Your rejected proposal (deployment — resource UP not allowed on PASS)\n"
            "```yaml\n"
            f"{rejected_deployment_yaml.strip()}\n"
            "```"
        )
    if rejected_hpa_yaml.strip():
        rejected_blocks.append(
            "## Your rejected proposal (HPA)\n"
            "```yaml\n"
            f"{rejected_hpa_yaml.strip()}\n"
            "```"
        )
    repair_user = (
        build_user_prompt(experiment, baseline_yaml, mode="squeeze")
        + "\n\nREPAIR (mandatory): SLO PASS and squeeze-down are active. Your previous YAML "
        "**increased** cpu and/or memory **requests** vs the on-disk file. That is forbidden "
        "on PASS (high cpu_util_pct means the pod is hot — do not raise requests).\n\n"
        "## Correct baseline (on-disk — requests/limits must not exceed this)\n"
        "The current YAML block above is authoritative.\n\n"
        + ("\n\n".join(rejected_blocks) if rejected_blocks else "")
        + "\n\nReturn FULL deployment_yaml_new and/or hpa_yaml_new that **only scale DOWN** "
        "vs the on-disk file: lower cpu/memory requests (and limits if you change them) "
        "and/or at most one fewer replica vs live. The result MUST differ from the on-disk "
        "file and MUST NOT increase requests or limits."
    )
    repaired = analyze_with_llm(EFFICIENCY_LLM_ONLY_SQUEEZE_PROMPT, repair_user)
    repaired = _postprocess_llm_result(repaired, experiment)
    if (repaired.get("deployment_yaml_new") or "").strip():
        result["deployment_yaml_new"] = repaired["deployment_yaml_new"]
    if (repaired.get("hpa_yaml_new") or "").strip():
        result["hpa_yaml_new"] = repaired["hpa_yaml_new"]
    if not (result.get("deployment_yaml_new") or "").strip() and not (
        result.get("hpa_yaml_new") or ""
    ).strip():
        return False
    if _yaml_increases_resources_vs_file(result, deployment_yaml_path):
        return False
    if _yaml_noop_vs_managed_paths(result, deployment_yaml_path, hpa_yaml_path):
        return False
    clamp_llm_squeeze_replicas_to_one_step(
        result,
        experiment,
        deployment_yaml_path=deployment_yaml_path,
        hpa_yaml_path=hpa_yaml_path,
    )
    return True


def _squeeze_should_cap_replicas(experiment: dict, result: dict) -> bool:
    """Cap replicas when at resource floor, live drift, or LLM explicitly scales replicas down."""
    if _live_replica_drift(experiment):
        return True
    if _llm_intends_replica_down(result, experiment):
        return True
    observed = experiment.get("observed") or {}
    live = int(observed.get("replicas") or 0)
    if live < 2:
        return False
    cpu_floor, mem_floor = _squeeze_resource_floors()
    cfg = experiment.get("config") or {}
    at_cpu_floor = int(cfg.get("cpu_request_m") or 0) <= cpu_floor
    at_mem_floor = int(cfg.get("mem_request_mib") or 0) <= mem_floor
    return at_cpu_floor and at_mem_floor


def _llm_pure_squeeze() -> bool:
    """When true (default for llm-squeeze script), sizing comes from LLM+prompt only."""
    return os.environ.get("SQUEEZE_LLM_PURE", "1").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


def _llm_vanilla_squeeze() -> bool:
    """When true, LLM gets coarse summary only (no full experiment JSON / scaling_hint)."""
    return os.environ.get("SQUEEZE_LLM_VANILLA", "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


def _squeeze_until_violation_active() -> bool:
    """True when squeeze must run until a real FAIL (first_fail), not stop at best_pass."""
    return os.environ.get("SQUEEZE_UNTIL_VIOLATION", "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


def _llm_squeeze_down_boundary_active(experiment: dict) -> bool:
    """True when LLM squeeze is seeking the DOWN cost-effective boundary (compare / down_demo)."""
    if os.environ.get("SQUEEZE_LLM_DOWN_BOUNDARY", "1").strip().lower() in (
        "0",
        "false",
        "no",
        "off",
    ):
        return False
    if experiment.get("squeeze_optimizer") != "llm":
        return False
    if experiment.get("up_recovery"):
        return False
    if experiment.get("analysis_goal") != "efficiency":
        return False
    if experiment.get("mode") != "squeeze":
        return False
    return True


def _llm_live_replicas(experiment: dict) -> int:
    obs = experiment.get("observed") or {}
    live_rep = int(obs.get("replicas") or 0)
    live_max = int(obs.get("replicas_max") or 0)
    return max(live_rep, live_max) if live_rep > 0 else live_max


def _llm_max_util_pct(experiment: dict) -> float:
    obs = experiment.get("observed") or {}
    return max(
        float(obs.get("cpu_util_pct") or 0.0),
        float(obs.get("mem_util_pct") or 0.0),
    )


def _llm_hot_replica_drop_required(experiment: dict) -> bool:
    """PASS with 3+ hot pods — must drop one replica this iteration."""
    if bool(((experiment.get("failure") or {}).get("failed"))):
        return False
    if _llm_live_replicas(experiment) < 3:
        return False
    threshold = float(os.environ.get("SQUEEZE_LLM_HOT_REPLICA_UTIL_PCT", "65"))
    return _llm_max_util_pct(experiment) >= threshold


def _llm_hot_multi_replica_burst(experiment: dict) -> bool:
    """Hot with 3+ pods — allow consecutive replica drops (match vanilla DOWN speed)."""
    return _llm_hot_replica_drop_required(experiment) or (
        _llm_live_replicas(experiment) >= 3 and _llm_max_util_pct(experiment) >= 55.0
    )


def _llm_hot_boundary_cpu_floor_m(experiment: dict) -> int:
    """Stop only after CPU request is trimmed near this floor (avoids fat 2-pod early stop)."""
    return int(os.environ.get("SQUEEZE_LLM_HOT_BOUNDARY_CPU_FLOOR_M", "65"))


def _llm_at_down_boundary_stop(experiment: dict) -> bool:
    """PASS at ≤2 pods near saturation — frontier reached; stop proposing further DOWN."""
    if bool(((experiment.get("failure") or {}).get("failed"))):
        return False
    if _llm_live_replicas(experiment) > 2:
        return False
    threshold = float(os.environ.get("SQUEEZE_LLM_HOT_BOUNDARY_UTIL_PCT", "85"))
    if _llm_max_util_pct(experiment) < threshold:
        return False
    cpu_m = int((experiment.get("config") or {}).get("cpu_request_m") or 0)
    if cpu_m > _llm_hot_boundary_cpu_floor_m(experiment):
        return False
    return True


def _llm_over_replicated_replica_required(experiment: dict) -> bool:
    """PASS squeeze-down should drop one replica this iteration (fat-start / over-provisioned)."""
    if bool(((experiment.get("failure") or {}).get("failed"))):
        return False
    prev = experiment.get("_prev_iteration") or {}
    prev_axis = (prev.get("squeeze_down_axis") or "").strip().lower()
    live = _llm_live_replicas(experiment)
    max_util = _llm_max_util_pct(experiment)
    if prev_axis == "replica" and not _llm_hot_multi_replica_burst(experiment):
        return False
    if live < 2:
        return False
    if max_util >= 55.0:
        return live >= 3
    cost = experiment.get("cost") or {}
    cost_score = float(cost.get("cost_score") or 0.0)
    if live >= 4 and max_util < 50.0:
        return True
    if live >= 3 and cost_score > 0.25:
        return True
    if (
        float((experiment.get("observed") or {}).get("cpu_util_pct") or 0.0) < 35.0
        and float((experiment.get("observed") or {}).get("mem_util_pct") or 0.0) < 35.0
        and live >= 3
    ):
        return True
    if live >= 3:
        return True
    return False


def _llm_replica_down_allowed(experiment: dict) -> bool:
    """Replica DOWN allowed when CPU is already trimmed, enough resource-only PASSes, or over-replicated."""
    if _llm_over_replicated_replica_required(experiment):
        return True
    cfg = experiment.get("config") or {}
    cpu_m = int(cfg.get("cpu_request_m") or 0)
    ceiling = int(os.environ.get("SQUEEZE_LLM_REPLICA_CPU_REQUEST_CEILING_M", "100"))
    min_passes = int(
        os.environ.get("SQUEEZE_LLM_MIN_RESOURCE_PASSES_BEFORE_REPLICA", "2")
    )
    prev = experiment.get("_prev_iteration") or {}
    streak = int(prev.get("resource_pass_streak") or 0)
    max_util = _llm_max_util_pct(experiment)
    live = _llm_live_replicas(experiment)
    if max_util >= 55.0:
        return live >= 3
    if cpu_m > 0 and cpu_m <= ceiling:
        return True
    return streak >= min_passes


def _down_cap_experiment(experiment: dict) -> dict:
    """cap_squeeze_down_replicas_and_hpa requires scaling_hint DOWN/HOLD."""
    hint = experiment.get("scaling_hint")
    if hint in {"DOWN", "HOLD"}:
        return experiment
    return {**experiment, "scaling_hint": "DOWN"}


def _apply_down_boundary_stop(
    result: dict,
    experiment: dict,
    deployment_yaml_path: Path,
    hpa_yaml_path: Path,
) -> bool:
    """Clear DOWN YAML when hot at ≤2 pods so the squeeze loop stops at best_pass.

    When SQUEEZE_UNTIL_VIOLATION is on (DOWN compare sweeps), do not stop early —
    keep nudging resources down until experiment_build records first_fail.
    """
    if not _llm_at_down_boundary_stop(experiment):
        if (
            _llm_live_replicas(experiment) <= 2
            and _llm_max_util_pct(experiment)
            >= float(os.environ.get("SQUEEZE_LLM_HOT_BOUNDARY_UTIL_PCT", "85"))
            and not (result.get("deployment_yaml_new") or "").strip()
        ):
            _pure_llm_resource_nudge(
                result, experiment, deployment_yaml_path, hpa_yaml_path
            )
            if (result.get("deployment_yaml_new") or "").strip():
                ev = list(result.get("evidence") or [])
                ev.append(
                    f"guard.hot_boundary_trim: cpu_m>{_llm_hot_boundary_cpu_floor_m(experiment)} "
                    f"max_util={_llm_max_util_pct(experiment):.0f}%"
                )
                result["evidence"] = ev
                return True
        return False
    if _squeeze_until_violation_active():
        if not (result.get("deployment_yaml_new") or "").strip():
            _pure_llm_resource_nudge(
                result, experiment, deployment_yaml_path, hpa_yaml_path
            )
        if (result.get("deployment_yaml_new") or "").strip():
            ev = list(result.get("evidence") or [])
            ev.append(
                f"guard.hot_boundary_continue_until_violation: live={_llm_live_replicas(experiment)} "
                f"max_util={_llm_max_util_pct(experiment):.0f}%"
            )
            result["evidence"] = ev
            return True
        return False
    result["deployment_yaml_new"] = ""
    result["hpa_yaml_new"] = ""
    ev = list(result.get("evidence") or [])
    ev.append(
        f"guard.hot_boundary_stop: live={_llm_live_replicas(experiment)} "
        f"max_util={_llm_max_util_pct(experiment):.0f}%"
    )
    result["evidence"] = ev
    return True


def _deployment_replicas_from_yaml_blob(
    blob: str, *, deployment_yaml_path: Path
) -> int | None:
    if blob.strip():
        try:
            doc = yaml.safe_load(blob)
            if isinstance(doc, dict) and doc.get("kind") == "Deployment":
                return int((doc.get("spec") or {}).get("replicas") or 0) or None
        except Exception:
            pass
    if deployment_yaml_path.exists():
        try:
            doc = yaml.safe_load(deployment_yaml_path.read_text())
            if isinstance(doc, dict) and doc.get("kind") == "Deployment":
                return int((doc.get("spec") or {}).get("replicas") or 0) or None
        except Exception:
            pass
    return None


def _align_down_hpa_max_to_deployment_replicas(
    result: dict,
    deployment_yaml_path: Path,
    hpa_yaml_path: Path,
) -> None:
    """Prevent HPA maxReplicas < deployment.spec.replicas (HPA must not lead replica drops)."""
    hpa_new = (result.get("hpa_yaml_new") or "").strip()
    if not hpa_new:
        return
    dep_rep = _deployment_replicas_from_yaml_blob(
        (result.get("deployment_yaml_new") or "").strip(),
        deployment_yaml_path=deployment_yaml_path,
    )
    if not dep_rep or dep_rep < 1:
        return
    try:
        hpa_doc = yaml.safe_load(hpa_new)
    except Exception:
        return
    if not isinstance(hpa_doc, dict) or hpa_doc.get("kind") != "HorizontalPodAutoscaler":
        return
    hspec = hpa_doc.setdefault("spec", {})
    old_max = int(hspec.get("maxReplicas") or dep_rep)
    if old_max >= dep_rep:
        return
    hspec["maxReplicas"] = dep_rep
    result["hpa_yaml_new"] = yaml.safe_dump(hpa_doc, sort_keys=False)
    ev = list(result.get("evidence") or [])
    ev.append(f"guard.hpa_max_not_below_dep_replicas:{old_max}->{dep_rep}")
    result["evidence"] = ev


def _finalize_vanilla_llm_squeeze_down(
    result: dict,
    experiment: dict,
    deployment_yaml_path: Path,
    hpa_yaml_path: Path,
) -> None:
    """Minimal DOWN guards for vanilla LLM (no advanced replica enforcement)."""
    if bool(((experiment.get("failure") or {}).get("failed"))):
        return
    if not _llm_squeeze_down_boundary_active(experiment):
        return
    _align_down_hpa_max_to_deployment_replicas(
        result, deployment_yaml_path, hpa_yaml_path
    )


def _container_requests(doc: dict) -> tuple[dict, dict]:
    spec = (doc.get("spec") or {}).setdefault("template", {}).setdefault("spec", {})
    containers = spec.get("containers") or []
    if not containers:
        return {}, {}
    res = (containers[0].get("resources") or {}).get("requests") or {}
    return res, (containers[0].get("resources") or {}).get("limits") or {}


def _yaml_increases_resources_vs_file(result: dict, deployment_yaml_path: Path) -> bool:
    """True when LLM YAML raises CPU and/or memory requests vs on-disk file."""
    dep_new = (result.get("deployment_yaml_new") or "").strip()
    if not dep_new or not deployment_yaml_path.exists():
        return False
    try:
        new_doc = yaml.safe_load(dep_new)
        old_doc = yaml.safe_load(deployment_yaml_path.read_text())
    except Exception:
        return False
    if not isinstance(new_doc, dict) or not isinstance(old_doc, dict):
        return False
    new_req, _ = _container_requests(new_doc)
    old_req, _ = _container_requests(old_doc)
    cpu_up = _millicpu_value(new_req.get("cpu")) > _millicpu_value(old_req.get("cpu"))
    mem_up = _mib_value(new_req.get("memory")) > _mib_value(old_req.get("memory"))
    return cpu_up or mem_up


def _restore_file_resources_in_result_yaml(
    result: dict, deployment_yaml_path: Path
) -> None:
    """Reset container resources in LLM YAML to on-disk values (PASS squeeze guard)."""
    if not deployment_yaml_path.exists():
        return
    file_dep = yaml.safe_load(deployment_yaml_path.read_text())
    if not isinstance(file_dep, dict) or file_dep.get("kind") != "Deployment":
        return
    file_spec = (file_dep.get("spec") or {}).setdefault("template", {}).setdefault(
        "spec", {}
    )
    file_containers = file_spec.get("containers") or []
    if not file_containers:
        return
    file_res = file_containers[0].get("resources") or {}

    dep_new = (result.get("deployment_yaml_new") or "").strip()
    dep_doc = yaml.safe_load(dep_new) if dep_new else yaml.safe_load(file_dep)
    if not isinstance(dep_doc, dict):
        dep_doc = yaml.safe_load(file_dep)
    tmpl = dep_doc.setdefault("spec", {}).setdefault("template", {}).setdefault("spec", {})
    containers = tmpl.get("containers") or []
    if not containers:
        return
    containers[0]["resources"] = yaml.safe_load(yaml.safe_dump(file_res))
    result["deployment_yaml_new"] = yaml.safe_dump(dep_doc, sort_keys=False)


def _yaml_lowers_resources_vs_file(result: dict, deployment_yaml_path: Path) -> bool:
    dep_new = (result.get("deployment_yaml_new") or "").strip()
    if not dep_new or not deployment_yaml_path.exists():
        return False
    try:
        new_doc = yaml.safe_load(dep_new)
        old_doc = yaml.safe_load(deployment_yaml_path.read_text())
    except Exception:
        return False
    if not isinstance(new_doc, dict) or not isinstance(old_doc, dict):
        return False
    new_req, _ = _container_requests(new_doc)
    old_req, _ = _container_requests(old_doc)
    cpu_down = _millicpu_value(new_req.get("cpu")) < _millicpu_value(old_req.get("cpu"))
    mem_down = _mib_value(new_req.get("memory")) < _mib_value(old_req.get("memory"))
    return cpu_down or mem_down


def _yaml_lowers_replicas_vs_file(
    result: dict, deployment_yaml_path: Path, hpa_yaml_path: Path
) -> bool:
    if not deployment_yaml_path.exists():
        return False
    try:
        file_rep = int(
            (yaml.safe_load(deployment_yaml_path.read_text()).get("spec") or {}).get(
                "replicas"
            )
            or 0
        )
    except Exception:
        return False
    dep_new = (result.get("deployment_yaml_new") or "").strip()
    if dep_new:
        try:
            proposed = int(
                (yaml.safe_load(dep_new).get("spec") or {}).get("replicas") or 0
            )
            if 0 < proposed < file_rep:
                return True
        except Exception:
            pass
    hpa_new = (result.get("hpa_yaml_new") or "").strip()
    file_max = file_rep
    if hpa_yaml_path.exists():
        try:
            file_max = int(
                (
                    yaml.safe_load(hpa_yaml_path.read_text()).get("spec") or {}
                ).get("maxReplicas")
                or file_rep
            )
        except Exception:
            file_max = file_rep
    if hpa_new:
        try:
            mx = int((yaml.safe_load(hpa_new).get("spec") or {}).get("maxReplicas") or 0)
            if 0 < mx < file_max:
                return True
        except Exception:
            pass
    return False


def _hold_replicas_in_result_yaml(
    result: dict,
    deployment_yaml_path: Path,
    hpa_yaml_path: Path,
) -> None:
    """Restore on-disk replica counts when a replica DOWN is vetoed (keep LLM CPU/mem)."""
    if not deployment_yaml_path.exists():
        return
    file_dep = yaml.safe_load(deployment_yaml_path.read_text())
    if not isinstance(file_dep, dict) or file_dep.get("kind") != "Deployment":
        return
    file_rep = int((file_dep.get("spec") or {}).get("replicas") or 1)

    dep_new = (result.get("deployment_yaml_new") or "").strip()
    dep_doc = yaml.safe_load(dep_new) if dep_new else yaml.safe_load(file_dep)
    if not isinstance(dep_doc, dict):
        dep_doc = yaml.safe_load(file_dep)
    dep_doc.setdefault("spec", {})["replicas"] = file_rep
    result["deployment_yaml_new"] = yaml.safe_dump(dep_doc, sort_keys=False)

    file_hpa = None
    if hpa_yaml_path.exists():
        try:
            file_hpa = yaml.safe_load(hpa_yaml_path.read_text())
        except Exception:
            file_hpa = None
    if not isinstance(file_hpa, dict) or file_hpa.get("kind") != "HorizontalPodAutoscaler":
        return
    file_max = int((file_hpa.get("spec") or {}).get("maxReplicas") or file_rep)
    hpa_new = (result.get("hpa_yaml_new") or "").strip()
    hpa_doc = yaml.safe_load(hpa_new) if hpa_new else yaml.safe_load(file_hpa)
    if not isinstance(hpa_doc, dict):
        hpa_doc = yaml.safe_load(file_hpa)
    hspec = hpa_doc.setdefault("spec", {})
    hspec["maxReplicas"] = max(file_max, file_rep)
    result["hpa_yaml_new"] = yaml.safe_dump(hpa_doc, sort_keys=False)


def _pure_llm_resource_nudge(
    result: dict,
    experiment: dict,
    deployment_yaml_path: Path,
    hpa_yaml_path: Path,
) -> None:
    """Small CPU/mem DOWN on file YAML when veto left no valid diff (safety only)."""
    if not deployment_yaml_path.exists():
        return
    step = _compute_step_pct({**experiment, "scaling_hint": "DOWN"})
    if step <= 0:
        step = float(os.environ.get("SQUEEZE_LLM_FALLBACK_DOWN_STEP_PCT", "0.10"))
        step = max(0.05, min(step, 0.30))
    factor = 1.0 - step
    dep_doc = yaml.safe_load(deployment_yaml_path.read_text())
    if not dep_doc or dep_doc.get("kind") != "Deployment":
        return
    spec = dep_doc.setdefault("spec", {})
    file_rep = int(spec.get("replicas") or 1)
    tmpl = spec.setdefault("template", {}).setdefault("spec", {})
    containers = tmpl.get("containers") or []
    if not containers:
        return
    if not _apply_resource_down_to_container(containers[0], factor):
        return
    spec["replicas"] = file_rep
    result["deployment_yaml_new"] = yaml.safe_dump(dep_doc, sort_keys=False)
    if hpa_yaml_path.exists():
        hpa_doc = yaml.safe_load(hpa_yaml_path.read_text())
        if hpa_doc and hpa_doc.get("kind") == "HorizontalPodAutoscaler":
            hspec = hpa_doc.setdefault("spec", {})
            hspec["maxReplicas"] = max(
                int(hspec.get("maxReplicas") or file_rep), file_rep
            )
            result["hpa_yaml_new"] = yaml.safe_dump(hpa_doc, sort_keys=False)
    ev = list(result.get("evidence") or [])
    ev.append(f"guard.resource_nudge:step_pct={step:.3f}")
    result["evidence"] = ev


def _infer_applied_squeeze_down_axis(
    result: dict, deployment_yaml_path: Path, hpa_yaml_path: Path
) -> str:
    if _yaml_lowers_replicas_vs_file(result, deployment_yaml_path, hpa_yaml_path):
        return "replica"
    if _yaml_lowers_resources_vs_file(result, deployment_yaml_path):
        return "resources"
    return "resources"


def _compute_resource_pass_streak(experiment: dict, applied_axis: str) -> int:
    prev = experiment.get("_prev_iteration") or {}
    prev_streak = int(prev.get("resource_pass_streak") or 0)
    if applied_axis == "resources":
        return prev_streak + 1
    return 0


def _veto_llm_pure_squeeze_down(
    result: dict,
    experiment: dict,
    deployment_yaml_path: Path,
    hpa_yaml_path: Path,
) -> None:
    """Keep LLM sizing; veto illegal replica steps and ensure a DOWN diff remains."""
    has_yaml = bool(
        (result.get("deployment_yaml_new") or "").strip()
        or (result.get("hpa_yaml_new") or "").strip()
    )
    if not has_yaml:
        return

    resource_up_vetoed = False
    rejected_dep = ""
    rejected_hpa = ""
    # Pure-LLM finalize only runs on PASS: block mistaken 25m→100m "trim" upsizes.
    if _yaml_increases_resources_vs_file(result, deployment_yaml_path):
        rejected_dep = (result.get("deployment_yaml_new") or "").strip()
        rejected_hpa = (result.get("hpa_yaml_new") or "").strip()
        _restore_file_resources_in_result_yaml(result, deployment_yaml_path)
        resource_up_vetoed = True
        ev = list(result.get("evidence") or [])
        ev.append("guard.veto_pass_resource_up")
        result["evidence"] = ev

    prev_axis = (
        (experiment.get("_prev_iteration") or {}).get("squeeze_down_axis") or ""
    ).strip().lower()
    intends_replica = _llm_intends_replica_down(result, experiment)
    veto_reasons: list[str] = []
    if intends_replica and prev_axis == "replica" and not _llm_hot_multi_replica_burst(
        experiment
    ):
        veto_reasons.append("back_to_back_replica")
    if intends_replica and not _llm_replica_down_allowed(experiment):
        veto_reasons.append("resource_phase_gate")

    if veto_reasons:
        _hold_replicas_in_result_yaml(result, deployment_yaml_path, hpa_yaml_path)
        ev = list(result.get("evidence") or [])
        ev.append(f"guard.veto_replica_down:{','.join(veto_reasons)}")
        result["evidence"] = ev
        if not _yaml_lowers_resources_vs_file(result, deployment_yaml_path):
            if not _llm_at_down_boundary_stop(experiment):
                _pure_llm_resource_nudge(
                    result, experiment, deployment_yaml_path, hpa_yaml_path
                )

    if _yaml_noop_vs_managed_paths(result, deployment_yaml_path, hpa_yaml_path):
        repaired_ok = False
        if resource_up_vetoed and (rejected_dep or rejected_hpa):
            repaired_ok = _repair_pure_llm_vetoed_resource_up(
                result,
                experiment,
                deployment_yaml_path,
                hpa_yaml_path,
                rejected_deployment_yaml=rejected_dep,
                rejected_hpa_yaml=rejected_hpa,
            )
            if repaired_ok:
                ev = list(result.get("evidence") or [])
                ev.append("guard.llm_repair_veto_pass_resource_up")
                result["evidence"] = ev
        if not repaired_ok and not _yaml_lowers_resources_vs_file(
            result, deployment_yaml_path
        ):
            _pure_llm_resource_nudge(
                result, experiment, deployment_yaml_path, hpa_yaml_path
            )

    applied_axis = _infer_applied_squeeze_down_axis(
        result, deployment_yaml_path, hpa_yaml_path
    )
    result["squeeze_down_axis"] = applied_axis
    result["resource_pass_streak"] = _compute_resource_pass_streak(
        experiment, applied_axis
    )
    ev = list(result.get("evidence") or [])
    ev.append(f"squeeze_down_axis={applied_axis}")
    result["evidence"] = ev


def _pure_llm_reconcile_replica_drift(
    result: dict,
    experiment: dict,
    deployment_yaml_path: Path,
    hpa_yaml_path: Path,
) -> bool:
    """Emit YAML to converge live replica overshoot to managed config (pure LLM path)."""
    if not _live_replica_drift(experiment):
        return False
    cfg_rep = int((experiment.get("config") or {}).get("deployment_replicas") or 0)
    if cfg_rep < 1 or not deployment_yaml_path.exists():
        return False
    try:
        dep_doc = yaml.safe_load(deployment_yaml_path.read_text())
    except Exception:
        return False
    if not isinstance(dep_doc, dict) or dep_doc.get("kind") != "Deployment":
        return False
    dep_doc.setdefault("spec", {})["replicas"] = cfg_rep
    result["deployment_yaml_new"] = yaml.safe_dump(dep_doc, sort_keys=False)
    if hpa_yaml_path.exists():
        try:
            hpa_doc = yaml.safe_load(hpa_yaml_path.read_text())
            if isinstance(hpa_doc, dict) and hpa_doc.get("kind") == "HorizontalPodAutoscaler":
                hspec = hpa_doc.setdefault("spec", {})
                hspec["maxReplicas"] = cfg_rep
                hspec["minReplicas"] = min(int(hspec.get("minReplicas") or 1), cfg_rep)
                result["hpa_yaml_new"] = yaml.safe_dump(hpa_doc, sort_keys=False)
        except Exception:
            pass
    ev = list(result.get("evidence") or [])
    ev.append(f"guard.pure_llm_reconcile_drift:target_replicas={cfg_rep}")
    result["evidence"] = ev
    return True


def _finalize_llm_squeeze_down(
    result: dict,
    experiment: dict,
    deployment_yaml_path: Path,
    hpa_yaml_path: Path,
) -> None:
    """Post-LLM guards for DOWN boundary (pure LLM: replica clamp only; hybrid: formula fallbacks)."""
    if bool(((experiment.get("failure") or {}).get("failed"))):
        return
    if not _llm_squeeze_down_boundary_active(experiment):
        return

    from .k8s_manifest import (
        cap_squeeze_down_replicas_and_hpa,
        clamp_llm_squeeze_replicas_to_one_step,
    )

    pure = (
        experiment.get("squeeze_optimizer") == "llm" and _llm_pure_squeeze()
    )

    drift = _live_replica_drift(experiment)
    has_yaml = bool(
        (result.get("deployment_yaml_new") or "").strip()
        or (result.get("hpa_yaml_new") or "").strip()
    )

    # YAML already says N replicas but the cluster still runs more — LLM "no-op" patches are not enough.
    if drift and has_yaml and not _llm_intends_replica_down(result, experiment):
        result["deployment_yaml_new"] = ""
        result["hpa_yaml_new"] = ""
        has_yaml = False
        ev = list(result.get("evidence") or [])
        ev.append(
            f"guard.clear_yaml_live_drift: live={(experiment.get('observed') or {}).get('replicas')} "
            f"config_rep={(experiment.get('config') or {}).get('deployment_replicas')}"
        )
        result["evidence"] = ev

    if pure:
        # Hybrid path uses cap_squeeze + formula fallback; pure LLM must not stall on drift.
        if _live_replica_drift(experiment) and not has_yaml:
            if _pure_llm_reconcile_replica_drift(
                result, experiment, deployment_yaml_path, hpa_yaml_path
            ):
                has_yaml = True
            else:
                drift_exp = {**experiment, "scaling_hint": "DOWN"}
                cap_squeeze_down_replicas_and_hpa(
                    result,
                    drift_exp,
                    deployment_yaml_path=deployment_yaml_path,
                    hpa_yaml_path=hpa_yaml_path,
                )
                has_yaml = bool(
                    (result.get("deployment_yaml_new") or "").strip()
                    or (result.get("hpa_yaml_new") or "").strip()
                )
        if _llm_hot_replica_drop_required(experiment):
            if cap_squeeze_down_replicas_and_hpa(
                result,
                _down_cap_experiment(experiment),
                deployment_yaml_path=deployment_yaml_path,
                hpa_yaml_path=hpa_yaml_path,
            ):
                ev = list(result.get("evidence") or [])
                ev.append("guard.enforce_hot_replica_drop")
                result["evidence"] = ev
        elif _llm_over_replicated_replica_required(experiment) and not _llm_intends_replica_down(
            result, experiment
        ):
            if cap_squeeze_down_replicas_and_hpa(
                result,
                _down_cap_experiment(experiment),
                deployment_yaml_path=deployment_yaml_path,
                hpa_yaml_path=hpa_yaml_path,
            ):
                ev = list(result.get("evidence") or [])
                ev.append("guard.enforce_over_replicated_replica")
                result["evidence"] = ev
        if (result.get("deployment_yaml_new") or "").strip():
            clamp_llm_squeeze_replicas_to_one_step(
                result,
                experiment,
                deployment_yaml_path=deployment_yaml_path,
                hpa_yaml_path=hpa_yaml_path,
            )
        _veto_llm_pure_squeeze_down(
            result, experiment, deployment_yaml_path, hpa_yaml_path
        )
        if _needs_pure_llm_down_repair(
            result, experiment, deployment_yaml_path, hpa_yaml_path
        ):
            _repair_pure_llm_squeeze_down_yaml(
                result, experiment, deployment_yaml_path, hpa_yaml_path
            )
            if (result.get("deployment_yaml_new") or "").strip():
                clamp_llm_squeeze_replicas_to_one_step(
                    result,
                    experiment,
                    deployment_yaml_path=deployment_yaml_path,
                    hpa_yaml_path=hpa_yaml_path,
                )
            _veto_llm_pure_squeeze_down(
                result, experiment, deployment_yaml_path, hpa_yaml_path
            )
        _apply_down_boundary_stop(
            result, experiment, deployment_yaml_path, hpa_yaml_path
        )
        return

    if drift or _squeeze_should_cap_replicas(experiment, result):
        cap_squeeze_down_replicas_and_hpa(
            result,
            _down_cap_experiment(experiment),
            deployment_yaml_path=deployment_yaml_path,
            hpa_yaml_path=hpa_yaml_path,
        )
        has_yaml = bool(
            (result.get("deployment_yaml_new") or "").strip()
            or (result.get("hpa_yaml_new") or "").strip()
        )

    if drift or not has_yaml:
        _maybe_apply_deterministic_efficiency_yaml(
            result, experiment, deployment_yaml_path, hpa_yaml_path
        )
        if (result.get("deployment_yaml_new") or "").strip() or (
            result.get("hpa_yaml_new") or ""
        ).strip():
            ev = list(result.get("evidence") or [])
            ev.append("fallback.deterministic_down_step")
            result["evidence"] = ev
            return

    if not (result.get("deployment_yaml_new") or "").strip() and not (
        result.get("hpa_yaml_new") or ""
    ).strip():
        _ensure_llm_squeeze_minimal_down_fallback(
            result, experiment, deployment_yaml_path, hpa_yaml_path
        )


def _ensure_llm_squeeze_minimal_down_fallback(
    result: dict,
    experiment: dict,
    deployment_yaml_path: Path,
    hpa_yaml_path: Path,
) -> None:
    """Last-resort CPU/mem DOWN when LLM + deterministic produced no YAML."""
    # Telemetry not trustworthy: still apply a minimal DOWN on current repo YAML so the loop can continue.
    step = float(os.environ.get("SQUEEZE_LLM_FALLBACK_DOWN_STEP_PCT", "0.10"))
    step = max(0.05, min(step, 0.30))
    factor = 1.0 - step
    if deployment_yaml_path.exists():
        dep_doc = yaml.safe_load(deployment_yaml_path.read_text())
        if dep_doc and dep_doc.get("kind") == "Deployment":
            spec = dep_doc.setdefault("spec", {})
            tmpl = spec.setdefault("template", {}).setdefault("spec", {})
            containers = tmpl.get("containers") or []
            if containers:
                c0 = containers[0]
                res = c0.setdefault("resources", {})
                req = res.setdefault("requests", {})
                lim = res.setdefault("limits", {})
                req["cpu"] = _scale_millicpu(req.get("cpu", "100m"), factor)
                lim["cpu"] = _scale_millicpu(lim.get("cpu", "200m"), factor)
                req["memory"] = _scale_mib(req.get("memory", "50Mi"), factor)
                lim["memory"] = _scale_mib(lim.get("memory", "100Mi"), factor)
                result["deployment_yaml_new"] = yaml.safe_dump(dep_doc, sort_keys=False)
    if hpa_yaml_path.exists():
        hpa_doc = yaml.safe_load(hpa_yaml_path.read_text())
        if hpa_doc and hpa_doc.get("kind") == "HorizontalPodAutoscaler":
            spec = hpa_doc.setdefault("spec", {})
            min_r = int(spec.get("minReplicas") or 1)
            max_r = int(spec.get("maxReplicas") or max(min_r, 2))
            delta = max(1, int(math.ceil(max_r * step * 0.5)))
            spec["maxReplicas"] = max(min_r + 1, max_r - delta)
            result["hpa_yaml_new"] = yaml.safe_dump(hpa_doc, sort_keys=False)
    if (result.get("deployment_yaml_new") or "").strip() or (result.get("hpa_yaml_new") or "").strip():
        ev = list(result.get("evidence") or [])
        ev.append(f"fallback.minimal_down_step_pct={step}")
        result["evidence"] = ev


def _postprocess_llm_result(result: dict, experiment: dict) -> dict:
    """
    Apply deterministic safety checks so the output cannot contradict the input metrics.
    """
    _normalize_llm_yaml_fields(result)
    down_boundary = _llm_squeeze_down_boundary_active(experiment)

    if (
        not down_boundary
        and experiment.get("scaling_hint") == "UNKNOWN"
        and experiment.get("analysis_goal") == "efficiency"
    ):
        result["deployment_yaml_new"] = ""
        result["hpa_yaml_new"] = ""
        result["optimization_headroom"] = result.get("optimization_headroom") or "NONE"

    observed = experiment.get("observed") or {}
    failure = experiment.get("failure") or {}
    slo = experiment.get("slo") or {}

    # In efficiency squeeze mode, a HOLD hint means "do not move" unless failure forces UP.
    # Guard against unsafe scale-down when utilization is already high (can cause connection refused / OOM).
    if (
        not down_boundary
        and experiment.get("analysis_goal") == "efficiency"
        and experiment.get("scaling_hint") == "HOLD"
    ):
        tel = (observed.get("telemetry") or {})
        if tel.get("utilization_trustworthy"):
            cpu_util_pct = float(observed.get("cpu_util_pct") or 0.0)
            mem_util_pct = float(observed.get("mem_util_pct") or 0.0)
            cpu_util_to_limit = float(observed.get("cpu_util_to_limit") or 0.0)
            util = max(cpu_util_pct, mem_util_pct)
            if util >= 80.0 or cpu_util_to_limit >= 0.9:
                # If already failing, allow UP adjustments to proceed; otherwise block YAML changes.
                if not bool(failure.get("failed")):
                    result["deployment_yaml_new"] = ""
                    result["hpa_yaml_new"] = ""
                    result["optimization_headroom"] = "NONE"
                    ev = list(result.get("evidence") or [])
                    ev.append(
                        f"guard.hold_blocked_yaml: util={util:.1f} cpu_util_to_limit={cpu_util_to_limit:.2f}"
                    )
                    result["evidence"] = ev

    # SLO FAIL + UP hint: block net scale-down YAML (LLM often misreads high util as over-provisioned).
    if (
        not down_boundary
        and experiment.get("analysis_goal") == "efficiency"
        and bool(failure.get("failed"))
        and experiment.get("scaling_hint") == "UP"
    ):
        dep_new = (result.get("deployment_yaml_new") or "").strip()
        hpa_new = (result.get("hpa_yaml_new") or "").strip()
        if dep_new or hpa_new:
            try:
                cfg = experiment.get("config") or {}
                cur_cpu = int(cfg.get("cpu_request_m") or 0)
                cur_mem = int(cfg.get("mem_request_mib") or 0)
                cur_repl = int(cfg.get("deployment_replicas") or 1)
                new_doc = yaml.safe_load(dep_new) if dep_new else {}
                new_cpu = cur_cpu
                new_mem = cur_mem
                new_repl = cur_repl
                if new_doc and new_doc.get("kind") == "Deployment":
                    c0 = ((new_doc.get("spec") or {}).get("template") or {}).get(
                        "spec", {}
                    ).get("containers", [{}])[0]
                    req = (c0.get("resources") or {}).get("requests") or {}
                    new_cpu = _millicpu_value(req.get("cpu")) or cur_cpu
                    new_mem = _mib_value(req.get("memory")) or cur_mem
                    new_repl = int((new_doc.get("spec") or {}).get("replicas") or cur_repl)
                hpa_doc = yaml.safe_load(hpa_new) if hpa_new else {}
                new_hpa_max = int(
                    ((hpa_doc.get("spec") or {}).get("maxReplicas") or cur_repl)
                )
                net_down = (
                    new_cpu < cur_cpu
                    or new_mem < cur_mem
                    or new_repl < cur_repl
                    or new_hpa_max < cur_repl
                )
                if net_down:
                    result["deployment_yaml_new"] = ""
                    result["hpa_yaml_new"] = ""
                    ev = list(result.get("evidence") or [])
                    ev.append(
                        "guard.veto_fail_up_hint_scale_down: "
                        f"cpu {cur_cpu}->{new_cpu}m mem {cur_mem}->{new_mem}Mi repl {cur_repl}->{new_repl}"
                    )
                    result["evidence"] = ev
            except Exception:
                pass

    # LLM-only squeeze safety bias (disabled during DOWN boundary compare — must reach first_fail).
    if (
        not down_boundary
        and experiment.get("analysis_goal") == "efficiency"
        and experiment.get("squeeze_optimizer") == "llm"
        and not bool(failure.get("failed"))
    ):
        cpu_util_pct = float(observed.get("cpu_util_pct") or 0.0)
        curr_p95 = float((observed.get("latency_ms") or {}).get("p95") or 0.0)
        cpu_guard_pct = float(os.environ.get("SQUEEZE_LLM_CPU_GUARD_PCT", "85"))
        p95_guard_ratio = float(os.environ.get("SQUEEZE_LLM_P95_REGRESSION_RATIO", "1.2"))
        prev = experiment.get("_prev_iteration") or {}
        prev_ok = prev.get("slo_status") == "PASS"
        prev_p95 = float(prev.get("latency_ms_p95") or 0.0)
        p95_regressed = bool(prev_ok and prev_p95 > 0 and curr_p95 > (prev_p95 * p95_guard_ratio))
        cpu_hot = cpu_util_pct >= cpu_guard_pct
        if cpu_hot or p95_regressed:
            result["deployment_yaml_new"] = ""
            result["hpa_yaml_new"] = ""
            result["optimization_headroom"] = "NONE"
            ev = list(result.get("evidence") or [])
            ev.append(
                "guard.llm_early_stop: "
                f"cpu_util_pct={cpu_util_pct:.1f} (>= {cpu_guard_pct:.1f}) "
                f"p95_curr={curr_p95:.2f} p95_prev={prev_p95:.2f} ratio={p95_guard_ratio:.2f}"
            )
            result["evidence"] = ev

    # If failure is only due to k6 thresholds (stricter than SLO) and SLO is actually met,
    # treat as no bottleneck to avoid bogus archetypes.
    p95 = (observed.get("latency_ms") or {}).get("p95")
    err = observed.get("error_rate")
    slo_p95 = slo.get("p95_latency_ms")
    slo_err = slo.get("error_rate")
    slo_violated = False
    if p95 is not None and slo_p95 is not None and p95 > slo_p95:
        slo_violated = True
    if err is not None and slo_err is not None and err > slo_err:
        slo_violated = True
    if failure.get("reason") == "k6_thresholds_crossed" and not slo_violated:
        result["failure_archetype"] = "NONE"

    # Enforce AUTOSCALER_LAG prerequisites (never allow it with low CPU signal).
    cpu_util_pct = observed.get("cpu_util_pct") or 0
    cpu_util_to_limit = observed.get("cpu_util_to_limit") or 0
    if result.get("failure_archetype") == "AUTOSCALER_LAG":
        if cpu_util_pct < 50 and cpu_util_to_limit < 0.7:
            # Prefer dependency saturation when CPU/mem are low and latency is high; else UNKNOWN.
            mem_util_pct = observed.get("mem_util_pct") or 0
            if (
                (cpu_util_pct < 30)
                and (mem_util_pct < 30)
                and (p95 is not None)
                and (slo_p95 is not None)
                and (p95 > slo_p95)
            ):
                result["failure_archetype"] = "DEPENDENCY_SATURATION"
            else:
                result["failure_archetype"] = "UNKNOWN"

    # Ensure evidence always includes replicas & replicas_max when present.
    evidence = list(result.get("evidence") or [])
    if observed.get("replicas") is not None and not any(
        "observed.replicas:" in e for e in evidence
    ):
        evidence.append(f"observed.replicas: {observed.get('replicas')}")
    if observed.get("replicas_max") is not None and not any(
        "observed.replicas_max:" in e for e in evidence
    ):
        evidence.append(f"observed.replicas_max: {observed.get('replicas_max')}")
    result["evidence"] = evidence

    # If UNKNOWN, do not allow YAML changes (failure-diagnosis mode only).
    if (
        result.get("failure_archetype") == "UNKNOWN"
        and experiment.get("analysis_goal") != "efficiency"
    ):
        result["deployment_yaml_new"] = ""
        result["hpa_yaml_new"] = ""

    # If NONE, YAML changes are optional (scale-down). But if model returned YAML, keep it.
    return result


def _resolve_squeeze_optimizer(meta: dict | None, experiment_config: dict | None) -> str:
    opt = None
    if meta:
        opt = meta.get("squeeze_optimizer")
    if opt is None and experiment_config:
        opt = experiment_config.get("squeeze_optimizer")
    if opt is None:
        opt = os.environ.get("SQUEEZE_OPTIMIZER", "hybrid")
    opt = str(opt).lower().strip()
    if opt not in {"hybrid", "formula", "llm", "hpa"}:
        opt = "hybrid"
    return opt


def _replay_observe_result(experiment: dict) -> dict:
    """Replay arm: same config re-tested; metrics only, no optimizer."""
    obs = experiment.get("observed") or {}
    cfg = experiment.get("config") or {}
    slo = _slo_status_from_experiment(experiment)
    failed = bool((experiment.get("failure") or {}).get("failed"))
    burn = obs.get("cpu_usage_avg_m")
    cpu_pct = obs.get("cpu_util_request_pct")
    lines = [
        "## Replay observe-only",
        "",
        "- **Optimizer**: replay (no YAML change; config applied before k6).",
        f"- **SLO**: {slo}; failed={failed}",
        f"- **Config**: {cfg.get('cpu_request_m')}m CPU, {cfg.get('mem_request_mib')} MiB, "
        f"{cfg.get('deployment_replicas')} repl",
        f"- **cpu_usage_avg_m**: {burn}; **cpu_util_request_pct**: {cpu_pct}",
    ]
    return {
        "report": "\n".join(lines),
        "deployment_yaml_new": "",
        "hpa_yaml_new": "",
        "failure_archetype": (experiment.get("failure") or {}).get("reason") or "none",
        "optimization_headroom": "NONE",
        "evidence": ["optimizer.replay_observe"],
    }


def _hpa_only_result(experiment: dict) -> dict:
    """HPA-only arm: observe after one load window; no YAML tuning."""
    obs = experiment.get("observed") or {}
    cfg = experiment.get("config") or {}
    slo = _slo_status_from_experiment(experiment)
    failed = bool((experiment.get("failure") or {}).get("failed"))
    rep = obs.get("replicas")
    rep_max = obs.get("replicas_max") or rep
    lines = [
        "## HPA-only evaluation",
        "",
        "- **Optimizer**: Kubernetes HPA (replica scaling only; CPU/memory requests fixed).",
        f"- **SLO**: {slo}; failed={failed}",
        f"- **Observed replicas**: {rep} (max during window: {rep_max})",
        f"- **CPU request**: {cfg.get('cpu_request_m')}m; **mem request**: {cfg.get('mem_request_mib')} MiB",
        "- No deployment/HPA YAML changes for the next iteration (single-shot arm).",
    ]
    return {
        "report": "\n".join(lines),
        "deployment_yaml_new": "",
        "hpa_yaml_new": "",
        "failure_archetype": (experiment.get("failure") or {}).get("reason") or "none",
        "optimization_headroom": "NONE",
        "evidence": ["optimizer.hpa_only"],
    }


def _formula_only_result(
    experiment: dict,
    deployment_yaml_path: Path,
    hpa_yaml_path: Path,
) -> dict:
    """Deterministic squeeze step: no LLM; YAML comes only from _maybe_apply_deterministic_efficiency_yaml."""
    step = _compute_step_pct(experiment)
    hint = experiment.get("scaling_hint")
    tel = ((experiment.get("observed") or {}).get("telemetry") or {})
    trustworthy = bool(tel.get("utilization_trustworthy"))
    slo_ok = _slo_status_from_experiment(experiment)
    eff = hint
    if hint == "HOLD":
        failed = bool(((experiment.get("failure") or {}).get("failed")))
        eff = "UP" if failed else "DOWN"
    lines = [
        f"- **Optimizer**: deterministic formula (no LLM for YAML this iteration).",
        f"- **SLO**: {slo_ok}; scaling_hint={hint}; effective_direction={eff}; step_pct={step}",
        f"- **Utilization trustworthy**: {trustworthy}",
    ]
    if not trustworthy:
        lines.append("- Telemetry not trustworthy for utilization-based steps; no YAML unless policy allows.")
    elif eff not in {"UP", "DOWN"}:
        lines.append("- No resource step: scaling_hint does not map to UP/DOWN.")
    else:
        lines.append(
            f"- Applying **{eff}** step ~{step * 100:.1f}% on requests/limits and HPA (deterministic)."
        )
    result = {
        "report": "\n".join(lines),
        "deployment_yaml_new": "",
        "hpa_yaml_new": "",
        "failure_archetype": "NONE",
        "lambda_crit_estimate": None,
        "next_experiment": "Re-run the same fixed workload after applying YAML.",
        "optimization_headroom": "MEDIUM" if slo_ok == "PASS" and hint == "DOWN" else "NONE",
        "over_provisioned": slo_ok == "PASS",
        "evidence": [
            f"formula.step_pct={step}",
            f"formula.scaling_hint={hint}",
        ],
    }
    result = _postprocess_llm_result(result, experiment)
    _maybe_apply_deterministic_efficiency_yaml(
        result, experiment, deployment_yaml_path, hpa_yaml_path
    )
    return result


def _bound(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _in_up_recovery_path(experiment: dict) -> bool:
    if experiment.get("up_recovery"):
        return True
    failure = experiment.get("failure") or {}
    return bool(failure.get("failed")) and experiment.get("scaling_hint") == "UP"


def _load_deployment_doc(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        doc = yaml.safe_load(path.read_text())
    except Exception:
        return None
    return doc if isinstance(doc, dict) and doc.get("kind") == "Deployment" else None


def _deployment_container_blocks(doc: dict) -> tuple[dict, dict, dict] | None:
    template_spec = ((doc.get("spec") or {}).get("template") or {}).get("spec") or {}
    containers = template_spec.get("containers") or []
    if not containers:
        return None
    c0 = containers[0]
    res = c0.setdefault("resources", {})
    return c0, res.setdefault("requests", {}), res.setdefault("limits", {})


def _metric_up_step_from_file(
    experiment: dict,
    deployment_yaml_path: Path,
    *,
    step_override: float | None = None,
) -> dict[str, int] | None:
    """One UP step from on-disk deployment using observed metrics (squeeze step math only)."""
    doc = _load_deployment_doc(deployment_yaml_path)
    blocks = _deployment_container_blocks(doc) if doc else None
    if not blocks:
        return None
    _, req, lim = blocks
    step = (
        step_override
        if step_override is not None
        else _compute_step_pct({**experiment, "scaling_hint": "UP"})
    )
    if step <= 0:
        return None
    factor = 1.0 + step
    return {
        "cpu_req": max(
            1, int(math.ceil(_millicpu_value(req.get("cpu", "50m")) * factor))
        ),
        "cpu_lim": max(
            1, int(math.ceil(_millicpu_value(lim.get("cpu", "100m")) * factor))
        ),
        "mem_req": max(1, int(math.ceil(_mib_value(req.get("memory", "25Mi")) * factor))),
        "mem_lim": max(
            1, int(math.ceil(_mib_value(lim.get("memory", "50Mi")) * factor))
        ),
        "replicas": int((doc.get("spec") or {}).get("replicas") or 1),
    }


def _up_recovery_replica_eligible(experiment: dict) -> bool:
    """Single-pod UP recovery may add at most one replica (capped by env)."""
    if not _in_up_recovery_path(experiment):
        return False
    if not bool(((experiment.get("failure") or {}).get("failed"))):
        return False
    cfg = experiment.get("config") or {}
    dep_rep = int(cfg.get("deployment_replicas") or 1)
    hpa_max = int((cfg.get("hpa") or {}).get("max_replicas") or dep_rep)
    max_rep = int(os.environ.get("SQUEEZE_UP_RECOVERY_MAX_REPLICAS", "6"))
    if dep_rep >= max_rep or hpa_max >= max_rep:
        return False
    if dep_rep > 1 or hpa_max > 1:
        return False
    return True


def _up_recovery_throughput_ratio_floor() -> float:
    return float(os.environ.get("SQUEEZE_UP_THROUGHPUT_RATIO_FLOOR", "0.85"))


def _up_recovery_ratios(experiment: dict) -> dict[str, float]:
    """Load-normalized signals (work for any target RPS)."""
    obs = experiment.get("observed") or {}
    slo = experiment.get("slo") or {}
    wl = experiment.get("workload") or {}
    target = float(wl.get("target_requests_per_second") or 0)
    ach = float(
        obs.get("achieved_requests_per_second_target_window")
        or obs.get("achieved_requests_per_second")
        or 0
    )
    p95 = float((obs.get("latency_ms") or {}).get("p95") or 0)
    slo_p95 = float(slo.get("p95_latency_ms") or 500)
    throughput_ratio = (ach / target) if target > 0 else 1.0
    latency_ratio = (p95 / slo_p95) if slo_p95 > 0 and p95 > 0 else 0.0
    return {
        "target_rps": target,
        "achieved_rps": ach,
        "throughput_ratio": throughput_ratio,
        "latency_ratio": latency_ratio,
        "p95_ms": p95,
        "slo_p95_ms": slo_p95,
        "cpu_util_pct": float(obs.get("cpu_util_pct") or 0.0),
        "mem_util_pct": float(obs.get("mem_util_pct") or 0.0),
        "cpu_util_to_limit": float(obs.get("cpu_util_to_limit") or 0.0),
    }


def _up_recovery_bottleneck(experiment: dict) -> str:
    """Primary UP axis from observed ratios (not hardcoded RPS)."""
    r = _up_recovery_ratios(experiment)
    thr_floor = _up_recovery_throughput_ratio_floor()
    if r["throughput_ratio"] < thr_floor:
        return "throughput"
    if r["mem_util_pct"] >= 100.0:
        return "memory"
    if r["cpu_util_pct"] >= 85.0 or r["cpu_util_to_limit"] >= 0.85:
        return "cpu"
    if r["latency_ratio"] > 1.0:
        return "latency"
    return "balanced"


def _attach_up_recovery_signals(experiment: dict) -> None:
    if not _in_up_recovery_path(experiment):
        return
    ratios = _up_recovery_ratios(experiment)
    bottleneck = _up_recovery_bottleneck(experiment)
    prefer_replica = _up_recovery_prefers_replica_step(experiment)
    experiment["up_recovery_signals"] = {
        **ratios,
        "bottleneck": bottleneck,
        "prefer_replica_step": prefer_replica,
        "throughput_ratio_floor": _up_recovery_throughput_ratio_floor(),
    }


def _up_recovery_throughput_near_target(experiment: dict) -> bool:
    return _up_recovery_ratios(experiment)["throughput_ratio"] >= _up_recovery_throughput_ratio_floor()


def _up_recovery_latency_slo_met(experiment: dict) -> bool:
    """p95 and throughput OK but row may still FAIL on cpu_util_request_pct gate."""
    r = _up_recovery_ratios(experiment)
    return (
        r["p95_ms"] <= r["slo_p95_ms"]
        and r["throughput_ratio"] >= _up_recovery_throughput_ratio_floor()
    )


def _up_recovery_prefers_replica_step(experiment: dict) -> bool:
    """+1 replica when single-pod UP recovery needs horizontal headroom (any target RPS)."""
    if not _up_recovery_replica_eligible(experiment):
        return False
    if not bool(((experiment.get("failure") or {}).get("failed"))):
        return False
    r = _up_recovery_ratios(experiment)
    thr_floor = _up_recovery_throughput_ratio_floor()
    # Throughput already near target but latency still failing → scale out.
    if r["throughput_ratio"] >= thr_floor:
        return True
    # Throughput collapse at single pod → scale out before oversized vertical-only jumps.
    return r["throughput_ratio"] < thr_floor


def _sync_up_recovery_hpa_after_vertical(
    result: dict,
    experiment: dict,
    dep_doc: dict,
    hpa_doc: dict | None,
    step: float,
) -> None:
    """After vertical UP: raise HPA max/min headroom only (do not pin deployment replicas)."""
    if not hpa_doc or hpa_doc.get("kind") != "HorizontalPodAutoscaler":
        return
    if not _in_up_recovery_path(experiment):
        return
    hspec = hpa_doc.setdefault("spec", {})
    min_r = int(hspec.get("minReplicas") or 1)
    max_r = int(hspec.get("maxReplicas") or max(min_r, 2))
    delta = max(1, int(math.ceil(max_r * step * 0.5)))
    new_max = min(
        int(os.environ.get("SQUEEZE_UP_RECOVERY_MAX_REPLICAS", "6")),
        max_r + delta,
    )
    if new_max <= max_r:
        return
    hspec["maxReplicas"] = new_max
    obs = experiment.get("observed") or {}
    obs_rep = int(obs.get("replicas") or 0)
    obs_max = int(obs.get("replicas_max") or 0)
    floor = max(min_r, obs_rep, obs_max, min_r + 1)
    hspec["minReplicas"] = min(new_max, floor)
    result["hpa_yaml_new"] = yaml.safe_dump(hpa_doc, sort_keys=False)
    # Do not set deployment.spec.replicas = maxReplicas (cost blow-up; let HPA scale).


def _apply_up_recovery_replica_step(
    result: dict,
    experiment: dict,
    deployment_yaml_path: Path,
    hpa_yaml_path: Path,
    *,
    evidence_tag: str,
) -> bool:
    """Bump deployment replicas and HPA max together (UP recovery)."""
    if not _up_recovery_prefers_replica_step(experiment):
        return False
    dep_doc = None
    pending = (result.get("deployment_yaml_new") or "").strip()
    if pending:
        try:
            dep_doc = yaml.safe_load(pending)
        except Exception:
            dep_doc = None
    if not dep_doc and deployment_yaml_path.exists():
        dep_doc = yaml.safe_load(deployment_yaml_path.read_text())
    if not dep_doc or dep_doc.get("kind") != "Deployment":
        return False
    hpa_doc = None
    pending_hpa = (result.get("hpa_yaml_new") or "").strip()
    if pending_hpa:
        try:
            hpa_doc = yaml.safe_load(pending_hpa)
        except Exception:
            hpa_doc = None
    if not hpa_doc and hpa_yaml_path.exists():
        hpa_doc = yaml.safe_load(hpa_yaml_path.read_text())

    spec = dep_doc.setdefault("spec", {})
    cur_rep = int(spec.get("replicas") or 1)
    max_rep = int(os.environ.get("SQUEEZE_UP_RECOVERY_MAX_REPLICAS", "6"))
    new_rep = min(cur_rep + 1, max_rep)
    if new_rep <= cur_rep:
        return False
    spec["replicas"] = new_rep

    if hpa_doc and hpa_doc.get("kind") == "HorizontalPodAutoscaler":
        hspec = hpa_doc.setdefault("spec", {})
        hspec["maxReplicas"] = max(int(hspec.get("maxReplicas") or 1), new_rep)
        hspec["minReplicas"] = min(int(hspec.get("minReplicas") or 1), new_rep)
        result["hpa_yaml_new"] = yaml.safe_dump(hpa_doc, sort_keys=False)

    result["deployment_yaml_new"] = yaml.safe_dump(dep_doc, sort_keys=False)
    ev = list(result.get("evidence") or [])
    ev.append(f"{evidence_tag}.up_recovery_replica_step:replicas={new_rep}")
    result["evidence"] = ev
    return True


def _guard_llm_up_recovery_yaml(
    result: dict,
    experiment: dict,
    deployment_yaml_path: Path,
    hpa_yaml_path: Path,
) -> None:
    """UP recovery safety clamp only — LLM owns sizing via prompts (replica step ≤1 vs live)."""
    if experiment.get("analysis_goal") != "efficiency":
        return
    if experiment.get("squeeze_optimizer") != "llm":
        return
    if _llm_squeeze_down_boundary_active(experiment):
        return
    if not _in_up_recovery_path(experiment):
        return

    dep_new = (result.get("deployment_yaml_new") or "").strip()
    if not dep_new:
        return
    try:
        dep_doc = yaml.safe_load(dep_new)
    except Exception:
        return
    if not isinstance(dep_doc, dict) or dep_doc.get("kind") != "Deployment":
        return

    cfg = experiment.get("config") or {}
    obs = experiment.get("observed") or {}
    file_repl = int(cfg.get("deployment_replicas") or 1)
    live = max(
        int(obs.get("replicas") or 0),
        int(obs.get("replicas_max") or 0),
        file_repl,
    )
    max_rep = int(os.environ.get("SQUEEZE_UP_RECOVERY_MAX_REPLICAS", "6"))
    spec = dep_doc.setdefault("spec", {})
    proposed = int(spec.get("replicas") or file_repl)
    cap = min(max_rep, max(live, file_repl) + 1)
    changed = False
    notes: list[str] = []
    if proposed > cap:
        spec["replicas"] = cap
        changed = True
        notes.append(f"replicas_clamp: llm={proposed} -> {cap} (live={live})")
        result["deployment_yaml_new"] = yaml.safe_dump(dep_doc, sort_keys=False)

    hpa_new = (result.get("hpa_yaml_new") or "").strip()
    hpa_doc = None
    if hpa_new:
        try:
            hpa_doc = yaml.safe_load(hpa_new)
        except Exception:
            hpa_doc = None
    dep_rep = int((dep_doc.get("spec") or {}).get("replicas") or cap)
    if isinstance(hpa_doc, dict) and hpa_doc.get("kind") == "HorizontalPodAutoscaler":
        hspec = hpa_doc.setdefault("spec", {})
        max_r = int(hspec.get("maxReplicas") or dep_rep)
        new_max = min(max(max_r, dep_rep), max_rep)
        if new_max > cap:
            new_max = cap
        if new_max != max_r:
            changed = True
            notes.append(f"hpa.maxReplicas_clamp: {max_r} -> {new_max}")
        hspec["maxReplicas"] = new_max
        hspec["minReplicas"] = min(int(hspec.get("minReplicas") or 1), new_max)
        result["hpa_yaml_new"] = yaml.safe_dump(hpa_doc, sort_keys=False)

    if changed:
        ev = list(result.get("evidence") or [])
        ev.append("guard.up_recovery: " + "; ".join(notes))
        result["evidence"] = ev


def _compute_step_pct(experiment: dict) -> float:
    """
    Deterministic step size for faster convergence.
    - DOWN: step_pct = bound(base + 0.25 * slack, floor, 0.30)
      where slack = max(0, (60 - max(cpu_util_pct, mem_util_pct)) / 60)
      and base/floor are adaptive in squeeze mode to avoid over-cutting when
      utilization is already tight:
        * util < 60%  -> base=0.10, floor=0.10
        * util >= 60% -> base=0.05, floor=0.05
    - UP: step_pct = bound(0.15 + 0.08 * min(severity, 3.0), 0.15, 0.40)
      where severity = max(err_pressure, lat_pressure, throughput_pressure)
    """
    observed = experiment.get("observed") or {}
    slo = experiment.get("slo") or {}
    scaling_hint = experiment.get("scaling_hint")
    cpu = float(observed.get("cpu_util_pct") or 0.0)
    mem = float(observed.get("mem_util_pct") or 0.0)

    if scaling_hint == "DOWN":
        # Aim around ~60% utilization; larger slack -> larger cut.
        # Keep moving DOWN in squeeze mode, but use a smaller floor when
        # utilization is already tight to avoid over-aggressive reductions.
        util = max(cpu, mem)
        slack = max(0.0, (60.0 - util) / 60.0)
        down_floor = 0.05 if util >= 60.0 else 0.10
        down_base = down_floor
        return round(_bound(down_base + (0.25 * slack), down_floor, 0.30), 3)

    if scaling_hint == "UP":
        if _in_up_recovery_path(experiment) and _up_recovery_latency_slo_met(experiment):
            return 0.15
        err = float(observed.get("error_rate") or 0.0)
        p95 = float((observed.get("latency_ms") or {}).get("p95") or 0.0)
        slo_err = float(slo.get("error_rate") or 0.01)
        slo_p95 = float(slo.get("p95_latency_ms") or 500.0)
        achieved = float(observed.get("achieved_requests_per_second_target_window") or 0.0)
        target = float((experiment.get("workload") or {}).get("target_requests_per_second") or 0.0)

        err_pressure = max(0.0, (err / max(slo_err, 1e-6)) - 1.0)
        lat_pressure = max(0.0, (p95 / max(slo_p95, 1e-6)) - 1.0)
        throughput_pressure = max(0.0, (target / max(achieved, 1e-6)) - 1.0) if target > 0 else 0.0
        severity = max(err_pressure, lat_pressure, throughput_pressure)
        thr_floor = _up_recovery_throughput_ratio_floor()
        if target > 0 and achieved >= thr_floor * target and lat_pressure > 0:
            # Per-pod latency bound while meeting RPS: stronger vertical steps (any load).
            severity = max(severity, min(3.0, lat_pressure + 0.5))
        return round(_bound(0.15 + (0.08 * min(severity, 3.0)), 0.15, 0.40), 3)

    return 0.0


def _squeeze_resource_floors() -> tuple[int, int]:
    cpu_floor = int(os.environ.get("SQUEEZE_CPU_REQUEST_FLOOR_M", "50"))
    mem_floor = int(os.environ.get("SQUEEZE_MEM_REQUEST_FLOOR_MIB", "32"))
    return cpu_floor, mem_floor


def _millicpu_value(val: str | int | float | None) -> int:
    from analysis.experiment_build import parse_cpu_millicores

    return parse_cpu_millicores(val)


def _mib_value(val: str | int | float | None) -> int:
    from analysis.experiment_build import parse_memory_mib

    return parse_memory_mib(val)


def _scale_millicpu(
    val: str | int | float | None, factor: float, *, floor: int | None = None
) -> str:
    cpu_floor, _ = _squeeze_resource_floors()
    floor = cpu_floor if floor is None else floor
    base = _millicpu_value(val)
    out = max(floor, int(math.ceil(base * factor)))
    return f"{out}m"


def _scale_mib(val: str | int | float | None, factor: float, *, floor: int | None = None) -> str:
    _, mem_floor = _squeeze_resource_floors()
    floor = mem_floor if floor is None else floor
    base = _mib_value(val)
    out = max(floor, int(math.ceil(base * factor)))
    return f"{out}Mi"


def _scaled_millicpu_changes(val: str | int | float | None, factor: float) -> bool:
    cpu_floor, _ = _squeeze_resource_floors()
    base = _millicpu_value(val)
    if base <= cpu_floor:
        return False
    return max(cpu_floor, int(math.ceil(base * factor))) != base


def _scaled_mib_changes(val: str | int | float | None, factor: float) -> bool:
    _, mem_floor = _squeeze_resource_floors()
    base = _mib_value(val)
    if base <= mem_floor:
        return False
    return max(mem_floor, int(math.ceil(base * factor))) != base


def _planned_squeeze_down_axis(experiment: dict) -> str:
    """Alternate DOWN steps: resources (CPU/mem) vs replica (-1), never replica twice in a row."""
    if bool(((experiment.get("failure") or {}).get("failed"))):
        return "resources"
    prev = experiment.get("_prev_iteration") or {}
    if prev.get("slo_status") != "PASS":
        return "resources"
    last = (prev.get("squeeze_down_axis") or "").strip().lower()
    if last == "replica":
        return "resources"
    if last == "resources":
        return "replica"
    return "resources"


def _apply_resource_down_to_container(c0: dict, factor: float) -> bool:
    """Scale container requests/limits DOWN; return True if requests changed."""
    res = c0.setdefault("resources", {})
    req = res.setdefault("requests", {})
    lim = res.setdefault("limits", {})
    req_cpu_changed = _scaled_millicpu_changes(req.get("cpu", "100m"), factor)
    mem_req_changed = _scaled_mib_changes(req.get("memory", "50Mi"), factor)
    if req_cpu_changed:
        req["cpu"] = _scale_millicpu(req.get("cpu", "100m"), factor)
        lim["cpu"] = _scale_millicpu(lim.get("cpu", "200m"), factor)
    if mem_req_changed:
        req["memory"] = _scale_mib(req.get("memory", "50Mi"), factor)
        lim["memory"] = _scale_mib(lim.get("memory", "100Mi"), factor)
    if req_cpu_changed and not mem_req_changed:
        lim["memory"] = _scale_mib(lim.get("memory", "100Mi"), factor)
    if mem_req_changed and not req_cpu_changed:
        lim["cpu"] = _scale_millicpu(lim.get("cpu", "200m"), factor)
    return req_cpu_changed or mem_req_changed


def _apply_squeeze_down_axis_policy(
    result: dict,
    experiment: dict,
    deployment_yaml_path: Path,
    hpa_yaml_path: Path,
) -> None:
    """Enforce alternating replica vs CPU/mem DOWN steps (formula / hybrid path only)."""
    if experiment.get("analysis_goal") != "efficiency":
        return
    if experiment.get("mode") != "squeeze":
        return
    if bool(((experiment.get("failure") or {}).get("failed"))):
        return
    tel = ((experiment.get("observed") or {}).get("telemetry") or {})
    if not tel.get("utilization_trustworthy"):
        return

    hint = experiment.get("scaling_hint")
    if hint == "HOLD":
        hint = "DOWN"
    if hint != "DOWN":
        if _llm_squeeze_down_boundary_active(experiment):
            hint = "DOWN"
        else:
            return

    step = _compute_step_pct({**experiment, "scaling_hint": "DOWN"})
    if step <= 0:
        return
    factor = 1.0 - step
    axis = _planned_squeeze_down_axis(experiment)

    if not deployment_yaml_path.exists():
        return
    dep_doc = yaml.safe_load(deployment_yaml_path.read_text())
    if not dep_doc or dep_doc.get("kind") != "Deployment":
        return
    hpa_doc = None
    if hpa_yaml_path.exists():
        hpa_doc = yaml.safe_load(hpa_yaml_path.read_text())

    obs = experiment.get("observed") or {}
    live = max(
        int(obs.get("replicas") or 0),
        int(obs.get("replicas_max") or 0),
    )
    spec = dep_doc.setdefault("spec", {})
    tmpl = spec.setdefault("template", {}).setdefault("spec", {})
    containers = tmpl.get("containers") or []
    if not containers:
        return

    repl_changed = False
    res_changed = False

    if axis == "replica" and live >= 2:
        repl_changed = _formula_down_replica_step(dep_doc, hpa_doc, experiment, step)
        res_changed = _apply_resource_down_to_container(containers[0], factor)
        applied_axis = "replica"
    else:
        file_rep = int(spec.get("replicas") or live or 1)
        res_changed = _apply_resource_down_to_container(containers[0], factor)
        spec["replicas"] = max(file_rep, live)
        if hpa_doc and hpa_doc.get("kind") == "HorizontalPodAutoscaler":
            hspec = hpa_doc.setdefault("spec", {})
            hspec["maxReplicas"] = max(
                int(hspec.get("maxReplicas") or file_rep),
                file_rep,
                live,
            )
        if not res_changed and live >= 2:
            repl_changed = _formula_down_replica_step(dep_doc, hpa_doc, experiment, step)
            applied_axis = "replica"
        else:
            applied_axis = "resources"

    if not repl_changed and not res_changed:
        ev = list(result.get("evidence") or [])
        ev.append(f"squeeze_down_axis={axis}:no_progress")
        result["evidence"] = ev
        return

    result["deployment_yaml_new"] = yaml.safe_dump(dep_doc, sort_keys=False)
    if hpa_doc and hpa_doc.get("kind") == "HorizontalPodAutoscaler":
        result["hpa_yaml_new"] = yaml.safe_dump(hpa_doc, sort_keys=False)
    result["squeeze_down_axis"] = applied_axis
    ev = list(result.get("evidence") or [])
    ev.append(f"squeeze_down_axis={applied_axis}")
    ev.append(f"squeeze_down_planned={axis}")
    result["evidence"] = ev


def _formula_down_replica_step(
    dep_doc: dict,
    hpa_doc: dict | None,
    experiment: dict,
    step: float,
) -> bool:
    """Reduce deployment.spec.replicas and HPA max when CPU/mem requests are already at floor."""
    obs = experiment.get("observed") or {}
    live = max(1, int(obs.get("replicas") or 0))
    if live < 2:
        return False

    spec = dep_doc.setdefault("spec", {})
    target = live - 1
    old_rep = int(spec.get("replicas") or live)
    changed = False
    if old_rep != target:
        spec["replicas"] = target
        changed = True

    if hpa_doc and hpa_doc.get("kind") == "HorizontalPodAutoscaler":
        hspec = hpa_doc.setdefault("spec", {})
        min_r = int(hspec.get("minReplicas") or 1)
        max_r = int(hspec.get("maxReplicas") or live)
        delta = max(1, int(math.ceil(max_r * step * 0.5)))
        new_max = max(min_r, min(target, max_r - delta))
        if max_r != new_max:
            hspec["maxReplicas"] = new_max
            changed = True
        if min_r > target:
            hspec["minReplicas"] = max(1, target)
            changed = True
    return changed


def _apply_formula_up_horizontal_step(
    result: dict,
    experiment: dict,
    deployment_yaml_path: Path,
    hpa_yaml_path: Path,
) -> bool:
    return _apply_up_recovery_replica_step(
        result,
        experiment,
        deployment_yaml_path,
        hpa_yaml_path,
        evidence_tag="formula",
    )


def _maybe_apply_deterministic_efficiency_yaml(
    result: dict, experiment: dict, deployment_yaml_path: Path, hpa_yaml_path: Path
) -> None:
    # Deterministic UP/DOWN movement path for fewer iterations.
    if experiment.get("analysis_goal") != "efficiency":
        return
    tel = ((experiment.get("observed") or {}).get("telemetry") or {})
    if not tel.get("utilization_trustworthy"):
        return
    hint = experiment.get("scaling_hint")
    # In squeeze mode, HOLD should not stall goal-seeking:
    # - PASS path keeps moving DOWN until first FAIL
    # - FAIL path keeps moving UP until first PASS
    if hint == "HOLD":
        failed = bool(((experiment.get("failure") or {}).get("failed")))
        hint = "UP" if failed else "DOWN"
    if hint not in {"UP", "DOWN"}:
        return

    step = _compute_step_pct(experiment)
    if step <= 0:
        return
    factor = (1.0 + step) if hint == "UP" else (1.0 - step)

    dep_doc = None
    hpa_doc = None
    if deployment_yaml_path.exists():
        dep_doc = yaml.safe_load(deployment_yaml_path.read_text())
    if hpa_yaml_path.exists():
        hpa_doc = yaml.safe_load(hpa_yaml_path.read_text())

    if not dep_doc or dep_doc.get("kind") != "Deployment":
        return

    spec = dep_doc.setdefault("spec", {})
    tmpl = spec.setdefault("template", {}).setdefault("spec", {})
    containers = tmpl.get("containers") or []
    if not containers:
        return
    c0 = containers[0]
    res = c0.setdefault("resources", {})
    req = res.setdefault("requests", {})
    lim = res.setdefault("limits", {})

    if hint == "UP":
        if _apply_formula_up_horizontal_step(
            result, experiment, deployment_yaml_path, hpa_yaml_path
        ):
            return
        if _in_up_recovery_path(experiment) and _up_recovery_latency_slo_met(experiment):
            metrics = _metric_up_step_from_file(
                experiment, deployment_yaml_path, step_override=0.15
            )
            if metrics:
                req["cpu"] = f"{metrics['cpu_req']}m"
                lim["cpu"] = f"{metrics['cpu_lim']}m"
                req["memory"] = f"{metrics['mem_req']}Mi"
                lim["memory"] = f"{metrics['mem_lim']}Mi"
                result["deployment_yaml_new"] = yaml.safe_dump(dep_doc, sort_keys=False)
                _sync_up_recovery_hpa_after_vertical(
                    result, experiment, dep_doc, hpa_doc, 0.15
                )
                return
        req["cpu"] = _scale_millicpu(req.get("cpu", "100m"), factor)
        lim["cpu"] = _scale_millicpu(lim.get("cpu", "200m"), factor)
        req["memory"] = _scale_mib(req.get("memory", "50Mi"), factor)
        lim["memory"] = _scale_mib(lim.get("memory", "100Mi"), factor)
        result["deployment_yaml_new"] = yaml.safe_dump(dep_doc, sort_keys=False)
    else:
        _apply_squeeze_down_axis_policy(
            result, experiment, deployment_yaml_path, hpa_yaml_path
        )
        return

    if hint == "UP":
        _sync_up_recovery_hpa_after_vertical(result, experiment, dep_doc, hpa_doc, step)


def load_summary() -> tuple[dict, Path, dict | None]:
    """Reads k6 summary (and optional run_meta), creates run dir, copies summary. Returns (summary_dict, run_dir, run_meta or None)."""
    summary_path = _results_base() / "k6-summary.json"
    run_meta_path = _results_base() / "run_meta.json"
    results_dir = _results_base()
    if not summary_path.exists():
        raise FileNotFoundError(f"Run k6 first; expected {summary_path}")
    with open(summary_path) as f:
        data = json.load(f)

    meta = None
    if run_meta_path.exists():
        try:
            with open(run_meta_path) as f:
                meta = json.load(f)
            run_meta_path.unlink()
        except (json.JSONDecodeError, OSError):
            meta = None

    run_label = (meta or {}).get("run_label")
    iteration_index = (meta or {}).get("iteration_index")
    if run_label and iteration_index is not None:
        run_dir = results_dir / str(run_label) / f"iteration-{int(iteration_index)}"
    elif run_label:
        run_dir = results_dir / str(run_label)
    else:
        today_str = date.today().strftime("%Y-%m-%d")
        idx = 1
        while True:
            run_dir = results_dir / f"{today_str}-{idx}"
            if not run_dir.exists():
                break
            idx += 1

    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "k6-run-summary.json").write_text(json.dumps(data, indent=2))
    try:
        summary_path.unlink()
    except FileNotFoundError:
        pass

    if meta is not None and (
        "experiment_id" in meta
        or "workload" in meta
        or "slo" in meta
        or "profile" in meta
        or "script" in meta
        or "k6_thresholds_crossed" in meta
        or "mode" in meta
        or "prometheus" in meta
        or "service" in meta
        or "endpoint" in meta
        or "base_url" in meta
        or "k8s_namespace" in meta
        or "k8s_deployment" in meta
        or "analysis_goal" in meta
        or "deployment_yaml" in meta
        or "hpa_yaml" in meta
        or "prometheus_url" in meta
        or "up_recovery" in meta
        or "squeeze_optimizer" in meta
    ):
        cfg = {
            "experiment_id": meta.get("experiment_id"),
            "workload": meta.get("workload"),
            "slo": meta.get("slo"),
        }
        if "analysis_goal" in meta:
            cfg["analysis_goal"] = meta["analysis_goal"]
        if "mode" in meta:
            cfg["mode"] = meta["mode"]
        if "profile" in meta:
            cfg["profile"] = meta["profile"]
        if "script" in meta:
            cfg["script"] = meta["script"]
        if "k6_thresholds_crossed" in meta:
            cfg["k6_thresholds_crossed"] = meta["k6_thresholds_crossed"]
        if "prometheus" in meta:
            cfg["prometheus"] = meta["prometheus"]
        if "service" in meta:
            cfg["service"] = meta["service"]
        if "endpoint" in meta:
            cfg["endpoint"] = meta["endpoint"]
        if "base_url" in meta:
            cfg["base_url"] = meta["base_url"]
        if "k8s_namespace" in meta:
            cfg["k8s_namespace"] = meta["k8s_namespace"]
        if "k8s_deployment" in meta:
            cfg["k8s_deployment"] = meta["k8s_deployment"]
        if "deployment_yaml" in meta:
            cfg["deployment_yaml"] = meta["deployment_yaml"]
        if "hpa_yaml" in meta:
            cfg["hpa_yaml"] = meta["hpa_yaml"]
        if "prometheus_url" in meta:
            cfg["prometheus_url"] = meta["prometheus_url"]
        if meta.get("up_recovery"):
            cfg["up_recovery"] = True
        if "squeeze_optimizer" in meta:
            cfg["squeeze_optimizer"] = meta["squeeze_optimizer"]
        (run_dir / "experiment_config.json").write_text(json.dumps(cfg))

    return data, run_dir, meta


def load_current_yaml(deployment_yaml: Path, hpa_yaml: Path) -> str:
    """Deployment + HPA YAML for the prompt."""
    parts = []
    if deployment_yaml.exists():
        parts.append(f"# FILE: {deployment_yaml.relative_to(REPO_ROOT)}\n")
        parts.append(deployment_yaml.read_text())
    if hpa_yaml.exists():
        parts.append(f"\n# FILE: {hpa_yaml.relative_to(REPO_ROOT)}\n")
        parts.append(hpa_yaml.read_text())
    return "\n".join(parts) if parts else ""


def run_analysis(run_dir: Path | None = None) -> tuple[dict, Path, Path, Path]:
    """Build experiment.json, call LLM, return (analysis result, run_dir)."""
    meta = None
    if run_dir is None:
        _, run_dir, meta = load_summary()
    else:
        with open(run_dir / "k6-run-summary.json") as f:
            json.load(f)  # ensure exists
        # Re-run: get start_ts/end_ts from existing experiment.json if present
        exp_path = run_dir / "experiment.json"
        if exp_path.exists():
            try:
                with open(exp_path) as f:
                    existing = json.load(f)
                meta = {
                    "start_ts": existing.get("start_ts"),
                    "end_ts": existing.get("end_ts"),
                    "prometheus": existing.get("prometheus", True),
                    "k8s_namespace": existing.get("k8s_namespace", "default"),
                    "k8s_deployment": existing.get("k8s_deployment", "stress-service"),
                    "analysis_goal": existing.get("analysis_goal", "failure"),
                    "mode": existing.get("mode"),
                    "deployment_yaml": existing.get("deployment_yaml"),
                    "hpa_yaml": existing.get("hpa_yaml"),
                    "prometheus_url": existing.get("prometheus_url"),
                    "squeeze_optimizer": existing.get("squeeze_optimizer"),
                }
            except (json.JSONDecodeError, OSError):
                pass

    deployment_yaml_path, hpa_yaml_path = _resolve_yaml_paths(meta)
    canonical = load_shared_canonical_overrides(run_dir)
    _log(
        f"run_analysis_start run_dir={run_dir} deployment_yaml={deployment_yaml_path} "
        f"hpa_yaml={hpa_yaml_path} shared_canonical={bool(canonical)}"
    )
    k6_path = run_dir / "k6-run-summary.json"
    config = get_config_from_yaml(deployment_yaml_path, hpa_yaml_path)
    if canonical and canonical.get("config"):
        config = {**config, **canonical["config"]}

    experiment_config = None
    if meta is not None and (
        "experiment_id" in meta
        or "workload" in meta
        or "slo" in meta
        or "k6_thresholds_crossed" in meta
        or "mode" in meta
        or "prometheus" in meta
        or "service" in meta
        or "endpoint" in meta
        or "base_url" in meta
        or "k8s_namespace" in meta
        or "k8s_deployment" in meta
        or "analysis_goal" in meta
        or "deployment_yaml" in meta
        or "hpa_yaml" in meta
        or "prometheus_url" in meta
        or "up_recovery" in meta
        or "squeeze_optimizer" in meta
    ):
        experiment_config = {
            "experiment_id": meta.get("experiment_id"),
            "workload": meta.get("workload"),
            "slo": meta.get("slo"),
        }
        if "analysis_goal" in meta:
            experiment_config["analysis_goal"] = meta["analysis_goal"]
        if "mode" in meta:
            experiment_config["mode"] = meta["mode"]
        if "profile" in meta:
            experiment_config["profile"] = meta["profile"]
        if "script" in meta:
            experiment_config["script"] = meta["script"]
        if "k6_thresholds_crossed" in meta:
            experiment_config["k6_thresholds_crossed"] = meta["k6_thresholds_crossed"]
        if "prometheus" in meta:
            experiment_config["prometheus"] = meta["prometheus"]
        if "service" in meta:
            experiment_config["service"] = meta["service"]
        if "endpoint" in meta:
            experiment_config["endpoint"] = meta["endpoint"]
        if "base_url" in meta:
            experiment_config["base_url"] = meta["base_url"]
        if "k8s_namespace" in meta:
            experiment_config["k8s_namespace"] = meta["k8s_namespace"]
        if "k8s_deployment" in meta:
            experiment_config["k8s_deployment"] = meta["k8s_deployment"]
        if "deployment_yaml" in meta:
            experiment_config["deployment_yaml"] = meta["deployment_yaml"]
        if "hpa_yaml" in meta:
            experiment_config["hpa_yaml"] = meta["hpa_yaml"]
        if "prometheus_url" in meta:
            experiment_config["prometheus_url"] = meta["prometheus_url"]
        if meta.get("up_recovery"):
            experiment_config["up_recovery"] = True
        if "squeeze_optimizer" in meta:
            experiment_config["squeeze_optimizer"] = meta["squeeze_optimizer"]
    if experiment_config is None:
        config_path = run_dir / "experiment_config.json"
        if config_path.exists():
            try:
                with open(config_path) as f:
                    experiment_config = json.load(f)
            except (json.JSONDecodeError, OSError):
                pass

    if meta is not None and experiment_config:
        for k in (
            "prometheus",
            "k8s_namespace",
            "k8s_deployment",
            "service",
            "endpoint",
            "base_url",
            "analysis_goal",
            "deployment_yaml",
            "hpa_yaml",
            "prometheus_url",
            "squeeze_optimizer",
        ):
            if experiment_config.get(k) is not None:
                meta[k] = experiment_config[k]
        if "up_recovery" in experiment_config:
            meta["up_recovery"] = bool(experiment_config["up_recovery"])

    observed_override = None
    start_ts = None
    end_ts = None
    if canonical:
        meta = meta or {}
        if canonical.get("start_ts") is not None:
            meta["start_ts"] = canonical["start_ts"]
        if canonical.get("end_ts") is not None:
            meta["end_ts"] = canonical["end_ts"]
        frozen_observed = canonical.get("observed")
        if isinstance(frozen_observed, dict):
            observed_override = dict(frozen_observed)
            _log(
                "shared_reanalyze_frozen_observed "
                f"burn={observed_override.get('cpu_usage_avg_m')} "
                f"cpu_util_request_pct={observed_override.get('cpu_util_request_pct')}"
            )
        if canonical.get("config"):
            experiment_config = experiment_config or {}
            experiment_config["config"] = canonical["config"]
    if meta is not None:
        start_ts = meta.get("start_ts")
        end_ts = meta.get("end_ts")
        use_prom = meta.get("prometheus", True)
        if (
            observed_override is None
            and use_prom
            and start_ts is not None
            and end_ts is not None
        ):
            from .prometheus_collect import get_prometheus_observed

            hpa_cfg = config.get("hpa") or {}
            _log(
                f"prometheus_collect_start namespace={meta.get('k8s_namespace')} "
                f"deployment={meta.get('k8s_deployment')} url={meta.get('prometheus_url')}"
            )
            observed_override = get_prometheus_observed(
                start_ts=float(start_ts),
                end_ts=float(end_ts),
                namespace=meta.get("k8s_namespace") or "default",
                deployment_name=meta.get("k8s_deployment") or "stress-service",
                prometheus_url=meta.get("prometheus_url") or DEFAULT_PROMETHEUS_URL,
                cpu_request_m=int(config.get("cpu_request_m") or 0),
                cpu_limit_m=config.get("cpu_limit_m") or 500,
                mem_limit_mib=config.get("mem_limit_mib") or 256,
                deployment_replicas=int(config.get("deployment_replicas") or 0),
                hpa_min_replicas=int(hpa_cfg.get("min_replicas") or 0),
            )
            telem = (observed_override or {}).get("telemetry") or {}
            _log(
                "prometheus_collect_done "
                f"cpu_util_pct={(observed_override or {}).get('cpu_util_pct')} "
                f"mem_util_pct={(observed_override or {}).get('mem_util_pct')} "
                f"cpu_series_matched={telem.get('cpu_series_matched')} "
                f"mem_series_matched={telem.get('mem_series_matched')} "
                f"utilization_trustworthy={telem.get('utilization_trustworthy')}"
            )
    exp_data = build_experiment_payload(
        run_dir,
        k6_path,
        deployment_yaml_path,
        hpa_yaml_path,
        experiment_config=experiment_config,
        observed_override=observed_override,
    )
    if start_ts is not None:
        exp_data["start_ts"] = start_ts
    if end_ts is not None:
        exp_data["end_ts"] = end_ts
    if meta is not None:
        for k in (
            "prometheus",
            "base_url",
            "k8s_namespace",
            "k8s_deployment",
            "analysis_goal",
            "deployment_yaml",
            "hpa_yaml",
            "prometheus_url",
            "up_recovery",
            "squeeze_optimizer",
        ):
            if k in meta:
                exp_data[k] = meta[k]
    squeeze_opt = _resolve_squeeze_optimizer(meta, experiment_config)
    exp_data["squeeze_optimizer"] = squeeze_opt
    if squeeze_opt == "llm" and _llm_vanilla_squeeze():
        exp_data["llm_vanilla_squeeze"] = True
        exp_data["scaling_rationale"] = (
            "Vanilla LLM squeeze: coarse outcome summary + current YAML only "
            "(no detailed telemetry in the prompt)."
        )
    elif squeeze_opt == "llm" and _llm_pure_squeeze():
        exp_data["llm_pure_squeeze"] = True
        exp_data["scaling_rationale"] = (
            "Advanced LLM squeeze: full experiment metrics in prompt; "
            "decide UP/DOWN and step sizes from observed.* (no formula fallback)."
        )
        attach_scaling_hint(exp_data)
    else:
        attach_scaling_hint(exp_data)
    if _in_up_recovery_path(exp_data):
        _attach_up_recovery_signals(exp_data)
    _attach_previous_iteration_context(exp_data, meta)
    (run_dir / "experiment.json").write_text(json.dumps(exp_data, indent=2))
    _log(
        f"experiment_written scaling_hint={exp_data.get('scaling_hint')} "
        f"failure_reason={(exp_data.get('failure') or {}).get('reason')}"
    )

    analysis_goal = (meta or {}).get("analysis_goal", "failure")
    mode_flag = (meta or {}).get("mode")
    use_efficiency = analysis_goal == "efficiency" or mode_flag == "squeeze"
    user_mode = "squeeze" if use_efficiency else "failure"
    if user_mode == "squeeze" and squeeze_opt not in {"hpa", "replay"}:
        obs = exp_data.get("observed") or {}
        tel = (obs.get("telemetry") or {})
        if tel.get("utilization_trustworthy"):
            from .k8s_manifest import sync_managed_yaml_to_observed_scale

            # DOWN squeeze: do not sync YAML up to a transient HPA scale-up (undoes replica cap).
            allow_scale_up = not (
                exp_data.get("mode") == "squeeze" and not exp_data.get("up_recovery")
            )
            sync_notes = sync_managed_yaml_to_observed_scale(
                deployment_yaml_path,
                hpa_yaml_path,
                live_replicas=int(obs.get("replicas") or 0),
                live_replicas_max=int(obs.get("replicas_max") or obs.get("replicas") or 0),
                allow_scale_up=allow_scale_up,
            )
            if sync_notes:
                cfg = get_config_from_yaml(deployment_yaml_path, hpa_yaml_path)
                exp_data["config"] = cfg
                _log("yaml_live_sync " + "; ".join(sync_notes))
    measured_yaml = load_measured_yaml_for_prompt(run_dir) if canonical else None
    yaml_str = measured_yaml or load_current_yaml(deployment_yaml_path, hpa_yaml_path)
    user_prompt = build_user_prompt(exp_data, yaml_str, mode=user_mode)

    if use_efficiency and squeeze_opt == "hpa":
        _log("hpa_only_observe mode=squeeze (no LLM/formula YAML)")
        result = _hpa_only_result(exp_data)
    elif use_efficiency and squeeze_opt == "replay":
        _log("replay_observe mode=squeeze (no optimizer YAML)")
        result = _replay_observe_result(exp_data)
    elif use_efficiency and squeeze_opt == "formula":
        _log(
            f"formula_optimizer_step mode={user_mode} analysis_goal={analysis_goal} "
            f"scaling_hint={exp_data.get('scaling_hint')}"
        )
        result = _formula_only_result(exp_data, deployment_yaml_path, hpa_yaml_path)
        _log(
            f"formula_optimizer_done failure_archetype={result.get('failure_archetype')} "
            f"has_deployment_yaml_new={bool((result.get('deployment_yaml_new') or '').strip())} "
            f"has_hpa_yaml_new={bool((result.get('hpa_yaml_new') or '').strip())}"
        )
    else:
        if use_efficiency and squeeze_opt == "llm" and _llm_vanilla_squeeze():
            system_prompt = VANILLA_LLM_SQUEEZE_PROMPT
            user_prompt = build_vanilla_user_prompt(
                exp_data, yaml_str, mode=user_mode
            )
        elif use_efficiency and squeeze_opt == "llm":
            system_prompt = EFFICIENCY_LLM_ONLY_SQUEEZE_PROMPT
        else:
            system_prompt = EFFICIENCY_SYSTEM_PROMPT if use_efficiency else SYSTEM_PROMPT
        _log(
            f"llm_analyze_start mode={user_mode} analysis_goal={analysis_goal} "
            f"optimizer={squeeze_opt} vanilla={_llm_vanilla_squeeze()} "
            f"user_prompt_chars={len(user_prompt)}"
        )
        result = analyze_with_llm(system_prompt, user_prompt)
        result = _postprocess_llm_result(result, exp_data)
        if use_efficiency and squeeze_opt == "llm" and not _llm_vanilla_squeeze():
            if _in_up_recovery_path(exp_data):
                _guard_llm_up_recovery_yaml(
                    result, exp_data, deployment_yaml_path, hpa_yaml_path
                )
        if use_efficiency and squeeze_opt == "hybrid":
            _maybe_apply_deterministic_efficiency_yaml(
                result, exp_data, deployment_yaml_path, hpa_yaml_path
            )
        if _llm_squeeze_down_boundary_active(exp_data) and not _llm_vanilla_squeeze():
            _finalize_llm_squeeze_down(
                result, exp_data, deployment_yaml_path, hpa_yaml_path
            )
        elif _llm_squeeze_down_boundary_active(exp_data) and _llm_vanilla_squeeze():
            _finalize_vanilla_llm_squeeze_down(
                result, exp_data, deployment_yaml_path, hpa_yaml_path
            )
        _log(
            f"llm_analyze_done failure_archetype={result.get('failure_archetype')} "
            f"has_deployment_yaml_new={bool((result.get('deployment_yaml_new') or '').strip())} "
            f"has_hpa_yaml_new={bool((result.get('hpa_yaml_new') or '').strip())} "
            f"down_boundary={_llm_squeeze_down_boundary_active(exp_data)}"
        )
    return result, run_dir, deployment_yaml_path, hpa_yaml_path


def write_outputs(
    result: dict,
    run_dir: Path,
    deployment_yaml_path: Path,
    hpa_yaml_path: Path,
) -> None:
    """Write report.md, recommended.diff (for display), analysis.json; overwrite repo YAMLs when LLM returns full files."""
    import difflib

    report = _coerce_report_markdown(result.get("report", ""))
    _normalize_llm_yaml_fields(result)
    if deployment_yaml_path.exists():
        shutil.copy2(deployment_yaml_path, run_dir / MEASURED_DEPLOYMENT_YAML)
    if hpa_yaml_path.exists():
        shutil.copy2(hpa_yaml_path, run_dir / MEASURED_HPA_YAML)
    deployment_yaml_new = (result.get("deployment_yaml_new") or "").strip()
    hpa_yaml_new = (result.get("hpa_yaml_new") or "").strip()

    # If the LLM produces invalid YAML, don't write/apply it (avoids breaking subsequent iterations).
    if deployment_yaml_new:
        try:
            yaml.safe_load(deployment_yaml_new)
        except Exception as e:
            report = (
                report
                + "\n\n"
                + f"- WARNING: deployment_yaml_new was invalid YAML; ignoring. error={e}\n"
            )
            deployment_yaml_new = ""
        else:
            from analysis.experiment_build import normalize_deployment_yaml_resources

            deployment_yaml_new, norm_notes = normalize_deployment_yaml_resources(
                deployment_yaml_new
            )
            if norm_notes:
                report = (
                    report
                    + "\n\n"
                    + "- Normalized deployment resources: "
                    + "; ".join(norm_notes)
                    + "\n"
                )
    if hpa_yaml_new:
        from analysis.k8s_manifest import prepare_hpa_yaml_new

        prepared, hpa_warn = prepare_hpa_yaml_new(
            hpa_yaml_new, hpa_yaml_path=hpa_yaml_path, repo_root=REPO_ROOT
        )
        if hpa_warn:
            report = report + "\n\n" + f"- WARNING: {hpa_warn}; HPA change ignored.\n"
            hpa_yaml_new = ""
        else:
            hpa_yaml_new = prepared
    (run_dir / "report.md").write_text(report)

    diff_parts = []
    if deployment_yaml_new:
        old_dep = deployment_yaml_path.read_text() if deployment_yaml_path.exists() else ""
        deployment_yaml_path.parent.mkdir(parents=True, exist_ok=True)
        deployment_yaml_path.write_text(deployment_yaml_new)
        if hpa_yaml_path.exists() and not hpa_yaml_new:
            from analysis.k8s_manifest import align_squeeze_hpa_to_deployment_replicas

            align_squeeze_hpa_to_deployment_replicas(
                deployment_yaml_path, hpa_yaml_path
            )
        dep_rel = str(deployment_yaml_path.relative_to(REPO_ROOT))
        diff_parts.append(
            "".join(
                difflib.unified_diff(
                    old_dep.splitlines(keepends=True),
                    deployment_yaml_new.splitlines(keepends=True),
                    fromfile=dep_rel,
                    tofile=dep_rel,
                )
            )
        )
    if hpa_yaml_new:
        old_hpa = hpa_yaml_path.read_text() if hpa_yaml_path.exists() else ""
        hpa_yaml_path.parent.mkdir(parents=True, exist_ok=True)
        hpa_yaml_path.write_text(hpa_yaml_new)
        hpa_rel = str(hpa_yaml_path.relative_to(REPO_ROOT))
        diff_parts.append(
            "".join(
                difflib.unified_diff(
                    old_hpa.splitlines(keepends=True),
                    hpa_yaml_new.splitlines(keepends=True),
                    fromfile=hpa_rel,
                    tofile=hpa_rel,
                )
            )
        )
    (run_dir / "recommended.diff").write_text(
        "\n".join(diff_parts) if diff_parts else ""
    )
    if diff_parts and deployment_yaml_path.exists():
        shutil.copy2(deployment_yaml_path, run_dir / RECOMMENDED_DEPLOYMENT_YAML)
        if hpa_yaml_path.exists():
            shutil.copy2(hpa_yaml_path, run_dir / RECOMMENDED_HPA_YAML)
    _log(
        f"outputs_written run_dir={run_dir} diff_nonempty={bool(diff_parts)} "
        f"report_chars={len(report)}"
    )

    experiment = {}
    exp_path = run_dir / "experiment.json"
    if exp_path.exists():
        try:
            experiment = json.loads(exp_path.read_text())
        except json.JSONDecodeError:
            experiment = {}

    analysis_artifact = {
        "mode": (experiment.get("mode") if experiment else None),
        "analysis_goal": (experiment.get("analysis_goal") if experiment else None),
        "squeeze_optimizer": experiment.get("squeeze_optimizer") if experiment else None,
        "slo_status": _slo_status_from_experiment(experiment) if experiment else "UNKNOWN",
        "cost": (experiment.get("cost") if experiment else {}),
        "failure_archetype": result.get("failure_archetype", ""),
        "lambda_crit_estimate": result.get("lambda_crit_estimate"),
        "next_experiment": result.get("next_experiment", ""),
        "optimization_headroom": result.get("optimization_headroom"),
        "over_provisioned": result.get("over_provisioned"),
        "evidence": result.get("evidence", []),
        "squeeze_down_axis": result.get("squeeze_down_axis"),
        "resource_pass_streak": result.get("resource_pass_streak"),
        "scaling_hint": experiment.get("scaling_hint"),
        "scaling_rationale": experiment.get("scaling_rationale"),
        "up_recovery": experiment.get("up_recovery"),
        "observed_summary": _observed_summary_from_experiment(experiment)
        if experiment
        else {},
    }
    (run_dir / "analysis.json").write_text(json.dumps(analysis_artifact, indent=2))


def main() -> Path | None:
    result, run_dir, deployment_yaml_path, hpa_yaml_path = run_analysis()
    write_outputs(result, run_dir, deployment_yaml_path, hpa_yaml_path)
    print(f"Run output: {run_dir}")
    print(
        "  k6-run-summary.json, experiment.json, analysis.json, report.md, recommended.diff"
    )
    if result.get("failure_archetype"):
        print(f"  Failure archetype: {result.get('failure_archetype')}")
    return run_dir


if __name__ == "__main__":
    main()
