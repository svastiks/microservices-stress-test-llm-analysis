#!/usr/bin/env bash
# Archive one verified engineer-vs-advanced run under artifacts_latest/ENGINEER_VS_ADVANCED_LLM/.
#
# Resolves source from vanilla (advanced-llm-run) or formula (llm-run) archives.
#
# Usage:
#   ./scripts/archive_engineer_vs_advanced_run.sh DOWN 55
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"
export ROOT

# shellcheck source=scripts/lib/find_advanced_artifact_run.sh
source "${ROOT}/scripts/lib/find_advanced_artifact_run.sh"

ORIENT="${1:?usage: $0 DOWN|UP <rps>}"
RPS="${2:?usage: $0 DOWN|UP <rps>}"
ARTIFACTS="${ROOT}/artifacts_latest/ENGINEER_VS_ADVANCED_LLM"

SRC_RUN="$(find_engineer_source_run "${ORIENT}" "${RPS}")" || {
  echo "no verified engineer run for ${ORIENT} rps=${RPS} (vanilla or formula archives)" >&2
  exit 1
}

SUB="$(advanced_llm_subdir "${SRC_RUN}")" || {
  echo "no advanced-llm-run or llm-run under ${SRC_RUN}" >&2
  exit 1
}

RUN_NAME="$(basename "${SRC_RUN}")"
ARCHIVE_NAME="${RUN_NAME}"
if [[ "${RUN_NAME}" != GOOD_* && "${RUN_NAME}" != BAD_* && "${RUN_NAME}" != NEAR_TIE_* ]]; then
  ARCHIVE_NAME="GOOD_COST_WIN_${RUN_NAME}"
fi

VERIFY_EXP="${SRC_RUN}/${SUB}/iteration-1/engineer-baseline/verify-run/experiment.json"
BASELINE_DIR="${SRC_RUN}/${SUB}/iteration-1/engineer-baseline"
PROFILE_EXP="${SRC_RUN}/${SUB}/iteration-1/experiment.json"
ADV_RUN="${SRC_RUN}/${SUB}"
COMP_SRC="${ROOT}/artifacts/ENGINEER_VS_ADVANCED_LLM/${ORIENT}/run-rps${RPS}/comparison.md"

DEST="${ARTIFACTS}/${ORIENT}/${ARCHIVE_NAME}"
rm -rf "${DEST}"
mkdir -p "${DEST}/profiling-source" "${DEST}/engineer-baseline" "${DEST}/advanced-benchmark"

cp "${PROFILE_EXP}" "${DEST}/profiling-source/experiment.json"
cp -R "${BASELINE_DIR}/." "${DEST}/engineer-baseline/"
cp -R "${ADV_RUN}/." "${DEST}/advanced-benchmark/advanced-llm-run/"
[[ -f "${SRC_RUN}/comparison.md" ]] && cp "${SRC_RUN}/comparison.md" "${DEST}/advanced-benchmark/source-comparison.md"
[[ -f "${SRC_RUN}/sweep-round-1.txt" ]] && cp "${SRC_RUN}/sweep-round-1.txt" "${DEST}/advanced-benchmark/"

if [[ -f "${COMP_SRC}" ]]; then
  cp "${COMP_SRC}" "${DEST}/comparison.md"
else
  echo "WARN: ${COMP_SRC} missing — run build_engineer_vs_advanced_comparisons.sh first" >&2
fi

python3 - <<PY
import json
from pathlib import Path

dest = Path("${DEST}")
verify = json.loads((dest / "engineer-baseline/verify-run/experiment.json").read_text())
adv = json.loads((dest / "advanced-benchmark/advanced-llm-run/cost-effective-boundary.json").read_text())
eng_cost = (verify.get("cost") or {}).get("cost_score")
adv_cost = adv.get("cost_best_pass_score")
cfg = verify.get("config") or {}
status = "FAIL" if (verify.get("failure") or {}).get("failed") else "PASS"
adv_wins = eng_cost is not None and adv_cost is not None and float(adv_cost) < float(eng_cost)
lines = [
    "# Engineer vs Advanced archive summary",
    "",
    f"- **RPS**: ${RPS} (${ORIENT})",
    f"- **Source archive**: ${SRC_RUN}",
    f"- **Advanced subdir**: ${SUB} (formula llm-run = advanced LLM)",
    f"- **Engineer verify**: {status} {cfg.get('deployment_replicas')}×{cfg.get('cpu_request_m')}m/{cfg.get('mem_request_mib')}Mi prov_cost={eng_cost}",
    f"- **Advanced best_pass prov_cost**: {adv_cost}",
    f"- **Advanced wins cost**: {adv_wins}",
    "",
    "## Contents",
    "",
    "- profiling-source/experiment.json — advanced iter-1 metrics used to derive engineer baseline",
    "- engineer-baseline/ — derived YAML + verify-run cluster test",
    "- advanced-benchmark/advanced-llm-run/ — full advanced squeeze (from llm-run or advanced-llm-run)",
    "- advanced-benchmark/source-comparison.md — original vanilla/formula comparison",
    "- comparison.md — engineer vs advanced comparison table",
]
(dest / "README.md").write_text("\n".join(lines) + "\n")
print(f"archived → {dest}")
PY
