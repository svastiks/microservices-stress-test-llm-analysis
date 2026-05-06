"""
Query Prometheus over a time window and return observed metrics for experiment JSON.
Fills replicas, cpu_util_pct, mem_util_pct, oom_kills, cpu_util_to_limit, and telemetry.*.
"""
from typing import Any

import requests

DEFAULT_PROMETHEUS_URL = "http://localhost:9090"

# Pad the k6 window so short runs still overlap Prometheus scrapes.
_TIME_PAD_S = 45.0


def _log(msg: str) -> None:
    print(f"[prom] {msg}")


def _prom_api_candidates(base_url: str) -> list[str]:
    """Return Prometheus API base candidates, handling /prometheus prefix setups."""
    base = base_url.rstrip("/")
    if base.endswith("/prometheus"):
        return [f"{base}/api/v1"]
    return [f"{base}/api/v1", f"{base}/prometheus/api/v1"]


def _query(
    base_url: str,
    query: str,
    time_ts: float | None = None,
    timeout: float = 10.0,
) -> list[dict]:
    params: dict[str, Any] = {"query": query}
    if time_ts is not None:
        params["time"] = time_ts
    for api_base in _prom_api_candidates(base_url):
        try:
            r = requests.get(
                f"{api_base}/query",
                params=params,
                timeout=timeout,
            )
            r.raise_for_status()
            data = r.json()
            if data.get("status") != "success":
                continue
            return (data.get("data", {}) or {}).get("result", []) or []
        except Exception:
            continue
    return []


def _query_range(
    base_url: str,
    query: str,
    start: float,
    end: float,
    step: str = "30s",
    timeout: float = 20.0,
) -> list[dict]:
    for api_base in _prom_api_candidates(base_url):
        try:
            r = requests.get(
                f"{api_base}/query_range",
                params={"query": query, "start": start, "end": end, "step": step},
                timeout=timeout,
            )
            r.raise_for_status()
            data = r.json()
            if data.get("status") != "success":
                continue
            return (data.get("data", {}) or {}).get("result", []) or []
        except Exception:
            continue
    return []


def _last_value(results: list[dict]) -> float:
    if not results:
        return 0.0
    r = results[0]
    vals = r.get("values") or r.get("value")
    if vals is None:
        return 0.0
    if isinstance(vals, list) and vals and isinstance(vals[0], (list, tuple)):
        return float(vals[-1][1])
    if isinstance(vals, (list, tuple)) and len(vals) >= 2:
        return float(vals[1])
    return 0.0


def _max_value(results: list[dict]) -> float:
    if not results:
        return 0.0
    out = 0.0
    for r in results:
        vals = r.get("values") or []
        for pair in vals:
            if isinstance(pair, (list, tuple)) and len(pair) >= 2:
                out = max(out, float(pair[1]))
    return out


def _sum_series_maxima(results: list[dict]) -> float:
    if not results:
        return 0.0
    total = 0.0
    for r in results:
        vals = r.get("values") or []
        series_max = 0.0
        for pair in vals:
            if isinstance(pair, (list, tuple)) and len(pair) >= 2:
                series_max = max(series_max, float(pair[1]))
        total += series_max
    return total


def _range_step(start: float, end: float) -> str:
    return "15s" if (end - start) < 150 else "30s"


def _cadvisor_pod_selector(namespace: str, deployment_name: str) -> str:
    return (
        f'namespace="{namespace}",pod=~"{deployment_name}.+",'
        f'container!="",container!="POD",image!=""'
    )


def _first_non_empty_range(
    base_url: str, queries: list[str], start: float, end: float, step: str
) -> tuple[list[dict], int]:
    """Try queries in order; return first non-empty result and attempt count."""
    attempts = 0
    for q in queries:
        attempts += 1
        out = _query_range(base_url, q, start, end, step=step)
        if out:
            return out, attempts
    return [], attempts


def get_prometheus_observed(
    start_ts: float,
    end_ts: float,
    namespace: str = "default",
    deployment_name: str = "stress-service",
    prometheus_url: str = DEFAULT_PROMETHEUS_URL,
    cpu_limit_m: int = 500,
    mem_limit_mib: int = 256,
    deployment_replicas: int = 0,
    hpa_min_replicas: int = 0,
    time_pad_s: float = _TIME_PAD_S,
) -> dict:
    """
    Query Prometheus over an expanded window around [start_ts, end_ts].
    When replica series are empty but YAML declares replicas, use config fallback for denominators only.
    """
    observed: dict[str, Any] = {
        "replicas": 0,
        "replicas_max": 0,
        "cpu_util_pct": 0.0,
        "mem_util_pct": 0.0,
        "oom_kills": 0,
        "cpu_util_to_limit": 0.0,
    }

    q_start = float(start_ts) - time_pad_s
    q_end = float(end_ts) + time_pad_s
    step = _range_step(q_start, q_end)
    hpa_name = f"{deployment_name}-hpa"
    _log(
        f"collect_start namespace={namespace} deployment={deployment_name} "
        f"window=({q_start:.3f},{q_end:.3f}) step={step}"
    )

    repl_avail_q = (
        f"kube_deployment_status_replicas_available{{"
        f'deployment="{deployment_name}",namespace="{namespace}"}}'
    )
    repl_spec_q = (
        f"kube_deployment_spec_replicas{{"
        f'deployment="{deployment_name}",namespace="{namespace}"}}'
    )
    repl_hpa_q = (
        f"kube_horizontalpodautoscaler_status_current_replicas{{"
        f'horizontalpodautoscaler="{hpa_name}",namespace="{namespace}"}}'
    )

    repl_avail_r = _query_range(prometheus_url, repl_avail_q, q_start, q_end, step=step)
    repl_spec_r = _query_range(prometheus_url, repl_spec_q, q_start, q_end, step=step)
    repl_hpa_r = _query_range(prometheus_url, repl_hpa_q, q_start, q_end, step=step)

    max_avail = int(_max_value(repl_avail_r))
    max_spec = int(_max_value(repl_spec_r))
    max_hpa = int(_max_value(repl_hpa_r))
    max_from_prom = max(max_avail, max_spec, max_hpa)

    replicas_series_matched = bool(repl_avail_r or repl_spec_r or repl_hpa_r)

    yaml_floor = max(int(deployment_replicas or 0), int(hpa_min_replicas or 0), 1)
    if max_from_prom > 0:
        max_replicas = max_from_prom
        replicas_inferred = False
    else:
        max_replicas = yaml_floor
        replicas_inferred = True

    observed["replicas"] = max_replicas
    observed["replicas_max"] = max_replicas

    cadv = _cadvisor_pod_selector(namespace, deployment_name)
    cpu_queries = [
        # kubelet/cadvisor explicit labels (matches many kube-prometheus setups)
        f'sum(rate(container_cpu_usage_seconds_total{{job="kubelet",metrics_path="/metrics/cadvisor",{cadv}}}[1m]))',
        # same but without image label constraint
        f'sum(rate(container_cpu_usage_seconds_total{{job="kubelet",metrics_path="/metrics/cadvisor",namespace="{namespace}",pod=~"{deployment_name}.+",container!="",container!="POD"}}[1m]))',
        # Preferred strict selector
        f"sum(rate(container_cpu_usage_seconds_total{{{cadv}}}[1m]))",
        # Fallback when image label is absent in exporter payload
        f'sum(rate(container_cpu_usage_seconds_total{{namespace="{namespace}",pod=~"{deployment_name}.+",container!="",container!="POD"}}[1m]))',
        # Final fallback: pod-only selector
        f'sum(rate(container_cpu_usage_seconds_total{{namespace="{namespace}",pod=~"{deployment_name}.+"}}[1m]))',
        # Older scrape label variants
        f'sum(rate(container_cpu_usage_seconds_total{{namespace="{namespace}",pod_name=~"{deployment_name}.+",container_name!=""}}[1m]))',
    ]
    cpu_results, cpu_query_attempts = _first_non_empty_range(
        prometheus_url, cpu_queries, q_start, q_end, step
    )
    cpu_usage_cores = _max_value(cpu_results)
    cpu_collection_mode = "aggregate_query"
    if not cpu_results:
        cpu_per_pod_queries = [
            f'rate(container_cpu_usage_seconds_total{{job="kubelet",metrics_path="/metrics/cadvisor",{cadv}}}[1m])',
            f'rate(container_cpu_usage_seconds_total{{namespace="{namespace}",pod=~"{deployment_name}.+",container!="",container!="POD"}}[1m])',
            f'rate(container_cpu_usage_seconds_total{{namespace="{namespace}",pod_name=~"{deployment_name}.+",container_name!=""}}[1m])',
        ]
        cpu_per_pod_results, cpu_per_pod_attempts = _first_non_empty_range(
            prometheus_url, cpu_per_pod_queries, q_start, q_end, step
        )
        cpu_query_attempts += cpu_per_pod_attempts
        if cpu_per_pod_results:
            cpu_usage_cores = _sum_series_maxima(cpu_per_pod_results)
            cpu_results = cpu_per_pod_results
            cpu_collection_mode = "per_pod_series_sum"

    mem_queries = [
        # kubelet/cadvisor explicit labels (matches many kube-prometheus setups)
        f'sum(container_memory_working_set_bytes{{job="kubelet",metrics_path="/metrics/cadvisor",{cadv}}})',
        # same but without image label constraint
        f'sum(container_memory_working_set_bytes{{job="kubelet",metrics_path="/metrics/cadvisor",namespace="{namespace}",pod=~"{deployment_name}.+",container!="",container!="POD"}})',
        f"sum(container_memory_working_set_bytes{{{cadv}}})",
        f'sum(container_memory_working_set_bytes{{namespace="{namespace}",pod=~"{deployment_name}.+",container!="",container!="POD"}})',
        f'sum(container_memory_working_set_bytes{{namespace="{namespace}",pod=~"{deployment_name}.+"}})',
        # Older scrape label variants
        f'sum(container_memory_working_set_bytes{{namespace="{namespace}",pod_name=~"{deployment_name}.+",container_name!=""}})',
    ]
    mem_results, mem_query_attempts = _first_non_empty_range(
        prometheus_url, mem_queries, q_start, q_end, step
    )
    mem_bytes = _max_value(mem_results)
    mem_collection_mode = "aggregate_query"
    if not mem_results:
        mem_per_pod_queries = [
            f'container_memory_working_set_bytes{{job="kubelet",metrics_path="/metrics/cadvisor",{cadv}}}',
            f'container_memory_working_set_bytes{{namespace="{namespace}",pod=~"{deployment_name}.+",container!="",container!="POD"}}',
            f'container_memory_working_set_bytes{{namespace="{namespace}",pod_name=~"{deployment_name}.+",container_name!=""}}',
        ]
        mem_per_pod_results, mem_per_pod_attempts = _first_non_empty_range(
            prometheus_url, mem_per_pod_queries, q_start, q_end, step
        )
        mem_query_attempts += mem_per_pod_attempts
        if mem_per_pod_results:
            mem_bytes = _sum_series_maxima(mem_per_pod_results)
            mem_results = mem_per_pod_results
            mem_collection_mode = "per_pod_series_sum"

    denom_replicas = max(max_replicas, 1)

    if cpu_limit_m > 0:
        total_cpu_limit_cores = (cpu_limit_m / 1000.0) * denom_replicas
        if total_cpu_limit_cores > 0:
            observed["cpu_util_pct"] = round(
                100 * cpu_usage_cores / total_cpu_limit_cores, 1
            )
            observed["cpu_util_to_limit"] = round(
                cpu_usage_cores / total_cpu_limit_cores, 2
            )

    if mem_limit_mib > 0:
        total_mem_limit_bytes = mem_limit_mib * 1024 * 1024 * denom_replicas
        if total_mem_limit_bytes > 0:
            observed["mem_util_pct"] = round(
                100 * mem_bytes / total_mem_limit_bytes, 1
            )

    oom_q = (
        f"sum(kube_pod_container_status_last_terminated_reason{{"
        f'namespace="{namespace}",reason="OOMKilled",pod=~"{deployment_name}.+"}})'
    )
    oom_results = _query(prometheus_url, oom_q, time_ts=end_ts)
    observed["oom_kills"] = int(_last_value(oom_results))

    cpu_series_matched = bool(cpu_results)
    mem_series_matched = bool(mem_results)
    utilization_trustworthy = bool(
        cpu_series_matched
        and mem_series_matched
        and (replicas_series_matched or replicas_inferred)
    )

    observed["telemetry"] = {
        "window_start_ts": q_start,
        "window_end_ts": q_end,
        "replicas_series_matched": replicas_series_matched,
        "replicas_inferred_from_config": replicas_inferred,
        "cpu_series_matched": cpu_series_matched,
        "mem_series_matched": mem_series_matched,
        "cpu_query_attempts": cpu_query_attempts,
        "mem_query_attempts": mem_query_attempts,
        "cpu_collection_mode": cpu_collection_mode,
        "mem_collection_mode": mem_collection_mode,
        "utilization_trustworthy": utilization_trustworthy,
    }
    _log(
        f"collect_done cpu_util_pct={observed.get('cpu_util_pct')} "
        f"mem_util_pct={observed.get('mem_util_pct')} "
        f"cpu_series_matched={cpu_series_matched} mem_series_matched={mem_series_matched} "
        f"cpu_attempts={cpu_query_attempts} mem_attempts={mem_query_attempts} "
        f"cpu_mode={cpu_collection_mode} mem_mode={mem_collection_mode}"
    )

    return observed
