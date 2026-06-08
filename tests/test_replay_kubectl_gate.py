import unittest


def replay_applies_kubectl(*, base_url: str | None, k8s_apply_enabled: bool) -> bool:
    """Mirror start.py _replay_trajectory_pipeline kubectl gate."""
    skip_kubectl_apply = bool(base_url) and not k8s_apply_enabled
    return k8s_apply_enabled and not skip_kubectl_apply


class ReplayKubectlGateTests(unittest.TestCase):
    def test_in_cluster_base_url_still_applies(self) -> None:
        self.assertTrue(
            replay_applies_kubectl(
                base_url="http://web.svastik.svc.cluster.local:8080",
                k8s_apply_enabled=True,
            )
        )

    def test_external_only_skips_kubectl(self) -> None:
        self.assertFalse(
            replay_applies_kubectl(
                base_url="http://localhost:8080",
                k8s_apply_enabled=False,
            )
        )


if __name__ == "__main__":
    unittest.main()
