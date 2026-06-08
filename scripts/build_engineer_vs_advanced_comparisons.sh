#!/usr/bin/env bash
# Build engineer (B1) vs advanced-llm comparisons into artifacts/ENGINEER_VS_ADVANCED_LLM/.
#
# Requires engineer sweep: one experiment.json per RPS with cpu_request_m>=100 (fat baseline).
#   UP:   ./scripts/run_up_demo_engineer_baseline_sweep.sh
#   DOWN: ./scripts/run_down_demo_static_baseline_sweep.sh  (same fat YAML)
#
# Advanced side: canonical GOOD_* runs under artifacts/VANILLA_LLM_VS_ADVANCED_LLM/ (advanced-llm-run only).
#
# Usage:
#   ENGINEER_UP_SWEEP=results-from-cluster/engineer-up-sweep-<stamp> \
#   ENGINEER_DOWN_SWEEP=results-from-cluster/static-down-sweep-<stamp> \
#   ./scripts/build_engineer_vs_advanced_comparisons.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"
export PYTHONPATH="${ROOT}${PYTHONPATH:+:${PYTHONPATH}}"

ARTIFACTS="${ROOT}/artifacts/ENGINEER_VS_ADVANCED_LLM"
ADVANCED_ROOT="${ADVANCED_ROOT:-${ROOT}/artifacts/VANILLA_LLM_VS_ADVANCED_LLM}"

# Default engineer sweeps (override if you have newer stamps)
ENGINEER_UP_SWEEP="${ENGINEER_UP_SWEEP:-${ROOT}/results-from-cluster/static-up-sweep-20260527-125059}"
ENGINEER_DOWN_SWEEP="${ENGINEER_DOWN_SWEEP:-}"

log() { echo "[engineer-vs-advanced] $*"; }

is_fat_engineer_exp() {
  local exp="$1"
  python3 - <<PY
import json, sys
e = json.load(open("${exp}"))
cpu = int((e.get("config") or {}).get("cpu_request_m") or 0)
# Fat engineer baseline uses 150m requests; thin strawman is 50m.
sys.exit(0 if cpu >= 100 else 1)
PY
}

find_engineer_exp() {
  local sweep="$1"
  local rps="$2"
  local exp
  if [[ ! -d "${sweep}" ]]; then
    return 1
  fi
  for exp in "${sweep}"/run-"${rps}"/experiment.json "${sweep}"/run-*/experiment.json; do
    [[ -f "${exp}" ]] || continue
    local got
    got="$(python3 - <<PY
import json
e=json.load(open("${exp}"))
print(e.get("workload",{}).get("target_requests_per_second",""))
PY
)"
    if [[ "${got}" == "${rps}" ]] && is_fat_engineer_exp "${exp}"; then
        echo "${exp}"
        return 0
    fi
  done
  return 1
}

# DOWN fat-start matches advanced iter 1 before any squeeze — valid B1 proxy when sweep missing.
find_engineer_proxy_iter1() {
  local orient="$1"
  local rps="$2"
  local d="${ADVANCED_ROOT}/${orient}"
  local run
  for run in "${d}"/GOOD_BOTH_WIN_run*rps"${rps}"* "${d}"/GOOD_COST_WIN_run*rps"${rps}"* "${d}"/GOOD_*; do
    [[ -d "${run}" ]] || continue
    local exp="${run}/advanced-llm-run/iteration-1/experiment.json"
    [[ -f "${exp}" ]] || continue
    if is_fat_engineer_exp "${exp}"; then
      echo "${exp}"
      return 0
    fi
  done
  return 1
}

find_advanced_boundary() {
  local orient="$1"
  local rps="$2"
  local d="${ADVANCED_ROOT}/${orient}"
  [[ -d "${d}" ]] || return 1
  local run
  for run in "${d}"/GOOD_*run*rps"${rps}"* "${d}"/GOOD_*run-*; do
    [[ -d "${run}" ]] || continue
    local b="${run}/advanced-llm-run/cost-effective-boundary.json"
    [[ -f "${b}" ]] || continue
    echo "${b}"
    return 0
  done
  return 1
}

build_pair() {
  local orient="$1"
  local rps="$2"
  local engineer_sweep="$3"
  local scenario="$4"

  local engineer_exp adv_b engineer_note=""
  if engineer_exp="$(find_engineer_exp "${engineer_sweep}" "${rps}" 2>/dev/null)"; then
    engineer_note="engineer sweep"
  elif [[ "${orient}" == "DOWN" && "${ENGINEER_USE_ITER1_PROXY:-1}" == "1" ]]; then
    if engineer_exp="$(find_engineer_proxy_iter1 "${orient}" "${rps}")"; then
      engineer_note="proxy: advanced-llm iteration-1 (fat wired, no squeeze)"
    fi
  fi
  if [[ -z "${engineer_exp:-}" ]]; then
    log "SKIP ${orient} rps=${rps}: no fat engineer experiment (sweep=${engineer_sweep:-none})"
    return 0
  fi
  if ! adv_b="$(find_advanced_boundary "${orient}" "${rps}")"; then
    log "SKIP ${orient} rps=${rps}: no advanced boundary under ${ADVANCED_ROOT}"
    return 0
  fi

  local out_dir="${ARTIFACTS}/${orient}/run-rps${rps}"
  mkdir -p "${out_dir}"
  cp "${engineer_exp}" "${out_dir}/engineer-experiment.json"
  cp "${adv_b}" "${out_dir}/advanced-boundary.json"

  python3 - <<PY
from pathlib import Path
from analysis.compare_static_baseline import compare_engineer_vs_advanced

root = Path("${ROOT}")
out = Path("${out_dir}")
text = compare_engineer_vs_advanced(
    Path("${engineer_exp}"),
    Path("${adv_b}"),
    scenario="${scenario}",
    rps=${rps},
    engineer_data=str(Path("${engineer_exp}").parent.relative_to(root)),
    advanced_data=str(Path("${adv_b}").parent.relative_to(root)),
)
note = "${engineer_note}"
if note:
    text = text.replace("---\\n", f"---\\n\\n- **Engineer source**: {note}\\n", 1)
(out / "comparison.md").write_text(text)
print("wrote", out / "comparison.md", "(", note or "sweep", ")")
PY
}

mkdir -p "${ARTIFACTS}/UP" "${ARTIFACTS}/DOWN"

log "advanced root: ${ADVANCED_ROOT}"
log "engineer UP sweep: ${ENGINEER_UP_SWEEP}"
log "engineer DOWN sweep: ${ENGINEER_DOWN_SWEEP:-<not set>}"

for rps in 220 240 260; do
  build_pair UP "${rps}" "${ENGINEER_UP_SWEEP}" up_demo
done

for rps in 25 35 45; do
  build_pair DOWN "${rps}" "${ENGINEER_DOWN_SWEEP}" down_demo
done

log "done -> ${ARTIFACTS}"
