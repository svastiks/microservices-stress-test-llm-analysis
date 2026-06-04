#!/usr/bin/env bash
# Build aggregate/ tables (median, IQR, bootstrap CI, Wilcoxon) for a completed sweep.
#
# Example:
#   ./scripts/aggregate_sweep_campaign.sh results-from-cluster/compare-up-sweep-20260602-092609 \
#     --mode formula_llm --label-a formula --label-b llm
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"
export PYTHONPATH="${ROOT}${PYTHONPATH:+:${PYTHONPATH}}"

SWEEP_ROOT="${1:?sweep_root required}"
shift || true

exec python3 -m analysis.campaign_aggregate "${SWEEP_ROOT}" "$@"
