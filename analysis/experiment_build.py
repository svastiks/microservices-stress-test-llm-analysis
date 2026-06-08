"""
Build combined experiment JSON from k6 summary + config from YAML + optional Prometheus observed.
"""
import json
import math
import os
from pathlib import Path
from typing import Any
from datetime import datetime, timezone

import yaml
import uuid

from .cost_model import cost_from_config

REPO_ROOT = Path(__file__).resolve().parent.parent


def parse_cpu_millicores(val: str | int | float | None) -> int:
    """Parse Kubernetes CPU (e.g. '100m', '112.5m', '1') to integer millicores."""
    if val is None:
        return 0
    s = str(val).strip()
    if not s:
        return 0
    if s.endswith("m"):
        v = float(s[:-1])
        return max(1, int(v) if v == int(v) else math.ceil(v))
    v = float(s) * 1000
    return max(1, int(v) if v == int(v) else math.ceil(v))


def format_cpu_millicores(millicores: int) -> str:
    return f"{max(1, int(millicores))}m"


def parse_memory_mib(val: str | int | float | None) -> int:
    """Parse Kubernetes memory to integer MiB."""
    if val is None:
        return 0
    s = str(val).strip()
    if not s:
        return 0
    if s.endswith("Mi"):
        v = float(s[:-2])
        return max(1, int(v) if v == int(v) else math.ceil(v))
    if s.endswith("Gi"):
        return max(1, int(round(float(s[:-2]) * 1024)))
    if s.endswith("Ki"):
        return max(1, int(round(float(s[:-2]) / 1024)))
    return max(1, int(s))  # assume bytes, rough


def format_memory_mib(mib: int) -> str:
    return f"{max(1, int(mib))}Mi"


def _parse_cpu(s: str) -> int:
    return parse_cpu_millicores(s)


def _parse_memory_mib(s: str) -> int:
    return parse_memory_mib(s)


def normalize_deployment_yaml_resources(yaml_text: str) -> tuple[str, list[str]]:
    """Round fractional LLM CPU/memory quantities to valid Kubernetes strings."""
    if not yaml_text.strip():
        return yaml_text, []
    try:
        doc = yaml.safe_load(yaml_text)
    except Exception:
        return yaml_text, []
    if not isinstance(doc, dict) or doc.get("kind") != "Deployment":
        return yaml_text, []
    notes: list[str] = []
    spec = doc.get("spec") or {}
    template = (spec.get("template") or {}).get("spec") or {}
    for container in template.get("containers") or []:
        res = container.get("resources") or {}
        for block_name in ("requests", "limits"):
            block = res.get(block_name) or {}
            if not isinstance(block, dict):
                continue
            if "cpu" in block and block["cpu"] is not None:
                old = block["cpu"]
                new_m = parse_cpu_millicores(old)
                new = format_cpu_millicores(new_m)
                if str(old) != new:
                    notes.append(f"{block_name}.cpu: {old} -> {new}")
                    block["cpu"] = new
            if "memory" in block and block["memory"] is not None:
                old = block["memory"]
                new_mib = parse_memory_mib(old)
                new = format_memory_mib(new_mib)
                if str(old) != new:
                    notes.append(f"{block_name}.memory: {old} -> {new}")
                    block["memory"] = new
    if not notes:
        return yaml_text, notes
    dump_kw = {
        "default_flow_style": False,
        "sort_keys": False,
        "allow_unicode": True,
    }
    return yaml.safe_dump(doc, **dump_kw), notes


def get_config_from_yaml(deployment_path: Path, hpa_path: Path) -> dict:
    """Read deployment and HPA YAML files and return config block for experiment JSON."""
    config = {
        "cpu_request_m": 0,
        "cpu_limit_m": 0,
        "mem_request_mib": 0,
        "mem_limit_mib": 0,
        "deployment_replicas": 0,
        "hpa": {"min_replicas": 0, "max_replicas": 0, "target_cpu_util_pct": 0},
    }
    if deployment_path.exists():
        with open(deployment_path) as f:
            docs = list(yaml.safe_load_all(f)) or []
        for doc in docs:
            if doc and doc.get("kind") == "Deployment":
                spec = doc.get("spec", {}) or {}
                if spec.get("replicas") is not None:
                    config["deployment_replicas"] = int(spec["replicas"])
                template = spec.get("template", {}) or {}
                containers = (template.get("spec") or {}).get("containers") or []
                if containers:
                    c = containers[0]
                    r = c.get("resources", {}) or {}
                    req = r.get("requests", {}) or {}
                    lim = r.get("limits", {}) or {}
                    config["cpu_request_m"] = _parse_cpu(req.get("cpu", ""))
                    config["cpu_limit_m"] = _parse_cpu(lim.get("cpu", ""))
                    config["mem_request_mib"] = _parse_memory_mib(req.get("memory", ""))
                    config["mem_limit_mib"] = _parse_memory_mib(lim.get("memory", ""))
                break
    if hpa_path.exists():
        with open(hpa_path) as f:
            doc = yaml.safe_load(f)
        if doc and doc.get("kind") == "HorizontalPodAutoscaler":
            spec = doc.get("spec", {}) or {}
            config["hpa"]["min_replicas"] = spec.get("minReplicas") or 0
            config["hpa"]["max_replicas"] = spec.get("maxReplicas") or 0
            for m in spec.get("metrics", []) or []:
                if (m.get("resource") or {}).get("name") == "cpu":
                    config["hpa"]["target_cpu_util_pct"] = (
                        (m.get("resource") or {}).get("target") or {}
                    ).get("averageUtilization") or 0
                    break
    return config


def apply_config_to_managed_yaml(
    config: dict,
    deployment_yaml_path: Path,
    hpa_yaml_path: Path,
) -> None:
    """Write deployment/HPA CPU, memory, replicas from an experiment config block."""
    if not deployment_yaml_path.is_file():
        raise FileNotFoundError(deployment_yaml_path)
    dep_doc = yaml.safe_load(deployment_yaml_path.read_text())
    if not isinstance(dep_doc, dict) or dep_doc.get("kind") != "Deployment":
        raise ValueError(f"Not a Deployment: {deployment_yaml_path}")
    hpa_doc = None
    if hpa_yaml_path.is_file():
        hpa_doc = yaml.safe_load(hpa_yaml_path.read_text())

    cpu_req = int(config.get("cpu_request_m") or 0)
    cpu_lim = int(config.get("cpu_limit_m") or cpu_req)
    mem_req = int(config.get("mem_request_mib") or 0)
    mem_lim = int(config.get("mem_limit_mib") or mem_req)
    repl = max(1, int(config.get("deployment_replicas") or 1))

    spec = dep_doc.setdefault("spec", {})
    spec["replicas"] = repl
    tmpl = spec.setdefault("template", {}).setdefault("spec", {})
    containers = tmpl.get("containers") or []
    if not containers:
        raise ValueError(f"No containers in {deployment_yaml_path}")
    c0 = containers[0]
    res = c0.setdefault("resources", {})
    req = res.setdefault("requests", {})
    lim = res.setdefault("limits", {})
    req["cpu"] = format_cpu_millicores(cpu_req)
    lim["cpu"] = format_cpu_millicores(cpu_lim)
    req["memory"] = format_memory_mib(mem_req)
    lim["memory"] = format_memory_mib(mem_lim)

    dump_kw = {
        "default_flow_style": False,
        "sort_keys": False,
        "allow_unicode": True,
    }
    deployment_yaml_path.write_text(yaml.safe_dump(dep_doc, **dump_kw))

    hpa_cfg = config.get("hpa") or {}
    if isinstance(hpa_doc, dict) and hpa_doc.get("kind") == "HorizontalPodAutoscaler":
        hspec = hpa_doc.setdefault("spec", {})
        min_r = max(1, int(hpa_cfg.get("min_replicas") or repl))
        max_r = max(min_r, int(hpa_cfg.get("max_replicas") or repl))
        hspec["minReplicas"] = min(min_r, repl)
        hspec["maxReplicas"] = min(max_r, repl)
        target = int(hpa_cfg.get("target_cpu_util_pct") or 60)
        metrics = hspec.setdefault("metrics", [])
        if metrics and isinstance(metrics[0], dict):
            res_m = metrics[0].setdefault("resource", {})
            res_m["name"] = "cpu"
            tgt = res_m.setdefault("target", {})
            tgt["type"] = "Utilization"
            tgt["averageUtilization"] = target
        hpa_yaml_path.write_text(yaml.safe_dump(hpa_doc, **dump_kw))


def from_k6_summary(
    summary: dict, slo: dict | None = None, workload: dict | None = None
) -> tuple[dict, dict]:
    """Build observed (k6 part) and failure from k6 summary."""
    slo = slo or {}
    workload = workload or {}
    p95_limit = slo.get("p95_latency_ms") or 2000
    error_limit = slo.get("error_rate") or 0.05
    m = summary.get("metrics", {}) or {}
    hr = m.get("http_reqs", {}) or {}
    hrd = m.get("http_req_duration", {}) or {}
    hrf = m.get("http_req_failed", {}) or {}
    dropped = m.get("dropped_iterations", {}) or {}
    count = int(hr.get("count", 0))
    rate = float(hr.get("rate", 0))
    duration_s = count / rate if rate else 0
    workload_duration_s = float(workload.get("duration_s") or 0)
    achieved_target_window_rps = (
        (count / workload_duration_s) if workload_duration_s > 0 else rate
    )

    err_val = float(hrf.get("value", 0) or 0)
    observed = {
        "total_requests": count,
        "observed_duration_s": round(duration_s, 1),
        "achieved_requests_per_second": round(rate, 1),
        "achieved_requests_per_second_target_window": round(achieved_target_window_rps, 1),
        "dropped_iterations": int(dropped.get("count", 0) or 0),
        "latency_ms": {
            "p95": round(hrd.get("p(95)", 0), 0),
            "p99": round(hrd.get("p(99)", 0), 0),
        },
        "error_rate": round(err_val, 4),
    }

    failure = {"failed": False, "reason": ""}
    p95_actual = observed["latency_ms"]["p95"]
    if p95_actual > p95_limit:
        failure["failed"] = True
        failure["reason"] = "p95_slo_violation"
    elif observed["error_rate"] > error_limit:
        failure["failed"] = True
        failure["reason"] = "error_rate_slo_violation"
    return observed, failure


def squeeze_cpu_util_fail_pct() -> float:
    """PASS/FAIL threshold for observed CPU utilization in squeeze mode (default 95%)."""
    return float(os.environ.get("SQUEEZE_CPU_UTIL_FAIL_PCT", "95"))


def squeeze_cpu_util_gate_field() -> str:
    """Metric used for squeeze CPU PASS/FAIL gate: request (HPA-aligned) or limit."""
    gate = os.environ.get("SQUEEZE_CPU_UTIL_GATE", "request").strip().lower()
    return "cpu_util_pct" if gate == "limit" else "cpu_util_request_pct"


def apply_squeeze_cpu_util_failure(payload: dict) -> None:
    """
    In squeeze mode, high CPU utilization ends the PASS frontier (same class as p95 SLO breach).
    Requires trustworthy Prometheus telemetry.
    Default gate uses request-relative cpu_util_request_pct (HPA-aligned).
    Set SQUEEZE_CPU_UTIL_GATE=limit to restore limit-relative behavior.
    """
    if payload.get("mode") != "squeeze":
        return
    failure = payload.setdefault("failure", {"failed": False, "reason": ""})
    if failure.get("failed"):
        return
    observed = payload.get("observed") or {}
    tel = observed.get("telemetry") or {}
    if not tel.get("utilization_trustworthy"):
        return
    field = squeeze_cpu_util_gate_field()
    cpu = float(observed.get(field) or observed.get("cpu_util_pct") or 0.0)
    threshold = squeeze_cpu_util_fail_pct()
    if cpu > threshold:
        failure["failed"] = True
        failure["reason"] = "cpu_utilization_exceeded"


def _cost_from_config(config: dict, observed: dict) -> dict:
    """Compute provisioned cost from replicas and per-pod requests (see cost_model.py)."""
    return cost_from_config(config, observed)


def build_experiment_payload(
    run_dir: Path,
    k6_summary_path: Path,
    deployment_yaml_path: Path,
    hpa_yaml_path: Path,
    experiment_config: dict | None = None,
    observed_override: dict | None = None,
) -> dict:
    """
    Build full experiment JSON.
    experiment_config: optional { experiment_id, service, endpoint, workload, slo }.
    observed_override: optional runtime metrics from Prometheus (replicas, cpu_util_pct, mem_util_pct, oom_kills, cpu_util_to_limit, replicas_at_start, scaled_during_test).
    """
    if not k6_summary_path.exists():
        raise FileNotFoundError(f"No k6 summary at {k6_summary_path}")
    with open(k6_summary_path) as f:
        summary = json.load(f)

    exp = experiment_config or {}
    slo = exp.get("slo") or {}
    observed_k6, failure = from_k6_summary(summary, slo, exp.get("workload") or {})
    if exp.get("k6_thresholds_crossed"):
        failure["failed"] = True
        failure["reason"] = failure.get("reason") or "k6_thresholds_crossed"

    config = get_config_from_yaml(deployment_yaml_path, hpa_yaml_path)
    if exp.get("config"):
        config = {**config, **exp["config"]}

    label = exp.get("experiment_id", "run")
    run_suffix = (
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        + "-"
        + uuid.uuid4().hex[:8]
    )

    payload: dict[str, Any] = {
        "experiment_id": f"{label}-{run_suffix}",
        "mode": exp.get("mode"),
        "analysis_goal": exp.get("analysis_goal"),
        "service": exp.get("service", "stress-service"),
        "endpoint": exp.get("endpoint", "POST /login"),
        "config": config,
        "workload": exp.get("workload", {}),
        "slo": exp.get("slo", {}),
        "observed": observed_k6,
        "failure": failure,
    }

    if exp.get("up_recovery"):
        payload["up_recovery"] = True

    if observed_override:
        payload["observed"].update(observed_override)

    # replicas_at_start from file if present (captured before k6, at the start)
    replicas_at_start_path = run_dir / "replicas_at_start.txt"
    if replicas_at_start_path.exists():
        try:
            payload["observed"]["replicas_at_start"] = int(
                replicas_at_start_path.read_text().strip()
            )
            r = payload["observed"].get("replicas", 0)
            start = payload["observed"]["replicas_at_start"]
            payload["observed"]["scaled_during_test"] = r > start
        except (ValueError, OSError):
            pass

    apply_squeeze_cpu_util_failure(payload)
    payload["cost"] = _cost_from_config(payload.get("config") or {}, payload.get("observed") or {})
    return payload
