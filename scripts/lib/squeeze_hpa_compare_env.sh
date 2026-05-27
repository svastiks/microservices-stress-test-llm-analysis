# Method 2: HPA-only vs vanilla LLM compare (isolated from formula compare).
# shellcheck shell=bash
_hpa_compare_lib_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/lib/squeeze_llm_env.sh
source "${_hpa_compare_lib_dir}/squeeze_llm_env.sh"

apply_hpa_compare_env() {
  apply_llm_squeeze_env
  export COMPARE_SYNC_MODE=hpa
  export SQUEEZE_COMPARE_SUBDIR_HPA="${SQUEEZE_COMPARE_SUBDIR_HPA:-squeeze-compare-hpa}"
  export SQUEEZE_COMPARE_SUBDIR_LLM="${SQUEEZE_COMPARE_SUBDIR_LLM:-squeeze-compare-llm}"
  export SQUEEZE_COMPARE_PRUNE_PRIOR="${SQUEEZE_COMPARE_PRUNE_PRIOR:-1}"
  # Drop stale method-1 formula runs on the PVC so sync cannot bundle formula+llm by mistake.
  export SQUEEZE_COMPARE_PRUNE_STALE_FORMULA="${SQUEEZE_COMPARE_PRUNE_STALE_FORMULA:-1}"
}
