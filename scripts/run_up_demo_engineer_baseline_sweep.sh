#!/usr/bin/env bash
# UP engineer baseline (B1): fat 5×150m/75Mi + HPA, one k6 pass per RPS — no squeeze.
# Compare output to advanced-llm via scripts/build_engineer_vs_advanced_comparisons.sh
#
#   BUILD_ANALYZER_IMAGE=true COMPARE_SWEEP_RPS=220,240,260 ./scripts/run_up_demo_engineer_baseline_sweep.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export ROOT
# shellcheck source=scripts/lib/engineer_baseline_env.sh
source "${ROOT}/scripts/lib/engineer_baseline_env.sh"

export SWEEP_NAME_PREFIX="${SWEEP_NAME_PREFIX:-engineer-up-sweep}"
# Reuse static sweep driver; only baseline YAML differs from thin default.
exec "${ROOT}/scripts/run_up_demo_static_baseline_sweep.sh"
