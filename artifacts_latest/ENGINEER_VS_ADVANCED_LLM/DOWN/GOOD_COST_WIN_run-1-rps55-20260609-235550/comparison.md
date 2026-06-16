# Engineer baseline vs advanced LLM squeeze comparison

- **Target RPS**: 55 (`down_demo`)
- **Engineer**: Autopilot single-shot sizing from profiling metrics; one k6 verify pass at fixed RPS; no squeeze loop.
- **Advanced LLM**: iterative squeeze with full telemetry + guards (`cost-effective-boundary.json`).
- **Static data**: `artifacts_latest/FORMULA_VS_ADVANCED_LLM/DOWN/GOOD_COST_WIN_run-1-rps55-20260609-235550/llm-run/iteration-1/engineer-baseline/verify-run`
- **LLM data**: `artifacts_latest/FORMULA_VS_ADVANCED_LLM/DOWN/GOOD_COST_WIN_run-1-rps55-20260609-235550/llm-run`

---

- **Advanced source**: llm-run under vanilla/formula archives

- **Engineer source**: verified: Autopilot-derived YAML + cluster k6
## Details (squeeze-style table)

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **engineer**: `optimizer=static_baseline` · `stopped_reason=single_pass_no_apply_loop` · iterations=1 · `best_pass_dir=/Users/svastik/Documents/Svastik/github/microservices-stress-test-llm-analysis/artifacts_latest/FORMULA_VS_ADVANCED_LLM/DOWN/GOOD_COST_WIN_run-1-rps55-20260609-235550/llm-run/iteration-1/engineer-baseline/verify-run` · best_pass_prov_cost=0.7001, best_pass_util_cost=0.215
- **advanced-llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=6 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-5` · prov_cost_total=203.970907 (steady=203.904, best_pass=0.2832), util_cost_total=90.597508 (steady=90.576, best_pass=0.1258)

## Resource delta (first row → last row)

| | 🟩 CPU req (m) | 🟧 Mem req (MiB) |
|---|---:|---:|
| engineer | +0.0 | +0.0 |
| advanced-llm | -60.0 | -35.0 |

## Combined iterations

One row per iteration index (boundary `rows` order). Rows are **not** matched configs — each arm ran an independent squeeze trajectory. When `paired-baseline-probe.md` exists under each arm, **row 1** shares the same observed burn/cpu% (one k6 window, two optimizer analyses).

| # | engineer status | ⬜ engineer prov cost | ⬜ engineer util cost | engineer p95 | engineer err | engineer ach RPS | engineer cpu% req | engineer mem% | 🟩 engineer cpu m | 🟧 engineer mem Mi | engineer cpu lim | engineer mem lim | engineer repl | advanced-llm status | ⬜ advanced-llm prov cost | ⬜ advanced-llm util cost | advanced-llm p95 | advanced-llm err | advanced-llm ach RPS | advanced-llm cpu% req | advanced-llm mem% | 🟩 advanced-llm cpu m | 🟧 advanced-llm mem Mi | advanced-llm cpu lim | advanced-llm mem lim | advanced-llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7001 | 0.215 | 6 | 0 | 55 | 30.8 | 25.6 | 191 | 32 | 382 | 64 | 4 | PASS | 0.7116 | 0.1776 | 74 | 0 | 55 | 51.2 | 13.2 | 150 | 75 | 300 | 150 | 5 |
| 2 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.6383 | 0.1764 | 74 | 0 | 55 | 56.5 | 16.4 | 135 | 63 | 270 | 127 | 5 |
| 3 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.4579 | 0.1155 | 74 | 0 | 55 | 51.6 | 16 | 121 | 57 | 243 | 111 | 4 |
| 4 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.4155 | 0.1819 | 74 | 0 | 55 | 90.2 | 17.1 | 110 | 50 | 220 | 100 | 4 |
| 5 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.2832 | 0.1258 | 75 | 0 | 55 | 90.8 | 24.5 | 100 | 45 | 200 | 90 | 3 |
| 6 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.1698 | 0.0831 | 75 | 0 | 55 | 100.8 | 18.4 | 90 | 40 | 180 | 81 | 2 |

*Iteration count mismatch: engineer=1, advanced-llm=6.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | engineer status | ⬜ engineer prov cost | ⬜ engineer util cost | advanced-llm status | ⬜ advanced-llm prov cost | ⬜ advanced-llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7001 | 0.215 | PASS | 0.7116 | 0.1776 |
| 2 | — | — | — | PASS | 0.6383 | 0.1764 |
| 3 | — | — | — | PASS | 0.4579 | 0.1155 |
| 4 | — | — | — | PASS | 0.4155 | 0.1819 |
| 5 | — | — | — | PASS | 0.2832 | 0.1258 |
| 6 | — | — | — | FAIL | 0.1698 | 0.0831 |
