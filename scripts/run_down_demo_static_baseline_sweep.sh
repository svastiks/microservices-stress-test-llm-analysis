#!/usr/bin/env bash
# DOWN static / engineer baseline sweep (fat deployment + HPA; no LLM loop).
#
# Default baseline: robot-shop-web-deployment.baseline.yaml (5 repl @ 150m/75Mi).
# Thin UP-style baseline is wrong for DOWN — use this script, not static-up, for Method 2 DOWN.
#
# Example (5 loads × 10 repeats = 50 rounds):
#   BUILD_ANALYZER_IMAGE=true \
#   COMPARE_SWEEP_LOADS=20,25,35,45,55 COMPARE_SWEEP_REPEATS_PER_LOAD=10 \
#   COMPARE_SWEEP_K6_DURATION=90s \
#   ./scripts/run_down_demo_static_baseline_sweep.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

: "${COMPARE_SWEEP_BASE_PROFILE:=down_demo}"
: "${COMPARE_SWEEP_RPS:=25,35,45,55}"

SWEEP_STAMP="$(date +%Y%m%d-%H%M%S)"
SWEEP_PARENT="${COMPARE_SWEEP_PARENT:-${ROOT}/results-from-cluster}"
SWEEP_ROOT="${SWEEP_PARENT}/static-down-sweep-${SWEEP_STAMP}"
mkdir -p "${SWEEP_ROOT}"

# shellcheck source=scripts/lib/expand_compare_sweep_matrix.sh
source "${ROOT}/scripts/lib/expand_compare_sweep_matrix.sh"
if ! parse_compare_sweep_rps_matrix "${COMPARE_SWEEP_RPS}"; then
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

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [static-down-sweep] $*"; }

export RESULTS_DEST="${SWEEP_ROOT}"
export BASELINE_DEPLOYMENT_YAML="${BASELINE_DEPLOYMENT_YAML:-${ROOT}/infra/k8s/spark/robot-shop-web-deployment.baseline.yaml}"
export BASELINE_HPA_YAML="${BASELINE_HPA_YAML:-${ROOT}/infra/k8s/spark/robot-shop-web-hpa.baseline.yaml}"
export RESET_BASELINE_EACH_PROFILE=true
export COMPARE_SYNC_MODE=static
export STRESS_RESULTS_SUBDIR=static-baseline
unset SQUEEZE_LLM_PURE SQUEEZE_COMPARE_FORMULA_UNTIL_VIOLATION SQUEEZE_COMPARE_FORMULA_MAX_ITERATIONS 2>/dev/null || true

log "sweep root: ${SWEEP_ROOT} profile=${COMPARE_SWEEP_BASE_PROFILE} rounds=${ROUNDS}"
log "baseline deployment=${BASELINE_DEPLOYMENT_YAML}"
log "baseline hpa=${BASELINE_HPA_YAML}"
if [[ "${COMPARE_SWEEP_SHUFFLE_ROUNDS:-}" == "1" ]]; then
  log "round order: shuffled (seed=${COMPARE_SWEEP_SHUFFLE_SEED:-random})"
fi

any_fail=0
for ((r = 0; r < ROUNDS; r++)); do
  idx=$((r + 1))
  export COMPARE_SWEEP_ROUND="${idx}"
  export STRESS_K6_RPS="${CLEAN_RPS[r]}"
  export PROFILES_CSV="${COMPARE_SWEEP_BASE_PROFILE}"
  log "=== round ${idx}/${ROUNDS} ${ROUND_LABELS[r]} STRESS_K6_RPS=${STRESS_K6_RPS} (static-baseline) ==="

  round_ok=1
  if ! ./scripts/run_cluster_profiles.sh --static-baseline; then
    log "ERROR: round ${idx} failed"
    round_ok=0
    any_fail=1
  fi

  run_label="run-${idx}"
  if [[ -f "${SWEEP_ROOT}/.last_sync_r${idx}.txt" ]]; then
    run_label="$(tr -d '\r\n' < "${SWEEP_ROOT}/.last_sync_r${idx}.txt")"
  fi
  status="OK"
  if [[ "${round_ok}" -eq 0 ]]; then
    status="FAILED"
  fi
  {
    echo "round=${idx}/${ROUNDS}"
    echo "status=${status}"
    echo "label=${ROUND_LABELS[r]}"
    echo "STRESS_K6_RPS=${STRESS_K6_RPS}"
    echo "PROFILES_CSV=${PROFILES_CSV}"
    echo "run_dir=${SWEEP_ROOT}/${run_label}"
    echo "experiment_json=${SWEEP_ROOT}/${run_label}/experiment.json"
    echo "finished_utc=$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  } > "${SWEEP_ROOT}/sweep-round-${idx}.txt"
done
unset COMPARE_SWEEP_ROUND 2>/dev/null || true
[[ "${any_fail}" -eq 0 ]] || exit 1
log "done"
