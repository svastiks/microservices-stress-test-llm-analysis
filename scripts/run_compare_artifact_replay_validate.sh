#!/usr/bin/env bash
# Replay formula + LLM trajectories from a saved compare artifact (same configs, observe-only k6).
# Seeds local formula-run/ + llm-run/ onto PVC, replays each arm, writes per-arm + matched-config tables.
#
# Usage:
#   ARTIFACT_DIR=artifacts_with_cpu_fix/FORMULA_VS_ADVANCED_LLM/DOWN/GOOD_COST_WIN_run-1-rps25-20260604-230952 \
#   KUBE_CONTEXT=monitoring COMPARE_SWEEP_K6_DURATION=90s SQUEEZE_SETTLE_SECONDS=30 STRESS_K6_RPS=25 \
#   ./scripts/run_compare_artifact_replay_validate.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

ARTIFACT_DIR="${ARTIFACT_DIR:-}"
if [[ -z "${ARTIFACT_DIR}" ]]; then
  echo "ARTIFACT_DIR is required (path to compare run with formula-run/ and llm-run/)" >&2
  exit 1
fi
if [[ "${ARTIFACT_DIR}" != /* ]]; then
  ARTIFACT_DIR="${ROOT}/${ARTIFACT_DIR}"
fi
if [[ ! -f "${ARTIFACT_DIR}/formula-run/cost-effective-boundary.json" \
   || ! -f "${ARTIFACT_DIR}/llm-run/cost-effective-boundary.json" ]]; then
  echo "ARTIFACT_DIR must contain formula-run/ and llm-run/ with cost-effective-boundary.json" >&2
  exit 1
fi

STAMP="$(date +%Y%m%d-%H%M%S)"
OUT_PARENT="${REPLAY_VALIDATE_PARENT:-${ROOT}/results-from-cluster}"
VALIDATE_ROOT="${OUT_PARENT}/compare-artifact-replay-${STAMP}"
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

# shellcheck source=scripts/lib/kube_cluster.sh
source "${ROOT}/scripts/lib/kube_cluster.sh"
# shellcheck source=scripts/lib/seed_pvc_run.sh
source "${ROOT}/scripts/lib/seed_pvc_run.sh"

ensure_kube_cluster

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] [compare-artifact-replay] $*"
}

export PROFILES_CSV="${PROFILES_CSV:-down_demo}"
export STRESS_K6_RPS="${STRESS_K6_RPS:-25}"
if [[ -n "${COMPARE_SWEEP_K6_DURATION:-}" ]]; then
  export STRESS_K6_DURATION="${COMPARE_SWEEP_K6_DURATION}"
fi
export SQUEEZE_CPU_UTIL_FAIL_PCT="${SQUEEZE_CPU_UTIL_FAIL_PCT:-95}"

SEED_FORMULA="${REPLAY_SEED_SUBDIR_FORMULA:-replay-seed-formula}"
SEED_LLM="${REPLAY_SEED_SUBDIR_LLM:-replay-seed-llm}"
OUT_FORMULA="${REPLAY_OUT_SUBDIR_FORMULA:-replay-out-formula}"
OUT_LLM="${REPLAY_OUT_SUBDIR_LLM:-replay-out-llm}"

log "artifact: ${ARTIFACT_DIR}"
log "output:   ${VALIDATE_ROOT}"

# --- Seed artifact runs onto PVC (so replay reads exact saved configs) ---
log "=== seed formula-run -> /app/results/${SEED_FORMULA}/run-1 ==="
seed_pvc_run "${ARTIFACT_DIR}/formula-run" "${SEED_FORMULA}"
log "=== seed llm-run -> /app/results/${SEED_LLM}/run-1 ==="
seed_pvc_run "${ARTIFACT_DIR}/llm-run" "${SEED_LLM}"

# --- Replay formula arm ---
log "=== replay formula trajectory ==="
unset SQUEEZE_OPTIMIZER
export STRESS_RESULTS_SUBDIR="${OUT_FORMULA}"
export REPLAY_SOURCE_PATH="/app/results/${SEED_FORMULA}/run-1"
export RESULTS_DEST="${VALIDATE_ROOT}/formula-replay"
mkdir -p "${RESULTS_DEST}"
if ! ./scripts/run_cluster_profiles.sh --replay-trajectory; then
  log "ERROR: formula replay failed"
  exit 1
fi

# --- Replay LLM arm ---
log "=== replay llm trajectory ==="
export STRESS_RESULTS_SUBDIR="${OUT_LLM}"
export REPLAY_SOURCE_PATH="/app/results/${SEED_LLM}/run-1"
export RESULTS_DEST="${VALIDATE_ROOT}/llm-replay"
mkdir -p "${RESULTS_DEST}"
if ! ./scripts/run_cluster_profiles.sh --replay-trajectory; then
  log "ERROR: llm replay failed"
  exit 1
fi

# --- Local reports: per-arm + matched-config ---
FORMULA_REPLAY_DIR="${VALIDATE_ROOT}/formula-replay/${OUT_FORMULA}"
LLM_REPLAY_DIR="${VALIDATE_ROOT}/llm-replay/${OUT_LLM}"
REPORT_DIR="${VALIDATE_ROOT}/reports"
mkdir -p "${REPORT_DIR}"
cp -R "${ARTIFACT_DIR}/formula-run" "${REPORT_DIR}/formula-run"
cp -R "${ARTIFACT_DIR}/llm-run" "${REPORT_DIR}/llm-run"

MATCHED="$(PYTHONPATH="${ROOT}" python3 -c "
from pathlib import Path
from analysis.replay_trajectory import write_compare_artifact_replay_bundle
p = write_compare_artifact_replay_bundle(
    Path('${REPORT_DIR}'),
    Path('${FORMULA_REPLAY_DIR}'),
    Path('${LLM_REPLAY_DIR}'),
    Path('${REPORT_DIR}'),
)
print(p)
")"

log "done"
log "  formula replay: ${FORMULA_REPLAY_DIR}/"
log "  llm replay:     ${LLM_REPLAY_DIR}/"
log "  reports:        ${REPORT_DIR}/"
log "    formula-replay-comparison.md"
log "    llm-replay-comparison.md"
log "    matched-config-replay.md"
log "  matched table:  ${MATCHED}"
exit 0
