import argparse
import json
import os
import re
import subprocess
import time
from pathlib import Path
from analysis.apply_diff import apply_recommended_diff
from analysis.results import main as analysis_main
from analysis.results_db import write_boundary, write_iteration
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


def run_k6(profile_config: dict, script_name: str, base_url: str | None = None) -> int:
    """Run k6 load test. Returns k6 exit code (0 = pass, 99 = thresholds crossed)."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    if base_url:
        env["BASE_URL"] = base_url
    env["RPS"] = str(profile_config.get("RPS", 50))
    env["DURATION"] = str(profile_config.get("DURATION", "60s"))
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


def _write_run_meta(run_meta: dict) -> None:
    (RESULTS_DIR / "run_meta.json").write_text(json.dumps(run_meta))


def _next_run_label() -> str:
    max_idx = 0
    if RESULTS_DIR.exists():
        for p in RESULTS_DIR.iterdir():
            if not p.is_dir():
                continue
            m = re.fullmatch(r"run-(\d+)", p.name)
            if m:
                max_idx = max(max_idx, int(m.group(1)))
    return f"run-{max_idx + 1}"


def _run_once(
    profile: str,
    script: str,
    mode: str | None,
    *,
    base_url: str | None,
    prometheus: bool,
    k8s_namespace: str,
    k8s_deployment: str,
    analysis_goal: str,
    deployment_yaml: str,
    hpa_yaml: str,
    prometheus_url: str,
    run_label: str | None = None,
    iteration_index: int | None = None,
) -> Path | None:
    profile_config = get_profile(profile)
    start_ts = time.time()
    k6_exit = run_k6(profile_config, script, base_url=base_url)
    end_ts = time.time()
    run_meta: dict = {
        "start_ts": start_ts,
        "end_ts": end_ts,
        "profile": profile,
        "script": script,
        "mode": mode,
        "analysis_goal": analysis_goal,
        "k6_thresholds_crossed": k6_exit == 99,
        "prometheus": prometheus,
        "k8s_namespace": k8s_namespace,
        "k8s_deployment": k8s_deployment,
        "deployment_yaml": deployment_yaml,
        "hpa_yaml": hpa_yaml,
        "prometheus_url": prometheus_url,
    }
    if base_url:
        run_meta["base_url"] = base_url
        run_meta["service"] = "robot-shop-web"
        run_meta["endpoint"] = "POST /api/user/login"
    if profile_config:
        run_meta["experiment_id"] = profile_config.get("experiment_id")
        run_meta["workload"] = profile_config.get("workload")
        run_meta["slo"] = profile_config.get("slo")
    if run_label:
        run_meta["run_label"] = run_label
    if iteration_index is not None:
        run_meta["iteration_index"] = int(iteration_index)
    _write_run_meta(run_meta)
    run_dir = analysis_main()
    if run_dir is not None:
        try:
            write_iteration(run_dir, run_meta)
        except Exception as e:
            print(f"[results-db] iteration write skipped: {e}")
    return run_dir


def _read_experiment_status(run_dir: Path) -> tuple[str, dict]:
    exp_path = run_dir / "experiment.json"
    if not exp_path.exists():
        return "UNKNOWN", {}
    try:
        exp = json.loads(exp_path.read_text())
    except json.JSONDecodeError:
        return "UNKNOWN", {}
    failed = bool((exp.get("failure") or {}).get("failed"))
    return ("FAIL" if failed else "PASS"), exp


def _squeeze_row(run_dir: Path, experiment: dict, status: str) -> dict:
    observed = experiment.get("observed") or {}
    latency = observed.get("latency_ms") or {}
    config = experiment.get("config") or {}
    cost = experiment.get("cost") or {}
    return {
        "run_dir": str(run_dir),
        "status": status,
        "target_rps": (experiment.get("workload") or {}).get("target_requests_per_second"),
        "achieved_rps": observed.get("achieved_requests_per_second"),
        "p95_ms": latency.get("p95"),
        "error_rate": observed.get("error_rate"),
        "replicas": config.get("deployment_replicas"),
        "cpu_request_m": config.get("cpu_request_m"),
        "mem_request_mib": config.get("mem_request_mib"),
        "cost_score": cost.get("cost_score"),
    }


def _write_squeeze_summary(
    rows: list[dict],
    *,
    run_root: Path,
    best_pass_dir: Path | None,
    first_fail_dir: Path | None,
    stopped_reason: str,
) -> None:
    summary = {
        "stopped_reason": stopped_reason,
        "best_pass_dir": str(best_pass_dir) if best_pass_dir else None,
        "first_fail_dir": str(first_fail_dir) if first_fail_dir else None,
        "rows": rows,
    }
    run_root.mkdir(parents=True, exist_ok=True)
    (run_root / "cost-effective-boundary.json").write_text(json.dumps(summary, indent=2))

    md_lines = [
        "# Cost-Effective Boundary",
        "",
        f"- Stopped reason: {stopped_reason}",
        f"- Best pass: {best_pass_dir}" if best_pass_dir else "- Best pass: none",
        f"- First fail: {first_fail_dir}" if first_fail_dir else "- First fail: none",
        "",
        "| Run | Status | Target RPS | Achieved RPS | p95 ms | Error rate | Replicas | CPU req (m) | Mem req (Mi) | Cost |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        md_lines.append(
            "| {run_dir} | {status} | {target_rps} | {achieved_rps} | {p95_ms} | {error_rate} | {replicas} | {cpu_request_m} | {mem_request_mib} | {cost_score} |".format(
                **row
            )
        )
    (run_root / "cost-effective-boundary.md").write_text("\n".join(md_lines) + "\n")
    try:
        write_boundary(run_root, summary)
    except Exception as e:
        print(f"[results-db] boundary write skipped: {e}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Run k6 load test then LLM analysis")
    p.add_argument("--profile", choices=["low", "medium", "high"], default="medium")
    p.add_argument(
        "--script",
        choices=["login", "signup", "robotshop_login"],
        default="login",
        help="Which k6 script to run (stress-service login/signup or robotshop_login)",
    )
    mode_group = p.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--verify",
        action="store_true",
        help="Apply one recommendation and run a second time; compares run2 vs run1.",
    )
    mode_group.add_argument(
        "--squeeze",
        action="store_true",
        help="Iterative scale-down loop; repeats while PASS and stops on first FAIL (or other stop condition).",
    )
    p.add_argument(
        "--max-iterations",
        type=int,
        default=8,
        help="Maximum iterations for squeeze mode.",
    )
    p.add_argument(
        "--until-violation",
        action="store_true",
        help="For squeeze mode, keep iterating until the first FAIL instead of stopping at --max-iterations.",
    )
    p.add_argument(
        "--base-url",
        default=None,
        metavar="URL",
        help="HTTP base for k6 (e.g. http://localhost:8080 for Robot Shop web). Skips kubectl port-forward to stress-service.",
    )
    p.add_argument(
        "--robot-shop",
        action="store_true",
        help="Shortcut: sets BASE_URL to localhost:8080 (override via ROBOT_SHOP_BASE_URL) and uses robotshop_login k6 script.",
    )
    p.add_argument(
        "--no-prometheus",
        action="store_true",
        help="Do not port-forward Prometheus and skip Prom queries (Docker-only Robot Shop).",
    )
    p.add_argument(
        "--efficiency",
        action="store_true",
        help="Use efficiency (squeeze-style) LLM prompt: scale-down / cost, same fixed workload — even for K8s stress-service.",
    )
    p.add_argument(
        "--k8s-namespace",
        default=os.environ.get("K8S_NAMESPACE", "default"),
        help="Namespace for Prometheus scrape target (K8s SUT).",
    )
    p.add_argument(
        "--k8s-deployment",
        default=os.environ.get("K8S_DEPLOYMENT", "stress-service"),
        help="Deployment name for Prometheus scrape target.",
    )
    p.add_argument(
        "--deployment-yaml",
        default="service/k8s/deployment.yaml",
        help="Deployment YAML path to analyze/update/apply.",
    )
    p.add_argument(
        "--hpa-yaml",
        default="service/k8s/hpa.yaml",
        help="HPA YAML path to analyze/update/apply.",
    )
    p.add_argument(
        "--sut-service",
        default=os.environ.get("K8S_SERVICE", "stress-service"),
        help="Kubernetes Service name to port-forward when --base-url is not used.",
    )
    p.add_argument(
        "--sut-service-port",
        type=int,
        default=80,
        help="Service port to port-forward from when --base-url is not used.",
    )
    p.add_argument(
        "--prometheus-url",
        default=os.environ.get("PROMETHEUS_URL", "http://localhost:9090"),
        help="Prometheus base URL used by analysis (localhost uses port-forward; in-cluster DNS skips port-forward).",
    )
    args = p.parse_args()

    mode: str | None = None
    if args.verify:
        mode = "verify"
    elif args.squeeze or args.until_violation:
        mode = "squeeze"

    base_url = args.base_url
    if args.robot_shop:
        base_url = base_url or os.environ.get("ROBOT_SHOP_BASE_URL", "http://localhost:8080")
        args.script = "robotshop_login"

    if mode == "verify" and base_url:
        p.error(
            "verify applies Kubernetes YAML between runs; omit --base-url / --robot-shop, or use K8s for the SUT."
        )

    prometheus = not args.no_prometheus
    k8s_namespace = args.k8s_namespace
    k8s_deployment = args.k8s_deployment
    deployment_yaml = args.deployment_yaml
    hpa_yaml = args.hpa_yaml
    prometheus_url = args.prometheus_url
    analysis_goal = (
        "efficiency"
        if (base_url or args.efficiency)
        else "failure"
    )
    k8s_apply_enabled = bool(
        k8s_namespace and k8s_deployment and deployment_yaml and hpa_yaml
    )

    port_forwards: list[subprocess.Popen] = []
    try:
        if prometheus and (
            args.prometheus_url.startswith("http://localhost")
            or args.prometheus_url.startswith("http://127.0.0.1")
            or args.prometheus_url.startswith("https://localhost")
            or args.prometheus_url.startswith("https://127.0.0.1")
        ):
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
        if not base_url:
            port_forwards.append(
                start_port_forward(
                    [
                        "kubectl",
                        "-n",
                        args.k8s_namespace,
                        "port-forward",
                        f"svc/{args.sut_service}",
                        f"8000:{args.sut_service_port}",
                    ]
                )
            )
            # k6 scripts consume BASE_URL; point them at the forwarded local port.
            base_url = "http://localhost:8000"

        run_1_dir: Path | None = None
        if mode != "squeeze":
            run_1_dir = _run_once(
                args.profile,
                args.script,
                mode,
                base_url=base_url,
                prometheus=prometheus,
                k8s_namespace=k8s_namespace,
                k8s_deployment=k8s_deployment,
                analysis_goal=analysis_goal,
                deployment_yaml=deployment_yaml,
                hpa_yaml=hpa_yaml,
                prometheus_url=prometheus_url,
            )
        if run_1_dir is not None:
            if mode == "verify":
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
                            apply_recommended_diff(
                                run_1_dir,
                                deployment_yaml_path=(REPO_ROOT / deployment_yaml),
                                hpa_yaml_path=(REPO_ROOT / hpa_yaml),
                                deployment_name=k8s_deployment,
                                namespace=k8s_namespace,
                                repo_root=REPO_ROOT,
                            )
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
                            run_2_dir = _run_once(
                                profile,
                                script,
                                mode,
                                base_url=base_url,
                                prometheus=prometheus,
                                k8s_namespace=k8s_namespace,
                                k8s_deployment=k8s_deployment,
                                analysis_goal=analysis_goal,
                                deployment_yaml=deployment_yaml,
                                hpa_yaml=hpa_yaml,
                                prometheus_url=prometheus_url,
                            )
                            if run_2_dir is not None:
                                result = run_verification(run_1_dir, run_2_dir)
                                write_verification_output(result, run_1_dir, run_2_dir)
                                print(
                                    f"Verification written to {run_1_dir / 'verification'}"
                                )
        elif mode == "squeeze":
            run_label = _next_run_label()
            run_root = RESULTS_DIR / run_label
            print(
                (
                    "[squeeze] until first violation"
                    if args.until_violation
                    else f"[squeeze] max_iterations={args.max_iterations}"
                )
                + (
                    " (kubectl apply enabled)"
                    if (k8s_apply_enabled and (not base_url or args.efficiency))
                    else " (no kubectl apply — external BASE_URL)"
                )
                + f" [{run_label}]"
            )
            run_1_dir = _run_once(
                args.profile,
                args.script,
                mode,
                base_url=base_url,
                prometheus=prometheus,
                k8s_namespace=k8s_namespace,
                k8s_deployment=k8s_deployment,
                analysis_goal=analysis_goal,
                deployment_yaml=deployment_yaml,
                hpa_yaml=hpa_yaml,
                prometheus_url=prometheus_url,
                run_label=run_label,
                iteration_index=1,
            )
            if run_1_dir is None:
                raise RuntimeError("failed to create first squeeze iteration")
            best_pass_dir = None
            first_fail_dir = None
            squeeze_rows: list[dict] = []
            stopped_reason = "unknown"

            status_1, exp_1 = _read_experiment_status(run_1_dir)
            squeeze_rows.append(_squeeze_row(run_1_dir, exp_1, status_1))
            if status_1 == "PASS":
                best_pass_dir = run_1_dir
                print(
                    f"[squeeze] Iteration 1 PASS, cost={((exp_1.get('cost') or {}).get('cost_score'))}"
                )
            else:
                first_fail_dir = run_1_dir
                stopped_reason = "first_run_failed"
                print("[squeeze] Iteration 1 already failed; stopping.")
            _write_squeeze_summary(
                squeeze_rows,
                run_root=run_root,
                best_pass_dir=best_pass_dir,
                first_fail_dir=first_fail_dir,
                stopped_reason=stopped_reason,
            )

            current_iteration = 1
            while (
                first_fail_dir is None
                and best_pass_dir is not None
                and (args.until_violation or current_iteration < args.max_iterations)
            ):
                current_iteration += 1
                recommended_diff = (best_pass_dir / "recommended.diff").read_text().strip()
                if not recommended_diff:
                    print("[squeeze] No further optimization diff from LLM; frontier reached.")
                    stopped_reason = "empty_recommended_diff"
                    _write_squeeze_summary(
                        squeeze_rows,
                        run_root=run_root,
                        best_pass_dir=best_pass_dir,
                        first_fail_dir=first_fail_dir,
                        stopped_reason=stopped_reason,
                    )
                    break

                print(
                    f"[squeeze] Applying optimization and running iteration {current_iteration}..."
                )
                if base_url and not k8s_apply_enabled:
                    print(
                        "[squeeze] BASE_URL is set (e.g. Robot Shop in Docker): skipping "
                        "`kubectl apply`. Repo YAML still updates each analysis; k6 hits the same "
                        "URL — metrics reflect the live SUT, not every YAML change."
                    )
                else:
                    apply_recommended_diff(
                        best_pass_dir,
                        deployment_yaml_path=(REPO_ROOT / deployment_yaml),
                        hpa_yaml_path=(REPO_ROOT / hpa_yaml),
                        deployment_name=k8s_deployment,
                        namespace=k8s_namespace,
                        repo_root=REPO_ROOT,
                    )
                next_run_dir = _run_once(
                    args.profile,
                    args.script,
                    mode,
                    base_url=base_url,
                    prometheus=prometheus,
                    k8s_namespace=k8s_namespace,
                    k8s_deployment=k8s_deployment,
                    analysis_goal=analysis_goal,
                    deployment_yaml=deployment_yaml,
                    hpa_yaml=hpa_yaml,
                    prometheus_url=prometheus_url,
                    run_label=run_label,
                    iteration_index=current_iteration,
                )
                if next_run_dir is None:
                    stopped_reason = "next_run_missing"
                    _write_squeeze_summary(
                        squeeze_rows,
                        run_root=run_root,
                        best_pass_dir=best_pass_dir,
                        first_fail_dir=first_fail_dir,
                        stopped_reason=stopped_reason,
                    )
                    break
                status, exp = _read_experiment_status(next_run_dir)
                squeeze_rows.append(_squeeze_row(next_run_dir, exp, status))
                if status == "PASS":
                    best_pass_dir = next_run_dir
                    print(
                        f"[squeeze] Iteration {current_iteration} PASS, cost={((exp.get('cost') or {}).get('cost_score'))}"
                    )
                else:
                    first_fail_dir = next_run_dir
                    stopped_reason = "first_fail"
                    print(f"[squeeze] Iteration {current_iteration} FAIL; stopping.")
                _write_squeeze_summary(
                    squeeze_rows,
                    run_root=run_root,
                    best_pass_dir=best_pass_dir,
                    first_fail_dir=first_fail_dir,
                    stopped_reason=stopped_reason,
                )

            if (
                stopped_reason == "unknown"
                and first_fail_dir is None
                and best_pass_dir is not None
                and not args.until_violation
                and current_iteration >= args.max_iterations
            ):
                stopped_reason = "max_iterations_reached"
                _write_squeeze_summary(
                    squeeze_rows,
                    run_root=run_root,
                    best_pass_dir=best_pass_dir,
                    first_fail_dir=first_fail_dir,
                    stopped_reason=stopped_reason,
                )

            if best_pass_dir:
                print(f"[squeeze] Optimal frontier (last PASS): {best_pass_dir}")
            if first_fail_dir:
                print(f"[squeeze] First FAIL: {first_fail_dir}")
    finally:
        for proc in port_forwards:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except Exception:
                pass
