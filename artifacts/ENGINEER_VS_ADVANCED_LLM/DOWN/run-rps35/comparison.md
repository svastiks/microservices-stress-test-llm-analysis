# Engineer baseline vs advanced LLM squeeze comparison

- **Target RPS**: 35 (`down_demo`)
- **Engineer (B1)**: fat deployment (`robot-shop-web-deployment.baseline.yaml`: 5×150m/75Mi) + HPA; one k6 pass at fixed RPS; no squeeze (`down_demo`).
- **Advanced LLM**: iterative squeeze with full telemetry + guards (`cost-effective-boundary.json`).
- **Static data**: `artifacts/VANILLA_LLM_VS_ADVANCED_LLM/DOWN/GOOD_BOTH_WIN_run-1-rps35-20260604-074743/advanced-llm-run/iteration-1`
- **LLM data**: `artifacts/VANILLA_LLM_VS_ADVANCED_LLM/DOWN/GOOD_BOTH_WIN_run-1-rps35-20260604-074743/advanced-llm-run`

---

- **Engineer source**: proxy: advanced-llm iteration-1 (fat wired, no squeeze)
## Details (squeeze-style table)

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **engineer**: `optimizer=static_baseline` · `stopped_reason=single_pass_no_apply_loop` · iterations=1 · `best_pass_dir=/Users/svastik/Documents/Svastik/github/microservices-stress-test-llm-analysis/artifacts/VANILLA_LLM_VS_ADVANCED_LLM/DOWN/GOOD_BOTH_WIN_run-1-rps35-20260604-074743/advanced-llm-run/iteration-1` · best_pass_prov_cost=0.7116, best_pass_util_cost=0.1066
- **advanced-llm**: `optimizer=llm` · `stopped_reason=empty_recommended_diff` · iterations=7 · `best_pass_dir=/app/results/squeeze-compare-advanced-llm/run-1/iteration-7` · prov_cost_total=107.35202 (steady=107.28, best_pass=0.149), util_cost_total=94.777017 (steady=94.752, best_pass=0.1316)

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| engineer | +0.0 | +0.0 |
| advanced-llm | -71.0 | -40.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | engineer status | engineer prov cost | engineer util cost | engineer p95 | engineer err | engineer ach RPS | engineer cpu% | engineer mem% | engineer cpu m | engineer mem Mi | engineer cpu lim | engineer mem lim | engineer repl | advanced-llm status | advanced-llm prov cost | advanced-llm util cost | advanced-llm p95 | advanced-llm err | advanced-llm ach RPS | advanced-llm cpu% | advanced-llm mem% | advanced-llm cpu m | advanced-llm mem Mi | advanced-llm cpu lim | advanced-llm mem lim | advanced-llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1066 | 6 | 0 | 35 | 15.3 | 9.2 | 150 | 75 | 300 | 150 | 5 | PASS | 0.7116 | 0.1066 | 6 | 0 | 35 | 15.3 | 9.2 | 150 | 75 | 300 | 150 | 5 |
| 2 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.6392 | 0.1515 | 6 | 0 | 35 | 24.4 | 10.3 | 135 | 65 | 270 | 135 | 5 |
| 3 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.4571 | 0.1641 | 6 | 0 | 35 | 36.8 | 17.9 | 121 | 55 | 242 | 121 | 4 |
| 4 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.4115 | 0.1615 | 6 | 0 | 35 | 40 | 23.6 | 109 | 49 | 218 | 109 | 4 |
| 5 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.2775 | 0.1507 | 6 | 0 | 35 | 55.2 | 36.1 | 98 | 44 | 195 | 95 | 3 |
| 6 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.2349 | 0.1347 | 5 | 0 | 35 | 58.3 | 37.6 | 83 | 37 | 165 | 80 | 3 |
| 7 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.149 | 0.1316 | 5 | 0 | 35 | 90.2 | 49.4 | 79 | 35 | 148 | 72 | 2 |

*Iteration count mismatch: engineer=1, advanced-llm=7.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | engineer status | engineer prov cost | engineer util cost | advanced-llm status | advanced-llm prov cost | advanced-llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1066 | PASS | 0.7116 | 0.1066 |
| 2 | — | — | — | PASS | 0.6392 | 0.1515 |
| 3 | — | — | — | PASS | 0.4571 | 0.1641 |
| 4 | — | — | — | PASS | 0.4115 | 0.1615 |
| 5 | — | — | — | PASS | 0.2775 | 0.1507 |
| 6 | — | — | — | PASS | 0.2349 | 0.1347 |
| 7 | — | — | — | PASS | 0.149 | 0.1316 |
