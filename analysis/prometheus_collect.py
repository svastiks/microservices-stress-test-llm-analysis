"""
Query Prometheus over the k6 window and return observed metrics for experiment JSON.

Primary utilization (cpu_util_request_pct, cpu_util_pct, mem_util_pct) uses the mean of
Prometheus samples in [start_ts, end_ts]. Peak variants (*_peak) use the window maximum.
"""
from typing import Any

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


def _range_step(start: float, end: float) -> str:
    return "15s" if (end - start) < 150 else "30s"


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
    q = f"rate(container_cpu_usage_seconds_total{{{pod_selector}}}[1m])"
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
    step = _range_step(k6_start, k6_end)
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
    cpu_queries = [
        # Deployment-shaped pod names, loose labels, longer rate window (sparse scrapes / k3s)
        f"sum(rate(container_cpu_usage_seconds_total{{{dep_pod}}}[5m]))",
        f"sum(rate(container_cpu_usage_seconds_total{{{cadv_loose}}}[5m]))",
        f'sum(rate(container_cpu_usage_seconds_total{{job="kubelet",metrics_path="/metrics/cadvisor",{dep_pod}}}[5m]))',
        f'sum(rate(container_cpu_usage_seconds_total{{job="kubelet",metrics_path="/metrics/cadvisor",{cadv_loose}}}[5m]))',
        f'sum(rate(container_cpu_usage_seconds_total{{job=~"(kubelet|.*cadvisor.*)",namespace="{namespace}",pod=~"{deployment_name}-.+",container!="",container!="POD"}}[5m]))',
        # kubelet/cadvisor explicit labels (matches many kube-prometheus setups)
        f'sum(rate(container_cpu_usage_seconds_total{{job="kubelet",metrics_path="/metrics/cadvisor",{cadv}}}[1m]))',
        f'sum(rate(container_cpu_usage_seconds_total{{job="kubelet",metrics_path="/metrics/cadvisor",{cadv}}}[5m]))',
        # same but without image label constraint
        f'sum(rate(container_cpu_usage_seconds_total{{job="kubelet",metrics_path="/metrics/cadvisor",namespace="{namespace}",pod=~"{deployment_name}.+",container!="",container!="POD"}}[1m]))',
        f'sum(rate(container_cpu_usage_seconds_total{{job="kubelet",metrics_path="/metrics/cadvisor",namespace="{namespace}",pod=~"{deployment_name}.+",container!="",container!="POD"}}[5m]))',
        # Preferred strict selector
        f"sum(rate(container_cpu_usage_seconds_total{{{cadv}}}[1m]))",
        f"sum(rate(container_cpu_usage_seconds_total{{{cadv}}}[5m]))",
        # Fallback when image label is absent in exporter payload
        f'sum(rate(container_cpu_usage_seconds_total{{namespace="{namespace}",pod=~"{deployment_name}.+",container!="",container!="POD"}}[5m]))',
        f'sum(rate(container_cpu_usage_seconds_total{{namespace="{namespace}",pod=~"{deployment_name}.+",container!="",container!="POD"}}[1m]))',
        # Final fallback: pod-only selector
        f'sum(rate(container_cpu_usage_seconds_total{{namespace="{namespace}",pod=~"{deployment_name}.+"}}[5m]))',
        # Older scrape label variants
        f'sum(rate(container_cpu_usage_seconds_total{{namespace="{namespace}",pod_name=~"{deployment_name}.+",container_name!=""}}[5m]))',
    ]
    cpu_query_used: str | None = None
    cpu_results, cpu_query_attempts, cpu_query_used = _first_non_empty_range(
        prometheus_url, cpu_queries, q_start, q_end, step
    )
    cpu_usage_mean_cores = _mean_value(cpu_results)
    cpu_usage_peak_cores = _max_value(cpu_results)
    cpu_collection_mode = "aggregate_query"
    if not cpu_results:
        instant_cpu_queries = [
            f"sum(rate(container_cpu_usage_seconds_total{{{dep_pod}}}[5m]))",
            f"sum(rate(container_cpu_usage_seconds_total{{{cadv_loose}}}[5m]))",
            f'sum(rate(container_cpu_usage_seconds_total{{namespace="{namespace}",pod=~"{deployment_name}.+",container!="",container!="POD"}}[5m]))',
        ]
        for iq in instant_cpu_queries:
            cpu_query_attempts += 1
            inst = _query(prometheus_url, iq, time_ts=k6_end)
            if inst:
                cpu_results = inst
                cpu_query_used = iq
                cpu_collection_mode = "instant_query"
                try:
                    instant_cores = float((inst[0].get("value") or [0, "0"])[1])
                except (TypeError, ValueError, IndexError):
                    instant_cores = 0.0
                cpu_usage_mean_cores = instant_cores
                cpu_usage_peak_cores = instant_cores
                break
    if not cpu_results:
        cpu_per_pod_queries = [
            f"rate(container_cpu_usage_seconds_total{{{dep_pod}}}[5m])",
            f"rate(container_cpu_usage_seconds_total{{{cadv_loose}}}[5m])",
            f'rate(container_cpu_usage_seconds_total{{job="kubelet",metrics_path="/metrics/cadvisor",{dep_pod}}}[5m])',
            f'rate(container_cpu_usage_seconds_total{{job="kubelet",metrics_path="/metrics/cadvisor",{cadv}}}[1m])',
            f'rate(container_cpu_usage_seconds_total{{namespace="{namespace}",pod=~"{deployment_name}.+",container!="",container!="POD"}}[5m])',
            f'rate(container_cpu_usage_seconds_total{{namespace="{namespace}",pod=~"{deployment_name}.+",container!="",container!="POD"}}[1m])',
            f'rate(container_cpu_usage_seconds_total{{namespace="{namespace}",pod_name=~"{deployment_name}.+",container_name!=""}}[5m])',
        ]
        cpu_per_pod_results, cpu_per_pod_attempts, cpu_query_used = _first_non_empty_range(
            prometheus_url, cpu_per_pod_queries, q_start, q_end, step
        )
        cpu_query_attempts += cpu_per_pod_attempts
        if cpu_per_pod_results:
            cpu_usage_mean_cores = _sum_series_means(cpu_per_pod_results)
            cpu_usage_peak_cores = _sum_series_maxima(cpu_per_pod_results)
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
    mem_query_used: str | None = None
    mem_results, mem_query_attempts, mem_query_used = _first_non_empty_range(
        prometheus_url, mem_queries, q_start, q_end, step
    )
    mem_bytes_mean = _mean_value(mem_results)
    mem_bytes_peak = _max_value(mem_results)
    mem_collection_mode = "aggregate_query"
    if not mem_results:
        mem_per_pod_queries = [
            f'container_memory_working_set_bytes{{job="kubelet",metrics_path="/metrics/cadvisor",{cadv}}}',
            f'container_memory_working_set_bytes{{namespace="{namespace}",pod=~"{deployment_name}.+",container!="",container!="POD"}}',
            f'container_memory_working_set_bytes{{namespace="{namespace}",pod_name=~"{deployment_name}.+",container_name!=""}}',
        ]
        mem_per_pod_results, mem_per_pod_attempts, mem_query_used = _first_non_empty_range(
            prometheus_url, mem_per_pod_queries, q_start, q_end, step
        )
        mem_query_attempts += mem_per_pod_attempts
        if mem_per_pod_results:
            mem_bytes_mean = _sum_series_means(mem_per_pod_results)
            mem_bytes_peak = _sum_series_maxima(mem_per_pod_results)
            mem_results = mem_per_pod_results
            mem_collection_mode = "per_pod_series_sum"

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
    utilization_trustworthy = bool(
        cpu_series_matched
        and mem_series_matched
        and (replicas_series_matched or replicas_inferred)
    )

    cpu_per_pod = _per_pod_cpu_diagnostics(
        prometheus_url, dep_pod, q_start, q_end, step
    )
    cpu_per_pod_sum_m = round(sum(row["cpu_mean_m"] for row in cpu_per_pod), 1)
    cpu_aggregate_vs_pods_delta_m = round(
        float(observed["cpu_usage_avg_m"]) - cpu_per_pod_sum_m, 1
    )

    observed["telemetry"] = {
        "k6_window_start_ts": k6_start,
        "k6_window_end_ts": k6_end,
        "window_start_ts": q_start,
        "window_end_ts": q_end,
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
        f"per_pod_sum_m={cpu_per_pod_sum_m} aggregate_delta_m={cpu_aggregate_vs_pods_delta_m}"
    )
    for row in cpu_per_pod:
        _log(
            f"collect_per_pod pod={row['pod']} container={row['container']} "
            f"mean_m={row['cpu_mean_m']} peak_m={row['cpu_peak_m']} "
            f"samples={row['sample_count']}"
        )

    return observed
