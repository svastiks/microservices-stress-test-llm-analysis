# Engineer baseline vs advanced LLM squeeze comparison

- **Target RPS**: 45 (`down_demo`)
- **Engineer**: Autopilot single-shot sizing from profiling metrics; one k6 verify pass at fixed RPS; no squeeze loop.
- **Advanced LLM**: iterative squeeze with full telemetry + guards (`cost-effective-boundary.json`).
- **Static data**: `artifacts_latest/VANILLA_LLM_VS_ADVANCED_LLM/DOWN/GOOD_COST_WIN_run-1-rps45-20260610-132102/advanced-llm-run/iteration-1/engineer-baseline/verify-run`
- **LLM data**: `artifacts_latest/VANILLA_LLM_VS_ADVANCED_LLM/DOWN/GOOD_COST_WIN_run-1-rps45-20260610-132102/advanced-llm-run`

---

- **Engineer source**: verified: Autopilot-derived YAML + cluster k6
## Details (squeeze-style table)

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **engineer**: `optimizer=static_baseline` · `stopped_reason=single_pass_no_apply_loop` · iterations=1 · `best_pass_dir=/Users/svastik/Documents/Svastik/github/microservices-stress-test-llm-analysis/artifacts_latest/VANILLA_LLM_VS_ADVANCED_LLM/DOWN/GOOD_COST_WIN_run-1-rps45-20260610-132102/advanced-llm-run/iteration-1/engineer-baseline/verify-run` · best_pass_prov_cost=0.6929, best_pass_util_cost=0.1747
- **advanced-llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=6 · `best_pass_dir=/app/results/squeeze-compare-advanced-llm/run-1/iteration-5` · prov_cost_total=125.772925 (steady=125.712, best_pass=0.1746), util_cost_total=58.196775 (steady=58.176, best_pass=0.0808)

## Resource delta (first row → last row)

| | 🟩 CPU req (m) | 🟧 Mem req (MiB) |
|---|---:|---:|
| engineer | +0.0 | +0.0 |
| advanced-llm | -72.0 | -35.0 |

## Combined iterations

One row per iteration index (boundary `rows` order). Rows are **not** matched configs — each arm ran an independent squeeze trajectory. When `paired-baseline-probe.md` exists under each arm, **row 1** shares the same observed burn/cpu% (one k6 window, two optimizer analyses).

| # | engineer status | ⬜ engineer prov cost | ⬜ engineer util cost | engineer p95 | engineer err | engineer ach RPS | engineer cpu% req | engineer mem% | 🟩 engineer cpu m | 🟧 engineer mem Mi | engineer cpu lim | engineer mem lim | engineer repl | advanced-llm status | ⬜ advanced-llm prov cost | ⬜ advanced-llm util cost | advanced-llm p95 | advanced-llm err | advanced-llm ach RPS | advanced-llm cpu% req | advanced-llm mem% | 🟩 advanced-llm cpu m | 🟧 advanced-llm mem Mi | advanced-llm cpu lim | advanced-llm mem lim | advanced-llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.6929 | 0.1747 | 6 | 0 | 45 | 25.2 | 26.2 | 189 | 32 | 378 | 64 | 4 | PASS | 0.7116 | 0.1762 | 74 | 0 | 45 | 51.1 | 11 | 150 | 75 | 300 | 150 | 5 |
| 2 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.6407 | 0.1788 | 74 | 0 | 45 | 57.2 | 15.2 | 135 | 68 | 270 | 135 | 5 |
| 3 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.4554 | 0.1917 | 74 | 0 | 45 | 81.3 | 17.8 | 120 | 60 | 225 | 120 | 4 |
| 4 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.3065 | 0.1274 | 74 | 0 | 45 | 80.1 | 21.4 | 108 | 51 | 203 | 102 | 3 |
| 5 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.1746 | 0.0808 | 75 | 0 | 45 | 90.1 | 16.6 | 92 | 46 | 173 | 90 | 2 |
| 6 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.1482 | 0.0761 | 74 | 0 | 45 | 104.3 | 18.5 | 78 | 40 | 153 | 81 | 2 |

*Iteration count mismatch: engineer=1, advanced-llm=6.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | engineer status | ⬜ engineer prov cost | ⬜ engineer util cost | advanced-llm status | ⬜ advanced-llm prov cost | ⬜ advanced-llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.6929 | 0.1747 | PASS | 0.7116 | 0.1762 |
| 2 | — | — | — | PASS | 0.6407 | 0.1788 |
| 3 | — | — | — | PASS | 0.4554 | 0.1917 |
| 4 | — | — | — | PASS | 0.3065 | 0.1274 |
| 5 | — | — | — | PASS | 0.1746 | 0.0808 |
| 6 | — | — | — | FAIL | 0.1482 | 0.0761 |
