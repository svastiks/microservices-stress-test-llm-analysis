"""Apply current YAMLs with kubectl and wait for rollout."""
import json
import subprocess
import time
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent


def _kubectl_get_json(kind: str, name: str, namespace: str) -> dict:
    out = subprocess.check_output(
        ["kubectl", "-n", namespace, "get", kind, name, "-o", "json"],
        text=True,
    )
    return json.loads(out)


def kubectl_apply(
    deployment_yaml_path: Path,
    hpa_yaml_path: Path,
    repo_root: Path | None = None,
) -> None:
    """Run kubectl apply -f for deployment and HPA."""
    root = repo_root or REPO_ROOT
    print("kubectl apply (deployment + hpa)...", flush=True)
    subprocess.run(
        [
            "kubectl",
            "apply",
            "-f",
            str(deployment_yaml_path),
            "-f",
            str(hpa_yaml_path),
        ],
        cwd=root,
        check=True,
    )


def ensure_up_demo_thin_baseline(
    *,
    deployment_yaml_path: Path,
    hpa_yaml_path: Path,
    deployment_name: str,
    namespace: str,
    repo_root: Path | None = None,
    timeout_s: int = 300,
) -> None:
    """Rewrite deployment/HPA YAML to a single-replica, non-scaling HPA and apply.

    Used for profile ``up_demo`` so iteration 1 starts under-provisioned at the target
    load (HPA cannot add pods). Without this, a warm cluster often passes iteration 1
    and the DOWN squeeze mis-fires.
    """
    root = repo_root or REPO_ROOT
    dep = yaml.safe_load(deployment_yaml_path.read_text())
    hpa = yaml.safe_load(hpa_yaml_path.read_text())
    if (dep or {}).get("kind") != "Deployment":
        raise ValueError(f"expected Deployment YAML at {deployment_yaml_path}")
    if (hpa or {}).get("kind") != "HorizontalPodAutoscaler":
        raise ValueError(f"expected HorizontalPodAutoscaler YAML at {hpa_yaml_path}")
    dep.setdefault("spec", {})["replicas"] = 1
    hpa.setdefault("spec", {})["minReplicas"] = 1
    hpa["spec"]["maxReplicas"] = 1
    _dump_kw = {
        "default_flow_style": False,
        "sort_keys": False,
        "allow_unicode": True,
    }
    deployment_yaml_path.write_text(yaml.dump(dep, **_dump_kw))
    hpa_yaml_path.write_text(yaml.dump(hpa, **_dump_kw))
    print(
        "[up_demo] thin baseline: replicas=1, HPA min=max=1; kubectl apply...",
        flush=True,
    )
    kubectl_apply(deployment_yaml_path, hpa_yaml_path, root)
    wait_rollout(deployment_name=deployment_name, timeout_s=timeout_s, namespace=namespace)
    wait_single_replica_steady(deployment_name=deployment_name, namespace=namespace, timeout_s=timeout_s)
    print("[up_demo] thin baseline ready.", flush=True)


def wait_single_replica_steady(
    *,
    deployment_name: str,
    namespace: str,
    timeout_s: int = 300,
    steady_checks: int = 3,
    check_interval_s: float = 2.0,
) -> None:
    """Wait until deployment + HPA are stably pinned at exactly one replica."""
    hpa_name = f"{deployment_name}-hpa"
    deadline = time.time() + timeout_s
    stable_hits = 0
    attempt = 0
    while time.time() < deadline:
        attempt += 1
        dep = _kubectl_get_json("deployment", deployment_name, namespace)
        hpa = _kubectl_get_json("hpa", hpa_name, namespace)
        dep_spec = (dep.get("spec") or {}).get("replicas")
        dep_status = dep.get("status") or {}
        updated = dep_status.get("updatedReplicas", 0)
        ready = dep_status.get("readyReplicas", 0)
        available = dep_status.get("availableReplicas", 0)
        observed = dep_status.get("observedGeneration")
        generation = dep.get("metadata", {}).get("generation")
        hpa_spec = hpa.get("spec") or {}
        hpa_status = hpa.get("status") or {}
        hpa_min = hpa_spec.get("minReplicas")
        hpa_max = hpa_spec.get("maxReplicas")
        hpa_current = hpa_status.get("currentReplicas")
        hpa_desired = hpa_status.get("desiredReplicas")
        is_steady = (
            dep_spec == 1
            and updated == 1
            and ready == 1
            and available == 1
            and observed == generation
            and hpa_min == 1
            and hpa_max == 1
            and hpa_current == 1
            and hpa_desired == 1
        )
        print(
            "[up_demo] baseline check "
            f"attempt={attempt} dep(spec={dep_spec},updated={updated},ready={ready},avail={available},gen={observed}/{generation}) "
            f"hpa(min={hpa_min},max={hpa_max},current={hpa_current},desired={hpa_desired}) "
            f"steady={is_steady}",
            flush=True,
        )
        if is_steady:
            stable_hits += 1
            if stable_hits >= steady_checks:
                print(
                    f"[up_demo] baseline steady for {stable_hits} consecutive checks; proceeding.",
                    flush=True,
                )
                return
        else:
            stable_hits = 0
        time.sleep(check_interval_s)
    raise TimeoutError(
        f"Timed out waiting for single-replica steady state on deployment/{deployment_name} and hpa/{hpa_name} in ns/{namespace}"
    )


def wait_rollout(
    deployment_name: str,
    timeout_s: int = 300,
    namespace: str = "default",
) -> None:
    """Block until deployment rollout completes."""
    print(f"kubectl rollout status deployment/{deployment_name}...", flush=True)
    subprocess.run(
        [
            "kubectl",
            "rollout",
            "status",
            f"deployment/{deployment_name}",
            "-n",
            namespace,
            f"--timeout={timeout_s}s",
        ],
        check=True,
    )


def apply_recommended_diff(
    run_dir: Path,
    deployment_yaml_path: Path,
    hpa_yaml_path: Path,
    deployment_name: str,
    namespace: str,
    repo_root: Path | None = None,
) -> None:
    """Apply current deployment/HPA YAMLs via kubectl and wait for rollout."""
    root = repo_root or REPO_ROOT
    diff_path = run_dir / "recommended.diff"
    if diff_path.exists() and not diff_path.read_text().strip():
        raise ValueError("recommended.diff is empty (no YAML changes recommended)")
    kubectl_apply(deployment_yaml_path, hpa_yaml_path, root)
    wait_rollout(deployment_name=deployment_name, namespace=namespace)
    print("rollout complete.", flush=True)
