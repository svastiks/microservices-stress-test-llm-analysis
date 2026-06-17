# Engineer baseline vs advanced LLM squeeze comparison

- **Target RPS**: 260 (`up_demo`)
- **Engineer**: Autopilot single-shot sizing from profiling metrics; one k6 verify pass at fixed RPS; no squeeze loop.
- **Advanced LLM**: iterative squeeze with full telemetry + guards (`cost-effective-boundary.json`).
- **Static data**: `artifacts_latest/VANILLA_LLM_VS_ADVANCED_LLM/UP/GOOD_COST_WIN_run-1-rps260-20260610-121406/advanced-llm-run/iteration-1/engineer-baseline/verify-run`
- **LLM data**: `artifacts_latest/VANILLA_LLM_VS_ADVANCED_LLM/UP/GOOD_COST_WIN_run-1-rps260-20260610-121406/advanced-llm-run`

---

- **Engineer source**: verified: Autopilot-derived YAML + cluster k6
## Details (squeeze-style table)

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **engineer**: `optimizer=static_baseline` · `stopped_reason=single_pass_no_apply_loop` · iterations=1 · `best_pass_dir=/Users/svastik/Documents/Svastik/github/microservices-stress-test-llm-analysis/artifacts_latest/VANILLA_LLM_VS_ADVANCED_LLM/UP/GOOD_COST_WIN_run-1-rps260-20260610-121406/advanced-llm-run/iteration-1/engineer-baseline/verify-run` · best_pass_prov_cost=0.121, best_pass_util_cost=0.0922
- **advanced-llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=10 · `best_pass_dir=/app/results/squeeze-compare-advanced-llm/run-1/iteration-10` · prov_cost_total=186.44732 (steady=186.408, best_pass=0.2589), util_cost_total=85.633375 (steady=85.608, best_pass=0.1189)

## Resource delta (first row → last row)

| | 🟩 CPU req (m) | 🟧 Mem req (MiB) |
|---|---:|---:|
| engineer | +0.0 | +0.0 |
| advanced-llm | +86.0 | +47.0 |

## Combined iterations

One row per iteration index (boundary `rows` order). Rows are **not** matched configs — each arm ran an independent squeeze trajectory. When `paired-baseline-probe.md` exists under each arm, **row 1** shares the same observed burn/cpu% (one k6 window, two optimizer analyses).

| # | engineer status | ⬜ engineer prov cost | ⬜ engineer util cost | engineer p95 | engineer err | engineer ach RPS | engineer cpu% req | engineer mem% | 🟩 engineer cpu m | 🟧 engineer mem Mi | engineer cpu lim | engineer mem lim | engineer repl | advanced-llm status | ⬜ advanced-llm prov cost | ⬜ advanced-llm util cost | advanced-llm p95 | advanced-llm err | advanced-llm ach RPS | advanced-llm cpu% req | advanced-llm mem% | 🟩 advanced-llm cpu m | 🟧 advanced-llm mem Mi | advanced-llm cpu lim | advanced-llm mem lim | advanced-llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.121 | 0.0922 | 416 | 0 | 260 | 78.1 | 38.9 | 128 | 59 | 256 | 118 | 1 | FAIL | 0.0474 | 0.0425 | 4138 | 0 | 254.4 | 178.8 | 93.7 | 50 | 25 | 100 | 50 | 1 |
| 2 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.0949 | 0.0868 | 676 | 0 | 260 | 187.4 | 51.2 | 50 | 25 | 100 | 50 | 2 |
| 3 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.1101 | 0.0968 | 453 | 0 | 260 | 179.5 | 41.8 | 58 | 29 | 115 | 57 | 2 |
| 4 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.1272 | 0.1042 | 611 | 0 | 260 | 166.5 | 34.2 | 67 | 34 | 132 | 66 | 2 |
| 5 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.1416 | 0.1093 | 424 | 0 | 260 | 159.9 | 31.9 | 75 | 34 | 151 | 66 | 2 |
| 6 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.1624 | 0.1107 | 410 | 0 | 260 | 141.2 | 26.4 | 86 | 39 | 173 | 76 | 2 |
| 7 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.187 | 0.116 | 1073 | 0 | 259.9 | 128.7 | 22.3 | 99 | 45 | 199 | 88 | 2 |
| 8 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.2116 | 0.1134 | 645 | 0 | 260 | 112.5 | 18.9 | 112 | 51 | 228 | 102 | 2 |
| 9 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.2317 | 0.1164 | 512 | 0 | 260 | 105 | 16.2 | 122 | 62 | 246 | 118 | 2 |
| 10 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.2589 | 0.1189 | 415 | 0 | 260 | 91.7 | 13.6 | 136 | 72 | 261 | 138 | 2 |

*Iteration count mismatch: engineer=1, advanced-llm=10.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | engineer status | ⬜ engineer prov cost | ⬜ engineer util cost | advanced-llm status | ⬜ advanced-llm prov cost | ⬜ advanced-llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.121 | 0.0922 | FAIL | 0.0474 | 0.0425 |
| 2 | — | — | — | FAIL | 0.0949 | 0.0868 |
| 3 | — | — | — | FAIL | 0.1101 | 0.0968 |
| 4 | — | — | — | FAIL | 0.1272 | 0.1042 |
| 5 | — | — | — | FAIL | 0.1416 | 0.1093 |
| 6 | — | — | — | FAIL | 0.1624 | 0.1107 |
| 7 | — | — | — | FAIL | 0.187 | 0.116 |
| 8 | — | — | — | FAIL | 0.2116 | 0.1134 |
| 9 | — | — | — | FAIL | 0.2317 | 0.1164 |
| 10 | — | — | — | PASS | 0.2589 | 0.1189 |
