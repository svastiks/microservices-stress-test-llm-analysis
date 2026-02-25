import json
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

    return data, run_dir


def load_current_yaml() -> str:
    if not COMPOSE_PATH.exists():
        return ""
    return COMPOSE_PATH.read_text()


def run_analysis() -> tuple[dict, Path]:
    summary, run_dir = load_summary()
    yaml_str = load_current_yaml()
    user_prompt = build_user_prompt(summary, yaml_str)
    result = analyze_with_llm(SYSTEM_PROMPT, user_prompt)
    return result, run_dir


def write_outputs(result: dict, run_dir: Path) -> None:
    report = result.get("report", "")
    yaml_fix = result.get("yaml_fix", "").strip()
    (run_dir / "report.md").write_text(report)
    if yaml_fix:
        (run_dir / "recommended.diff.yaml").write_text(yaml_fix)


def main() -> None:
    result, run_dir = run_analysis()
    write_outputs(result, run_dir)
    print(f"Run output: {run_dir}")
    print(f"  report.md, k6-run-summary.json" + (", recommended.diff.yaml" if result.get("yaml_fix") else ""))


if __name__ == "__main__":
    main()
