# Engineer baseline vs advanced LLM squeeze comparison

- **Target RPS**: 25 (`down_demo`)
- **Engineer (B1)**: fat deployment (`robot-shop-web-deployment.baseline.yaml`: 5×150m/75Mi) + HPA; one k6 pass at fixed RPS; no squeeze (`down_demo`).
- **Advanced LLM**: iterative squeeze with full telemetry + guards (`cost-effective-boundary.json`).
- **Static data**: `artifacts/VANILLA_LLM_VS_ADVANCED_LLM/DOWN/GOOD_BOTH_WIN_run-2-rps25/advanced-llm-run/iteration-1`
- **LLM data**: `artifacts/VANILLA_LLM_VS_ADVANCED_LLM/DOWN/GOOD_BOTH_WIN_run-2-rps25/advanced-llm-run`

---

- **Engineer source**: proxy: advanced-llm iteration-1 (fat wired, no squeeze)
## Details (squeeze-style table)

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **engineer**: `optimizer=static_baseline` · `stopped_reason=single_pass_no_apply_loop` · iterations=1 · `best_pass_dir=/Users/svastik/Documents/Svastik/github/microservices-stress-test-llm-analysis/artifacts/VANILLA_LLM_VS_ADVANCED_LLM/DOWN/GOOD_BOTH_WIN_run-2-rps25/advanced-llm-run/iteration-1` · best_pass_prov_cost=0.7116, best_pass_util_cost=0.0985
- **advanced-llm**: `optimizer=llm` · `stopped_reason=empty_recommended_diff` · iterations=7 · `best_pass_dir=/app/results/squeeze-compare-advanced-llm/run-1/iteration-7` · prov_cost_total=108.648698 (steady=108.576, best_pass=0.1508), util_cost_total=93.696693 (steady=93.672, best_pass=0.1301)

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| engineer | +0.0 | +0.0 |
| advanced-llm | -70.0 | -40.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | engineer status | engineer prov cost | engineer util cost | engineer p95 | engineer err | engineer ach RPS | engineer cpu% | engineer mem% | engineer cpu m | engineer mem Mi | engineer cpu lim | engineer mem lim | engineer repl | advanced-llm status | advanced-llm prov cost | advanced-llm util cost | advanced-llm p95 | advanced-llm err | advanced-llm ach RPS | advanced-llm cpu% | advanced-llm mem% | advanced-llm cpu m | advanced-llm mem Mi | advanced-llm cpu lim | advanced-llm mem lim | advanced-llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.0985 | 6 | 0 | 25 | 14.1 | 9.1 | 150 | 75 | 300 | 150 | 5 | PASS | 0.7116 | 0.0985 | 6 | 0 | 25 | 14.1 | 9.1 | 150 | 75 | 300 | 150 | 5 |
| 2 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.6392 | 0.1412 | 6 | 0 | 25 | 22.7 | 10.5 | 135 | 65 | 270 | 130 | 5 |
| 3 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.4583 | 0.1575 | 6 | 0 | 25 | 35.2 | 18.2 | 121 | 58 | 243 | 117 | 4 |
| 4 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.4155 | 0.1574 | 6 | 0 | 25 | 38.5 | 25.4 | 110 | 50 | 220 | 100 | 4 |
| 5 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.2805 | 0.1552 | 6 | 0 | 25 | 56 | 41.5 | 99 | 45 | 198 | 85 | 3 |
| 6 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.252 | 0.1478 | 5 | 0 | 25 | 59.6 | 38.8 | 89 | 40 | 178 | 75 | 3 |
| 7 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.1508 | 0.1301 | 5 | 0 | 25 | 87.4 | 62.8 | 80 | 35 | 160 | 70 | 2 |

*Iteration count mismatch: engineer=1, advanced-llm=7.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | engineer status | engineer prov cost | engineer util cost | advanced-llm status | advanced-llm prov cost | advanced-llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.0985 | PASS | 0.7116 | 0.0985 |
| 2 | — | — | — | PASS | 0.6392 | 0.1412 |
| 3 | — | — | — | PASS | 0.4583 | 0.1575 |
| 4 | — | — | — | PASS | 0.4155 | 0.1574 |
| 5 | — | — | — | PASS | 0.2805 | 0.1552 |
| 6 | — | — | — | PASS | 0.252 | 0.1478 |
| 7 | — | — | — | PASS | 0.1508 | 0.1301 |
