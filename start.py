import subprocess
from pathlib import Path
from analysis.results import main as analysis_main


REPO_ROOT = Path(__file__).resolve().parent


def run_k6_basic() -> None:
    cmd = [
        "k6",
        "run",
        "--summary-export=./results/k6-summary.json",
        "load-tests/k6/basic.js",
    ]
    subprocess.run(cmd, cwd=REPO_ROOT, check=True)


def run_analysis() -> None:
    """Start LLM based analysis."""
    analysis_main()


if __name__ == "__main__":
    run_k6_basic()
    run_analysis()

