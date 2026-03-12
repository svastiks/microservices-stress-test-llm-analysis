"""Apply current YAMLs with kubectl and wait for rollout."""
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEPLOYMENT_REL = "service/k8s/deployment.yaml"
HPA_REL = "service/k8s/hpa.yaml"
DEPLOYMENT_NAME = "stress-service"
NAMESPACE = "default"


def kubectl_apply(repo_root: Path | None = None) -> None:
    """Run kubectl apply -f for deployment and HPA."""
    root = repo_root or REPO_ROOT
    print("kubectl apply (deployment + hpa)...", flush=True)
    subprocess.run(
        [
            "kubectl",
            "apply",
            "-f",
            str(root / DEPLOYMENT_REL),
            "-f",
            str(root / HPA_REL),
        ],
        cwd=root,
        check=True,
    )


def wait_rollout(timeout_s: int = 300, namespace: str = NAMESPACE) -> None:
    """Block until deployment rollout completes."""
    print(f"kubectl rollout status deployment/{DEPLOYMENT_NAME}...", flush=True)
    subprocess.run(
        [
            "kubectl",
            "rollout",
            "status",
            f"deployment/{DEPLOYMENT_NAME}",
            "-n",
            namespace,
            f"--timeout={timeout_s}s",
        ],
        check=True,
    )


def apply_recommended_diff(run_dir: Path, repo_root: Path | None = None) -> None:
    """Apply current deployment/HPA YAMLs via kubectl and wait for rollout."""
    root = repo_root or REPO_ROOT
    diff_path = run_dir / "recommended.diff"
    if diff_path.exists() and not diff_path.read_text().strip():
        raise ValueError("recommended.diff is empty (no YAML changes recommended)")
    kubectl_apply(root)
    wait_rollout()
    print("rollout complete.", flush=True)
