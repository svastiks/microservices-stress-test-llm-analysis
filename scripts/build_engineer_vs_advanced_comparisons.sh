#!/usr/bin/env bash
# Build engineer vs advanced-llm comparisons into artifacts/ENGINEER_VS_ADVANCED_LLM/.
#
# Advanced runs are resolved from artifacts_latest/VANILLA_LLM_VS_ADVANCED_LLM and
# artifacts_latest/FORMULA_VS_ADVANCED_LLM (llm-run = advanced LLM in formula archives).
#
# Usage:
#   ./scripts/build_engineer_vs_advanced_comparisons.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"
export ROOT
export PYTHONPATH="${ROOT}${PYTHONPATH:+:${PYTHONPATH}}"

# shellcheck source=scripts/lib/find_advanced_artifact_run.sh
source "${ROOT}/scripts/lib/find_advanced_artifact_run.sh"

ARTIFACTS="${ROOT}/artifacts/ENGINEER_VS_ADVANCED_LLM"
ENGINEER_UP_SWEEP="${ENGINEER_UP_SWEEP:-${ROOT}/results-from-cluster/static-up-sweep-20260527-125059}"
ENGINEER_DOWN_SWEEP="${ENGINEER_DOWN_SWEEP:-}"

log() { echo "[engineer-vs-advanced] $*"; }

is_fat_engineer_exp() {
  local exp="$1"
  python3 - <<PY
import json, sys
e = json.load(open("${exp}"))
cpu = int((e.get("config") or {}).get("cpu_request_m") or 0)
sys.exit(0 if cpu >= 100 else 1)
PY
}

find_engineer_exp() {
  local sweep="$1" rps="$2" exp got
  if [[ ! -d "${sweep}" ]]; then
    return 1
  fi
  for exp in "${sweep}"/run-"${rps}"/experiment.json "${sweep}"/run-*/experiment.json; do
    [[ -f "${exp}" ]] || continue
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

advanced_boundary_for_run() {
  local run="$1" sub b
  sub="$(advanced_llm_subdir "${run}")" || return 1
  b="${run}/${sub}/cost-effective-boundary.json"
  [[ -f "${b}" ]] || return 1
  echo "${b}"
}

build_pair() {
  local orient="$1" rps="$2" engineer_sweep="$3" scenario="$4"
  local engineer_exp adv_b engineer_note="" source_run sub

  if engineer_exp="$(find_engineer_verify_exp "${orient}" "${rps}" 2>/dev/null)"; then
    engineer_note="verified: Autopilot-derived YAML + cluster k6"
    source_run="$(find_engineer_source_run "${orient}" "${rps}")"
    adv_b="$(advanced_boundary_for_run "${source_run}")" || true
  elif engineer_exp="$(find_engineer_exp "${engineer_sweep}" "${rps}" 2>/dev/null)"; then
    engineer_note="engineer sweep"
  elif [[ "${ENGINEER_USE_ITER1_PROXY:-1}" == "1" ]]; then
    if engineer_exp="$(find_profiling_iter1_exp "${orient}" "${rps}" 2>/dev/null)" \
      && is_fat_engineer_exp "${engineer_exp}"; then
      engineer_note="proxy: advanced iter-1 profiling (fat wired) — run verify first"
    fi
  fi

  if [[ -z "${engineer_exp:-}" ]]; then
    log "SKIP ${orient} rps=${rps}: no engineer experiment"
    return 0
  fi

  if [[ -z "${adv_b:-}" ]]; then
    adv_b="$(find_advanced_boundary "${orient}" "${rps}")" || {
      log "SKIP ${orient} rps=${rps}: no advanced boundary (vanilla or formula archives)"
      return 0
    }
  fi

  sub="$(advanced_llm_subdir "$(dirname "$(dirname "${adv_b}")")")"
  local out_dir="${ARTIFACTS}/${orient}/run-rps${rps}"
  mkdir -p "${out_dir}"
  cp "${engineer_exp}" "${out_dir}/engineer-experiment.json"
  cp "${adv_b}" "${out_dir}/advanced-boundary.json"

  python3 - <<PY
from pathlib import Path
from analysis.compare_static_baseline import compare_engineer_vs_advanced

root = Path("${ROOT}").resolve()
engineer_exp = Path("${engineer_exp}").resolve()
adv_b = Path("${adv_b}").resolve()
out = Path("${out_dir}")
text = compare_engineer_vs_advanced(
    engineer_exp,
    adv_b,
    scenario="${scenario}",
    rps=${rps},
    engineer_data=str(engineer_exp.parent.relative_to(root)),
    advanced_data=str(adv_b.parent.relative_to(root)),
)
note = "${engineer_note}"
source = "${sub}"
if note:
    text = text.replace("---\\n", f"---\\n\\n- **Engineer source**: {note}\\n", 1)
    text = text.replace("---\\n", f"---\\n\\n- **Advanced source**: {source} under vanilla/formula archives\\n", 1)
(out / "comparison.md").write_text(text)
print("wrote", out / "comparison.md", "(", note or "sweep", ", advanced=", source, ")")
PY
}

mkdir -p "${ARTIFACTS}/UP" "${ARTIFACTS}/DOWN}"

log "artifact roots: vanilla + formula (advanced-llm-run / llm-run)"
log "engineer UP sweep: ${ENGINEER_UP_SWEEP}"
log "engineer DOWN sweep: ${ENGINEER_DOWN_SWEEP:-<not set>}"

for rps in 220 240 260; do
  build_pair UP "${rps}" "${ENGINEER_UP_SWEEP}" up_demo
done

for rps in 25 35 45 55; do
  build_pair DOWN "${rps}" "${ENGINEER_DOWN_SWEEP}" down_demo
done

log "done -> ${ARTIFACTS}"
