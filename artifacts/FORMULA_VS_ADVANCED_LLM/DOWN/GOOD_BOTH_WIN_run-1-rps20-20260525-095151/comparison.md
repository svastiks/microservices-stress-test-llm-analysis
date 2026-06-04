# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **formula**: `optimizer=formula` · `stopped_reason=first_fail` · iterations=16 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-15` · prov_cost_total=104.073608 (steady=103.968, best_pass=0.1444), util_cost_total=86.752843 (steady=86.688, best_pass=0.1204)
- **llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=9 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-8` · prov_cost_total=27.411785 (steady=27.36, best_pass=0.038), util_cost_total=18.594152 (steady=18.576, best_pass=0.0258)

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | -100.0 | -43.0 |
| llm | -140.0 | -70.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula prov cost | formula util cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | llm prov cost | llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1995 | 6 | 0 | 20 | 28.9 | 12.1 | 150 | 75 | 300 | 150 | 5 | PASS | 0.7116 | 0.1668 | 6 | 0 | 20 | 23.8 | 16.8 | 150 | 75 | 300 | 150 | 5 |
| 2 | PASS | 0.5503 | 0.2256 | 6 | 0 | 20 | 42.1 | 20.7 | 116 | 58 | 231 | 116 | 5 | PASS | 0.4744 | 0.1507 | 6 | 0 | 20 | 32.5 | 18.2 | 100 | 50 | 300 | 150 | 5 |
| 3 | PASS | 0.4554 | 0.2378 | 6 | 0 | 20 | 53.7 | 24.9 | 96 | 48 | 191 | 96 | 5 | PASS | 0.3036 | 0.1247 | 6 | 0 | 20 | 42.2 | 20.1 | 80 | 40 | 300 | 150 | 4 |
| 4 | PASS | 0.3985 | 0.198 | 6 | 0 | 20 | 50.8 | 29.1 | 84 | 42 | 167 | 84 | 5 | PASS | 0.1917 | 0.0698 | 6 | 0 | 20 | 37.4 | 21.1 | 50 | 30 | 300 | 150 | 4 |
| 5 | PASS | 0.2773 | 0.2068 | 7 | 0 | 20 | 76.7 | 36.4 | 73 | 37 | 144 | 73 | 4 | PASS | 0.1718 | 0.0627 | 6 | 0 | 20 | 37.4 | 22 | 45 | 25 | 250 | 120 | 4 |
| 6 | PASS | 0.2661 | 0.2046 | 25 | 0 | 20 | 79 | 39.5 | 70 | 36 | 137 | 70 | 4 | PASS | 0.1139 | 0.0674 | 6 | 0 | 20 | 60.8 | 29.5 | 40 | 20 | 200 | 100 | 3 |
| 7 | PASS | 0.1912 | 0.1611 | 23 | 0 | 20 | 86.6 | 43.3 | 67 | 35 | 131 | 67 | 3 | PASS | 0.0569 | 0.0488 | 6 | 0 | 20 | 88.4 | 35.2 | 30 | 15 | 200 | 100 | 2 |
| 8 | PASS | 0.1828 | 0.1629 | 36 | 0 | 20 | 91.6 | 46.8 | 64 | 34 | 125 | 64 | 3 | PASS | 0.038 | 0.0258 | 7 | 0 | 20 | 70.2 | 26.5 | 20 | 10 | 200 | 100 | 2 |
| 9 | PASS | 0.1744 | 0.1558 | 86 | 0 | 20 | 92.3 | 38.8 | 61 | 33 | 119 | 61 | 3 | FAIL | 0.0095 | 0.0094 | 177 | 0 | 20 | 165.3 | 89.9 | 10 | 5 | 120 | 60 | 1 |
| 10 | PASS | 0.166 | 0.1289 | 68 | 0 | 20 | 79.3 | 50.2 | 58 | 32 | 114 | 58 | 3 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 11 | PASS | 0.1606 | 0.1296 | 85 | 0 | 20 | 83.1 | 42 | 56 | 32 | 109 | 56 | 3 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 12 | PASS | 0.1552 | 0.1218 | 73 | 0 | 20 | 80 | 54.6 | 54 | 32 | 104 | 54 | 3 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 13 | PASS | 0.1498 | 0.128 | 132 | 0 | 20 | 88.1 | 45.7 | 52 | 32 | 99 | 52 | 3 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 14 | PASS | 0.1444 | 0.1184 | 95 | 0 | 20 | 83.6 | 58.9 | 50 | 32 | 95 | 50 | 3 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 15 | PASS | 0.1444 | 0.1204 | 93 | 0 | 20 | 85.1 | 58.9 | 50 | 32 | 95 | 50 | 3 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 16 | FAIL | 0.0963 | 0.0945 | 241 | 0 | 20 | 148.4 | 72.3 | 50 | 32 | 80 | 42 | 2 | — | — | — | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: formula=16, llm=9.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | formula status | formula prov cost | formula util cost | llm status | llm prov cost | llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1995 | PASS | 0.7116 | 0.1668 |
| 2 | PASS | 0.5503 | 0.2256 | PASS | 0.4744 | 0.1507 |
| 3 | PASS | 0.4554 | 0.2378 | PASS | 0.3036 | 0.1247 |
| 4 | PASS | 0.3985 | 0.198 | PASS | 0.1917 | 0.0698 |
| 5 | PASS | 0.2773 | 0.2068 | PASS | 0.1718 | 0.0627 |
| 6 | PASS | 0.2661 | 0.2046 | PASS | 0.1139 | 0.0674 |
| 7 | PASS | 0.1912 | 0.1611 | PASS | 0.0569 | 0.0488 |
| 8 | PASS | 0.1828 | 0.1629 | PASS | 0.038 | 0.0258 |
| 9 | PASS | 0.1744 | 0.1558 | FAIL | 0.0095 | 0.0094 |
| 10 | PASS | 0.166 | 0.1289 | — | — | — |
| 11 | PASS | 0.1606 | 0.1296 | — | — | — |
| 12 | PASS | 0.1552 | 0.1218 | — | — | — |
| 13 | PASS | 0.1498 | 0.128 | — | — | — |
| 14 | PASS | 0.1444 | 0.1184 | — | — | — |
| 15 | PASS | 0.1444 | 0.1204 | — | — | — |
| 16 | FAIL | 0.0963 | 0.0945 | — | — | — |
