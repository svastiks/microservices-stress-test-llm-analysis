#!/usr/bin/env python3
"""Exit 0 when advanced-llm beats vanilla-llm on compare pass bar.

COMPARE_SWEEP_PASS_BAR:
  cost  — advanced best_pass prov cost < vanilla (minimum for DOWN smoke)
  full  — cost win AND advanced iterations <= vanilla (ideal)
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_advanced_vanilla_pass_bar.py <run-dir>", file=sys.stderr)
        return 2
    run_dir = Path(sys.argv[1])
    mode = os.environ.get("COMPARE_SWEEP_PASS_BAR", "cost").strip().lower()
    adv_p = run_dir / "advanced-llm-run" / "cost-effective-boundary.json"
    van_p = run_dir / "vanilla-llm-run" / "cost-effective-boundary.json"
    if not adv_p.is_file() or not van_p.is_file():
        print(f"PASS_BAR: missing boundary JSON under {run_dir}", file=sys.stderr)
        return 1
    adv, van = _load(adv_p), _load(van_p)
    a_cost = float(adv.get("cost_best_pass_score") or 0)
    v_cost = float(van.get("cost_best_pass_score") or 0)
    a_iters = len(adv.get("rows") or [])
    v_iters = len(van.get("rows") or [])
    cost_ok = a_cost > 0 and v_cost > 0 and a_cost < v_cost
    iter_ok = a_iters > 0 and v_iters > 0 and a_iters <= v_iters
    if mode in ("full", "both", "cost_and_iters"):
        passed = cost_ok and iter_ok
        mode_label = "full"
    else:
        passed = cost_ok
        mode_label = "cost"
    print(
        f"PASS_BAR[{mode_label}]: advanced best_pass={a_cost:.4f} iters={a_iters} | "
        f"vanilla best_pass={v_cost:.4f} iters={v_iters} | "
        f"cost={'OK' if cost_ok else 'FAIL'} iters={'OK' if iter_ok else 'FAIL'} | "
        f"{'PASS' if passed else 'FAIL'}"
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
