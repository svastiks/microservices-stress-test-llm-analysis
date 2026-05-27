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
# Empty / "none" = poll until the job completes (kubectl --timeout=0 checks once; do not use it).
WAIT_TIMEOUT="${WAIT_TIMEOUT:-}"
WAIT_POLL_SECONDS="${WAIT_POLL_SECONDS:-60}"
RESULTS_PVC_SYNC_LLMS_ONLY="${RESULTS_PVC_SYNC_LLMS_ONLY:-false}"
RESULTS_DEST="${RESULTS_DEST:-./results-from-cluster}"
# thin (default): RESULTS_DEST/run-<n>/formula-run/, llm-run/ (each holds iteration-* like a single-optimizer run),
#   plus comparison.md (regenerated locally from the two cost-effective-boundary.json files; PVC root file is fallback only).
# full: copy entire PVC tree to RESULTS_DEST/pvc-import-<stamp>/ (optional snapshots/ if RESULTS_PVC_SNAPSHOTS=true).
RESULTS_PVC_SYNC_LAYOUT="${RESULTS_PVC_SYNC_LAYOUT:-thin}"
RESULTS_PVC_SNAPSHOTS="${RESULTS_PVC_SNAPSHOTS:-false}"
# When true, also copy run-<n>/comparison.md to RESULTS_DEST root as squeeze-optimizer-comparison.md.
RESULTS_PVC_COPY_COMPARISON_TO_ROOT="${RESULTS_PVC_COPY_COMPARISON_TO_ROOT:-false}"
# When true, also write squeeze-optimizer-comparison-<timestamp>.md under RESULTS_DEST (root copy only).
RESULTS_STAMPED_COMPARISON_MD="${RESULTS_STAMPED_COMPARISON_MD:-false}"
# When set (e.g. compare sweep round 1..N), sync copies PVC data to RESULTS_DEST/run-<round>
# (not always run-1) so multi-RPS sweeps keep every round locally.
COMPARE_SWEEP_ROUND="${COMPARE_SWEEP_ROUND:-}"
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
  local rc=$?
  kubectl -n "${NAMESPACE}" delete pod "${READER_POD}" --ignore-not-found >/dev/null 2>&1 || true
  exit "${rc}"
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
log "results_pvc_sync_layout: ${RESULTS_PVC_SYNC_LAYOUT}"
log "results_pvc_snapshots: ${RESULTS_PVC_SNAPSHOTS}"
log "results_pvc_copy_comparison_to_root: ${RESULTS_PVC_COPY_COMPARISON_TO_ROOT}"
log "results_stamped_comparison_md: ${RESULTS_STAMPED_COMPARISON_MD}"
if [[ -n "${COMPARE_SWEEP_ROUND:-}" ]]; then
  log "compare_sweep_round: ${COMPARE_SWEEP_ROUND}"
fi
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

job_condition_status() {
  local job_name="$1"
  local cond="$2"
  kubectl -n "${NAMESPACE}" get "job/${job_name}" \
    -o "jsonpath={.status.conditions[?(@.type==\"${cond}\")].status}" 2>/dev/null || true
}

wait_for_analyzer_job() {
  local job_name="$1"
  if [[ -n "${WAIT_TIMEOUT}" && "${WAIT_TIMEOUT}" != "none" ]]; then
    log "waiting for ${job_name} (timeout=${WAIT_TIMEOUT})"
    kubectl -n "${NAMESPACE}" wait --for=condition=complete --timeout="${WAIT_TIMEOUT}" "job/${job_name}"
    return $?
  fi
  log "waiting for ${job_name} (poll every ${WAIT_POLL_SECONDS}s, no overall timeout)"
  while true; do
    if [[ "$(job_condition_status "${job_name}" Complete)" == "True" ]]; then
      return 0
    fi
    if [[ "$(job_condition_status "${job_name}" Failed)" == "True" ]]; then
      return 1
    fi
    if ! kubectl -n "${NAMESPACE}" get "job/${job_name}" >/dev/null 2>&1; then
      return 1
    fi
    sleep "${WAIT_POLL_SECONDS}"
  done
}

latest_numbered_run_dir() {
  local parent="$1"
  local best=""
  local best_n=-1
  local d b n
  if [[ ! -d "${parent}" ]]; then
    return 0
  fi
  for d in "${parent}"/run-*; do
    [[ -d "${d}" ]] || continue
    b="$(basename "${d}")"
    if [[ "${b}" =~ ^run-([0-9]+)$ ]]; then
      n="${BASH_REMATCH[1]}"
      if (( n > best_n )); then
        best_n="${n}"
        best="${d}"
      fi
    fi
  done
  if [[ -n "${best}" ]]; then
    printf "%s" "${best}"
  fi
}

# Copy analyzer PVC to RESULTS_DEST after every profile job (success or failure) so partial runs are not lost.
# Compare (--compare-squeeze-optimizers): one folder run-<n>/formula-run, run-<n>/llm-run (iteration-* inside), plus
#   comparison.md (rebuilt from those trees' cost-effective-boundary.json on sync).
# Other jobs: copy latest top-level PVC run-<n>/ only (no latest/, no snapshots/, no duplicate run/ bundle).
sync_results_pvc_to_local() {
  local reason="${1:-sync}"
  log "copy results PVC to local ${RESULTS_DEST} (${reason}) ..."
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

  if ! kubectl -n "${NAMESPACE}" wait --for=condition=Ready "pod/${READER_POD}" --timeout=120s >/dev/null; then
    log "WARNING: reader pod not Ready; skipping PVC copy for this sync"
    kubectl -n "${NAMESPACE}" delete pod "${READER_POD}" --ignore-not-found >/dev/null || true
    return 0
  fi

  local RUN_STAMP
  RUN_STAMP="$(date +%Y%m%d-%H%M%S)"
  local SNAPSHOT_DIR TMP_COPY_DIR COPIED_ROOT FORMULA_SRC LLM_SRC SINGLE_RUN
  SNAPSHOT_DIR="${RESULTS_DEST}/snapshots/${RUN_STAMP}"
  TMP_COPY_DIR="$(mktemp -d)"

  if ! kubectl -n "${NAMESPACE}" cp "${READER_POD}:/results" "${TMP_COPY_DIR}"; then
    log "WARNING: kubectl cp from PVC failed; skipping layout for this sync"
    rm -rf "${TMP_COPY_DIR}"
    kubectl -n "${NAMESPACE}" delete pod "${READER_POD}" --ignore-not-found >/dev/null || true
    return 0
  fi

  COPIED_ROOT="${TMP_COPY_DIR}/results"
  if [[ ! -d "${COPIED_ROOT}" ]]; then
    COPIED_ROOT="${TMP_COPY_DIR}"
  fi

  # Drop legacy mirror dirs this script used to create (avoid stale duplicates next to run-<n>/).
  rm -rf "${RESULTS_DEST}/latest" "${RESULTS_DEST}/run" 2>/dev/null || true
  if [[ "${RESULTS_PVC_SNAPSHOTS}" != "true" ]]; then
    rm -rf "${RESULTS_DEST}/snapshots" 2>/dev/null || true
  fi

  if [[ "${RESULTS_PVC_SYNC_LAYOUT}" == "full" ]]; then
    local IMPORT_DIR
    IMPORT_DIR="${RESULTS_DEST}/pvc-import-${RUN_STAMP}"
    mkdir -p "${IMPORT_DIR}"
    cp -R "${COPIED_ROOT}/." "${IMPORT_DIR}/"
    if [[ "${RESULTS_PVC_SNAPSHOTS}" == "true" ]]; then
      mkdir -p "${SNAPSHOT_DIR}"
      cp -R "${COPIED_ROOT}/." "${SNAPSHOT_DIR}/"
    fi
    log "PVC sync done (${reason}, layout=full): import=${IMPORT_DIR}"
    kubectl -n "${NAMESPACE}" delete pod "${READER_POD}" --ignore-not-found >/dev/null
    rm -rf "${TMP_COPY_DIR}"
    return 0
  fi

  # --- thin ---
  if [[ "${RESULTS_PVC_SYNC_LLMS_ONLY}" == "true" && -d "${COPIED_ROOT}/squeeze-compare-llm" ]]; then
    LLM_SRC="$(latest_numbered_run_dir "${COPIED_ROOT}/squeeze-compare-llm")"
    if [[ -n "${LLM_SRC}" ]]; then
      run_label="$(basename "${LLM_SRC}")"
      run_out="${RESULTS_DEST}/${run_label}"
      rm -rf "${run_out}"
      cp -R "${LLM_SRC}" "${run_out}"
      log "PVC sync done (${reason}, layout=thin, llm-only): ${run_out}"
    else
      log "WARNING: squeeze-compare-llm present but no run-* found"
    fi
  elif [[ "${COMPARE_SYNC_MODE:-}" == "hpa" ]] \
    && [[ ! -d "${COPIED_ROOT}/squeeze-compare-hpa" || ! -d "${COPIED_ROOT}/squeeze-compare-llm" ]]; then
    if [[ -d "${COPIED_ROOT}/squeeze-compare-formula" && -d "${COPIED_ROOT}/squeeze-compare-llm" ]]; then
      log "ERROR: COMPARE_SYNC_MODE=hpa but PVC has formula+llm only (stale method-1 or job ran --compare-squeeze-optimizers)"
      log "  Rebuild analyzer image and run: ./scripts/run_down_demo_hpa_vs_llm_sweep.sh with BUILD_ANALYZER_IMAGE=true"
    else
      log "WARNING: COMPARE_SYNC_MODE=hpa but PVC missing squeeze-compare-hpa and/or squeeze-compare-llm"
    fi
  elif [[ "${COMPARE_SYNC_MODE:-}" == "hpa" ]] \
    && [[ -d "${COPIED_ROOT}/squeeze-compare-hpa" && -d "${COPIED_ROOT}/squeeze-compare-llm" ]]; then
    HPA_SRC="$(latest_numbered_run_dir "${COPIED_ROOT}/squeeze-compare-hpa")"
    LLM_SRC="$(latest_numbered_run_dir "${COPIED_ROOT}/squeeze-compare-llm")"
    if [[ -z "${HPA_SRC}" || -z "${LLM_SRC}" ]]; then
      log "WARNING: compare layout expected squeeze-compare hpa+llm runs on PVC; skipping bundle"
    else
      local h_base l_base run_label run_out n_h n_l
      h_base="$(basename "${HPA_SRC}")"
      l_base="$(basename "${LLM_SRC}")"
      run_label="${h_base}"
      if [[ "${h_base}" =~ ^run-([0-9]+)$ ]]; then
        n_h="${BASH_REMATCH[1]}"
      else
        n_h=-1
      fi
      if [[ "${l_base}" =~ ^run-([0-9]+)$ ]]; then
        n_l="${BASH_REMATCH[1]}"
      else
        n_l=-1
      fi
      if [[ "${n_h}" -ge 0 && "${n_l}" -ge 0 && "${n_h}" != "${n_l}" ]]; then
        log "ERROR: hpa ${h_base} vs llm ${l_base} run index mismatch — stale PVC bundle; skipping compare copy"
      else
      if [[ -n "${COMPARE_SWEEP_ROUND:-}" ]]; then
        run_label="run-${COMPARE_SWEEP_ROUND}"
      fi
      run_out="${RESULTS_DEST}/${run_label}"
      rm -rf "${run_out}"
      mkdir -p "${run_out}"
      cp -R "${HPA_SRC}" "${run_out}/hpa-run"
      cp -R "${LLM_SRC}" "${run_out}/llm-run"
      _repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
      if PYTHONPATH="${_repo_root}${PYTHONPATH:+:${PYTHONPATH}}" python3 -c "
from pathlib import Path
from analysis.compare_squeeze_methods import compare
run_out = Path(r'''${run_out}''')
fa = run_out / 'hpa-run' / 'cost-effective-boundary.json'
fb = run_out / 'llm-run' / 'cost-effective-boundary.json'
if not fa.is_file() or not fb.is_file():
    raise SystemExit('missing boundary json')
run_out.joinpath('comparison.md').write_text(
    compare(fa, fb, label_a='hpa', label_b='llm')
)
"; then
        log "wrote comparison.md from bundled boundary JSON (hpa vs llm)"
      else
        log "WARNING: could not regenerate comparison.md from boundary JSON"
        if [[ -f "${COPIED_ROOT}/squeeze-optimizer-comparison.md" ]]; then
          cp "${COPIED_ROOT}/squeeze-optimizer-comparison.md" "${run_out}/comparison.md"
        fi
      fi
      if [[ -n "${COMPARE_SWEEP_ROUND:-}" ]]; then
        printf '%s\n' "${run_label}" > "${RESULTS_DEST}/.last_sync_r${COMPARE_SWEEP_ROUND}.txt"
      fi
      if [[ "${RESULTS_PVC_COPY_COMPARISON_TO_ROOT}" == "true" ]]; then
        cp "${run_out}/comparison.md" "${RESULTS_DEST}/squeeze-optimizer-comparison.md"
      fi
      log "PVC sync done (${reason}, layout=thin, hpa-compare): ${run_out}"
      fi
    fi
  elif [[ "${COMPARE_SYNC_MODE:-}" != "hpa" ]] \
    && [[ -d "${COPIED_ROOT}/squeeze-compare-formula" && -d "${COPIED_ROOT}/squeeze-compare-llm" ]]; then
    FORMULA_SRC="$(latest_numbered_run_dir "${COPIED_ROOT}/squeeze-compare-formula")"
    LLM_SRC="$(latest_numbered_run_dir "${COPIED_ROOT}/squeeze-compare-llm")"
    if [[ -z "${FORMULA_SRC}" || -z "${LLM_SRC}" ]]; then
      log "WARNING: compare layout expected squeeze-compare formula+llm runs on PVC; skipping bundle"
    else
      local f_base l_base run_label run_out n_f n_l
      f_base="$(basename "${FORMULA_SRC}")"
      l_base="$(basename "${LLM_SRC}")"
      run_label="${f_base}"
      if [[ "${f_base}" =~ ^run-([0-9]+)$ ]]; then
        n_f="${BASH_REMATCH[1]}"
      else
        n_f=-1
      fi
      if [[ "${l_base}" =~ ^run-([0-9]+)$ ]]; then
        n_l="${BASH_REMATCH[1]}"
      else
        n_l=-1
      fi
      if [[ "${n_f}" -ge 0 && "${n_l}" -ge 0 && "${n_f}" != "${n_l}" ]]; then
        log "ERROR: formula ${f_base} vs llm ${l_base} run index mismatch — stale PVC bundle; skipping compare copy"
        log "  Re-run with BUILD_ANALYZER_IMAGE=true and SQUEEZE_COMPARE_PRUNE_PRIOR=1 (see squeeze_up_demo_env.sh)"
      else
      if [[ -n "${COMPARE_SWEEP_ROUND:-}" ]]; then
        run_label="run-${COMPARE_SWEEP_ROUND}"
      fi
      run_out="${RESULTS_DEST}/${run_label}"
      rm -rf "${run_out}"
      mkdir -p "${run_out}"
      cp -R "${FORMULA_SRC}" "${run_out}/formula-run"
      cp -R "${LLM_SRC}" "${run_out}/llm-run"
      # Regenerate comparison.md from the bundled boundary JSON. PVC root
      # squeeze-optimizer-comparison.md can lag another run or stale job output;
      # formula-run/ and llm-run/ are always the latest run-* we just copied.
      _repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
      if PYTHONPATH="${_repo_root}${PYTHONPATH:+:${PYTHONPATH}}" python3 -c "
from pathlib import Path
from analysis.compare_squeeze_methods import compare
run_out = Path(r'''${run_out}''')
fa = run_out / 'formula-run' / 'cost-effective-boundary.json'
fb = run_out / 'llm-run' / 'cost-effective-boundary.json'
if not fa.is_file() or not fb.is_file():
    raise SystemExit('missing boundary json')
run_out.joinpath('comparison.md').write_text(
    compare(fa, fb, label_a='formula', label_b='llm')
)
"; then
        log "wrote comparison.md from bundled boundary JSON (formula vs llm)"
      else
        log "WARNING: could not regenerate comparison.md from boundary JSON; using PVC squeeze-optimizer-comparison.md if present"
        if [[ -f "${COPIED_ROOT}/squeeze-optimizer-comparison.md" ]]; then
          cp "${COPIED_ROOT}/squeeze-optimizer-comparison.md" "${run_out}/comparison.md"
        fi
      fi
      if [[ -n "${COMPARE_SWEEP_ROUND:-}" ]]; then
        printf '%s\n' "${run_label}" > "${RESULTS_DEST}/.last_sync_r${COMPARE_SWEEP_ROUND}.txt"
      fi
      if [[ "${RESULTS_PVC_COPY_COMPARISON_TO_ROOT}" == "true" ]]; then
        cp "${run_out}/comparison.md" "${RESULTS_DEST}/squeeze-optimizer-comparison.md"
        if [[ "${RESULTS_STAMPED_COMPARISON_MD}" == "true" ]]; then
          cp "${run_out}/comparison.md" "${RESULTS_DEST}/squeeze-optimizer-comparison-${RUN_STAMP}.md"
        fi
      fi
      rm -f "${run_out}/squeeze-optimizer-comparison.txt" "${run_out}/squeeze-optimizer-comparison.md" \
            "${RESULTS_DEST}/squeeze-optimizer-comparison.txt"
      log "PVC sync done (${reason}, layout=thin, compare): ${run_out}"
      fi
    fi
  elif [[ -d "${COPIED_ROOT}/squeeze-compare-llm" ]]; then
    LLM_SRC="$(latest_numbered_run_dir "${COPIED_ROOT}/squeeze-compare-llm")"
    if [[ -n "${LLM_SRC}" ]]; then
      run_label="$(basename "${LLM_SRC}")"
      run_out="${RESULTS_DEST}/${run_label}"
      mkdir -p "${run_out}"
      rm -rf "${run_out}"
      cp -R "${LLM_SRC}" "${run_out}"
      log "PVC sync done (${reason}, layout=thin, llm-only): ${run_out}"
    else
      log "WARNING: squeeze-compare-llm present but no run-* found"
    fi
  else
    SINGLE_RUN="$(latest_numbered_run_dir "${COPIED_ROOT}")"
    if [[ -n "${SINGLE_RUN}" ]]; then
      local copy_base
      copy_base="$(basename "${SINGLE_RUN}")"
      mkdir -p "${RESULTS_DEST}"
      rm -rf "${RESULTS_DEST}/${copy_base}"
      cp -R "${SINGLE_RUN}" "${RESULTS_DEST}/${copy_base}"
      log "PVC sync done (${reason}, layout=thin, run=${copy_base})"
    else
      log "WARNING: no top-level run-* directory found on PVC under ${COPIED_ROOT}; nothing copied"
    fi
  fi

  if [[ "${RESULTS_PVC_SNAPSHOTS}" == "true" ]]; then
    mkdir -p "${SNAPSHOT_DIR}"
    cp -R "${COPIED_ROOT}/." "${SNAPSHOT_DIR}/"
    log "PVC snapshot written: ${SNAPSHOT_DIR}"
  fi

  kubectl -n "${NAMESPACE}" delete pod "${READER_POD}" --ignore-not-found >/dev/null
  rm -rf "${TMP_COPY_DIR}"
}

# Strip --sync-pvc-only for job launch; handle copy-only after sync_results_pvc_to_local exists.
SYNC_PVC_ONLY=false
PROFILE_ARGS=()
for arg in "$@"; do
  if [[ "${arg}" == "--sync-pvc-only" ]]; then
    SYNC_PVC_ONLY=true
  else
    PROFILE_ARGS+=("${arg}")
  fi
done
if [[ "${SYNC_PVC_ONLY}" == "true" ]]; then
  sync_results_pvc_to_local "sync_pvc_only"
  exit 0
fi
set -- "${PROFILE_ARGS[@]}"

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
  ./scripts/run_analyzer_job.sh ${EXTRA_ARGS+"${EXTRA_ARGS[@]}"}

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
  wait_ok=0
  job_still_running=0
  if wait_for_analyzer_job "${job_name}"; then
    wait_ok=1
  elif [[ "$(job_condition_status "${job_name}" Complete)" != "True" \
      && "$(job_condition_status "${job_name}" Failed)" != "True" ]]; then
    job_still_running=1
  fi
  if [[ "${wait_ok}" -eq 1 ]]; then
    log "${job_name} completed"
  else
    if [[ "${job_still_running}" -eq 1 ]]; then
      log "${job_name} still running after wait ended; collecting diagnostics (job not deleted)"
    else
      log "${job_name} failed; collecting diagnostics"
    fi
    kubectl -n "${NAMESPACE}" get job "${job_name}" || true
    kubectl -n "${NAMESPACE}" describe "job/${job_name}" || true
    kubectl -n "${NAMESPACE}" get pods -l job-name="${job_name}" -o wide || true
    save_job_logs "${job_name}" "${job_log}"
    log "saved failure logs to ${job_log}"
    if [[ "${CLEANUP_FAILED_JOBS}" == "true" && "${job_still_running}" -eq 0 ]]; then
      kubectl -n "${NAMESPACE}" delete job "${job_name}" --ignore-not-found >/dev/null || true
    fi
    if [[ -n "${log_pid}" ]]; then
      kill "${log_pid}" >/dev/null 2>&1 || true
      wait "${log_pid}" 2>/dev/null || true
    fi
    sync_results_pvc_to_local "job_failed_or_timeout profile=${p} job=${job_name}"
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
  sync_results_pvc_to_local "profile_ok profile=${p} job=${job_name}"
done

log "cluster-run finished (PVC was synced after each profile job, success or failure)"

if [[ "${CLEANUP_TERMINAL_PODS}" == "true" ]]; then
  kubectl -n "${NAMESPACE}" delete pod --field-selector=status.phase==Succeeded --ignore-not-found >/dev/null || true
  kubectl -n "${NAMESPACE}" delete pod --field-selector=status.phase==Failed --ignore-not-found >/dev/null || true
fi
