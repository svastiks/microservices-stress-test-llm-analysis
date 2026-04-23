#!/usr/bin/env bash
set -euo pipefail

# Prints shell export lines derived from current kube context.
# Usage:
#   eval "$(./scripts/detect_cluster_vars.sh)"
# Optional overrides:
#   NAMESPACE=svastik JOB_NAME=stress-analyzer-run SA_NAME=stress-analyzer ./scripts/detect_cluster_vars.sh

NAMESPACE="${NAMESPACE:-svastik}"
JOB_NAME="${JOB_NAME:-stress-analyzer-run}"
SA_NAME="${SA_NAME:-stress-analyzer}"
JOB_YAML_PATH="${JOB_YAML_PATH:-k8s/spark/analyzer-job.yaml}"

jsonpath() {
  local resource="$1"
  local path="$2"
  kubectl get "${resource}" -o "jsonpath=${path}" 2>/dev/null || true
}

echo "export KUBE_CONTEXT='$(kubectl config current-context 2>/dev/null || true)'"
echo "export KUBE_NAMESPACE='${NAMESPACE}'"

if kubectl get ns "${NAMESPACE}" >/dev/null 2>&1; then
  echo "export NAMESPACE_EXISTS='true'"
else
  echo "export NAMESPACE_EXISTS='false'"
fi

JOB_IMAGE="$(jsonpath "job/${JOB_NAME} -n ${NAMESPACE}" '{.spec.template.spec.containers[0].image}')"
JOB_PULL_POLICY="$(jsonpath "job/${JOB_NAME} -n ${NAMESPACE}" '{.spec.template.spec.containers[0].imagePullPolicy}')"
JOB_PULL_SECRET="$(jsonpath "job/${JOB_NAME} -n ${NAMESPACE}" '{.spec.template.spec.imagePullSecrets[0].name}')"

SA_PULL_SECRET="$(jsonpath "sa/${SA_NAME} -n ${NAMESPACE}" '{.imagePullSecrets[0].name}')"

if [[ -z "${JOB_IMAGE}" && -f "${JOB_YAML_PATH}" ]]; then
  JOB_IMAGE="$(kubectl create --dry-run=client -f "${JOB_YAML_PATH}" -o jsonpath='{.spec.template.spec.containers[0].image}' 2>/dev/null || true)"
  JOB_PULL_POLICY="$(kubectl create --dry-run=client -f "${JOB_YAML_PATH}" -o jsonpath='{.spec.template.spec.containers[0].imagePullPolicy}' 2>/dev/null || true)"
  JOB_PULL_SECRET="$(kubectl create --dry-run=client -f "${JOB_YAML_PATH}" -o jsonpath='{.spec.template.spec.imagePullSecrets[0].name}' 2>/dev/null || true)"
fi

echo "export JOB_NAME='${JOB_NAME}'"
echo "export SA_NAME='${SA_NAME}'"
echo "export JOB_YAML_PATH='${JOB_YAML_PATH}'"
echo "export ANALYZER_IMAGE='${JOB_IMAGE}'"
echo "export ANALYZER_IMAGE_PULL_POLICY='${JOB_PULL_POLICY}'"
echo "export JOB_IMAGE_PULL_SECRET='${JOB_PULL_SECRET}'"
echo "export SA_IMAGE_PULL_SECRET='${SA_PULL_SECRET}'"

if [[ -n "${JOB_IMAGE}" ]]; then
  if [[ "${JOB_IMAGE}" == *"/"* ]]; then
    echo "export IMAGE_SOURCE_HINT='registry'"
  else
    echo "export IMAGE_SOURCE_HINT='node-local'"
  fi
else
  echo "export IMAGE_SOURCE_HINT='unknown'"
fi
