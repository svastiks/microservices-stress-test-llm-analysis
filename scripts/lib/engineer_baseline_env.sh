# Method 2 (B1): what a strong engineer wires before any squeeze loop.
# UP @ high RPS: fat deployment (5×150m/75Mi) + standard HPA — not thin 50m/25Mi (SLO fails).
# DOWN: same fat deployment (matches down_demo fat-start).
#
# Usage: source scripts/lib/engineer_baseline_env.sh
ROOT="${ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"

export BASELINE_DEPLOYMENT_YAML="${BASELINE_DEPLOYMENT_YAML:-${ROOT}/infra/k8s/spark/robot-shop-web-deployment.baseline.yaml}"
export BASELINE_HPA_YAML="${BASELINE_HPA_YAML:-${ROOT}/infra/k8s/spark/robot-shop-web-hpa.baseline.yaml}"

if [[ "${USE_THIN_UP_BASELINE:-}" == "1" ]]; then
  export BASELINE_DEPLOYMENT_YAML="${ROOT}/infra/k8s/spark/robot-shop-web-deployment.up-demo-thin.baseline.yaml"
fi
