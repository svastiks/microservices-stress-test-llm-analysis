"""
Provisioned cost scoring (see cost_model.md).

Default: CPU/memory weighted 90/10 (≈ GCP custom-machine $ ratio). Set COST_MODEL=legacy
for the old equal-weight sum, or COST_MODEL=gcp for $/hour from published unit prices.
"""

from __future__ import annotations

import os
from typing import Any

# GCP us-central1 custom machine on-demand (cost_model.md §2)
GCP_CPU_USD_PER_MCORE_H = 0.033174 / 1000.0
GCP_MEM_USD_PER_MIB_H = 0.004446 / 1024.0

DEFAULT_CPU_WEIGHT = 0.9
DEFAULT_MEM_WEIGHT = 0.1


def cost_model_name() -> str:
    return (os.environ.get("COST_MODEL") or "weighted").strip().lower()


def cost_cpu_weight() -> float:
    return float(os.environ.get("COST_CPU_WEIGHT", str(DEFAULT_CPU_WEIGHT)))


def cost_mem_weight() -> float:
    return float(os.environ.get("COST_MEM_WEIGHT", str(DEFAULT_MEM_WEIGHT)))


def cost_iteration_hours() -> float:
    """One k6 evaluation window in hours (default 90s)."""
    raw = os.environ.get("COST_ITERATION_HOURS")
    if raw is not None and str(raw).strip():
        return float(raw)
    seconds = float(os.environ.get("STRESS_K6_DURATION_SECONDS", "90"))
    return seconds / 3600.0


def cost_horizon_hours() -> float:
    """Deployment horizon H for steady-state term (default 720h ≈ monthly)."""
    return float(os.environ.get("COST_HORIZON_HOURS", "720"))


def _util_fraction(util_pct: float | int | None) -> float:
    """Fraction of request used [0, 1]; util >100% capped at 1 for cost."""
    try:
        u = float(util_pct or 0)
    except (TypeError, ValueError):
        return 0.0
    return min(max(u / 100.0, 0.0), 1.0)


def per_pod_unit_cost(cpu_request_m: int, mem_request_mib: int) -> float:
    """Normalized or $/h unit cost for one pod from requests (not limits)."""
    cpu = max(0, int(cpu_request_m or 0))
    mem = max(0, int(mem_request_mib or 0))
    cpu_u = cpu / 1000.0
    mem_u = mem / 1024.0
    model = cost_model_name()
    if model == "legacy":
        return cpu_u + mem_u
    if model == "gcp":
        return GCP_CPU_USD_PER_MCORE_H * cpu + GCP_MEM_USD_PER_MIB_H * mem
    # weighted (default)
    return cost_cpu_weight() * cpu_u + cost_mem_weight() * mem_u


def per_pod_util_unit_cost(
    cpu_request_m: int,
    mem_request_mib: int,
    cpu_util_pct: float | int | None,
    mem_util_pct: float | int | None,
) -> float:
    """Weighted unit cost from requests × observed utilization (per pod)."""
    cpu_m = max(0, int(cpu_request_m or 0))
    mem_mib = max(0, int(mem_request_mib or 0))
    cpu_u = (cpu_m / 1000.0) * _util_fraction(cpu_util_pct)
    mem_u = (mem_mib / 1024.0) * _util_fraction(mem_util_pct)
    model = cost_model_name()
    if model == "legacy":
        return cpu_u + mem_u
    if model == "gcp":
        return (
            GCP_CPU_USD_PER_MCORE_H * cpu_m * _util_fraction(cpu_util_pct)
            + GCP_MEM_USD_PER_MIB_H * mem_mib * _util_fraction(mem_util_pct)
        )
    return cost_cpu_weight() * cpu_u + cost_mem_weight() * mem_u


def replicas_effective(config: dict, observed: dict) -> int:
    hpa = config.get("hpa") or {}
    replicas_observed = int(observed.get("replicas") or observed.get("replicas_max") or 0)
    dep_rep = int(config.get("deployment_replicas") or 0)
    min_r = int(hpa.get("min_replicas") or 0)
    n = replicas_observed or dep_rep or min_r or 1
    return max(1, n)


def cost_from_config(config: dict, observed: dict) -> dict[str, Any]:
    """Per-iteration provisioned cost (requests × replicas)."""
    n = replicas_effective(config, observed)
    cpu_request_m = int(config.get("cpu_request_m") or 0)
    mem_request_mib = int(config.get("mem_request_mib") or 0)
    cpu_limit_m = int(config.get("cpu_limit_m") or 0)
    mem_limit_mib = int(config.get("mem_limit_mib") or 0)
    unit = per_pod_unit_cost(cpu_request_m, mem_request_mib)
    cost_score = round(n * unit, 4)
    cpu_util = observed.get("cpu_util_pct")
    mem_util = observed.get("mem_util_pct")
    util_unit = per_pod_util_unit_cost(cpu_request_m, mem_request_mib, cpu_util, mem_util)
    cost_score_util = round(n * util_unit, 4)
    out: dict[str, Any] = {
        "cost_model": cost_model_name(),
        "replicas_effective": n,
        "provisioned_request_cpu_m": n * cpu_request_m,
        "provisioned_request_mem_mib": n * mem_request_mib,
        "provisioned_limit_cpu_m": n * cpu_limit_m,
        "provisioned_limit_mem_mib": n * mem_limit_mib,
        "per_pod_unit_cost": round(unit, 6),
        "per_pod_unit_cost_util": round(util_unit, 6),
        "cost_score": cost_score,
        "cost_score_util": cost_score_util,
    }
    if cost_model_name() != "legacy":
        legacy_unit = (cpu_request_m / 1000.0) + (mem_request_mib / 1024.0)
        out["cost_score_legacy"] = round(n * legacy_unit, 4)
    return out


def boundary_cost_totals(rows: list[dict]) -> dict[str, Any]:
    """
    Search + steady-state totals from boundary rows (cost_model.md §3–§5).
    Uses each row's cost_score when present; else recomputes from requests × replicas.
    """
    t_h = cost_iteration_hours()
    h_h = cost_horizon_hours()
    iter_scores: list[float] = []
    best_pass_score: float | None = None
    best_pass_score_util: float | None = None
    iter_scores_util: list[float] = []

    for row in rows or []:
        score = row.get("cost_score")
        if score is None:
            repl = max(1, int(row.get("replicas") or 0))
            cpu = int(row.get("cpu_request_m") or 0)
            mem = int(row.get("mem_request_mib") or 0)
            score = repl * per_pod_unit_cost(cpu, mem)
        else:
            score = float(score)
        iter_scores.append(score)

        score_u = row_util_cost(row)
        if score_u is not None:
            iter_scores_util.append(score_u)

        if row.get("status") == "PASS":
            best_pass_score = score
            if score_u is not None:
                best_pass_score_util = score_u

    search = round(t_h * sum(iter_scores), 6)
    steady = round(h_h * (best_pass_score or 0.0), 6) if best_pass_score is not None else 0.0
    search_util = round(t_h * sum(iter_scores_util), 6) if iter_scores_util else None
    steady_util = (
        round(h_h * best_pass_score_util, 6) if best_pass_score_util is not None else None
    )
    out = {
        "cost_model": cost_model_name(),
        "cost_iteration_hours": t_h,
        "cost_horizon_hours": h_h,
        "cost_search": search,
        "cost_steady_state": steady,
        "cost_total": round(search + steady, 6),
        "cost_best_pass_score": best_pass_score,
    }
    if search_util is not None and steady_util is not None:
        out["cost_search_util"] = search_util
        out["cost_steady_state_util"] = steady_util
        out["cost_total_util"] = round(search_util + steady_util, 6)
        out["cost_best_pass_score_util"] = best_pass_score_util
    return out


def row_util_cost(row: dict) -> float | None:
    """Utilization-weighted cost for a boundary row; computed if missing."""
    if row.get("cost_score_util") is not None:
        try:
            return float(row["cost_score_util"])
        except (TypeError, ValueError):
            pass
    repl = max(1, int(row.get("replicas") or 0))
    cpu = int(row.get("cpu_request_m") or 0)
    mem = int(row.get("mem_request_mib") or 0)
    if cpu <= 0 and mem <= 0:
        return None
    unit = per_pod_util_unit_cost(
        cpu, mem, row.get("cpu_util_pct"), row.get("mem_util_pct")
    )
    return round(repl * unit, 4)
