# Squeeze optimizer comparison

## Summary

- **formula**: `optimizer=formula` · `stopped_reason=first_fail` · iterations=10 · `best_pass_dir=/app/results/squeeze-compare-formula/run-37/iteration-9`
- **llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=5 · `best_pass_dir=/app/results/squeeze-compare-llm/run-48/iteration-4`

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | -93.0 | -43.0 |
| llm | -70.0 | -35.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula repl | llm status | llm cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 1.116 | 6 | 0 | 25 | 23.7 | 14.7 | 150 | 75 | 5 | PASS | 1.116 | 6 | 0 | 25 | 27.2 | 14.1 | 150 | 75 | 5 |
| 2 | PASS | 0.8433 | 6 | 0 | 25 | 42.9 | 25.7 | 113 | 57 | 5 | PASS | 0.7441 | 21 | 0 | 25 | 65 | 32.4 | 100 | 50 | 5 |
| 3 | PASS | 0.7044 | 6 | 0 | 25 | 53.9 | 26.3 | 94 | 48 | 5 | PASS | 0.6697 | 33 | 0 | 25 | 72.2 | 34.8 | 90 | 45 | 5 |
| 4 | PASS | 0.6201 | 6 | 0 | 25 | 50.8 | 29.5 | 83 | 42 | 5 | PASS | 0.5358 | 36 | 0 | 25 | 79 | 45.1 | 90 | 45 | 4 |
| 5 | PASS | 0.4325 | 23 | 0 | 25 | 77.2 | 37.4 | 72 | 37 | 4 | FAIL | 0.3572 | 69 | 0 | 25 | 95.6 | 39.5 | 80 | 40 | 3 |
| 6 | PASS | 0.4166 | 27 | 0 | 25 | 80.5 | 38.7 | 69 | 36 | 4 | — | — | — | — | — | — | — | — | — | — |
| 7 | PASS | 0.4007 | 40 | 0 | 25 | 64 | 33.5 | 66 | 35 | 4 | — | — | — | — | — | — | — | — | — | — |
| 8 | PASS | 0.3848 | 43 | 0 | 25 | 66.4 | 35.4 | 63 | 34 | 4 | — | — | — | — | — | — | — | — | — | — |
| 9 | PASS | 0.2767 | 88 | 0 | 25 | 91.5 | 49.2 | 60 | 33 | 3 | — | — | — | — | — | — | — | — | — | — |
| 10 | FAIL | 0.2647 | 73 | 0 | 25 | 96.1 | 53 | 57 | 32 | 3 | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: formula=10, llm=5.*
