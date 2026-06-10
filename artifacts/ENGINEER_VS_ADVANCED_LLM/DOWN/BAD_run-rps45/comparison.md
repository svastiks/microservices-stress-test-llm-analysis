# Engineer baseline vs advanced LLM squeeze comparison

- **Target RPS**: 45 (`down_demo`)
- **Engineer (B1)**: fat deployment (`robot-shop-web-deployment.baseline.yaml`: 5×150m/75Mi) + HPA; one k6 pass at fixed RPS; no squeeze (`down_demo`).
- **Advanced LLM**: iterative squeeze with full telemetry + guards (`cost-effective-boundary.json`).
- **Static data**: `artifacts/VANILLA_LLM_VS_ADVANCED_LLM/DOWN/GOOD_COST_WIN_run-3-rps45/advanced-llm-run/iteration-1`
- **LLM data**: `artifacts/VANILLA_LLM_VS_ADVANCED_LLM/DOWN/GOOD_COST_WIN_run-3-rps45/advanced-llm-run`

---

- **Engineer source**: proxy: advanced-llm iteration-1 (fat wired, no squeeze)
## Details (squeeze-style table)

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **engineer**: `optimizer=static_baseline` · `stopped_reason=single_pass_no_apply_loop` · iterations=1 · `best_pass_dir=/Users/svastik/Documents/Svastik/github/microservices-stress-test-llm-analysis/artifacts/VANILLA_LLM_VS_ADVANCED_LLM/DOWN/GOOD_COST_WIN_run-3-rps45/advanced-llm-run/iteration-1` · best_pass_prov_cost=0.7116, best_pass_util_cost=0.1013
- **advanced-llm**: `optimizer=llm` · `stopped_reason=empty_recommended_diff` · iterations=11 · `best_pass_dir=/app/results/squeeze-compare-advanced-llm/run-1/iteration-11` · prov_cost_total=62.79002 (steady=62.712, best_pass=0.0871), util_cost_total=55.76122 (steady=55.728, best_pass=0.0774)

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| engineer | +0.0 | +0.0 |
| advanced-llm | -104.0 | -53.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | engineer status | engineer prov cost | engineer util cost | engineer p95 | engineer err | engineer ach RPS | engineer cpu% | engineer mem% | engineer cpu m | engineer mem Mi | engineer cpu lim | engineer mem lim | engineer repl | advanced-llm status | advanced-llm prov cost | advanced-llm util cost | advanced-llm p95 | advanced-llm err | advanced-llm ach RPS | advanced-llm cpu% | advanced-llm mem% | advanced-llm cpu m | advanced-llm mem Mi | advanced-llm cpu lim | advanced-llm mem lim | advanced-llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1013 | 6 | 0 | 45 | 14.5 | 9.3 | 150 | 75 | 300 | 150 | 5 | PASS | 0.7116 | 0.1013 | 6 | 0 | 45 | 14.5 | 9.3 | 150 | 75 | 300 | 150 | 5 |
| 2 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.5114 | 0.1449 | 6 | 0 | 45 | 29.1 | 13.5 | 135 | 65 | 270 | 130 | 4 |
| 3 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.4535 | 0.1557 | 6 | 0 | 45 | 35.1 | 19.1 | 120 | 55 | 240 | 115 | 4 |
| 4 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.4155 | 0.1631 | 5 | 0 | 45 | 39.9 | 25.9 | 110 | 50 | 210 | 100 | 4 |
| 5 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.2832 | 0.1566 | 6 | 0 | 45 | 56 | 41 | 100 | 45 | 190 | 85 | 3 |
| 6 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.1698 | 0.1457 | 5 | 0 | 45 | 87.2 | 57.2 | 90 | 40 | 170 | 75 | 2 |
| 7 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.1508 | 0.1278 | 5 | 0 | 45 | 85.4 | 70.4 | 80 | 35 | 155 | 65 | 2 |
| 8 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.1283 | 0.096 | 5 | 0 | 45 | 76.4 | 41.9 | 68 | 30 | 155 | 65 | 2 |
| 9 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.1129 | 0.0826 | 5 | 0 | 45 | 75.1 | 30.4 | 60 | 25 | 140 | 60 | 2 |
| 10 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.0967 | 0.0777 | 16 | 0 | 45 | 83 | 30.4 | 51 | 25 | 126 | 60 | 2 |
| 11 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.0871 | 0.0774 | 33 | 0 | 45 | 91.7 | 33.9 | 46 | 22 | 113 | 55 | 2 |

*Iteration count mismatch: engineer=1, advanced-llm=11.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | engineer status | engineer prov cost | engineer util cost | advanced-llm status | advanced-llm prov cost | advanced-llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1013 | PASS | 0.7116 | 0.1013 |
| 2 | — | — | — | PASS | 0.5114 | 0.1449 |
| 3 | — | — | — | PASS | 0.4535 | 0.1557 |
| 4 | — | — | — | PASS | 0.4155 | 0.1631 |
| 5 | — | — | — | PASS | 0.2832 | 0.1566 |
| 6 | — | — | — | PASS | 0.1698 | 0.1457 |
| 7 | — | — | — | PASS | 0.1508 | 0.1278 |
| 8 | — | — | — | PASS | 0.1283 | 0.096 |
| 9 | — | — | — | PASS | 0.1129 | 0.0826 |
| 10 | — | — | — | PASS | 0.0967 | 0.0777 |
| 11 | — | — | — | PASS | 0.0871 | 0.0774 |
