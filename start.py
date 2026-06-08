import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

from analysis.results import squeeze_cluster_ahead_of_yaml
from analysis.apply_diff import (
    apply_hpa_only_baseline,
    apply_managed_web_baseline,
    apply_recommended_diff,
    apply_recovery_probe_up_step,
    apply_squeeze_stall_resource_step,
    apply_violation_probe_down_step,
    ensure_squeeze_cluster_ready_before_k6,
    ensure_up_demo_thin_baseline,
    kubectl_apply,
    prepare_squeeze_observe_before_k6,
    reset_managed_web_yaml_to_baseline,
    squeeze_yaml_live_replica_drift,
    wait_rollout,
)
from analysis.results import main as analysis_main
from analysis.cost_model import boundary_cost_totals
from analysis.results_db import write_boundary, write_iteration
from analysis.results_paths import results_dir as _results_dir_for_repo
from analysis.verify import run_verification, write_verification_output
from analysis.experiment_build import apply_config_to_managed_yaml
from analysis.compare_shared_measure import (
    SHARED_CANONICAL_EXPERIMENT_FILENAME,
    compare_paired_measure_enabled,
    compare_skip_iteration_1,
    extract_shared_canonical_fields,
    format_paired_probe_report,
    paired_burn_delta_pct,
    paired_burn_tolerance_pct,
)
from analysis.experiment_build import get_config_from_yaml
from analysis.replay_trajectory import (
    load_boundary_rows,
    load_iteration_config,
    write_replay_comparison,
)

REPO_ROOT = Path(__file__).resolve().parent
EXPERIMENTS_PATH = REPO_ROOT / "experiments.json"


def _results_dir() -> Path:
    return _results_dir_for_repo(REPO_ROOT)


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


def _effective_profile_config(profile: str) -> dict:
    """
    Profile JSON from experiments.json, with optional k6 overrides from the environment
    (so cluster jobs can vary RPS without adding new --profile argparse choices).

    STRESS_K6_RPS: integer target RPS (updates RPS, workload.target_requests_per_second)
    STRESS_K6_DURATION: k6 duration string, e.g. 90s (updates DURATION, workload.duration_s when parseable)
    """
    base = get_profile(profile) or {}
    cfg = json.loads(json.dumps(base)) if base else {}
    rps_ov = os.environ.get("STRESS_K6_RPS", "").strip()
    if rps_ov:
        try:
            r = int(rps_ov)
            cfg["RPS"] = r
            wl = dict(cfg.get("workload") or {})
            wl["target_requests_per_second"] = r
            cfg["workload"] = wl
        except ValueError:
            pass
    dur_ov = os.environ.get("STRESS_K6_DURATION", "").strip()
    if dur_ov:
        cfg["DURATION"] = dur_ov
        wl = dict(cfg.get("workload") or {})
        ds = dur_ov.rstrip("sS")
        try:
            wl["duration_s"] = int(float(ds))
        except ValueError:
            pass
        cfg["workload"] = wl
    return cfg


def _validate_k6_summary_export(summary_path: Path) -> None:
    """Fail fast when k6 exited 0/99 but produced no traffic or a broken summary (e.g. dead BASE_URL)."""
    if os.environ.get("K6_SKIP_SUMMARY_HEALTH_CHECK", "").lower() in {"1", "true", "yes"}:
        return
    if not summary_path.exists():
        raise RuntimeError(f"k6 summary missing at {summary_path}")
    try:
        data = json.loads(summary_path.read_text())
    except json.JSONDecodeError as e:
        raise RuntimeError(f"k6 summary is not valid JSON: {summary_path} ({e})") from e
    metrics = data.get("metrics") or {}
    http = metrics.get("http_reqs") or {}
    count = http.get("count")
    if count is None:
        raise RuntimeError(
            f"k6 summary has no http_reqs.count (unexpected format); see {summary_path}"
        )
    if int(count) < 1:
        raise RuntimeError(
            f"k6 made zero HTTP requests (http_reqs.count={count}); "
            f"check BASE_URL / port-forward / service health. summary={summary_path}"
        )


def _squeeze_warmup_duration() -> str | None:
    raw = os.environ.get("SQUEEZE_WARMUP_K6_DURATION", "60s").strip()
    if not raw or raw.lower() in ("0", "false", "off", "no", "none", "skip"):
        return None
    return raw


def _run_squeeze_warmup_k6(
    profile_config: dict,
    script: str,
    base_url: str | None,
) -> None:
    duration = _squeeze_warmup_duration()
    if not duration:
        return
    _log(f"warmup_k6 duration={duration} (metrics discarded)")
    warmup_summary = _results_dir() / "k6-warmup-summary.json"
    run_k6(
        profile_config,
        script,
        base_url=base_url,
        duration_override=duration,
        summary_export=warmup_summary,
    )


def run_k6(
    profile_config: dict,
    script_name: str,
    base_url: str | None = None,
    *,
    duration_override: str | None = None,
    summary_export: Path | None = None,
) -> int:
    """Run k6 load test. Returns k6 exit code (0 = pass, 99 = thresholds crossed)."""
    rd = _results_dir()
    rd.mkdir(parents=True, exist_ok=True)
    if summary_export is None:
        summary_export = rd / "k6-summary.json"
    env = os.environ.copy()
    if base_url:
        env["BASE_URL"] = base_url
    env["RPS"] = str(profile_config.get("RPS", 50))
    env["DURATION"] = str(
        duration_override or profile_config.get("DURATION", "60s")
    )
    slo_cfg = profile_config.get("slo") or {}
    env["SLO_P95_MS"] = str(slo_cfg.get("p95_latency_ms", 500))
    env["SLO_ERROR_RATE"] = str(slo_cfg.get("error_rate", 0.01))
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
        f"--summary-export={summary_export}",
        script,
    ]
    result = subprocess.run(cmd, cwd=REPO_ROOT, env=env)
    if result.returncode not in (0, 99):
        raise subprocess.CalledProcessError(result.returncode, cmd)
    _validate_k6_summary_export(summary_export)
    return result.returncode


def _read_k6_snapshot() -> dict:
    summary_path = _results_dir() / "k6-summary.json"
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
    (_results_dir() / "run_meta.json").write_text(json.dumps(run_meta))


def _next_run_label() -> str:
    forced = os.environ.get("STRESS_RESULTS_RUN_LABEL", "").strip()
    if forced:
        return forced
    max_idx = 0
    rd = _results_dir()
    if rd.exists():
        for p in rd.iterdir():
            if not p.is_dir():
                continue
            m = re.fullmatch(r"run-(\d+)", p.name)
            if m:
                max_idx = max(max_idx, int(m.group(1)))
    return f"run-{max_idx + 1}"


def _max_run_index_under(parent: Path) -> int:
    max_idx = 0
    if not parent.is_dir():
        return 0
    for p in parent.iterdir():
        if not p.is_dir():
            continue
        m = re.fullmatch(r"run-(\d+)", p.name)
        if m:
            max_idx = max(max_idx, int(m.group(1)))
    return max_idx


def _prune_compare_run_dirs(repo_root: Path, *subdir_names: str) -> None:
    if os.environ.get("SQUEEZE_COMPARE_PRUNE_PRIOR", "1").strip().lower() not in (
        "1",
        "true",
        "yes",
        "on",
    ):
        return
    for sub in subdir_names:
        parent = repo_root / "results" / sub.strip().strip("/")
        if not parent.is_dir():
            continue
        for p in list(parent.iterdir()):
            if p.is_dir() and re.fullmatch(r"run-\d+", p.name):
                shutil.rmtree(p, ignore_errors=True)
                print(f"[squeeze-compare] pruned prior {p}", flush=True)


def _allocate_compare_pair_label(repo_root: Path, sub_formula: str, sub_llm: str) -> str:
    n = max(
        _max_run_index_under(repo_root / "results" / sub_formula),
        _max_run_index_under(repo_root / "results" / sub_llm),
    )
    return f"run-{n + 1}"


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
    squeeze_optimizer: str = "hybrid",
) -> Path | None:
    if settle_seconds > 0:
        _log(f"settling_before_run seconds={settle_seconds}")
        time.sleep(settle_seconds)
    profile_config = _effective_profile_config(profile)
    _log(
        f"run_start profile={profile} script={script} mode={mode} "
        f"analysis_goal={analysis_goal} prometheus={prometheus}"
    )
    if mode == "squeeze":
        _run_squeeze_warmup_k6(profile_config, script, base_url)
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
    if squeeze_optimizer and squeeze_optimizer != "hybrid":
        run_meta["squeeze_optimizer"] = squeeze_optimizer
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


def _squeeze_progress_key(experiment: dict) -> tuple:
    """Dimensions that must change between productive DOWN iterations."""
    cfg = experiment.get("config") or {}
    hpa = cfg.get("hpa") or {}
    observed = experiment.get("observed") or {}
    cost = experiment.get("cost") or {}
    return (
        cfg.get("cpu_request_m"),
        cfg.get("mem_request_mib"),
        cfg.get("deployment_replicas"),
        hpa.get("min_replicas"),
        hpa.get("max_replicas"),
        observed.get("replicas"),
        cost.get("cost_score"),
    )


def _squeeze_effective_progress_key(experiment: dict) -> tuple:
    """Live scale + provisioned resources + cost (detects yaml/live replica stall)."""
    cfg = experiment.get("config") or {}
    observed = experiment.get("observed") or {}
    cost = experiment.get("cost") or {}
    live_rep = max(
        int(observed.get("replicas") or 0),
        int(observed.get("replicas_max") or 0),
    )
    score = cost.get("cost_score")
    try:
        score = round(float(score), 6) if score is not None else None
    except (TypeError, ValueError):
        score = None
    return (
        cfg.get("cpu_request_m"),
        cfg.get("mem_request_mib"),
        live_rep,
        score,
    )


def _is_up_demo_profile(profile: str | None) -> bool:
    return (profile or "").strip() in {"up_demo", "up_demo_strict"}


def _squeeze_preflight_before_k6(
    *,
    mode: str,
    profile: str,
    base_url: str | None,
    k8s_apply_enabled: bool,
    deployment_yaml: str,
    hpa_yaml: str,
    k8s_namespace: str,
    k8s_deployment: str,
) -> None:
    if mode != "squeeze" or (base_url and not k8s_apply_enabled):
        return
    # down_demo compare: wait for yaml/live replica match. up_demo uses thin baseline + UP recovery.
    if _is_up_demo_profile(profile):
        return
    dep_path = REPO_ROOT / deployment_yaml
    hpa_path = REPO_ROOT / hpa_yaml
    ensure_squeeze_cluster_ready_before_k6(
        deployment_yaml_path=dep_path,
        hpa_yaml_path=hpa_path,
        deployment_name=k8s_deployment,
        namespace=k8s_namespace,
    )


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
        "cpu_util_request_pct": observed.get("cpu_util_request_pct"),
        "cpu_util_request_pct_peak": observed.get("cpu_util_request_pct_peak"),
        "mem_util_pct": observed.get("mem_util_pct"),
        "mem_util_pct_peak": observed.get("mem_util_pct_peak"),
        "cpu_usage_avg_m": observed.get("cpu_usage_avg_m"),
        "replicas": observed.get("replicas"),
        "cpu_request_m": config.get("cpu_request_m"),
        "mem_request_mib": config.get("mem_request_mib"),
        "cpu_limit_m": config.get("cpu_limit_m"),
        "mem_limit_mib": config.get("mem_limit_mib"),
        "cost_score": cost.get("cost_score"),
        "cost_score_util": cost.get("cost_score_util"),
    }


def _write_squeeze_summary(
    rows: list[dict],
    *,
    run_root: Path,
    best_pass_dir: Path | None,
    first_fail_dir: Path | None,
    stopped_reason: str,
    squeeze_optimizer: str | None = None,
) -> None:
    summary = {
        "stopped_reason": stopped_reason,
        "best_pass_dir": str(best_pass_dir) if best_pass_dir else None,
        "first_fail_dir": str(first_fail_dir) if first_fail_dir else None,
        "rows": rows,
    }
    if squeeze_optimizer:
        summary["squeeze_optimizer"] = squeeze_optimizer
    summary.update(boundary_cost_totals(rows))
    run_root.mkdir(parents=True, exist_ok=True)
    (run_root / "cost-effective-boundary.json").write_text(json.dumps(summary, indent=2))

    md_lines = [
        "# Cost-Effective Boundary",
        "",
        f"- Stopped reason: {stopped_reason}",
        f"- Best pass: {best_pass_dir}" if best_pass_dir else "- Best pass: none",
        f"- First fail: {first_fail_dir}" if first_fail_dir else "- First fail: none",
        f"- Cost model: {summary.get('cost_model', 'weighted')} · search={summary.get('cost_search')} · "
        f"steady={summary.get('cost_steady_state')} · total={summary.get('cost_total')} "
        f"(T={summary.get('cost_iteration_hours')}h, H={summary.get('cost_horizon_hours')}h)",
        "",
        "| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Prov cost | Util cost |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        md_lines.append(
            "| {run_dir} | {status} | {target_rps} | {achieved_rps} | {achieved_rps_target_window} | {dropped_iterations} | {p95_ms} | {error_rate} | {cpu_util_pct} | {mem_util_pct} | {replicas} | {cpu_request_m} | {mem_request_mib} | {cpu_limit_m} | {mem_limit_mib} | {cost_score} | {cost_score_util} |".format(
                **{**row, "cost_score_util": row.get("cost_score_util", "—")}
            )
        )
    (run_root / "cost-effective-boundary.md").write_text("\n".join(md_lines) + "\n")
    try:
        write_boundary(run_root, summary)
    except Exception as e:
        print(f"[results-db] boundary write skipped: {e}")


def _warn_squeeze_boundary_health(boundary_path: Path, label: str) -> None:
    """Surface common causes of empty diffs / short runs in logs."""
    try:
        data = json.loads(boundary_path.read_text())
    except (OSError, json.JSONDecodeError) as e:
        print(f"[squeeze-compare] WARNING: {label} boundary invalid: {e}", flush=True)
        return
    rows = data.get("rows") or []
    sr = data.get("stopped_reason")
    if not rows:
        print(
            f"[squeeze-compare] WARNING: {label} has no boundary rows (stopped_reason={sr!r})",
            flush=True,
        )
    if sr == "up_recovery_probe_exhausted":
        print(
            f"[squeeze-compare] WARNING: {label} stopped on up_recovery_probe_exhausted — "
            "empty recommended.diff during UP recovery and synthetic UP probe hit caps; "
            "cluster may still be under capacity.",
            flush=True,
        )
    if sr == "until_violation_probe_exhausted":
        print(
            f"[squeeze-compare] WARNING: {label} stopped on until_violation_probe_exhausted — "
            "empty recommended.diff and deployment CPU/memory could not be reduced further "
            "(probe floors); no measured FAIL in boundary.",
            flush=True,
        )
    if sr == "empty_recommended_diff":
        print(
            f"[squeeze-compare] WARNING: {label} stopped on empty_recommended_diff — "
            "usually utilization_trustworthy=false, scaling_hint not UP/DOWN, or LLM returned empty YAML; "
            f"inspect {boundary_path.parent}/iteration-1/",
            flush=True,
        )
    if sr == "first_run_failed":
        print(
            f"[squeeze-compare] WARNING: {label} stopped on first_run_failed — comparison may be one-sided",
            flush=True,
        )
    if sr == "no_progress":
        print(
            f"[squeeze-compare] WARNING: {label} stopped on no_progress — "
            "two consecutive PASS iterations had identical provisioned config (often request floors); "
            "inspect last recommended.diff.",
            flush=True,
        )


def _latest_run_root(results_parent: Path) -> Path | None:
    best_n = -1
    best: Path | None = None
    if not results_parent.is_dir():
        return None
    for p in results_parent.iterdir():
        if not p.is_dir():
            continue
        m = re.fullmatch(r"run-(\d+)", p.name)
        if not m:
            continue
        n = int(m.group(1))
        if n > best_n:
            best_n = n
            best = p
    return best


def _replay_trajectory_pipeline(
    args: argparse.Namespace,
    *,
    base_url: str | None,
    prometheus: bool,
    k8s_namespace: str,
    k8s_deployment: str,
    analysis_goal: str,
    deployment_yaml: str,
    hpa_yaml: str,
    prometheus_url: str,
) -> int:
    """Re-apply each source iteration config and run k6 (observe-only); compare metrics."""
    source_raw = (
        (getattr(args, "replay_source", None) or "")
        or os.environ.get("REPLAY_SOURCE_PATH", "")
    ).strip()
    if not source_raw:
        print("[replay] ERROR: set --replay-source or REPLAY_SOURCE_PATH", flush=True)
        return 1
    source_path = Path(source_raw)
    if not source_path.is_absolute():
        source_path = REPO_ROOT / source_path
    try:
        source_run, source_rows = load_boundary_rows(source_path)
    except (FileNotFoundError, ValueError) as e:
        print(f"[replay] ERROR: {e}", flush=True)
        return 1

    dep_path = REPO_ROOT / deployment_yaml
    hpa_path = REPO_ROOT / hpa_yaml
    k8s_apply_enabled = bool(
        k8s_namespace and k8s_deployment and deployment_yaml and hpa_yaml
    )
    # Match squeeze loop: skip kubectl only for external BASE_URL without k8s (Docker-only).
    skip_kubectl_apply = bool(base_url) and not k8s_apply_enabled
    squeeze_kubectl = k8s_apply_enabled and not skip_kubectl_apply

    run_label = os.environ.get("STRESS_RESULTS_RUN_LABEL", "").strip() or _next_run_label()
    run_root = _results_dir() / run_label
    replay_rows: list[dict] = []
    print(
        f"[replay] source={source_run} iterations={len(source_rows)} "
        f"dest={run_root}",
        flush=True,
    )

    for i, row in enumerate(source_rows, start=1):
        cfg = load_iteration_config(source_run, i, row)
        apply_config_to_managed_yaml(cfg, dep_path, hpa_path)
        from analysis.k8s_manifest import align_squeeze_hpa_to_deployment_replicas

        align_squeeze_hpa_to_deployment_replicas(dep_path, hpa_path)
        if squeeze_kubectl:
            print(f"[replay] applying config iteration {i} ...", flush=True)
            kubectl_apply(dep_path, hpa_path, REPO_ROOT)
            wait_rollout(deployment_name=k8s_deployment, namespace=k8s_namespace)
            pinned = prepare_squeeze_observe_before_k6(
                deployment_yaml_path=dep_path,
                hpa_yaml_path=hpa_path,
                deployment_name=k8s_deployment,
                namespace=k8s_namespace,
            )
            print(
                f"[replay] iteration {i} observe-ready replicas={pinned}",
                flush=True,
            )
        run_dir = _run_once(
            args.profile,
            args.script,
            "squeeze",
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
            iteration_index=i,
            squeeze_optimizer="replay",
        )
        if run_dir is None:
            print(f"[replay] ERROR: iteration {i} produced no run dir", flush=True)
            return 1
        status, exp = _read_experiment_status(run_dir)
        obs = exp.get("observed") or {}
        cfg_repl = int(cfg.get("deployment_replicas") or 0)
        obs_repl = int(obs.get("replicas") or 0)
        if cfg_repl and obs_repl and cfg_repl != obs_repl:
            print(
                f"[replay] WARNING iteration {i}: config replicas={cfg_repl} "
                f"!= observed={obs_repl} (replay may be invalid)",
                flush=True,
            )
        replay_rows.append(_squeeze_row(run_dir, exp, status))
        print(
            f"[replay] iteration {i} {status} repl={obs_repl} "
            f"cpu%={obs.get('cpu_util_request_pct')} burn={obs.get('cpu_usage_avg_m')}",
            flush=True,
        )

    _write_squeeze_summary(
        replay_rows,
        run_root=run_root,
        best_pass_dir=None,
        first_fail_dir=None,
        stopped_reason="replay_complete",
        squeeze_optimizer="replay",
    )
    out = write_replay_comparison(source_run, run_root)
    print(f"[replay] comparison written to {out}", flush=True)
    return 0


def _compare_paired_run_dir(results_parent: Path, pair_id: str) -> Path | None:
    """Resolve the compare arm run dir for this job's paired label (not highest run-*)."""
    run_dir = results_parent / pair_id
    return run_dir if run_dir.is_dir() else None


def _run_observe_probe_measure(
    *,
    profile: str,
    script: str,
    base_url: str | None,
    prometheus: bool,
    k8s_namespace: str,
    k8s_deployment: str,
    deployment_yaml: str,
    hpa_yaml: str,
    prometheus_url: str,
    label: str,
) -> dict:
    """Warmup + measured k6 + Prometheus observe (no LLM). For paired stability probes."""
    profile_config = _effective_profile_config(profile)
    _log(f"paired_probe_{label} start")
    _run_squeeze_warmup_k6(profile_config, script, base_url)
    start_ts = time.time()
    k6_exit = run_k6(profile_config, script, base_url=base_url)
    end_ts = time.time()
    _log(f"paired_probe_{label} k6_done exit={k6_exit}")
    out: dict = {
        "start_ts": start_ts,
        "end_ts": end_ts,
        "cpu_usage_avg_m": None,
        "cpu_util_request_pct": None,
    }
    if not prometheus:
        return out
    from analysis.prometheus_collect import DEFAULT_PROMETHEUS_URL, get_prometheus_observed

    dep_path = REPO_ROOT / deployment_yaml
    hpa_path = REPO_ROOT / hpa_yaml
    cfg = get_config_from_yaml(dep_path, hpa_path)
    hpa = cfg.get("hpa") or {}
    observed = get_prometheus_observed(
        start_ts=float(start_ts),
        end_ts=float(end_ts),
        namespace=k8s_namespace or "default",
        deployment_name=k8s_deployment or "stress-service",
        prometheus_url=prometheus_url or DEFAULT_PROMETHEUS_URL,
        cpu_request_m=int(cfg.get("cpu_request_m") or 0),
        cpu_limit_m=cfg.get("cpu_limit_m") or 500,
        mem_limit_mib=cfg.get("mem_limit_mib") or 256,
        deployment_replicas=int(cfg.get("deployment_replicas") or 0),
        hpa_min_replicas=int(hpa.get("min_replicas") or 0),
    )
    out["cpu_usage_avg_m"] = (observed or {}).get("cpu_usage_avg_m")
    out["cpu_util_request_pct"] = (observed or {}).get("cpu_util_request_pct")
    return out


def _reanalyze_shared_iteration(
    args: argparse.Namespace,
    *,
    pair_id: str,
    src_subdir: str,
    dest_subdir: str,
    optimizer: str,
    llm_vanilla: bool | None,
    base_url: str | None,
    prometheus: bool,
    analysis_goal: str,
) -> Path | None:
    """Copy shared iter-1 k6 window; re-run analysis under another optimizer/prompt."""
    src_iter = REPO_ROOT / "results" / src_subdir / pair_id / "iteration-1"
    if not src_iter.is_dir():
        raise FileNotFoundError(f"shared iter-1 missing: {src_iter}")
    dest_root = REPO_ROOT / "results" / dest_subdir
    dest_iter = dest_root / pair_id / "iteration-1"
    dest_iter.parent.mkdir(parents=True, exist_ok=True)
    if dest_iter.exists():
        shutil.rmtree(dest_iter)
    shutil.copytree(src_iter, dest_iter)
    for name in ("analysis.json", "experiment.json", "report.md", "recommended.diff"):
        p = dest_iter / name
        if p.exists():
            p.unlink()
    k6_iter = dest_iter / "k6-run-summary.json"
    if not k6_iter.is_file():
        raise FileNotFoundError(f"missing k6-run-summary in {dest_iter}")
    shutil.copy(k6_iter, dest_root / "k6-summary.json")

    src_exp_path = src_iter / "experiment.json"
    start_ts = end_ts = None
    k6_crossed = False
    if src_exp_path.is_file():
        try:
            src_exp = json.loads(src_exp_path.read_text())
            start_ts = src_exp.get("start_ts")
            end_ts = src_exp.get("end_ts")
            k6_crossed = bool(src_exp.get("k6_thresholds_crossed"))
            canonical = extract_shared_canonical_fields(src_exp)
            if canonical:
                (dest_iter / SHARED_CANONICAL_EXPERIMENT_FILENAME).write_text(
                    json.dumps(canonical, indent=2)
                )
                _log(
                    "shared_iter1_canonical_frozen "
                    f"cpu_req={((canonical.get('config') or {}).get('cpu_request_m'))} "
                    f"burn={((canonical.get('observed') or {}).get('cpu_usage_avg_m'))}"
                )
        except json.JSONDecodeError:
            pass

    prev_sub = os.environ.get("STRESS_RESULTS_SUBDIR")
    prev_vanilla = os.environ.get("SQUEEZE_LLM_VANILLA")
    os.environ["STRESS_RESULTS_SUBDIR"] = dest_subdir
    if llm_vanilla is not None:
        os.environ["SQUEEZE_LLM_VANILLA"] = "1" if llm_vanilla else "0"
    profile_config = _effective_profile_config(args.profile)
    run_meta: dict = {
        "start_ts": start_ts,
        "end_ts": end_ts,
        "profile": args.profile,
        "script": args.script,
        "mode": "squeeze",
        "analysis_goal": analysis_goal,
        "k6_thresholds_crossed": k6_crossed,
        "prometheus": prometheus,
        "k8s_namespace": args.k8s_namespace,
        "k8s_deployment": args.k8s_deployment,
        "deployment_yaml": args.deployment_yaml,
        "hpa_yaml": args.hpa_yaml,
        "prometheus_url": args.prometheus_url,
        "run_label": pair_id,
        "iteration_index": 1,
        "squeeze_optimizer": optimizer,
    }
    if base_url:
        run_meta["base_url"] = base_url
        run_meta["service"] = "robot-shop-web"
        run_meta["endpoint"] = "POST /api/user/login"
    if profile_config:
        run_meta["experiment_id"] = profile_config.get("experiment_id")
        run_meta["workload"] = profile_config.get("workload")
        run_meta["slo"] = profile_config.get("slo")
    _write_run_meta(run_meta)
    _log(f"shared_iter1_reanalyze optimizer={optimizer} subdir={dest_subdir}")
    run_dir = analysis_main()
    if prev_sub:
        os.environ["STRESS_RESULTS_SUBDIR"] = prev_sub
    else:
        os.environ.pop("STRESS_RESULTS_SUBDIR", None)
    if prev_vanilla is None:
        os.environ.pop("SQUEEZE_LLM_VANILLA", None)
    else:
        os.environ["SQUEEZE_LLM_VANILLA"] = prev_vanilla
    return run_dir


def _run_shared_compare_iteration_1(
    args: argparse.Namespace,
    *,
    pair_id: str,
    arm_a_subdir: str,
    arm_b_subdir: str,
    optimizer_a: str,
    optimizer_b: str,
    llm_vanilla_a: bool | None = None,
    llm_vanilla_b: bool | None = None,
    base_url: str | None,
    prometheus: bool,
    analysis_goal: str,
    k8s_apply_enabled: bool,
) -> None:
    """One canonical k6 at baseline YAML; both compare arms analyze the same observed telemetry."""
    if not compare_paired_measure_enabled():
        return
    print(
        f"[squeeze-compare] paired shared iteration-1 pair={pair_id} "
        f"({optimizer_a} + {optimizer_b})",
        flush=True,
    )
    probes: list[dict] = []
    for label in ("a", "b"):
        _squeeze_preflight_before_k6(
            mode="squeeze",
            profile=args.profile,
            base_url=base_url,
            k8s_apply_enabled=k8s_apply_enabled,
            deployment_yaml=args.deployment_yaml,
            hpa_yaml=args.hpa_yaml,
            k8s_namespace=args.k8s_namespace,
            k8s_deployment=args.k8s_deployment,
        )
        probes.append(
            _run_observe_probe_measure(
                profile=args.profile,
                script=args.script,
                base_url=base_url,
                prometheus=prometheus,
                k8s_namespace=args.k8s_namespace,
                k8s_deployment=args.k8s_deployment,
                deployment_yaml=args.deployment_yaml,
                hpa_yaml=args.hpa_yaml,
                prometheus_url=args.prometheus_url,
                label=label,
            )
        )
    tol = paired_burn_tolerance_pct()
    ba = float(probes[0].get("cpu_usage_avg_m") or 0)
    bb = float(probes[1].get("cpu_usage_avg_m") or 0)
    delta = paired_burn_delta_pct(ba, bb)
    report = format_paired_probe_report(
        pair_id=pair_id,
        probe_a=probes[0],
        probe_b=probes[1],
        tolerance_pct=tol,
    )
    print(report, flush=True)
    if delta > tol:
        print(
            f"[squeeze-compare] WARNING: paired probe burn delta {delta:.1f}% "
            f"exceeds tolerance {tol:.1f}%",
            flush=True,
        )

    prev_sub = os.environ.get("STRESS_RESULTS_SUBDIR")
    prev_label = os.environ.get("STRESS_RESULTS_RUN_LABEL")
    prev_vanilla = os.environ.get("SQUEEZE_LLM_VANILLA")
    os.environ["STRESS_RESULTS_SUBDIR"] = arm_a_subdir
    os.environ["STRESS_RESULTS_RUN_LABEL"] = pair_id
    if llm_vanilla_a is not None:
        os.environ["SQUEEZE_LLM_VANILLA"] = "1" if llm_vanilla_a else "0"

    _squeeze_preflight_before_k6(
        mode="squeeze",
        profile=args.profile,
        base_url=base_url,
        k8s_apply_enabled=k8s_apply_enabled,
        deployment_yaml=args.deployment_yaml,
        hpa_yaml=args.hpa_yaml,
        k8s_namespace=args.k8s_namespace,
        k8s_deployment=args.k8s_deployment,
    )
    run_a = _run_once(
        args.profile,
        args.script,
        "squeeze",
        base_url=base_url,
        prometheus=prometheus,
        k8s_namespace=args.k8s_namespace,
        k8s_deployment=args.k8s_deployment,
        analysis_goal=analysis_goal,
        deployment_yaml=args.deployment_yaml,
        hpa_yaml=args.hpa_yaml,
        prometheus_url=args.prometheus_url,
        settle_seconds=args.settle_seconds,
        run_label=pair_id,
        iteration_index=1,
        squeeze_optimizer=optimizer_a,
    )
    if run_a is None:
        raise RuntimeError("shared compare iteration-1 canonical measure failed")

    _reanalyze_shared_iteration(
        args,
        pair_id=pair_id,
        src_subdir=arm_a_subdir,
        dest_subdir=arm_b_subdir,
        optimizer=optimizer_b,
        llm_vanilla=llm_vanilla_b,
        base_url=base_url,
        prometheus=prometheus,
        analysis_goal=analysis_goal,
    )

    for sub in (arm_a_subdir, arm_b_subdir):
        out = REPO_ROOT / "results" / sub / pair_id / "paired-baseline-probe.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report)

    if prev_sub:
        os.environ["STRESS_RESULTS_SUBDIR"] = prev_sub
    else:
        os.environ.pop("STRESS_RESULTS_SUBDIR", None)
    if prev_label:
        os.environ["STRESS_RESULTS_RUN_LABEL"] = prev_label
    else:
        os.environ.pop("STRESS_RESULTS_RUN_LABEL", None)
    if prev_vanilla is None:
        os.environ.pop("SQUEEZE_LLM_VANILLA", None)
    else:
        os.environ["SQUEEZE_LLM_VANILLA"] = prev_vanilla

    os.environ["SQUEEZE_COMPARE_SKIP_ITERATION_1"] = "1"
    print(
        "[squeeze-compare] shared iteration-1 complete; subprocess arms skip re-measure",
        flush=True,
    )


def _run_squeeze_subprocess(
    args: argparse.Namespace,
    *,
    optimizer: str,
    results_subdir: str,
    final_report_llm: bool,
    squeeze_max_iterations: int,
    squeeze_until_violation: bool,
    llm_vanilla: bool | None = None,
) -> int:
    env = os.environ.copy()
    env["STRESS_RESULTS_SUBDIR"] = results_subdir
    env["SQUEEZE_OPTIMIZER"] = optimizer
    if llm_vanilla is not None:
        env["SQUEEZE_LLM_VANILLA"] = "1" if llm_vanilla else "0"
    pair = os.environ.get("SQUEEZE_COMPARE_PAIR_ID", "").strip()
    if pair:
        env["STRESS_RESULTS_RUN_LABEL"] = pair
    if compare_skip_iteration_1():
        env["SQUEEZE_COMPARE_SKIP_ITERATION_1"] = "1"
    cap = max(1, int(squeeze_max_iterations))
    cmd = [
        sys.executable,
        str(REPO_ROOT / "start.py"),
        "--squeeze",
        "--profile",
        args.profile,
        "--script",
        args.script,
        "--max-iterations",
        str(cap),
        "--settle-seconds",
        str(args.settle_seconds),
        "--k8s-namespace",
        str(args.k8s_namespace),
        "--k8s-deployment",
        str(args.k8s_deployment),
        "--deployment-yaml",
        args.deployment_yaml,
        "--hpa-yaml",
        args.hpa_yaml,
        "--sut-service",
        args.sut_service,
        "--sut-service-port",
        str(args.sut_service_port),
        "--prometheus-url",
        args.prometheus_url,
        "--squeeze-optimizer",
        optimizer,
    ]
    if args.robot_shop:
        cmd.append("--robot-shop")
    if args.base_url:
        cmd.extend(["--base-url", args.base_url])
    if args.no_prometheus:
        cmd.append("--no-prometheus")
    if args.efficiency:
        cmd.append("--efficiency")
    if squeeze_until_violation:
        cmd.append("--until-violation")
    if final_report_llm and optimizer == "formula":
        cmd.append("--squeeze-final-report-llm")
    print(
        f"[squeeze-compare] subprocess optimizer={optimizer} subdir={results_subdir} "
        f"max_iterations={cap} until_violation={squeeze_until_violation} "
        f"llm_vanilla={env.get('SQUEEZE_LLM_VANILLA', '<inherit>')}",
        flush=True,
    )
    proc = subprocess.run(cmd, cwd=REPO_ROOT, env=env)
    if proc.returncode != 0:
        print(
            f"[squeeze-compare] subprocess failed exit={proc.returncode} "
            f"optimizer={optimizer} (see logs above)",
            flush=True,
        )
    return proc.returncode


def _run_hpa_only_subprocess(args: argparse.Namespace, *, results_subdir: str) -> int:
    env = os.environ.copy()
    env["STRESS_RESULTS_SUBDIR"] = results_subdir
    pair = os.environ.get("SQUEEZE_COMPARE_PAIR_ID", "").strip()
    if pair:
        env["STRESS_RESULTS_RUN_LABEL"] = pair
    cmd = [
        sys.executable,
        str(REPO_ROOT / "start.py"),
        "--hpa-only",
        "--profile",
        args.profile,
        "--script",
        args.script,
        "--settle-seconds",
        str(args.settle_seconds),
        "--k8s-namespace",
        str(args.k8s_namespace),
        "--k8s-deployment",
        str(args.k8s_deployment),
        "--deployment-yaml",
        args.deployment_yaml,
        "--hpa-yaml",
        args.hpa_yaml,
        "--sut-service",
        args.sut_service,
        "--sut-service-port",
        str(args.sut_service_port),
        "--prometheus-url",
        args.prometheus_url,
        "--efficiency",
    ]
    if args.robot_shop:
        cmd.append("--robot-shop")
    if args.base_url:
        cmd.extend(["--base-url", args.base_url])
    if args.no_prometheus:
        cmd.append("--no-prometheus")
    print(
        f"[hpa-compare] subprocess hpa-only subdir={results_subdir}",
        flush=True,
    )
    proc = subprocess.run(cmd, cwd=REPO_ROOT, env=env)
    if proc.returncode != 0:
        print(
            f"[hpa-compare] subprocess failed exit={proc.returncode} (see logs above)",
            flush=True,
        )
    return proc.returncode


def _hpa_only_pipeline(
    args: argparse.Namespace,
    *,
    base_url: str | None,
    prometheus: bool,
    k8s_namespace: str,
    k8s_deployment: str,
    deployment_yaml: str,
    hpa_yaml: str,
    prometheus_url: str,
    analysis_goal: str,
) -> int:
    """Single k6 window with HPA enabled; writes one-row cost-effective boundary."""
    k8s_apply_enabled = bool(k8s_namespace and k8s_deployment and deployment_yaml and hpa_yaml)
    if not k8s_apply_enabled:
        print("[hpa-only] requires k8s deployment/hpa paths", flush=True)
        return 1

    pair = os.environ.get("SQUEEZE_COMPARE_PAIR_ID", "").strip()
    run_label = os.environ.get("STRESS_RESULTS_RUN_LABEL", "").strip() or _next_run_label()
    run_root = _results_dir() / run_label
    run_root.mkdir(parents=True, exist_ok=True)

    apply_hpa_only_baseline(
        deployment_yaml_path=REPO_ROOT / deployment_yaml,
        hpa_yaml_path=REPO_ROOT / hpa_yaml,
        deployment_name=k8s_deployment,
        namespace=k8s_namespace,
        profile=args.profile,
        repo_root=REPO_ROOT,
    )
    if args.settle_seconds > 0:
        _log(f"post-hpa-baseline settle seconds={args.settle_seconds}")
        time.sleep(args.settle_seconds)

    print(f"[hpa-only] run_label={run_label} profile={args.profile}", flush=True)
    run_dir = _run_once(
        args.profile,
        args.script,
        "squeeze",
        base_url=base_url,
        prometheus=prometheus,
        k8s_namespace=k8s_namespace,
        k8s_deployment=k8s_deployment,
        analysis_goal=analysis_goal,
        deployment_yaml=deployment_yaml,
        hpa_yaml=hpa_yaml,
        prometheus_url=prometheus_url,
        settle_seconds=0,
        run_label=run_label,
        iteration_index=1,
        squeeze_optimizer="hpa",
    )
    if run_dir is None:
        print("[hpa-only] run failed (no iteration dir)", flush=True)
        return 1

    status, exp = _read_experiment_status(run_dir)
    row = _squeeze_row(run_dir, exp, status)
    best_pass = run_dir if status == "PASS" else None
    first_fail = run_dir if status == "FAIL" else None
    _write_squeeze_summary(
        [row],
        run_root=run_root,
        best_pass_dir=best_pass,
        first_fail_dir=first_fail,
        stopped_reason="hpa_only",
        squeeze_optimizer="hpa",
    )
    print(f"[hpa-only] wrote {run_root / 'cost-effective-boundary.json'}", flush=True)
    return 0


def _apply_compare_arm_baseline(args: argparse.Namespace, *, label: str) -> None:
    """Shared cluster + YAML starting point for each compare arm."""
    print(f"[squeeze-compare] baseline reset ({label})...", flush=True)
    if _is_up_demo_profile(args.profile):
        print(
            "[squeeze-compare] up_demo: thin web baseline (1 replica, HPA max=1); "
            "start.py will re-pin before iteration 1.",
            flush=True,
        )
        ensure_up_demo_thin_baseline(
            deployment_yaml_path=REPO_ROOT / args.deployment_yaml,
            hpa_yaml_path=REPO_ROOT / args.hpa_yaml,
            deployment_name=args.k8s_deployment,
            namespace=args.k8s_namespace,
            repo_root=REPO_ROOT,
        )
    else:
        apply_managed_web_baseline(
            deployment_yaml_path=REPO_ROOT / args.deployment_yaml,
            hpa_yaml_path=REPO_ROOT / args.hpa_yaml,
            deployment_name=args.k8s_deployment,
            namespace=args.k8s_namespace,
            repo_root=REPO_ROOT,
        )
    if args.settle_seconds > 0:
        _log(f"post-baseline settle seconds={args.settle_seconds} ({label})")
        time.sleep(args.settle_seconds)


def _compare_squeeze_optimizers_main(args: argparse.Namespace) -> int:
    dep_path = REPO_ROOT / args.deployment_yaml
    hpa_path = REPO_ROOT / args.hpa_yaml
    sub_formula = (
        os.environ.get("SQUEEZE_COMPARE_SUBDIR_FORMULA", "squeeze-compare-formula")
        .strip()
        .strip("/")
        or "squeeze-compare-formula"
    )
    sub_llm = (
        os.environ.get("SQUEEZE_COMPARE_SUBDIR_LLM", "squeeze-compare-llm")
        .strip()
        .strip("/")
        or "squeeze-compare-llm"
    )
    try:
        # Formula phase: by default capped iterations only (no --until-violation) so compare stays bounded.
        # Set SQUEEZE_COMPARE_FORMULA_UNTIL_VIOLATION=1 to mirror LLM stop mode; ceiling is max(compare cap, --max-iterations).
        _formula_uv = os.environ.get("SQUEEZE_COMPARE_FORMULA_UNTIL_VIOLATION", "").strip().lower() in (
            "1",
            "true",
            "yes",
            "on",
        )
        _formula_cap = (
            max(int(args.compare_formula_max_iterations), int(args.max_iterations))
            if _formula_uv
            else int(args.compare_formula_max_iterations)
        )
        _prune_compare_run_dirs(REPO_ROOT, sub_formula, sub_llm)
        pair_id = _allocate_compare_pair_label(REPO_ROOT, sub_formula, sub_llm)
        os.environ["SQUEEZE_COMPARE_PAIR_ID"] = pair_id
        print(f"[squeeze-compare] paired run label={pair_id} (formula + llm)", flush=True)

        _apply_compare_arm_baseline(args, label="before shared iteration-1")
        k8s_apply_enabled = bool(
            args.k8s_namespace
            and args.k8s_deployment
            and args.deployment_yaml
            and args.hpa_yaml
        )
        base_url = args.base_url
        prometheus = not args.no_prometheus
        analysis_goal = "efficiency" if args.efficiency else "failure"
        _run_shared_compare_iteration_1(
            args,
            pair_id=pair_id,
            arm_a_subdir=sub_formula,
            arm_b_subdir=sub_llm,
            optimizer_a="formula",
            optimizer_b="llm",
            base_url=base_url,
            prometheus=prometheus,
            analysis_goal=analysis_goal,
            k8s_apply_enabled=k8s_apply_enabled and not (base_url and not k8s_apply_enabled),
        )
        c1 = _run_squeeze_subprocess(
            args,
            optimizer="formula",
            results_subdir=sub_formula,
            final_report_llm=args.squeeze_final_report_llm,
            squeeze_max_iterations=_formula_cap,
            squeeze_until_violation=_formula_uv,
        )
        _continue = os.environ.get(
            "SQUEEZE_COMPARE_CONTINUE_ON_FORMULA_FAIL", "1"
        ).strip().lower() in ("1", "true", "yes", "on")
        if c1 != 0 and not _continue:
            return c1
        if c1 != 0:
            print(
                "[squeeze-compare] formula arm failed; continuing to LLM arm "
                f"(pair={pair_id})",
                flush=True,
            )

        _apply_compare_arm_baseline(args, label="before llm arm")

        c2 = _run_squeeze_subprocess(
            args,
            optimizer="llm",
            results_subdir=sub_llm,
            final_report_llm=False,
            squeeze_max_iterations=args.max_iterations,
            squeeze_until_violation=args.until_violation,
        )
        if c2 != 0:
            return c2

        root_formula = REPO_ROOT / "results" / sub_formula
        root_llm = REPO_ROOT / "results" / sub_llm
        run_a = _compare_paired_run_dir(root_formula, pair_id)
        run_b = _compare_paired_run_dir(root_llm, pair_id)
        os.environ.pop("SQUEEZE_COMPARE_PAIR_ID", None)
        os.environ.pop("STRESS_RESULTS_RUN_LABEL", None)
        if not run_a or not run_b:
            print(
                f"[squeeze-compare] could not find paired run dirs "
                f"{pair_id} under comparison subdirs",
                flush=True,
            )
            return 1
        b_a = run_a / "cost-effective-boundary.json"
        b_b = run_b / "cost-effective-boundary.json"
        if not b_a.exists() or not b_b.exists():
            print(f"[squeeze-compare] missing boundary: {b_a} {b_b}", flush=True)
            return 1

        _warn_squeeze_boundary_health(b_a, "formula")
        _warn_squeeze_boundary_health(b_b, "llm")

        from analysis.compare_squeeze_methods import compare as compare_boundaries

        text = compare_boundaries(b_a, b_b, label_a="formula", label_b="llm")
        out = REPO_ROOT / "results" / "squeeze-optimizer-comparison.md"
        # Keep a stable "latest" file and a per-run immutable file.
        out_versioned = (
            REPO_ROOT
            / "results"
            / f"squeeze-optimizer-comparison-{run_a.name}-vs-{run_b.name}.md"
        )
        out.write_text(text)
        out_versioned.write_text(text)
        # Legacy cleanup: older images/scripts produced .txt for this report.
        legacy_txt = REPO_ROOT / "results" / "squeeze-optimizer-comparison.txt"
        if legacy_txt.exists():
            try:
                legacy_txt.unlink()
                print(f"[squeeze-compare] removed legacy {legacy_txt}", flush=True)
            except OSError as e:
                print(
                    f"[squeeze-compare] warning: could not remove legacy txt {legacy_txt}: {e}",
                    flush=True,
                )
        print(text, end="")
        print(f"[squeeze-compare] wrote {out}", flush=True)
        print(f"[squeeze-compare] wrote {out_versioned}", flush=True)
        return 0
    finally:
        try:
            reset_managed_web_yaml_to_baseline(dep_path, hpa_path)
        except Exception as e:
            print(f"[squeeze-compare] warning: could not restore baseline YAML: {e}", flush=True)


def _compare_advanced_vs_vanilla_llm_main(args: argparse.Namespace) -> int:
    """Advanced LLM (full metrics) vs vanilla LLM (coarse summary) on the same squeeze loop."""
    dep_path = REPO_ROOT / args.deployment_yaml
    hpa_path = REPO_ROOT / args.hpa_yaml
    sub_advanced = (
        os.environ.get("SQUEEZE_COMPARE_SUBDIR_ADVANCED", "squeeze-compare-advanced-llm")
        .strip()
        .strip("/")
        or "squeeze-compare-advanced-llm"
    )
    sub_vanilla = (
        os.environ.get("SQUEEZE_COMPARE_SUBDIR_VANILLA", "squeeze-compare-vanilla-llm")
        .strip()
        .strip("/")
        or "squeeze-compare-vanilla-llm"
    )
    try:
        _prune_compare_run_dirs(REPO_ROOT, sub_advanced, sub_vanilla)
        if os.environ.get("SQUEEZE_COMPARE_PRUNE_STALE_FORMULA", "1").strip().lower() in (
            "1",
            "true",
            "yes",
            "on",
        ):
            _prune_compare_run_dirs(REPO_ROOT, "squeeze-compare-formula")
        pair_id = _allocate_compare_pair_label(REPO_ROOT, sub_advanced, sub_vanilla)
        os.environ["SQUEEZE_COMPARE_PAIR_ID"] = pair_id
        print(
            f"[advanced-vanilla-compare] paired run label={pair_id} "
            f"(advanced-llm + vanilla-llm)",
            flush=True,
        )

        _apply_compare_arm_baseline(args, label="before shared iteration-1")
        k8s_apply_enabled = bool(
            args.k8s_namespace
            and args.k8s_deployment
            and args.deployment_yaml
            and args.hpa_yaml
        )
        base_url = args.base_url
        prometheus = not args.no_prometheus
        analysis_goal = "efficiency" if args.efficiency else "failure"
        _run_shared_compare_iteration_1(
            args,
            pair_id=pair_id,
            arm_a_subdir=sub_advanced,
            arm_b_subdir=sub_vanilla,
            optimizer_a="llm",
            optimizer_b="llm",
            llm_vanilla_a=False,
            llm_vanilla_b=True,
            base_url=base_url,
            prometheus=prometheus,
            analysis_goal=analysis_goal,
            k8s_apply_enabled=k8s_apply_enabled and not (base_url and not k8s_apply_enabled),
        )
        c1 = _run_squeeze_subprocess(
            args,
            optimizer="llm",
            results_subdir=sub_advanced,
            final_report_llm=False,
            squeeze_max_iterations=args.max_iterations,
            squeeze_until_violation=args.until_violation,
            llm_vanilla=False,
        )
        _continue = os.environ.get(
            "SQUEEZE_COMPARE_CONTINUE_ON_ADVANCED_FAIL", "1"
        ).strip().lower() in ("1", "true", "yes", "on")
        if c1 != 0 and not _continue:
            return c1
        if c1 != 0:
            print(
                "[advanced-vanilla-compare] advanced arm failed; continuing to vanilla arm "
                f"(pair={pair_id})",
                flush=True,
            )

        _apply_compare_arm_baseline(args, label="before vanilla-llm arm")
        c2 = _run_squeeze_subprocess(
            args,
            optimizer="llm",
            results_subdir=sub_vanilla,
            final_report_llm=False,
            squeeze_max_iterations=args.max_iterations,
            squeeze_until_violation=args.until_violation,
            llm_vanilla=True,
        )
        if c2 != 0:
            return c2

        root_adv = REPO_ROOT / "results" / sub_advanced
        root_van = REPO_ROOT / "results" / sub_vanilla
        run_a = _compare_paired_run_dir(root_adv, pair_id)
        run_b = _compare_paired_run_dir(root_van, pair_id)
        os.environ.pop("SQUEEZE_COMPARE_PAIR_ID", None)
        os.environ.pop("STRESS_RESULTS_RUN_LABEL", None)
        if not run_a or not run_b:
            print(
                f"[advanced-vanilla-compare] could not find paired run dirs "
                f"{pair_id} under comparison subdirs",
                flush=True,
            )
            return 1
        b_a = run_a / "cost-effective-boundary.json"
        b_b = run_b / "cost-effective-boundary.json"
        if not b_a.exists() or not b_b.exists():
            print(f"[advanced-vanilla-compare] missing boundary: {b_a} {b_b}", flush=True)
            return 1

        _warn_squeeze_boundary_health(b_a, "advanced-llm")
        _warn_squeeze_boundary_health(b_b, "vanilla-llm")

        from analysis.compare_squeeze_methods import compare as compare_boundaries

        text = compare_boundaries(
            b_a, b_b, label_a="advanced-llm", label_b="vanilla-llm"
        )
        out = REPO_ROOT / "results" / "squeeze-optimizer-comparison.md"
        out_versioned = (
            REPO_ROOT
            / "results"
            / f"squeeze-optimizer-comparison-{run_a.name}-vs-{run_b.name}.md"
        )
        out.write_text(text)
        out_versioned.write_text(text)
        print(text, end="")
        print(f"[advanced-vanilla-compare] wrote {out}", flush=True)
        return 0
    finally:
        try:
            reset_managed_web_yaml_to_baseline(dep_path, hpa_path)
        except Exception as e:
            print(
                f"[advanced-vanilla-compare] warning: could not restore baseline YAML: {e}",
                flush=True,
            )


def _compare_hpa_vs_llm_main(args: argparse.Namespace) -> int:
    dep_path = REPO_ROOT / args.deployment_yaml
    hpa_path = REPO_ROOT / args.hpa_yaml
    sub_hpa = (
        os.environ.get("SQUEEZE_COMPARE_SUBDIR_HPA", "squeeze-compare-hpa")
        .strip()
        .strip("/")
        or "squeeze-compare-hpa"
    )
    sub_llm = (
        os.environ.get("SQUEEZE_COMPARE_SUBDIR_LLM", "squeeze-compare-llm")
        .strip()
        .strip("/")
        or "squeeze-compare-llm"
    )
    try:
        _prune_compare_run_dirs(REPO_ROOT, sub_hpa, sub_llm)
        if os.environ.get("SQUEEZE_COMPARE_PRUNE_STALE_FORMULA", "1").strip().lower() in (
            "1",
            "true",
            "yes",
            "on",
        ):
            _prune_compare_run_dirs(REPO_ROOT, "squeeze-compare-formula")
        pair_id = _allocate_compare_pair_label(REPO_ROOT, sub_hpa, sub_llm)
        os.environ["SQUEEZE_COMPARE_PAIR_ID"] = pair_id
        print(f"[hpa-compare] paired run label={pair_id} (hpa + llm)", flush=True)

        print("[hpa-compare] HPA arm baseline...", flush=True)
        apply_hpa_only_baseline(
            deployment_yaml_path=dep_path,
            hpa_yaml_path=hpa_path,
            deployment_name=args.k8s_deployment,
            namespace=args.k8s_namespace,
            profile=args.profile,
            repo_root=REPO_ROOT,
        )
        if args.settle_seconds > 0:
            time.sleep(args.settle_seconds)

        c1 = _run_hpa_only_subprocess(args, results_subdir=sub_hpa)
        _continue = os.environ.get(
            "SQUEEZE_COMPARE_CONTINUE_ON_HPA_FAIL", "1"
        ).strip().lower() in ("1", "true", "yes", "on")
        if c1 != 0 and not _continue:
            return c1
        if c1 != 0:
            print(
                f"[hpa-compare] HPA arm failed; continuing to LLM arm (pair={pair_id})",
                flush=True,
            )

        _apply_compare_arm_baseline(args, label="before llm arm")
        c2 = _run_squeeze_subprocess(
            args,
            optimizer="llm",
            results_subdir=sub_llm,
            final_report_llm=False,
            squeeze_max_iterations=args.max_iterations,
            squeeze_until_violation=args.until_violation,
        )
        if c2 != 0:
            return c2

        root_hpa = REPO_ROOT / "results" / sub_hpa
        root_llm = REPO_ROOT / "results" / sub_llm
        run_a = _compare_paired_run_dir(root_hpa, pair_id)
        run_b = _compare_paired_run_dir(root_llm, pair_id)
        os.environ.pop("SQUEEZE_COMPARE_PAIR_ID", None)
        os.environ.pop("STRESS_RESULTS_RUN_LABEL", None)
        if not run_a or not run_b:
            print("[hpa-compare] could not find run-* under comparison subdirs", flush=True)
            return 1
        b_a = run_a / "cost-effective-boundary.json"
        b_b = run_b / "cost-effective-boundary.json"
        if not b_a.exists() or not b_b.exists():
            print(f"[hpa-compare] missing boundary: {b_a} {b_b}", flush=True)
            return 1

        _warn_squeeze_boundary_health(b_a, "hpa")
        _warn_squeeze_boundary_health(b_b, "llm")

        from analysis.compare_squeeze_methods import compare as compare_boundaries

        text = compare_boundaries(b_a, b_b, label_a="hpa", label_b="llm")
        out = REPO_ROOT / "results" / "squeeze-optimizer-comparison.md"
        out_versioned = (
            REPO_ROOT
            / "results"
            / f"squeeze-optimizer-comparison-{run_a.name}-vs-{run_b.name}.md"
        )
        out.write_text(text)
        out_versioned.write_text(text)
        print(text, end="")
        print(f"[hpa-compare] wrote {out}", flush=True)
        return 0
    finally:
        try:
            reset_managed_web_yaml_to_baseline(dep_path, hpa_path)
        except Exception as e:
            print(f"[hpa-compare] warning: could not restore baseline YAML: {e}", flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Run k6 load test then LLM analysis")
    p.add_argument(
        "--profile",
        choices=[
            "low",
            "medium",
            "high",
            "down_demo",
            "down_demo_r15",
            "down_demo_r25",
            "down_demo_r35",
            "down_demo_r45",
            "up_demo",
            "up_demo_strict",
        ],
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
    mode_group.add_argument(
        "--replay-trajectory",
        action="store_true",
        help=(
            "Re-apply each config from --replay-source boundary and run k6 again "
            "(observe-only). Writes replay-comparison.md vs source."
        ),
    )
    mode_group.add_argument(
        "--compare-squeeze-optimizers",
        action="store_true",
        help=(
            "Run squeeze with formula optimizer (STRESS_RESULTS_SUBDIR=squeeze-compare-formula by default), "
            "reset managed web to *.baseline.yaml + kubectl apply + replica_wait + settle before "
            "each arm, then run squeeze with LLM-only optimizer "
            "(squeeze-compare-llm). Writes results/squeeze-optimizer-comparison.md (Markdown tables). "
            "Formula phase uses --compare-formula-max-iterations (capped); "
            "env SQUEEZE_COMPARE_FORMULA_UNTIL_VIOLATION=1 adds --until-violation with ceiling "
            "max(compare cap, --max-iterations)."
        ),
    )
    mode_group.add_argument(
        "--compare-hpa-vs-llm",
        action="store_true",
        help=(
            "Method 2: one HPA-only load window (squeeze-compare-hpa) then vanilla LLM squeeze "
            "(squeeze-compare-llm). HPA may scale replicas; requests stay fixed. "
            "Writes results/squeeze-optimizer-comparison.md with labels hpa vs llm."
        ),
    )
    mode_group.add_argument(
        "--compare-advanced-vs-vanilla-llm",
        action="store_true",
        help=(
            "Compare advanced LLM squeeze (full experiment metrics in prompt) vs vanilla LLM "
            "(coarse summary + YAML only). Subdirs squeeze-compare-advanced-llm and "
            "squeeze-compare-vanilla-llm. Writes squeeze-optimizer-comparison.md."
        ),
    )
    p.add_argument(
        "--hpa-only",
        action="store_true",
        help="Single evaluation: fixed CPU/mem requests, HPA scales replicas during k6 (subprocess of --compare-hpa-vs-llm).",
    )
    p.add_argument(
        "--max-iterations",
        type=int,
        default=8,
        help="Maximum iterations for squeeze mode.",
    )
    p.add_argument(
        "--compare-formula-max-iterations",
        type=int,
        default=int(
            os.environ.get("SQUEEZE_COMPARE_FORMULA_MAX_ITERATIONS") or "3"
        ),
        help=(
            "With --compare-squeeze-optimizers: minimum iteration cap for the formula (first) phase; "
            "raised to max(--max-iterations, this value) when SQUEEZE_COMPARE_FORMULA_UNTIL_VIOLATION is set. "
            "Default 3 or env SQUEEZE_COMPARE_FORMULA_MAX_ITERATIONS."
        ),
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
            "For squeeze mode on Kubernetes: keep iterating toward the first measured FAIL so the "
            "last PASS is the frontier. With kubectl apply enabled, if the optimizer returns an "
            "empty recommended.diff, a small deterministic DOWN step on deployment CPU/memory may "
            "still be applied (env SQUEEZE_UNTIL_VIOLATION_PROBE_STEP_PCT) for formula/hybrid "
            "unless disabled; optimizer=llm skips that probe by default so compare LLM runs use "
            "LLM patches only (set SQUEEZE_UNTIL_VIOLATION_PROBE_LLM=1 to opt in). Without this flag, "
            "the loop stops at empty diff or the iteration cap. UP recovery still honors --max-iterations."
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
    p.add_argument(
        "--replay-source",
        default=os.environ.get("REPLAY_SOURCE_PATH", ""),
        help="Source run dir or cost-effective-boundary.json for --replay-trajectory.",
    )
    p.add_argument(
        "--squeeze-optimizer",
        choices=["hybrid", "formula", "llm", "hpa", "replay"],
        default=os.environ.get("SQUEEZE_OPTIMIZER", "hybrid"),
        help=(
            "squeeze YAML source: hybrid=LLM then deterministic override (default); "
            "formula=Python step only; llm=LLM only (no deterministic YAML); "
            "hpa=observe only (HPA-only arm); replay=set via --replay-trajectory."
        ),
    )
    p.add_argument(
        "--squeeze-final-report-llm",
        action="store_true",
        help=(
            "After a formula-only squeeze, call the LLM once for squeeze-formula-llm-summary.txt "
            "(optimization YAML was not from the LLM)."
        ),
    )
    args = p.parse_args()

    if args.replay_trajectory:
        if args.verify or args.squeeze or args.compare_squeeze_optimizers:
            p.error("--replay-trajectory is mutually exclusive with other run modes")
        base_url_replay = args.base_url
        if args.robot_shop:
            base_url_replay = base_url_replay or os.environ.get(
                "ROBOT_SHOP_BASE_URL", "http://localhost:8080"
            )
            args.script = "robotshop_login"
        prometheus_replay = not args.no_prometheus
        analysis_goal_replay = (
            "efficiency"
            if (base_url_replay or args.efficiency)
            else "failure"
        )
        sys.exit(
            _replay_trajectory_pipeline(
                args,
                base_url=base_url_replay,
                prometheus=prometheus_replay,
                k8s_namespace=args.k8s_namespace,
                k8s_deployment=args.k8s_deployment,
                analysis_goal=analysis_goal_replay,
                deployment_yaml=args.deployment_yaml,
                hpa_yaml=args.hpa_yaml,
                prometheus_url=args.prometheus_url,
            )
        )

    if args.compare_squeeze_optimizers:
        if args.verify:
            p.error("--compare-squeeze-optimizers cannot be used with --verify")
        sys.exit(_compare_squeeze_optimizers_main(args))

    if args.compare_hpa_vs_llm:
        if args.verify:
            p.error("--compare-hpa-vs-llm cannot be used with --verify")
        sys.exit(_compare_hpa_vs_llm_main(args))

    if args.compare_advanced_vs_vanilla_llm:
        if args.verify:
            p.error("--compare-advanced-vs-vanilla-llm cannot be used with --verify")
        sys.exit(_compare_advanced_vs_vanilla_llm_main(args))

    mode: str | None = None
    if args.verify:
        mode = "verify"
    elif args.squeeze or args.until_violation:
        mode = "squeeze"
    elif args.hpa_only:
        mode = "hpa_only"

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

        if mode == "hpa_only":
            sys.exit(
                _hpa_only_pipeline(
                    args,
                    base_url=base_url,
                    prometheus=prometheus,
                    k8s_namespace=k8s_namespace,
                    k8s_deployment=k8s_deployment,
                    deployment_yaml=deployment_yaml,
                    hpa_yaml=hpa_yaml,
                    prometheus_url=prometheus_url,
                    analysis_goal=analysis_goal,
                )
            )

        run_1_dir: Path | None = None
        if mode != "squeeze":
            single_run_label = os.environ.get("STRESS_RESULTS_RUN_LABEL", "").strip() or None
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
                run_label=single_run_label,
                squeeze_optimizer=args.squeeze_optimizer,
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
                                squeeze_optimizer=args.squeeze_optimizer,
                            )
                            if run_2_dir is not None:
                                result = run_verification(run_1_dir, run_2_dir)
                                write_verification_output(result, run_1_dir, run_2_dir)
                                print(
                                    f"Verification written to {run_1_dir / 'verification'}"
                                )
        elif mode == "squeeze":
            run_label = os.environ.get("STRESS_RESULTS_RUN_LABEL", "").strip() or _next_run_label()
            run_root = _results_dir() / run_label
            is_up_demo_profile = args.profile in {"up_demo", "up_demo_strict"}
            skip_iter1 = compare_skip_iteration_1() and (run_root / "iteration-1").is_dir()
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
                + f" [{run_label}] optimizer={args.squeeze_optimizer}"
                + (" shared-iter-1" if skip_iter1 else "")
            )
            if skip_iter1:
                print(
                    "[squeeze] using shared compare iteration-1 (same observed burn as paired arm)",
                    flush=True,
                )
                run_1_dir = run_root / "iteration-1"
            else:
                if is_up_demo_profile and k8s_apply_enabled:
                    _log(
                        f"{args.profile}: pinning cluster to thin baseline before iteration 1 "
                        "(single replica, HPA maxReplicas=1)"
                    )
                    ensure_up_demo_thin_baseline(
                        deployment_yaml_path=REPO_ROOT / deployment_yaml,
                        hpa_yaml_path=REPO_ROOT / hpa_yaml,
                        deployment_name=k8s_deployment,
                        namespace=k8s_namespace,
                        repo_root=REPO_ROOT,
                    )
                _squeeze_preflight_before_k6(
                    mode=mode,
                    profile=args.profile,
                    base_url=base_url,
                    k8s_apply_enabled=k8s_apply_enabled,
                    deployment_yaml=deployment_yaml,
                    hpa_yaml=hpa_yaml,
                    k8s_namespace=k8s_namespace,
                    k8s_deployment=k8s_deployment,
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
                    squeeze_optimizer=args.squeeze_optimizer,
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
                fail_1 = bool((exp_1.get("failure") or {}).get("failed"))
                up_demo_fail_recovery = (
                    is_up_demo_profile
                    and fail_1
                    and first_hint in ("UP", "HOLD", None)
                )
                if (first_diff and first_hint == "UP") or up_demo_fail_recovery:
                    up_recovery_active = True
                    print(
                        "[squeeze] Iteration 1 FAIL"
                        + (
                            " (up_demo under-provisioned start)"
                            if up_demo_fail_recovery and first_hint != "UP"
                            else " with UP hint"
                        )
                        + f", cost={((exp_1.get('cost') or {}).get('cost_score'))}; "
                        "entering scale-up recovery loop."
                    )
                else:
                    first_fail_dir = run_1_dir
                    stopped_reason = "first_run_failed"
                    print(
                        "[squeeze] Iteration 1 already failed, "
                        f"cost={((exp_1.get('cost') or {}).get('cost_score'))}; stopping."
                    )
            # up_demo* expects under-provisioned start (FAIL then UP). If iter 1 PASS, HPA likely
            # scaled out — do not run DOWN squeeze or we destroy the demo narrative.
            up_demo_skip_down_squeeze = is_up_demo_profile and status_1 == "PASS"
            if up_demo_skip_down_squeeze:
                stopped_reason = f"{args.profile}_first_pass_overprovisioned"
                print(
                    f"[squeeze] {args.profile}: iteration 1 PASS — not under-provisioned at this load "
                    "(HPA often scales out before k6). Skipping DOWN squeeze. "
                    "Use a thin baseline first (e.g. scale deploy to 1, HPA maxReplicas=1, "
                    f"low CPU/mem) then re-run {args.profile}."
                )
            _write_squeeze_summary(
                squeeze_rows,
                run_root=run_root,
                best_pass_dir=best_pass_dir,
                first_fail_dir=first_fail_dir,
                stopped_reason=stopped_reason,
                squeeze_optimizer=args.squeeze_optimizer,
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
                squeeze_kubectl = not (base_url and not k8s_apply_enabled)
                # Deterministic probe must not run for optimizer=llm during squeeze-compare LLM arm:
                # that phase should advance only on LLM-produced YAML, not hidden formula-like cuts.
                _llm_probe = os.environ.get("SQUEEZE_UNTIL_VIOLATION_PROBE_LLM", "").strip().lower() in (
                    "1",
                    "true",
                    "yes",
                    "on",
                )
                probe_allowed = (
                    args.until_violation
                    and not up_recovery_active
                    and squeeze_kubectl
                    and k8s_apply_enabled
                    and (args.squeeze_optimizer != "llm" or _llm_probe)
                )
                recovery_probe_applied = False
                probe_applied = False
                reconcile_apply = False
                if not recommended_diff:
                    exp_path = anchor_run_dir / "experiment.json"
                    if (
                        args.squeeze_optimizer == "llm"
                        and squeeze_kubectl
                        and k8s_apply_enabled
                        and not up_recovery_active
                        and exp_path.exists()
                    ):
                        try:
                            anchor_exp = json.loads(exp_path.read_text())
                            reconcile_apply = squeeze_cluster_ahead_of_yaml(anchor_exp)
                        except json.JSONDecodeError:
                            reconcile_apply = False
                    if reconcile_apply:
                        print(
                            "[squeeze] empty recommended.diff but live replicas exceed "
                            "managed YAML; re-applying cluster manifests before next iteration.",
                            flush=True,
                        )
                    elif up_recovery_active and squeeze_kubectl and k8s_apply_enabled:
                        recovery_probe_applied = apply_recovery_probe_up_step(
                            deployment_yaml_path=(REPO_ROOT / deployment_yaml),
                            hpa_yaml_path=(REPO_ROOT / hpa_yaml),
                            deployment_name=k8s_deployment,
                            namespace=k8s_namespace,
                            repo_root=REPO_ROOT,
                        )
                    elif probe_allowed:
                        probe_applied = apply_violation_probe_down_step(
                            deployment_yaml_path=(REPO_ROOT / deployment_yaml),
                            hpa_yaml_path=(REPO_ROOT / hpa_yaml),
                            deployment_name=k8s_deployment,
                            namespace=k8s_namespace,
                            repo_root=REPO_ROOT,
                        )
                    if not (
                        recovery_probe_applied or probe_applied or reconcile_apply
                    ):
                        if probe_allowed:
                            stopped_reason = "until_violation_probe_exhausted"
                            print(
                                "[squeeze] until_violation: empty recommended.diff and violation "
                                "probe could not shrink deployment further (floors or no resources); "
                                f"stopping (optimizer={args.squeeze_optimizer}).",
                                flush=True,
                            )
                        elif (
                            up_recovery_active
                            and squeeze_kubectl
                            and k8s_apply_enabled
                        ):
                            stopped_reason = "up_recovery_probe_exhausted"
                            print(
                                "[squeeze] up_recovery: empty recommended.diff and recovery UP "
                                "probe could not add capacity further (caps or no resources block); "
                                f"stopping (optimizer={args.squeeze_optimizer}).",
                                flush=True,
                            )
                        else:
                            stopped_reason = "empty_recommended_diff"
                            if (
                                args.until_violation
                                and args.squeeze_optimizer == "llm"
                                and squeeze_kubectl
                                and k8s_apply_enabled
                                and not _llm_probe
                            ):
                                print(
                                    "[squeeze] until_violation: empty recommended.diff with "
                                    "optimizer=llm; stopping without deterministic probe (LLM arm uses "
                                    "LLM patches only). Set SQUEEZE_UNTIL_VIOLATION_PROBE_LLM=1 to allow probe.",
                                    flush=True,
                                )
                            else:
                                print(
                                    "[squeeze] No further optimization diff; frontier reached "
                                    f"(optimizer={args.squeeze_optimizer}).",
                                    flush=True,
                                )
                        _write_squeeze_summary(
                            squeeze_rows,
                            run_root=run_root,
                            best_pass_dir=best_pass_dir,
                            first_fail_dir=first_fail_dir,
                            stopped_reason=stopped_reason,
                            squeeze_optimizer=args.squeeze_optimizer,
                        )
                        break

                if recommended_diff or reconcile_apply:
                    if reconcile_apply and not recommended_diff:
                        print(
                            f"[squeeze] Reconciling managed YAML to cluster and running "
                            f"iteration {current_iteration}..."
                        )
                    else:
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
                            allow_empty_diff=reconcile_apply,
                        )
                elif recovery_probe_applied or probe_applied:
                    if recovery_probe_applied:
                        print(
                            f"[squeeze] After recovery UP probe synthetic apply, running iteration {current_iteration}..."
                        )
                    else:
                        print(
                            f"[squeeze] After violation-probe DOWN, running iteration {current_iteration}..."
                        )
                _squeeze_preflight_before_k6(
                    mode=mode,
                    profile=args.profile,
                    base_url=base_url,
                    k8s_apply_enabled=k8s_apply_enabled,
                    deployment_yaml=deployment_yaml,
                    hpa_yaml=hpa_yaml,
                    k8s_namespace=k8s_namespace,
                    k8s_deployment=k8s_deployment,
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
                    squeeze_optimizer=args.squeeze_optimizer,
                )
                if next_run_dir is None:
                    stopped_reason = "next_run_missing"
                    _write_squeeze_summary(
                        squeeze_rows,
                        run_root=run_root,
                        best_pass_dir=best_pass_dir,
                        first_fail_dir=first_fail_dir,
                        stopped_reason=stopped_reason,
                        squeeze_optimizer=args.squeeze_optimizer,
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
                    if (
                        not up_recovery_active
                        and current_iteration > 1
                    ):
                        prev_exp_path = (
                            run_root / f"iteration-{current_iteration - 1}" / "experiment.json"
                        )
                        if prev_exp_path.exists():
                            try:
                                prev_exp = json.loads(prev_exp_path.read_text())
                                effective_stall = (
                                    _squeeze_effective_progress_key(exp)
                                    == _squeeze_effective_progress_key(prev_exp)
                                )
                                if effective_stall:
                                    dep_path = REPO_ROOT / deployment_yaml
                                    hpa_path = REPO_ROOT / hpa_yaml
                                    recovered = False
                                    if (
                                        squeeze_kubectl
                                        and k8s_apply_enabled
                                        and squeeze_yaml_live_replica_drift(
                                            dep_path,
                                            deployment_name=k8s_deployment,
                                            namespace=k8s_namespace,
                                        )
                                    ):
                                        print(
                                            f"[squeeze] Iteration {current_iteration}: "
                                            "effective stall with yaml/live replica drift; "
                                            "re-waiting and re-running k6...",
                                            flush=True,
                                        )
                                        ensure_squeeze_cluster_ready_before_k6(
                                            deployment_yaml_path=dep_path,
                                            hpa_yaml_path=hpa_path,
                                            deployment_name=k8s_deployment,
                                            namespace=k8s_namespace,
                                        )
                                        retry_dir = _run_once(
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
                                            squeeze_optimizer=args.squeeze_optimizer,
                                        )
                                        if retry_dir is not None:
                                            retry_status, retry_exp = (
                                                _read_experiment_status(retry_dir)
                                            )
                                            squeeze_rows[-1] = _squeeze_row(
                                                retry_dir, retry_exp, retry_status
                                            )
                                            anchor_run_dir = retry_dir
                                            status, exp = retry_status, retry_exp
                                            if status == "PASS":
                                                best_pass_dir = retry_dir
                                            recovered = (
                                                _squeeze_effective_progress_key(exp)
                                                != _squeeze_effective_progress_key(prev_exp)
                                            )
                                    if (
                                        not recovered
                                        and squeeze_kubectl
                                        and k8s_apply_enabled
                                        and apply_squeeze_stall_resource_step(
                                            deployment_yaml_path=dep_path,
                                            hpa_yaml_path=hpa_path,
                                            deployment_name=k8s_deployment,
                                            namespace=k8s_namespace,
                                            repo_root=REPO_ROOT,
                                        )
                                    ):
                                        print(
                                            f"[squeeze] Iteration {current_iteration}: "
                                            "effective stall; applied resource-only recovery "
                                            "before next iteration.",
                                            flush=True,
                                        )
                                        recovered = True
                                    if not recovered:
                                        stopped_reason = "no_effective_progress"
                                        print(
                                            f"[squeeze] Iteration {current_iteration}: "
                                            "no effective DOWN progress vs previous PASS "
                                            "(live replicas + cost unchanged); stopping.",
                                            flush=True,
                                        )
                                        _write_squeeze_summary(
                                            squeeze_rows,
                                            run_root=run_root,
                                            best_pass_dir=best_pass_dir,
                                            first_fail_dir=first_fail_dir,
                                            stopped_reason=stopped_reason,
                                            squeeze_optimizer=args.squeeze_optimizer,
                                        )
                                        break
                            except json.JSONDecodeError:
                                pass
                    if up_recovery_active:
                        stopped_reason = "recovered_from_underprovisioning"
                        _write_squeeze_summary(
                            squeeze_rows,
                            run_root=run_root,
                            best_pass_dir=best_pass_dir,
                            first_fail_dir=first_fail_dir,
                            stopped_reason=stopped_reason,
                            squeeze_optimizer=args.squeeze_optimizer,
                        )
                        print("[squeeze] Recovery complete after UP movement; stopping.")
                        break
                else:
                    if not up_recovery_active:
                        first_fail_dir = next_run_dir
                        stopped_reason = "first_fail"
                        print(
                            f"[squeeze] Iteration {current_iteration} FAIL, "
                            f"cost={((exp.get('cost') or {}).get('cost_score'))}; stopping."
                        )
                    else:
                        print(
                            f"[squeeze] Iteration {current_iteration} still FAIL, "
                            f"cost={((exp.get('cost') or {}).get('cost_score'))}, "
                            "in recovery mode; continuing."
                        )
                _write_squeeze_summary(
                    squeeze_rows,
                    run_root=run_root,
                    best_pass_dir=best_pass_dir,
                    first_fail_dir=first_fail_dir,
                    stopped_reason=stopped_reason,
                    squeeze_optimizer=args.squeeze_optimizer,
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
                    squeeze_optimizer=args.squeeze_optimizer,
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
                    squeeze_optimizer=args.squeeze_optimizer,
                )

            if best_pass_dir:
                print(f"[squeeze] Optimal frontier (last PASS): {best_pass_dir}")
            if first_fail_dir:
                print(f"[squeeze] First FAIL: {first_fail_dir}")
            if (
                args.squeeze_optimizer == "formula"
                and args.squeeze_final_report_llm
                and run_root.exists()
            ):
                try:
                    from analysis.squeeze_final_report import write_formula_final_report

                    out = write_formula_final_report(run_root)
                    if out:
                        print(f"[squeeze] formula final LLM summary: {out}")
                except Exception as e:
                    print(f"[squeeze] formula final LLM summary failed: {e}")
    finally:
        for proc in port_forwards:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except Exception:
                pass
