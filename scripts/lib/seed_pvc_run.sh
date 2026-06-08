#!/usr/bin/env bash
# Copy a local squeeze run tree (iteration-*, cost-effective-boundary.json) onto analyzer PVC.
# Usage: seed_pvc_run <local_run_dir> <pvc_subdir>   # lands at /results/<subdir>/run-1/
# shellcheck shell=bash
seed_pvc_run() {
  local local_run="$1"
  local pvc_subdir="$2"
  local namespace="${NAMESPACE:-svastik}"
  local reader_pod="${READER_POD:-analyzer-results-reader}"
  local _lib
  _lib="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/kube_cluster.sh"
  # shellcheck source=scripts/lib/kube_cluster.sh
  source "${_lib}"
  ensure_kube_cluster

  if [[ ! -d "${local_run}" ]]; then
    echo "[seed-pvc] missing local run dir: ${local_run}" >&2
    return 1
  fi
  if [[ ! -f "${local_run}/cost-effective-boundary.json" ]]; then
    echo "[seed-pvc] missing cost-effective-boundary.json under ${local_run}" >&2
    return 1
  fi

  kubectl -n "${namespace}" delete pod "${reader_pod}" --ignore-not-found >/dev/null
  kubectl -n "${namespace}" apply -f - >/dev/null <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: ${reader_pod}
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

  if ! kubectl -n "${namespace}" wait --for=condition=Ready "pod/${reader_pod}" --timeout=120s >/dev/null; then
    echo "[seed-pvc] reader pod not Ready" >&2
    kubectl -n "${namespace}" delete pod "${reader_pod}" --ignore-not-found >/dev/null || true
    return 1
  fi

  kubectl -n "${namespace}" exec "${reader_pod}" -- sh -c "rm -rf /results/${pvc_subdir} && mkdir -p /results/${pvc_subdir}/run-1"
  kubectl -n "${namespace}" cp "${local_run}/." "${namespace}/${reader_pod}:/results/${pvc_subdir}/run-1/"
  kubectl -n "${namespace}" delete pod "${reader_pod}" --ignore-not-found >/dev/null
  echo "[seed-pvc] seeded /results/${pvc_subdir}/run-1 from ${local_run}"
}
