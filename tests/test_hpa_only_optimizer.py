"""HPA-only compare arm helpers."""
from analysis.results import _hpa_only_result, _resolve_squeeze_optimizer


def test_resolve_squeeze_optimizer_hpa():
    assert _resolve_squeeze_optimizer({"squeeze_optimizer": "hpa"}, None) == "hpa"


def test_hpa_only_result_empty_yaml():
    exp = {
        "observed": {"replicas": 3, "replicas_max": 4},
        "config": {"cpu_request_m": 50, "mem_request_mib": 25},
        "failure": {"failed": True},
    }
    r = _hpa_only_result(exp)
    assert r["deployment_yaml_new"] == ""
    assert r["hpa_yaml_new"] == ""
    assert "HPA-only" in r["report"]
