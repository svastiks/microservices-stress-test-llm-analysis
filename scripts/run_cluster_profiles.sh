#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="${NAMESPACE:-svastik}"
MON_NS="${MON_NS:-monitoring}"
KUBE_CONTEXT="${KUBE_CONTEXT:-monitoring}"
KUBECONFIG_PATH="${KUBECONFIG_PATH:-/Users/svastik/Documents/Research/hetzner-svastik-monitoring.yaml}"
# Prefer PROFILES_CSV; else PROFILES; else default pair.
PROFILES_CSV="${PROFILES_CSV:-${PROFILES:-down_demo,up_demo}}"
ANALYZER_SCRIPT="${ANALYZER_SCRIPT:-robotshop_login}"
ANALYZER_IMAGE="${ANALYZER_IMAGE:-docker.io/svastik/microservices-stress-analyzer:latest}"
ANALYZER_IMAGE_PULL_POLICY="${ANALYZER_IMAGE_PULL_POLICY:-Always}"
BUILD_ANALYZER_IMAGE="${BUILD_ANALYZER_IMAGE:-false}"
BUILD_PLATFORMS="${BUILD_PLATFORMS:-linux/amd64,linux/arm64}"
STREAM_JOB_LOGS="${STREAM_JOB_LOGS:-true}"
WAIT_TIMEOUT="${WAIT_TIMEOUT:-45m}"
RESULTS_DEST="${RESULTS_DEST:-./results-from-cluster}"
READER_POD="${READER_POD:-analyzer-results-reader}"
RESET_BASELINE_EACH_PROFILE="${RESET_BASELINE_EACH_PROFILE:-true}"
CLEANUP_COMPLETED_JOBS="${CLEANUP_COMPLETED_JOBS:-true}"
CLEANUP_TERMINAL_PODS="${CLEANUP_TERMINAL_PODS:-true}"
CLEANUP_FAILED_JOBS="${CLEANUP_FAILED_JOBS:-true}"
DEPLOY_ANALYZER_MONGODB="${DEPLOY_ANALYZER_MONGODB:-false}"
LOG_DIR="${LOG_DIR:-./results/cluster-run-logs}"
DEPLOYMENT_YAML="${DEPLOYMENT_YAML:-infra/k8s/spark/robot-shop-web-deployment.yaml}"
HPA_YAML="${HPA_YAML:-infra/k8s/spark/robot-shop-web-hpa.yaml}"
BASELINE_DEPLOYMENT_YAML="${BASELINE_DEPLOYMENT_YAML:-infra/k8s/spark/robot-shop-web-deployment.baseline.yaml}"
BASELINE_HPA_YAML="${BASELINE_HPA_YAML:-infra/k8s/spark/robot-shop-web-hpa.baseline.yaml}"
FORCE_DEPLOY_STACK="${FORCE_DEPLOY_STACK:-true}"
UP_DEMO_STABILIZE_USER="${UP_DEMO_STABILIZE_USER:-true}"
UP_DEMO_USER_CPU_REQUEST="${UP_DEMO_USER_CPU_REQUEST:-150m}"
UP_DEMO_USER_CPU_LIMIT="${UP_DEMO_USER_CPU_LIMIT:-300m}"
UP_DEMO_USER_MEM_REQUEST="${UP_DEMO_USER_MEM_REQUEST:-128Mi}"
UP_DEMO_USER_MEM_LIMIT="${UP_DEMO_USER_MEM_LIMIT:-256Mi}"
# After a squeeze, web can be left with tiny requests/limits and stay NotReady; restore baseline
# before blocking on rollout (only when we already reset per profile — same baseline files).
WEB_INITIAL_ROLLOUT_TIMEOUT="${WEB_INITIAL_ROLLOUT_TIMEOUT:-300s}"

# Auto-load .env for convenience (existing shell env still wins).
if [[ -f ".env" ]]; then
  # shellcheck disable=SC1091
  set -a
  source ".env"
  set +a
fi

mkdir -p "${LOG_DIR}"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] [cluster-run] $*"
}

on_error() {
  local exit_code=$?
  log "ERROR at line ${1}; exit_code=${exit_code}"
  exit "${exit_code}"
}
trap 'on_error $LINENO' ERR

cleanup_on_exit() {
  kubectl -n "${NAMESPACE}" delete pod "${READER_POD}" --ignore-not-found >/dev/null 2>&1 || true
}
trap cleanup_on_exit EXIT

if [[ -n "${KUBECONFIG_PATH}" ]]; then
  export KUBECONFIG="${KUBECONFIG_PATH}"
fi

log "kubeconfig: ${KUBECONFIG:-<default>}"
log "available contexts:"
kubectl config get-contexts
log "switching context to: ${KUBE_CONTEXT}"
kubectl config use-context "${KUBE_CONTEXT}" >/dev/null
kubectl get pods >/dev/null

log "context: $(kubectl config current-context)"
log "namespace: ${NAMESPACE}"
log "profiles: ${PROFILES_CSV}"
log "log_dir: ${LOG_DIR}"
log "analyzer_image: ${ANALYZER_IMAGE}"
log "analyzer_image_pull_policy: ${ANALYZER_IMAGE_PULL_POLICY}"
log "build_analyzer_image: ${BUILD_ANALYZER_IMAGE}"
log "stream_job_logs: ${STREAM_JOB_LOGS}"
log "cleanup_completed_jobs: ${CLEANUP_COMPLETED_JOBS}"
log "cleanup_terminal_pods: ${CLEANUP_TERMINAL_PODS}"
log "cleanup_failed_jobs: ${CLEANUP_FAILED_JOBS}"
log "deploy_analyzer_mongodb: ${DEPLOY_ANALYZER_MONGODB}"
log "up_demo_stabilize_user: ${UP_DEMO_STABILIZE_USER}"
if [[ "$#" -gt 0 ]]; then
  log "extra args for analyzer job: $*"
fi

get_job_pod_name() {
  local job_name="$1"
  kubectl -n "${NAMESPACE}" get pods -l "job-name=${job_name}" -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || true
}

save_job_logs() {
  local job_name="$1"
  local out_file="$2"
  local pod_name
  pod_name="$(get_job_pod_name "${job_name}")"
  if [[ -n "${pod_name}" ]]; then
    kubectl -n "${NAMESPACE}" logs "${pod_name}" --all-containers=true --tail=500 > "${out_file}" 2>&1 || true
  else
    kubectl -n "${NAMESPACE}" logs "job/${job_name}" --all-containers=true --tail=500 > "${out_file}" 2>&1 || true
  fi
}

reset_managed_web_yaml_to_baseline() {
  cp "${BASELINE_DEPLOYMENT_YAML}" "${DEPLOYMENT_YAML}"
  cp "${BASELINE_HPA_YAML}" "${HPA_YAML}"
}

apply_managed_web_baseline() {
  log "apply immutable managed baseline (web deployment + hpa)"
  reset_managed_web_yaml_to_baseline
  kubectl apply -f "${DEPLOYMENT_YAML}" >/dev/null
  kubectl apply -f "${HPA_YAML}" >/dev/null
  kubectl -n "${NAMESPACE}" rollout status deployment/web --timeout=300s >/dev/null
}

if [[ ! -f "${BASELINE_DEPLOYMENT_YAML}" || ! -f "${BASELINE_HPA_YAML}" ]]; then
  log "baseline YAML missing: ${BASELINE_DEPLOYMENT_YAML} / ${BASELINE_HPA_YAML}"
  exit 1
fi

# Prevent stale/mutated optimization YAML from leaking between runs or into the image build.
reset_managed_web_yaml_to_baseline

if [[ "${BUILD_ANALYZER_IMAGE}" == "true" ]]; then
  log "building and pushing analyzer image: ${ANALYZER_IMAGE}"
  docker buildx create --use --name multiarch-builder >/dev/null 2>&1 || docker buildx use multiarch-builder
  docker buildx build \
    --platform "${BUILD_PLATFORMS}" \
    -f Dockerfile.analyzer \
    -t "${ANALYZER_IMAGE}" \
    --push .
fi

deploy_stack_with_fallback() {
  if ./scripts/deploy_spark_stack.sh; then
    return 0
  fi

  log "deploy_spark_stack failed (likely Helm ownership conflict); applying managed web deployment/hpa directly and continuing"
  kubectl apply -f "${DEPLOYMENT_YAML}" >/dev/null
  kubectl apply -f "${HPA_YAML}" >/dev/null
  kubectl apply -f infra/k8s/spark/analyzer-rbac.yaml >/dev/null
}

stack_ready() {
  kubectl -n "${NAMESPACE}" get deploy web >/dev/null 2>&1 \
    && kubectl -n "${NAMESPACE}" get svc web >/dev/null 2>&1 \
    && kubectl -n "${NAMESPACE}" get hpa web-hpa >/dev/null 2>&1
}

if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  log "OPENAI_API_KEY is required (env var or .env)"
  exit 1
fi

if [[ "${FORCE_DEPLOY_STACK}" == "true" ]]; then
  if stack_ready; then
    log "stack already present; skipping redeploy (set FORCE_DEPLOY_STACK=hard to force helm deploy)"
  else
    log "force deploy enabled and stack missing; running deploy_spark_stack"
    deploy_stack_with_fallback
  fi
elif [[ "${FORCE_DEPLOY_STACK}" == "hard" ]]; then
  log "hard force deploy enabled; running deploy_spark_stack regardless of existing stack"
  deploy_stack_with_fallback
else
  if stack_ready; then
    log "robot-shop web/svc/hpa already present; skipping helm deploy (set FORCE_DEPLOY_STACK=true to force)"
  else
    log "robot-shop stack incomplete; running deploy_spark_stack"
    deploy_stack_with_fallback
  fi
fi
if [[ "${RESET_BASELINE_EACH_PROFILE}" == "true" ]]; then
  log "pre-run: restore managed web baseline (prior runs may leave web NotReady / HPA unknown)"
  apply_managed_web_baseline
fi
kubectl -n "${NAMESPACE}" get deploy,svc,hpa
kubectl -n "${NAMESPACE}" rollout status deployment/web --timeout="${WEB_INITIAL_ROLLOUT_TIMEOUT}"

log "ensure analyzer infra..."
kubectl apply -f infra/k8s/spark/analyzer-rbac.yaml >/dev/null
kubectl apply -f infra/k8s/spark/analyzer-results-pvc.yaml >/dev/null
if [[ "${DEPLOY_ANALYZER_MONGODB}" == "true" ]]; then
  kubectl apply -f infra/k8s/spark/mongodb.yaml >/dev/null
else
  log "skipping analyzer-mongodb deploy (set DEPLOY_ANALYZER_MONGODB=true to enable)"
fi

kubectl -n "${NAMESPACE}" create secret generic llm-api \
  --from-literal=OPENAI_API_KEY="${OPENAI_API_KEY}" \
  --dry-run=client -o yaml | kubectl apply -f - >/dev/null

EXTRA_ARGS=("$@")

IFS=',' read -r -a PROFILE_LIST <<< "${PROFILES_CSV}"
for profile in "${PROFILE_LIST[@]}"; do
  p="$(echo "${profile}" | xargs)"
  if [[ -z "${p}" ]]; then
    continue
  fi

  if [[ "${RESET_BASELINE_EACH_PROFILE}" == "true" ]]; then
    log "reset baseline in cluster before profile=${p}"
    apply_managed_web_baseline
  fi

  if [[ "${p}" == "up_demo" && "${UP_DEMO_STABILIZE_USER}" == "true" ]]; then
    log "up_demo: raising user service memory/cpu to avoid OOM during recovery demo"
    kubectl -n "${NAMESPACE}" set resources deployment/user \
      --requests="cpu=${UP_DEMO_USER_CPU_REQUEST},memory=${UP_DEMO_USER_MEM_REQUEST}" \
      --limits="cpu=${UP_DEMO_USER_CPU_LIMIT},memory=${UP_DEMO_USER_MEM_LIMIT}" >/dev/null
    kubectl -n "${NAMESPACE}" rollout status deployment/user --timeout=300s >/dev/null
  fi

  p_job="$(echo "${p}" | tr '[:upper:]' '[:lower:]' | tr '_' '-' | tr -cd 'a-z0-9.-')"
  p_job="${p_job#-}"
  p_job="${p_job%-}"
  if [[ -z "${p_job}" ]]; then
    log "invalid profile for job naming: '${p}'"
    exit 1
  fi
  job_name="stress-analyzer-${p_job}"
  job_log="${LOG_DIR}/${job_name}.log"
  log "launch profile=${p} job=${job_name}"
  PROFILE="${p}" \
  ANALYZER_SCRIPT="${ANALYZER_SCRIPT}" \
  ANALYZER_IMAGE="${ANALYZER_IMAGE}" \
  ANALYZER_IMAGE_PULL_POLICY="${ANALYZER_IMAGE_PULL_POLICY}" \
  JOB_NAME="${job_name}" \
  ./scripts/run_analyzer_job.sh "${EXTRA_ARGS[@]}"

  log "waiting for ${job_name} (timeout=${WAIT_TIMEOUT})"
  log_pid=""
  if [[ "${STREAM_JOB_LOGS}" == "true" ]]; then
    (
      # Wait for pod to exist.
      for _ in $(seq 1 120); do
        pod_name="$(get_job_pod_name "${job_name}")"
        if [[ -n "${pod_name}" ]]; then
          break
        fi
        sleep 1
      done

      if [[ -n "${pod_name:-}" ]]; then
        # Wait until pod is runnable/terminal to avoid noisy "container ... is not available" spam.
        for _ in $(seq 1 300); do
          phase="$(kubectl -n "${NAMESPACE}" get pod "${pod_name}" -o jsonpath='{.status.phase}' 2>/dev/null || true)"
          if [[ "${phase}" == "Running" || "${phase}" == "Succeeded" || "${phase}" == "Failed" ]]; then
            break
          fi
          sleep 1
        done
        kubectl -n "${NAMESPACE}" logs -f "${pod_name}" --all-containers=true --pod-running-timeout=10m 2>/dev/null || true
      fi
    ) &
    log_pid="$!"
  fi
  if kubectl -n "${NAMESPACE}" wait --for=condition=complete --timeout="${WAIT_TIMEOUT}" "job/${job_name}"; then
    log "${job_name} completed"
  else
    log "${job_name} failed or timed out; collecting diagnostics"
    kubectl -n "${NAMESPACE}" get job "${job_name}" || true
    kubectl -n "${NAMESPACE}" describe "job/${job_name}" || true
    kubectl -n "${NAMESPACE}" get pods -l job-name="${job_name}" -o wide || true
    save_job_logs "${job_name}" "${job_log}"
    log "saved failure logs to ${job_log}"
    if [[ "${CLEANUP_FAILED_JOBS}" == "true" ]]; then
      kubectl -n "${NAMESPACE}" delete job "${job_name}" --ignore-not-found >/dev/null || true
    fi
    if [[ -n "${log_pid}" ]]; then
      kill "${log_pid}" >/dev/null 2>&1 || true
      wait "${log_pid}" 2>/dev/null || true
    fi
    exit 1
  fi

  if [[ -n "${log_pid}" ]]; then
    kill "${log_pid}" >/dev/null 2>&1 || true
    wait "${log_pid}" 2>/dev/null || true
  fi
  save_job_logs "${job_name}" "${job_log}"
  log "saved job logs to ${job_log}"
  if [[ "${CLEANUP_COMPLETED_JOBS}" == "true" ]]; then
    kubectl -n "${NAMESPACE}" delete job "${job_name}" --ignore-not-found >/dev/null || true
  fi
done

log "copy results PVC to local ${RESULTS_DEST} ..."
kubectl -n "${NAMESPACE}" delete pod "${READER_POD}" --ignore-not-found >/dev/null
kubectl -n "${NAMESPACE}" apply -f - >/dev/null <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: ${READER_POD}
spec:
  restartPolicy: Never
  containers:
  - name: reader
    image: busybox
    command: ["sh","-c","sleep 3600"]
    volumeMounts:
    - name: results
      mountPath: /results
  volumes:
  - name: results
    persistentVolumeClaim:
      claimName: analyzer-results-pvc
EOF

kubectl -n "${NAMESPACE}" wait --for=condition=Ready "pod/${READER_POD}" --timeout=120s >/dev/null
rm -rf "${RESULTS_DEST}"
kubectl -n "${NAMESPACE}" cp "${READER_POD}:/results" "${RESULTS_DEST}"
kubectl -n "${NAMESPACE}" delete pod "${READER_POD}" --ignore-not-found >/dev/null

log "done. local artifacts: ${RESULTS_DEST}"
if [[ "${CLEANUP_TERMINAL_PODS}" == "true" ]]; then
  kubectl -n "${NAMESPACE}" delete pod --field-selector=status.phase==Succeeded --ignore-not-found >/dev/null || true
  kubectl -n "${NAMESPACE}" delete pod --field-selector=status.phase==Failed --ignore-not-found >/dev/null || true
fi
