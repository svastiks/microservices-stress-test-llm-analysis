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

    def test_user_prompt_replica_first_at_thin_baseline(self) -> None:
        prompt = build_user_prompt(self._thin_up_exp(), "deployment yaml", mode="squeeze")
        self.assertIn("REPLICA-FIRST", prompt)
        self.assertIn("prefer_replica_step=true", prompt)
        self.assertIn("keeping CPU and memory requests/limits **identical**", prompt)
        self.assertIn("Do NOT propose 70m/35Mi", prompt)

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
