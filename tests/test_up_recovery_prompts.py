import unittest

from analysis.prompts import EFFICIENCY_LLM_ONLY_SQUEEZE_PROMPT, build_user_prompt
from analysis.results import _attach_up_recovery_signals


class TestUpRecoveryPrompts(unittest.TestCase):
    def _thin_up_exp(self) -> dict:
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
                "replicas_max": 1,
                "latency_ms": {"p95": 600},
            },
            "slo": {"p95_latency_ms": 500},
        }
        _attach_up_recovery_signals(exp)
        return exp

    def test_system_prompt_one_axis_up_recovery(self) -> None:
        self.assertIn("One axis per iteration", EFFICIENCY_LLM_ONLY_SQUEEZE_PROMPT)
        self.assertIn("thin baseline", EFFICIENCY_LLM_ONLY_SQUEEZE_PROMPT.lower())
        self.assertIn("UP RECOVERY FRONTIER EXAMPLE", EFFICIENCY_LLM_ONLY_SQUEEZE_PROMPT)
        self.assertIn("135m/66Mi", EFFICIENCY_LLM_ONLY_SQUEEZE_PROMPT)

    def test_user_prompt_replica_first_at_thin_baseline(self) -> None:
        prompt = build_user_prompt(self._thin_up_exp(), "deployment yaml", mode="squeeze")
        self.assertIn("REPLICA-FIRST", prompt)
        self.assertIn("prefer_replica_step=true", prompt)
        self.assertIn("keeping CPU and memory requests/limits **identical**", prompt)
        self.assertIn("Do NOT propose 70m/35Mi", prompt)

    def test_user_prompt_cpu_gate_uses_request_pct(self) -> None:
        prompt = build_user_prompt(self._thin_up_exp(), "deployment yaml", mode="squeeze")
        self.assertIn("cpu_util_request_pct", prompt)
        self.assertIn("do NOT compare it to HPA target_cpu_util_pct", prompt)

    def test_user_prompt_cpu_gate_only_mandatory_vertical(self) -> None:
        exp = self._thin_up_exp()
        exp["config"]["deployment_replicas"] = 2
        exp["config"]["hpa"]["max_replicas"] = 2
        exp["config"]["cpu_request_m"] = 58
        exp["config"]["mem_request_mib"] = 25
        exp["observed"]["replicas"] = 2
        exp["observed"]["replicas_max"] = 2
        exp["observed"]["latency_ms"]["p95"] = 214
        exp["observed"]["cpu_util_request_pct"] = 176.1
        exp["observed"]["cpu_util_pct"] = 88.8
        exp["failure"] = {"failed": True, "reason": "cpu_utilization_exceeded"}
        _attach_up_recovery_signals(exp)
        prompt = build_user_prompt(exp, "deployment yaml", mode="squeeze")
        self.assertIn("CPU-GATE-ONLY UP (mandatory", prompt)
        self.assertIn("coupled", prompt.lower())
        self.assertIn("hold spec.replicas", prompt)
        self.assertNotIn("REPLICA-FIRST (mandatory", prompt)

    def test_user_prompt_cpu_gate_precision_near_threshold(self) -> None:
        exp = self._thin_up_exp()
        exp["config"]["deployment_replicas"] = 2
        exp["config"]["hpa"]["max_replicas"] = 2
        exp["config"]["cpu_request_m"] = 129
        exp["config"]["mem_request_mib"] = 66
        exp["observed"]["replicas"] = 2
        exp["observed"]["replicas_max"] = 2
        exp["observed"]["latency_ms"]["p95"] = 224
        exp["observed"]["cpu_util_request_pct"] = 96.0
        exp["observed"]["mem_util_pct"] = 15.4
        exp["failure"] = {"failed": True, "reason": "cpu_utilization_exceeded"}
        _attach_up_recovery_signals(exp)
        prompt = build_user_prompt(exp, "deployment yaml", mode="squeeze")
        self.assertIn("CPU-GATE PRECISION UP (mandatory", prompt)
        self.assertIn("CPU request only", prompt)
        self.assertIn("135m", prompt)
        self.assertIn("hold memory", prompt.lower())
        self.assertNotIn("CPU-GATE-ONLY UP (mandatory", prompt)

    def test_user_prompt_no_replica_first_after_vertical(self) -> None:
        exp = self._thin_up_exp()
        exp["config"]["cpu_request_m"] = 98
        exp["config"]["mem_request_mib"] = 49
        _attach_up_recovery_signals(exp)
        prompt = build_user_prompt(exp, "deployment yaml", mode="squeeze")
        self.assertNotIn("REPLICA-FIRST (mandatory", prompt)

    def test_user_prompt_fat_start_down_mandatory_replica_drop(self) -> None:
        exp = {
            "analysis_goal": "efficiency",
            "squeeze_optimizer": "llm",
            "mode": "squeeze",
            "scaling_hint": "DOWN",
            "failure": {"failed": False},
            "workload": {"target_requests_per_second": 35},
            "config": {
                "cpu_request_m": 150,
                "mem_request_mib": 75,
                "deployment_replicas": 5,
                "hpa": {"max_replicas": 5},
            },
            "observed": {
                "cpu_util_pct": 12.0,
                "mem_util_pct": 18.0,
                "replicas": 5,
                "replicas_max": 5,
                "latency_ms": {"p95": 80},
            },
            "cost": {"cost_score": 0.71},
            "slo": {"p95_latency_ms": 500},
        }
        prompt = build_user_prompt(exp, "deployment yaml", mode="squeeze")
        self.assertIn("FAT-START DOWN (mandatory", prompt)
        self.assertIn("spec.replicas=4", prompt)
        self.assertIn("FORBIDDEN", prompt)
        self.assertNotIn("Phase 1: hold replicas", prompt)
