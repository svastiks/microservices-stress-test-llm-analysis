"""
Build combined experiment JSON from k6 summary + config from YAML + optional Prometheus observed.
"""
import json
from pathlib import Path
from typing import Any
from datetime import datetime, timezone

import yaml
import uuid

REPO_ROOT = Path(__file__).resolve().parent.parent


def _parse_cpu(s: str) -> int:
    """Parse Kubernetes CPU (e.g. '100m', '1') to millicores."""
    if not s:
        return 0
    s = str(s).strip()
    if s.endswith("m"):
        return int(s[:-1])
    return int(float(s) * 1000)


def _parse_memory_mib(s: str) -> int:
    """Parse Kubernetes memory to MiB."""
    if not s:
        return 0
    s = str(s).strip()
    if s.endswith("Mi"):
        return int(s[:-2])
    if s.endswith("Gi"):
        return int(s[:-2]) * 1024
    if s.endswith("Ki"):
        return int(s[:-2]) // 1024
    return int(s)  # assume bytes, rough


def get_config_from_yaml(deployment_path: Path, hpa_path: Path) -> dict:
    """Read deployment and HPA YAML files and return config block for experiment JSON."""
    config = {
        "cpu_request_m": 0,
        "cpu_limit_m": 0,
        "mem_request_mib": 0,
        "mem_limit_mib": 0,
        "hpa": {"min_replicas": 0, "max_replicas": 0, "target_cpu_util_pct": 0},
    }
    if deployment_path.exists():
        with open(deployment_path) as f:
            docs = list(yaml.safe_load_all(f)) or []
        for doc in docs:
            if doc and doc.get("kind") == "Deployment":
                spec = doc.get("spec", {}) or {}
                template = spec.get("template", {}) or {}
                containers = (template.get("spec") or {}).get("containers") or []
                if containers:
                    c = containers[0]
                    r = c.get("resources", {}) or {}
                    req = r.get("requests", {}) or {}
                    lim = r.get("limits", {}) or {}
                    config["cpu_request_m"] = _parse_cpu(req.get("cpu", ""))
                    config["cpu_limit_m"] = _parse_cpu(lim.get("cpu", ""))
                    config["mem_request_mib"] = _parse_memory_mib(req.get("memory", ""))
                    config["mem_limit_mib"] = _parse_memory_mib(lim.get("memory", ""))
                break
    if hpa_path.exists():
        with open(hpa_path) as f:
            doc = yaml.safe_load(f)
        if doc and doc.get("kind") == "HorizontalPodAutoscaler":
            spec = doc.get("spec", {}) or {}
            config["hpa"]["min_replicas"] = spec.get("minReplicas") or 0
            config["hpa"]["max_replicas"] = spec.get("maxReplicas") or 0
            for m in spec.get("metrics", []) or []:
                if (m.get("resource") or {}).get("name") == "cpu":
                    config["hpa"]["target_cpu_util_pct"] = (
                        (m.get("resource") or {}).get("target") or {}
                    ).get("averageUtilization") or 0
                    break
    return config


def from_k6_summary(summary: dict, slo: dict | None = None) -> tuple[dict, dict]:
    """Build observed (k6 part) and failure from k6 summary. slo: { p95_latency_ms, error_rate }."""
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


def build_experiment_payload(
    run_dir: Path,
    k6_summary_path: Path,
    deployment_yaml_path: Path,
    hpa_yaml_path: Path,
    experiment_config: dict | None = None,
    observed_override: dict | None = None,
) -> dict:
    """
    Build full experiment JSON.
    experiment_config: optional { experiment_id, service, endpoint, workload, slo }.
    observed_override: optional runtime metrics from Prometheus (replicas, cpu_util_pct, mem_util_pct, oom_kills, cpu_util_to_limit, replicas_at_start, scaled_during_test).
    """
    if not k6_summary_path.exists():
        raise FileNotFoundError(f"No k6 summary at {k6_summary_path}")
    with open(k6_summary_path) as f:
        summary = json.load(f)

    exp = experiment_config or {}
    slo = exp.get("slo") or {}
    observed_k6, failure = from_k6_summary(summary, slo)
    if exp.get("k6_thresholds_crossed"):
        failure["failed"] = True
        failure["reason"] = failure.get("reason") or "k6_thresholds_crossed"

    config = get_config_from_yaml(deployment_yaml_path, hpa_yaml_path)
    if exp.get("config"):
        config = {**config, **exp["config"]}

    label = exp.get("experiment_id", "run")
    run_suffix = (
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        + "-"
        + uuid.uuid4().hex[:8]
    )

    payload: dict[str, Any] = {
        "experiment_id": f"{label}-{run_suffix}",
        "service": exp.get("service", "stress-service"),
        "endpoint": exp.get("endpoint", "POST /login"),
        "config": config,
        "workload": exp.get("workload", {}),
        "slo": exp.get("slo", {}),
        "observed": observed_k6,
        "failure": failure,
    }

    if observed_override:
        payload["observed"].update(observed_override)

    # replicas_at_start from file if present (captured before k6, at the start)
    replicas_at_start_path = run_dir / "replicas_at_start.txt"
    if replicas_at_start_path.exists():
        try:
            payload["observed"]["replicas_at_start"] = int(
                replicas_at_start_path.read_text().strip()
            )
            r = payload["observed"].get("replicas", 0)
            start = payload["observed"]["replicas_at_start"]
            payload["observed"]["scaled_during_test"] = r > start
        except (ValueError, OSError):
            pass

    return payload
