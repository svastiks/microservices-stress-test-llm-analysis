# Shared env for squeeze compare + LLM-only runs (formula and LLM arms).
# shellcheck shell=bash
apply_llm_squeeze_env() {
  export SQUEEZE_UNTIL_VIOLATION="${SQUEEZE_UNTIL_VIOLATION:-true}"
  export SQUEEZE_MAX_ITERATIONS="${SQUEEZE_MAX_ITERATIONS:-16}"
  export SQUEEZE_LLM_DOWN_BOUNDARY="${SQUEEZE_LLM_DOWN_BOUNDARY:-1}"
  # Research mode: YAML sizing from LLM+prompt only (no formula fallbacks / violation probe).
  export SQUEEZE_LLM_PURE="${SQUEEZE_LLM_PURE:-1}"
  # PASS/FAIL: p95 SLO or CPU util above threshold (see analysis/experiment_build.py).
  export SQUEEZE_CPU_UTIL_FAIL_PCT="${SQUEEZE_CPU_UTIL_FAIL_PCT:-95}"
  # Block next DOWN diff when prior PASS was already hot (supplement to util FAIL).
  export SQUEEZE_LLM_CPU_GUARD_PCT="${SQUEEZE_LLM_CPU_GUARD_PCT:-95}"
  export SQUEEZE_LLM_P95_REGRESSION_RATIO="${SQUEEZE_LLM_P95_REGRESSION_RATIO:-99}"
  # After DOWN apply, wait until ready replicas match spec (avoids k6 on stale pod count).
  export SQUEEZE_WAIT_REPLICAS_STEADY="${SQUEEZE_WAIT_REPLICAS_STEADY:-1}"
  # Off by default in pure LLM runs — probe uses fixed % cuts (formula-like).
  export SQUEEZE_UNTIL_VIOLATION_PROBE_LLM="${SQUEEZE_UNTIL_VIOLATION_PROBE_LLM:-0}"
  # Pure LLM: resource-first phase before replica cuts (Python vetoes only).
  export SQUEEZE_LLM_REPLICA_CPU_REQUEST_CEILING_M="${SQUEEZE_LLM_REPLICA_CPU_REQUEST_CEILING_M:-100}"
  export SQUEEZE_LLM_MIN_RESOURCE_PASSES_BEFORE_REPLICA="${SQUEEZE_LLM_MIN_RESOURCE_PASSES_BEFORE_REPLICA:-2}"
  export SQUEEZE_REPLICA_STEADY_CHECKS="${SQUEEZE_REPLICA_STEADY_CHECKS:-3}"
  export SQUEEZE_STALL_RESOURCE_STEP_PCT="${SQUEEZE_STALL_RESOURCE_STEP_PCT:-0.08}"
}
