#!/usr/bin/env bash
# Engineer UP redo: fat static profiling → derive → verify → compare → archive.
#
# RPS default: 220, 240, 260. Low-time defaults: 60s k6, 15s settle.
#
# Usage:
#   BUILD_ANALYZER_IMAGE=true KUBE_CONTEXT=monitoring \
#   ./scripts/chain_engineer_up_fat_profile_sweep.sh
#
# Optional:
#   COMPARE_SWEEP_RPS=220,240,260
#   COMPARE_SWEEP_K6_DURATION=60s
#   SQUEEZE_SETTLE_SECONDS=15
#   CHAIN_SKIP_PROFILE=1   # reuse SWEEP_ROOT profiling only
#   CHAIN_SKIP_ARCHIVE=1
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"
export ROOT

# shellcheck source=scripts/lib/find_advanced_artifact_run.sh
source "${ROOT}/scripts/lib/find_advanced_artifact_run.sh"

: "${COMPARE_SWEEP_RPS:=220,240,260}"
: "${COMPARE_SWEEP_BASE_PROFILE:=up_demo}"
: "${BUILD_ANALYZER_IMAGE:=true}"
: "${KUBE_CONTEXT:=monitoring}"
: "${COMPARE_SWEEP_K6_DURATION:=60s}"
: "${SQUEEZE_SETTLE_SECONDS:=15}"
: "${SWEEP_NAME_PREFIX:=engineer-up-fat-profile}"

export BUILD_ANALYZER_IMAGE KUBE_CONTEXT COMPARE_SWEEP_K6_DURATION SQUEEZE_SETTLE_SECONDS
export COMPARE_SWEEP_RPS COMPARE_SWEEP_BASE_PROFILE STRESS_K6_DURATION="${COMPARE_SWEEP_K6_DURATION}"

STAMP="$(date +%Y%m%d-%H%M%S)"
SWEEP_ROOT="${SWEEP_ROOT:-${ROOT}/results-from-cluster/${SWEEP_NAME_PREFIX}-${STAMP}}"
CHAIN_LOG="${CHAIN_LOG:-${ROOT}/results/cluster-run-logs/chain-engineer-up-fat-profile-${STAMP}.log}"
mkdir -p "$(dirname "${CHAIN_LOG}")" "${SWEEP_ROOT}"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [chain-engineer-up] $*" | tee -a "${CHAIN_LOG}"; }

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

declare -a ROUND_LABELS=()
# shellcheck source=scripts/lib/expand_compare_sweep_matrix.sh
source "${ROOT}/scripts/lib/expand_compare_sweep_matrix.sh"
if ! parse_compare_sweep_rps_matrix "${COMPARE_SWEEP_RPS}"; then
  exit 1
fi

log "sweep root: ${SWEEP_ROOT}"
log "rps=${COMPARE_SWEEP_RPS} k6=${COMPARE_SWEEP_K6_DURATION} settle=${SQUEEZE_SETTLE_SECONDS}s"

# --- Phase 1: fat static profiling (5×150m/75Mi + HPA) ---
if [[ "${CHAIN_SKIP_PROFILE:-}" != "1" ]]; then
  log "=== phase 1: fat UP profiling (${ROUNDS} rounds) ==="
  export SWEEP_ROOT SWEEP_NAME_PREFIX
  if ! ./scripts/run_up_demo_static_baseline_sweep.sh 2>&1 | tee -a "${CHAIN_LOG}"; then
    log "ERROR: profiling sweep failed"
    exit 1
  fi
else
  log "=== phase 1: skipped (CHAIN_SKIP_PROFILE=1) ==="
  if [[ ! -d "${SWEEP_ROOT}" ]]; then
    log "ERROR: SWEEP_ROOT missing: ${SWEEP_ROOT}"
    exit 1
  fi
fi

# --- Phase 2–3: derive + verify per round ---
log "=== phase 2–3: derive + verify ==="
declare -a SYNCED_RPS=()
for ((r = 0; r < ROUNDS; r++)); do
  idx=$((r + 1))
  rps="${CLEAN_RPS[r]}"
  run_label="run-${idx}"
  if [[ -f "${SWEEP_ROOT}/.last_sync_r${idx}.txt" ]]; then
    run_label="$(tr -d '\r\n' < "${SWEEP_ROOT}/.last_sync_r${idx}.txt")"
  fi
  profile_exp="${SWEEP_ROOT}/${run_label}/experiment.json"
  baseline_dir="${SWEEP_ROOT}/${run_label}/engineer-baseline"

  if [[ ! -f "${profile_exp}" ]]; then
    log "ERROR: missing profiling experiment ${profile_exp}"
    exit 1
  fi

  log "--- rps=${rps} profile=${profile_exp} ---"
  rm -rf "${baseline_dir}"
  if ! ./scripts/derive_engineer_baseline.sh "${profile_exp}" "${baseline_dir}" 2>&1 | tee -a "${CHAIN_LOG}"; then
    log "ERROR: derive failed rps=${rps}"
    exit 1
  fi
  cp "${profile_exp}" "${baseline_dir}/profiling-experiment.json"

  export ENGINEER_VERIFY_SWEEP_ROOT="${SWEEP_ROOT}/verify-rps${rps}-${STAMP}"
  if ! ./scripts/run_engineer_derived_verify.sh "${baseline_dir}" 2>&1 | tee -a "${CHAIN_LOG}"; then
    log "ERROR: verify failed rps=${rps}"
    exit 1
  fi

  adv_run="$(find_advanced_run_for_rps UP "${rps}")" || {
    log "ERROR: no advanced artifact run for UP rps=${rps}"
    exit 1
  }
  sub="$(advanced_llm_subdir "${adv_run}")" || {
    log "ERROR: no llm-run under ${adv_run}"
    exit 1
  }
  adv_engineer_dir="${adv_run}/${sub}/engineer-baseline"
  rm -rf "${adv_engineer_dir}"
  mkdir -p "${adv_engineer_dir}"
  cp -R "${baseline_dir}/." "${adv_engineer_dir}/"
  log "synced engineer-baseline → ${adv_engineer_dir}"
  SYNCED_RPS+=("${rps}")
done

# --- Phase 4: compare + archive ---
log "=== phase 4: compare + archive ==="
if ! ./scripts/build_engineer_vs_advanced_comparisons.sh 2>&1 | tee -a "${CHAIN_LOG}"; then
  log "ERROR: build comparisons failed"
  exit 1
fi

if [[ "${CHAIN_SKIP_ARCHIVE:-}" != "1" ]]; then
  for rps in "${SYNCED_RPS[@]}"; do
    log "archiving UP rps=${rps}"
    if ! ./scripts/archive_engineer_vs_advanced_run.sh UP "${rps}" 2>&1 | tee -a "${CHAIN_LOG}"; then
      log "ERROR: archive failed rps=${rps}"
      exit 1
    fi
  done
else
  log "archive skipped (CHAIN_SKIP_ARCHIVE=1)"
fi

log "done sweep=${SWEEP_ROOT} archive=${ROOT}/artifacts_latest/ENGINEER_VS_ADVANCED_LLM/UP/"
