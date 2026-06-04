# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **formula**: `optimizer=formula` · `stopped_reason=first_fail` · iterations=14 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-13` · prov_cost_total=138.709228 (steady=138.6, best_pass=0.1925), util_cost_total=92.075545 (steady=92.016, best_pass=0.1278)
- **llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=8 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-7` · prov_cost_total=102.520293 (steady=102.456, best_pass=0.1423), util_cost_total=82.110302 (steady=82.08, best_pass=0.114)

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | -100.0 | -43.0 |
| llm | -110.0 | -55.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula prov cost | formula util cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | llm prov cost | llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1419 | 6 | 0 | 35 | 20.4 | 11.5 | 150 | 75 | 300 | 150 | 5 | PASS | 0.7116 | 0.1626 | 6 | 0 | 35 | 23.3 | 14.5 | 150 | 75 | 300 | 150 | 5 |
| 2 | PASS | 0.5268 | 0.2067 | 6 | 0 | 35 | 40.2 | 21.7 | 111 | 56 | 221 | 111 | 5 | PASS | 0.4744 | 0.2116 | 6 | 0 | 35 | 45.7 | 24.4 | 100 | 50 | 200 | 100 | 5 |
| 3 | PASS | 0.432 | 0.2174 | 6 | 0 | 35 | 51.6 | 27 | 91 | 46 | 181 | 91 | 5 | PASS | 0.427 | 0.2145 | 6 | 0 | 35 | 51.5 | 27.1 | 90 | 45 | 180 | 90 | 5 |
| 4 | PASS | 0.375 | 0.1875 | 7 | 0 | 35 | 51 | 31.6 | 79 | 40 | 157 | 79 | 5 | PASS | 0.3036 | 0.1809 | 6 | 0 | 35 | 60.8 | 37.3 | 80 | 40 | 170 | 85 | 4 |
| 5 | PASS | 0.3276 | 0.1913 | 31 | 0 | 35 | 59.9 | 30.8 | 69 | 35 | 136 | 69 | 5 | PASS | 0.2661 | 0.1469 | 13 | 0 | 35 | 56.6 | 30.1 | 70 | 36 | 150 | 75 | 4 |
| 6 | PASS | 0.2991 | 0.1943 | 33 | 0 | 35 | 66.4 | 39 | 63 | 32 | 123 | 63 | 5 | PASS | 0.1708 | 0.1066 | 15 | 0 | 35 | 64 | 33.6 | 60 | 30 | 150 | 75 | 3 |
| 7 | PASS | 0.2856 | 0.1853 | 48 | 0 | 35 | 66.6 | 35.1 | 60 | 32 | 117 | 60 | 5 | PASS | 0.1423 | 0.114 | 111 | 0 | 35 | 81.8 | 48.6 | 50 | 25 | 100 | 50 | 3 |
| 8 | PASS | 0.2721 | 0.1801 | 51 | 0 | 35 | 67.6 | 42.8 | 57 | 32 | 112 | 57 | 5 | FAIL | 0.0759 | 0.075 | 24 | 0 | 35 | 113.7 | 77.1 | 40 | 20 | 100 | 50 | 2 |
| 9 | PASS | 0.2105 | 0.1704 | 61 | 0 | 35 | 82.5 | 56.6 | 55 | 32 | 107 | 55 | 4 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 10 | PASS | 0.2033 | 0.1719 | 53 | 0 | 35 | 86.7 | 51.9 | 53 | 32 | 102 | 53 | 4 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 11 | PASS | 0.1961 | 0.1426 | 68 | 0 | 35 | 74.6 | 44.9 | 51 | 32 | 97 | 51 | 4 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 12 | PASS | 0.1925 | 0.1249 | 63 | 0 | 35 | 66.2 | 45.6 | 50 | 32 | 93 | 49 | 4 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 13 | PASS | 0.1925 | 0.1278 | 70 | 0 | 35 | 67.7 | 47.7 | 50 | 32 | 93 | 49 | 4 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 14 | FAIL | 0.1444 | 0.1397 | 146 | 0 | 35 | 105.6 | 49.6 | 50 | 32 | 78 | 42 | 3 | — | — | — | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: formula=14, llm=8.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | formula status | formula prov cost | formula util cost | llm status | llm prov cost | llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1419 | PASS | 0.7116 | 0.1626 |
| 2 | PASS | 0.5268 | 0.2067 | PASS | 0.4744 | 0.2116 |
| 3 | PASS | 0.432 | 0.2174 | PASS | 0.427 | 0.2145 |
| 4 | PASS | 0.375 | 0.1875 | PASS | 0.3036 | 0.1809 |
| 5 | PASS | 0.3276 | 0.1913 | PASS | 0.2661 | 0.1469 |
| 6 | PASS | 0.2991 | 0.1943 | PASS | 0.1708 | 0.1066 |
| 7 | PASS | 0.2856 | 0.1853 | PASS | 0.1423 | 0.114 |
| 8 | PASS | 0.2721 | 0.1801 | FAIL | 0.0759 | 0.075 |
| 9 | PASS | 0.2105 | 0.1704 | — | — | — |
| 10 | PASS | 0.2033 | 0.1719 | — | — | — |
| 11 | PASS | 0.1961 | 0.1426 | — | — | — |
| 12 | PASS | 0.1925 | 0.1249 | — | — | — |
| 13 | PASS | 0.1925 | 0.1278 | — | — | — |
| 14 | FAIL | 0.1444 | 0.1397 | — | — | — |
