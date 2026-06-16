#!/usr/bin/env bash
# Step 3: deploy derived engineer YAML + one k6 verify pass in cluster.
#
# Prereq: ./scripts/derive_engineer_baseline.sh <profiling-experiment.json>
#
# Usage:
#   BUILD_ANALYZER_IMAGE=true KUBE_CONTEXT=monitoring \
#   COMPARE_SWEEP_K6_DURATION=90s \
#   ./scripts/run_engineer_derived_verify.sh \
#     artifacts_latest/.../iteration-1/engineer-baseline
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

BASELINE_DIR="${1:?usage: $0 <engineer-baseline-dir>}"
BASELINE_DIR="$(cd "${BASELINE_DIR}" && pwd)"

DEP="${BASELINE_DIR}/engineer-deployment.yaml"
HPA="${BASELINE_DIR}/engineer-hpa.yaml"
META="${BASELINE_DIR}/engineer-baseline.json"

if [[ ! -f "${DEP}" || ! -f "${HPA}" || ! -f "${META}" ]]; then
  echo "missing engineer-baseline outputs in ${BASELINE_DIR}" >&2
  echo "run: ./scripts/derive_engineer_baseline.sh <profiling-experiment.json>" >&2
  exit 1
fi

if [[ -f ".env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source ".env"
  set +a
fi
if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  echo "OPENAI_API_KEY is required" >&2
  exit 1
fi

read -r RPS PROFILE <<<"$(python3 - <<PY
import json
meta = json.load(open("${META}"))
rps = int(meta.get("target_rps") or 0)
profile = "up_demo" if rps >= 100 else "down_demo"
print(rps, profile)
PY
)"

STAMP="$(date +%Y%m%d-%H%M%S)"
SWEEP_ROOT="${ENGINEER_VERIFY_SWEEP_ROOT:-${ROOT}/results-from-cluster/engineer-verify-${STAMP}}"
mkdir -p "${SWEEP_ROOT}"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [engineer-verify] $*"; }

log "baseline dir: ${BASELINE_DIR}"
log "deploy: ${DEP}"
log "hpa: ${HPA}"
log "rps=${RPS} profile=${PROFILE}"
log "sweep root: ${SWEEP_ROOT}"

export RESULTS_DEST="${SWEEP_ROOT}"
export BASELINE_DEPLOYMENT_YAML="${DEP}"
export BASELINE_HPA_YAML="${HPA}"
export COMPARE_SWEEP_BASE_PROFILE="${PROFILE}"
export PROFILES_CSV="${PROFILE}"
export STRESS_K6_RPS="${RPS}"
export COMPARE_SWEEP_ROUND=1
export RESET_BASELINE_EACH_PROFILE=true
export COMPARE_SYNC_MODE=static
export STRESS_RESULTS_SUBDIR=engineer-derived-verify

if ! ./scripts/run_cluster_profiles.sh --static-baseline; then
  log "ERROR: cluster verify failed"
  exit 1
fi

VERIFY_OUT="${BASELINE_DIR}/verify-run"
RUN_DIR="${SWEEP_ROOT}/run-1"
if [[ ! -f "${RUN_DIR}/experiment.json" ]]; then
  log "ERROR: expected ${RUN_DIR}/experiment.json after sync"
  exit 1
fi

rm -rf "${VERIFY_OUT}"
mkdir -p "${VERIFY_OUT}"
cp -R "${RUN_DIR}/." "${VERIFY_OUT}/"
cp "${META}" "${VERIFY_OUT}/engineer-baseline-derived.json"

python3 - <<PY
import json
from pathlib import Path

exp = json.loads(Path("${VERIFY_OUT}/experiment.json").read_text())
derived = json.loads(Path("${META}").read_text())
cfg = exp.get("config") or {}
cost = exp.get("cost") or {}
fail = exp.get("failure") or {}
status = "FAIL" if fail.get("failed") else "PASS"
print(
    f"verify {status}: {cfg.get('deployment_replicas')}×"
    f"{cfg.get('cpu_request_m')}m/{cfg.get('mem_request_mib')}Mi "
    f"measured_prov_cost={cost.get('cost_score')} "
    f"derived_prov_cost={(derived.get('cost') or {}).get('cost_score')}"
)
PY

log "verify-run synced → ${VERIFY_OUT}"
log "next: ./scripts/build_engineer_vs_advanced_comparisons.sh"
