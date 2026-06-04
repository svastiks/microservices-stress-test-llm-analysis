# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **formula**: `optimizer=formula` · `stopped_reason=first_fail` · iterations=13 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-12` · prov_cost_total=143.893923 (steady=143.784, best_pass=0.1997), util_cost_total=120.515303 (steady=120.456, best_pass=0.1673)
- **llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=9 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-8` · prov_cost_total=61.19 (steady=61.128, best_pass=0.0849), util_cost_total=43.008363 (steady=42.984, best_pass=0.0597)

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | -100.0 | -43.0 |
| llm | -110.0 | -55.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula prov cost | formula util cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | llm prov cost | llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1501 | 6 | 0 | 45 | 21.7 | 9.9 | 150 | 75 | 300 | 150 | 5 | PASS | 0.7116 | 0.1679 | 6 | 0 | 45 | 24.1 | 14.2 | 150 | 75 | 300 | 150 | 5 |
| 2 | PASS | 0.5268 | 0.2111 | 6 | 0 | 45 | 41.2 | 19.4 | 111 | 56 | 222 | 111 | 5 | PASS | 0.4744 | 0.1431 | 6 | 0 | 45 | 30.9 | 16.4 | 100 | 50 | 300 | 150 | 5 |
| 3 | PASS | 0.4369 | 0.2182 | 6 | 0 | 45 | 51.2 | 27.2 | 92 | 47 | 183 | 92 | 5 | PASS | 0.4245 | 0.1591 | 6 | 0 | 45 | 38.3 | 20.6 | 90 | 40 | 250 | 125 | 5 |
| 4 | PASS | 0.38 | 0.1938 | 9 | 0 | 45 | 52.1 | 31 | 80 | 41 | 158 | 80 | 5 | PASS | 0.2757 | 0.1436 | 6 | 0 | 45 | 53.1 | 31.4 | 73 | 33 | 203 | 102 | 4 |
| 5 | PASS | 0.3326 | 0.1963 | 23 | 0 | 45 | 60.6 | 30.6 | 70 | 36 | 137 | 70 | 5 | PASS | 0.2277 | 0.1008 | 6 | 0 | 45 | 45.2 | 27.1 | 60 | 30 | 203 | 102 | 4 |
| 6 | PASS | 0.3186 | 0.1918 | 35 | 0 | 45 | 61.5 | 37.2 | 67 | 35 | 131 | 67 | 5 | PASS | 0.1465 | 0.0837 | 6 | 0 | 45 | 58.9 | 29.3 | 51 | 30 | 171 | 86 | 3 |
| 7 | PASS | 0.3046 | 0.1908 | 47 | 0 | 45 | 64.2 | 35.3 | 64 | 34 | 125 | 64 | 5 | PASS | 0.0967 | 0.0798 | 6 | 0 | 45 | 84.5 | 46.6 | 51 | 25 | 145 | 80 | 2 |
| 8 | PASS | 0.2906 | 0.1912 | 52 | 0 | 45 | 67.3 | 40.4 | 61 | 33 | 119 | 61 | 5 | PASS | 0.0849 | 0.0597 | 7 | 0 | 45 | 71.7 | 42.5 | 45 | 20 | 125 | 70 | 2 |
| 9 | PASS | 0.2766 | 0.1796 | 55 | 0 | 45 | 66.6 | 37 | 58 | 32 | 114 | 58 | 5 | FAIL | 0.038 | 0.0368 | 81 | 0 | 45 | 100.4 | 41.5 | 40 | 20 | 100 | 50 | 1 |
| 10 | PASS | 0.2676 | 0.1768 | 61 | 0 | 45 | 67.4 | 44.2 | 56 | 32 | 109 | 56 | 5 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 11 | PASS | 0.2069 | 0.1669 | 56 | 0 | 45 | 82.7 | 49.2 | 54 | 32 | 104 | 54 | 4 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 12 | PASS | 0.1997 | 0.1673 | 64 | 0 | 45 | 85.8 | 53.5 | 52 | 32 | 99 | 52 | 4 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 13 | FAIL | 0.1444 | 0.1382 | 68 | 0 | 45 | 98.9 | 49.7 | 50 | 32 | 95 | 50 | 3 | — | — | — | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: formula=13, llm=9.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | formula status | formula prov cost | formula util cost | llm status | llm prov cost | llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1501 | PASS | 0.7116 | 0.1679 |
| 2 | PASS | 0.5268 | 0.2111 | PASS | 0.4744 | 0.1431 |
| 3 | PASS | 0.4369 | 0.2182 | PASS | 0.4245 | 0.1591 |
| 4 | PASS | 0.38 | 0.1938 | PASS | 0.2757 | 0.1436 |
| 5 | PASS | 0.3326 | 0.1963 | PASS | 0.2277 | 0.1008 |
| 6 | PASS | 0.3186 | 0.1918 | PASS | 0.1465 | 0.0837 |
| 7 | PASS | 0.3046 | 0.1908 | PASS | 0.0967 | 0.0798 |
| 8 | PASS | 0.2906 | 0.1912 | PASS | 0.0849 | 0.0597 |
| 9 | PASS | 0.2766 | 0.1796 | FAIL | 0.038 | 0.0368 |
| 10 | PASS | 0.2676 | 0.1768 | — | — | — |
| 11 | PASS | 0.2069 | 0.1669 | — | — | — |
| 12 | PASS | 0.1997 | 0.1673 | — | — | — |
| 13 | FAIL | 0.1444 | 0.1382 | — | — | — |
