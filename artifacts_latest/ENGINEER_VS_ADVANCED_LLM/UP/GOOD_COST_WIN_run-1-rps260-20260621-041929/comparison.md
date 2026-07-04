# Engineer baseline vs advanced LLM squeeze comparison

- **Target RPS**: 260 (`up_demo`)
- **Engineer**: Autopilot single-shot sizing from profiling metrics; one k6 verify pass at fixed RPS; no squeeze loop.
- **Advanced LLM**: iterative squeeze with full telemetry + guards (`cost-effective-boundary.json`).
- **Static data**: `artifacts_latest/FORMULA_VS_ADVANCED_LLM/UP/GOOD_COST_WIN_run-1-rps260-20260609-204250/llm-run/engineer-baseline/verify-run`
- **LLM data**: `artifacts_latest/FORMULA_VS_ADVANCED_LLM/UP/GOOD_COST_WIN_run-1-rps260-20260609-204250/llm-run`

---

- **Advanced source**: llm-run under vanilla/formula archives

- **Engineer source**: verified: Autopilot-derived YAML + cluster k6
## Details (squeeze-style table)

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **engineer**: `optimizer=static_baseline` · `stopped_reason=single_pass_no_apply_loop` · iterations=1 · `best_pass_dir=None`
- **advanced-llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=11 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-11` · prov_cost_total=202.007413 (steady=201.96, best_pass=0.2805), util_cost_total=118.976448 (steady=118.944, best_pass=0.1652)

## Resource delta (first row → last row)

| | 🟩 CPU req (m) | 🟧 Mem req (MiB) |
|---|---:|---:|
| engineer | +0.0 | +0.0 |
| advanced-llm | +95.0 | +75.0 |

## Combined iterations

One row per iteration index (boundary `rows` order). Rows are **not** matched configs — each arm ran an independent squeeze trajectory. When `paired-baseline-probe.md` exists under each arm, **row 1** shares the same observed burn/cpu% (one k6 window, two optimizer analyses).

| # | engineer status | ⬜ engineer prov cost | ⬜ engineer util cost | engineer p95 | engineer err | engineer ach RPS | engineer cpu% req | engineer mem% | 🟩 engineer cpu m | 🟧 engineer mem Mi | engineer cpu lim | engineer mem lim | engineer repl | advanced-llm status | ⬜ advanced-llm prov cost | ⬜ advanced-llm util cost | advanced-llm p95 | advanced-llm err | advanced-llm ach RPS | advanced-llm cpu% req | advanced-llm mem% | 🟩 advanced-llm cpu m | 🟧 advanced-llm mem Mi | advanced-llm cpu lim | advanced-llm mem lim | advanced-llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.4954 | 0.2221 | 512 | 0 | 258.6 | 45.3 | 20.3 | 180 | 32 | 360 | 64 | 3 | FAIL | 0.0474 | 0.0442 | 4731 | 0 | 250.4 | 186.1 | 95.2 | 50 | 25 | 100 | 50 | 1 |
| 2 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.0949 | 0.0879 | 811 | 0 | 260 | 189.5 | 53.8 | 50 | 25 | 100 | 50 | 2 |
| 3 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.1101 | 0.1024 | 864 | 0 | 260 | 190.2 | 41 | 58 | 29 | 115 | 58 | 2 |
| 4 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.1272 | 0.1049 | 535 | 0 | 260 | 174.2 | 25.6 | 66 | 43 | 133 | 86 | 2 |
| 5 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.1541 | 0.1108 | 379 | 0 | 260 | 140.6 | 21.7 | 79 | 61 | 146 | 103 | 2 |
| 6 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.1775 | 0.1231 | 361 | 0 | 260 | 136.1 | 17.5 | 91 | 70 | 168 | 118 | 2 |
| 7 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.2046 | 0.128 | 480 | 0 | 260 | 123.1 | 13.8 | 105 | 80 | 194 | 136 | 2 |
| 8 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.219 | 0.1384 | 461 | 0 | 260 | 115 | 13.8 | 113 | 80 | 194 | 136 | 2 |
| 9 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.2334 | 0.1384 | 428 | 0 | 260 | 100.2 | 14.8 | 121 | 80 | 194 | 136 | 2 |
| 10 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.2478 | 0.1546 | 516 | 0 | 260 | 98.6 | 14.6 | 129 | 80 | 194 | 136 | 2 |
| 11 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.2805 | 0.1652 | 407 | 0 | 260 | 88.3 | 12.2 | 145 | 100 | 205 | 154 | 2 |

*Iteration count mismatch: engineer=1, advanced-llm=11.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | engineer status | ⬜ engineer prov cost | ⬜ engineer util cost | advanced-llm status | ⬜ advanced-llm prov cost | ⬜ advanced-llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.4954 | 0.2221 | FAIL | 0.0474 | 0.0442 |
| 2 | — | — | — | FAIL | 0.0949 | 0.0879 |
| 3 | — | — | — | FAIL | 0.1101 | 0.1024 |
| 4 | — | — | — | FAIL | 0.1272 | 0.1049 |
| 5 | — | — | — | FAIL | 0.1541 | 0.1108 |
| 6 | — | — | — | FAIL | 0.1775 | 0.1231 |
| 7 | — | — | — | FAIL | 0.2046 | 0.128 |
| 8 | — | — | — | FAIL | 0.219 | 0.1384 |
| 9 | — | — | — | FAIL | 0.2334 | 0.1384 |
| 10 | — | — | — | FAIL | 0.2478 | 0.1546 |
| 11 | — | — | — | PASS | 0.2805 | 0.1652 |
