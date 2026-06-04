# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **advanced-llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=10 · `best_pass_dir=/app/results/squeeze-compare-advanced-llm/run-1/iteration-9` · prov_cost_total=69.77225 (steady=69.696, best_pass=0.0968), util_cost_total=49.066845 (steady=49.032, best_pass=0.0681)
- **vanilla-llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=9 · `best_pass_dir=/app/results/squeeze-compare-vanilla-llm/run-1/iteration-8` · prov_cost_total=94.755438 (steady=94.68, best_pass=0.1315), util_cost_total=83.767945 (steady=83.736, best_pass=0.1163)

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| advanced-llm | -105.0 | -40.0 |
| vanilla-llm | -90.0 | -50.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | advanced-llm status | advanced-llm prov cost | advanced-llm util cost | advanced-llm p95 | advanced-llm err | advanced-llm ach RPS | advanced-llm cpu% | advanced-llm mem% | advanced-llm cpu m | advanced-llm mem Mi | advanced-llm cpu lim | advanced-llm mem lim | advanced-llm repl | vanilla-llm status | vanilla-llm prov cost | vanilla-llm util cost | vanilla-llm p95 | vanilla-llm err | vanilla-llm ach RPS | vanilla-llm cpu% | vanilla-llm mem% | vanilla-llm cpu m | vanilla-llm mem Mi | vanilla-llm cpu lim | vanilla-llm mem lim | vanilla-llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.2245 | 6 | 0 | 35 | 32.7 | 10.2 | 150 | 75 | 300 | 150 | 5 | PASS | 0.7116 | 0.1398 | 6 | 0 | 35 | 20.2 | 9.3 | 150 | 75 | 300 | 150 | 5 |
| 2 | PASS | 0.5693 | 0.233 | 6 | 0 | 35 | 42.2 | 17.6 | 120 | 60 | 240 | 120 | 5 | PASS | 0.6143 | 0.1959 | 6 | 0 | 35 | 32.9 | 11.8 | 130 | 60 | 240 | 120 | 5 |
| 3 | PASS | 0.4744 | 0.1881 | 6 | 0 | 35 | 40.7 | 20.4 | 100 | 50 | 240 | 120 | 5 | PASS | 0.4515 | 0.1867 | 6 | 0 | 35 | 42.3 | 20.2 | 120 | 50 | 220 | 110 | 4 |
| 4 | PASS | 0.3795 | 0.1714 | 6 | 0 | 35 | 46.2 | 25.9 | 80 | 40 | 200 | 100 | 5 | PASS | 0.3102 | 0.1817 | 6 | 0 | 35 | 59.5 | 37.8 | 110 | 45 | 200 | 100 | 3 |
| 5 | PASS | 0.2657 | 0.1423 | 6 | 0 | 35 | 55.2 | 23.5 | 70 | 35 | 180 | 100 | 4 | PASS | 0.2817 | 0.135 | 6 | 0 | 35 | 49.1 | 20.6 | 100 | 40 | 180 | 90 | 3 |
| 6 | PASS | 0.1804 | 0.1129 | 6 | 0 | 35 | 64.6 | 29.7 | 63 | 35 | 180 | 100 | 3 | PASS | 0.2535 | 0.1032 | 5 | 0 | 35 | 41.8 | 15.4 | 90 | 36 | 160 | 80 | 3 |
| 7 | PASS | 0.1723 | 0.1181 | 6 | 0 | 35 | 70.9 | 31.9 | 60 | 35 | 162 | 100 | 3 | PASS | 0.1503 | 0.1093 | 5 | 0 | 35 | 74.7 | 28.1 | 80 | 32 | 140 | 70 | 2 |
| 8 | PASS | 0.1561 | 0.0942 | 5 | 0 | 35 | 62.9 | 24.5 | 54 | 35 | 162 | 100 | 3 | PASS | 0.1315 | 0.1163 | 21 | 0 | 35 | 90.8 | 35.3 | 70 | 28 | 120 | 56 | 2 |
| 9 | PASS | 0.0968 | 0.0681 | 5 | 0 | 35 | 73.5 | 29.2 | 50 | 35 | 162 | 100 | 2 | FAIL | 0.1129 | 0.1099 | 90 | 0 | 35 | 103.3 | 39.4 | 60 | 25 | 100 | 50 | 2 |
| 10 | FAIL | 0.0439 | 0.0412 | 6 | 0 | 35 | 130.4 | 20.1 | 45 | 35 | 146 | 100 | 1 | — | — | — | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: advanced-llm=10, vanilla-llm=9.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | advanced-llm status | advanced-llm prov cost | advanced-llm util cost | vanilla-llm status | vanilla-llm prov cost | vanilla-llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.2245 | PASS | 0.7116 | 0.1398 |
| 2 | PASS | 0.5693 | 0.233 | PASS | 0.6143 | 0.1959 |
| 3 | PASS | 0.4744 | 0.1881 | PASS | 0.4515 | 0.1867 |
| 4 | PASS | 0.3795 | 0.1714 | PASS | 0.3102 | 0.1817 |
| 5 | PASS | 0.2657 | 0.1423 | PASS | 0.2817 | 0.135 |
| 6 | PASS | 0.1804 | 0.1129 | PASS | 0.2535 | 0.1032 |
| 7 | PASS | 0.1723 | 0.1181 | PASS | 0.1503 | 0.1093 |
| 8 | PASS | 0.1561 | 0.0942 | PASS | 0.1315 | 0.1163 |
| 9 | PASS | 0.0968 | 0.0681 | FAIL | 0.1129 | 0.1099 |
| 10 | FAIL | 0.0439 | 0.0412 | — | — | — |
