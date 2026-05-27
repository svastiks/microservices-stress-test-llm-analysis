#!/usr/bin/env bash
# Method 2: HPA-only vs vanilla LLM (up_demo RPS ladder).
# Artifacts: results-from-cluster/compare-hpa-up-sweep-<stamp>/run-N/{hpa-run,llm-run,comparison.md}
#
#   BUILD_ANALYZER_IMAGE=true SQUEEZE_LLM_PURE=1 \
#     COMPARE_SWEEP_RPS=200,220,240,260,280 COMPARE_SWEEP_ROUNDS=5 \
#     ./scripts/run_up_demo_hpa_vs_llm_sweep.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

: "${COMPARE_SWEEP_BASE_PROFILE:=up_demo}"
: "${COMPARE_SWEEP_RPS:=200,220,240,260,280}"

SWEEP_STAMP="$(date +%Y%m%d-%H%M%S)"
SWEEP_PARENT="${COMPARE_SWEEP_PARENT:-${ROOT}/results-from-cluster}"
SWEEP_ROOT="${SWEEP_PARENT}/compare-hpa-up-sweep-${SWEEP_STAMP}"
mkdir -p "${SWEEP_ROOT}"

IFS=',' read -r -a RPS_LIST <<< "${COMPARE_SWEEP_RPS}"
CLEAN_RPS=()
for _r in "${RPS_LIST[@]}"; do
  _q="$(echo "${_r}" | xargs)"
  [[ -n "${_q}" ]] && CLEAN_RPS+=("${_q}")
done
ROUNDS="${COMPARE_SWEEP_ROUNDS:-${#CLEAN_RPS[@]}}"
if ((${#CLEAN_RPS[@]} == 0)) || ! [[ "${ROUNDS}" =~ ^[0-9]+$ ]] || ((ROUNDS < 1)) || ((ROUNDS > ${#CLEAN_RPS[@]})); then
  echo "invalid COMPARE_SWEEP_RPS / COMPARE_SWEEP_ROUNDS" >&2
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

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [hpa-sweep-up] $*"; }

# shellcheck source=scripts/lib/squeeze_up_demo_env.sh
source "${ROOT}/scripts/lib/squeeze_up_demo_env.sh"
# shellcheck source=scripts/lib/squeeze_hpa_compare_env.sh
source "${ROOT}/scripts/lib/squeeze_hpa_compare_env.sh"
# shellcheck source=scripts/lib/sweep_round_finalize.sh
source "${ROOT}/scripts/lib/sweep_round_finalize.sh"

export RESULTS_DEST="${SWEEP_ROOT}"
log "sweep root: ${SWEEP_ROOT} profile=${COMPARE_SWEEP_BASE_PROFILE} rounds=${ROUNDS}"

any_fail=0
for ((r = 0; r < ROUNDS; r++)); do
  idx=$((r + 1))
  export COMPARE_SWEEP_ROUND="${idx}"
  export STRESS_K6_RPS="${CLEAN_RPS[r]}"
  export PROFILES_CSV="${COMPARE_SWEEP_BASE_PROFILE}"
  log "=== round ${idx}/${ROUNDS} STRESS_K6_RPS=${STRESS_K6_RPS} ==="
  apply_up_demo_compare_env
  apply_hpa_compare_env
  round_ok=1
  if ! ./scripts/run_cluster_profiles.sh --compare-hpa-vs-llm; then
    log "ERROR: round ${idx} failed"
    round_ok=0
    any_fail=1
  fi
  finalize_sweep_round_local "${SWEEP_ROOT}" "${idx}" "${round_ok}" log || true
  {
    echo "round=${idx}/${ROUNDS}"
    echo "STRESS_K6_RPS=${STRESS_K6_RPS}"
    echo "run_dir=${SWEEP_ROOT}/run-${idx}"
  } > "${SWEEP_ROOT}/sweep-round-${idx}.txt"
done
unset COMPARE_SWEEP_ROUND 2>/dev/null || true
[[ "${any_fail}" -eq 0 ]] || exit 1
log "done"
