import json
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

from .api import analyze_with_llm
from .experiment_build import build_experiment_payload, get_config_from_yaml
from .prompts import EFFICIENCY_SYSTEM_PROMPT, SYSTEM_PROMPT, build_user_prompt

SUMMARY_PATH = REPO_ROOT / "results" / "k6-summary.json"
RUN_META_PATH = REPO_ROOT / "results" / "run_meta.json"
RESULTS_DIR = REPO_ROOT / "results"
DEFAULT_DEPLOYMENT_YAML = REPO_ROOT / "service" / "k8s" / "deployment.yaml"
DEFAULT_HPA_YAML = REPO_ROOT / "service" / "k8s" / "hpa.yaml"
DEFAULT_PROMETHEUS_URL = "http://localhost:9090"


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


def _postprocess_llm_result(result: dict, experiment: dict) -> dict:
    """
    Apply deterministic safety checks so the output cannot contradict the input metrics.
    """
    observed = experiment.get("observed") or {}
    failure = experiment.get("failure") or {}
    slo = experiment.get("slo") or {}

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


def load_summary() -> tuple[dict, Path, dict | None]:
    """Reads k6 summary (and optional run_meta), creates run dir, copies summary. Returns (summary_dict, run_dir, run_meta or None)."""
    if not SUMMARY_PATH.exists():
        raise FileNotFoundError(f"Run k6 first; expected {SUMMARY_PATH}")
    with open(SUMMARY_PATH) as f:
        data = json.load(f)

    meta = None
    if RUN_META_PATH.exists():
        try:
            with open(RUN_META_PATH) as f:
                meta = json.load(f)
            if (
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
            RUN_META_PATH.unlink()
        except (json.JSONDecodeError, OSError):
            meta = None

    run_label = (meta or {}).get("run_label")
    iteration_index = (meta or {}).get("iteration_index")
    if run_label and iteration_index is not None:
        run_dir = RESULTS_DIR / str(run_label) / f"iteration-{int(iteration_index)}"
    else:
        today_str = date.today().strftime("%Y-%m-%d")
        idx = 1
        while True:
            run_dir = RESULTS_DIR / f"{today_str}-{idx}"
            if not run_dir.exists():
                break
            idx += 1

    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "k6-run-summary.json").write_text(json.dumps(data, indent=2))
    try:
        SUMMARY_PATH.unlink()
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
                }
            except (json.JSONDecodeError, OSError):
                pass

    deployment_yaml_path, hpa_yaml_path = _resolve_yaml_paths(meta)
    k6_path = run_dir / "k6-run-summary.json"
    config = get_config_from_yaml(deployment_yaml_path, hpa_yaml_path)

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
        ):
            if experiment_config.get(k) is not None:
                meta[k] = experiment_config[k]

    observed_override = None
    start_ts = None
    end_ts = None
    if meta is not None:
        start_ts = meta.get("start_ts")
        end_ts = meta.get("end_ts")
        use_prom = meta.get("prometheus", True)
        if use_prom and start_ts is not None and end_ts is not None:
            from .prometheus_collect import get_prometheus_observed

            observed_override = get_prometheus_observed(
                start_ts=float(start_ts),
                end_ts=float(end_ts),
                namespace=meta.get("k8s_namespace") or "default",
                deployment_name=meta.get("k8s_deployment") or "stress-service",
                prometheus_url=meta.get("prometheus_url") or DEFAULT_PROMETHEUS_URL,
                cpu_limit_m=config.get("cpu_limit_m") or 500,
                mem_limit_mib=config.get("mem_limit_mib") or 256,
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
        ):
            if k in meta:
                exp_data[k] = meta[k]
    (run_dir / "experiment.json").write_text(json.dumps(exp_data, indent=2))

    analysis_goal = (meta or {}).get("analysis_goal", "failure")
    mode_flag = (meta or {}).get("mode")
    use_efficiency = analysis_goal == "efficiency" or mode_flag == "squeeze"
    user_mode = "squeeze" if use_efficiency else "failure"
    yaml_str = load_current_yaml(deployment_yaml_path, hpa_yaml_path)
    user_prompt = build_user_prompt(exp_data, yaml_str, mode=user_mode)
    system_prompt = EFFICIENCY_SYSTEM_PROMPT if use_efficiency else SYSTEM_PROMPT
    result = analyze_with_llm(system_prompt, user_prompt)
    result = _postprocess_llm_result(result, exp_data)
    return result, run_dir, deployment_yaml_path, hpa_yaml_path


def write_outputs(
    result: dict,
    run_dir: Path,
    deployment_yaml_path: Path,
    hpa_yaml_path: Path,
) -> None:
    """Write report.md, recommended.diff (for display), analysis.json; overwrite repo YAMLs when LLM returns full files."""
    import difflib

    report = result.get("report", "")
    deployment_yaml_new = (result.get("deployment_yaml_new") or "").strip()
    hpa_yaml_new = (result.get("hpa_yaml_new") or "").strip()
    (run_dir / "report.md").write_text(report)

    diff_parts = []
    if deployment_yaml_new:
        old_dep = deployment_yaml_path.read_text() if deployment_yaml_path.exists() else ""
        deployment_yaml_path.parent.mkdir(parents=True, exist_ok=True)
        deployment_yaml_path.write_text(deployment_yaml_new)
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
        "slo_status": _slo_status_from_experiment(experiment) if experiment else "UNKNOWN",
        "cost": (experiment.get("cost") if experiment else {}),
        "failure_archetype": result.get("failure_archetype", ""),
        "lambda_crit_estimate": result.get("lambda_crit_estimate"),
        "next_experiment": result.get("next_experiment", ""),
        "optimization_headroom": result.get("optimization_headroom"),
        "over_provisioned": result.get("over_provisioned"),
        "evidence": result.get("evidence", []),
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
