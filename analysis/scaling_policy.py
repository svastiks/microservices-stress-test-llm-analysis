"""Deterministic scaling direction from observed metrics + telemetry confidence."""


def attach_scaling_hint(experiment: dict) -> None:
    """
    Set experiment.scaling_hint in {UP, DOWN, HOLD, UNKNOWN} and a short rationale.
    UP ≈ under-provisioned / need more resources; DOWN ≈ over-provisioned / can trim;
    UNKNOWN = do not trust utilization for provisioning decisions.
    """
    obs = experiment.get("observed") or {}
    tel = obs.get("telemetry") or {}
    trustworthy = bool(tel.get("utilization_trustworthy"))

    fail = experiment.get("failure") or {}
    failed = bool(fail.get("failed"))
    slo = experiment.get("slo") or {}

    p95 = (obs.get("latency_ms") or {}).get("p95")
    err = obs.get("error_rate")
    slo_p95 = slo.get("p95_latency_ms")
    slo_err = slo.get("error_rate")

    cpu_pct = float(obs.get("cpu_util_pct") or 0)
    mem_pct = float(obs.get("mem_util_pct") or 0)
    cpu_to_lim = float(obs.get("cpu_util_to_limit") or 0)
    oom = int(obs.get("oom_kills") or 0)
    dropped_iterations = float(obs.get("dropped_iterations") or 0)
    achieved_rps_target_window = float(
        obs.get("achieved_requests_per_second_target_window") or 0
    )
    workload = experiment.get("workload") or {}
    target_rps = float(workload.get("target_requests_per_second") or 0)
    replicas = int(obs.get("replicas") or 0)
    observed_replicas_max = int(obs.get("replicas_max") or 0)
    cfg_hpa = (experiment.get("config") or {}).get("hpa") or {}
    configured_hpa_max = int(cfg_hpa.get("max_replicas") or 0)

    slo_p95_bad = p95 is not None and slo_p95 is not None and p95 > slo_p95
    slo_err_bad = err is not None and slo_err is not None and err > slo_err
    slo_stress = failed or slo_p95_bad or slo_err_bad
    throughput_collapse = bool(
        target_rps > 0 and achieved_rps_target_window < (0.85 * target_rps)
    )

    if not trustworthy:
        experiment["scaling_hint"] = "UNKNOWN"
        experiment["scaling_rationale"] = (
            "CPU/memory/replica utilization from Prometheus is missing or unreliable "
            "(see observed.telemetry). Do not infer over- vs under-provisioning from utilization."
        )
        return

    if slo_stress:
        # Squeeze loop under-provisioning recovery: never stall on HOLD while SLO is failing.
        if experiment.get("up_recovery"):
            experiment["scaling_hint"] = "UP"
            experiment["scaling_rationale"] = (
                "Under-provisioning recovery sweep: keep increasing capacity until SLO passes."
            )
            return
        # UP movement: if we are already at HPA ceiling and SLO is badly broken, scale up vertically.
        # Compare observed replicas against configured HPA max (not observed max vs itself).
        at_hpa_ceiling = configured_hpa_max > 0 and observed_replicas_max >= configured_hpa_max
        severe_p95 = bool(
            p95 is not None and slo_p95 is not None and p95 >= (3.0 * float(slo_p95))
        )
        severe_err = bool(
            err is not None and slo_err is not None and err >= (3.0 * float(slo_err))
        )
        if at_hpa_ceiling and (severe_p95 or severe_err):
            experiment["scaling_hint"] = "UP"
            experiment["scaling_rationale"] = (
                "SLO/error stress while replicas are at HPA max; scale up CPU/memory limits "
                "and/or raise HPA max to recover headroom."
            )
            return
        if oom > 0 or mem_pct >= 90:
            experiment["scaling_hint"] = "UP"
            experiment["scaling_rationale"] = (
                "SLO/error stress with memory pressure or OOM; increase memory and/or replicas."
            )
        elif cpu_pct >= 85 or cpu_to_lim >= 0.85:
            experiment["scaling_hint"] = "UP"
            experiment["scaling_rationale"] = (
                "SLO/error stress with high CPU vs limits; increase CPU and/or replicas."
            )
        elif throughput_collapse or dropped_iterations > 0:
            experiment["scaling_hint"] = "UP"
            experiment["scaling_rationale"] = (
                "SLO/error stress with throughput collapse or dropped iterations; "
                "increase replicas/limits to recover request handling headroom."
            )
        elif cpu_pct < 30 and mem_pct < 30 and oom == 0:
            experiment["scaling_hint"] = "HOLD"
            experiment["scaling_rationale"] = (
                "SLO/error stress but CPU and memory slack; unlikely CPU/mem bound—avoid blind scale-up."
            )
        else:
            experiment["scaling_hint"] = "HOLD"
            experiment["scaling_rationale"] = (
                "SLO/error stress with ambiguous utilization; investigate before large resource changes."
            )
        return

    if cpu_pct < 35 and mem_pct < 40:
        experiment["scaling_hint"] = "DOWN"
        experiment["scaling_rationale"] = (
            "SLO pass with low CPU and memory vs limits; candidate for modest right-sizing down."
        )
    elif cpu_pct > 75 or mem_pct > 80:
        if experiment.get("mode") == "squeeze" and not experiment.get("up_recovery"):
            experiment["scaling_hint"] = "DOWN"
            experiment["scaling_rationale"] = (
                "SLO pass in squeeze DOWN boundary search; continue reducing despite elevated utilization."
            )
        else:
            experiment["scaling_hint"] = "HOLD"
            experiment["scaling_rationale"] = (
                "SLO pass but utilization elevated; do not reduce CPU/memory/replicas without stronger slack evidence."
            )
    elif cpu_pct < 35 or mem_pct < 40:
        experiment["scaling_hint"] = "DOWN"
        experiment["scaling_rationale"] = (
            "SLO pass with slack on at least one resource; small reduction may be safe."
        )
    else:
        if experiment.get("mode") == "squeeze" and not experiment.get("up_recovery"):
            experiment["scaling_hint"] = "DOWN"
            experiment["scaling_rationale"] = (
                "SLO pass in squeeze DOWN boundary search; continue reducing toward first FAIL."
            )
        else:
            experiment["scaling_hint"] = "HOLD"
            experiment["scaling_rationale"] = (
                "SLO pass with mid-range utilization; prefer small or no moves."
            )
