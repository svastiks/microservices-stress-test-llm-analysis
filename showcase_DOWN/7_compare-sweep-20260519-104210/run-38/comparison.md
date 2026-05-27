# Squeeze optimizer comparison

## Summary

- **formula**: `optimizer=formula` · `stopped_reason=first_fail` · iterations=11 · `best_pass_dir=/app/results/squeeze-compare-formula/run-38/iteration-10`
- **llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=6 · `best_pass_dir=/app/results/squeeze-compare-llm/run-49/iteration-5`

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | -93.0 | -42.0 |
| llm | -120.0 | -60.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula repl | llm status | llm cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 1.116 | 6 | 0 | 25 | 27.3 | 11.7 | 150 | 75 | 5 | PASS | 1.116 | 6 | 0 | 25 | 28.1 | 14.2 | 150 | 75 | 5 |
| 2 | PASS | 0.8582 | 6 | 0 | 25 | 43.3 | 21.2 | 115 | 58 | 5 | PASS | 0.7441 | 6 | 0 | 25 | 51.4 | 24.7 | 100 | 50 | 5 |
| 3 | PASS | 0.7193 | 6 | 0 | 25 | 55.4 | 25.6 | 96 | 49 | 5 | PASS | 0.5953 | 6 | 0 | 25 | 52.8 | 27.9 | 80 | 40 | 5 |
| 4 | PASS | 0.6398 | 6 | 0 | 25 | 54.1 | 29 | 85 | 44 | 5 | PASS | 0.3572 | 27 | 0 | 25 | 73.3 | 39.7 | 60 | 30 | 4 |
| 5 | PASS | 0.4523 | 29 | 0 | 25 | 74 | 35.3 | 75 | 39 | 4 | PASS | 0.2381 | 128 | 0 | 25 | 90 | 53.2 | 40 | 20 | 4 |
| 6 | PASS | 0.4364 | 24 | 0 | 25 | 76.6 | 38.3 | 72 | 38 | 4 | FAIL | 0.1339 | 175 | 0 | 25 | 134 | 76 | 30 | 15 | 3 |
| 7 | PASS | 0.4205 | 48 | 0 | 25 | 64.4 | 37 | 69 | 37 | 4 | — | — | — | — | — | — | — | — | — | — |
| 8 | PASS | 0.4046 | 33 | 0 | 25 | 68.3 | 33.9 | 66 | 36 | 4 | — | — | — | — | — | — | — | — | — | — |
| 9 | PASS | 0.3887 | 48 | 0 | 25 | 69.4 | 35.2 | 63 | 35 | 4 | — | — | — | — | — | — | — | — | — | — |
| 10 | PASS | 0.3728 | 47 | 0 | 25 | 72.9 | 37.8 | 60 | 34 | 4 | — | — | — | — | — | — | — | — | — | — |
| 11 | FAIL | 0.2677 | 101 | 0 | 25 | 99.7 | 52.3 | 57 | 33 | 3 | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: formula=11, llm=6.*
