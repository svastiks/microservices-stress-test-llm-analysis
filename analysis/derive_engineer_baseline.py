"""
Derive a single-shot engineer baseline from one profiling experiment.json.

Autopilot-inspired sizing (no squeeze loop):
  - cpu_request_m  = ceil(hottest_pod_cpu_peak_m × CPU_BUFFER)
  - mem_request_mib = ceil(per_pod_mem_peak_mib × MEM_BUFFER)
  - replicas       = ceil(fleet_cpu_peak_m / (cpu_request_m × TARGET_UTIL))
  - limits         = LIMIT_MULTIPLIER × requests

Input: one k6 pass at target RPS (typically fat-start iter-1 or engineer sweep).
Output: engineer-baseline.json, deployment/hpa YAML, markdown summary.
"""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
from typing import Any

import yaml

from analysis.cost_model import cost_from_config

DEFAULT_CPU_BUFFER = 1.3
DEFAULT_MEM_BUFFER = 1.2
DEFAULT_TARGET_UTIL = 0.6
DEFAULT_LIMIT_MULTIPLIER = 2.0
MIN_CPU_REQUEST_M = 25
MIN_MEM_REQUEST_MIB = 32


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if raw is None or not str(raw).strip():
        return default
    return float(raw)


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or not str(raw).strip():
        return default
    return int(raw)


def _live_replicas(obs: dict, cfg: dict) -> int:
    hpa = cfg.get("hpa") or {}
    for key in ("replicas", "replicas_max"):
        val = int(obs.get(key) or 0)
        if val > 0:
            return val
    for key in ("deployment_replicas",):
        val = int(cfg.get(key) or 0)
        if val > 0:
            return val
    return max(1, int(hpa.get("min_replicas") or 1))


def _per_pod_cpu_peak_m(obs: dict, cfg: dict) -> float:
    per_pod = ((obs.get("telemetry") or {}).get("cpu_per_pod")) or []
    peaks = [float(p.get("cpu_peak_m") or 0) for p in per_pod if p.get("cpu_peak_m")]
    if peaks:
        return max(peaks)
    req_m = int(cfg.get("cpu_request_m") or 0)
    pct = float(
        obs.get("cpu_util_request_pct_peak")
        or obs.get("cpu_util_request_pct")
        or 0
    )
    if req_m > 0 and pct > 0:
        return req_m * pct / 100.0
    return float(obs.get("cpu_usage_avg_m") or 0) / max(_live_replicas(obs, cfg), 1)


def _fleet_cpu_peak_m(obs: dict, cfg: dict) -> float:
    per_pod = ((obs.get("telemetry") or {}).get("cpu_per_pod")) or []
    peaks = [float(p.get("cpu_peak_m") or 0) for p in per_pod if p.get("cpu_peak_m")]
    if peaks:
        return sum(peaks)
    live = _live_replicas(obs, cfg)
    req_m = int(cfg.get("cpu_request_m") or 0)
    pct = float(
        obs.get("cpu_util_request_pct_peak")
        or obs.get("cpu_util_request_pct")
        or 0
    )
    if req_m > 0 and pct > 0 and live > 0:
        return live * req_m * pct / 100.0
    return float(obs.get("cpu_usage_avg_m") or 0)


def _per_pod_mem_peak_mib(obs: dict, cfg: dict) -> float:
    per_pod = ((obs.get("telemetry") or {}).get("mem_per_pod")) or []
    peaks = [float(p.get("mem_peak_mib") or 0) for p in per_pod if p.get("mem_peak_mib")]
    if peaks:
        return max(peaks)
    live = max(_live_replicas(obs, cfg), 1)
    avg_fleet = float(obs.get("mem_usage_avg_mib") or 0)
    if avg_fleet > 0:
        avg_per_pod = avg_fleet / live
        mem_util = float(obs.get("mem_util_pct") or 0)
        mem_peak_util = float(obs.get("mem_util_pct_peak") or 0)
        if mem_util > 0 and mem_peak_util > 0:
            return avg_per_pod * (mem_peak_util / mem_util)
        return avg_per_pod
    mem_lim = int(cfg.get("mem_limit_mib") or 0)
    pct = float(obs.get("mem_util_pct_peak") or obs.get("mem_util_pct") or 0)
    if mem_lim > 0 and pct > 0:
        return mem_lim * pct / 100.0
    return float(cfg.get("mem_request_mib") or MIN_MEM_REQUEST_MIB)


def derive_engineer_config(
    experiment: dict,
    *,
    cpu_buffer: float | None = None,
    mem_buffer: float | None = None,
    target_util: float | None = None,
    limit_multiplier: float | None = None,
) -> dict[str, Any]:
    """Return derived engineer config + provenance from one experiment.json payload."""
    obs = experiment.get("observed") or {}
    cfg = experiment.get("config") or {}
    hpa = cfg.get("hpa") or {}
    wl = experiment.get("workload") or {}

    cpu_buf = cpu_buffer if cpu_buffer is not None else _env_float(
        "ENGINEER_CPU_BUFFER", DEFAULT_CPU_BUFFER
    )
    mem_buf = mem_buffer if mem_buffer is not None else _env_float(
        "ENGINEER_MEM_BUFFER", DEFAULT_MEM_BUFFER
    )
    tgt_util = target_util if target_util is not None else _env_float(
        "ENGINEER_TARGET_UTIL", DEFAULT_TARGET_UTIL
    )
    lim_mult = limit_multiplier if limit_multiplier is not None else _env_float(
        "ENGINEER_LIMIT_MULTIPLIER", DEFAULT_LIMIT_MULTIPLIER
    )
    hpa_min = max(1, _env_int("ENGINEER_HPA_MIN_REPLICAS", int(hpa.get("min_replicas") or 1)))
    hpa_max = max(
        hpa_min,
        _env_int("ENGINEER_HPA_MAX_REPLICAS", int(hpa.get("max_replicas") or 5)),
    )
    hpa_target_cpu = _env_int(
        "ENGINEER_HPA_TARGET_CPU_UTIL_PCT",
        int(hpa.get("target_cpu_util_pct") or 60),
    )

    pod_cpu_peak_m = _per_pod_cpu_peak_m(obs, cfg)
    pod_mem_peak_mib = _per_pod_mem_peak_mib(obs, cfg)
    fleet_cpu_peak_m = _fleet_cpu_peak_m(obs, cfg)

    cpu_request_m = max(
        MIN_CPU_REQUEST_M,
        int(math.ceil(pod_cpu_peak_m * cpu_buf)),
    )
    mem_request_mib = max(
        MIN_MEM_REQUEST_MIB,
        int(math.ceil(pod_mem_peak_mib * mem_buf)),
    )
    cpu_limit_m = max(cpu_request_m, int(math.ceil(cpu_request_m * lim_mult)))
    mem_limit_mib = max(mem_request_mib, int(math.ceil(mem_request_mib * lim_mult)))

    denom = max(cpu_request_m * tgt_util, 1e-6)
    replicas = int(math.ceil(fleet_cpu_peak_m / denom))
    replicas = max(hpa_min, min(replicas, hpa_max))

    derived_cfg = {
        "cpu_request_m": cpu_request_m,
        "cpu_limit_m": cpu_limit_m,
        "mem_request_mib": mem_request_mib,
        "mem_limit_mib": mem_limit_mib,
        "deployment_replicas": replicas,
        "hpa": {
            "min_replicas": hpa_min,
            "max_replicas": replicas,
            "target_cpu_util_pct": hpa_target_cpu,
        },
    }
    derived_obs = {
        "replicas": replicas,
        "replicas_max": replicas,
        "cpu_util_pct": obs.get("cpu_util_pct"),
        "mem_util_pct": obs.get("mem_util_pct"),
    }
    cost = cost_from_config(derived_cfg, derived_obs)

    return {
        "method": "engineer_autopilot_single_shot",
        "citation": "Rzadca et al., Autopilot (EuroSys 2020); K8s VPA percentile sizing",
        "target_rps": wl.get("target_requests_per_second"),
        "source_experiment_id": experiment.get("experiment_id"),
        "parameters": {
            "cpu_buffer": cpu_buf,
            "mem_buffer": mem_buf,
            "target_util": tgt_util,
            "limit_multiplier": lim_mult,
        },
        "signals": {
            "pod_cpu_peak_m": round(pod_cpu_peak_m, 2),
            "pod_mem_peak_mib": round(pod_mem_peak_mib, 2),
            "fleet_cpu_peak_m": round(fleet_cpu_peak_m, 2),
            "profiling_replicas": _live_replicas(obs, cfg),
            "profiling_cpu_request_m": cfg.get("cpu_request_m"),
            "profiling_mem_request_mib": cfg.get("mem_request_mib"),
        },
        "config": derived_cfg,
        "cost": cost,
        "profiling_slo_pass": not bool((experiment.get("failure") or {}).get("failed")),
    }


def _fmt_cpu_m(m: int) -> str:
    return f"{int(m)}m"


def _fmt_mem_mib(mib: int) -> str:
    return f"{int(mib)}Mi"


def build_deployment_yaml(
    experiment: dict,
    derived: dict[str, Any],
    *,
    template_path: Path | None = None,
) -> str:
    cfg = derived["config"]
    dep_path = template_path
    if dep_path is None:
        dep_rel = experiment.get("deployment_yaml") or ""
        dep_path = Path(dep_rel) if dep_rel else None
    if dep_path is None or not dep_path.exists():
        dep_path = Path("infra/k8s/spark/robot-shop-web-deployment.baseline.yaml")
    doc = yaml.safe_load(dep_path.read_text())
    doc["spec"]["replicas"] = int(cfg["deployment_replicas"])
    container = doc["spec"]["template"]["spec"]["containers"][0]
    container["resources"]["requests"]["cpu"] = _fmt_cpu_m(cfg["cpu_request_m"])
    container["resources"]["requests"]["memory"] = _fmt_mem_mib(cfg["mem_request_mib"])
    container["resources"]["limits"]["cpu"] = _fmt_cpu_m(cfg["cpu_limit_m"])
    container["resources"]["limits"]["memory"] = _fmt_mem_mib(cfg["mem_limit_mib"])
    return yaml.dump(doc, default_flow_style=False, sort_keys=False)


def build_hpa_yaml(
    experiment: dict,
    derived: dict[str, Any],
    *,
    template_path: Path | None = None,
) -> str:
    cfg = derived["config"]
    hpa_cfg = cfg["hpa"]
    hpa_path = template_path
    if hpa_path is None:
        hpa_rel = experiment.get("hpa_yaml") or ""
        hpa_path = Path(hpa_rel) if hpa_rel else None
    if hpa_path is None or not hpa_path.exists():
        hpa_path = Path("infra/k8s/spark/robot-shop-web-hpa.baseline.yaml")
    doc = yaml.safe_load(hpa_path.read_text())
    replicas = int(cfg["deployment_replicas"])
    doc["spec"]["minReplicas"] = int(hpa_cfg["min_replicas"])
    doc["spec"]["maxReplicas"] = replicas
    for metric in doc["spec"].get("metrics") or []:
        res = (metric.get("resource") or {})
        if res.get("name") == "cpu":
            res.setdefault("target", {})["averageUtilization"] = int(
                hpa_cfg["target_cpu_util_pct"]
            )
    return yaml.dump(doc, default_flow_style=False, sort_keys=False)


def format_markdown(derived: dict[str, Any], *, source: str) -> str:
    cfg = derived["config"]
    cost = derived.get("cost") or {}
    sig = derived.get("signals") or {}
    params = derived.get("parameters") or {}
    lines = [
        "# Engineer baseline (Autopilot single-shot)",
        "",
        f"- **Source**: `{source}`",
        f"- **Target RPS**: {derived.get('target_rps')}",
        f"- **Profiling SLO PASS**: {derived.get('profiling_slo_pass')}",
        "",
        "## Method",
        "",
        (
            f"- CPU request = ceil(pod_cpu_peak_m × {params.get('cpu_buffer')}) "
            f"→ **{cfg['cpu_request_m']}m**"
        ),
        (
            f"- Mem request = ceil(pod_mem_peak_mib × {params.get('mem_buffer')}) "
            f"→ **{cfg['mem_request_mib']} MiB**"
        ),
        (
            f"- Replicas = ceil(fleet_cpu_peak_m / (cpu_request × {params.get('target_util')})) "
            f"→ **{cfg['deployment_replicas']}**"
        ),
        f"- Limits = {params.get('limit_multiplier')}× requests",
        "",
        "## Signals (from profiling run)",
        "",
        f"- pod_cpu_peak_m: {sig.get('pod_cpu_peak_m')}",
        f"- pod_mem_peak_mib: {sig.get('pod_mem_peak_mib')}",
        f"- fleet_cpu_peak_m: {sig.get('fleet_cpu_peak_m')}",
        f"- profiling config: {sig.get('profiling_replicas')}×"
        f"{sig.get('profiling_cpu_request_m')}m/"
        f"{sig.get('profiling_mem_request_mib')}Mi",
        "",
        "## Derived provisioned cost",
        "",
        f"- **prov_cost**: {cost.get('cost_score')}",
        f"- **util_cost** (profiling util, derived sizing): {cost.get('cost_score_util')}",
        "",
    ]
    return "\n".join(lines)


def write_engineer_baseline(
    experiment_path: Path,
    out_dir: Path,
    *,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    experiment = json.loads(experiment_path.read_text())
    derived = derive_engineer_config(experiment)
    out_dir.mkdir(parents=True, exist_ok=True)

    root = repo_root or Path.cwd()
    dep_tpl = None
    hpa_tpl = None
    dep_rel = experiment.get("deployment_yaml")
    hpa_rel = experiment.get("hpa_yaml")
    if dep_rel:
        p = Path(dep_rel)
        dep_tpl = p if p.is_absolute() else root / p
    if hpa_rel:
        p = Path(hpa_rel)
        hpa_tpl = p if p.is_absolute() else root / p

    (out_dir / "engineer-baseline.json").write_text(
        json.dumps(derived, indent=2) + "\n"
    )
    (out_dir / "engineer-deployment.yaml").write_text(
        build_deployment_yaml(experiment, derived, template_path=dep_tpl)
    )
    (out_dir / "engineer-hpa.yaml").write_text(
        build_hpa_yaml(experiment, derived, template_path=hpa_tpl)
    )
    (out_dir / "engineer-baseline.md").write_text(
        format_markdown(derived, source=str(experiment_path))
    )
    return derived


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Derive Autopilot-style engineer baseline from experiment.json"
    )
    parser.add_argument("experiment_json", type=Path, help="Profiling experiment.json")
    parser.add_argument(
        "-o",
        "--out-dir",
        type=Path,
        default=None,
        help="Output directory (default: <experiment_dir>/engineer-baseline)",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repo root for resolving deployment_yaml paths",
    )
    args = parser.parse_args(argv)
    exp_path = args.experiment_json.resolve()
    if not exp_path.is_file():
        raise SystemExit(f"not found: {exp_path}")
    out_dir = args.out_dir or (exp_path.parent / "engineer-baseline")
    derived = write_engineer_baseline(exp_path, out_dir, repo_root=args.repo_root.resolve())
    cost = derived.get("cost") or {}
    cfg = derived.get("config") or {}
    print(
        f"engineer baseline: {cfg.get('deployment_replicas')}×"
        f"{cfg.get('cpu_request_m')}m/{cfg.get('mem_request_mib')}Mi "
        f"prov_cost={cost.get('cost_score')} → {out_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
