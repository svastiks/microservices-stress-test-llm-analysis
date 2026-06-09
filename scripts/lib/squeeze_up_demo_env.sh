# UP-demo compare only — do not source squeeze_llm_env.sh (down_demo pure-LLM knobs).
# shellcheck shell=bash
apply_up_demo_compare_env() {
  export SQUEEZE_UNTIL_VIOLATION="${SQUEEZE_UNTIL_VIOLATION:-false}"
  export SQUEEZE_MAX_ITERATIONS="${SQUEEZE_MAX_ITERATIONS:-16}"
  export SQUEEZE_COMPARE_FORMULA_MAX_ITERATIONS="${SQUEEZE_COMPARE_FORMULA_MAX_ITERATIONS:-16}"
  export SQUEEZE_COMPARE_FORMULA_UNTIL_VIOLATION="${SQUEEZE_COMPARE_FORMULA_UNTIL_VIOLATION:-0}"
  # Match down_demo compare: vanilla LLM (YAML + prompt only; same SQUEEZE_LLM_PURE default as squeeze_llm_env.sh).
  export SQUEEZE_LLM_PURE="${SQUEEZE_LLM_PURE:-1}"
  export SQUEEZE_LLM_DOWN_BOUNDARY="${SQUEEZE_LLM_DOWN_BOUNDARY:-0}"
  # Compare hygiene: paired run-N for formula+llm; drop stale PVC runs; finish LLM even if formula errors.
  export SQUEEZE_COMPARE_PRUNE_PRIOR="${SQUEEZE_COMPARE_PRUNE_PRIOR:-1}"
  export SQUEEZE_COMPARE_CONTINUE_ON_FORMULA_FAIL="${SQUEEZE_COMPARE_CONTINUE_ON_FORMULA_FAIL:-1}"
  # UP @ 260: cap replica scale-out (cluster rollouts) and allow longer multi-pod rollouts.
  export SQUEEZE_UP_RECOVERY_MAX_REPLICAS="${SQUEEZE_UP_RECOVERY_MAX_REPLICAS:-6}"
  export SQUEEZE_ROLLOUT_TIMEOUT_S="${SQUEEZE_ROLLOUT_TIMEOUT_S:-600}"
  # Same PASS/FAIL frontier as down_demo (p95 SLO, error rate, CPU util > threshold).
  export SQUEEZE_CPU_UTIL_FAIL_PCT="${SQUEEZE_CPU_UTIL_FAIL_PCT:-95}"
  # Independent arms (default off): iter-1 may differ; judge on best_pass not row 1.
  export SQUEEZE_COMPARE_PAIRED_MEASURE="${SQUEEZE_COMPARE_PAIRED_MEASURE:-0}"
  export SQUEEZE_WARMUP_K6_DURATION="${SQUEEZE_WARMUP_K6_DURATION:-60s}"
  export SQUEEZE_SETTLE_SECONDS="${SQUEEZE_SETTLE_SECONDS:-30}"
  export SQUEEZE_COMPARE_PROBE_COUNT="${SQUEEZE_COMPARE_PROBE_COUNT:-3}"
  export SQUEEZE_COMPARE_PROBE_SETTLE_SECONDS="${SQUEEZE_COMPARE_PROBE_SETTLE_SECONDS:-15}"
  unset SQUEEZE_LLM_REPLICA_CPU_REQUEST_CEILING_M 2>/dev/null || true
  unset SQUEEZE_LLM_MIN_RESOURCE_PASSES_BEFORE_REPLICA 2>/dev/null || true
}
