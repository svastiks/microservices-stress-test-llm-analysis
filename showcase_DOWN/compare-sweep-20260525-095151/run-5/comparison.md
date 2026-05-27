# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **formula**: `optimizer=formula` · `stopped_reason=first_fail` · iterations=14 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-13` · prov_cost_total=173.351893 (steady=173.232, best_pass=0.2406), util_cost_total=125.995443 (steady=125.928, best_pass=0.1749)
- **llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-2` · prov_cost_total=341.60619 (steady=341.568, best_pass=0.4744), util_cost_total=297.887005 (steady=297.864, best_pass=0.4137)

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | -100.0 | -43.0 |
| llm | -60.0 | -30.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula prov cost | formula util cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | llm prov cost | llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1766 | 7 | 0 | 55 | 25.4 | 14.1 | 150 | 75 | 300 | 150 | 5 | PASS | 0.7116 | 0.1701 | 7 | 0 | 55 | 24.4 | 14.8 | 150 | 75 | 300 | 150 | 5 |
| 2 | PASS | 0.5408 | 0.2312 | 6 | 0 | 55 | 43.9 | 21.7 | 114 | 57 | 227 | 114 | 5 | PASS | 0.4744 | 0.4137 | 124 | 0 | 55 | 89.2 | 50.3 | 100 | 50 | 100 | 50 | 5 |
| 3 | PASS | 0.4509 | 0.2336 | 7 | 0 | 55 | 53.4 | 22.7 | 95 | 48 | 190 | 95 | 5 | FAIL | 0.3416 | 0.3364 | 122 | 0 | 55 | 128.2 | 70.5 | 90 | 45 | 90 | 45 | 4 |
| 4 | PASS | 0.394 | 0.2036 | 7 | 0 | 55 | 52.8 | 31 | 83 | 42 | 166 | 83 | 5 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 5 | PASS | 0.3466 | 0.1941 | 38 | 0 | 55 | 57.7 | 25 | 73 | 37 | 145 | 73 | 5 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 6 | PASS | 0.3086 | 0.1855 | 63 | 0 | 55 | 61.6 | 33.2 | 65 | 33 | 130 | 65 | 5 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 7 | PASS | 0.2946 | 0.1919 | 51 | 0 | 55 | 66.8 | 35.1 | 62 | 32 | 124 | 62 | 5 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 8 | PASS | 0.2811 | 0.187 | 68 | 0 | 55 | 67.9 | 42.8 | 59 | 32 | 118 | 59 | 5 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 9 | PASS | 0.2721 | 0.184 | 86 | 0 | 55 | 69.3 | 39.9 | 57 | 32 | 113 | 57 | 5 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 10 | PASS | 0.2631 | 0.1872 | 71 | 0 | 55 | 72.7 | 46.2 | 55 | 32 | 108 | 55 | 5 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 11 | PASS | 0.2541 | 0.1787 | 79 | 0 | 55 | 72.1 | 43.3 | 53 | 32 | 103 | 53 | 5 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 12 | PASS | 0.2451 | 0.1815 | 123 | 0 | 55 | 75.7 | 49.4 | 51 | 32 | 98 | 51 | 5 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 13 | PASS | 0.2406 | 0.1749 | 135 | 0 | 55 | 74.5 | 46.5 | 50 | 32 | 94 | 49 | 5 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 14 | FAIL | 0.1925 | 0.1879 | 134 | 0 | 55 | 99.9 | 64.8 | 50 | 32 | 85 | 45 | 4 | — | — | — | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: formula=14, llm=3.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | formula status | formula prov cost | formula util cost | llm status | llm prov cost | llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1766 | PASS | 0.7116 | 0.1701 |
| 2 | PASS | 0.5408 | 0.2312 | PASS | 0.4744 | 0.4137 |
| 3 | PASS | 0.4509 | 0.2336 | FAIL | 0.3416 | 0.3364 |
| 4 | PASS | 0.394 | 0.2036 | — | — | — |
| 5 | PASS | 0.3466 | 0.1941 | — | — | — |
| 6 | PASS | 0.3086 | 0.1855 | — | — | — |
| 7 | PASS | 0.2946 | 0.1919 | — | — | — |
| 8 | PASS | 0.2811 | 0.187 | — | — | — |
| 9 | PASS | 0.2721 | 0.184 | — | — | — |
| 10 | PASS | 0.2631 | 0.1872 | — | — | — |
| 11 | PASS | 0.2541 | 0.1787 | — | — | — |
| 12 | PASS | 0.2451 | 0.1815 | — | — | — |
| 13 | PASS | 0.2406 | 0.1749 | — | — | — |
| 14 | FAIL | 0.1925 | 0.1879 | — | — | — |
