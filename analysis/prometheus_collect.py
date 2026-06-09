"""
Query Prometheus over the k6 window and return observed metrics for experiment JSON.

Burn/cpu% use per-pod rate() summed over web pods (canonical). Requires >=12 samples
in the k6 window (5s step on 90s tests) before utilization_trustworthy.
"""
from typing import Any

import os

import requests

DEFAULT_PROMETHEUS_URL = "http://localhost:9090"

# Optional pad around [start_ts, end_ts]. Default 0: gate on k6 window only.
_TIME_PAD_S = 0.0


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


def _mean_value(results: list[dict]) -> float:
    if not results:
        return 0.0
    vals: list[float] = []
    for r in results:
        for pair in r.get("values") or []:
            if isinstance(pair, (list, tuple)) and len(pair) >= 2:
                vals.append(float(pair[1]))
    return sum(vals) / len(vals) if vals else 0.0


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


def _sum_series_means(results: list[dict]) -> float:
    if not results:
        return 0.0
    total = 0.0
    for r in results:
        vals = r.get("values") or []
        series_vals = [
            float(pair[1])
            for pair in vals
            if isinstance(pair, (list, tuple)) and len(pair) >= 2
        ]
        if series_vals:
            total += sum(series_vals) / len(series_vals)
    return total


def _util_pct(usage: float, capacity: float) -> float:
    if capacity <= 0:
        return 0.0
    return round(100 * usage / capacity, 1)


def _cpu_rate_window() -> str:
    return os.environ.get("SQUEEZE_PROM_CPU_RATE_WINDOW", "1m").strip() or "1m"


def _prom_range_step(start: float, end: float) -> str:
    span = end - start
    if span < 150:
        return os.environ.get("SQUEEZE_PROM_RANGE_STEP", "5s").strip() or "5s"
    if span < 300:
        return "15s"
    return "30s"


def _min_prom_samples() -> int:
    return max(1, int(os.environ.get("SQUEEZE_PROM_MIN_SAMPLES", "12")))


def _max_sample_count(results: list[dict]) -> int:
    if not results:
        return 0
    return max(len(r.get("values") or []) for r in results)


def _per_pod_rows_from_results(results: list[dict]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for r in results:
        metric = r.get("metric") or {}
        pod = metric.get("pod") or metric.get("pod_name") or "?"
        container = metric.get("container") or metric.get("container_name") or "?"
        mean_cores = _mean_value([r])
        peak_cores = _max_value([r])
        out.append(
            {
                "pod": pod,
                "container": container,
                "cpu_mean_cores": round(mean_cores, 4),
                "cpu_mean_m": round(mean_cores * 1000.0, 1),
                "cpu_peak_cores": round(peak_cores, 4),
                "cpu_peak_m": round(peak_cores * 1000.0, 1),
                "sample_count": len(r.get("values") or []),
            }
        )
    out.sort(key=lambda row: row["cpu_mean_m"], reverse=True)
    return out


def _cadvisor_pod_selector(namespace: str, deployment_name: str) -> str:
    return (
        f'namespace="{namespace}",pod=~"{deployment_name}.+",'
        f'container!="",container!="POD",image!=""'
    )


def _cadvisor_pod_selector_loose(namespace: str, deployment_name: str) -> str:
    """Same as strict cadvisor selector but omit image!= — absent `image` drops all series with strict matcher."""
    return (
        f'namespace="{namespace}",pod=~"{deployment_name}.+",'
        f'container!="",container!="POD"'
    )


def _deployment_pod_re(namespace: str, deployment_name: str) -> str:
    """Pods from a Deployment are {name}-{rs-hash}-{rand}; prefer this regex first."""
    return (
        f'namespace="{namespace}",pod=~"{deployment_name}-.+",'
        f'container!="",container!="POD"'
    )


def _first_non_empty_range(
    base_url: str, queries: list[str], start: float, end: float, step: str
) -> tuple[list[dict], int, str | None]:
    """Try queries in order; return first non-empty result, attempt count, winning query."""
    attempts = 0
    for q in queries:
        attempts += 1
        out = _query_range(base_url, q, start, end, step=step)
        if out:
            return out, attempts, q
    return [], attempts, None


def _per_pod_cpu_diagnostics(
    prometheus_url: str,
    pod_selector: str,
    q_start: float,
    q_end: float,
    step: str,
) -> list[dict[str, Any]]:
    """Per-pod/container CPU means over the k6 window (burn divergence debugging)."""
    q = f"rate(container_cpu_usage_seconds_total{{{pod_selector}}}[{_cpu_rate_window()}])"
    results = _query_range(prometheus_url, q, q_start, q_end, step=step)
    out: list[dict[str, Any]] = []
    for r in results:
        metric = r.get("metric") or {}
        pod = metric.get("pod") or metric.get("pod_name") or "?"
        container = metric.get("container") or metric.get("container_name") or "?"
        mean_cores = _mean_value([r])
        peak_cores = _max_value([r])
        out.append(
            {
                "pod": pod,
                "container": container,
                "cpu_mean_cores": round(mean_cores, 4),
                "cpu_mean_m": round(mean_cores * 1000.0, 1),
                "cpu_peak_cores": round(peak_cores, 4),
                "cpu_peak_m": round(peak_cores * 1000.0, 1),
                "sample_count": len(r.get("values") or []),
            }
        )
    out.sort(key=lambda row: row["cpu_mean_m"], reverse=True)
    return out


def get_prometheus_observed(
    start_ts: float,
    end_ts: float,
    namespace: str = "default",
    deployment_name: str = "stress-service",
    prometheus_url: str = DEFAULT_PROMETHEUS_URL,
    cpu_request_m: int = 0,
    cpu_limit_m: int = 500,
    mem_limit_mib: int = 256,
    deployment_replicas: int = 0,
    hpa_min_replicas: int = 0,
    time_pad_s: float = _TIME_PAD_S,
) -> dict:
    """
    Query Prometheus over [start_ts, end_ts] (optional time_pad_s).

    Primary utilization fields (cpu_util_request_pct, cpu_util_pct, mem_util_pct) use the
    arithmetic mean of samples in that window. Peak variants (*_peak) retain the window max.
    When replica series are empty but YAML declares replicas, use config fallback for denominators.
    """
    observed: dict[str, Any] = {
        "replicas": 0,
        "replicas_max": 0,
        "cpu_util_pct": 0.0,
        "cpu_util_pct_peak": 0.0,
        "cpu_util_request_pct": 0.0,
        "cpu_util_request_pct_peak": 0.0,
        "mem_util_pct": 0.0,
        "mem_util_pct_peak": 0.0,
        "cpu_usage_avg_m": 0.0,
        "mem_usage_avg_mib": 0.0,
        "oom_kills": 0,
        "cpu_util_to_limit": 0.0,
        "cpu_util_to_request": 0.0,
        "cpu_util_to_request_peak": 0.0,
    }

    k6_start = float(start_ts)
    k6_end = float(end_ts)
    q_start = k6_start - time_pad_s
    q_end = k6_end + time_pad_s
    step = _prom_range_step(k6_start, k6_end)
    rate_w = _cpu_rate_window()
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
    mean_avail = _mean_value(repl_avail_r)
    mean_spec = _mean_value(repl_spec_r)
    mean_hpa = _mean_value(repl_hpa_r)
    mean_from_prom = max(mean_avail, mean_spec, mean_hpa)

    replicas_series_matched = bool(repl_avail_r or repl_spec_r or repl_hpa_r)

    yaml_floor = max(int(deployment_replicas or 0), int(hpa_min_replicas or 0), 1)
    if max_from_prom > 0:
        max_replicas = max_from_prom
        mean_replicas = max(mean_from_prom, 1.0)
        replicas_inferred = False
    else:
        max_replicas = yaml_floor
        mean_replicas = float(yaml_floor)
        replicas_inferred = True

    observed["replicas"] = max_replicas
    observed["replicas_max"] = max_replicas
    denom_replicas_mean = max(int(round(mean_replicas)), 1)
    denom_replicas_peak = max(max_replicas, 1)

    cadv = _cadvisor_pod_selector(namespace, deployment_name)
    cadv_loose = _cadvisor_pod_selector_loose(namespace, deployment_name)
    dep_pod = _deployment_pod_re(namespace, deployment_name)
    cpu_per_pod_queries = [
        f"rate(container_cpu_usage_seconds_total{{{dep_pod}}}[{rate_w}])",
        f"rate(container_cpu_usage_seconds_total{{{cadv_loose}}}[{rate_w}])",
        f'rate(container_cpu_usage_seconds_total{{job="kubelet",metrics_path="/metrics/cadvisor",{dep_pod}}}[{rate_w}])',
        f'rate(container_cpu_usage_seconds_total{{job="kubelet",metrics_path="/metrics/cadvisor",{cadv_loose}}}[{rate_w}])',
        f'rate(container_cpu_usage_seconds_total{{namespace="{namespace}",pod=~"{deployment_name}.+",container!="",container!="POD"}}[{rate_w}])',
        f'rate(container_cpu_usage_seconds_total{{namespace="{namespace}",pod_name=~"{deployment_name}.+",container_name!=""}}[{rate_w}])',
    ]
    cpu_query_used: str | None = None
    cpu_results, cpu_query_attempts, cpu_query_used = _first_non_empty_range(
        prometheus_url, cpu_per_pod_queries, q_start, q_end, step
    )
    cpu_collection_mode = "per_pod_series_sum"
    if cpu_results:
        cpu_usage_mean_cores = _sum_series_means(cpu_results)
        cpu_usage_peak_cores = _sum_series_maxima(cpu_results)
    else:
        cpu_aggregate_queries = [
            f"sum(rate(container_cpu_usage_seconds_total{{{dep_pod}}}[{rate_w}]))",
            f"sum(rate(container_cpu_usage_seconds_total{{{cadv_loose}}}[{rate_w}]))",
            f'sum(rate(container_cpu_usage_seconds_total{{namespace="{namespace}",pod=~"{deployment_name}.+",container!="",container!="POD"}}[{rate_w}]))',
            f"sum(rate(container_cpu_usage_seconds_total{{{dep_pod}}}[5m]))",
            f'sum(rate(container_cpu_usage_seconds_total{{namespace="{namespace}",pod=~"{deployment_name}.+",container!="",container!="POD"}}[5m]))',
        ]
        agg_results, agg_attempts, cpu_query_used = _first_non_empty_range(
            prometheus_url, cpu_aggregate_queries, q_start, q_end, step
        )
        cpu_query_attempts += agg_attempts
        cpu_results = agg_results
        cpu_collection_mode = "aggregate_query"
        cpu_usage_mean_cores = _mean_value(cpu_results)
        cpu_usage_peak_cores = _max_value(cpu_results)

    mem_per_pod_queries = [
        f'container_memory_working_set_bytes{{job="kubelet",metrics_path="/metrics/cadvisor",{cadv}}}',
        f'container_memory_working_set_bytes{{namespace="{namespace}",pod=~"{deployment_name}.+",container!="",container!="POD"}}',
        f'container_memory_working_set_bytes{{namespace="{namespace}",pod_name=~"{deployment_name}.+",container_name!=""}}',
    ]
    mem_query_used: str | None = None
    mem_results, mem_query_attempts, mem_query_used = _first_non_empty_range(
        prometheus_url, mem_per_pod_queries, q_start, q_end, step
    )
    mem_collection_mode = "per_pod_series_sum"
    if mem_results:
        mem_bytes_mean = _sum_series_means(mem_results)
        mem_bytes_peak = _sum_series_maxima(mem_results)
    else:
        mem_aggregate_queries = [
            f'sum(container_memory_working_set_bytes{{job="kubelet",metrics_path="/metrics/cadvisor",{cadv}}})',
            f"sum(container_memory_working_set_bytes{{{cadv}}})",
            f'sum(container_memory_working_set_bytes{{namespace="{namespace}",pod=~"{deployment_name}.+",container!="",container!="POD"}})',
        ]
        agg_mem, agg_mem_attempts, mem_query_used = _first_non_empty_range(
            prometheus_url, mem_aggregate_queries, q_start, q_end, step
        )
        mem_query_attempts += agg_mem_attempts
        mem_results = agg_mem
        mem_collection_mode = "aggregate_query"
        mem_bytes_mean = _mean_value(mem_results)
        mem_bytes_peak = _max_value(mem_results)

    observed["cpu_usage_avg_m"] = round(cpu_usage_mean_cores * 1000.0, 1)
    observed["mem_usage_avg_mib"] = round(mem_bytes_mean / (1024 * 1024), 1)

    if cpu_request_m > 0:
        mean_req_cores = (cpu_request_m / 1000.0) * denom_replicas_mean
        peak_req_cores = (cpu_request_m / 1000.0) * denom_replicas_peak
        if mean_req_cores > 0:
            observed["cpu_util_request_pct"] = _util_pct(
                cpu_usage_mean_cores, mean_req_cores
            )
            observed["cpu_util_to_request"] = round(
                cpu_usage_mean_cores / mean_req_cores, 2
            )
        if peak_req_cores > 0:
            observed["cpu_util_request_pct_peak"] = _util_pct(
                cpu_usage_peak_cores, peak_req_cores
            )
            observed["cpu_util_to_request_peak"] = round(
                cpu_usage_peak_cores / peak_req_cores, 2
            )

    if cpu_limit_m > 0:
        mean_lim_cores = (cpu_limit_m / 1000.0) * denom_replicas_mean
        peak_lim_cores = (cpu_limit_m / 1000.0) * denom_replicas_peak
        if mean_lim_cores > 0:
            observed["cpu_util_pct"] = _util_pct(cpu_usage_mean_cores, mean_lim_cores)
            observed["cpu_util_to_limit"] = round(
                cpu_usage_mean_cores / mean_lim_cores, 2
            )
        if peak_lim_cores > 0:
            observed["cpu_util_pct_peak"] = _util_pct(
                cpu_usage_peak_cores, peak_lim_cores
            )

    if mem_limit_mib > 0:
        mean_mem_cap = mem_limit_mib * 1024 * 1024 * denom_replicas_mean
        peak_mem_cap = mem_limit_mib * 1024 * 1024 * denom_replicas_peak
        if mean_mem_cap > 0:
            observed["mem_util_pct"] = _util_pct(mem_bytes_mean, mean_mem_cap)
        if peak_mem_cap > 0:
            observed["mem_util_pct_peak"] = _util_pct(mem_bytes_peak, peak_mem_cap)

    oom_q = (
        f"sum(kube_pod_container_status_last_terminated_reason{{"
        f'namespace="{namespace}",reason="OOMKilled",pod=~"{deployment_name}.+"}})'
    )
    oom_results = _query(prometheus_url, oom_q, time_ts=end_ts)
    observed["oom_kills"] = int(_last_value(oom_results))

    cpu_series_matched = bool(cpu_results)
    mem_series_matched = bool(mem_results)
    cpu_sample_count = _max_sample_count(cpu_results)
    mem_sample_count = _max_sample_count(mem_results)
    min_samples = _min_prom_samples()
    utilization_trustworthy = bool(
        cpu_series_matched
        and mem_series_matched
        and (replicas_series_matched or replicas_inferred)
        and cpu_sample_count >= min_samples
    )

    if cpu_collection_mode == "per_pod_series_sum" and cpu_results:
        cpu_per_pod = _per_pod_rows_from_results(cpu_results)
    else:
        cpu_per_pod = _per_pod_cpu_diagnostics(
            prometheus_url, dep_pod, q_start, q_end, step
        )
    cpu_per_pod_sum_m = round(sum(row["cpu_mean_m"] for row in cpu_per_pod), 1)
    cpu_aggregate_vs_pods_delta_m = round(
        float(observed["cpu_usage_avg_m"]) - cpu_per_pod_sum_m, 1
    )
    prom_pod_count = len(cpu_per_pod)
    replica_count_mismatch = (
        prom_pod_count > 0 and prom_pod_count != denom_replicas_mean
    )
    if replica_count_mismatch:
        _log(
            f"collect_warn prom_pod_count={prom_pod_count} "
            f"yaml_replicas={denom_replicas_mean} "
            f"prom_replicas_mean={round(mean_replicas, 2)} MISMATCH"
        )

    observed["telemetry"] = {
        "k6_window_start_ts": k6_start,
        "k6_window_end_ts": k6_end,
        "window_start_ts": q_start,
        "window_end_ts": q_end,
        "prom_range_step": step,
        "cpu_rate_window": rate_w,
        "prom_min_samples": min_samples,
        "cpu_sample_count": cpu_sample_count,
        "mem_sample_count": mem_sample_count,
        "utilization_aggregation": "mean",
        "replicas_mean": round(mean_replicas, 2),
        "replicas_series_matched": replicas_series_matched,
        "replicas_inferred_from_config": replicas_inferred,
        "cpu_series_matched": cpu_series_matched,
        "mem_series_matched": mem_series_matched,
        "cpu_query_attempts": cpu_query_attempts,
        "mem_query_attempts": mem_query_attempts,
        "cpu_query_used": cpu_query_used,
        "mem_query_used": mem_query_used,
        "cpu_collection_mode": cpu_collection_mode,
        "mem_collection_mode": mem_collection_mode,
        "cpu_per_pod": cpu_per_pod,
        "cpu_per_pod_sum_m": cpu_per_pod_sum_m,
        "cpu_aggregate_vs_pods_delta_m": cpu_aggregate_vs_pods_delta_m,
        "prom_pod_count": prom_pod_count,
        "yaml_replicas_expected": denom_replicas_mean,
        "replica_count_mismatch": replica_count_mismatch,
        "utilization_trustworthy": utilization_trustworthy,
    }
    _log(
        f"collect_done cpu_util_request_pct={observed.get('cpu_util_request_pct')} "
        f"burn_m={observed.get('cpu_usage_avg_m')} "
        f"cpu_util_request_pct_peak={observed.get('cpu_util_request_pct_peak')} "
        f"mem_util_pct={observed.get('mem_util_pct')} "
        f"cpu_series_matched={cpu_series_matched} mem_series_matched={mem_series_matched} "
        f"cpu_attempts={cpu_query_attempts} mem_attempts={mem_query_attempts} "
        f"cpu_mode={cpu_collection_mode} mem_mode={mem_collection_mode} "
        f"cpu_query_used={cpu_query_used!r} "
        f"samples={cpu_sample_count}/{min_samples} step={step} rate={rate_w} "
        f"per_pod_sum_m={cpu_per_pod_sum_m} aggregate_delta_m={cpu_aggregate_vs_pods_delta_m} "
        f"trustworthy={utilization_trustworthy}"
    )
    for row in cpu_per_pod:
        _log(
            f"collect_per_pod pod={row['pod']} container={row['container']} "
            f"mean_m={row['cpu_mean_m']} peak_m={row['cpu_peak_m']} "
            f"samples={row['sample_count']}"
        )

    return observed
