import os
import unittest
from unittest import mock

from analysis.cost_model import (
    boundary_cost_totals,
    cost_from_config,
    per_pod_unit_cost,
    row_util_cost,
)


class TestCostModel(unittest.TestCase):
    def test_weighted_default_50m_25mi(self) -> None:
        with mock.patch.dict(os.environ, {"COST_MODEL": "weighted"}, clear=False):
            c = cost_from_config(
                {"cpu_request_m": 50, "mem_request_mib": 25, "deployment_replicas": 1},
                {"replicas": 1},
            )
            self.assertEqual(c["cost_model"], "weighted")
            self.assertAlmostEqual(c["cost_score"], 0.0474, places=4)
            self.assertAlmostEqual(c["cost_score_legacy"], 0.0744, places=4)

    def test_legacy_matches_old_formula(self) -> None:
        with mock.patch.dict(os.environ, {"COST_MODEL": "legacy"}, clear=False):
            c = cost_from_config(
                {"cpu_request_m": 50, "mem_request_mib": 25, "deployment_replicas": 1},
                {"replicas": 1},
            )
            self.assertAlmostEqual(c["cost_score"], 0.0744, places=4)
            self.assertNotIn("cost_score_legacy", c)

    def test_three_pod_formula_pass_shape(self) -> None:
        with mock.patch.dict(os.environ, {"COST_MODEL": "weighted"}, clear=False):
            c = cost_from_config(
                {"cpu_request_m": 64, "mem_request_mib": 32, "deployment_replicas": 3},
                {"replicas": 3},
            )
            # 3 * (0.9*0.064 + 0.1*0.03125) ≈ 0.182
            self.assertAlmostEqual(c["cost_score"], 0.1822, places=3)

    def test_boundary_totals_search_and_steady(self) -> None:
        with mock.patch.dict(
            os.environ,
            {
                "COST_MODEL": "weighted",
                "COST_ITERATION_HOURS": "0.025",
                "COST_HORIZON_HOURS": "10",
            },
            clear=False,
        ):
            rows = [
                {"status": "FAIL", "cost_score": 0.05},
                {"status": "PASS", "cost_score": 0.2},
            ]
            t = boundary_cost_totals(rows)
            self.assertAlmostEqual(t["cost_search"], 0.025 * (0.05 + 0.2), places=6)
            self.assertAlmostEqual(t["cost_steady_state"], 10 * 0.2, places=6)
            self.assertAlmostEqual(
                t["cost_total"], t["cost_search"] + t["cost_steady_state"], places=6
            )

    def test_util_cost_differs_at_same_provisioned(self) -> None:
        with mock.patch.dict(os.environ, {"COST_MODEL": "weighted"}, clear=False):
            base = {
                "cpu_request_m": 70,
                "mem_request_mib": 35,
                "deployment_replicas": 2,
            }
            low = cost_from_config(base, {"replicas": 2, "cpu_util_pct": 48, "mem_util_pct": 50})
            high = cost_from_config(base, {"replicas": 2, "cpu_util_pct": 61, "mem_util_pct": 100})
            self.assertEqual(low["cost_score"], high["cost_score"])
            self.assertLess(low["cost_score_util"], high["cost_score_util"])

    def test_row_util_cost_backfill(self) -> None:
        row = {
            "replicas": 2,
            "cpu_request_m": 70,
            "mem_request_mib": 35,
            "cpu_util_pct": 48.1,
            "mem_util_pct": 49.9,
        }
        self.assertAlmostEqual(row_util_cost(row), 0.064, places=3)

    def test_gcp_unit_prices_ordering(self) -> None:
        with mock.patch.dict(os.environ, {"COST_MODEL": "gcp"}, clear=False):
            cpu_only = per_pod_unit_cost(1000, 0)
            mem_only = per_pod_unit_cost(0, 1024)
            self.assertGreater(cpu_only, mem_only * 5)
