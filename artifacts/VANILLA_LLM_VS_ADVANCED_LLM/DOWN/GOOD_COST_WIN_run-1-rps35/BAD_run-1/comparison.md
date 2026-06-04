# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **advanced-llm**: `optimizer=llm` · `stopped_reason=empty_recommended_diff` · iterations=7 · `best_pass_dir=/app/results/squeeze-compare-advanced-llm/run-1/iteration-7` · prov_cost_total=102.884812 (steady=102.816, best_pass=0.1428), util_cost_total=95.285063 (steady=95.256, best_pass=0.1323)
- **vanilla-llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=6 · `best_pass_dir=/app/results/squeeze-compare-vanilla-llm/run-1/iteration-5` · prov_cost_total=118.852845 (steady=118.8, best_pass=0.165), util_cost_total=101.179315 (steady=101.16, best_pass=0.1405)

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| advanced-llm | -75.0 | -35.0 |
| vanilla-llm | -72.0 | -36.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | advanced-llm status | advanced-llm prov cost | advanced-llm util cost | advanced-llm p95 | advanced-llm err | advanced-llm ach RPS | advanced-llm cpu% | advanced-llm mem% | advanced-llm cpu m | advanced-llm mem Mi | advanced-llm cpu lim | advanced-llm mem lim | advanced-llm repl | vanilla-llm status | vanilla-llm prov cost | vanilla-llm util cost | vanilla-llm p95 | vanilla-llm err | vanilla-llm ach RPS | vanilla-llm cpu% | vanilla-llm mem% | vanilla-llm cpu m | vanilla-llm mem Mi | vanilla-llm cpu lim | vanilla-llm mem lim | vanilla-llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1812 | 6 | 0 | 35 | 26.1 | 13.8 | 150 | 75 | 300 | 150 | 5 | PASS | 0.7116 | 0.1209 | 6 | 0 | 35 | 17.3 | 11.2 | 150 | 75 | 300 | 150 | 5 |
| 2 | PASS | 0.5114 | 0.1926 | 6 | 0 | 35 | 38.8 | 16 | 135 | 65 | 255 | 135 | 4 | PASS | 0.5693 | 0.1413 | 6 | 0 | 35 | 25.4 | 14.2 | 120 | 60 | 240 | 120 | 5 |
| 3 | PASS | 0.4554 | 0.1831 | 6 | 0 | 35 | 41.4 | 18.2 | 120 | 60 | 225 | 120 | 4 | PASS | 0.4099 | 0.1551 | 6 | 0 | 35 | 38.6 | 23.9 | 108 | 54 | 216 | 108 | 4 |
| 4 | PASS | 0.4175 | 0.1684 | 6 | 0 | 35 | 41.2 | 24.6 | 110 | 55 | 195 | 105 | 4 | PASS | 0.184 | 0.1428 | 5 | 0 | 35 | 79 | 51.9 | 97 | 48 | 194 | 97 | 2 |
| 5 | PASS | 0.2711 | 0.1573 | 6 | 0 | 35 | 59.5 | 32.1 | 95 | 50 | 175 | 90 | 3 | PASS | 0.165 | 0.1405 | 5 | 0 | 35 | 87.6 | 39.7 | 87 | 43 | 155 | 87 | 2 |
| 6 | PASS | 0.2427 | 0.1476 | 5 | 0 | 35 | 62.6 | 30 | 85 | 45 | 145 | 80 | 3 | FAIL | 0.074 | 0.072 | 6 | 0 | 35 | 147.6 | 46.8 | 78 | 39 | 139 | 78 | 1 |
| 7 | PASS | 0.1428 | 0.1323 | 5 | 0 | 35 | 95 | 51.8 | 75 | 40 | 130 | 70 | 2 | — | — | — | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: advanced-llm=7, vanilla-llm=6.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | advanced-llm status | advanced-llm prov cost | advanced-llm util cost | vanilla-llm status | vanilla-llm prov cost | vanilla-llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1812 | PASS | 0.7116 | 0.1209 |
| 2 | PASS | 0.5114 | 0.1926 | PASS | 0.5693 | 0.1413 |
| 3 | PASS | 0.4554 | 0.1831 | PASS | 0.4099 | 0.1551 |
| 4 | PASS | 0.4175 | 0.1684 | PASS | 0.184 | 0.1428 |
| 5 | PASS | 0.2711 | 0.1573 | PASS | 0.165 | 0.1405 |
| 6 | PASS | 0.2427 | 0.1476 | FAIL | 0.074 | 0.072 |
| 7 | PASS | 0.1428 | 0.1323 | — | — | — |
