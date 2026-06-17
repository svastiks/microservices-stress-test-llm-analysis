# Engineer baseline vs advanced LLM squeeze comparison

- **Target RPS**: 220 (`up_demo`)
- **Engineer**: Autopilot single-shot sizing from profiling metrics; one k6 verify pass at fixed RPS; no squeeze loop.
- **Advanced LLM**: iterative squeeze with full telemetry + guards (`cost-effective-boundary.json`).
- **Static data**: `artifacts_latest/FORMULA_VS_ADVANCED_LLM/UP/GOOD_COST_WIN_run-1-rps220-20260609-134951/llm-run/engineer-baseline/verify-run`
- **LLM data**: `artifacts_latest/FORMULA_VS_ADVANCED_LLM/UP/GOOD_COST_WIN_run-1-rps220-20260609-134951/llm-run`

---

- **Advanced source**: llm-run under vanilla/formula archives

- **Engineer source**: verified: Autopilot-derived YAML + cluster k6
## Details (squeeze-style table)

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **engineer**: `optimizer=static_baseline` · `stopped_reason=single_pass_no_apply_loop` · iterations=1 · `best_pass_dir=/Users/svastik/Documents/Svastik/github/microservices-stress-test-llm-analysis/artifacts_latest/FORMULA_VS_ADVANCED_LLM/UP/GOOD_COST_WIN_run-1-rps220-20260609-134951/llm-run/engineer-baseline/verify-run` · best_pass_prov_cost=0.1217, best_pass_util_cost=0.118
- **advanced-llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=10 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-10` · prov_cost_total=179.535743 (steady=179.496, best_pass=0.2493), util_cost_total=23.421255 (steady=23.4, best_pass=0.0325)

## Resource delta (first row → last row)

| | 🟩 CPU req (m) | 🟧 Mem req (MiB) |
|---|---:|---:|
| engineer | +0.0 | +0.0 |
| advanced-llm | +82.0 | +35.0 |

## Combined iterations

One row per iteration index (boundary `rows` order). Rows are **not** matched configs — each arm ran an independent squeeze trajectory. When `paired-baseline-probe.md` exists under each arm, **row 1** shares the same observed burn/cpu% (one k6 window, two optimizer analyses).

| # | engineer status | ⬜ engineer prov cost | ⬜ engineer util cost | engineer p95 | engineer err | engineer ach RPS | engineer cpu% req | engineer mem% | 🟩 engineer cpu m | 🟧 engineer mem Mi | engineer cpu lim | engineer mem lim | engineer repl | advanced-llm status | ⬜ advanced-llm prov cost | ⬜ advanced-llm util cost | advanced-llm p95 | advanced-llm err | advanced-llm ach RPS | advanced-llm cpu% req | advanced-llm mem% | 🟩 advanced-llm cpu m | 🟧 advanced-llm mem Mi | advanced-llm cpu lim | advanced-llm mem lim | advanced-llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.1217 | 0.118 | 234 | 0 | 220 | 138.4 | 35 | 129 | 57 | 258 | 114 | 1 | FAIL | 0.0474 | 0.0425 | 3454 | 0 | 219.7 | 179 | 89.2 | 50 | 25 | 100 | 50 | 1 |
| 2 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.0949 | 0.0842 | 385 | 0 | 220 | 182.1 | 45.8 | 50 | 25 | 100 | 50 | 2 |
| 3 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.1101 | 0.0948 | 282 | 0 | 220 | 176 | 39.1 | 58 | 29 | 115 | 57 | 2 |
| 4 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.1272 | 0.104 | 251 | 0 | 220 | 166.7 | 30.1 | 67 | 34 | 132 | 66 | 2 |
| 5 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.1462 | 0.1096 | 253 | 0 | 220 | 153.5 | 25.5 | 77 | 39 | 152 | 76 | 2 |
| 6 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.1672 | 0.1095 | 257 | 0 | 220 | 134.4 | 20.9 | 88 | 45 | 174 | 87 | 2 |
| 7 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.192 | 0.1076 | 251 | 0 | 220 | 115.2 | 17.6 | 101 | 52 | 200 | 100 | 2 |
| 8 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.2205 | 0.105 | 230 | 0 | 220 | 98 | 15.4 | 116 | 60 | 230 | 115 | 2 |
| 9 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.2349 | 0.0605 | 231 | 0 | 220 | 97.7 | 15.7 | 124 | 60 | 460 | 115 | 2 |
| 10 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.2493 | 0.0325 | 283 | 0 | 220 | 89.8 | 16.2 | 132 | 60 | 920 | 115 | 2 |

*Iteration count mismatch: engineer=1, advanced-llm=10.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | engineer status | ⬜ engineer prov cost | ⬜ engineer util cost | advanced-llm status | ⬜ advanced-llm prov cost | ⬜ advanced-llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.1217 | 0.118 | FAIL | 0.0474 | 0.0425 |
| 2 | — | — | — | FAIL | 0.0949 | 0.0842 |
| 3 | — | — | — | FAIL | 0.1101 | 0.0948 |
| 4 | — | — | — | FAIL | 0.1272 | 0.104 |
| 5 | — | — | — | FAIL | 0.1462 | 0.1096 |
| 6 | — | — | — | FAIL | 0.1672 | 0.1095 |
| 7 | — | — | — | FAIL | 0.192 | 0.1076 |
| 8 | — | — | — | FAIL | 0.2205 | 0.105 |
| 9 | — | — | — | FAIL | 0.2349 | 0.0605 |
| 10 | — | — | — | PASS | 0.2493 | 0.0325 |
