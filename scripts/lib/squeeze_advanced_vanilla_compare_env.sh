# Advanced vs vanilla LLM compare (isolated PVC subdirs; profile sets UP vs DOWN path).
# shellcheck shell=bash
_av_lib_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/lib/squeeze_up_demo_env.sh
source "${_av_lib_dir}/squeeze_up_demo_env.sh"
# shellcheck source=scripts/lib/squeeze_llm_env.sh
source "${_av_lib_dir}/squeeze_llm_env.sh"

_apply_advanced_vanilla_compare_common() {
  export COMPARE_SYNC_MODE=advanced-vanilla
  export SQUEEZE_COMPARE_SUBDIR_ADVANCED="${SQUEEZE_COMPARE_SUBDIR_ADVANCED:-squeeze-compare-advanced-llm}"
  export SQUEEZE_COMPARE_SUBDIR_VANILLA="${SQUEEZE_COMPARE_SUBDIR_VANILLA:-squeeze-compare-vanilla-llm}"
  export SQUEEZE_COMPARE_CONTINUE_ON_ADVANCED_FAIL="${SQUEEZE_COMPARE_CONTINUE_ON_ADVANCED_FAIL:-1}"
  export SQUEEZE_COMPARE_PRUNE_STALE_FORMULA="${SQUEEZE_COMPARE_PRUNE_STALE_FORMULA:-1}"
  unset SQUEEZE_COMPARE_FORMULA_MAX_ITERATIONS 2>/dev/null || true
  unset SQUEEZE_COMPARE_FORMULA_UNTIL_VIOLATION 2>/dev/null || true
  unset SQUEEZE_COMPARE_CONTINUE_ON_FORMULA_FAIL 2>/dev/null || true
  apply_compare_sweep_fast_if_requested
}

# COMPARE_SWEEP_FAST=1 → 60s k6 + 15s settle (override with COMPARE_SWEEP_K6_DURATION / SQUEEZE_SETTLE_SECONDS).
apply_compare_sweep_fast_if_requested() {
  if [[ "${COMPARE_SWEEP_FAST:-}" != "1" ]]; then
    return 0
  fi
  export COMPARE_SWEEP_K6_DURATION="${COMPARE_SWEEP_K6_DURATION:-60s}"
  export STRESS_K6_DURATION="${STRESS_K6_DURATION:-${COMPARE_SWEEP_K6_DURATION}}"
  export SQUEEZE_SETTLE_SECONDS="${SQUEEZE_SETTLE_SECONDS:-15}"
}

# up_demo: thin baseline + UP recovery squeeze env
apply_advanced_vanilla_compare_env() {
  apply_up_demo_compare_env
  _apply_advanced_vanilla_compare_common
}

# down_demo: DOWN boundary search (same LLM arms as formula-vs-llm DOWN)
apply_advanced_vanilla_down_compare_env() {
  apply_llm_squeeze_env
  _apply_advanced_vanilla_compare_common
}
