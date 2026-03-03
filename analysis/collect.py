"""
Build combined experiment JSON from k6 summary + optional Kubernetes.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _parse_cpu(s: str) -> int:
    """Parse Kubernetes CPU (e.g. '100m', '1') to millicores."""
    if not s:
        return 0
    s = s.strip()
    if s.endswith("m"):
        return int(s[:-1])
    return int(float(s) * 1000)


def _parse_memory_mib(s: str) -> int:
    """Parse Kubernetes memory to MiB."""
    if not s:
        return 0
    s = s.strip()
    if s.endswith("Mi"):
        return int(s[:-2])
    if s.endswith("Gi"):
        return int(s[:-2]) * 1024
    if s.endswith("Ki"):
        return int(s[:-2]) // 1024
    return int(s)  # assume bytes, rough


def _k8s_get(*args: str) -> dict | None:
    try:
        out = subprocess.run(
            ["kubectl", "get", *args, "-o", "json"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=REPO_ROOT,
        )
        if out.returncode != 0:
            return None
        return json.loads(out.stdout)
    except (FileNotFoundError, json.JSONDecodeError, subprocess.TimeoutExpired):
        return None


def get_k8s_config(service_name: str) -> dict:
    """Read deployment and HPA for service_name. Returns config block."""
    dep = _k8s_get("deployment", service_name) if service_name else None
    hpa = (_k8s_get("hpa", f"{service_name}-hpa") or _k8s_get("hpa", service_name)) if service_name else None

    config = {
        "cpu_request_m": 0,
        "cpu_limit_m": 0,
        "mem_request_mib": 0,
        "mem_limit_mib": 0,
        "hpa": {"min_replicas": 0, "max_replicas": 0, "target_cpu_util_pct": 0},
    }
    if dep and dep.get("spec", {}).get("template", {}).get("spec", {}).get("containers"):
        c = dep["spec"]["template"]["spec"]["containers"][0]
        r = c.get("resources", {}) or {}
        req = r.get("requests", {}) or {}
        lim = r.get("limits", {}) or {}
        config["cpu_request_m"] = _parse_cpu(req.get("cpu", ""))
        config["cpu_limit_m"] = _parse_cpu(lim.get("cpu", ""))
        config["mem_request_mib"] = _parse_memory_mib(req.get("memory", ""))
        config["mem_limit_mib"] = _parse_memory_mib(lim.get("memory", ""))
    if hpa and hpa.get("spec"):
        config["hpa"]["min_replicas"] = hpa["spec"].get("minReplicas") or 0
        config["hpa"]["max_replicas"] = hpa["spec"].get("maxReplicas") or 0
        for m in hpa["spec"].get("metrics", []) or []:
            if m.get("resource", {}).get("name") == "cpu":
                config["hpa"]["target_cpu_util_pct"] = m.get("resource", {}).get("target", {}).get("averageUtilization") or 0
                break
    return config


def get_replica_count(service_name: str) -> int:
    """Current number of Running pods for the service (for pre-test snapshot)."""
    label = f"app={service_name}"
    pods = _k8s_get("pods", "-l", label) if service_name else None
    if not pods or not pods.get("items"):
        return 0
    return len([p for p in pods["items"] if p.get("status", {}).get("phase") == "Running"])


def poll_k8s_sample(service_name: str) -> dict:
    """Single poll: replicas (Running count), cpu_m (total millicores), mem_mib (total MiB). For live polling during test."""
    out = {"replicas": 0, "cpu_m": 0, "mem_mib": 0}
    label = f"app={service_name}"
    pods = _k8s_get("pods", "-l", label) if service_name else None
    if pods and pods.get("items"):
        out["replicas"] = len([p for p in pods["items"] if p.get("status", {}).get("phase") == "Running"])
    try:
        result = subprocess.run(
            ["kubectl", "top", "pods", "-l", label, "--no-headers"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=REPO_ROOT,
        )
        if result.returncode == 0 and result.stdout.strip():
            for line in result.stdout.strip().split("\n"):
                parts = line.split()
                if len(parts) >= 3:
                    out["cpu_m"] += _parse_cpu(parts[1])
                    raw = parts[2]
                    if "Mi" in raw:
                        out["mem_mib"] += int(raw.replace("Mi", ""))
                    elif "Ki" in raw:
                        out["mem_mib"] += int(raw.replace("Ki", "")) // 1024
    except (FileNotFoundError, ValueError, subprocess.TimeoutExpired):
        pass
    return out


def get_k8s_observed(service_name: str, label: str | None) -> dict:
    """Replicas, OOM count from get pods; CPU/mem from kubectl top (if metrics-server)."""
    label = label or f"app={service_name}"
    observed = {
        "replicas": 0,
        "cpu_util_pct": 0.0,
        "mem_util_pct": 0.0,
        "oom_kills": 0,
        "cpu_util_to_limit": 0.0,
    }
    pods = _k8s_get("pods", "-l", label) if service_name else None
    if pods and pods.get("items"):
        observed["replicas"] = len([p for p in pods["items"] if p.get("status", {}).get("phase") == "Running"])
        oom = 0
        for p in pods["items"]:
            for c in p.get("status", {}).get("containerStatuses", []) or []:
                if (c.get("lastState", {}) or {}).get("terminated", {}).get("reason") == "OOMKilled":
                    oom += 1
        observed["oom_kills"] = oom

    top = None
    try:
        out = subprocess.run(
            ["kubectl", "top", "pods", "-l", label, "--no-headers"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=REPO_ROOT,
        )
        if out.returncode == 0 and out.stdout.strip():
            total_cpu_m = 0
            total_mem_mib = 0
            for line in out.stdout.strip().split("\n"):
                parts = line.split()
                if len(parts) >= 3:
                    total_cpu_m += _parse_cpu(parts[1])
                    raw = parts[2]
                    if "Mi" in raw:
                        total_mem_mib += int(raw.replace("Mi", ""))
                    elif "Ki" in raw:
                        total_mem_mib += int(raw.replace("Ki", "")) // 1024
            top = {"cpu_m": total_cpu_m, "mem_mib": total_mem_mib}
    except (FileNotFoundError, ValueError, subprocess.TimeoutExpired):
        pass
    if top and observed["replicas"]:
        dep = _k8s_get("deployment", service_name) if service_name else None
        if dep and dep.get("spec", {}).get("template", {}).get("spec", {}).get("containers"):
            c = dep["spec"]["template"]["spec"]["containers"][0]
            r = c.get("resources", {}) or {}
            lim = r.get("limits", {}) or {}
            cpu_lim_m = _parse_cpu(lim.get("cpu", ""))
            mem_lim_mib = _parse_memory_mib(lim.get("memory", ""))
            if cpu_lim_m and observed["replicas"]:
                total_limit_m = cpu_lim_m * observed["replicas"]
                observed["cpu_util_pct"] = round(100 * top["cpu_m"] / total_limit_m, 1) if total_limit_m else 0
                observed["cpu_util_to_limit"] = round(top["cpu_m"] / total_limit_m, 2) if total_limit_m else 0
            if mem_lim_mib and observed["replicas"]:
                total_mem_limit = mem_lim_mib * observed["replicas"]
                observed["mem_util_pct"] = round(100 * top.get("mem_mib", 0) / total_mem_limit, 1) if total_mem_limit else 0
    return observed


def get_raw_k8s_snapshot(service_name: str) -> dict:
    """Raw k8s API / kubectl top output for audit. Returns dict with deployment, hpa, pods (JSON), top_stdout (str)."""
    label = f"app={service_name}"
    dep = _k8s_get("deployment", service_name) if service_name else None
    hpa = (_k8s_get("hpa", f"{service_name}-hpa") or _k8s_get("hpa", service_name)) if service_name else None
    pods = _k8s_get("pods", "-l", label) if service_name else None
    top_stdout = ""
    try:
        out = subprocess.run(
            ["kubectl", "top", "pods", "-l", label, "--no-headers"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=REPO_ROOT,
        )
        if out.returncode == 0:
            top_stdout = out.stdout or ""
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return {
        "deployment": dep,
        "hpa": hpa,
        "pods": pods,
        "top_stdout": top_stdout,
    }


def _provenance_lines(service_name: str, use_k8s: bool) -> list[str]:
    """Lines for sources.txt describing where each experiment field comes from."""
    lines = [
        "# Experiment JSON field sources (audit)",
        "experiment_id, service, endpoint <- experiment.config.json",
        "config <- experiment.config.json (if K8S=0); kubectl get deployment + kubectl get hpa (if K8S=1)",
        "workload, slo <- experiment.config.json",
        "observed.total_requests, observed_duration_s, achieved_requests_per_second <- k6-run-summary.json (metrics.http_reqs, rate)",
        "observed.latency_ms.p95, p99 <- k6-run-summary.json metrics.http_req_duration",
        "observed.error_rate <- k6-run-summary.json metrics.http_req_failed.value",
        "failure.failed, failure.reason <- derived from k6 thresholds vs SLO in from_k6_summary()",
    ]
    if use_k8s and service_name:
        lines.extend([
            "observed.replicas_at_start <- captured before k6 (replicas_at_start.txt), to see if HPA scaled during test",
            "observed.scaled_during_test <- true if replicas > replicas_at_start (for reports/JSON)",
            f"observed.replicas, oom_kills <- kubectl get pods -l app={service_name} (post-test snapshot); or from k8s-timeseries.json (max during test) if present",
            f"observed.cpu_util_pct, mem_util_pct <- kubectl top (snapshot); or avg from k8s-timeseries.json if present",
        ])
    return lines


def from_k6_summary(summary: dict, slo: dict | None = None) -> tuple[dict, dict]:
    """Build observed and failure from k6 summary. slo: { p95_latency_ms, error_rate }."""
    slo = slo or {}
    p95_limit = slo.get("p95_latency_ms") or 2000
    error_limit = slo.get("error_rate") or 0.05
    m = summary.get("metrics", {}) or {}
    hr = m.get("http_reqs", {}) or {}
    hrd = m.get("http_req_duration", {}) or {}
    hrf = m.get("http_req_failed", {}) or {}
    count = int(hr.get("count", 0))
    rate = float(hr.get("rate", 0))
    duration_s = count / rate if rate else 0

    # error_rate: use http_req_failed.value (fraction of failed requests), not passes/fails (threshold samples)
    err_val = float(hrf.get("value", 0) or 0)
    observed = {
        "total_requests": count,
        "observed_duration_s": round(duration_s, 1),
        "achieved_requests_per_second": round(rate, 1),
        "latency_ms": {
            "p95": round(hrd.get("p(95)", 0), 0),
            "p99": round(hrd.get("p(99)", 0), 0),
        },
        "error_rate": round(err_val, 4),
    }

    failure = {"failed": False, "reason": ""}
    p95_actual = observed["latency_ms"]["p95"]
    if p95_actual > p95_limit:
        failure["failed"] = True
        failure["reason"] = "p95_slo_violation"
    elif observed["error_rate"] > error_limit:
        failure["failed"] = True
        failure["reason"] = "error_rate_slo_violation"
    return observed, failure


def build_payload(
    run_dir: Path,
    config_path: Path,
    service_name: str,
    use_k8s: bool,
) -> dict:
    k6_path = run_dir / "k6-run-summary.json"
    if not k6_path.exists():
        raise FileNotFoundError(f"No k6 summary at {k6_path}")
    with open(k6_path) as f:
        summary = json.load(f)
    with open(config_path) as f:
        exp = json.load(f)

    observed_k6, failure = from_k6_summary(summary, exp.get("slo"))
    payload = {
        "experiment_id": exp.get("experiment_id", "run-1"),
        "service": exp.get("service", service_name),
        "endpoint": exp.get("endpoint", "POST /login"),
        "config": exp.get("config", {}),
        "workload": exp.get("workload", {}),
        "slo": exp.get("slo", {}),
        "observed": observed_k6,
        "failure": failure,
    }
    if use_k8s and service_name:
        payload["config"] = get_k8s_config(service_name)
        k8s_obs = get_k8s_observed(service_name, None)
        payload["observed"].update(k8s_obs)
    # replicas_at_start: captured before k6 so we can see if HPA scaled during the test
    replicas_at_start_path = run_dir.parent / "replicas_at_start.txt"
    if replicas_at_start_path.exists():
        try:
            payload["observed"]["replicas_at_start"] = int(replicas_at_start_path.read_text().strip())
        except (ValueError, OSError):
            pass
        try:
            replicas_at_start_path.unlink()
        except OSError:
            pass
    obs = payload["observed"]
    # If we have live-polled timeseries, use it for replicas and cpu/mem (more accurate than single snapshot)
    ts_path = run_dir / "k8s-timeseries.json"
    if ts_path.exists():
        try:
            with open(ts_path) as f:
                timeseries = json.load(f)
            if isinstance(timeseries, list) and timeseries:
                config = payload["config"]
                cpu_lim = config.get("cpu_limit_m") or 1
                mem_lim = config.get("mem_limit_mib") or 1
                max_replicas = max(s.get("replicas", 0) for s in timeseries)
                obs["replicas"] = max_replicas
                obs["replicas_at_end"] = timeseries[-1].get("replicas", 0)
                cpu_pcts = []
                mem_pcts = []
                for s in timeseries:
                    r = s.get("replicas", 0) or 1
                    if r > 0 and cpu_lim:
                        cpu_pcts.append(100 * (s.get("cpu_m") or 0) / (cpu_lim * r))
                    if r > 0 and mem_lim:
                        mem_pcts.append(100 * (s.get("mem_mib") or 0) / (mem_lim * r))
                if cpu_pcts:
                    obs["cpu_util_pct"] = round(sum(cpu_pcts) / len(cpu_pcts), 1)
                    obs["cpu_util_to_limit"] = round(sum(cpu_pcts) / len(cpu_pcts) / 100, 2)
                if mem_pcts:
                    obs["mem_util_pct"] = round(sum(mem_pcts) / len(mem_pcts), 1)
        except (json.JSONDecodeError, OSError):
            pass
    # Explicit scaling flag: did HPA scale during the test?
    if "replicas_at_start" in obs and "replicas" in obs:
        obs["scaled_during_test"] = obs["replicas"] > obs["replicas_at_start"]
    # Always write k8s snapshot when we have a service name (for audit); empty/null if no cluster or kubectl fails
    if service_name:
        raw = get_raw_k8s_snapshot(service_name)
        (run_dir / "k8s-snapshot.json").write_text(json.dumps(raw, indent=2))
    (run_dir / "sources.txt").write_text("\n".join(_provenance_lines(service_name, use_k8s)))
    return payload


def main():
    p = argparse.ArgumentParser(description="Combine k6 + K8s into experiment JSON")
    p.add_argument("--run-dir", type=Path, default=None, help="e.g. results/2026-02-25-5")
    p.add_argument("--config", type=Path, default=REPO_ROOT / "experiment.config.json")
    p.add_argument("--service", default="stress-service")
    p.add_argument("--k8s", action="store_true", help="Fetch deployment/HPA and pod metrics")
    p.add_argument("--out", type=Path, default=None, help="Write JSON here; default stdout")
    args = p.parse_args()
    if args.run_dir is None:
        # Latest run dir under results/
        results = REPO_ROOT / "results"
        dirs = sorted(results.glob("*-*"), key=lambda d: d.stat().st_mtime, reverse=True)
        args.run_dir = dirs[0] if dirs else results / "run"
    if not args.config.exists():
        print("experiment.config.json not found; use --config", file=sys.stderr)
        sys.exit(1)
    payload = build_payload(args.run_dir, args.config, args.service, args.k8s)
    out = args.out or (args.run_dir / "experiment.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        json.dump(payload, f, indent=2)
    if args.out is None:
        print(f"Wrote {out}")


if __name__ == "__main__":
    main()
