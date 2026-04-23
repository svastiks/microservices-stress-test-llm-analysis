"""Apply current YAMLs with kubectl and wait for rollout."""
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


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
