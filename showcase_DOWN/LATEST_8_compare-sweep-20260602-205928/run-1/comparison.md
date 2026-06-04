# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **formula**: `optimizer=formula` · `stopped_reason=first_fail` · iterations=19 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-18` · prov_cost_total=34.736203 (steady=34.632, best_pass=0.0481), util_cost_total=28.856023 (steady=28.8, best_pass=0.04)
- **llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=7 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-6` · prov_cost_total=83.07256 (steady=83.016, best_pass=0.1153), util_cost_total=76.12924 (steady=76.104, best_pass=0.1057)

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | -100.0 | -43.0 |
| llm | -120.0 | -55.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula prov cost | formula util cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | llm prov cost | llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.2211 | 6 | 0 | 25 | 32 | 13.9 | 150 | 75 | 300 | 150 | 5 | PASS | 0.7116 | 0.1358 | 6 | 0 | 25 | 19.6 | 9.5 | 150 | 75 | 300 | 150 | 5 |
| 2 | PASS | 0.5598 | 0.2228 | 6 | 0 | 25 | 40.7 | 23.2 | 118 | 59 | 235 | 118 | 5 | PASS | 0.4744 | 0.2072 | 6 | 0 | 25 | 44.9 | 21 | 100 | 50 | 200 | 100 | 5 |
| 3 | PASS | 0.3683 | 0.2162 | 6 | 0 | 25 | 60.2 | 31.2 | 97 | 49 | 193 | 97 | 4 | PASS | 0.427 | 0.2194 | 6 | 0 | 25 | 52.7 | 27 | 90 | 45 | 180 | 90 | 5 |
| 4 | PASS | 0.3532 | 0.1923 | 6 | 0 | 25 | 55.6 | 33.4 | 93 | 47 | 184 | 93 | 4 | PASS | 0.2845 | 0.1834 | 7 | 0 | 25 | 65.7 | 41.7 | 75 | 37 | 150 | 75 | 4 |
| 5 | PASS | 0.2364 | 0.1543 | 6 | 0 | 25 | 67.3 | 28 | 83 | 42 | 163 | 83 | 3 | PASS | 0.1917 | 0.1005 | 19 | 0 | 25 | 53.5 | 36 | 50 | 30 | 150 | 75 | 4 |
| 6 | PASS | 0.3 | 0.1388 | 7 | 0 | 25 | 47.5 | 23.5 | 79 | 40 | 155 | 79 | 4 | PASS | 0.1153 | 0.1057 | 59 | 0 | 25 | 94.5 | 49.5 | 40 | 25 | 100 | 50 | 3 |
| 7 | PASS | 0.1909 | 0.1174 | 27 | 0 | 25 | 62.9 | 36.5 | 67 | 34 | 132 | 67 | 3 | FAIL | 0.0579 | 0.0576 | 94 | 0 | 25 | 146.9 | 91.7 | 30 | 20 | 80 | 40 | 2 |
| 8 | PASS | 0.1825 | 0.1175 | 41 | 0 | 25 | 65.8 | 38.8 | 64 | 33 | 126 | 64 | 3 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 9 | PASS | 0.1741 | 0.1171 | 6 | 0 | 25 | 68.8 | 40.9 | 61 | 32 | 120 | 61 | 3 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 10 | PASS | 0.166 | 0.0967 | 45 | 0 | 25 | 59.3 | 41.1 | 58 | 32 | 114 | 58 | 3 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 11 | PASS | 0.1525 | 0.0961 | 62 | 0 | 25 | 63.6 | 54 | 53 | 32 | 103 | 53 | 3 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 12 | PASS | 0.1471 | 0.1025 | 70 | 0 | 25 | 71 | 50.2 | 51 | 32 | 98 | 51 | 3 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 13 | PASS | 0.1444 | 0.0999 | 26 | 0 | 25 | 70.4 | 51.9 | 50 | 32 | 94 | 49 | 3 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 14 | PASS | 0.1444 | 0.0976 | 44 | 0 | 25 | 69.2 | 44.1 | 50 | 32 | 85 | 45 | 3 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 15 | PASS | 0.0963 | 0.0762 | 61 | 0 | 25 | 81.3 | 48.3 | 50 | 32 | 79 | 42 | 2 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 16 | PASS | 0.0963 | 0.0547 | 7 | 0 | 25 | 58.9 | 27.7 | 50 | 32 | 79 | 42 | 2 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 17 | PASS | 0.0481 | 0.0327 | 155 | 0 | 25 | 68.9 | 54.2 | 50 | 32 | 66 | 36 | 1 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 18 | PASS | 0.0481 | 0.04 | 221 | 0 | 25 | 84.8 | 59.9 | 50 | 32 | 60 | 33 | 1 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 19 | FAIL | 0.0481 | 0.047 | 207 | 0 | 25 | 118.1 | 62.6 | 50 | 32 | 51 | 32 | 1 | — | — | — | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: formula=19, llm=7.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | formula status | formula prov cost | formula util cost | llm status | llm prov cost | llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.2211 | PASS | 0.7116 | 0.1358 |
| 2 | PASS | 0.5598 | 0.2228 | PASS | 0.4744 | 0.2072 |
| 3 | PASS | 0.3683 | 0.2162 | PASS | 0.427 | 0.2194 |
| 4 | PASS | 0.3532 | 0.1923 | PASS | 0.2845 | 0.1834 |
| 5 | PASS | 0.2364 | 0.1543 | PASS | 0.1917 | 0.1005 |
| 6 | PASS | 0.3 | 0.1388 | PASS | 0.1153 | 0.1057 |
| 7 | PASS | 0.1909 | 0.1174 | FAIL | 0.0579 | 0.0576 |
| 8 | PASS | 0.1825 | 0.1175 | — | — | — |
| 9 | PASS | 0.1741 | 0.1171 | — | — | — |
| 10 | PASS | 0.166 | 0.0967 | — | — | — |
| 11 | PASS | 0.1525 | 0.0961 | — | — | — |
| 12 | PASS | 0.1471 | 0.1025 | — | — | — |
| 13 | PASS | 0.1444 | 0.0999 | — | — | — |
| 14 | PASS | 0.1444 | 0.0976 | — | — | — |
| 15 | PASS | 0.0963 | 0.0762 | — | — | — |
| 16 | PASS | 0.0963 | 0.0547 | — | — | — |
| 17 | PASS | 0.0481 | 0.0327 | — | — | — |
| 18 | PASS | 0.0481 | 0.04 | — | — | — |
| 19 | FAIL | 0.0481 | 0.047 | — | — | — |
