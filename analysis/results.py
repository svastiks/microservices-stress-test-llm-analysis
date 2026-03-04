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
            if "experiment_id" in meta or "workload" in meta or "slo" in meta:
                (run_dir / "experiment_config.json").write_text(
                    json.dumps(
                        {
                            "experiment_id": meta.get("experiment_id"),
                            "workload": meta.get("workload"),
                            "slo": meta.get("slo"),
                        }
                    )
                )
            RUN_META_PATH.unlink()
        except (json.JSONDecodeError, OSError):
            meta = None

    return data, run_dir, meta


def load_current_yaml() -> str:
    """Deployment + HPA YAML for the prompt."""
    parts = []
    if DEPLOYMENT_YAML.exists():
        parts.append(DEPLOYMENT_YAML.read_text())
    if HPA_YAML.exists():
        parts.append(HPA_YAML.read_text())
    return "\n---\n".join(parts) if parts else ""


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
                meta = {"start_ts": existing.get("start_ts"), "end_ts": existing.get("end_ts")}
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
    if meta is not None and ("experiment_id" in meta or "workload" in meta or "slo" in meta):
        experiment_config = {
            "experiment_id": meta.get("experiment_id"),
            "workload": meta.get("workload"),
            "slo": meta.get("slo"),
        }
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
    return result, run_dir


def write_outputs(result: dict, run_dir: Path) -> None:
    """Write report.md, recommended.diff, analysis.json."""
    report = result.get("report", "")
    yaml_fix = (result.get("yaml_fix") or "").strip()
    (run_dir / "report.md").write_text(report)
    (run_dir / "recommended.diff").write_text(yaml_fix)

    analysis_artifact = {
        "failure_archetype": result.get("failure_archetype", ""),
        "lambda_crit_estimate": result.get("lambda_crit_estimate"),
        "next_experiment": result.get("next_experiment", ""),
        "evidence": result.get("evidence", []),
    }
    (run_dir / "analysis.json").write_text(
        json.dumps(analysis_artifact, indent=2)
    )


def main() -> None:
    result, run_dir = run_analysis()
    write_outputs(result, run_dir)
    print(f"Run output: {run_dir}")
    print("  k6-run-summary.json, experiment.json, analysis.json, report.md, recommended.diff")
    if result.get("failure_archetype"):
        print(f"  Failure archetype: {result.get('failure_archetype')}")


if __name__ == "__main__":
    main()
