"""Regression: up_demo fixes must not alter down_demo squeeze behavior."""
from __future__ import annotations

import os
import unittest
from unittest import mock

from analysis.results import (
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
    def test_guard_mem_saturated_uses_metric_step_from_file(self) -> None:
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
            cpu: 100m
            memory: 50Mi
          limits:
            cpu: 100m
            memory: 50Mi
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
        self.assertIn("cpu: 70m", out)
        self.assertIn("memory: 35Mi", out)
        self.assertNotIn("cpu: 100m", out.split("requests:")[1].split("limits:")[0])

    def test_guard_near_pass_caps_llm_overshoot(self) -> None:
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
            cpu: 138m
            memory: 70Mi
          limits:
            cpu: 200m
            memory: 100Mi
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
        self.assertNotIn("cpu: 138m", out)


class TestFormulaUpRecovery(unittest.TestCase):
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
  replicas: 1
  template:
    spec:
      containers:
      - name: web
        resources:
          requests:
            cpu: 70m
            memory: 35Mi
          limits:
            cpu: 105m
            memory: 53Mi
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
        ev = " ".join(result.get("evidence") or [])
        self.assertIn("replicas: 2", out)
        self.assertIn("axes=cpu,mem,replica", ev)
        self.assertIn("maxReplicas: 2", result.get("hpa_yaml_new") or "")
        self.assertNotIn("cpu: 50m", out.split("requests:")[1])
        self.assertNotIn("memory: 25Mi", out.split("requests:")[1])

    def test_llm_guard_applies_replica_step_when_throughput_ok(self) -> None:
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
  replicas: 1
  template:
    spec:
      containers:
      - name: web
        resources:
          requests:
            cpu: 320m
            memory: 200Mi
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
        ev = " ".join(result.get("evidence") or [])
        self.assertTrue(
            "guard.llm.up_recovery_replica_step" in ev or "axes=cpu,mem,replica" in ev,
            ev,
        )


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
