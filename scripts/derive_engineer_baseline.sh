#!/usr/bin/env bash
# Derive Autopilot-style engineer baseline from one profiling experiment.json.
#
#   ./scripts/derive_engineer_baseline.sh path/to/experiment.json [out-dir]
#
# Uses advanced iter-1 or engineer sweep experiment as input (fat-start profiling pass).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"
export PYTHONPATH="${ROOT}${PYTHONPATH:+:${PYTHONPATH}}"

EXP="${1:?usage: $0 experiment.json [out-dir]}"
OUT="${2:-}"

args=(python3 -m analysis.derive_engineer_baseline "${EXP}" --repo-root "${ROOT}")
if [[ -n "${OUT}" ]]; then
  args+=(-o "${OUT}")
fi
exec "${args[@]}"
