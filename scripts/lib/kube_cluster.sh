# Shared kubeconfig/context for cluster scripts (seed PVC, run_cluster_profiles, etc.).
# shellcheck shell=bash
ensure_kube_cluster() {
  KUBE_CONTEXT="${KUBE_CONTEXT:-monitoring}"
  KUBECONFIG_PATH="${KUBECONFIG_PATH:-/Users/svastik/Documents/Research/hetzner-svastik-monitoring.yaml}"
  NAMESPACE="${NAMESPACE:-svastik}"
  if [[ -n "${KUBECONFIG_PATH}" ]]; then
    export KUBECONFIG="${KUBECONFIG_PATH}"
  fi
  kubectl config use-context "${KUBE_CONTEXT}" >/dev/null
  if ! kubectl -n "${NAMESPACE}" get namespace "${NAMESPACE}" >/dev/null 2>&1; then
    echo "[kube] namespace '${NAMESPACE}' not found on context '${KUBE_CONTEXT}'" >&2
    echo "[kube] set KUBE_CONTEXT / KUBECONFIG_PATH (see scripts/run_cluster_profiles.sh)" >&2
    return 1
  fi
}
