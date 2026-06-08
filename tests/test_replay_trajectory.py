import unittest

from analysis.replay_trajectory import compare_matched_configs, compare_trajectories, config_key


class ReplayTrajectoryTests(unittest.TestCase):
    def test_compare_trajectories_markdown(self) -> None:
        source = [
            {
                "cpu_request_m": 92,
                "mem_request_mib": 46,
                "replicas": 4,
                "status": "FAIL",
                "cpu_usage_avg_m": 360.2,
                "cpu_util_request_pct": 97.9,
            }
        ]
        replay = [
            {
                "cpu_request_m": 92,
                "mem_request_mib": 46,
                "replicas": 4,
                "status": "FAIL",
                "cpu_usage_avg_m": 355.0,
                "cpu_util_request_pct": 96.2,
            }
        ]
        md = compare_trajectories(source, replay)
        self.assertIn("Status match", md)
        self.assertIn("92/46/4", md)
        self.assertIn("yes", md)


    def test_matched_configs_baseline(self) -> None:
        key = config_key({"cpu_request_m": 150, "mem_request_mib": 75, "replicas": 5})
        self.assertEqual(key, "150/75/5")
        fs = [{"cpu_request_m": 150, "mem_request_mib": 75, "replicas": 5, "status": "PASS", "cpu_util_request_pct": 34}]
        ls = [{"cpu_request_m": 150, "mem_request_mib": 75, "replicas": 5, "status": "PASS", "cpu_util_request_pct": 48}]
        md = compare_matched_configs(fs, fs, ls, ls)
        self.assertIn("150/75/5", md)
        self.assertIn("Configs tested by both arms", md)


if __name__ == "__main__":
    unittest.main()
