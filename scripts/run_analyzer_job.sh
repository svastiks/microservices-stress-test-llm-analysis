#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="${NAMESPACE:-svastik}"
JOB_NAME="${JOB_NAME:-stress-analyzer-run}"
JOB_YAML="${JOB_YAML:-./infra/k8s/spark/analyzer-job.yaml}"
ANALYZER_IMAGE="${ANALYZER_IMAGE:-}"
ANALYZER_IMAGE_PULL_POLICY="${ANALYZER_IMAGE_PULL_POLICY:-Always}"
IMAGE_PULL_SECRET="${IMAGE_PULL_SECRET:-}"
SERVICE_ACCOUNT="${SERVICE_ACCOUNT:-stress-analyzer}"
OPENAI_SECRET_NAME="${OPENAI_SECRET_NAME:-llm-api}"
RESULTS_PVC_YAML="${RESULTS_PVC_YAML:-./infra/k8s/spark/analyzer-results-pvc.yaml}"
SQUEEZE_UNTIL_VIOLATION="${SQUEEZE_UNTIL_VIOLATION:-false}"
SQUEEZE_MAX_ITERATIONS="${SQUEEZE_MAX_ITERATIONS:-8}"
SQUEEZE_SETTLE_SECONDS="${SQUEEZE_SETTLE_SECONDS:-30}"
COMPARE_SQUEEZE_OPTIMIZERS="${COMPARE_SQUEEZE_OPTIMIZERS:-false}"
COMPARE_HPA_VS_LLM="${COMPARE_HPA_VS_LLM:-false}"
COMPARE_ADVANCED_VS_VANILLA_LLM="${COMPARE_ADVANCED_VS_VANILLA_LLM:-false}"
STATIC_BASELINE="${STATIC_BASELINE:-false}"
REPLAY_TRAJECTORY="false"
SQUEEZE_FINAL_REPORT_LLM="${SQUEEZE_FINAL_REPORT_LLM:-false}"

for arg in "$@"; do
  if [[ "${arg}" == "--compare-squeeze-optimizers" ]]; then
    COMPARE_SQUEEZE_OPTIMIZERS="true"
  fi
  if [[ "${arg}" == "--compare-hpa-vs-llm" ]]; then
    COMPARE_HPA_VS_LLM="true"
  fi
  if [[ "${arg}" == "--compare-advanced-vs-vanilla-llm" ]]; then
    COMPARE_ADVANCED_VS_VANILLA_LLM="true"
  fi
  if [[ "${arg}" == "--static-baseline" ]]; then
    STATIC_BASELINE="true"
  fi
  if [[ "${arg}" == "--replay-trajectory" ]]; then
    REPLAY_TRAJECTORY="true"
  fi
done
_compare_count=0
[[ "${COMPARE_SQUEEZE_OPTIMIZERS}" == "true" ]] && _compare_count=$((_compare_count + 1))
[[ "${COMPARE_HPA_VS_LLM}" == "true" ]] && _compare_count=$((_compare_count + 1))
[[ "${COMPARE_ADVANCED_VS_VANILLA_LLM}" == "true" ]] && _compare_count=$((_compare_count + 1))
if (( _compare_count > 1 )); then
  echo "[analyzer] use only one compare mode flag at a time" >&2
  exit 1
fi
if [[ "${STATIC_BASELINE}" == "true" && "${_compare_count}" -gt 0 ]]; then
  echo "[analyzer] --static-baseline cannot be combined with compare flags" >&2
  exit 1
fi
if [[ "${REPLAY_TRAJECTORY}" == "true" && "${_compare_count}" -gt 0 ]]; then
  echo "[analyzer] --replay-trajectory cannot be combined with compare flags" >&2
  exit 1
fi
if [[ "${REPLAY_TRAJECTORY}" == "true" && "${STATIC_BASELINE}" == "true" ]]; then
  echo "[analyzer] --replay-trajectory cannot be combined with --static-baseline" >&2
  exit 1
fi
SUT_BASE_URL="${SUT_BASE_URL:-http://web.${NAMESPACE}.svc.cluster.local:8080}"
PROFILE="${PROFILE:-low}"
ANALYZER_SCRIPT="${ANALYZER_SCRIPT:-robotshop_login}"

echo "[analyzer] context: $(kubectl config current-context)"
echo "[analyzer] namespace: ${NAMESPACE}"
echo "[analyzer] job: ${JOB_NAME}"
echo "[analyzer] profile: ${PROFILE}"
echo "[analyzer] script: ${ANALYZER_SCRIPT}"
echo "[analyzer] squeeze: until_violation=${SQUEEZE_UNTIL_VIOLATION} max_iterations=${SQUEEZE_MAX_ITERATIONS} settle_seconds=${SQUEEZE_SETTLE_SECONDS} compare_optimizers=${COMPARE_SQUEEZE_OPTIMIZERS} compare_hpa_vs_llm=${COMPARE_HPA_VS_LLM} compare_advanced_vs_vanilla=${COMPARE_ADVANCED_VS_VANILLA_LLM} static_baseline=${STATIC_BASELINE} final_report_llm=${SQUEEZE_FINAL_REPORT_LLM}"

if [[ ! -f "${JOB_YAML}" ]]; then
  echo "[analyzer] job yaml not found: ${JOB_YAML}" >&2
  exit 1
fi

if [[ ! -f "${RESULTS_PVC_YAML}" ]]; then
  echo "[analyzer] results pvc yaml not found: ${RESULTS_PVC_YAML}" >&2
  exit 1
fi

if ! kubectl -n "${NAMESPACE}" get serviceaccount "${SERVICE_ACCOUNT}" >/dev/null 2>&1; then
  echo "[analyzer] missing serviceaccount '${SERVICE_ACCOUNT}' in namespace '${NAMESPACE}'" >&2
  echo "[analyzer] run: kubectl apply -f infra/k8s/spark/analyzer-rbac.yaml" >&2
  exit 1
fi

if ! kubectl -n "${NAMESPACE}" get secret "${OPENAI_SECRET_NAME}" >/dev/null 2>&1; then
  echo "[analyzer] missing secret '${OPENAI_SECRET_NAME}' in namespace '${NAMESPACE}'" >&2
  echo "[analyzer] run: kubectl -n ${NAMESPACE} create secret generic ${OPENAI_SECRET_NAME} --from-literal=OPENAI_API_KEY=..." >&2
  exit 1
fi

if [[ -n "${ANALYZER_IMAGE}" && "${ANALYZER_IMAGE}" == *"<"* ]]; then
  echo "[analyzer] ANALYZER_IMAGE still contains placeholder angle brackets: ${ANALYZER_IMAGE}" >&2
  exit 1
fi

echo "[analyzer] ensuring results pvc..."
kubectl apply -f "${RESULTS_PVC_YAML}" >/dev/null

MANIFEST="$(mktemp)"
trap 'rm -f "${MANIFEST}" "${MANIFEST}.tmp"' EXIT
cp "${JOB_YAML}" "${MANIFEST}"

kubectl patch --local -f "${MANIFEST}" --type merge -p \
  "{\"metadata\":{\"name\":\"${JOB_NAME}\",\"namespace\":\"${NAMESPACE}\"}}" -o yaml > "${MANIFEST}.tmp"
mv "${MANIFEST}.tmp" "${MANIFEST}"

if [[ -n "${ANALYZER_IMAGE}" ]]; then
  echo "[analyzer] using image: ${ANALYZER_IMAGE}"
  kubectl set image -f "${MANIFEST}" runner="${ANALYZER_IMAGE}" --local -o yaml > "${MANIFEST}.tmp"
else
  echo "[analyzer] using imagePullPolicy: ${ANALYZER_IMAGE_PULL_POLICY}"
  cp "${MANIFEST}" "${MANIFEST}.tmp"
fi
mv "${MANIFEST}.tmp" "${MANIFEST}"

kubectl patch --local -f "${MANIFEST}" --type strategic -p \
  "{\"spec\":{\"template\":{\"spec\":{\"containers\":[{\"name\":\"runner\",\"imagePullPolicy\":\"${ANALYZER_IMAGE_PULL_POLICY}\"}]}}}}" -o yaml > "${MANIFEST}.tmp"
mv "${MANIFEST}.tmp" "${MANIFEST}"

# Configure squeeze stop mode without manual YAML edits.
# With --until-violation, start.py still needs --max-iterations as a hard ceiling (UP recovery + safety).
if [[ "${SQUEEZE_UNTIL_VIOLATION}" == "true" ]]; then
  DYNAMIC_SQUEEZE_FLAGS='"--until-violation","--max-iterations","'"${SQUEEZE_MAX_ITERATIONS}"'"'
else
  DYNAMIC_SQUEEZE_FLAGS="\"--max-iterations\",\"${SQUEEZE_MAX_ITERATIONS}\""
fi

if [[ "${COMPARE_HPA_VS_LLM}" == "true" ]]; then
  kubectl patch --local -f "${MANIFEST}" --type strategic -p "{
    \"spec\":{
      \"template\":{
        \"spec\":{
          \"containers\":[
            {
              \"name\":\"runner\",
              \"command\":[
                \"python3\",
                \"start.py\",
                \"--compare-hpa-vs-llm\",
                \"--profile\",
                \"${PROFILE}\",
                \"--script\",
                \"${ANALYZER_SCRIPT}\",
                ${DYNAMIC_SQUEEZE_FLAGS},
                \"--settle-seconds\",
                \"${SQUEEZE_SETTLE_SECONDS}\",
                \"--efficiency\",
                \"--k8s-namespace\",
                \"${NAMESPACE}\",
                \"--k8s-deployment\",
                \"web\",
                \"--base-url\",
                \"${SUT_BASE_URL}\",
                \"--deployment-yaml\",
                \"infra/k8s/spark/robot-shop-web-deployment.yaml\",
                \"--hpa-yaml\",
                \"infra/k8s/spark/robot-shop-web-hpa.yaml\",
                \"--prometheus-url\",
                \"http://my-kube-prometheus-stack-prometheus.monitoring.svc:9090\"
              ]
            }
          ]
        }
      }
    }
  }" -o yaml > "${MANIFEST}.tmp"
  mv "${MANIFEST}.tmp" "${MANIFEST}"
elif [[ "${COMPARE_SQUEEZE_OPTIMIZERS}" == "true" ]]; then
  FINAL_REPORT_JSON=""
  if [[ "${SQUEEZE_FINAL_REPORT_LLM}" == "true" ]]; then
    FINAL_REPORT_JSON=',"--squeeze-final-report-llm"'
  fi
  COMPARE_FORMULA_MAX_ITER="${SQUEEZE_COMPARE_FORMULA_MAX_ITERATIONS:-3}"
  kubectl patch --local -f "${MANIFEST}" --type strategic -p "{
    \"spec\":{
      \"template\":{
        \"spec\":{
          \"containers\":[
            {
              \"name\":\"runner\",
              \"command\":[
                \"python3\",
                \"start.py\",
                \"--compare-squeeze-optimizers\",
                \"--compare-formula-max-iterations\",
                \"${COMPARE_FORMULA_MAX_ITER}\",
                \"--profile\",
                \"${PROFILE}\",
                \"--script\",
                \"${ANALYZER_SCRIPT}\",
                ${DYNAMIC_SQUEEZE_FLAGS},
                \"--settle-seconds\",
                \"${SQUEEZE_SETTLE_SECONDS}\",
                \"--efficiency\",
                \"--k8s-namespace\",
                \"${NAMESPACE}\",
                \"--k8s-deployment\",
                \"web\",
                \"--base-url\",
                \"${SUT_BASE_URL}\",
                \"--deployment-yaml\",
                \"infra/k8s/spark/robot-shop-web-deployment.yaml\",
                \"--hpa-yaml\",
                \"infra/k8s/spark/robot-shop-web-hpa.yaml\",
                \"--prometheus-url\",
                \"http://my-kube-prometheus-stack-prometheus.monitoring.svc:9090\"
                ${FINAL_REPORT_JSON}
              ]
            }
          ]
        }
      }
    }
  }" -o yaml > "${MANIFEST}.tmp"
  mv "${MANIFEST}.tmp" "${MANIFEST}"
elif [[ "${COMPARE_ADVANCED_VS_VANILLA_LLM}" == "true" ]]; then
  kubectl patch --local -f "${MANIFEST}" --type strategic -p "{
    \"spec\":{
      \"template\":{
        \"spec\":{
          \"containers\":[
            {
              \"name\":\"runner\",
              \"command\":[
                \"python3\",
                \"start.py\",
                \"--compare-advanced-vs-vanilla-llm\",
                \"--profile\",
                \"${PROFILE}\",
                \"--script\",
                \"${ANALYZER_SCRIPT}\",
                ${DYNAMIC_SQUEEZE_FLAGS},
                \"--settle-seconds\",
                \"${SQUEEZE_SETTLE_SECONDS}\",
                \"--efficiency\",
                \"--k8s-namespace\",
                \"${NAMESPACE}\",
                \"--k8s-deployment\",
                \"web\",
                \"--base-url\",
                \"${SUT_BASE_URL}\",
                \"--deployment-yaml\",
                \"infra/k8s/spark/robot-shop-web-deployment.yaml\",
                \"--hpa-yaml\",
                \"infra/k8s/spark/robot-shop-web-hpa.yaml\",
                \"--prometheus-url\",
                \"http://my-kube-prometheus-stack-prometheus.monitoring.svc:9090\"
              ]
            }
          ]
        }
      }
    }
  }" -o yaml > "${MANIFEST}.tmp"
  mv "${MANIFEST}.tmp" "${MANIFEST}"
elif [[ "${REPLAY_TRAJECTORY}" == "true" ]]; then
  REPLAY_SOURCE_ARG="${REPLAY_SOURCE_PATH:-/app/results/squeeze-formula-source/run-1}"
  kubectl patch --local -f "${MANIFEST}" --type strategic -p "{
    \"spec\":{
      \"template\":{
        \"spec\":{
          \"containers\":[
            {
              \"name\":\"runner\",
              \"command\":[
                \"python3\",
                \"start.py\",
                \"--replay-trajectory\",
                \"--replay-source\",
                \"${REPLAY_SOURCE_ARG}\",
                \"--profile\",
                \"${PROFILE}\",
                \"--script\",
                \"${ANALYZER_SCRIPT}\",
                \"--settle-seconds\",
                \"${SQUEEZE_SETTLE_SECONDS}\",
                \"--efficiency\",
                \"--k8s-namespace\",
                \"${NAMESPACE}\",
                \"--k8s-deployment\",
                \"web\",
                \"--base-url\",
                \"${SUT_BASE_URL}\",
                \"--deployment-yaml\",
                \"infra/k8s/spark/robot-shop-web-deployment.yaml\",
                \"--hpa-yaml\",
                \"infra/k8s/spark/robot-shop-web-hpa.yaml\",
                \"--prometheus-url\",
                \"http://my-kube-prometheus-stack-prometheus.monitoring.svc:9090\"
              ]
            }
          ]
        }
      }
    }
  }" -o yaml > "${MANIFEST}.tmp"
  mv "${MANIFEST}.tmp" "${MANIFEST}"
elif [[ "${STATIC_BASELINE}" == "true" ]]; then
  kubectl patch --local -f "${MANIFEST}" --type strategic -p "{
    \"spec\":{
      \"template\":{
        \"spec\":{
          \"containers\":[
            {
              \"name\":\"runner\",
              \"command\":[
                \"python3\",
                \"start.py\",
                \"--profile\",
                \"${PROFILE}\",
                \"--script\",
                \"${ANALYZER_SCRIPT}\",
                \"--efficiency\",
                \"--k8s-namespace\",
                \"${NAMESPACE}\",
                \"--k8s-deployment\",
                \"web\",
                \"--base-url\",
                \"${SUT_BASE_URL}\",
                \"--deployment-yaml\",
                \"infra/k8s/spark/robot-shop-web-deployment.yaml\",
                \"--hpa-yaml\",
                \"infra/k8s/spark/robot-shop-web-hpa.yaml\",
                \"--prometheus-url\",
                \"http://my-kube-prometheus-stack-prometheus.monitoring.svc:9090\",
                \"--squeeze-optimizer\",
                \"formula\"
              ]
            }
          ]
        }
      }
    }
  }" -o yaml > "${MANIFEST}.tmp"
  mv "${MANIFEST}.tmp" "${MANIFEST}"
else
  kubectl patch --local -f "${MANIFEST}" --type strategic -p "{
    \"spec\":{
      \"template\":{
        \"spec\":{
          \"containers\":[
            {
              \"name\":\"runner\",
              \"command\":[
                \"python3\",
                \"start.py\",
                \"--profile\",
                \"${PROFILE}\",
                \"--script\",
                \"${ANALYZER_SCRIPT}\",
                \"--squeeze\",
                ${DYNAMIC_SQUEEZE_FLAGS},
                \"--efficiency\",
                \"--k8s-namespace\",
                \"${NAMESPACE}\",
                \"--k8s-deployment\",
                \"web\",
                \"--base-url\",
                \"${SUT_BASE_URL}\",
                \"--deployment-yaml\",
                \"infra/k8s/spark/robot-shop-web-deployment.yaml\",
                \"--hpa-yaml\",
                \"infra/k8s/spark/robot-shop-web-hpa.yaml\",
                \"--prometheus-url\",
                \"http://my-kube-prometheus-stack-prometheus.monitoring.svc:9090\"
              ]
            }
          ]
        }
      }
    }
  }" -o yaml > "${MANIFEST}.tmp"
  mv "${MANIFEST}.tmp" "${MANIFEST}"
fi

SET_ENV_CMD=(
  kubectl set env -f "${MANIFEST}" --local -o yaml
  RESULTS_DB_ENABLED="${RESULTS_DB_ENABLED:-false}"
  RESULTS_DB_URI="${RESULTS_DB_URI:-mongodb://analyzer:change-me@analyzer-mongodb.svastik.svc.cluster.local:27017/admin}"
  RESULTS_DB_NAME="${RESULTS_DB_NAME:-stress_analyzer}"
  SQUEEZE_SETTLE_SECONDS="${SQUEEZE_SETTLE_SECONDS}"
)
if [[ -n "${STRESS_K6_RPS:-}" ]]; then
  SET_ENV_CMD+=(STRESS_K6_RPS="${STRESS_K6_RPS}")
fi
if [[ -n "${STRESS_K6_DURATION:-}" ]]; then
  SET_ENV_CMD+=(STRESS_K6_DURATION="${STRESS_K6_DURATION}")
fi
if [[ -n "${SQUEEZE_COMPARE_FORMULA_UNTIL_VIOLATION:-}" ]]; then
  SET_ENV_CMD+=(SQUEEZE_COMPARE_FORMULA_UNTIL_VIOLATION="${SQUEEZE_COMPARE_FORMULA_UNTIL_VIOLATION}")
fi
if [[ -n "${SQUEEZE_LLM_DOWN_BOUNDARY:-}" ]]; then
  SET_ENV_CMD+=(SQUEEZE_LLM_DOWN_BOUNDARY="${SQUEEZE_LLM_DOWN_BOUNDARY}")
fi
if [[ -n "${SQUEEZE_LLM_PURE+x}" ]]; then
  SET_ENV_CMD+=(SQUEEZE_LLM_PURE="${SQUEEZE_LLM_PURE}")
fi
if [[ -n "${SQUEEZE_CPU_UTIL_FAIL_PCT:-}" ]]; then
  SET_ENV_CMD+=(SQUEEZE_CPU_UTIL_FAIL_PCT="${SQUEEZE_CPU_UTIL_FAIL_PCT}")
fi
if [[ -n "${SQUEEZE_LLM_CPU_GUARD_PCT:-}" ]]; then
  SET_ENV_CMD+=(SQUEEZE_LLM_CPU_GUARD_PCT="${SQUEEZE_LLM_CPU_GUARD_PCT}")
fi
if [[ -n "${SQUEEZE_LLM_P95_REGRESSION_RATIO:-}" ]]; then
  SET_ENV_CMD+=(SQUEEZE_LLM_P95_REGRESSION_RATIO="${SQUEEZE_LLM_P95_REGRESSION_RATIO}")
fi
if [[ -n "${SQUEEZE_WAIT_REPLICAS_STEADY:-}" ]]; then
  SET_ENV_CMD+=(SQUEEZE_WAIT_REPLICAS_STEADY="${SQUEEZE_WAIT_REPLICAS_STEADY}")
fi
if [[ -n "${SQUEEZE_ROLLOUT_RESTART_BEFORE_OBSERVE:-}" ]]; then
  SET_ENV_CMD+=(SQUEEZE_ROLLOUT_RESTART_BEFORE_OBSERVE="${SQUEEZE_ROLLOUT_RESTART_BEFORE_OBSERVE}")
fi
if [[ -n "${SQUEEZE_WARMUP_K6_DURATION:-}" ]]; then
  SET_ENV_CMD+=(SQUEEZE_WARMUP_K6_DURATION="${SQUEEZE_WARMUP_K6_DURATION}")
fi
if [[ -n "${SQUEEZE_COMPARE_PAIRED_MEASURE:-}" ]]; then
  SET_ENV_CMD+=(SQUEEZE_COMPARE_PAIRED_MEASURE="${SQUEEZE_COMPARE_PAIRED_MEASURE}")
fi
if [[ -n "${SQUEEZE_COMPARE_PAIRED_BURN_TOLERANCE_PCT:-}" ]]; then
  SET_ENV_CMD+=(SQUEEZE_COMPARE_PAIRED_BURN_TOLERANCE_PCT="${SQUEEZE_COMPARE_PAIRED_BURN_TOLERANCE_PCT}")
fi
if [[ -n "${SQUEEZE_UNTIL_VIOLATION_PROBE_LLM:-}" ]]; then
  SET_ENV_CMD+=(SQUEEZE_UNTIL_VIOLATION_PROBE_LLM="${SQUEEZE_UNTIL_VIOLATION_PROBE_LLM}")
fi
if [[ -n "${STRESS_RESULTS_SUBDIR:-}" ]]; then
  SET_ENV_CMD+=(STRESS_RESULTS_SUBDIR="${STRESS_RESULTS_SUBDIR}")
fi
if [[ -n "${SQUEEZE_OPTIMIZER:-}" ]]; then
  SET_ENV_CMD+=(SQUEEZE_OPTIMIZER="${SQUEEZE_OPTIMIZER}")
fi
if [[ "${COMPARE_HPA_VS_LLM}" == "true" ]]; then
  SET_ENV_CMD+=(
    SQUEEZE_COMPARE_SUBDIR_HPA="${SQUEEZE_COMPARE_SUBDIR_HPA:-squeeze-compare-hpa}"
    SQUEEZE_COMPARE_SUBDIR_LLM="${SQUEEZE_COMPARE_SUBDIR_LLM:-squeeze-compare-llm}"
    SQUEEZE_COMPARE_PRUNE_STALE_FORMULA="${SQUEEZE_COMPARE_PRUNE_STALE_FORMULA:-1}"
  )
fi
if [[ "${COMPARE_ADVANCED_VS_VANILLA_LLM}" == "true" ]]; then
  SET_ENV_CMD+=(
    SQUEEZE_COMPARE_SUBDIR_ADVANCED="${SQUEEZE_COMPARE_SUBDIR_ADVANCED:-squeeze-compare-advanced-llm}"
    SQUEEZE_COMPARE_SUBDIR_VANILLA="${SQUEEZE_COMPARE_SUBDIR_VANILLA:-squeeze-compare-vanilla-llm}"
    SQUEEZE_COMPARE_CONTINUE_ON_ADVANCED_FAIL="${SQUEEZE_COMPARE_CONTINUE_ON_ADVANCED_FAIL:-1}"
    SQUEEZE_COMPARE_PRUNE_PRIOR="${SQUEEZE_COMPARE_PRUNE_PRIOR:-1}"
    SQUEEZE_COMPARE_PRUNE_STALE_FORMULA="${SQUEEZE_COMPARE_PRUNE_STALE_FORMULA:-1}"
    SQUEEZE_LLM_PURE="${SQUEEZE_LLM_PURE:-1}"
    SQUEEZE_LLM_DOWN_BOUNDARY="${SQUEEZE_LLM_DOWN_BOUNDARY:-0}"
    SQUEEZE_UP_RECOVERY_MAX_REPLICAS="${SQUEEZE_UP_RECOVERY_MAX_REPLICAS:-6}"
    SQUEEZE_ROLLOUT_TIMEOUT_S="${SQUEEZE_ROLLOUT_TIMEOUT_S:-600}"
    SQUEEZE_CPU_UTIL_FAIL_PCT="${SQUEEZE_CPU_UTIL_FAIL_PCT:-95}"
    SQUEEZE_UNTIL_VIOLATION="${SQUEEZE_UNTIL_VIOLATION}"
    SQUEEZE_MAX_ITERATIONS="${SQUEEZE_MAX_ITERATIONS}"
    SQUEEZE_SETTLE_SECONDS="${SQUEEZE_SETTLE_SECONDS}"
  )
fi
if [[ -n "${COMPARE_SYNC_MODE:-}" ]]; then
  SET_ENV_CMD+=(COMPARE_SYNC_MODE="${COMPARE_SYNC_MODE}")
fi
if [[ "${STATIC_BASELINE}" == "true" ]]; then
  SET_ENV_CMD+=(STRESS_RESULTS_SUBDIR="${STRESS_RESULTS_SUBDIR:-static-baseline}")
  if [[ -n "${COMPARE_SWEEP_ROUND:-}" ]]; then
    SET_ENV_CMD+=(STRESS_RESULTS_RUN_LABEL="run-${COMPARE_SWEEP_ROUND}")
  fi
fi
"${SET_ENV_CMD[@]}" > "${MANIFEST}.tmp"
mv "${MANIFEST}.tmp" "${MANIFEST}"

if [[ -n "${IMAGE_PULL_SECRET}" ]]; then
  echo "[analyzer] using imagePullSecret: ${IMAGE_PULL_SECRET}"
  kubectl patch --local -f "${MANIFEST}" --type merge -p \
    "{\"spec\":{\"template\":{\"spec\":{\"imagePullSecrets\":[{\"name\":\"${IMAGE_PULL_SECRET}\"}]}}}}" -o yaml > "${MANIFEST}.tmp"
  mv "${MANIFEST}.tmp" "${MANIFEST}"
fi

echo "[analyzer] recreating job..."
kubectl -n "${NAMESPACE}" delete job "${JOB_NAME}" --ignore-not-found >/dev/null
kubectl apply -f "${MANIFEST}"

echo "[analyzer] launched; follow logs with:"
echo "kubectl -n ${NAMESPACE} logs -f job/${JOB_NAME}"
