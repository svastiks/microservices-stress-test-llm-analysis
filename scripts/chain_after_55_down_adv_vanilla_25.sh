#!/usr/bin/env bash
# Wait for an in-flight 55 DOWN compare, then:
#   1) advanced vs vanilla DOWN @ 25 RPS
#   2) advanced vs vanilla UP @ 220 RPS (override with CHAIN_UP_RPS)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

WAIT_PID="${1:-}"
DOWN_LOG="${CHAIN_DOWN_LOG:-results/cluster-run-logs/stress-analyzer-down-demo-55-rerun2.log}"
CHAIN_LOG="${CHAIN_LOG:-results/cluster-run-logs/chain-55-then-adv-vanilla-25.log}"
ADV_DOWN_LOG="${CHAIN_ADV_DOWN_LOG:-results/cluster-run-logs/stress-analyzer-down-adv-vs-vanilla-25.log}"
ADV_UP_LOG="${CHAIN_ADV_UP_LOG:-results/cluster-run-logs/stress-analyzer-up-adv-vs-vanilla-220.log}"
CHAIN_UP_RPS="${CHAIN_UP_RPS:-220}"

mkdir -p results/cluster-run-logs

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [chain] $*" | tee -a "${CHAIN_LOG}"; }

if [[ -n "${WAIT_PID}" ]]; then
  log "waiting for PID ${WAIT_PID} (55 DOWN compare)..."
  while kill -0 "${WAIT_PID}" 2>/dev/null; do
    sleep 30
  done
  log "PID ${WAIT_PID} exited."
else
  log "no WAIT_PID — sleeping 5m then checking DOWN log for completion..."
  sleep 300
fi

if [[ -f "${DOWN_LOG}" ]] && grep -q "all 1 rounds completed" "${DOWN_LOG}"; then
  log "55 DOWN sweep OK per ${DOWN_LOG}"
elif [[ -f "${DOWN_LOG}" ]] && grep -q "sweep finished with failures" "${DOWN_LOG}"; then
  log "WARNING: 55 DOWN reported failures — still starting adv-vs-vanilla."
else
  log "WARNING: could not confirm 55 success — still starting adv-vs-vanilla."
fi

log "starting advanced vs vanilla DOWN @ 25 RPS..."
export BUILD_ANALYZER_IMAGE="${BUILD_ANALYZER_IMAGE:-false}"
export KUBE_CONTEXT="${KUBE_CONTEXT:-monitoring}"
export COMPARE_SWEEP_K6_DURATION="${COMPARE_SWEEP_K6_DURATION:-90s}"
export COMPARE_SWEEP_RPS=25
export COMPARE_SWEEP_ROUNDS=1
export SQUEEZE_SETTLE_SECONDS="${SQUEEZE_SETTLE_SECONDS:-30}"

./scripts/run_down_demo_advanced_vs_vanilla_sweep.sh 2>&1 | tee -a "${ADV_DOWN_LOG}"
log "advanced vs vanilla DOWN @ 25 finished."

log "starting advanced vs vanilla UP @ ${CHAIN_UP_RPS} RPS..."
export COMPARE_SWEEP_RPS="${CHAIN_UP_RPS}"
export COMPARE_SWEEP_ROUNDS=1

./scripts/run_up_demo_advanced_vs_vanilla_sweep.sh 2>&1 | tee -a "${ADV_UP_LOG}"
log "advanced vs vanilla UP @ ${CHAIN_UP_RPS} finished."
