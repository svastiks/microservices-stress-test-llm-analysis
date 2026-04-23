#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="${NAMESPACE:-svastik}"
MON_NS="${MON_NS:-monitoring}"
CHART_PATH="${CHART_PATH:-./extra/robot-shop-msa/K8s/helm}"
if [[ ! -f "${CHART_PATH}/Chart.yaml" ]]; then
  CHART_PATH="./robot-shop/K8s/helm"
fi

echo "[deploy] using context: $(kubectl config current-context)"
echo "[deploy] namespace: ${NAMESPACE}"
echo "[deploy] chart path: ${CHART_PATH}"

kubectl get ns "${NAMESPACE}" >/dev/null
kubectl get ns "${MON_NS}" >/dev/null

echo "[deploy] installing/upgrading robot-shop Helm release..."
helm upgrade --install robot-shop "${CHART_PATH}" \
  --namespace "${NAMESPACE}" \
  --set image.repo=robotshop \
  --set image.version=latest \
  --set image.pullPolicy=IfNotPresent \
  --set nodeport=false \
  --set loadtest.enabled=false

echo "[deploy] applying optimizer-managed web deployment + hpa..."
kubectl apply -f "./k8s/spark/robot-shop-web-deployment.yaml"
kubectl apply -f "./k8s/spark/robot-shop-web-hpa.yaml"

echo "[deploy] applying analyzer RBAC..."
kubectl apply -f "./k8s/spark/analyzer-rbac.yaml"

echo "[deploy] waiting for web rollout..."
kubectl -n "${NAMESPACE}" rollout status deployment/web --timeout=300s

echo "[deploy] basic checks..."
kubectl -n "${NAMESPACE}" get deploy web
kubectl -n "${NAMESPACE}" get svc web
kubectl -n "${NAMESPACE}" get hpa web-hpa
kubectl -n "${MON_NS}" get svc my-kube-prometheus-stack-prometheus

echo "[deploy] done"
