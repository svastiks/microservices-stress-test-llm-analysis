# Engineer baseline vs advanced LLM squeeze comparison

- **Target RPS**: 240 (`up_demo`)
- **Engineer**: Autopilot single-shot sizing from profiling metrics; one k6 verify pass at fixed RPS; no squeeze loop.
- **Advanced LLM**: iterative squeeze with full telemetry + guards (`cost-effective-boundary.json`).
- **Static data**: `artifacts_latest/FORMULA_VS_ADVANCED_LLM/UP/GOOD_COST_WIN_run-1-rps240-20260609-192356/llm-run/iteration-1/engineer-baseline/verify-run`
- **LLM data**: `artifacts_latest/FORMULA_VS_ADVANCED_LLM/UP/GOOD_COST_WIN_run-1-rps240-20260609-192356/llm-run`

---

- **Advanced source**: llm-run under vanilla/formula archives

- **Engineer source**: verified: Autopilot-derived YAML + cluster k6
## Details (squeeze-style table)

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **engineer**: `optimizer=static_baseline` · `stopped_reason=single_pass_no_apply_loop` · iterations=1 · `best_pass_dir=/Users/svastik/Documents/Svastik/github/microservices-stress-test-llm-analysis/artifacts_latest/FORMULA_VS_ADVANCED_LLM/UP/GOOD_COST_WIN_run-1-rps240-20260609-192356/llm-run/iteration-1/engineer-baseline/verify-run` · best_pass_prov_cost=0.1217, best_pass_util_cost=0.1185
- **advanced-llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=11 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-11` · prov_cost_total=175.86861 (steady=175.824, best_pass=0.2442), util_cost_total=78.867978 (steady=78.84, best_pass=0.1095)

## Resource delta (first row → last row)

| | 🟩 CPU req (m) | 🟧 Mem req (MiB) |
|---|---:|---:|
| engineer | +0.0 | +0.0 |
| advanced-llm | +80.0 | +27.0 |

## Combined iterations

One row per iteration index (boundary `rows` order). Rows are **not** matched configs — each arm ran an independent squeeze trajectory. When `paired-baseline-probe.md` exists under each arm, **row 1** shares the same observed burn/cpu% (one k6 window, two optimizer analyses).

| # | engineer status | ⬜ engineer prov cost | ⬜ engineer util cost | engineer p95 | engineer err | engineer ach RPS | engineer cpu% req | engineer mem% | 🟩 engineer cpu m | 🟧 engineer mem Mi | engineer cpu lim | engineer mem lim | engineer repl | advanced-llm status | ⬜ advanced-llm prov cost | ⬜ advanced-llm util cost | advanced-llm p95 | advanced-llm err | advanced-llm ach RPS | advanced-llm cpu% req | advanced-llm mem% | 🟩 advanced-llm cpu m | 🟧 advanced-llm mem Mi | advanced-llm cpu lim | advanced-llm mem lim | advanced-llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.1217 | 0.1185 | 424 | 0 | 240 | 137.7 | 42.7 | 129 | 57 | 258 | 114 | 1 | FAIL | 0.0474 | 0.0458 | 2982 | 0 | 235 | 193.4 | 92.5 | 50 | 25 | 100 | 50 | 1 |
| 2 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.0949 | 0.0869 | 771 | 0 | 240 | 187.5 | 52.8 | 50 | 25 | 100 | 50 | 2 |
| 3 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.1101 | 0.0961 | 399 | 0 | 240 | 178 | 41 | 58 | 29 | 115 | 58 | 2 |
| 4 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.1272 | 0.1058 | 310 | 0 | 240 | 169.4 | 31.9 | 67 | 34 | 132 | 66 | 2 |
| 5 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.1462 | 0.1081 | 347 | 0 | 240 | 151.1 | 27.2 | 77 | 39 | 152 | 76 | 2 |
| 6 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.1672 | 0.1088 | 364 | 0 | 240 | 133.5 | 21.8 | 88 | 45 | 174 | 87 | 2 |
| 7 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.1902 | 0.1077 | 277 | 0 | 240 | 117.6 | 18.7 | 100 | 52 | 200 | 100 | 2 |
| 8 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.2046 | 0.1119 | 393 | 0 | 240 | 113.2 | 18.4 | 108 | 52 | 216 | 100 | 2 |
| 9 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.219 | 0.1125 | 314 | 0 | 240 | 98.7 | 18.3 | 116 | 52 | 216 | 100 | 2 |
| 10 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.2334 | 0.126 | 383 | 0 | 240 | 96.8 | 19.2 | 124 | 52 | 216 | 100 | 2 |
| 11 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.2442 | 0.1095 | 313 | 0 | 240 | 92 | 18.4 | 130 | 52 | 260 | 100 | 2 |

*Iteration count mismatch: engineer=1, advanced-llm=11.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | engineer status | ⬜ engineer prov cost | ⬜ engineer util cost | advanced-llm status | ⬜ advanced-llm prov cost | ⬜ advanced-llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.1217 | 0.1185 | FAIL | 0.0474 | 0.0458 |
| 2 | — | — | — | FAIL | 0.0949 | 0.0869 |
| 3 | — | — | — | FAIL | 0.1101 | 0.0961 |
| 4 | — | — | — | FAIL | 0.1272 | 0.1058 |
| 5 | — | — | — | FAIL | 0.1462 | 0.1081 |
| 6 | — | — | — | FAIL | 0.1672 | 0.1088 |
| 7 | — | — | — | FAIL | 0.1902 | 0.1077 |
| 8 | — | — | — | FAIL | 0.2046 | 0.1119 |
| 9 | — | — | — | FAIL | 0.219 | 0.1125 |
| 10 | — | — | — | FAIL | 0.2334 | 0.126 |
| 11 | — | — | — | PASS | 0.2442 | 0.1095 |
