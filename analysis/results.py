import json
import shutil
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

from .api import analyze_with_llm
from .prompts import SYSTEM_PROMPT, build_user_prompt

SUMMARY_PATH = REPO_ROOT / "results" / "k6-summary.json"
COMPOSE_PATH = REPO_ROOT / "docker-compose.yml"
RESULTS_DIR = REPO_ROOT / "results"


def load_summary() -> tuple[dict, Path]:
    """Reads k6 summary, creates run dir and outputs artifacts."""
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
    # Move live-polled K8s timeseries into this run dir if present (from start.py when K8S=1)
    ts_src = RESULTS_DIR / "k8s-timeseries.json"
    if ts_src.exists():
        try:
            shutil.move(str(ts_src), str(run_dir / "k8s-timeseries.json"))
        except OSError:
            pass

    return data, run_dir


def load_current_yaml() -> str:
    if not COMPOSE_PATH.exists():
        return ""
    return COMPOSE_PATH.read_text()


def run_analysis() -> tuple[dict, Path]:
    summary, run_dir = load_summary()
    yaml_str = load_current_yaml()
    
    # Try to load or create experiment.json
    exp_path = run_dir / "experiment.json"
    exp_data = None
    if exp_path.exists():
        with open(exp_path) as f:
            exp_data = json.load(f)
    else:
        # Create experiment.json from k6 summary + config if available
        try:
            from .collect import build_payload
            config_path = REPO_ROOT / "experiment.config.json"
            if config_path.exists():
                use_k8s = __import__("os").environ.get("K8S") == "1"
                exp_data = build_payload(run_dir, config_path, "stress-service", use_k8s)
                (run_dir / "experiment.json").write_text(json.dumps(exp_data, indent=2))
        except Exception:
            pass
    
    # Use experiment.json if available, else legacy k6 summary
    if exp_data:
        user_prompt = build_user_prompt(exp_data, yaml_str)
    else:
        user_prompt = build_user_prompt(summary, yaml_str)
    
    result = analyze_with_llm(SYSTEM_PROMPT, user_prompt)
    return result, run_dir


def write_outputs(result: dict, run_dir: Path) -> None:
    report = result.get("report", "")
    yaml_fix = result.get("yaml_fix", "").strip()
    failure_archetype = result.get("failure_archetype", "")
    lambda_crit = result.get("lambda_crit_estimate", "")
    next_exp = result.get("next_experiment", "")
    evidence = result.get("evidence", [])
    
    (run_dir / "report.md").write_text(report)
    if yaml_fix:
        (run_dir / "recommended.diff.yaml").write_text(yaml_fix)
    
    # Write structured analysis JSON (include scaling when from K8s experiment)
    analysis_json = {
        "failure_archetype": failure_archetype,
        "lambda_crit_estimate": lambda_crit,
        "next_experiment": next_exp,
        "evidence": evidence,
    }
    exp_path = run_dir / "experiment.json"
    if exp_path.exists():
        try:
            exp = json.loads(exp_path.read_text())
            obs = exp.get("observed", {})
            if "scaled_during_test" in obs:
                analysis_json["scaled_during_test"] = obs["scaled_during_test"]
            if "replicas_at_start" in obs and "replicas" in obs:
                analysis_json["replicas_at_start"] = obs["replicas_at_start"]
                analysis_json["replicas"] = obs["replicas"]
            if "replicas_at_end" in obs:
                analysis_json["replicas_at_end"] = obs["replicas_at_end"]
        except (json.JSONDecodeError, OSError):
            pass
    (run_dir / "analysis.json").write_text(json.dumps(analysis_json, indent=2))
    


def main() -> None:
    result, run_dir = run_analysis()
    write_outputs(result, run_dir)
    artifacts = ["report.md", "k6-run-summary.json", "analysis.json", "sources.txt"]
    if result.get("yaml_fix"):
        artifacts.append("recommended.diff.yaml")
    if (run_dir / "experiment.json").exists():
        artifacts.append("experiment.json")
    if (run_dir / "k8s-snapshot.json").exists():
        artifacts.append("k8s-snapshot.json")
    if (run_dir / "k8s-timeseries.json").exists():
        artifacts.append("k8s-timeseries.json")
    print(f"Run output: {run_dir}")
    print(f"  {', '.join(artifacts)}")
    if result.get("failure_archetype"):
        print(f"  Failure archetype: {result.get('failure_archetype')}")
        if result.get("lambda_crit_estimate"):
            print(f"  λcrit estimate: {result.get('lambda_crit_estimate')} req/s")


if __name__ == "__main__":
    main()
