# Engineer baseline vs advanced LLM squeeze comparison

- **Target RPS**: 25 (`down_demo`)
- **Engineer**: Autopilot single-shot sizing from profiling metrics; one k6 verify pass at fixed RPS; no squeeze loop.
- **Advanced LLM**: iterative squeeze with full telemetry + guards (`cost-effective-boundary.json`).
- **Static data**: `artifacts_latest/VANILLA_LLM_VS_ADVANCED_LLM/DOWN/GOOD_COST_WIN_run-1-rps25-20260610-101852/advanced-llm-run/iteration-1/engineer-baseline/verify-run`
- **LLM data**: `artifacts_latest/VANILLA_LLM_VS_ADVANCED_LLM/DOWN/GOOD_COST_WIN_run-1-rps25-20260610-101852/advanced-llm-run`

---

- **Advanced source**: advanced-llm-run under vanilla/formula archives

- **Engineer source**: verified: Autopilot-derived YAML + cluster k6
## Details (squeeze-style table)

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **engineer**: `optimizer=static_baseline` · `stopped_reason=single_pass_no_apply_loop` · iterations=1 · `best_pass_dir=/Users/svastik/Documents/Svastik/github/microservices-stress-test-llm-analysis/artifacts_latest/VANILLA_LLM_VS_ADVANCED_LLM/DOWN/GOOD_COST_WIN_run-1-rps25-20260610-101852/advanced-llm-run/iteration-1/engineer-baseline/verify-run` · best_pass_prov_cost=0.6785, best_pass_util_cost=0.2471
- **advanced-llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=6 · `best_pass_dir=/app/results/squeeze-compare-advanced-llm/run-1/iteration-5` · prov_cost_total=120.002428 (steady=119.952, best_pass=0.1666), util_cost_total=53.65744 (steady=53.64, best_pass=0.0745)

## Resource delta (first row → last row)

| | 🟩 CPU req (m) | 🟧 Mem req (MiB) |
|---|---:|---:|
| engineer | +0.0 | +0.0 |
| advanced-llm | -75.0 | -39.0 |

## Combined iterations

One row per iteration index (boundary `rows` order). Rows are **not** matched configs — each arm ran an independent squeeze trajectory. When `paired-baseline-probe.md` exists under each arm, **row 1** shares the same observed burn/cpu% (one k6 window, two optimizer analyses).

| # | engineer status | ⬜ engineer prov cost | ⬜ engineer util cost | engineer p95 | engineer err | engineer ach RPS | engineer cpu% req | engineer mem% | 🟩 engineer cpu m | 🟧 engineer mem Mi | engineer cpu lim | engineer mem lim | engineer repl | advanced-llm status | ⬜ advanced-llm prov cost | ⬜ advanced-llm util cost | advanced-llm p95 | advanced-llm err | advanced-llm ach RPS | advanced-llm cpu% req | advanced-llm mem% | 🟩 advanced-llm cpu m | 🟧 advanced-llm mem Mi | advanced-llm cpu lim | advanced-llm mem lim | advanced-llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.6785 | 0.2471 | 6 | 0 | 25 | 36.5 | 32.4 | 185 | 32 | 370 | 64 | 4 | PASS | 0.7116 | 0.1719 | 74 | 0 | 25 | 49.8 | 10.5 | 150 | 75 | 300 | 150 | 5 |
| 2 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.4858 | 0.1744 | 74 | 0 | 25 | 73.4 | 19.5 | 128 | 64 | 255 | 127 | 4 |
| 3 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.3215 | 0.1208 | 74 | 0 | 25 | 72.5 | 20.1 | 113 | 56 | 213 | 106 | 3 |
| 4 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.1896 | 0.0775 | 74 | 0 | 25 | 75.9 | 15.9 | 100 | 49 | 180 | 92 | 2 |
| 5 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.1666 | 0.0745 | 74 | 0 | 25 | 81.2 | 18.5 | 88 | 42 | 155 | 78 | 2 |
| 6 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.142 | 0.0785 | 74 | 0 | 25 | 100.3 | 22 | 75 | 36 | 132 | 66 | 2 |

*Iteration count mismatch: engineer=1, advanced-llm=6.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | engineer status | ⬜ engineer prov cost | ⬜ engineer util cost | advanced-llm status | ⬜ advanced-llm prov cost | ⬜ advanced-llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.6785 | 0.2471 | PASS | 0.7116 | 0.1719 |
| 2 | — | — | — | PASS | 0.4858 | 0.1744 |
| 3 | — | — | — | PASS | 0.3215 | 0.1208 |
| 4 | — | — | — | PASS | 0.1896 | 0.0775 |
| 5 | — | — | — | PASS | 0.1666 | 0.0745 |
| 6 | — | — | — | FAIL | 0.142 | 0.0785 |
