# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **formula**: `optimizer=formula` · `stopped_reason=first_fail` · iterations=16 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-15` · prov_cost_total=138.724948 (steady=138.6, best_pass=0.1925), util_cost_total=103.752405 (steady=103.68, best_pass=0.144)
- **llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=9 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-8` · prov_cost_total=119.508565 (steady=119.448, best_pass=0.1659), util_cost_total=88.656965 (steady=88.632, best_pass=0.1231)

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | -100.0 | -43.0 |
| llm | -90.0 | -60.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula prov cost | formula util cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | llm prov cost | llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1687 | 6 | 0 | 35 | 24.2 | 14.5 | 150 | 75 | 300 | 150 | 5 | PASS | 0.7116 | 0.1688 | 7 | 0 | 35 | 24.2 | 14.8 | 150 | 75 | 300 | 150 | 5 |
| 2 | PASS | 0.5363 | 0.2272 | 7 | 0 | 35 | 43.5 | 21.7 | 113 | 57 | 226 | 113 | 5 | PASS | 0.4744 | 0.152 | 6 | 0 | 35 | 32.9 | 16.3 | 100 | 50 | 300 | 150 | 5 |
| 3 | PASS | 0.4464 | 0.2397 | 7 | 0 | 35 | 55.2 | 26.3 | 94 | 48 | 188 | 94 | 5 | PASS | 0.3795 | 0.1595 | 6 | 0 | 35 | 43.2 | 20.4 | 80 | 40 | 240 | 120 | 5 |
| 4 | PASS | 0.3945 | 0.2083 | 7 | 0 | 35 | 53.9 | 33.2 | 83 | 43 | 166 | 83 | 5 | PASS | 0.2277 | 0.1038 | 6 | 0 | 35 | 46.6 | 27 | 60 | 30 | 240 | 120 | 4 |
| 5 | PASS | 0.3471 | 0.2145 | 27 | 0 | 35 | 63.4 | 33.8 | 73 | 38 | 146 | 73 | 5 | PASS | 0.1898 | 0.0841 | 6 | 0 | 35 | 45.3 | 26.5 | 50 | 25 | 200 | 100 | 4 |
| 6 | PASS | 0.3331 | 0.2133 | 41 | 0 | 35 | 65.7 | 35.2 | 70 | 37 | 139 | 70 | 5 | PASS | 0.1423 | 0.0864 | 6 | 0 | 35 | 62.4 | 29.6 | 50 | 25 | 200 | 100 | 3 |
| 7 | PASS | 0.3191 | 0.1933 | 47 | 0 | 35 | 62.2 | 32.9 | 67 | 36 | 133 | 67 | 5 | PASS | 0.0759 | 0.0661 | 6 | 0 | 35 | 90.3 | 27.3 | 40 | 20 | 200 | 100 | 2 |
| 8 | PASS | 0.3051 | 0.1882 | 63 | 0 | 35 | 63.1 | 37.9 | 64 | 35 | 127 | 64 | 5 | PASS | 0.1659 | 0.1231 | 6 | 0 | 35 | 75.1 | 35.8 | 90 | 20 | 200 | 100 | 2 |
| 9 | PASS | 0.2329 | 0.1819 | 70 | 0 | 35 | 80.1 | 45.1 | 61 | 34 | 121 | 61 | 4 | FAIL | 0.0555 | 0.0548 | 6 | 0 | 35 | 134.2 | 54.5 | 60 | 15 | 200 | 100 | 1 |
| 10 | PASS | 0.2217 | 0.185 | 66 | 0 | 35 | 85.6 | 48.4 | 58 | 33 | 115 | 58 | 4 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 11 | PASS | 0.2141 | 0.1541 | 93 | 0 | 35 | 73.6 | 45.9 | 56 | 32 | 110 | 56 | 4 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 12 | PASS | 0.2069 | 0.1477 | 88 | 0 | 35 | 73.3 | 41.9 | 54 | 32 | 105 | 54 | 4 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 13 | PASS | 0.1997 | 0.1461 | 98 | 0 | 35 | 75.1 | 43.8 | 52 | 32 | 100 | 52 | 4 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 14 | PASS | 0.1925 | 0.1458 | 89 | 0 | 35 | 77.7 | 47.4 | 50 | 32 | 95 | 50 | 4 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 15 | PASS | 0.1925 | 0.144 | 104 | 0 | 35 | 76.7 | 47.4 | 50 | 32 | 95 | 50 | 4 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 16 | FAIL | 0.1444 | 0.1384 | 221 | 0 | 35 | 98.3 | 60.8 | 50 | 32 | 80 | 42 | 3 | — | — | — | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: formula=16, llm=9.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | formula status | formula prov cost | formula util cost | llm status | llm prov cost | llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1687 | PASS | 0.7116 | 0.1688 |
| 2 | PASS | 0.5363 | 0.2272 | PASS | 0.4744 | 0.152 |
| 3 | PASS | 0.4464 | 0.2397 | PASS | 0.3795 | 0.1595 |
| 4 | PASS | 0.3945 | 0.2083 | PASS | 0.2277 | 0.1038 |
| 5 | PASS | 0.3471 | 0.2145 | PASS | 0.1898 | 0.0841 |
| 6 | PASS | 0.3331 | 0.2133 | PASS | 0.1423 | 0.0864 |
| 7 | PASS | 0.3191 | 0.1933 | PASS | 0.0759 | 0.0661 |
| 8 | PASS | 0.3051 | 0.1882 | PASS | 0.1659 | 0.1231 |
| 9 | PASS | 0.2329 | 0.1819 | FAIL | 0.0555 | 0.0548 |
| 10 | PASS | 0.2217 | 0.185 | — | — | — |
| 11 | PASS | 0.2141 | 0.1541 | — | — | — |
| 12 | PASS | 0.2069 | 0.1477 | — | — | — |
| 13 | PASS | 0.1997 | 0.1461 | — | — | — |
| 14 | PASS | 0.1925 | 0.1458 | — | — | — |
| 15 | PASS | 0.1925 | 0.144 | — | — | — |
| 16 | FAIL | 0.1444 | 0.1384 | — | — | — |
