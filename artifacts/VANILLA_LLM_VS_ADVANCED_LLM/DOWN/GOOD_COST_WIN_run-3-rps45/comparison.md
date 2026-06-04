# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **advanced-llm**: `optimizer=llm` · `stopped_reason=empty_recommended_diff` · iterations=11 · `best_pass_dir=/app/results/squeeze-compare-advanced-llm/run-1/iteration-11` · prov_cost_total=62.79002 (steady=62.712, best_pass=0.0871), util_cost_total=55.76122 (steady=55.728, best_pass=0.0774)
- **vanilla-llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=6 · `best_pass_dir=/app/results/squeeze-compare-vanilla-llm/run-1/iteration-5` · prov_cost_total=122.31162 (steady=122.256, best_pass=0.1698), util_cost_total=93.403338 (steady=93.384, best_pass=0.1297)

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| advanced-llm | -104.0 | -53.0 |
| vanilla-llm | -70.0 | -40.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | advanced-llm status | advanced-llm prov cost | advanced-llm util cost | advanced-llm p95 | advanced-llm err | advanced-llm ach RPS | advanced-llm cpu% | advanced-llm mem% | advanced-llm cpu m | advanced-llm mem Mi | advanced-llm cpu lim | advanced-llm mem lim | advanced-llm repl | vanilla-llm status | vanilla-llm prov cost | vanilla-llm util cost | vanilla-llm p95 | vanilla-llm err | vanilla-llm ach RPS | vanilla-llm cpu% | vanilla-llm mem% | vanilla-llm cpu m | vanilla-llm mem Mi | vanilla-llm cpu lim | vanilla-llm mem lim | vanilla-llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1013 | 6 | 0 | 45 | 14.5 | 9.3 | 150 | 75 | 300 | 150 | 5 | PASS | 0.7116 | 0.1276 | 6 | 0 | 45 | 18.4 | 9.3 | 150 | 75 | 300 | 150 | 5 |
| 2 | PASS | 0.5114 | 0.1449 | 6 | 0 | 45 | 29.1 | 13.5 | 135 | 65 | 270 | 130 | 4 | PASS | 0.5693 | 0.1448 | 6 | 0 | 45 | 26.2 | 11.5 | 120 | 60 | 240 | 120 | 5 |
| 3 | PASS | 0.4535 | 0.1557 | 6 | 0 | 45 | 35.1 | 19.1 | 120 | 55 | 240 | 115 | 4 | PASS | 0.4155 | 0.1488 | 6 | 0 | 45 | 36.5 | 21.9 | 110 | 50 | 220 | 100 | 4 |
| 4 | PASS | 0.4155 | 0.1631 | 5 | 0 | 45 | 39.9 | 25.9 | 110 | 50 | 210 | 100 | 4 | PASS | 0.2832 | 0.148 | 5 | 0 | 45 | 52.9 | 39.2 | 100 | 45 | 200 | 90 | 3 |
| 5 | PASS | 0.2832 | 0.1566 | 6 | 0 | 45 | 56 | 41 | 100 | 45 | 190 | 85 | 3 | PASS | 0.1698 | 0.1297 | 5 | 0 | 45 | 77.9 | 44.2 | 90 | 40 | 180 | 80 | 2 |
| 6 | PASS | 0.1698 | 0.1457 | 5 | 0 | 45 | 87.2 | 57.2 | 90 | 40 | 170 | 75 | 2 | FAIL | 0.0754 | 0.0746 | 6 | 0 | 45 | 140.4 | 76.9 | 80 | 35 | 160 | 70 | 1 |
| 7 | PASS | 0.1508 | 0.1278 | 5 | 0 | 45 | 85.4 | 70.4 | 80 | 35 | 155 | 65 | 2 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 8 | PASS | 0.1283 | 0.096 | 5 | 0 | 45 | 76.4 | 41.9 | 68 | 30 | 155 | 65 | 2 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 9 | PASS | 0.1129 | 0.0826 | 5 | 0 | 45 | 75.1 | 30.4 | 60 | 25 | 140 | 60 | 2 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 10 | PASS | 0.0967 | 0.0777 | 16 | 0 | 45 | 83 | 30.4 | 51 | 25 | 126 | 60 | 2 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 11 | PASS | 0.0871 | 0.0774 | 33 | 0 | 45 | 91.7 | 33.9 | 46 | 22 | 113 | 55 | 2 | — | — | — | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: advanced-llm=11, vanilla-llm=6.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | advanced-llm status | advanced-llm prov cost | advanced-llm util cost | vanilla-llm status | vanilla-llm prov cost | vanilla-llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1013 | PASS | 0.7116 | 0.1276 |
| 2 | PASS | 0.5114 | 0.1449 | PASS | 0.5693 | 0.1448 |
| 3 | PASS | 0.4535 | 0.1557 | PASS | 0.4155 | 0.1488 |
| 4 | PASS | 0.4155 | 0.1631 | PASS | 0.2832 | 0.148 |
| 5 | PASS | 0.2832 | 0.1566 | PASS | 0.1698 | 0.1297 |
| 6 | PASS | 0.1698 | 0.1457 | FAIL | 0.0754 | 0.0746 |
| 7 | PASS | 0.1508 | 0.1278 | — | — | — |
| 8 | PASS | 0.1283 | 0.096 | — | — | — |
| 9 | PASS | 0.1129 | 0.0826 | — | — | — |
| 10 | PASS | 0.0967 | 0.0777 | — | — | — |
| 11 | PASS | 0.0871 | 0.0774 | — | — | — |
