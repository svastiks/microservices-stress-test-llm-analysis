import argparse
import json
import os
import re
import subprocess
import time
from pathlib import Path
from analysis.apply_diff import apply_recommended_diff, ensure_up_demo_thin_baseline
from analysis.results import main as analysis_main
from analysis.results_db import write_boundary, write_iteration
from analysis.verify import run_verification, write_verification_output

REPO_ROOT = Path(__file__).resolve().parent
RESULTS_DIR = REPO_ROOT / "results"
EXPERIMENTS_PATH = REPO_ROOT / "experiments.json"


def _log(msg: str) -> None:
    print(f"[pipeline] {msg}")


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
    script_path = REPO_ROOT / "benchmarks" / "load-tests" / "k6" / f"{script_name}.js"
    script = (
        str(script_path)
        if script_path.exists()
        else "benchmarks/load-tests/k6/basic.js"
    )
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


def _read_k6_snapshot() -> dict:
    summary_path = RESULTS_DIR / "k6-summary.json"
    if not summary_path.exists():
        return {}
    try:
        data = json.loads(summary_path.read_text())
    except json.JSONDecodeError:
        return {}
    metrics = data.get("metrics") or {}
    return {
        "http_req_failed": (metrics.get("http_req_failed") or {}).get("value"),
        "checks_value": (metrics.get("checks") or {}).get("value"),
        "http_reqs": (metrics.get("http_reqs") or {}).get("count"),
        "p95_ms": (metrics.get("http_req_duration") or {}).get("p(95)"),
    }


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
    settle_seconds: int = 0,
    run_label: str | None = None,
    iteration_index: int | None = None,
    up_recovery: bool = False,
) -> Path | None:
    if settle_seconds > 0:
        _log(f"settling_before_run seconds={settle_seconds}")
        time.sleep(settle_seconds)
    profile_config = get_profile(profile)
    _log(
        f"run_start profile={profile} script={script} mode={mode} "
        f"analysis_goal={analysis_goal} prometheus={prometheus}"
    )
    start_ts = time.time()
    k6_exit = run_k6(profile_config, script, base_url=base_url)
    k6_snapshot = _read_k6_snapshot()
    _log(
        f"k6_done exit={k6_exit} http_req_failed={k6_snapshot.get('http_req_failed')} "
        f"checks={k6_snapshot.get('checks_value')} p95_ms={k6_snapshot.get('p95_ms')} "
        f"http_reqs={k6_snapshot.get('http_reqs')}"
    )
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
    if up_recovery:
        run_meta["up_recovery"] = True
    _write_run_meta(run_meta)
    _log("analysis_start")
    run_dir = analysis_main()
    _log(f"analysis_done run_dir={run_dir}")
    if run_dir is not None:
        status, exp = _read_experiment_status(run_dir)
        failure_reason = (exp.get("failure") or {}).get("reason")
        telemetry = ((exp.get("observed") or {}).get("telemetry") or {})
        _log(
            f"experiment_status={status} failure_reason={failure_reason} "
            f"cpu_util_pct={(exp.get('observed') or {}).get('cpu_util_pct')} "
            f"mem_util_pct={(exp.get('observed') or {}).get('mem_util_pct')} "
            f"utilization_trustworthy={telemetry.get('utilization_trustworthy')}"
        )
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
        "achieved_rps_target_window": observed.get(
            "achieved_requests_per_second_target_window"
        ),
        "dropped_iterations": observed.get("dropped_iterations"),
        "p95_ms": latency.get("p95"),
        "error_rate": observed.get("error_rate"),
        "cpu_util_pct": observed.get("cpu_util_pct"),
        "mem_util_pct": observed.get("mem_util_pct"),
        "replicas": observed.get("replicas"),
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
        "| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | Cost |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        md_lines.append(
            "| {run_dir} | {status} | {target_rps} | {achieved_rps} | {achieved_rps_target_window} | {dropped_iterations} | {p95_ms} | {error_rate} | {cpu_util_pct} | {mem_util_pct} | {replicas} | {cpu_request_m} | {mem_request_mib} | {cost_score} |".format(
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
    p.add_argument(
        "--profile",
        choices=["low", "medium", "high", "down_demo", "up_demo"],
        default="medium",
    )
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
        "--settle-seconds",
        type=int,
        default=int(os.environ.get("SQUEEZE_SETTLE_SECONDS", "30")),
        help="Post-rollout settle delay (seconds) before each squeeze iteration run.",
    )
    p.add_argument(
        "--until-violation",
        action="store_true",
        help=(
            "For squeeze mode, keep iterating until the first FAIL instead of stopping at "
            "--max-iterations. Under-provisioning (UP) recovery still honors --max-iterations."
        ),
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
        default="apps/service/k8s/deployment.yaml",
        help="Deployment YAML path to analyze/update/apply.",
    )
    p.add_argument(
        "--hpa-yaml",
        default="apps/service/k8s/hpa.yaml",
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
                settle_seconds=args.settle_seconds if mode == "squeeze" else 0,
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
            if args.profile == "up_demo" and k8s_apply_enabled:
                _log(
                    "up_demo: pinning cluster to thin baseline before iteration 1 "
                    "(single replica, HPA maxReplicas=1)"
                )
                ensure_up_demo_thin_baseline(
                    deployment_yaml_path=REPO_ROOT / deployment_yaml,
                    hpa_yaml_path=REPO_ROOT / hpa_yaml,
                    deployment_name=k8s_deployment,
                    namespace=k8s_namespace,
                    repo_root=REPO_ROOT,
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
                settle_seconds=args.settle_seconds,
                run_label=run_label,
                iteration_index=1,
            )
            if run_1_dir is None:
                raise RuntimeError("failed to create first squeeze iteration")
            best_pass_dir = None
            first_fail_dir = None
            squeeze_rows: list[dict] = []
            stopped_reason = "unknown"
            # UP movement path: allow recovery from an initial FAIL by applying scale-up diffs.
            up_recovery_active = False
            anchor_run_dir = run_1_dir

            status_1, exp_1 = _read_experiment_status(run_1_dir)
            squeeze_rows.append(_squeeze_row(run_1_dir, exp_1, status_1))
            if status_1 == "PASS":
                best_pass_dir = run_1_dir
                print(
                    f"[squeeze] Iteration 1 PASS, cost={((exp_1.get('cost') or {}).get('cost_score'))}"
                )
            else:
                first_diff = (run_1_dir / "recommended.diff").read_text().strip()
                first_hint = exp_1.get("scaling_hint")
                if first_diff and first_hint == "UP":
                    up_recovery_active = True
                    print(
                        "[squeeze] Iteration 1 FAIL with UP hint; entering scale-up recovery loop."
                    )
                else:
                    first_fail_dir = run_1_dir
                    stopped_reason = "first_run_failed"
                    print("[squeeze] Iteration 1 already failed; stopping.")
            # up_demo expects under-provisioned start (FAIL then UP). If iter 1 PASS, HPA likely
            # scaled out — do not run DOWN squeeze or we destroy the demo narrative.
            up_demo_skip_down_squeeze = args.profile == "up_demo" and status_1 == "PASS"
            if up_demo_skip_down_squeeze:
                stopped_reason = "up_demo_first_pass_overprovisioned"
                print(
                    "[squeeze] up_demo: iteration 1 PASS — not under-provisioned at this load "
                    "(HPA often scales out before k6). Skipping DOWN squeeze. "
                    "Use a thin baseline first (e.g. scale deploy to 1, HPA maxReplicas=1, "
                    "low CPU/mem) then re-run up_demo."
                )
            _write_squeeze_summary(
                squeeze_rows,
                run_root=run_root,
                best_pass_dir=best_pass_dir,
                first_fail_dir=first_fail_dir,
                stopped_reason=stopped_reason,
            )

            current_iteration = 1
            while (
                not up_demo_skip_down_squeeze
                and first_fail_dir is None
                and (best_pass_dir is not None or up_recovery_active)
                and (
                    (up_recovery_active and current_iteration < args.max_iterations)
                    or (
                        not up_recovery_active
                        and (
                            args.until_violation
                            or current_iteration < args.max_iterations
                        )
                    )
                )
            ):
                current_iteration += 1
                recommended_diff = (anchor_run_dir / "recommended.diff").read_text().strip()
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
                        anchor_run_dir,
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
                    settle_seconds=args.settle_seconds,
                    run_label=run_label,
                    iteration_index=current_iteration,
                    up_recovery=up_recovery_active,
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
                anchor_run_dir = next_run_dir
                if status == "PASS":
                    best_pass_dir = next_run_dir
                    print(
                        f"[squeeze] Iteration {current_iteration} PASS, cost={((exp.get('cost') or {}).get('cost_score'))}"
                    )
                    if up_recovery_active:
                        stopped_reason = "recovered_from_underprovisioning"
                        _write_squeeze_summary(
                            squeeze_rows,
                            run_root=run_root,
                            best_pass_dir=best_pass_dir,
                            first_fail_dir=first_fail_dir,
                            stopped_reason=stopped_reason,
                        )
                        print("[squeeze] Recovery complete after UP movement; stopping.")
                        break
                else:
                    if not up_recovery_active:
                        first_fail_dir = next_run_dir
                        stopped_reason = "first_fail"
                        print(f"[squeeze] Iteration {current_iteration} FAIL; stopping.")
                    else:
                        print(
                            f"[squeeze] Iteration {current_iteration} still FAIL in recovery mode; continuing."
                        )
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
            elif (
                stopped_reason == "unknown"
                and first_fail_dir is None
                and best_pass_dir is None
                and up_recovery_active
                and current_iteration >= args.max_iterations
            ):
                stopped_reason = "up_recovery_max_iterations_reached"
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
