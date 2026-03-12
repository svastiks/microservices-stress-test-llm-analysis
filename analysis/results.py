import json
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

from .api import analyze_with_llm
from .experiment_build import build_experiment_payload, get_config_from_yaml
from .prompts import SYSTEM_PROMPT, build_user_prompt

SUMMARY_PATH = REPO_ROOT / "results" / "k6-summary.json"
RUN_META_PATH = REPO_ROOT / "results" / "run_meta.json"
RESULTS_DIR = REPO_ROOT / "results"
DEPLOYMENT_YAML = REPO_ROOT / "service" / "k8s" / "deployment.yaml"
HPA_YAML = REPO_ROOT / "service" / "k8s" / "hpa.yaml"
PROMETHEUS_URL = "http://localhost:9090"


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

    # If UNKNOWN, do not allow YAML changes.
    if result.get("failure_archetype") == "UNKNOWN":
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
            ):
                cfg = {
                    "experiment_id": meta.get("experiment_id"),
                    "workload": meta.get("workload"),
                    "slo": meta.get("slo"),
                }
                if "profile" in meta:
                    cfg["profile"] = meta["profile"]
                if "script" in meta:
                    cfg["script"] = meta["script"]
                if "k6_thresholds_crossed" in meta:
                    cfg["k6_thresholds_crossed"] = meta["k6_thresholds_crossed"]
                (run_dir / "experiment_config.json").write_text(json.dumps(cfg))
            RUN_META_PATH.unlink()
        except (json.JSONDecodeError, OSError):
            meta = None

    return data, run_dir, meta


def load_current_yaml() -> str:
    """Deployment + HPA YAML for the prompt."""
    parts = []
    if DEPLOYMENT_YAML.exists():
        parts.append(f"# FILE: {DEPLOYMENT_YAML.relative_to(REPO_ROOT)}\n")
        parts.append(DEPLOYMENT_YAML.read_text())
    if HPA_YAML.exists():
        parts.append(f"\n# FILE: {HPA_YAML.relative_to(REPO_ROOT)}\n")
        parts.append(HPA_YAML.read_text())
    return "\n".join(parts) if parts else ""


def run_analysis(run_dir: Path | None = None) -> tuple[dict, Path]:
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
                }
            except (json.JSONDecodeError, OSError):
                pass

    k6_path = run_dir / "k6-run-summary.json"
    config = get_config_from_yaml(DEPLOYMENT_YAML, HPA_YAML)
    observed_override = None
    start_ts = None
    end_ts = None
    if meta is not None:
        start_ts = meta.get("start_ts")
        end_ts = meta.get("end_ts")
        if start_ts is not None and end_ts is not None:
            start_ts = float(start_ts)
            end_ts = float(end_ts)
            from .prometheus_collect import get_prometheus_observed

            observed_override = get_prometheus_observed(
                start_ts=start_ts,
                end_ts=end_ts,
                namespace="default",
                deployment_name="stress-service",
                prometheus_url=PROMETHEUS_URL,
                cpu_limit_m=config.get("cpu_limit_m") or 500,
                mem_limit_mib=config.get("mem_limit_mib") or 256,
            )

    experiment_config = None
    if meta is not None and (
        "experiment_id" in meta
        or "workload" in meta
        or "slo" in meta
        or "k6_thresholds_crossed" in meta
    ):
        experiment_config = {
            "experiment_id": meta.get("experiment_id"),
            "workload": meta.get("workload"),
            "slo": meta.get("slo"),
        }
        if "profile" in meta:
            experiment_config["profile"] = meta["profile"]
        if "script" in meta:
            experiment_config["script"] = meta["script"]
        if "k6_thresholds_crossed" in meta:
            experiment_config["k6_thresholds_crossed"] = meta["k6_thresholds_crossed"]
    if experiment_config is None:
        config_path = run_dir / "experiment_config.json"
        if config_path.exists():
            try:
                with open(config_path) as f:
                    experiment_config = json.load(f)
            except (json.JSONDecodeError, OSError):
                pass
    exp_data = build_experiment_payload(
        run_dir,
        k6_path,
        DEPLOYMENT_YAML,
        HPA_YAML,
        experiment_config=experiment_config,
        observed_override=observed_override,
    )
    if start_ts is not None:
        exp_data["start_ts"] = start_ts
    if end_ts is not None:
        exp_data["end_ts"] = end_ts
    (run_dir / "experiment.json").write_text(json.dumps(exp_data, indent=2))

    yaml_str = load_current_yaml()
    user_prompt = build_user_prompt(exp_data, yaml_str)
    result = analyze_with_llm(SYSTEM_PROMPT, user_prompt)
    result = _postprocess_llm_result(result, exp_data)
    return result, run_dir


def write_outputs(result: dict, run_dir: Path) -> None:
    """Write report.md, recommended.diff (for display), analysis.json; overwrite repo YAMLs when LLM returns full files."""
    import difflib

    report = result.get("report", "")
    deployment_yaml_new = (result.get("deployment_yaml_new") or "").strip()
    hpa_yaml_new = (result.get("hpa_yaml_new") or "").strip()
    (run_dir / "report.md").write_text(report)

    diff_parts = []
    if deployment_yaml_new:
        old_dep = DEPLOYMENT_YAML.read_text() if DEPLOYMENT_YAML.exists() else ""
        DEPLOYMENT_YAML.parent.mkdir(parents=True, exist_ok=True)
        DEPLOYMENT_YAML.write_text(deployment_yaml_new)
        diff_parts.append(
            "".join(
                difflib.unified_diff(
                    old_dep.splitlines(keepends=True),
                    deployment_yaml_new.splitlines(keepends=True),
                    fromfile="service/k8s/deployment.yaml",
                    tofile="service/k8s/deployment.yaml",
                )
            )
        )
    if hpa_yaml_new:
        old_hpa = HPA_YAML.read_text() if HPA_YAML.exists() else ""
        HPA_YAML.parent.mkdir(parents=True, exist_ok=True)
        HPA_YAML.write_text(hpa_yaml_new)
        diff_parts.append(
            "".join(
                difflib.unified_diff(
                    old_hpa.splitlines(keepends=True),
                    hpa_yaml_new.splitlines(keepends=True),
                    fromfile="service/k8s/hpa.yaml",
                    tofile="service/k8s/hpa.yaml",
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
        "failure_archetype": result.get("failure_archetype", ""),
        "lambda_crit_estimate": result.get("lambda_crit_estimate"),
        "next_experiment": result.get("next_experiment", ""),
        "evidence": result.get("evidence", []),
        "observed_summary": _observed_summary_from_experiment(experiment)
        if experiment
        else {},
    }
    (run_dir / "analysis.json").write_text(json.dumps(analysis_artifact, indent=2))


def main() -> Path | None:
    result, run_dir = run_analysis()
    write_outputs(result, run_dir)
    print(f"Run output: {run_dir}")
    print(
        "  k6-run-summary.json, experiment.json, analysis.json, report.md, recommended.diff"
    )
    if result.get("failure_archetype"):
        print(f"  Failure archetype: {result.get('failure_archetype')}")
    return run_dir


if __name__ == "__main__":
    main()
