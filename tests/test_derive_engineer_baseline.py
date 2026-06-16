"""Tests for Autopilot-style engineer baseline derivation."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from analysis.derive_engineer_baseline import derive_engineer_config, write_engineer_baseline

SAMPLE_EXP = {
    "experiment_id": "test-exp",
    "workload": {"target_requests_per_second": 45},
    "failure": {"failed": False},
    "config": {
        "cpu_request_m": 150,
        "cpu_limit_m": 300,
        "mem_request_mib": 75,
        "mem_limit_mib": 150,
        "deployment_replicas": 5,
        "hpa": {"min_replicas": 1, "max_replicas": 5, "target_cpu_util_pct": 60},
    },
    "observed": {
        "replicas": 5,
        "cpu_util_request_pct_peak": 54.1,
        "mem_util_pct": 11.0,
        "mem_util_pct_peak": 11.2,
        "mem_usage_avg_mib": 82.8,
        "telemetry": {
            "cpu_per_pod": [
                {"pod": "web-a", "cpu_peak_m": 144.8},
                {"pod": "web-b", "cpu_peak_m": 110.4},
                {"pod": "web-c", "cpu_peak_m": 103.3},
                {"pod": "web-d", "cpu_peak_m": 47.5},
            ],
        },
    },
    "deployment_yaml": "infra/k8s/spark/robot-shop-web-deployment.baseline.yaml",
    "hpa_yaml": "infra/k8s/spark/robot-shop-web-hpa.baseline.yaml",
}


class TestDeriveEngineerBaseline(unittest.TestCase):
    def test_cpu_request_from_hottest_pod_peak(self) -> None:
        derived = derive_engineer_config(SAMPLE_EXP)
        # ceil(144.8 * 1.3) = 189
        self.assertEqual(derived["config"]["cpu_request_m"], 189)

    def test_replicas_from_fleet_peak_and_target_util(self) -> None:
        derived = derive_engineer_config(SAMPLE_EXP)
        # fleet peak = 406m, cpu_request=189, target 0.6 → ceil(406/113.4)=4
        self.assertEqual(derived["config"]["deployment_replicas"], 4)

    def test_limits_are_multiplier_of_requests(self) -> None:
        derived = derive_engineer_config(SAMPLE_EXP)
        cfg = derived["config"]
        self.assertEqual(cfg["cpu_limit_m"], cfg["cpu_request_m"] * 2)
        self.assertEqual(cfg["mem_limit_mib"], cfg["mem_request_mib"] * 2)

    def test_write_outputs(self) -> None:
        repo = Path(__file__).resolve().parent.parent
        exp_path = repo / "tests" / "_tmp_engineer_exp.json"
        out_dir = repo / "tests" / "_tmp_engineer_out"
        try:
            exp_path.write_text(json.dumps(SAMPLE_EXP))
            derived = write_engineer_baseline(exp_path, out_dir, repo_root=repo)
            self.assertTrue((out_dir / "engineer-baseline.json").is_file())
            self.assertTrue((out_dir / "engineer-deployment.yaml").is_file())
            self.assertTrue((out_dir / "engineer-hpa.yaml").is_file())
            self.assertIn("prov_cost", (out_dir / "engineer-baseline.md").read_text())
            self.assertIsNotNone(derived["cost"]["cost_score"])
        finally:
            exp_path.unlink(missing_ok=True)
            for f in out_dir.glob("*"):
                f.unlink()
            out_dir.rmdir() if out_dir.exists() else None


if __name__ == "__main__":
    unittest.main()
