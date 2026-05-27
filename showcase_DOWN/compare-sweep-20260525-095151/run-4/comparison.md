# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **formula**: `optimizer=formula` · `stopped_reason=first_fail` · iterations=9 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-8` · prov_cost_total=159.41935 (steady=159.336, best_pass=0.2213), util_cost_total=136.338748 (steady=136.296, best_pass=0.1893)
- **llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-2` · prov_cost_total=341.607138 (steady=341.568, best_pass=0.4744), util_cost_total=288.455818 (steady=288.432, best_pass=0.4006)

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | -94.0 | -43.0 |
| llm | -70.0 | -35.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula prov cost | formula util cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | llm prov cost | llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1487 | 6 | 0 | 45 | 21.4 | 11.7 | 150 | 75 | 300 | 150 | 5 | PASS | 0.7116 | 0.1828 | 6 | 0 | 45 | 26.3 | 14.4 | 150 | 75 | 300 | 150 | 5 |
| 2 | PASS | 0.5268 | 0.2175 | 6 | 0 | 45 | 42.5 | 19 | 111 | 56 | 222 | 111 | 5 | PASS | 0.4744 | 0.4006 | 97 | 0 | 45 | 86.7 | 42.8 | 100 | 50 | 100 | 50 | 5 |
| 3 | PASS | 0.4369 | 0.2256 | 7 | 0 | 45 | 53.2 | 23.3 | 92 | 47 | 184 | 92 | 5 | FAIL | 0.3795 | 0.3693 | 190 | 0 | 45 | 107.7 | 47.7 | 80 | 40 | 80 | 40 | 5 |
| 4 | PASS | 0.3845 | 0.2024 | 9 | 0 | 45 | 53.8 | 31.5 | 81 | 41 | 161 | 81 | 5 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 5 | PASS | 0.3371 | 0.1962 | 45 | 0 | 45 | 60 | 25.6 | 71 | 36 | 141 | 71 | 5 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 6 | PASS | 0.3231 | 0.1849 | 54 | 0 | 45 | 58.7 | 31 | 68 | 35 | 134 | 68 | 5 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 7 | PASS | 0.2321 | 0.1924 | 75 | 0 | 45 | 85.1 | 44.3 | 61 | 32 | 120 | 61 | 4 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 8 | PASS | 0.2213 | 0.1893 | 59 | 0 | 45 | 87.7 | 49.4 | 58 | 32 | 114 | 58 | 4 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 9 | FAIL | 0.1606 | 0.1529 | 152 | 0 | 45 | 97.7 | 55.4 | 56 | 32 | 109 | 56 | 3 | — | — | — | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: formula=9, llm=3.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | formula status | formula prov cost | formula util cost | llm status | llm prov cost | llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1487 | PASS | 0.7116 | 0.1828 |
| 2 | PASS | 0.5268 | 0.2175 | PASS | 0.4744 | 0.4006 |
| 3 | PASS | 0.4369 | 0.2256 | FAIL | 0.3795 | 0.3693 |
| 4 | PASS | 0.3845 | 0.2024 | — | — | — |
| 5 | PASS | 0.3371 | 0.1962 | — | — | — |
| 6 | PASS | 0.3231 | 0.1849 | — | — | — |
| 7 | PASS | 0.2321 | 0.1924 | — | — | — |
| 8 | PASS | 0.2213 | 0.1893 | — | — | — |
| 9 | FAIL | 0.1606 | 0.1529 | — | — | — |
