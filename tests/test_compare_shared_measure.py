"""Tests for paired compare shared measurement helpers."""
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from analysis.compare_shared_measure import (
    RECOMMENDED_DEPLOYMENT_YAML,
    SHARED_CANONICAL_EXPERIMENT_FILENAME,
    compare_paired_measure_enabled,
    compare_probe_count,
    compare_skip_iteration_1,
    extract_shared_canonical_fields,
    format_paired_probe_report,
    load_measured_yaml_for_prompt,
    load_shared_canonical_overrides,
    max_paired_burn_delta_pct,
    paired_burn_delta_pct,
    paired_burn_tolerance_pct,
    restore_compare_arm_iter1_yaml,
)


class TestCompareSharedMeasure(unittest.TestCase):
    def test_paired_burn_delta_pct(self) -> None:
        self.assertAlmostEqual(paired_burn_delta_pct(300, 330), 9.52, places=1)
        self.assertAlmostEqual(paired_burn_delta_pct(300, 300), 0.0)

    def test_compare_paired_measure_default_off(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("SQUEEZE_COMPARE_PAIRED_MEASURE", None)
            self.assertFalse(compare_paired_measure_enabled())

    def test_compare_skip_iteration_1_off_by_default(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("SQUEEZE_COMPARE_SKIP_ITERATION_1", None)
            self.assertFalse(compare_skip_iteration_1())

    def test_format_paired_probe_report(self) -> None:
        text = format_paired_probe_report(
            pair_id="run-1",
            probes=[
                {"cpu_usage_avg_m": 300, "cpu_util_request_pct": 40},
                {"cpu_usage_avg_m": 330, "cpu_util_request_pct": 44},
            ],
            tolerance_pct=15,
        )
        self.assertIn("run-1", text)
        self.assertIn("within tolerance: **yes**", text)

    def test_max_paired_burn_delta_pct(self) -> None:
        probes = [
            {"cpu_usage_avg_m": 250},
            {"cpu_usage_avg_m": 400},
            {"cpu_usage_avg_m": 380},
        ]
        self.assertGreater(max_paired_burn_delta_pct(probes), 40)

    def test_compare_probe_count_default(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("SQUEEZE_COMPARE_PROBE_COUNT", None)
            self.assertEqual(compare_probe_count(), 3)

    def test_restore_compare_arm_iter1_yaml(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            arm = root / "run-1"
            iter1 = arm / "iteration-1"
            iter1.mkdir(parents=True)
            (iter1 / RECOMMENDED_DEPLOYMENT_YAML).write_text("replicas: 4\n")
            dep = root / "deployment.yaml"
            hpa = root / "hpa.yaml"
            dep.write_text("replicas: 5\n")
            hpa.write_text("maxReplicas: 5\n")
            self.assertTrue(
                restore_compare_arm_iter1_yaml(
                    arm_run_dir=arm,
                    deployment_yaml_path=dep,
                    hpa_yaml_path=hpa,
                )
            )
            self.assertIn("replicas: 4", dep.read_text())

    def test_tolerance_env(self) -> None:
        with mock.patch.dict(os.environ, {"SQUEEZE_COMPARE_PAIRED_BURN_TOLERANCE_PCT": "10"}):
            self.assertEqual(paired_burn_tolerance_pct(), 10.0)

    def test_extract_shared_canonical_fields(self) -> None:
        exp = {
            "config": {"cpu_request_m": 150, "deployment_replicas": 5},
            "observed": {"cpu_usage_avg_m": 387.8, "cpu_util_request_pct": 51.7},
            "start_ts": 1.0,
            "end_ts": 2.0,
            "squeeze_optimizer": "formula",
        }
        frozen = extract_shared_canonical_fields(exp)
        self.assertEqual(frozen["config"]["cpu_request_m"], 150)
        self.assertEqual(frozen["observed"]["cpu_usage_avg_m"], 387.8)
        self.assertNotIn("squeeze_optimizer", frozen)

    def test_load_shared_canonical_overrides(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td)
            payload = {"config": {"cpu_request_m": 150}, "observed": {"cpu_usage_avg_m": 300}}
            (run_dir / SHARED_CANONICAL_EXPERIMENT_FILENAME).write_text(json.dumps(payload))
            loaded = load_shared_canonical_overrides(run_dir)
            self.assertEqual(loaded["observed"]["cpu_usage_avg_m"], 300)

    def test_load_measured_yaml_for_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td)
            (run_dir / "deployment-measured.yaml").write_text("replicas: 5\n")
            text = load_measured_yaml_for_prompt(run_dir)
            self.assertIn("measured state", text)
            self.assertIn("replicas: 5", text)


if __name__ == "__main__":
    unittest.main()
