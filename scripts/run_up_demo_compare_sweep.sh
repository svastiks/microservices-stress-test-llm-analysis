#!/usr/bin/env bash
# Queue N sequential squeeze-optimizer *compare* runs for up_demo (one cluster job per round).
# Same baseline each time (run_cluster_profiles resets web/HPA before each job).
#
# UP vs DOWN:
#   - up_demo uses spike_login_flash_sale scenario and high baseline RPS (see experiments.json, default 220).
#   - start.py applies up_demo thin baseline (1 repl @ 50m/25Mi, HPA max=1) before iter 1 so k6 tends to FAIL → UP recovery.
#   - If iteration 1 PASSes (cluster already "happy" at that load), the UP demo path skips the down-squeeze leg —
#     pick RPS high enough that thin web still violates SLO on iter 1. Too-low RPS rounds are unreliable for the demo.
#   - Compare uses vanilla LLM (SQUEEZE_LLM_PURE=1), same as down_demo — formula vs LLM only in prompts/YAML.
#
# Default mode (RPS ladder via STRESS_K6_RPS, same as down sweep):
#   - Fixed profile: up_demo (override with COMPARE_SWEEP_BASE_PROFILE=up_demo_strict if you want stricter preset)
#   - Default ladder: 160,190,220,260 (steps around experiments up_demo=220 and up_demo_strict=260)
#   - Optional duration for every round: COMPARE_SWEEP_K6_DURATION=90s → exports STRESS_K6_DURATION
#
# Optional profile-ladder mode (only if those names exist in start.py argparse on your image):
#   COMPARE_SWEEP_PROFILES=...  (if set, RPS list is ignored)
#
# Artifacts under compare-up-sweep-<stamp>/: local run-1..run-N per round (formula-run/, llm-run/, comparison.md; sweep-round-<i>.txt).
#
# Optional:
#   COMPARE_SWEEP_PARENT=...
#   COMPARE_SWEEP_RPS=160,190,220,260
#   COMPARE_SWEEP_LOADS=200,220,240,260,280  COMPARE_SWEEP_REPEATS_PER_LOAD=10  (5×10 matrix)
#   COMPARE_SWEEP_SHUFFLE_ROUNDS=1  COMPARE_SWEEP_SHUFFLE_SEED=42  (vanilla vs advanced drift control)
#   COMPARE_SWEEP_BASE_PROFILE=up_demo
#   COMPARE_SWEEP_ROUNDS=N
#   COMPARE_SWEEP_K6_DURATION=90s
#   UP_DEMO_STABILIZE_USER (run_cluster_profiles; default raises user deploy resources during up_demo)
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

# Defaults for this script only (do not overwrite if caller already exported).
: "${COMPARE_SWEEP_BASE_PROFILE:=up_demo}"
: "${COMPARE_SWEEP_RPS:=160,190,220,260}"

SWEEP_STAMP="$(date +%Y%m%d-%H%M%S)"
SWEEP_PARENT="${COMPARE_SWEEP_PARENT:-${ROOT}/results-from-cluster}"
SWEEP_ROOT="${SWEEP_PARENT}/compare-up-sweep-${SWEEP_STAMP}"
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
  if ! parse_compare_sweep_rps_matrix "${COMPARE_SWEEP_RPS}"; then
    exit 1
  fi
  first_rps="${CLEAN_RPS[0]}"
  if [[ "${first_rps}" =~ ^[0-9]+$ ]] && ((first_rps < 120)); then
    echo "[compare-up-sweep] WARNING: first RPS=${first_rps} is low for up_demo; iteration 1 may PASS (thin baseline)" \
      "and skip the intended UP recovery path — consider raising COMPARE_SWEEP_RPS." >&2
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
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] [compare-up-sweep] $*"
}

log "sweep artifacts root: ${SWEEP_ROOT}"
if [[ "${USE_PROFILE_NAMES}" -eq 1 ]]; then
  log "mode=profiles rounds=${ROUNDS}: ${ROUND_LABELS[*]}"
else
  log "mode=rps_overrides profile=${COMPARE_SWEEP_BASE_PROFILE} rounds=${ROUNDS}: ${ROUND_LABELS[*]}"
fi

# shellcheck source=scripts/lib/squeeze_up_demo_env.sh
source "${ROOT}/scripts/lib/squeeze_up_demo_env.sh"
# shellcheck source=scripts/lib/sweep_round_finalize.sh
source "${ROOT}/scripts/lib/sweep_round_finalize.sh"

apply_compare_squeeze_env() {
  apply_up_demo_compare_env
  export COMPARE_SYNC_MODE=formula
}

mkdir -p "${SWEEP_ROOT}"
export RESULTS_DEST="${SWEEP_ROOT}"
log "all rounds write under RESULTS_DEST=${RESULTS_DEST} (local run-1..run-N per sweep round)"

any_fail=0
for ((r = 0; r < ROUNDS; r++)); do
  idx=$((r + 1))
  export COMPARE_SWEEP_ROUND="${idx}"
  unset STRESS_K6_RPS STRESS_K6_DURATION 2>/dev/null || true
  if [[ -n "${COMPARE_SWEEP_K6_DURATION:-}" ]]; then
    export STRESS_K6_DURATION="${COMPARE_SWEEP_K6_DURATION}"
  fi

  if [[ "${USE_PROFILE_NAMES}" -eq 1 ]]; then
    profile="${CLEAN_PROFILES[${r}]}"
    export PROFILES_CSV="${profile}"
    log "=== round ${idx}/${ROUNDS} profile=${profile} (compare) ==="
  else
    export STRESS_K6_RPS="${CLEAN_RPS[${r}]}"
    export PROFILES_CSV="${COMPARE_SWEEP_BASE_PROFILE}"
    if [[ "${STRESS_K6_RPS}" =~ ^[0-9]+$ ]] && ((STRESS_K6_RPS >= 260)) \
      && [[ "${PROFILES_CSV}" == "up_demo" ]]; then
      log "WARNING: STRESS_K6_RPS=${STRESS_K6_RPS} with profile up_demo (preset 220 in experiments.json) — "
      log "  set COMPARE_SWEEP_BASE_PROFILE=up_demo_strict for aligned 260 RPS metadata, or LLM/formula k6 targets may disagree."
    fi
    log "=== round ${idx}/${ROUNDS} profile=${PROFILES_CSV} STRESS_K6_RPS=${STRESS_K6_RPS} STRESS_K6_DURATION=${STRESS_K6_DURATION:-<profile default>} (compare) ==="
  fi

  apply_compare_squeeze_env
  log "squeeze env: until_violation=${SQUEEZE_UNTIL_VIOLATION} max_iter=${SQUEEZE_MAX_ITERATIONS} formula_max=${SQUEEZE_COMPARE_FORMULA_MAX_ITERATIONS} formula_uv=${SQUEEZE_COMPARE_FORMULA_UNTIL_VIOLATION} llm_pure=${SQUEEZE_LLM_PURE:-<unset>} llm_down_boundary=${SQUEEZE_LLM_DOWN_BOUNDARY:-<unset>}"

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
