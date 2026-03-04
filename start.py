import argparse
import json
import os
import subprocess
import time
from pathlib import Path
from analysis.results import main as analysis_main

REPO_ROOT = Path(__file__).resolve().parent
RESULTS_DIR = REPO_ROOT / "results"
EXPERIMENTS_PATH = REPO_ROOT / "experiments.json"


def start_port_forward(cmd: list[str]) -> subprocess.Popen:
    """Start a kubectl port-forward in the background."""
    proc = subprocess.Popen(
        cmd,
        cwd=REPO_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    # Give port-forward a moment to establish before load starts
    time.sleep(2)
    return proc


def get_profile(profile: str) -> dict:
    if not EXPERIMENTS_PATH.exists():
        return {}
    with open(EXPERIMENTS_PATH) as f:
        data = json.load(f)
    return data.get(profile, {})


def run_k6(profile_config: dict, script_name: str) -> None:
    """
    Run k6 load test.
    """
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["RPS"] = str(profile_config.get("RPS", 50))
    env["DURATION"] = str(profile_config.get("DURATION", "90s"))
    if profile_config.get("RPS", 0) > 200:
        env["maxVUs"] = str(profile_config["RPS"] + 100)
    script_path = REPO_ROOT / "load-tests" / "k6" / f"{script_name}.js"
    script = str(script_path) if script_path.exists() else "load-tests/k6/basic.js"
    cmd = [
        "k6",
        "run",
        "--summary-export=./results/k6-summary.json",
        script,
    ]
    result = subprocess.run(cmd, cwd=REPO_ROOT, env=env)
    # k6 uses exit code 99 when thresholds fail but summary is still written.
    if result.returncode not in (0, 99):
        raise subprocess.CalledProcessError(result.returncode, cmd)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Run k6 load test then LLM analysis")
    p.add_argument("--profile", choices=["low", "medium", "high"], default="medium")
    p.add_argument(
        "--script",
        choices=["login", "signup"],
        default="login",
        help="Which k6 script to run (login or signup)",
    )
    args = p.parse_args()
    profile_config = get_profile(args.profile)

    port_forwards: list[subprocess.Popen] = []
    try:
        # Prometheus (monitoring namespace)
        port_forwards.append(
            start_port_forward(
                [
                    "kubectl",
                    "-n",
                    "monitoring",
                    "port-forward",
                    "svc/kps-kube-prometheus-stack-prometheus",
                    "9090:9090",
                ]
            )
        )
        # Service under test (default namespace)
        port_forwards.append(
            start_port_forward(
                [
                    "kubectl",
                    "port-forward",
                    "svc/stress-service",
                    "8000:80",
                ]
            )
        )

        start_ts = time.time()
        run_k6(profile_config, args.script)
        end_ts = time.time()
        run_meta = {"start_ts": start_ts, "end_ts": end_ts}
        if profile_config:
            run_meta["experiment_id"] = profile_config.get("experiment_id")
            run_meta["workload"] = profile_config.get("workload")
            run_meta["slo"] = profile_config.get("slo")
        (RESULTS_DIR / "run_meta.json").write_text(json.dumps(run_meta))
        analysis_main()
    finally:
        for proc in port_forwards:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except Exception:
                pass

