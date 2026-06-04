#!/usr/bin/env bash
# Queue N sequential squeeze-optimizer *compare* runs (one cluster job per round).
# Same baseline each time (run_cluster_profiles resets web/HPA before each job).
#
# Default mode (RPS ladder, works with --profile down_demo only on the cluster image):
#   - Fixed profile: down_demo (90s SLO shape from experiments.json)
#   - Vary load only: STRESS_K6_RPS=25,35,45,55 (passed into the Job via run_analyzer_job.sh)
#   - Requires an analyzer image built from this repo (start.py honors STRESS_K6_RPS).
#
# Optional profile-ladder mode (needs image with those profile names in start.py argparse):
#   COMPARE_SWEEP_PROFILES=down_demo_r15,down_demo_r25,...  (if set, RPS list is ignored)
#
# Artifacts under compare-sweep-<stamp>/:
#   - Local run-1..run-N per sweep round (COMPARE_SWEEP_ROUND); each has formula-run/, llm-run/, comparison.md
#   - Cluster PVC still uses run-1 per job; sync maps round i → local run-i (avoids overwriting prior rounds).
#   - sweep-round-<i>.txt per queue round (label, RPS, pointers to run-<i>/).
#   - After each round, PVC is synced to local run-<i>/ before the next round starts (see sweep_round_finalize.sh).
# Optional: RESULTS_PVC_SYNC_LAYOUT=full / RESULTS_PVC_SNAPSHOTS=true (see run_cluster_profiles.sh).
#
# Optional:
#   COMPARE_SWEEP_PARENT=...
#   COMPARE_SWEEP_RPS=25,35,45,55          (default when not using COMPARE_SWEEP_PROFILES)
#   COMPARE_SWEEP_BASE_PROFILE=down_demo   (default)
#   COMPARE_SWEEP_LOADS=20,25,35,45,55 COMPARE_SWEEP_REPEATS_PER_LOAD=10
#   COMPARE_SWEEP_ROUNDS=N                 (first N entries from RPS or profile list)
#   SQUEEZE_MAX_ITERATIONS / SQUEEZE_COMPARE_FORMULA_MAX_ITERATIONS / SQUEEZE_COMPARE_FORMULA_UNTIL_VIOLATION / etc.
#
# Note: higher RPS does not guarantee fewer iterations; measure it.
#
# For the same compare-sweep pattern on up_demo (different default RPS ladder), see:
#   scripts/run_up_demo_compare_sweep.sh
#
# Fast LLM-only iteration (no formula wait): scripts/run_down_demo_llm_squeeze.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

SWEEP_STAMP="$(date +%Y%m%d-%H%M%S)"
SWEEP_PARENT="${COMPARE_SWEEP_PARENT:-${ROOT}/results-from-cluster}"
SWEEP_ROOT="${SWEEP_PARENT}/compare-sweep-${SWEEP_STAMP}"
mkdir -p "${SWEEP_ROOT}"

USE_PROFILE_NAMES=0
ROUNDS=0
declare -a ROUND_LABELS=()

if [[ -n "${COMPARE_SWEEP_PROFILES:-}" ]]; then
  USE_PROFILE_NAMES=1
  IFS=',' read -r -a PROFILE_LIST <<< "${COMPARE_SWEEP_PROFILES}"
  CLEAN_PROFILES=()
  for _p in "${PROFILE_LIST[@]}"; do
    _q="$(echo "${_p}" | xargs)"
    [[ -n "${_q}" ]] && CLEAN_PROFILES+=("${_q}")
  done
  if ((${#CLEAN_PROFILES[@]} == 0)); then
    echo "COMPARE_SWEEP_PROFILES is non-empty but produced no profiles" >&2
    exit 1
  fi
  ROUNDS="${COMPARE_SWEEP_ROUNDS:-${#CLEAN_PROFILES[@]}}"
  if ! [[ "${ROUNDS}" =~ ^[0-9]+$ ]] || ((ROUNDS < 1)); then
    echo "COMPARE_SWEEP_ROUNDS must be a positive integer" >&2
    exit 1
  fi
  if ((ROUNDS > ${#CLEAN_PROFILES[@]})); then
    echo "COMPARE_SWEEP_ROUNDS=${ROUNDS} exceeds COMPARE_SWEEP_PROFILES length ${#CLEAN_PROFILES[@]}" >&2
    exit 1
  fi
  for ((i = 0; i < ROUNDS; i++)); do
    ROUND_LABELS+=("${CLEAN_PROFILES[i]}")
  done
else
  # shellcheck source=scripts/lib/expand_compare_sweep_matrix.sh
  source "${ROOT}/scripts/lib/expand_compare_sweep_matrix.sh"
  if ! parse_compare_sweep_rps_matrix "${COMPARE_SWEEP_RPS:-25,35,45,55}"; then
    exit 1
  fi
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

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] [compare-sweep] $*"
}

log "sweep artifacts root: ${SWEEP_ROOT}"
if [[ "${USE_PROFILE_NAMES}" -eq 1 ]]; then
  log "mode=profiles rounds=${ROUNDS}: ${ROUND_LABELS[*]}"
else
  log "mode=rps_overrides profile=${COMPARE_SWEEP_BASE_PROFILE:-down_demo} rounds=${ROUNDS}: ${ROUND_LABELS[*]}"
fi

# shellcheck source=scripts/lib/squeeze_llm_env.sh
source "${ROOT}/scripts/lib/squeeze_llm_env.sh"
# shellcheck source=scripts/lib/sweep_round_finalize.sh
source "${ROOT}/scripts/lib/sweep_round_finalize.sh"

apply_compare_squeeze_env() {
  apply_llm_squeeze_env
  export COMPARE_SYNC_MODE=formula
  export SQUEEZE_COMPARE_FORMULA_MAX_ITERATIONS="${SQUEEZE_COMPARE_FORMULA_MAX_ITERATIONS:-16}"
  export SQUEEZE_COMPARE_FORMULA_UNTIL_VIOLATION="${SQUEEZE_COMPARE_FORMULA_UNTIL_VIOLATION:-1}"
}

mkdir -p "${SWEEP_ROOT}"
export RESULTS_DEST="${SWEEP_ROOT}"
log "all rounds write under RESULTS_DEST=${RESULTS_DEST} (local run-1..run-N per sweep round; cluster PVC still run-1 per job)"

any_fail=0
for ((r = 0; r < ROUNDS; r++)); do
  idx=$((r + 1))
  export COMPARE_SWEEP_ROUND="${idx}"
  unset STRESS_K6_RPS STRESS_K6_DURATION 2>/dev/null || true

  if [[ "${USE_PROFILE_NAMES}" -eq 1 ]]; then
    profile="${CLEAN_PROFILES[${r}]}"
    export PROFILES_CSV="${profile}"
    log "=== round ${idx}/${ROUNDS} profile=${profile} (compare) ==="
  else
    export STRESS_K6_RPS="${CLEAN_RPS[${r}]}"
    export PROFILES_CSV="${COMPARE_SWEEP_BASE_PROFILE:-down_demo}"
    log "=== round ${idx}/${ROUNDS} profile=${PROFILES_CSV} STRESS_K6_RPS=${STRESS_K6_RPS} (compare) ==="
  fi

  apply_compare_squeeze_env
  log "squeeze env: until_violation=${SQUEEZE_UNTIL_VIOLATION} max_iter=${SQUEEZE_MAX_ITERATIONS} formula_max=${SQUEEZE_COMPARE_FORMULA_MAX_ITERATIONS} formula_uv=${SQUEEZE_COMPARE_FORMULA_UNTIL_VIOLATION}"

  round_ok=1
  if ! ./scripts/run_cluster_profiles.sh --compare-squeeze-optimizers; then
    log "ERROR: round ${idx} failed — partial data may exist under ${SWEEP_ROOT}"
    round_ok=0
    any_fail=1
  else
    log "round ${idx} OK; meta under ${SWEEP_ROOT}/sweep-round-${idx}.txt"
  fi

  finalize_sweep_round_local "${SWEEP_ROOT}" "${idx}" "${round_ok}" log || true

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
    echo "PROFILES_CSV=${PROFILES_CSV}"
    echo "STRESS_K6_RPS=${STRESS_K6_RPS:-}"
    echo "STRESS_K6_DURATION=${STRESS_K6_DURATION:-}"
    echo "finished_utc=$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
    echo "SQUEEZE_UNTIL_VIOLATION=${SQUEEZE_UNTIL_VIOLATION}"
    echo "SQUEEZE_MAX_ITERATIONS=${SQUEEZE_MAX_ITERATIONS}"
    echo "SQUEEZE_COMPARE_FORMULA_MAX_ITERATIONS=${SQUEEZE_COMPARE_FORMULA_MAX_ITERATIONS}"
    echo "SQUEEZE_COMPARE_FORMULA_UNTIL_VIOLATION=${SQUEEZE_COMPARE_FORMULA_UNTIL_VIOLATION:-}"
    echo "sweep_root=${SWEEP_ROOT}"
    echo "run_dir=${SWEEP_ROOT}/${run_label}"
    echo "comparison_md=${SWEEP_ROOT}/${run_label}/comparison.md"
  } > "${SWEEP_ROOT}/sweep-round-${idx}.txt" 2>/dev/null || true
done

unset COMPARE_SWEEP_ROUND 2>/dev/null || true

if [[ "${any_fail}" -ne 0 ]]; then
  log "sweep finished with failures"
  exit 1
fi
log "all ${ROUNDS} rounds completed"
exit 0
