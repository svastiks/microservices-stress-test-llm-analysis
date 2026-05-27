#!/usr/bin/env bash
# After each compare-sweep round: verify local run-<n>/ exists; resync PVC before next round.

sweep_round_has_local_bundle() {
  local run_dir="$1"
  if [[ "${COMPARE_SYNC_MODE:-}" == "hpa" ]]; then
    [[ -f "${run_dir}/comparison.md" && -f "${run_dir}/hpa-run/cost-effective-boundary.json" ]] \
      && ! [[ -d "${run_dir}/formula-run" ]]
    return
  fi
  [[ -f "${run_dir}/comparison.md" ]] \
    || [[ -f "${run_dir}/formula-run/cost-effective-boundary.json" ]] \
    || [[ -f "${run_dir}/hpa-run/cost-effective-boundary.json" ]]
}

finalize_sweep_round_local() {
  local sweep_root="$1"
  local idx="$2"
  local round_ok="${3:-1}"
  local run_dir="${sweep_root}/run-${idx}"
  local log_fn="${4:-echo}"

  if sweep_round_has_local_bundle "${run_dir}"; then
    "${log_fn}" "round ${idx}: local bundle OK at ${run_dir} — safe to continue"
    printf '%s\n' "run-${idx}" > "${sweep_root}/.last_sync_r${idx}.txt" 2>/dev/null || true
    return 0
  fi

  "${log_fn}" "round ${idx}: local bundle missing — copying PVC to ${run_dir} before next round"
  local root_dir="${ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
  if ! COMPARE_SWEEP_ROUND="${idx}" RESULTS_DEST="${sweep_root}" \
    "${root_dir}/scripts/run_cluster_profiles.sh" --sync-pvc-only; then
    "${log_fn}" "WARNING: round ${idx}: PVC sync failed"
  fi

  if sweep_round_has_local_bundle "${run_dir}"; then
    "${log_fn}" "round ${idx}: local bundle saved at ${run_dir}"
    return 0
  fi

  "${log_fn}" "WARNING: round ${idx}: still no local bundle at ${run_dir} (cluster job may have failed early)"
  return 1
}
