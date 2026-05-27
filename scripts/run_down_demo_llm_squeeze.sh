#!/usr/bin/env bash
# LLM-only down_demo squeeze — same cluster settings as the LLM arm of compare-sweep, without formula.
# Iterate here until first_fail + non-empty diffs look good, then run ./scripts/run_down_demo_compare_sweep.sh.
#
# Usage:
#   BUILD_ANALYZER_IMAGE=true ./scripts/run_down_demo_llm_squeeze.sh
#   STRESS_K6_RPS=25 COMPARE_SWEEP_K6_DURATION=60s ./scripts/run_down_demo_llm_squeeze.sh
#
# Artifacts: results-from-cluster/llm-squeeze-<stamp>/run-<n>/iteration-*
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

# shellcheck source=scripts/lib/squeeze_llm_env.sh
source "${ROOT}/scripts/lib/squeeze_llm_env.sh"

STAMP="$(date +%Y%m%d-%H%M%S)"
OUT_PARENT="${LLM_SQUEEZE_PARENT:-${ROOT}/results-from-cluster}"
export RESULTS_DEST="${OUT_PARENT}/llm-squeeze-${STAMP}"
mkdir -p "${RESULTS_DEST}"

export PROFILES_CSV="${PROFILES_CSV:-down_demo}"
export STRESS_K6_RPS="${STRESS_K6_RPS:-25}"
if [[ -n "${COMPARE_SWEEP_K6_DURATION:-}" ]]; then
  export STRESS_K6_DURATION="${COMPARE_SWEEP_K6_DURATION}"
fi

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

apply_llm_squeeze_env
export SQUEEZE_OPTIMIZER=llm
export STRESS_RESULTS_SUBDIR="${STRESS_RESULTS_SUBDIR:-squeeze-compare-llm}"
export RESULTS_PVC_SYNC_LLMS_ONLY=true

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] [llm-squeeze] $*"
}

log "RESULTS_DEST=${RESULTS_DEST}"
log "profile=${PROFILES_CSV} STRESS_K6_RPS=${STRESS_K6_RPS:-<profile default>} STRESS_K6_DURATION=${STRESS_K6_DURATION:-<profile default>}"
log "squeeze: optimizer=${SQUEEZE_OPTIMIZER} subdir=${STRESS_RESULTS_SUBDIR} until_violation=${SQUEEZE_UNTIL_VIOLATION} max_iter=${SQUEEZE_MAX_ITERATIONS}"

if ! ./scripts/run_cluster_profiles.sh; then
  log "ERROR: job failed — partial data may exist under ${RESULTS_DEST}"
  exit 1
fi

run_label=""
if [[ -d "${RESULTS_DEST}" ]]; then
  run_label="$(find "${RESULTS_DEST}" -maxdepth 1 -type d -name 'run-*' | sort -V | tail -1 | xargs basename 2>/dev/null || true)"
fi
log "done${run_label:+; latest=${RESULTS_DEST}/${run_label}}"
if [[ -f "${RESULTS_DEST}/${run_label}/cost-effective-boundary.json" ]]; then
  log "boundary: ${RESULTS_DEST}/${run_label}/cost-effective-boundary.json"
fi
exit 0
