#!/usr/bin/env bash
# UP advanced LLM vs vanilla LLM compare sweep (same squeeze loop, different prompt richness).
#
# Context (same as compare-up / static-up sweeps):
#   - run_cluster_profiles: kube context, stack, OPENAI secret, thin web+HPA baseline reset each round
#   - up_demo: user deploy stabilized; start.py pins thin web before iter 1 → FAIL → UP recovery
#   - Per round: one job runs advanced-llm then vanilla-llm arms; PVC → local run-N/
#
# Example:
#   BUILD_ANALYZER_IMAGE=true COMPARE_SWEEP_FAST=1 COMPARE_SWEEP_RPS=220,240,260 COMPARE_SWEEP_ROUNDS=3 \
#     ./scripts/run_up_demo_advanced_vs_vanilla_sweep.sh
#
# Example:
#   BUILD_ANALYZER_IMAGE=true COMPARE_SWEEP_RPS=220,240,260 COMPARE_SWEEP_ROUNDS=3 \
#     ./scripts/run_up_demo_advanced_vs_vanilla_sweep.sh
#
# Optional:
#   COMPARE_SWEEP_PARENT=...
#   COMPARE_SWEEP_BASE_PROFILE=up_demo | up_demo_strict
#   COMPARE_SWEEP_LOADS=200,220,240,260,280 COMPARE_SWEEP_REPEATS_PER_LOAD=10
#   COMPARE_SWEEP_SHUFFLE_ROUNDS=1  (recommended — reduces time-of-day drift)
#   COMPARE_SWEEP_K6_DURATION=90s
#   UP_DEMO_STABILIZE_USER=true (run_cluster_profiles default)
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

: "${COMPARE_SWEEP_BASE_PROFILE:=up_demo}"
: "${COMPARE_SWEEP_RPS:=220,240,260}"

SWEEP_STAMP="$(date +%Y%m%d-%H%M%S)"
SWEEP_PARENT="${COMPARE_SWEEP_PARENT:-${ROOT}/results-from-cluster}"
SWEEP_ROOT="${SWEEP_PARENT}/compare-advanced-vanilla-up-sweep-${SWEEP_STAMP}"
mkdir -p "${SWEEP_ROOT}"

declare -a ROUND_LABELS=()
# shellcheck source=scripts/lib/expand_compare_sweep_matrix.sh
source "${ROOT}/scripts/lib/expand_compare_sweep_matrix.sh"
if ! parse_compare_sweep_rps_matrix "${COMPARE_SWEEP_RPS}"; then
  exit 1
fi
first_rps="${CLEAN_RPS[0]}"
if [[ "${first_rps}" =~ ^[0-9]+$ ]] && ((first_rps < 120)); then
  echo "[advanced-vanilla-up-sweep] WARNING: first RPS=${first_rps} is low for up_demo; iteration 1 may PASS and skip UP recovery." >&2
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

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [advanced-vanilla-up-sweep] $*"; }

# shellcheck source=scripts/lib/squeeze_advanced_vanilla_compare_env.sh
source "${ROOT}/scripts/lib/squeeze_advanced_vanilla_compare_env.sh"
# shellcheck source=scripts/lib/sweep_round_finalize.sh
source "${ROOT}/scripts/lib/sweep_round_finalize.sh"

export RESULTS_DEST="${SWEEP_ROOT}"
export BASELINE_DEPLOYMENT_YAML="${ROOT}/infra/k8s/spark/robot-shop-web-deployment.up-demo-thin.baseline.yaml"
export BASELINE_HPA_YAML="${ROOT}/infra/k8s/spark/robot-shop-web-hpa.baseline.yaml"
export RESET_BASELINE_EACH_PROFILE=true
export UP_DEMO_STABILIZE_USER="${UP_DEMO_STABILIZE_USER:-true}"
export PROFILES_CSV="${COMPARE_SWEEP_BASE_PROFILE}"
unset SQUEEZE_COMPARE_FORMULA_MAX_ITERATIONS SQUEEZE_COMPARE_FORMULA_UNTIL_VIOLATION 2>/dev/null || true
unset SQUEEZE_COMPARE_CONTINUE_ON_FORMULA_FAIL 2>/dev/null || true

log "sweep root: ${SWEEP_ROOT}"
log "profile=${COMPARE_SWEEP_BASE_PROFILE} rounds=${ROUNDS}: ${ROUND_LABELS[*]}"
log "baseline deployment=${BASELINE_DEPLOYMENT_YAML}"
log "baseline hpa=${BASELINE_HPA_YAML}"
log "build_analyzer_image=${BUILD_ANALYZER_IMAGE:-false} up_demo_stabilize_user=${UP_DEMO_STABILIZE_USER}"
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
  if [[ "${STRESS_K6_RPS}" =~ ^[0-9]+$ ]] && ((STRESS_K6_RPS >= 260)) \
    && [[ "${PROFILES_CSV}" == "up_demo" ]]; then
    log "WARNING: STRESS_K6_RPS=${STRESS_K6_RPS} with up_demo (preset 220) — use up_demo_strict for aligned metadata"
  fi

  apply_advanced_vanilla_compare_env
  log "=== round ${idx}/${ROUNDS} STRESS_K6_RPS=${STRESS_K6_RPS} STRESS_K6_DURATION=${STRESS_K6_DURATION:-<profile default>} SQUEEZE_SETTLE_SECONDS=${SQUEEZE_SETTLE_SECONDS:-30} (advanced-llm vs vanilla-llm) ==="
  log "squeeze env: until_violation=${SQUEEZE_UNTIL_VIOLATION} max_iter=${SQUEEZE_MAX_ITERATIONS} llm_pure=${SQUEEZE_LLM_PURE:-<unset>} llm_down_boundary=${SQUEEZE_LLM_DOWN_BOUNDARY:-<unset>} sync=${COMPARE_SYNC_MODE}"

  round_ok=1
  if ! ./scripts/run_cluster_profiles.sh --compare-advanced-vs-vanilla-llm; then
    log "ERROR: round ${idx} failed — partial data may exist under ${SWEEP_ROOT}"
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
  status="OK"
  if [[ "${round_ok}" -eq 0 ]]; then
    status="FAILED"
  fi
  {
    echo "round=${idx}/${ROUNDS}"
    echo "status=${status}"
    echo "label=${ROUND_LABELS[r]}"
    echo "STRESS_K6_RPS=${STRESS_K6_RPS}"
    echo "STRESS_K6_DURATION=${STRESS_K6_DURATION:-}"
    echo "PROFILES_CSV=${PROFILES_CSV}"
    echo "SQUEEZE_UNTIL_VIOLATION=${SQUEEZE_UNTIL_VIOLATION}"
    echo "SQUEEZE_MAX_ITERATIONS=${SQUEEZE_MAX_ITERATIONS}"
    echo "SQUEEZE_LLM_PURE=${SQUEEZE_LLM_PURE:-}"
    echo "COMPARE_SYNC_MODE=${COMPARE_SYNC_MODE}"
    echo "sweep_root=${SWEEP_ROOT}"
    echo "run_dir=${SWEEP_ROOT}/${run_label}"
    echo "advanced_run=${SWEEP_ROOT}/${run_label}/advanced-llm-run"
    echo "vanilla_run=${SWEEP_ROOT}/${run_label}/vanilla-llm-run"
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
