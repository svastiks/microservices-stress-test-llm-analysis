"""Tests for research campaign aggregation."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from analysis.campaign_aggregate import aggregate_sweep


def _write_boundary(path: Path, rows: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "stopped_reason": "test",
                "rows": rows,
            }
        )
    )


class TestCampaignAggregate(unittest.TestCase):
    def test_formula_llm_aggregate(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for idx, (ca, cb) in enumerate([(0.1, 0.12), (0.1, 0.11), (0.1, 0.13)], start=1):
                run = root / f"run-{idx}"
                row = {
                    "status": "PASS",
                    "target_rps": 220,
                    "p95_ms": 200.0,
                    "error_rate": 0.0,
                    "cost_score": 0.0,
                    "cost_score_util": 0.0,
                }
                ra = {**row, "cost_score": ca, "p95_ms": 180.0}
                rb = {**row, "cost_score": cb, "p95_ms": 190.0}
                _write_boundary(run / "formula-run" / "cost-effective-boundary.json", [ra])
                _write_boundary(run / "llm-run" / "cost-effective-boundary.json", [rb])
                (root / f"sweep-round-{idx}.txt").write_text(f"STRESS_K6_RPS=220\n")
            out = aggregate_sweep(
                root,
                mode="formula_llm",
                label_a="formula",
                label_b="llm",
            )
            per_run = out / "per_run_metrics.csv"
            self.assertTrue(per_run.is_file())
            text = per_run.read_text()
            self.assertIn("prov_winner", text)
            self.assertTrue((out / "by_load_summary.csv").is_file())
            self.assertTrue((out / "campaign_summary.txt").is_file())


if __name__ == "__main__":
    unittest.main()
