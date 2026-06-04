#!/usr/bin/env bash
# Build static-vs-LLM comparison.md files from a static sweep + showcase UP LLM runs.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

STATIC_SWEEP="${1:-${ROOT}/results-from-cluster/static-up-sweep-20260527-125059}"
SHOWCASE="${SHOWCASE_UP:-${ROOT}/showcase_UP}"
LLM_SWEEP="${LLM_COMPARE_SWEEP:-${SHOWCASE}/compare-up-sweep-20260525-231308}"
LLM_280="${LLM_COMPARE_280:-${SHOWCASE}/compare-up-sweep-20260525-010051/run-1}"

export PYTHONPATH="${ROOT}${PYTHONPATH:+:${PYTHONPATH}}"

# static run-N -> RPS -> showcase run-M (llm-run)
declare -a PAIRS=(
  "220:1:2"
  "240:2:3"
  "260:3:4"
  "280:4:1:010051"
)

for spec in "${PAIRS[@]}"; do
  IFS=':' read -r rps static_idx showcase_idx alt <<<"${spec}"
  static_exp="${STATIC_SWEEP}/run-${static_idx}/experiment.json"
  if [[ "${alt:-}" == "010051" ]]; then
    llm_boundary="${LLM_280}/llm-run/cost-effective-boundary.json"
    llm_note="showcase 010051"
    showcase_run="${SHOWCASE}/compare-up-sweep-20260525-010051/run-1"
  else
    llm_boundary="${LLM_SWEEP}/run-${showcase_idx}/llm-run/cost-effective-boundary.json"
    llm_note=""
    showcase_run="${LLM_SWEEP}/run-${showcase_idx}"
  fi
  if [[ ! -f "${static_exp}" || ! -f "${llm_boundary}" ]]; then
    echo "skip rps=${rps}: missing static=${static_exp} llm=${llm_boundary}" >&2
    continue
  fi
  out_static="${STATIC_SWEEP}/run-${static_idx}/comparison.md"
  out_showcase="${showcase_run}/comparison-static.md"
  python3 - <<PY
from pathlib import Path
from analysis.compare_static_baseline import compare_static_vs_llm

text = compare_static_vs_llm(
    Path("${static_exp}"),
    Path("${llm_boundary}"),
    rps=${rps},
    static_sweep=str(Path("${STATIC_SWEEP}/run-${static_idx}").resolve().relative_to(Path("${ROOT}").resolve())),
    llm_sweep=str(Path("${showcase_run}/llm-run").resolve().relative_to(Path("${ROOT}").resolve())),
)
for path in (Path("${out_static}"), Path("${out_showcase}")):
    path.write_text(text)
    print(f"wrote {path}")
PY
done

python3 - <<PY
from pathlib import Path
from analysis.compare_static_baseline import build_summary

root = Path("${ROOT}")
static = Path("${STATIC_SWEEP}")
showcase = Path("${SHOWCASE}")
pairs = [
    (220, static / "run-1/experiment.json", showcase / "compare-up-sweep-20260525-231308/run-2/llm-run/cost-effective-boundary.json", ""),
    (240, static / "run-2/experiment.json", showcase / "compare-up-sweep-20260525-231308/run-3/llm-run/cost-effective-boundary.json", ""),
    (260, static / "run-3/experiment.json", showcase / "compare-up-sweep-20260525-231308/run-4/llm-run/cost-effective-boundary.json", ""),
    (280, static / "run-4/experiment.json", showcase / "compare-up-sweep-20260525-010051/run-1/llm-run/cost-effective-boundary.json", "010051 sweep"),
]
summary = build_summary(
    pairs,
    static_sweep_root=static.resolve().relative_to(root.resolve()),
    llm_sweep_primary="showcase_UP/compare-up-sweep-20260525-231308",
)
out = showcase / "static-vs-llm-up-summary.md"
out.write_text(summary)
print(f"wrote {out}")
PY

echo "done"
