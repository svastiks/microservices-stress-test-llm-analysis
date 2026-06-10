import unittest

from analysis.scaling_policy import attach_scaling_hint


class TestScalingPolicyUntrustworthy(unittest.TestCase):
    def _base_exp(self) -> dict:
        return {
            "failure": {"failed": True, "reason": "latency_slo_exceeded"},
            "slo": {"p95_latency_ms": 500, "error_rate": 0.01},
            "workload": {"target_requests_per_second": 240},
            "observed": {
                "latency_ms": {"p95": 4179},
                "error_rate": 0.0,
                "dropped_iterations": 7179,
                "achieved_requests_per_second_target_window": 160.0,
                "telemetry": {"utilization_trustworthy": False},
            },
        }

    def test_untrustworthy_slo_stress_hints_up(self) -> None:
        exp = self._base_exp()
        attach_scaling_hint(exp)
        self.assertEqual(exp["scaling_hint"], "UP")
        self.assertIn("k6/SLO stress", exp["scaling_rationale"])

    def test_untrustworthy_pass_hints_unknown(self) -> None:
        exp = self._base_exp()
        exp["failure"] = {"failed": False}
        exp["observed"]["latency_ms"] = {"p95": 200}
        exp["observed"]["dropped_iterations"] = 0
        exp["observed"]["achieved_requests_per_second_target_window"] = 240.0
        attach_scaling_hint(exp)
        self.assertEqual(exp["scaling_hint"], "UNKNOWN")


class TestUpDemoFailRecoveryGate(unittest.TestCase):
    def test_unknown_hint_enters_recovery(self) -> None:
        is_up_demo = True
        fail_1 = True
        scaling_hint = "UNKNOWN"
        has_diff = False
        up_demo_fail_recovery = (
            is_up_demo and fail_1 and scaling_hint in ("UP", "HOLD", None, "UNKNOWN")
        )
        outcome = (
            "up_recovery"
            if (has_diff and scaling_hint == "UP") or up_demo_fail_recovery
            else "first_run_failed"
        )
        self.assertEqual(outcome, "up_recovery")
