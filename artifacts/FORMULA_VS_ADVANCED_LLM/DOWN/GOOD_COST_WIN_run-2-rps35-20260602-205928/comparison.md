# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **formula**: `optimizer=formula` · `stopped_reason=first_fail` · iterations=10 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-9` · prov_cost_total=78.48507 (steady=78.408, best_pass=0.1089), util_cost_total=72.038532 (steady=72.0, best_pass=0.1)
- **llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=12 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-11` · prov_cost_total=14.46966 (steady=14.4, best_pass=0.02), util_cost_total=12.41009 (steady=12.384, best_pass=0.0172)

## Resource delta (first row → last row)

| | 🟩 CPU req (m) | 🟧 Mem req (MiB) |
|---|---:|---:|
| formula | -95.0 | -43.0 |
| llm | -135.0 | -60.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | ⬜ formula prov cost | ⬜ formula util cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | 🟩 formula cpu m | 🟧 formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | ⬜ llm prov cost | ⬜ llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | 🟩 llm cpu m | 🟧 llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1473 | 6 | 0 | 35 | 21.2 | 11.5 | 150 | 75 | 300 | 150 | 5 | PASS | 0.7116 | 0.1433 | 6 | 0 | 35 | 20.6 | 11.7 | 150 | 75 | 300 | 150 | 5 |
| 2 | PASS | 0.5268 | 0.2098 | 6 | 0 | 35 | 40.8 | 21.9 | 111 | 56 | 222 | 111 | 5 | PASS | 0.4744 | 0.1447 | 6 | 0 | 35 | 31.4 | 14 | 100 | 50 | 300 | 150 | 5 |
| 3 | PASS | 0.3492 | 0.219 | 6 | 0 | 35 | 64.3 | 33.7 | 92 | 46 | 183 | 92 | 4 | PASS | 0.4744 | 0.1789 | 6 | 0 | 35 | 38.7 | 19.5 | 100 | 50 | 250 | 125 | 5 |
| 4 | PASS | 0.334 | 0.1976 | 6 | 0 | 35 | 60.4 | 36.1 | 88 | 44 | 174 | 88 | 4 | PASS | 0.3152 | 0.1741 | 6 | 0 | 35 | 56.4 | 34.2 | 83 | 42 | 184 | 92 | 4 |
| 5 | PASS | 0.3188 | 0.1623 | 7 | 0 | 35 | 52.4 | 23.3 | 84 | 42 | 166 | 84 | 4 | PASS | 0.2856 | 0.1324 | 6 | 0 | 35 | 47.3 | 29.7 | 75 | 40 | 184 | 92 | 4 |
| 6 | PASS | 0.2773 | 0.1361 | 20 | 0 | 35 | 50.1 | 30.6 | 73 | 37 | 145 | 73 | 4 | PASS | 0.1714 | 0.0889 | 6 | 0 | 35 | 53.3 | 27.2 | 60 | 32 | 184 | 92 | 3 |
| 7 | PASS | 0.1795 | 0.1362 | 47 | 0 | 35 | 78 | 37.9 | 63 | 32 | 125 | 63 | 3 | PASS | 0.1438 | 0.0706 | 6 | 0 | 35 | 50.3 | 31.1 | 50 | 30 | 164 | 80 | 3 |
| 8 | PASS | 0.1714 | 0.131 | 45 | 0 | 35 | 78.4 | 43.1 | 60 | 32 | 119 | 60 | 3 | PASS | 0.0775 | 0.0445 | 6 | 0 | 35 | 59 | 37.3 | 40 | 28 | 164 | 80 | 2 |
| 9 | PASS | 0.1089 | 0.1 | 67 | 0 | 35 | 93.6 | 63.9 | 57 | 32 | 114 | 57 | 2 | PASS | 0.0775 | 0.0284 | 7 | 0 | 35 | 37.4 | 26.1 | 40 | 28 | 164 | 80 | 2 |
| 10 | FAIL | 0.1053 | 0.102 | 17 | 0 | 35 | 98.6 | 70.7 | 55 | 32 | 109 | 55 | 2 | PASS | 0.02 | 0.0064 | 4 | 0 | 35 | 32.8 | 25.7 | 20 | 20 | 151 | 74 | 1 |
| 11 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.02 | 0.0172 | 69 | 0 | 35 | 91.3 | 38.5 | 20 | 20 | 100 | 50 | 1 |
| 12 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.015 | 0.0142 | 109 | 0 | 35 | 122.1 | 47.7 | 15 | 15 | 83 | 42 | 1 |

*Iteration count mismatch: formula=10, llm=12.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | formula status | ⬜ formula prov cost | ⬜ formula util cost | llm status | ⬜ llm prov cost | ⬜ llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1473 | PASS | 0.7116 | 0.1433 |
| 2 | PASS | 0.5268 | 0.2098 | PASS | 0.4744 | 0.1447 |
| 3 | PASS | 0.3492 | 0.219 | PASS | 0.4744 | 0.1789 |
| 4 | PASS | 0.334 | 0.1976 | PASS | 0.3152 | 0.1741 |
| 5 | PASS | 0.3188 | 0.1623 | PASS | 0.2856 | 0.1324 |
| 6 | PASS | 0.2773 | 0.1361 | PASS | 0.1714 | 0.0889 |
| 7 | PASS | 0.1795 | 0.1362 | PASS | 0.1438 | 0.0706 |
| 8 | PASS | 0.1714 | 0.131 | PASS | 0.0775 | 0.0445 |
| 9 | PASS | 0.1089 | 0.1 | PASS | 0.0775 | 0.0284 |
| 10 | FAIL | 0.1053 | 0.102 | PASS | 0.02 | 0.0064 |
| 11 | — | — | — | PASS | 0.02 | 0.0172 |
| 12 | — | — | — | FAIL | 0.015 | 0.0142 |
