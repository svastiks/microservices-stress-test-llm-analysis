#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
  cat <<'EOF'
Setup local Kubernetes + monitoring for the demo stress-service (custom FastAPI app).

This script:
- Starts minikube
- Builds and loads stress-service + mock-dependency images
- Deploys Deployment + HPA for stress-service
- Installs kube-prometheus-stack + ServiceMonitor
- Optionally runs a single experiment via start.py
EOF
}

log() { printf "\n==> %s\n" "$*"; }
die() { printf "\nERROR: %s\n" "$*" >&2; exit 1; }

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "missing required command: $1"
}

CPUS="4"
MEMORY="7680mb"
DRIVER="docker"
RESET="0"
SKIP_BUILD="0"
SKIP_LOAD="0"
SKIP_DEPLOY="0"
SKIP_MONITORING="0"
RUN_EXPERIMENT="0"
PROFILE="low"
SCRIPT_NAME="login"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --cpus) CPUS="${2:-}"; shift 2 ;;
    --memory) MEMORY="${2:-}"; shift 2 ;;
    --driver) DRIVER="${2:-}"; shift 2 ;;
    --reset) RESET="1"; shift ;;
    --skip-build) SKIP_BUILD="1"; shift ;;
    --skip-load) SKIP_LOAD="1"; shift ;;
    --skip-deploy) SKIP_DEPLOY="1"; shift ;;
    --skip-monitoring) SKIP_MONITORING="1"; shift ;;
    --run-experiment) RUN_EXPERIMENT="1"; shift ;;
    --profile) PROFILE="${2:-}"; shift 2 ;;
    --script) SCRIPT_NAME="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown argument: $1 (use --help)" ;;
  esac
done

need_cmd minikube
need_cmd kubectl
need_cmd docker
need_cmd helm
need_cmd python3

cd "$REPO_ROOT"

if [[ "$RESET" == "1" ]]; then
  log "Resetting minikube"
  minikube delete || true
fi

log "Starting minikube (cpus=$CPUS memory=$MEMORY driver=$DRIVER)"
minikube start --cpus="$CPUS" --memory="$MEMORY" --driver="$DRIVER"

log "Enabling metrics-server addon"
minikube addons enable metrics-server

if [[ "$SKIP_BUILD" != "1" ]]; then
  log "Building Docker images"
  docker build -t stress-service:latest -f apps/service/Dockerfile apps/service/
  docker build -t mock-dependency:latest -f apps/service/Dockerfile.mock apps/service/
else
  log "Skipping Docker image builds"
fi

if [[ "$SKIP_LOAD" != "1" ]]; then
  log "Loading images into minikube"
  minikube image load stress-service:latest
  minikube image load mock-dependency:latest
else
  log "Skipping image loads"
fi

if [[ "$SKIP_DEPLOY" != "1" ]]; then
  log "Deploying app + mock dependency + HPA"
  kubectl apply -f apps/service/k8s/mock-dependency.yaml
  kubectl apply -f apps/service/k8s/deployment.yaml
  kubectl apply -f apps/service/k8s/hpa.yaml
else
  log "Skipping app/hpa deploy"
fi

if [[ "$SKIP_MONITORING" != "1" ]]; then
  log "Installing Prometheus stack (kube-prometheus-stack)"
  helm repo add prometheus-community https://prometheus-community.github.io/helm-charts >/dev/null 2>&1 || true
  helm repo update

  if helm -n monitoring status kps >/dev/null 2>&1; then
    log "Prometheus stack already installed (release=kps); skipping helm install"
  else
    helm install kps prometheus-community/kube-prometheus-stack \
      -n monitoring --create-namespace \
      -f apps/service/monitoring/helm-values.yaml
  fi

  log "Registering ServiceMonitor"
  kubectl apply -f apps/service/monitoring/servicemonitor.yaml
else
  log "Skipping monitoring install + ServiceMonitor"
fi

log "Sanity-check cluster + monitoring"
kubectl get pods
kubectl get svc
kubectl get pods -n monitoring || true
kubectl get svc -n monitoring || true

if [[ "$RUN_EXPERIMENT" == "1" ]]; then
  log "Running experiment (profile=$PROFILE script=$SCRIPT_NAME)"
  if [[ -f ".env" ]]; then
    set -a
    # shellcheck disable=SC1091
    source ".env"
    set +a
  fi
  python3 start.py --profile "$PROFILE" --script "$SCRIPT_NAME"
else
  log "Setup complete (experiment not run). To run it now:"
  printf "   python3 start.py --profile %s --script %s\n" "$PROFILE" "$SCRIPT_NAME"
fi

