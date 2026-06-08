"""Shared paired observe for squeeze compare arms (same YAML, aligned burn at iter 1)."""
from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from typing import Any

SHARED_CANONICAL_EXPERIMENT_FILENAME = "shared_canonical_experiment.json"
MEASURED_DEPLOYMENT_YAML = "deployment-measured.yaml"
MEASURED_HPA_YAML = "hpa-measured.yaml"
RECOMMENDED_DEPLOYMENT_YAML = "deployment-recommended.yaml"
RECOMMENDED_HPA_YAML = "hpa-recommended.yaml"


def compare_paired_measure_enabled() -> bool:
    return os.environ.get("SQUEEZE_COMPARE_PAIRED_MEASURE", "0").strip().lower() in (
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


def compare_probe_count() -> int:
    try:
        return max(2, int(os.environ.get("SQUEEZE_COMPARE_PROBE_COUNT", "3")))
    except ValueError:
        return 3


def compare_probe_settle_seconds() -> int:
    try:
        return max(0, int(os.environ.get("SQUEEZE_COMPARE_PROBE_SETTLE_SECONDS", "15")))
    except ValueError:
        return 15


def max_paired_burn_delta_pct(probes: list[dict]) -> float:
    burns = [float(p.get("cpu_usage_avg_m") or 0) for p in probes]
    worst = 0.0
    for i, a in enumerate(burns):
        for b in burns[i + 1 :]:
            worst = max(worst, paired_burn_delta_pct(a, b))
    return worst


def paired_burn_delta_pct(a: float, b: float) -> float:
    mid = (float(a) + float(b)) / 2.0
    if mid <= 0:
        return 0.0
    return abs(float(a) - float(b)) / mid * 100.0


def format_paired_probe_report(
    *,
    pair_id: str,
    probes: list[dict],
    tolerance_pct: float,
) -> str:
    delta = max_paired_burn_delta_pct(probes)
    ok = delta <= tolerance_pct
    lines = [
        "# Paired baseline observe (compare iter 1)",
        "",
        f"- pair: `{pair_id}`",
        f"- tolerance: {tolerance_pct:.1f}% burn delta (worst pair)",
        f"- probe count: {len(probes)}",
    ]
    for i, probe in enumerate(probes, start=1):
        burn = float(probe.get("cpu_usage_avg_m") or 0)
        lines.append(
            f"- probe-{i} burn: {burn:.1f}m · cpu% req: {probe.get('cpu_util_request_pct')}"
        )
    lines.extend(
        [
            f"- worst burn delta: {delta:.1f}% · within tolerance: **{'yes' if ok else 'no'}**",
            "",
            "Canonical iter-1 uses **one** k6 window; both arms re-analyze the same observed "
            "telemetry (formula vs LLM optimizer only).",
        ]
    )
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


def restore_compare_arm_iter1_yaml(
    *,
    arm_run_dir: Path,
    deployment_yaml_path: Path,
    hpa_yaml_path: Path,
) -> bool:
    """After baseline reset, restore repo YAML to iter-1 recommended state (disk only)."""
    iter1 = arm_run_dir / "iteration-1"
    dep_rec = iter1 / RECOMMENDED_DEPLOYMENT_YAML
    if not dep_rec.is_file():
        return False
    deployment_yaml_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(dep_rec, deployment_yaml_path)
    hpa_rec = iter1 / RECOMMENDED_HPA_YAML
    if hpa_rec.is_file():
        hpa_yaml_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(hpa_rec, hpa_yaml_path)
    return True
