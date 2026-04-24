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
SQUEEZE_MAX_ITERATIONS="${SQUEEZE_MAX_ITERATIONS:-5}"
SUT_BASE_URL="${SUT_BASE_URL:-http://web.${NAMESPACE}.svc.cluster.local:8080}"

echo "[analyzer] context: $(kubectl config current-context)"
echo "[analyzer] namespace: ${NAMESPACE}"
echo "[analyzer] job: ${JOB_NAME}"

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
if [[ "${SQUEEZE_UNTIL_VIOLATION}" == "true" ]]; then
  DYNAMIC_SQUEEZE_FLAGS='"--until-violation"'
else
  DYNAMIC_SQUEEZE_FLAGS="\"--max-iterations\",\"${SQUEEZE_MAX_ITERATIONS}\""
fi

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
              \"low\",
              \"--script\",
              \"robotshop_login\",
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

kubectl set env -f "${MANIFEST}" --local -o yaml \
  RESULTS_DB_ENABLED="${RESULTS_DB_ENABLED:-false}" \
  RESULTS_DB_URI="${RESULTS_DB_URI:-mongodb://analyzer:change-me@analyzer-mongodb.svastik.svc.cluster.local:27017/admin}" \
  RESULTS_DB_NAME="${RESULTS_DB_NAME:-stress_analyzer}" > "${MANIFEST}.tmp"
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
