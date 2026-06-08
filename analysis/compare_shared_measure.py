"""Shared paired observe for squeeze compare arms (same YAML, aligned burn at iter 1)."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

SHARED_CANONICAL_EXPERIMENT_FILENAME = "shared_canonical_experiment.json"
MEASURED_DEPLOYMENT_YAML = "deployment-measured.yaml"
MEASURED_HPA_YAML = "hpa-measured.yaml"


def compare_paired_measure_enabled() -> bool:
    return os.environ.get("SQUEEZE_COMPARE_PAIRED_MEASURE", "1").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


def compare_skip_iteration_1() -> bool:
    return os.environ.get("SQUEEZE_COMPARE_SKIP_ITERATION_1", "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


def paired_burn_tolerance_pct() -> float:
    try:
        return float(os.environ.get("SQUEEZE_COMPARE_PAIRED_BURN_TOLERANCE_PCT", "15"))
    except ValueError:
        return 15.0


def paired_burn_delta_pct(a: float, b: float) -> float:
    mid = (float(a) + float(b)) / 2.0
    if mid <= 0:
        return 0.0
    return abs(float(a) - float(b)) / mid * 100.0


def format_paired_probe_report(
    *,
    pair_id: str,
    probe_a: dict,
    probe_b: dict,
    tolerance_pct: float,
) -> str:
    ba = float(probe_a.get("cpu_usage_avg_m") or 0)
    bb = float(probe_b.get("cpu_usage_avg_m") or 0)
    delta = paired_burn_delta_pct(ba, bb)
    ok = delta <= tolerance_pct
    lines = [
        "# Paired baseline observe (compare iter 1)",
        "",
        f"- pair: `{pair_id}`",
        f"- tolerance: {tolerance_pct:.1f}% burn delta",
        f"- probe-a burn: {ba:.1f}m · cpu% req: {probe_a.get('cpu_util_request_pct')}",
        f"- probe-b burn: {bb:.1f}m · cpu% req: {probe_b.get('cpu_util_request_pct')}",
        f"- burn delta: {delta:.1f}% · within tolerance: **{'yes' if ok else 'no'}**",
        "",
        "Canonical iter-1 uses **one** k6 window; both arms re-analyze the same observed "
        "telemetry (formula vs LLM optimizer only).",
    ]
    return "\n".join(lines) + "\n"


def extract_shared_canonical_fields(exp: dict[str, Any]) -> dict[str, Any]:
    """Freeze config + observed (+ timestamps) from canonical iter-1 for reanalyze."""
    out: dict[str, Any] = {}
    if exp.get("config"):
        out["config"] = exp["config"]
    if exp.get("observed"):
        out["observed"] = exp["observed"]
    for key in ("start_ts", "end_ts"):
        if exp.get(key) is not None:
            out[key] = exp[key]
    return out


def load_shared_canonical_overrides(run_dir: Path) -> dict[str, Any] | None:
    path = run_dir / SHARED_CANONICAL_EXPERIMENT_FILENAME
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return None
    return data if isinstance(data, dict) else None


def load_measured_yaml_for_prompt(run_dir: Path) -> str | None:
    """YAML as deployed during the measured k6 window (before recommended.diff apply)."""
    parts: list[str] = []
    dep = run_dir / MEASURED_DEPLOYMENT_YAML
    hpa = run_dir / MEASURED_HPA_YAML
    if dep.is_file():
        parts.append(f"# FILE: {MEASURED_DEPLOYMENT_YAML} (measured state)\n")
        parts.append(dep.read_text())
    if hpa.is_file():
        parts.append(f"\n# FILE: {MEASURED_HPA_YAML} (measured state)\n")
        parts.append(hpa.read_text())
    return "\n".join(parts) if parts else None
