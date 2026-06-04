"""Aggregate compare-sweep runs for research campaigns (stats + winner markers)."""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

ARM_LAYOUTS: dict[str, tuple[str, str]] = {
    "formula_llm": ("formula-run", "llm-run"),
    "advanced_vanilla": ("advanced-llm-run", "vanilla-llm-run"),
    "hpa_llm": ("hpa-run", "llm-run"),
}


def _load_boundary(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _best_pass_row(boundary: dict[str, Any]) -> dict[str, Any] | None:
    rows = boundary.get("rows") or []
    for row in reversed(rows):
        if (row.get("status") or "").upper() == "PASS":
            return row
    return rows[-1] if rows else None


def _run_metrics(run_dir: Path, arm_a: str, arm_b: str) -> dict[str, Any] | None:
    ba = run_dir / arm_a / "cost-effective-boundary.json"
    bb = run_dir / arm_b / "cost-effective-boundary.json"
    if not ba.is_file() or not bb.is_file():
        return None
    da, db = _load_boundary(ba), _load_boundary(bb)
    pa, pb = _best_pass_row(da), _best_pass_row(db)
    if not pa or not pb:
        return None

    def _f(row: dict, key: str) -> float | None:
        v = row.get(key)
        if v is None:
            return None
        try:
            return float(v)
        except (TypeError, ValueError):
            return None

    return {
        "iterations_a": len(da.get("rows") or []),
        "iterations_b": len(db.get("rows") or []),
        "stopped_a": da.get("stopped_reason"),
        "stopped_b": db.get("stopped_reason"),
        "pass_a": (pa.get("status") or "").upper() == "PASS",
        "pass_b": (pb.get("status") or "").upper() == "PASS",
        "prov_cost_a": _f(pa, "cost_score"),
        "prov_cost_b": _f(pb, "cost_score"),
        "util_cost_a": _f(pa, "cost_score_util"),
        "util_cost_b": _f(pb, "cost_score_util"),
        "p95_a": _f(pa, "p95_ms"),
        "p95_b": _f(pb, "p95_ms"),
        "error_a": _f(pa, "error_rate"),
        "error_b": _f(pb, "error_rate"),
        "target_rps": pa.get("target_rps") or pb.get("target_rps"),
        "achieved_a": _f(pa, "achieved_rps_target_window") or _f(pa, "achieved_rps"),
        "achieved_b": _f(pb, "achieved_rps_target_window") or _f(pb, "achieved_rps"),
    }


def _parse_rps_from_meta(sweep_root: Path, run_idx: int) -> float | None:
    meta = sweep_root / f"sweep-round-{run_idx}.txt"
    if not meta.is_file():
        return None
    for line in meta.read_text().splitlines():
        if line.startswith("STRESS_K6_RPS="):
            val = line.split("=", 1)[1].strip()
            try:
                return float(val)
            except ValueError:
                return None
    return None


def _winner_lower_is_better(a: float | None, b: float | None, *, tie_eps: float = 1e-6) -> str:
    if a is None or b is None:
        return "n/a"
    if abs(a - b) <= tie_eps:
        return "tie"
    return "a" if a < b else "b"


def _bootstrap_ci(
    values: list[float],
    *,
    n_boot: int = 2000,
    alpha: float = 0.05,
    seed: int = 0,
) -> tuple[float, float, float]:
    if not values:
        return (math.nan, math.nan, math.nan)
    if len(values) == 1:
        v = values[0]
        return (v, v, v)
    rng = random.Random(seed)
    n = len(values)
    meds: list[float] = []
    for _ in range(n_boot):
        sample = [values[rng.randrange(n)] for _ in range(n)]
        meds.append(statistics.median(sample))
    meds.sort()
    lo = meds[int((alpha / 2) * n_boot)]
    hi = meds[int((1 - alpha / 2) * n_boot) - 1]
    return (statistics.median(values), lo, hi)


def _iqr(values: list[float]) -> tuple[float, float, float]:
    if not values:
        return (math.nan, math.nan, math.nan)
    qs = statistics.quantiles(values, n=4, method="inclusive") if len(values) >= 2 else [values[0], values[0], values[0]]
    if len(values) == 1:
        return (values[0], values[0], values[0])
    return (statistics.median(values), qs[0], qs[2])


def _wilcoxon_signed_rank_pvalue(diffs: list[float]) -> float | None:
    """Two-sided Wilcoxon signed-rank; scipy if available, else None."""
    nz = [d for d in diffs if abs(d) > 1e-12]
    if len(nz) < 5:
        return None
    try:
        from scipy.stats import wilcoxon  # type: ignore

        res = wilcoxon(nz, alternative="two-sided", zero_method="wilcox")
        return float(res.pvalue)
    except Exception:
        return None


def _cohens_dz(diffs: list[float]) -> float | None:
    if len(diffs) < 2:
        return None
    mean_d = statistics.mean(diffs)
    sd = statistics.stdev(diffs)
    if sd <= 1e-12:
        return None
    return mean_d / sd


def discover_runs(sweep_root: Path) -> list[int]:
    out: list[int] = []
    for p in sorted(sweep_root.glob("run-*")):
        if not p.is_dir():
            continue
        try:
            out.append(int(p.name.split("-", 1)[1]))
        except ValueError:
            continue
    return out


def aggregate_sweep(
    sweep_root: Path,
    *,
    mode: str,
    label_a: str,
    label_b: str,
    out_dir: Path | None = None,
) -> Path:
    if mode not in ARM_LAYOUTS:
        raise ValueError(f"unknown mode {mode!r}; choose from {list(ARM_LAYOUTS)}")
    arm_a, arm_b = ARM_LAYOUTS[mode]
    out_dir = out_dir or (sweep_root / "aggregate")
    out_dir.mkdir(parents=True, exist_ok=True)

    per_run: list[dict[str, Any]] = []
    for idx in discover_runs(sweep_root):
        run_dir = sweep_root / f"run-{idx}"
        m = _run_metrics(run_dir, arm_a, arm_b)
        if not m:
            continue
        rps = _parse_rps_from_meta(sweep_root, idx) or m.get("target_rps")
        m.update(
            {
                "run": idx,
                "run_dir": str(run_dir),
                "stress_k6_rps": rps,
                "label_a": label_a,
                "label_b": label_b,
            }
        )
        if m["prov_cost_a"] is not None and m["prov_cost_b"] is not None:
            m["prov_cost_delta_b_minus_a"] = m["prov_cost_b"] - m["prov_cost_a"]
            m["prov_winner"] = _winner_lower_is_better(m["prov_cost_a"], m["prov_cost_b"])
        if m["p95_a"] is not None and m["p95_b"] is not None:
            m["p95_delta_b_minus_a"] = m["p95_b"] - m["p95_a"]
            m["p95_winner"] = _winner_lower_is_better(m["p95_a"], m["p95_b"])
        per_run.append(m)

    per_run_path = out_dir / "per_run_metrics.csv"
    if per_run:
        fields = sorted({k for row in per_run for k in row})
        with per_run_path.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            w.writerows(per_run)

    by_load: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in per_run:
        key = str(row.get("stress_k6_rps") or "unknown")
        by_load[key].append(row)

    summary_rows: list[dict[str, Any]] = []
    test_rows: list[dict[str, Any]] = []

    for load, rows in sorted(by_load.items(), key=lambda kv: float(kv[0]) if kv[0].replace(".", "").isdigit() else kv[0]):
        prov_d = [r["prov_cost_delta_b_minus_a"] for r in rows if r.get("prov_cost_delta_b_minus_a") is not None]
        p95_d = [r["p95_delta_b_minus_a"] for r in rows if r.get("p95_delta_b_minus_a") is not None]
        _, prov_q1, prov_q3 = _iqr(prov_d) if prov_d else (math.nan, math.nan, math.nan)
        _, prov_ci_lo, prov_ci_hi = _bootstrap_ci(prov_d) if prov_d else (math.nan, math.nan, math.nan)
        wins_b = sum(1 for r in rows if r.get("prov_winner") == "b")
        wins_a = sum(1 for r in rows if r.get("prov_winner") == "a")
        summary_rows.append(
            {
                "stress_k6_rps": load,
                "n": len(rows),
                "prov_median_delta_b_minus_a": statistics.median(prov_d) if prov_d else "",
                "prov_iqr_delta": f"{prov_q1:.6g}-{prov_q3:.6g}" if prov_d else "",
                "prov_bootstrap_ci95_lo": prov_ci_lo if prov_d else "",
                "prov_bootstrap_ci95_hi": prov_ci_hi if prov_d else "",
                "prov_wins_a": wins_a,
                "prov_wins_b": wins_b,
                "prov_wins_tie": len(rows) - wins_a - wins_b,
            }
        )
        test_rows.append(
            {
                "stress_k6_rps": load,
                "metric": "prov_cost_delta_b_minus_a",
                "n_pairs": len(prov_d),
                "median_delta": statistics.median(prov_d) if prov_d else "",
                "cohens_dz": _cohens_dz(prov_d) or "",
                "wilcoxon_p_two_sided": _wilcoxon_signed_rank_pvalue(prov_d) or "",
            }
        )
        if p95_d:
            test_rows.append(
                {
                    "stress_k6_rps": load,
                    "metric": "p95_delta_b_minus_a",
                    "n_pairs": len(p95_d),
                    "median_delta": statistics.median(p95_d),
                    "cohens_dz": _cohens_dz(p95_d) or "",
                    "wilcoxon_p_two_sided": _wilcoxon_signed_rank_pvalue(p95_d) or "",
                }
            )

    summary_path = out_dir / "by_load_summary.csv"
    with summary_path.open("w", newline="") as f:
        if summary_rows:
            w = csv.DictWriter(f, fieldnames=list(summary_rows[0].keys()))
            w.writeheader()
            w.writerows(summary_rows)

    tests_path = out_dir / "paired_tests.csv"
    with tests_path.open("w", newline="") as f:
        if test_rows:
            w = csv.DictWriter(f, fieldnames=list(test_rows[0].keys()))
            w.writeheader()
            w.writerows(test_rows)

    lines = [
        f"sweep_root={sweep_root.resolve()}",
        f"mode={mode}",
        f"arms={arm_a} vs {arm_b}",
        f"labels={label_a} vs {label_b}",
        f"runs_included={len(per_run)}",
        f"per_run_csv={per_run_path}",
        f"by_load_csv={summary_path}",
        f"paired_tests_csv={tests_path}",
        "",
        "Winner columns in per_run_metrics: prov_winner / p95_winner (a|b|tie; lower is better).",
        "Delta columns are b_minus_a (positive => arm B higher cost/latency).",
        "Install scipy for Wilcoxon p-values: pip install scipy",
    ]
    summary_txt = out_dir / "campaign_summary.txt"
    summary_txt.write_text("\n".join(lines) + "\n")
    return out_dir


def main() -> None:
    p = argparse.ArgumentParser(description="Aggregate compare-sweep for research campaigns")
    p.add_argument("sweep_root", type=Path)
    p.add_argument(
        "--mode",
        choices=sorted(ARM_LAYOUTS),
        default="formula_llm",
    )
    p.add_argument("--label-a", default="a")
    p.add_argument("--label-b", default="b")
    p.add_argument("--out-dir", type=Path, default=None)
    args = p.parse_args()
    out = aggregate_sweep(
        args.sweep_root,
        mode=args.mode,
        label_a=args.label_a,
        label_b=args.label_b,
        out_dir=args.out_dir,
    )
    print(out)


if __name__ == "__main__":
    main()
