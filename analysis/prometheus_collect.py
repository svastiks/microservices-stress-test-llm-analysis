"""
Query Prometheus over a time window and return observed metrics for experiment JSON.
Used to fill replicas, cpu_util_pct, mem_util_pct, oom_kills, cpu_util_to_limit.
"""
import json
import time
from pathlib import Path
from typing import Any

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent

# Default: port-forward Prometheus to localhost
DEFAULT_PROMETHEUS_URL = "http://localhost:9090"


def _query(
    base_url: str,
    query: str,
    time_ts: float | None = None,
    timeout: float = 10.0,
) -> list[dict]:
    """Run instant query; return list of metric results."""
    params: dict[str, Any] = {"query": query}
    if time_ts is not None:
        params["time"] = time_ts
    try:
        r = requests.get(
            f"{base_url.rstrip('/')}/api/v1/query",
            params=params,
            timeout=timeout,
        )
        r.raise_for_status()
        data = r.json()
        if data.get("status") != "success":
            return []
        return (data.get("data", {}) or {}).get("result", []) or []
    except Exception:
        return []


def _query_range(
    base_url: str,
    query: str,
    start: float,
    end: float,
    step: str = "30s",
    timeout: float = 15.0,
) -> list[dict]:
    """Run range query; return list of results with 'values' (timestamp, value) pairs."""
    try:
        r = requests.get(
            f"{base_url.rstrip('/')}/api/v1/query_range",
            params={"query": query, "start": start, "end": end, "step": step},
            timeout=timeout,
        )
        r.raise_for_status()
        data = r.json()
        if data.get("status") != "success":
            return []
        return (data.get("data", {}) or {}).get("result", []) or []
    except Exception:
        return []


def _last_value(results: list[dict]) -> float:
    """Extract last value from range result or single value from instant result."""
    if not results:
        return 0.0
    r = results[0]
    vals = r.get("values") or r.get("value")
    if vals is None:
        return 0.0
    if isinstance(vals, list) and vals:
        return float(vals[-1][1])
    if isinstance(vals, (list, tuple)) and len(vals) >= 2:
        return float(vals[1])
    return 0.0


def _max_value(results: list[dict]) -> float:
    """Max over all values in range results."""
    if not results:
        return 0.0
    out = 0.0
    for r in results:
        vals = r.get("values") or []
        for pair in vals:
            if isinstance(pair, (list, tuple)) and len(pair) >= 2:
                out = max(out, float(pair[1]))
    return out


def get_prometheus_observed(
    start_ts: float,
    end_ts: float,
    namespace: str = "default",
    deployment_name: str = "stress-service",
    prometheus_url: str = DEFAULT_PROMETHEUS_URL,
    cpu_limit_m: int = 500,
    mem_limit_mib: int = 256,
) -> dict:
    """
    Query Prometheus over [start_ts, end_ts] and return observed dict for experiment JSON.
    Returns: replicas, cpu_util_pct, mem_util_pct, oom_kills, cpu_util_to_limit.
    Uses kube-state-metrics and cAdvisor metrics from kube-prometheus-stack.
    """
    observed = {
        "replicas": 0,
        "replicas_max": 0,
        "cpu_util_pct": 0.0,
        "mem_util_pct": 0.0,
        "oom_kills": 0,
        "cpu_util_to_limit": 0.0,
    }
    # Replicas: max over window (HPA current or deployment available)
    replicas_query = (
        f'kube_deployment_status_replicas_available{{deployment="{deployment_name}",namespace="{namespace}"}}'
    )
    repl_results = _query_range(prometheus_url, replicas_query, start_ts, end_ts)
    max_replicas = int(_max_value(repl_results))
    if max_replicas == 0:
        # Fallback: HPA current replicas
        hpa_query = f'kube_horizontalpodautoscaler_status_current_replicas{{horizontalpodautoscaler="{deployment_name}-hpa",namespace="{namespace}"}}'
        repl_results = _query_range(prometheus_url, hpa_query, start_ts, end_ts)
        max_replicas = int(_max_value(repl_results))
    observed["replicas"] = max_replicas
    observed["replicas_max"] = max_replicas

    # CPU: container_cpu_usage_seconds_total (rate) summed over deployment pods
    cpu_usage_query = (
        f'sum(rate(container_cpu_usage_seconds_total{{'
        f'namespace="{namespace}",pod=~"{deployment_name}.+",cpu="total"'
        f'}}[1m]))'
    )
    cpu_results = _query_range(prometheus_url, cpu_usage_query, start_ts, end_ts)
    cpu_usage_cores = _max_value(cpu_results)
    if max_replicas > 0 and cpu_limit_m > 0:
        total_cpu_limit_cores = (cpu_limit_m / 1000.0) * max_replicas
        if total_cpu_limit_cores > 0:
            observed["cpu_util_pct"] = round(
                100 * cpu_usage_cores / total_cpu_limit_cores, 1
            )
            observed["cpu_util_to_limit"] = round(
                cpu_usage_cores / total_cpu_limit_cores, 2
            )

    # Memory: container_memory_working_set_bytes
    mem_usage_query = (
        f'sum(container_memory_working_set_bytes{{'
        f'namespace="{namespace}",pod=~"{deployment_name}.+"'
        f'}})'
    )
    mem_results = _query_range(prometheus_url, mem_usage_query, start_ts, end_ts)
    mem_bytes = _max_value(mem_results)
    if max_replicas > 0 and mem_limit_mib > 0:
        total_mem_limit_bytes = mem_limit_mib * 1024 * 1024 * max_replicas
        if total_mem_limit_bytes > 0:
            observed["mem_util_pct"] = round(
                100 * mem_bytes / total_mem_limit_bytes, 1
            )

    # OOM: kube-state-metrics exposes gauge last_terminated_reason; sum at end_ts = containers that terminated with OOMKilled
    oom_query = f'sum(kube_pod_container_status_last_terminated_reason{{namespace="{namespace}",reason="OOMKilled"}})'
    oom_results = _query(prometheus_url, oom_query, time_ts=end_ts)
    observed["oom_kills"] = int(_last_value(oom_results))

    return observed
