# Resolve Advanced LLM artifact runs from vanilla and formula archives.
#
# Vanilla compare dirs use advanced-llm-run/; formula compare dirs use llm-run/ (same optimizer).

shopt -s nullglob 2>/dev/null || true
#
#   advanced_llm_subdir "$run_dir"          -> advanced-llm-run | llm-run
#   find_advanced_run_for_rps DOWN 55       -> /path/to/GOOD_...run-1-rps55-...
#   find_engineer_verify_exp DOWN 55        -> .../verify-run/experiment.json
#   find_advanced_boundary DOWN 55          -> .../cost-effective-boundary.json
#   find_profiling_iter1_exp DOWN 55        -> .../iteration-1/experiment.json

find_advanced_artifact_roots() {
  local root="${1:-${ROOT:-.}}"
  printf '%s\n' \
    "${root}/artifacts_latest/FORMULA_VS_ADVANCED_LLM" \
    "${root}/artifacts_latest/VANILLA_LLM_VS_ADVANCED_LLM"
}

advanced_llm_subdir() {
  local run_dir="$1"
  if [[ -d "${run_dir}/advanced-llm-run" ]]; then
    echo "advanced-llm-run"
    return 0
  fi
  if [[ -d "${run_dir}/llm-run" ]]; then
    echo "llm-run"
    return 0
  fi
  return 1
}

# Emit candidate run dirs best-first: GOOD_COST_WIN, GOOD_BOTH_WIN, NEAR_TIE, BAD_, then others.
_iter_advanced_run_candidates() {
  local orient="$1" rps="$2" root orient_dir run prefix
  for prefix in GOOD_COST_WIN GOOD_BOTH_WIN NEAR_TIE BAD_ GOOD_; do
    while IFS= read -r root; do
      orient_dir="${root}/${orient}"
      [[ -d "${orient_dir}" ]] || continue
      for run in "${orient_dir}"/${prefix}*run*rps"${rps}"*; do
        [[ -d "${run}" ]] || continue
        advanced_llm_subdir "${run}" >/dev/null || continue
        printf '%s\n' "${run}"
      done
    done < <(find_advanced_artifact_roots "${ROOT}")
  done
}

find_advanced_run_for_rps() {
  local orient="$1" rps="$2" run
  while IFS= read -r run; do
    echo "${run}"
    return 0
  done < <(_iter_advanced_run_candidates "${orient}" "${rps}")
  return 1
}

# Prefer a run that already has engineer verify-run for this RPS.
find_engineer_verify_exp() {
  local orient="$1" rps="$2" run sub exp
  while IFS= read -r run; do
    sub="$(advanced_llm_subdir "${run}")" || continue
    exp="${run}/${sub}/iteration-1/engineer-baseline/verify-run/experiment.json"
    if [[ -f "${exp}" ]]; then
      echo "${exp}"
      return 0
    fi
  done < <(_iter_advanced_run_candidates "${orient}" "${rps}")
  return 1
}

find_advanced_boundary() {
  local orient="$1" rps="$2" run sub b
  while IFS= read -r run; do
    sub="$(advanced_llm_subdir "${run}")" || continue
    b="${run}/${sub}/cost-effective-boundary.json"
    if [[ -f "${b}" ]]; then
      echo "${b}"
      return 0
    fi
  done < <(_iter_advanced_run_candidates "${orient}" "${rps}")
  return 1
}

find_profiling_iter1_exp() {
  local orient="$1" rps="$2" run sub exp
  while IFS= read -r run; do
    sub="$(advanced_llm_subdir "${run}")" || continue
    exp="${run}/${sub}/iteration-1/experiment.json"
    if [[ -f "${exp}" ]]; then
      echo "${exp}"
      return 0
    fi
  done < <(_iter_advanced_run_candidates "${orient}" "${rps}")
  return 1
}

# Run dir backing a verified engineer experiment (for archive / pairing).
find_engineer_source_run() {
  local orient="$1" rps="$2" exp d
  if ! exp="$(find_engineer_verify_exp "${orient}" "${rps}")"; then
    return 1
  fi
  d="${exp}"
  d="$(dirname "${d}")"
  d="$(dirname "${d}")"
  d="$(dirname "${d}")"
  d="$(dirname "${d}")"
  d="$(dirname "${d}")"
  echo "${d}"
}
