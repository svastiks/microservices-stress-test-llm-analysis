import argparse
import json
import os
import subprocess
import time
from pathlib import Path
from analysis.apply_diff import apply_recommended_diff
from analysis.results import main as analysis_main
from analysis.verify import run_verification, write_verification_output

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


def run_k6(profile_config: dict, script_name: str) -> int:
    """Run k6 load test. Returns k6 exit code (0 = pass, 99 = thresholds crossed)."""
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
    if result.returncode not in (0, 99):
        raise subprocess.CalledProcessError(result.returncode, cmd)
    return result.returncode


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Run k6 load test then LLM analysis")
    p.add_argument("--profile", choices=["low", "medium", "high"], default="medium")
    p.add_argument(
        "--script",
        choices=["login", "signup"],
        default="login",
        help="Which k6 script to run (login or signup)",
    )
    p.add_argument(
        "mode",
        nargs="?",
        choices=["verify"],
        help="Append 'verify' to auto-apply recommended.diff, re-run, and compare artifacts.",
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
        k6_exit = run_k6(profile_config, args.script)
        end_ts = time.time()
        run_meta = {
            "start_ts": start_ts,
            "end_ts": end_ts,
            "profile": args.profile,
            "script": args.script,
        }
        run_meta["k6_thresholds_crossed"] = k6_exit == 99
        if profile_config:
            run_meta["experiment_id"] = profile_config.get("experiment_id")
            run_meta["workload"] = profile_config.get("workload")
            run_meta["slo"] = profile_config.get("slo")
        (RESULTS_DIR / "run_meta.json").write_text(json.dumps(run_meta))
        run_1_dir = analysis_main()
        if run_1_dir is not None:
            if args.mode == "verify":
                verification_dir = run_1_dir / "verification"
                verification_md = verification_dir / "llm-result-verification.md"
                if verification_md.exists():
                    print(
                        f"Verification already exists at {verification_md}; skipping."
                    )
                else:
                    recommended_diff = (
                        (run_1_dir / "recommended.diff").read_text().strip()
                    )
                    if not recommended_diff:
                        print("recommended.diff is empty; skipping verify flow.")
                    else:
                        try:
                            print("Applying recommended diff...")
                            apply_recommended_diff(run_1_dir, REPO_ROOT)
                            print("Diff applied. Starting run 2 with same config...")
                        except Exception as e:
                            print(f"Diff apply or rollout failed: {e}")
                            verification_dir.mkdir(parents=True, exist_ok=True)
                            verification_md.write_text(
                                f"# Verification skipped\n\nDiff apply or rollout failed: {e}\n"
                            )
                            print(f"Verification note written to {verification_dir}")
                        else:
                            cfg_path = run_1_dir / "experiment_config.json"
                            if cfg_path.exists():
                                cfg = json.loads(cfg_path.read_text())
                                profile = cfg.get("profile", args.profile)
                                script = cfg.get("script", args.script)
                            else:
                                profile, script = args.profile, args.script
                            profile_config_2 = get_profile(profile)
                            start_ts = time.time()
                            k6_exit_2 = run_k6(profile_config_2, script)
                            end_ts = time.time()
                            run_meta_2 = {
                                "start_ts": start_ts,
                                "end_ts": end_ts,
                                "profile": profile,
                                "script": script,
                            }
                            run_meta_2["k6_thresholds_crossed"] = k6_exit_2 == 99
                            if profile_config_2:
                                run_meta_2["experiment_id"] = profile_config_2.get(
                                    "experiment_id"
                                )
                                run_meta_2["workload"] = profile_config_2.get(
                                    "workload"
                                )
                                run_meta_2["slo"] = profile_config_2.get("slo")
                            (RESULTS_DIR / "run_meta.json").write_text(
                                json.dumps(run_meta_2)
                            )
                            run_2_dir = analysis_main()
                            if run_2_dir is not None:
                                result = run_verification(run_1_dir, run_2_dir)
                                write_verification_output(result, run_1_dir, run_2_dir)
                                print(
                                    f"Verification written to {run_1_dir / 'verification'}"
                                )
    finally:
        for proc in port_forwards:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except Exception:
                pass
