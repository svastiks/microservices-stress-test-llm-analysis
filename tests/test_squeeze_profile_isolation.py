"""Regression: up_demo fixes must not alter down_demo squeeze behavior."""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from analysis.results import (
    _apply_down_boundary_stop,
    _finalize_llm_squeeze_down,
    _llm_at_down_boundary_stop,
    _llm_over_replicated_replica_required,
    _llm_squeeze_down_boundary_active,
    _live_replica_drift,
    _postprocess_llm_result,
    _pure_llm_reconcile_replica_drift,
)


def _iter1_up_recovery_gate(
    *,
    profile: str,
    status_1: str,
    scaling_hint: str | None,
    failed: bool,
    has_diff: bool,
) -> str:
    """Mirror start.py iter-1 branch outcomes (up_recovery vs first_run_failed)."""
    is_up_demo = profile in {"up_demo", "up_demo_strict"}
    if status_1 == "PASS":
        return "down_squeeze_continue"
    fail_1 = failed
    up_demo_fail_recovery = (
        is_up_demo and fail_1 and scaling_hint in ("UP", "HOLD", None)
    )
    if (has_diff and scaling_hint == "UP") or up_demo_fail_recovery:
        return "up_recovery"
    return "first_run_failed"


class TestDownDemoUnchanged(unittest.TestCase):
    def test_down_boundary_active_with_down_sweep_env(self) -> None:
        exp = {
            "squeeze_optimizer": "llm",
            "analysis_goal": "efficiency",
            "mode": "squeeze",
        }
        with mock.patch.dict(os.environ, {"SQUEEZE_LLM_DOWN_BOUNDARY": "1"}, clear=False):
            self.assertTrue(_llm_squeeze_down_boundary_active(exp))

    def test_down_pass_llm_down_yaml_not_vetoed(self) -> None:
        """PASS + scaling_hint DOWN: down compare must keep LLM scale-down YAML."""
        exp = {
            "squeeze_optimizer": "llm",
            "analysis_goal": "efficiency",
            "mode": "squeeze",
            "scaling_hint": "DOWN",
            "failure": {"failed": False},
            "config": {
                "cpu_request_m": 150,
                "mem_request_mib": 75,
                "deployment_replicas": 5,
            },
            "observed": {"telemetry": {"utilization_trustworthy": True}},
        }
        down_dep = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 5
  template:
    spec:
      containers:
      - name: web
        resources:
          requests:
            cpu: 100m
            memory: 50Mi
          limits:
            cpu: 200m
            memory: 100Mi
"""
        result = {
            "deployment_yaml_new": down_dep,
            "hpa_yaml_new": "",
            "evidence": [],
        }
        with mock.patch.dict(os.environ, {"SQUEEZE_LLM_DOWN_BOUNDARY": "1"}, clear=False):
            out = _postprocess_llm_result(result, exp)
        self.assertTrue((out.get("deployment_yaml_new") or "").strip())

    def test_fat_start_enforces_replica_when_llm_trims_resources_only(self) -> None:
        """Fat down_demo baseline: guard injects replica drop if LLM only lowers CPU/mem."""
        exp = {
            "squeeze_optimizer": "llm",
            "analysis_goal": "efficiency",
            "mode": "squeeze",
            "scaling_hint": "DOWN",
            "failure": {"failed": False},
            "config": {
                "cpu_request_m": 150,
                "mem_request_mib": 75,
                "deployment_replicas": 5,
                "hpa": {"max_replicas": 5},
            },
            "observed": {
                "telemetry": {"utilization_trustworthy": True},
                "cpu_util_pct": 14.0,
                "mem_util_pct": 9.0,
                "replicas": 5,
                "replicas_max": 5,
            },
            "cost": {"cost_score": 0.71},
        }
        self.assertTrue(_llm_over_replicated_replica_required(exp))
        dep_on_disk = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 5
  template:
    spec:
      containers:
      - name: web
        resources:
          requests:
            cpu: 150m
            memory: 75Mi
          limits:
            cpu: 300m
            memory: 150Mi
"""
        hpa_on_disk = """apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web-hpa
spec:
  minReplicas: 1
  maxReplicas: 5
"""
        result = {
            "deployment_yaml_new": dep_on_disk.replace("150m", "135m").replace("75Mi", "65Mi"),
            "hpa_yaml_new": "",
            "evidence": [],
        }
        with tempfile.TemporaryDirectory() as td:
            dep_path = Path(td) / "dep.yaml"
            hpa_path = Path(td) / "hpa.yaml"
            dep_path.write_text(dep_on_disk)
            hpa_path.write_text(hpa_on_disk)
            with mock.patch.dict(os.environ, {"SQUEEZE_LLM_DOWN_BOUNDARY": "1"}, clear=False):
                _finalize_llm_squeeze_down(result, exp, dep_path, hpa_path)
        self.assertIn("replicas: 4", result["deployment_yaml_new"])
        self.assertEqual(result.get("squeeze_down_axis"), "replica")
        ev = " ".join(result.get("evidence") or [])
        self.assertNotIn("guard.veto_replica_down:resource_phase_gate", ev)

    def test_hot_multi_replica_requires_replica_drop(self) -> None:
        exp = {
            "squeeze_optimizer": "llm",
            "analysis_goal": "efficiency",
            "mode": "squeeze",
            "scaling_hint": "DOWN",
            "failure": {"failed": False},
            "config": {"cpu_request_m": 98, "deployment_replicas": 3},
            "observed": {
                "cpu_util_pct": 62.0,
                "mem_util_pct": 40.0,
                "replicas": 3,
                "replicas_max": 3,
            },
            "cost": {"cost_score": 0.28},
        }
        self.assertTrue(_llm_over_replicated_replica_required(exp))

    def test_hot_boundary_stop_clears_yaml(self) -> None:
        exp = {
            "squeeze_optimizer": "llm",
            "analysis_goal": "efficiency",
            "mode": "squeeze",
            "scaling_hint": "DOWN",
            "failure": {"failed": False},
            "config": {"cpu_request_m": 80, "deployment_replicas": 2},
            "observed": {
                "cpu_util_pct": 94.0,
                "mem_util_pct": 44.0,
                "replicas": 2,
                "replicas_max": 2,
            },
        }
        self.assertTrue(_llm_at_down_boundary_stop(exp))
        dep_on_disk = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: web
        resources:
          requests:
            cpu: 80m
            memory: 40Mi
"""
        result = {
            "deployment_yaml_new": dep_on_disk.replace("80m", "70m"),
            "hpa_yaml_new": "",
            "evidence": [],
        }
        with tempfile.TemporaryDirectory() as td:
            dep_path = Path(td) / "dep.yaml"
            hpa_path = Path(td) / "hpa.yaml"
            dep_path.write_text(dep_on_disk)
            hpa_path.write_text(
                "apiVersion: autoscaling/v2\nkind: HorizontalPodAutoscaler\n"
                "spec:\n  minReplicas: 1\n  maxReplicas: 2\n"
            )
            self.assertTrue(
                _apply_down_boundary_stop(result, exp, dep_path, hpa_path)
            )
        self.assertEqual(result.get("deployment_yaml_new"), "")
        self.assertIn("guard.hot_boundary_stop", " ".join(result.get("evidence") or []))

    def test_hot_replica_drop_enforced_at_73_util(self) -> None:
        from analysis.results import _llm_hot_replica_drop_required

        exp = {
            "squeeze_optimizer": "llm",
            "analysis_goal": "efficiency",
            "mode": "squeeze",
            "scaling_hint": "DOWN",
            "failure": {"failed": False},
            "config": {"cpu_request_m": 83, "deployment_replicas": 3},
            "observed": {
                "cpu_util_pct": 73.0,
                "mem_util_pct": 42.0,
                "replicas": 3,
                "replicas_max": 3,
            },
        }
        self.assertTrue(_llm_hot_replica_drop_required(exp))
        dep_on_disk = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: web
        resources:
          requests:
            cpu: 83m
            memory: 40Mi
"""
        result = {
            "deployment_yaml_new": dep_on_disk.replace("83m", "75m"),
            "hpa_yaml_new": "",
            "evidence": [],
        }
        with tempfile.TemporaryDirectory() as td:
            dep_path = Path(td) / "dep.yaml"
            hpa_path = Path(td) / "hpa.yaml"
            dep_path.write_text(dep_on_disk)
            hpa_path.write_text(
                "apiVersion: autoscaling/v2\nkind: HorizontalPodAutoscaler\n"
                "spec:\n  minReplicas: 1\n  maxReplicas: 3\n"
            )
            with mock.patch.dict(os.environ, {"SQUEEZE_LLM_DOWN_BOUNDARY": "1"}, clear=False):
                _finalize_llm_squeeze_down(result, exp, dep_path, hpa_path)
        self.assertIn("replicas: 2", result["deployment_yaml_new"])
        self.assertIn("guard.enforce_hot_replica_drop", " ".join(result.get("evidence") or []))

    def test_hot_multi_replica_required_after_prev_replica(self) -> None:
        from analysis.results import _llm_hot_multi_replica_burst

        exp = {
            "failure": {"failed": False},
            "_prev_iteration": {"squeeze_down_axis": "replica"},
            "observed": {
                "cpu_util_pct": 62.0,
                "mem_util_pct": 38.0,
                "replicas": 3,
                "replicas_max": 3,
            },
        }
        self.assertTrue(_llm_hot_multi_replica_burst(exp))
        self.assertTrue(_llm_over_replicated_replica_required(exp))

    def test_down_demo_iter1_pass_still_enters_down_squeeze(self) -> None:
        self.assertEqual(
            _iter1_up_recovery_gate(
                profile="down_demo",
                status_1="PASS",
                scaling_hint="DOWN",
                failed=False,
                has_diff=True,
            ),
            "down_squeeze_continue",
        )

    def test_down_demo_iter1_fail_down_hint_stops(self) -> None:
        self.assertEqual(
            _iter1_up_recovery_gate(
                profile="down_demo",
                status_1="FAIL",
                scaling_hint="DOWN",
                failed=True,
                has_diff=True,
            ),
            "first_run_failed",
        )


class TestResourceParsing(unittest.TestCase):
    def test_fractional_millicpu_parses(self) -> None:
        from analysis.experiment_build import (
            format_cpu_millicores,
            get_config_from_yaml,
            normalize_deployment_yaml_resources,
            parse_cpu_millicores,
        )
        import tempfile
        from pathlib import Path

        self.assertEqual(parse_cpu_millicores("112.5m"), 113)
        self.assertEqual(format_cpu_millicores(113), "113m")
        dep = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: web
        resources:
          requests:
            cpu: 112.5m
            memory: 75Mi
"""
        norm, notes = normalize_deployment_yaml_resources(dep)
        self.assertTrue(any("112.5m" in n for n in notes))
        self.assertIn("cpu: 113m", norm)
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "dep.yaml"
            p.write_text(norm)
            cfg = get_config_from_yaml(p, Path(td) / "missing-hpa.yaml")
            self.assertEqual(cfg["cpu_request_m"], 113)


class TestPureLlmDriftReconcile(unittest.TestCase):
    def test_reconcile_emits_yaml_when_live_exceeds_config(self) -> None:
        import tempfile
        from pathlib import Path

        exp = {
            "config": {"deployment_replicas": 4},
            "observed": {"replicas": 5, "replicas_max": 5},
        }
        self.assertTrue(_live_replica_drift(exp))
        with tempfile.TemporaryDirectory() as td:
            dep = Path(td) / "robot-shop-web-deployment.yaml"
            hpa = Path(td) / "robot-shop-web-hpa.yaml"
            dep.write_text(
                "apiVersion: apps/v1\nkind: Deployment\nmetadata:\n  name: web\n"
                "spec:\n  replicas: 4\n  template:\n    spec:\n      containers:\n"
                "      - name: web\n        resources:\n          requests:\n"
                "            cpu: 90m\n            memory: 45Mi\n"
            )
            hpa.write_text(
                "apiVersion: autoscaling/v2\nkind: HorizontalPodAutoscaler\n"
                "metadata:\n  name: web-hpa\nspec:\n  minReplicas: 1\n  maxReplicas: 5\n"
            )
            result: dict = {}
            ok = _pure_llm_reconcile_replica_drift(result, exp, dep, hpa)
            self.assertTrue(ok)
            self.assertIn("replicas: 4", result.get("deployment_yaml_new", ""))
            self.assertIn("maxReplicas: 4", result.get("hpa_yaml_new", ""))


class TestUpRecoveryGuard(unittest.TestCase):
    def test_guard_passes_through_llm_replica_first_yaml(self) -> None:
        """Guard must not rewrite LLM sizing — replica-first is prompt-driven."""
        from analysis.results import _guard_llm_up_recovery_yaml
        import tempfile
        from pathlib import Path

        dep = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: web
        resources:
          requests:
            cpu: 50m
            memory: 25Mi
          limits:
            cpu: 100m
            memory: 50Mi
"""
        llm_yaml = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: web
        resources:
          requests:
            cpu: 50m
            memory: 25Mi
          limits:
            cpu: 100m
            memory: 50Mi
"""
        exp = {
            "analysis_goal": "efficiency",
            "squeeze_optimizer": "llm",
            "mode": "squeeze",
            "up_recovery": True,
            "scaling_hint": "UP",
            "failure": {"failed": True},
            "config": {
                "cpu_request_m": 50,
                "mem_request_mib": 25,
                "deployment_replicas": 1,
                "hpa": {"max_replicas": 1},
            },
            "observed": {
                "cpu_util_pct": 140.0,
                "mem_util_pct": 245.0,
                "replicas": 1,
            },
            "workload": {"target_requests_per_second": 220},
            "slo": {"p95_latency_ms": 500},
        }
        result = {"deployment_yaml_new": llm_yaml, "evidence": []}
        with tempfile.TemporaryDirectory() as td:
            dep_path = Path(td) / "dep.yaml"
            hpa_path = Path(td) / "hpa.yaml"
            dep_path.write_text(dep)
            hpa_path.write_text(
                "apiVersion: autoscaling/v2\nkind: HorizontalPodAutoscaler\n"
                "spec:\n  minReplicas: 1\n  maxReplicas: 1\n"
            )
            _guard_llm_up_recovery_yaml(result, exp, dep_path, hpa_path)
        out = result["deployment_yaml_new"]
        self.assertIn("cpu: 50m", out)
        self.assertIn("memory: 25Mi", out)
        self.assertIn("replicas: 2", out)
        self.assertNotIn("guard.up_recovery:", " ".join(result.get("evidence") or []))

    def test_guard_clamps_replica_jump_over_one(self) -> None:
        from analysis.results import _guard_llm_up_recovery_yaml
        import tempfile
        from pathlib import Path

        exp = {
            "analysis_goal": "efficiency",
            "squeeze_optimizer": "llm",
            "mode": "squeeze",
            "up_recovery": True,
            "failure": {"failed": True},
            "config": {"deployment_replicas": 1, "hpa": {"max_replicas": 1}},
            "observed": {"replicas": 1, "replicas_max": 1},
        }
        result = {
            "deployment_yaml_new": """apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 4
  template:
    spec:
      containers:
      - name: web
        resources:
          requests:
            cpu: 50m
            memory: 25Mi
""",
            "hpa_yaml_new": """apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  minReplicas: 1
  maxReplicas: 4
""",
            "evidence": [],
        }
        with tempfile.TemporaryDirectory() as td:
            dep_path = Path(td) / "dep.yaml"
            hpa_path = Path(td) / "hpa.yaml"
            dep_path.write_text("apiVersion: apps/v1\nkind: Deployment\nspec:\n  replicas: 1\n")
            hpa_path.write_text(
                "apiVersion: autoscaling/v2\nkind: HorizontalPodAutoscaler\n"
                "spec:\n  minReplicas: 1\n  maxReplicas: 1\n"
            )
            _guard_llm_up_recovery_yaml(result, exp, dep_path, hpa_path)
        self.assertIn("replicas: 2", result["deployment_yaml_new"])
        self.assertIn("maxReplicas: 2", result["hpa_yaml_new"])
        self.assertIn("replicas_clamp", " ".join(result.get("evidence") or []))

    def test_guard_passes_through_near_pass_vertical(self) -> None:
        """Near-pass vertical sizing is LLM/prompt-owned; guard does not cap CPU/mem."""
        from analysis.results import _guard_llm_up_recovery_yaml
        import tempfile
        from pathlib import Path

        dep = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: web
        resources:
          requests:
            cpu: 98m
            memory: 49Mi
          limits:
            cpu: 147m
            memory: 74Mi
"""
        exp = {
            "analysis_goal": "efficiency",
            "squeeze_optimizer": "llm",
            "mode": "squeeze",
            "up_recovery": True,
            "scaling_hint": "UP",
            "failure": {"failed": True},
            "config": {
                "cpu_request_m": 98,
                "mem_request_mib": 49,
                "deployment_replicas": 1,
                "hpa": {"max_replicas": 1},
            },
            "observed": {
                "cpu_util_pct": 55.0,
                "mem_util_pct": 58.0,
                "replicas": 1,
                "latency_ms": {"p95": 533.0},
            },
            "workload": {"target_requests_per_second": 220},
            "slo": {"p95_latency_ms": 500},
        }
        result = {
            "deployment_yaml_new": """apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: web
        resources:
          requests:
            cpu: 113m
            memory: 57Mi
          limits:
            cpu: 170m
            memory: 86Mi
""",
            "evidence": [],
        }
        with tempfile.TemporaryDirectory() as td:
            dep_path = Path(td) / "dep.yaml"
            hpa_path = Path(td) / "hpa.yaml"
            dep_path.write_text(dep)
            hpa_path.write_text(
                "apiVersion: autoscaling/v2\nkind: HorizontalPodAutoscaler\n"
                "spec:\n  minReplicas: 1\n  maxReplicas: 1\n"
            )
            _guard_llm_up_recovery_yaml(result, exp, dep_path, hpa_path)
        out = result["deployment_yaml_new"]
        self.assertIn("cpu: 113m", out)
        self.assertIn("memory: 57Mi", out)


class TestFormulaUpRecovery(unittest.TestCase):
    def test_prefers_replica_on_throughput_collapse_any_target_rps(self) -> None:
        from analysis.results import _up_recovery_prefers_replica_step

        for target, achieved in ((220, 155), (400, 280), (180, 120)):
            exp = {
                "up_recovery": True,
                "failure": {"failed": True},
                "workload": {"target_requests_per_second": target},
                "config": {"deployment_replicas": 1, "hpa": {"max_replicas": 1}},
                "observed": {
                    "achieved_requests_per_second_target_window": float(achieved),
                    "cpu_util_pct": 90.0,
                    "mem_util_pct": 80.0,
                },
            }
            self.assertTrue(
                _up_recovery_prefers_replica_step(exp),
                f"expected replica at target={target} achieved={achieved}",
            )

    def test_up_recovery_signals_bottleneck_throughput(self) -> None:
        from analysis.results import _attach_up_recovery_signals

        exp = {
            "up_recovery": True,
            "failure": {"failed": True},
            "workload": {"target_requests_per_second": 300},
            "config": {"deployment_replicas": 1, "hpa": {"max_replicas": 1}},
            "observed": {
                "achieved_requests_per_second_target_window": 200.0,
                "latency_ms": {"p95": 600},
                "cpu_util_pct": 50.0,
                "mem_util_pct": 40.0,
            },
            "slo": {"p95_latency_ms": 500},
        }
        _attach_up_recovery_signals(exp)
        sig = exp["up_recovery_signals"]
        self.assertAlmostEqual(sig["throughput_ratio"], 200.0 / 300.0)
        self.assertEqual(sig["bottleneck"], "throughput")
        self.assertTrue(sig["prefer_replica_step"])

    def test_hpa_sync_after_vertical_does_not_pin_deployment_replicas(self) -> None:
        from analysis.results import _sync_up_recovery_hpa_after_vertical
        import yaml

        exp = {"up_recovery": True, "observed": {"replicas": 1, "replicas_max": 1}}
        dep_doc = yaml.safe_load(
            "apiVersion: apps/v1\nkind: Deployment\nspec:\n  replicas: 1\n"
        )
        hpa_doc = yaml.safe_load(
            "apiVersion: autoscaling/v2\nkind: HorizontalPodAutoscaler\n"
            "spec:\n  minReplicas: 1\n  maxReplicas: 2\n"
        )
        result: dict = {}
        _sync_up_recovery_hpa_after_vertical(result, exp, dep_doc, hpa_doc, 0.25)
        self.assertNotIn("deployment_yaml_new", result)
        self.assertEqual(dep_doc["spec"]["replicas"], 1)

    def test_prefers_replica_when_throughput_ok_but_not_saturated(self) -> None:
        from analysis.results import _up_recovery_prefers_replica_step

        exp = {
            "up_recovery": True,
            "failure": {"failed": True},
            "workload": {"target_requests_per_second": 260},
            "config": {
                "deployment_replicas": 1,
                "hpa": {"max_replicas": 1},
            },
            "observed": {
                "achieved_requests_per_second_target_window": 258.0,
                "cpu_util_pct": 69.0,
                "mem_util_pct": 84.0,
            },
        }
        self.assertTrue(_up_recovery_prefers_replica_step(exp))

    def test_replica_step_respects_max_replicas(self) -> None:
        from analysis.results import _apply_up_recovery_replica_step
        import os
        import tempfile
        from pathlib import Path

        os.environ["SQUEEZE_UP_RECOVERY_MAX_REPLICAS"] = "6"
        exp = {
            "up_recovery": True,
            "failure": {"failed": True},
            "workload": {"target_requests_per_second": 260},
            "config": {
                "deployment_replicas": 6,
                "hpa": {"max_replicas": 6},
            },
            "observed": {
                "achieved_requests_per_second_target_window": 260.0,
                "cpu_util_pct": 30.0,
                "mem_util_pct": 20.0,
            },
        }
        result: dict = {"evidence": []}
        with tempfile.TemporaryDirectory() as td:
            dep_path = Path(td) / "dep.yaml"
            hpa_path = Path(td) / "hpa.yaml"
            dep_path.write_text(
                "apiVersion: apps/v1\nkind: Deployment\nmetadata:\n  name: web\n"
                "spec:\n  replicas: 6\n"
            )
            hpa_path.write_text(
                "apiVersion: autoscaling/v2\nkind: HorizontalPodAutoscaler\n"
                "spec:\n  minReplicas: 1\n  maxReplicas: 6\n"
            )
            ok = _apply_up_recovery_replica_step(
                result, exp, dep_path, hpa_path, evidence_tag="test"
            )
        self.assertFalse(ok)

    def test_horizontal_step_sets_two_replicas(self) -> None:
        from analysis.results import _apply_formula_up_horizontal_step
        import tempfile
        from pathlib import Path

        exp = {
            "up_recovery": True,
            "failure": {"failed": True},
            "workload": {"target_requests_per_second": 260},
            "config": {
                "deployment_replicas": 1,
                "hpa": {"max_replicas": 1},
            },
            "observed": {
                "achieved_requests_per_second_target_window": 258.0,
                "cpu_util_pct": 69.0,
                "mem_util_pct": 84.0,
            },
        }
        dep = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: web
        resources:
          requests:
            cpu: 165m
            memory: 84Mi
"""
        result: dict = {"evidence": []}
        with tempfile.TemporaryDirectory() as td:
            dep_path = Path(td) / "dep.yaml"
            hpa_path = Path(td) / "hpa.yaml"
            dep_path.write_text(dep)
            hpa_path.write_text(
                "apiVersion: autoscaling/v2\nkind: HorizontalPodAutoscaler\n"
                "spec:\n  minReplicas: 1\n  maxReplicas: 1\n"
            )
            ok = _apply_formula_up_horizontal_step(result, exp, dep_path, hpa_path)
        self.assertTrue(ok)
        self.assertIn("replicas: 2", result["deployment_yaml_new"])
        self.assertIn("maxReplicas: 2", result["hpa_yaml_new"])

    def test_prefers_replica_when_mem_saturated_and_throughput_near_target(self) -> None:
        from analysis.results import _up_recovery_prefers_replica_step

        exp = {
            "up_recovery": True,
            "failure": {"failed": True},
            "workload": {"target_requests_per_second": 260},
            "config": {
                "deployment_replicas": 1,
                "hpa": {"max_replicas": 1},
            },
            "observed": {
                "achieved_requests_per_second_target_window": 256.4,
                "cpu_util_pct": 103.8,
                "mem_util_pct": 119.0,
            },
        }
        self.assertTrue(_up_recovery_prefers_replica_step(exp))

    def test_llm_guard_mem_saturated_combined_cpu_mem_replica(self) -> None:
        """230512 iter-2 shape: mem>100%, ach~target → vertical + 2 pods (not forced 1)."""
        from analysis.results import _guard_llm_up_recovery_yaml
        import tempfile
        from pathlib import Path

        exp = {
            "analysis_goal": "efficiency",
            "squeeze_optimizer": "llm",
            "mode": "squeeze",
            "up_recovery": True,
            "scaling_hint": "UP",
            "failure": {"failed": True},
            "workload": {"target_requests_per_second": 260},
            "config": {
                "cpu_request_m": 50,
                "mem_request_mib": 25,
                "deployment_replicas": 1,
                "hpa": {"max_replicas": 1},
            },
            "observed": {
                "achieved_requests_per_second_target_window": 256.4,
                "cpu_util_pct": 103.8,
                "mem_util_pct": 119.0,
                "replicas": 1,
                "replicas_max": 1,
                "telemetry": {"utilization_trustworthy": True},
            },
            "slo": {"p95_latency_ms": 500},
        }
        result = {
            "deployment_yaml_new": """apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: web
        resources:
          requests:
            cpu: 50m
            memory: 25Mi
          limits:
            cpu: 100m
            memory: 50Mi
""",
            "hpa_yaml_new": """apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  minReplicas: 1
  maxReplicas: 2
""",
            "evidence": [],
        }
        dep = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: web
        resources:
          requests:
            cpu: 50m
            memory: 25Mi
          limits:
            cpu: 100m
            memory: 50Mi
"""
        with tempfile.TemporaryDirectory() as td:
            dep_path = Path(td) / "dep.yaml"
            hpa_path = Path(td) / "hpa.yaml"
            dep_path.write_text(dep)
            hpa_path.write_text(
                "apiVersion: autoscaling/v2\nkind: HorizontalPodAutoscaler\n"
                "spec:\n  minReplicas: 1\n  maxReplicas: 1\n"
            )
            _guard_llm_up_recovery_yaml(result, exp, dep_path, hpa_path)
        out = result["deployment_yaml_new"]
        self.assertIn("replicas: 2", out)
        self.assertIn("cpu: 50m", out)
        self.assertIn("memory: 25Mi", out)
        self.assertNotIn("guard.up_recovery:", " ".join(result.get("evidence") or []))

    def test_llm_guard_passes_through_replica_first_yaml(self) -> None:
        """run-7 shape: ach below target at thin baseline → replica only, not 70m/35Mi."""
        from analysis.results import _guard_llm_up_recovery_yaml
        import tempfile
        from pathlib import Path

        dep = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: web
        resources:
          requests:
            cpu: 50m
            memory: 25Mi
          limits:
            cpu: 100m
            memory: 50Mi
"""
        exp = {
            "analysis_goal": "efficiency",
            "squeeze_optimizer": "llm",
            "mode": "squeeze",
            "up_recovery": True,
            "scaling_hint": "UP",
            "failure": {"failed": True},
            "workload": {"target_requests_per_second": 220},
            "config": {
                "cpu_request_m": 50,
                "mem_request_mib": 25,
                "deployment_replicas": 1,
                "hpa": {"max_replicas": 1},
            },
            "observed": {
                "achieved_requests_per_second_target_window": 165.0,
                "cpu_util_pct": 96.9,
                "mem_util_pct": 24.3,
                "replicas": 1,
            },
            "slo": {"p95_latency_ms": 500},
        }
        result = {
            "deployment_yaml_new": """apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: web
        resources:
          requests:
            cpu: 50m
            memory: 25Mi
          limits:
            cpu: 100m
            memory: 50Mi
""",
            "hpa_yaml_new": """apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  minReplicas: 1
  maxReplicas: 2
""",
            "evidence": [],
        }
        with tempfile.TemporaryDirectory() as td:
            dep_path = Path(td) / "dep.yaml"
            hpa_path = Path(td) / "hpa.yaml"
            dep_path.write_text(dep)
            hpa_path.write_text(
                "apiVersion: autoscaling/v2\nkind: HorizontalPodAutoscaler\n"
                "spec:\n  minReplicas: 1\n  maxReplicas: 1\n"
            )
            _guard_llm_up_recovery_yaml(result, exp, dep_path, hpa_path)
        out = result["deployment_yaml_new"]
        self.assertIn("replicas: 2", out)
        self.assertIn("cpu: 50m", out)
        self.assertIn("memory: 25Mi", out)
        self.assertNotIn("cpu: 70m", out)

    def test_llm_guard_passes_through_post_baseline_vertical(self) -> None:
        """After thin baseline, vertical + replica steps are LLM-owned."""
        from analysis.results import _guard_llm_up_recovery_yaml
        import tempfile
        from pathlib import Path

        exp = {
            "analysis_goal": "efficiency",
            "squeeze_optimizer": "llm",
            "mode": "squeeze",
            "up_recovery": True,
            "scaling_hint": "UP",
            "failure": {"failed": True},
            "workload": {"target_requests_per_second": 260},
            "config": {
                "cpu_request_m": 170,
                "mem_request_mib": 85,
                "deployment_replicas": 1,
                "hpa": {"max_replicas": 1},
            },
            "observed": {
                "achieved_requests_per_second_target_window": 258.0,
                "cpu_util_pct": 57.0,
                "mem_util_pct": 96.0,
                "replicas": 1,
                "replicas_max": 1,
            },
            "slo": {"p95_latency_ms": 500},
        }
        result = {
            "deployment_yaml_new": """apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: web
        resources:
          requests:
            cpu: 196m
            memory: 98Mi
""",
            "hpa_yaml_new": """apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  minReplicas: 1
  maxReplicas: 2
""",
            "evidence": [],
        }
        with tempfile.TemporaryDirectory() as td:
            dep_path = Path(td) / "dep.yaml"
            hpa_path = Path(td) / "hpa.yaml"
            dep_path.write_text(
                "apiVersion: apps/v1\nkind: Deployment\nmetadata:\n  name: web\n"
                "spec:\n  replicas: 1\n  template:\n    spec:\n      containers:\n"
                "      - name: web\n        resources:\n          requests:\n"
                "            cpu: 170m\n            memory: 85Mi\n"
            )
            hpa_path.write_text(
                "apiVersion: autoscaling/v2\nkind: HorizontalPodAutoscaler\n"
                "spec:\n  minReplicas: 1\n  maxReplicas: 1\n"
            )
            _guard_llm_up_recovery_yaml(result, exp, dep_path, hpa_path)
        self.assertIn("replicas: 2", result["deployment_yaml_new"])
        self.assertIn("cpu: 196m", result["deployment_yaml_new"])


class TestUpDemoIsolation(unittest.TestCase):
    def test_up_demo_iter1_fail_enters_recovery(self) -> None:
        self.assertEqual(
            _iter1_up_recovery_gate(
                profile="up_demo",
                status_1="FAIL",
                scaling_hint="UP",
                failed=True,
                has_diff=True,
            ),
            "up_recovery",
        )

    def test_fail_up_hint_down_yaml_vetoed_when_not_down_boundary(self) -> None:
        exp = {
            "squeeze_optimizer": "llm",
            "analysis_goal": "efficiency",
            "mode": "squeeze",
            "scaling_hint": "UP",
            "failure": {"failed": True},
            "config": {
                "cpu_request_m": 50,
                "mem_request_mib": 25,
                "deployment_replicas": 1,
            },
            "observed": {},
        }
        down_dep = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: web
        resources:
          requests:
            cpu: 25m
            memory: 10Mi
"""
        result = {"deployment_yaml_new": down_dep, "hpa_yaml_new": "", "evidence": []}
        with mock.patch.dict(
            os.environ, {"SQUEEZE_LLM_DOWN_BOUNDARY": "0"}, clear=False
        ):
            out = _postprocess_llm_result(result, exp)
        self.assertEqual((out.get("deployment_yaml_new") or "").strip(), "")


if __name__ == "__main__":
    unittest.main()
