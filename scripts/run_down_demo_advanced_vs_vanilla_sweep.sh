#!/usr/bin/env bash
# DOWN advanced LLM vs vanilla LLM compare sweep (down_demo DOWN boundary search).
#
# Pass bar (COMPARE_SWEEP_PASS_BAR): cost = advanced best_pass < vanilla (smoke minimum);
#   full = cost + advanced iters <= vanilla. Smoke until cost PASS; batch round 2+ only when you approve.
#
# Example (1-round smoke, fast 60s k6):
#   BUILD_ANALYZER_IMAGE=true COMPARE_SWEEP_FAST=1 COMPARE_SWEEP_RPS=35 COMPARE_SWEEP_ROUNDS=1 \
#     COMPARE_SWEEP_PASS_BAR=cost ./scripts/run_down_demo_advanced_vs_vanilla_sweep.sh
#
# Example (1-round smoke):
#   BUILD_ANALYZER_IMAGE=true COMPARE_SWEEP_RPS=25 COMPARE_SWEEP_ROUNDS=1 \
#     ./scripts/run_down_demo_advanced_vs_vanilla_sweep.sh
#
# Full matrix:
#   COMPARE_SWEEP_LOADS=20,25,35,45,55 COMPARE_SWEEP_REPEATS_PER_LOAD=10 \
#   COMPARE_SWEEP_SHUFFLE_ROUNDS=1 ./scripts/run_down_demo_advanced_vs_vanilla_sweep.sh
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

: "${COMPARE_SWEEP_BASE_PROFILE:=down_demo}"
: "${COMPARE_SWEEP_RPS:=25,35,45,55}"
: "${COMPARE_SWEEP_PASS_BAR:=cost}"

SWEEP_STAMP="$(date +%Y%m%d-%H%M%S)"
SWEEP_PARENT="${COMPARE_SWEEP_PARENT:-${ROOT}/results-from-cluster}"
SWEEP_ROOT="${SWEEP_PARENT}/compare-advanced-vanilla-down-sweep-${SWEEP_STAMP}"
mkdir -p "${SWEEP_ROOT}"

declare -a ROUND_LABELS=()
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
  echo "OPENAI_API_KEY is required (env or .env)" >&2
  exit 1
fi

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [advanced-vanilla-down-sweep] $*"; }

# shellcheck source=scripts/lib/squeeze_advanced_vanilla_compare_env.sh
source "${ROOT}/scripts/lib/squeeze_advanced_vanilla_compare_env.sh"
# shellcheck source=scripts/lib/sweep_round_finalize.sh
source "${ROOT}/scripts/lib/sweep_round_finalize.sh"

export RESULTS_DEST="${SWEEP_ROOT}"
export RESET_BASELINE_EACH_PROFILE=true
export PROFILES_CSV="${COMPARE_SWEEP_BASE_PROFILE}"
unset BASELINE_DEPLOYMENT_YAML BASELINE_HPA_YAML UP_DEMO_STABILIZE_USER 2>/dev/null || true

log "sweep root: ${SWEEP_ROOT}"
log "profile=${COMPARE_SWEEP_BASE_PROFILE} rounds=${ROUNDS}: ${ROUND_LABELS[*]}"
log "all rounds write under RESULTS_DEST=${RESULTS_DEST}"

any_fail=0
for ((r = 0; r < ROUNDS; r++)); do
  idx=$((r + 1))
  export COMPARE_SWEEP_ROUND="${idx}"
  unset STRESS_K6_RPS STRESS_K6_DURATION 2>/dev/null || true
  if [[ -n "${COMPARE_SWEEP_K6_DURATION:-}" ]]; then
    export STRESS_K6_DURATION="${COMPARE_SWEEP_K6_DURATION}"
  fi
  export STRESS_K6_RPS="${CLEAN_RPS[r]}"
  export PROFILES_CSV="${COMPARE_SWEEP_BASE_PROFILE}"

  apply_advanced_vanilla_down_compare_env
  log "=== round ${idx}/${ROUNDS} ${ROUND_LABELS[r]} STRESS_K6_RPS=${STRESS_K6_RPS} STRESS_K6_DURATION=${STRESS_K6_DURATION:-<profile default>} SQUEEZE_SETTLE_SECONDS=${SQUEEZE_SETTLE_SECONDS:-30} (advanced-llm vs vanilla-llm DOWN) ==="

  round_ok=1
  if ! ./scripts/run_cluster_profiles.sh --compare-advanced-vs-vanilla-llm; then
    log "ERROR: round ${idx} failed"
    round_ok=0
    any_fail=1
  else
    log "round ${idx} OK"
  fi

  finalize_sweep_round_local "${SWEEP_ROOT}" "${idx}" "${round_ok}" log || true

  run_label="run-${idx}"
  if [[ -f "${SWEEP_ROOT}/.last_sync_r${idx}.txt" ]]; then
    run_label="$(tr -d '\r\n' < "${SWEEP_ROOT}/.last_sync_r${idx}.txt")"
  fi
  run_dir="${SWEEP_ROOT}/${run_label}"
  pass_bar_ok=1
  if sweep_round_has_local_bundle "${run_dir}"; then
    if ! sweep_round_advanced_vanilla_pass_bar "${run_dir}"; then
      log "ERROR: round ${idx} PASS BAR failed (COMPARE_SWEEP_PASS_BAR=${COMPARE_SWEEP_PASS_BAR})"
      pass_bar_ok=0
      any_fail=1
      if [[ "${COMPARE_SWEEP_STOP_ON_PASS_BAR_FAIL:-1}" =~ ^(1|true|yes|on)$ ]]; then
        log "stopping sweep — fix and re-smoke one RPS before multi-round batch"
        break
      fi
    else
      log "round ${idx} PASS BAR OK (${COMPARE_SWEEP_PASS_BAR})"
      if [[ "${round_ok}" -eq 0 ]]; then
        log "WARNING: cluster job failed/timeout but compare bundle passed bar — OK for smoke"
        if [[ "${ROUNDS}" -eq 1 ]]; then
          any_fail=0
        fi
      fi
    fi
  elif [[ "${round_ok}" -eq 0 ]]; then
    pass_bar_ok=0
  fi

  status="OK"
  if [[ "${pass_bar_ok:-1}" -eq 0 ]]; then
    status="PASS_BAR_FAIL"
  elif [[ "${round_ok}" -eq 0 ]]; then
    status="CLUSTER_FAIL"
  fi
  {
    echo "round=${idx}/${ROUNDS}"
    echo "status=${status}"
    echo "label=${ROUND_LABELS[r]}"
    echo "STRESS_K6_RPS=${STRESS_K6_RPS}"
    echo "STRESS_K6_DURATION=${STRESS_K6_DURATION:-}"
    echo "PROFILES_CSV=${PROFILES_CSV}"
    echo "sweep_root=${SWEEP_ROOT}"
    echo "run_dir=${SWEEP_ROOT}/${run_label}"
    echo "comparison_md=${SWEEP_ROOT}/${run_label}/comparison.md"
    echo "finished_utc=$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  } > "${SWEEP_ROOT}/sweep-round-${idx}.txt" 2>/dev/null || true
done
unset COMPARE_SWEEP_ROUND 2>/dev/null || true

if [[ "${any_fail}" -ne 0 ]]; then
  log "sweep finished with failures"
  exit 1
fi
log "all ${ROUNDS} rounds completed"
exit 0
