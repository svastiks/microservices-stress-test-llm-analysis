# DOWN advanced-vs-vanilla — checkpoint (2026-06-03)

Resume here after UP 3-round batch. Read this before touching DOWN prompts/guards again.

## Pass bar (smoke @35 RPS, 60s fast profile)

Advanced must **beat vanilla on both**:
- `best_pass` prov cost **lower** than vanilla
- iteration count **≤** vanilla

## Deck / artifacts (Method 3 DOWN)

| Run | Path | Notes |
|-----|------|--------|
| **Best balanced (90s)** | `artifacts/.../DOWN/run-1-rps35-20260603-162229` | Advanced **0.0968** vs vanilla **0.1315**, 10 vs 9 iters — **use for deck** |
| Cost win (60s) | `artifacts/.../DOWN/run-1-rps35-20260603-223736` | Advanced **0.1103** vs vanilla **0.1514**, **10 vs 7 iters** — wins cost, loses speed |
| Speed+cost near-miss | `artifacts/.../DOWN/run-1-rps35-20260603-214147` | Advanced **0.2074** vs vanilla **0.2547**, 7 vs 6 iters |
| Broken vanilla | `artifacts/.../DOWN/run-1-rps35-20260603-143208` | Fence-strip bug — **do not use** |
| Partial runs | `205228`, `201853`, `221054` | also in `results-from-cluster/` |

## Root causes found & fixes already landed

1. **Vanilla fence strip** — `analysis/results.py` `_strip_markdown_yaml_fences`; tests in `tests/test_llm_yaml_fence_strip.py`
2. **Replica veto undoing clamp** — `_llm_replica_down_allowed` + `_llm_over_replicated_replica_required`; fat-start bypasses `resource_phase_gate`
3. **Hot multi-replica** — at live ≥ 3 and util ≥ 55%, replica drop beats CPU trim; consecutive replica OK when hot (`_llm_hot_multi_replica_burst`)
4. **Hot replica enforce** — `_llm_hot_replica_drop_required` (live ≥ 3, util ≥ 65%) + `cap_squeeze_down_replicas_and_hpa` via `_down_cap_experiment()` (sets `scaling_hint=DOWN` — **cap was no-op without this**)
5. **Boundary stop** — `_llm_at_down_boundary_stop` at live ≤ 2, util ≥ **92%** clears YAML (`empty_recommended_diff`)

## What still fails (223736 post-fix)

- Advanced drops to 2 repl by iter 6 ✓
- Then **grinds CPU** at 2 repl iters 7–10 (80m→58m) while util 83–93% — vanilla **FAILs at iter 7**
- Need: at **live=2 and util ≥ ~85%**, stop trimming / return empty YAML (or one bold trim to FAIL), not 3+ resource-only passes

## Next DOWN tweak (when resuming)

1. Lower boundary for 2-repl phase: e.g. `SQUEEZE_LLM_HOT_BOUNDARY_UTIL_PCT=85` when live ≤ 2 **or** block `_veto`/resource nudge after first hot trim at 2 repl
2. Re-smoke: `BUILD_ANALYZER_IMAGE=true KUBE_CONTEXT=monitoring COMPARE_SWEEP_FAST=1 COMPARE_SWEEP_RPS=35 COMPARE_SWEEP_ROUNDS=1 ./scripts/run_down_demo_advanced_vs_vanilla_sweep.sh`
3. If pass → batch: `COMPARE_SWEEP_RPS=25,35,45 COMPARE_SWEEP_ROUNDS=3` same script (`run_down_demo_advanced_vs_vanilla_sweep.sh`)

## Key files touched

- `analysis/prompts.py` — FAT-START, hot-multi-replica, boundary empty YAML
- `analysis/results.py` — guards above, `_finalize_llm_squeeze_down` pure-LLM path
- `tests/test_squeeze_profile_isolation.py`, `tests/test_up_recovery_prompts.py`

## Cluster

- `KUBE_CONTEXT=monitoring`
- `KUBECONFIG=/Users/svastik/Documents/Research/hetzner-svastik-monitoring.yaml`
- Sync recovery: `RESULTS_DEST=results-from-cluster/compare-advanced-vanilla-down-sweep-<stamp> COMPARE_SYNC_MODE=advanced-vanilla COMPARE_SWEEP_ROUND=1 ./scripts/run_cluster_profiles.sh --compare-advanced-vs-vanilla-llm --sync-pvc-only`

## UP status (parallel track)

- Smoke **passed** @240 (`175505`): advanced 0.0949 vs vanilla 0.1139, 2 iters each
- **3-round batch** `compare-advanced-vanilla-up-sweep-20260603-232821`:
  - **Round 1 @220 OK** — advanced 0.0949 vs vanilla 0.1898
  - **Round 2 @240 OK** — advanced 0.1227 vs vanilla 0.1878
  - **Round 3 @260 FAILED** — job `BackoffLimitExceeded`; replica wait timeout (target=5); vanilla arm incomplete. Partial sync in `run-3/`
- **Retry in flight** @260 only (new sweep dir)
