#!/usr/bin/env bash
# Validate cross-arm metric theory: formula-only DOWN squeeze, then replay the same
# configs (observe-only) and compare burn / cpu% / PASS-FAIL per iteration.
#
# Usage:
#   BUILD_ANALYZER_IMAGE=true KUBE_CONTEXT=monitoring \
#     COMPARE_SWEEP_K6_DURATION=90s SQUEEZE_SETTLE_SECONDS=30 STRESS_K6_RPS=25 \
#     ./scripts/run_down_demo_formula_replay_validate.sh
#
# Artifacts under results-from-cluster/formula-replay-validate-<stamp>/:
#   source/squeeze-formula-source/   formula trajectory (cost-effective-boundary.json, iteration-*)
#   replay/squeeze-formula-replay/   replay k6 runs + replay-comparison.md
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

STAMP="$(date +%Y%m%d-%H%M%S)"
OUT_PARENT="${REPLAY_VALIDATE_PARENT:-${ROOT}/results-from-cluster}"
VALIDATE_ROOT="${OUT_PARENT}/formula-replay-validate-${STAMP}"
mkdir -p "${VALIDATE_ROOT}"

if [[ -f ".env" ]]; then
  # shellcheck disable=SC1091
  set -a
  source ".env"
  set +a
fi

if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  echo "OPENAI_API_KEY is required (env or .env)" >&2
  exit 1
fi

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] [formula-replay-validate] $*"
}

export PROFILES_CSV="${PROFILES_CSV:-down_demo}"
export STRESS_K6_RPS="${STRESS_K6_RPS:-25}"
if [[ -n "${COMPARE_SWEEP_K6_DURATION:-}" ]]; then
  export STRESS_K6_DURATION="${COMPARE_SWEEP_K6_DURATION}"
fi
export SQUEEZE_COMPARE_FORMULA_UNTIL_VIOLATION="${SQUEEZE_COMPARE_FORMULA_UNTIL_VIOLATION:-1}"
export SQUEEZE_UNTIL_VIOLATION="${SQUEEZE_UNTIL_VIOLATION:-true}"
export SQUEEZE_MAX_ITERATIONS="${SQUEEZE_MAX_ITERATIONS:-16}"
export SQUEEZE_CPU_UTIL_FAIL_PCT="${SQUEEZE_CPU_UTIL_FAIL_PCT:-95}"
SUBDIR_SOURCE="${STRESS_RESULTS_SUBDIR_SOURCE:-squeeze-formula-source}"
SUBDIR_REPLAY="${STRESS_RESULTS_SUBDIR_REPLAY:-squeeze-formula-replay}"

log "artifacts root: ${VALIDATE_ROOT}"

# --- Phase 1: formula-only DOWN squeeze (source trajectory) ---
log "=== phase 1/2: formula-only DOWN @ RPS=${STRESS_K6_RPS} ==="
export SQUEEZE_OPTIMIZER=formula
export STRESS_RESULTS_SUBDIR="${SUBDIR_SOURCE}"
export RESULTS_DEST="${VALIDATE_ROOT}/source"
mkdir -p "${RESULTS_DEST}"

if ! ./scripts/run_cluster_profiles.sh; then
  log "ERROR: phase 1 (formula) failed"
  exit 1
fi
SOURCE_BOUNDARY="${RESULTS_DEST}/${SUBDIR_SOURCE}/cost-effective-boundary.json"
if [[ ! -f "${SOURCE_BOUNDARY}" ]]; then
  log "ERROR: phase 1 did not produce a boundary at ${SOURCE_BOUNDARY}"
  log "  Cluster job likely never ran (check cluster-run logs) or PVC sync missed /app/results/${SUBDIR_SOURCE}/run-1."
  log "  Re-run phase 1 only, or set REPLAY_SOURCE_PATH to an existing formula run on PVC"
  log "  (e.g. /app/results/squeeze-compare-formula/run-1 from a compare sweep)."
  exit 1
fi
log "phase 1 OK: ${SOURCE_BOUNDARY}"

# --- Phase 2: replay each source config (observe-only k6) ---
log "=== phase 2/2: replay source trajectory (same configs, no optimizer) ==="
unset SQUEEZE_OPTIMIZER
export STRESS_RESULTS_SUBDIR="${SUBDIR_REPLAY}"
export REPLAY_SOURCE_PATH="${REPLAY_SOURCE_PATH:-/app/results/${SUBDIR_SOURCE}/run-1}"
export RESULTS_DEST="${VALIDATE_ROOT}/replay"
mkdir -p "${RESULTS_DEST}"

if ! ./scripts/run_cluster_profiles.sh --replay-trajectory; then
  log "ERROR: phase 2 (replay) failed"
  exit 1
fi

log "done"
log "  source: ${VALIDATE_ROOT}/source/${SUBDIR_SOURCE}/"
log "  replay: ${VALIDATE_ROOT}/replay/${SUBDIR_REPLAY}/"
if [[ -f "${VALIDATE_ROOT}/replay/${SUBDIR_REPLAY}/replay-comparison.md" ]]; then
  log "  comparison: ${VALIDATE_ROOT}/replay/${SUBDIR_REPLAY}/replay-comparison.md"
fi
exit 0
