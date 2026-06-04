# Squeeze optimizer comparison

## Summary

- **formula**: `optimizer=formula` · `stopped_reason=first_fail` · iterations=11 · `best_pass_dir=/app/results/squeeze-compare-formula/run-34/iteration-10`
- **llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=7 · `best_pass_dir=/app/results/squeeze-compare-llm/run-45/iteration-6`

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | -93.0 | -43.0 |
| llm | -110.0 | -55.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula repl | llm status | llm cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 1.116 | 6 | 0 | 25 | 24.1 | 11.7 | 150 | 75 | 5 | PASS | 1.116 | 6 | 0 | 25 | 27.8 | 14.2 | 150 | 75 | 5 |
| 2 | PASS | 0.8433 | 6 | 0 | 25 | 43.1 | 21.5 | 113 | 57 | 5 | PASS | 0.7441 | 6 | 0 | 25 | 48.4 | 24.8 | 100 | 50 | 5 |
| 3 | PASS | 0.5635 | 7 | 0 | 25 | 67.7 | 32.9 | 94 | 48 | 4 | PASS | 0.6697 | 6 | 0 | 25 | 56.2 | 27.2 | 90 | 45 | 5 |
| 4 | PASS | 0.5397 | 7 | 0 | 25 | 63.4 | 35.3 | 90 | 46 | 4 | PASS | 0.4363 | 7 | 0 | 25 | 64 | 40.4 | 70 | 40 | 4 |
| 5 | PASS | 0.5159 | 9 | 0 | 25 | 54.6 | 29.5 | 86 | 44 | 4 | PASS | 0.3572 | 6 | 0 | 25 | 54.6 | 28.3 | 60 | 30 | 4 |
| 6 | PASS | 0.4563 | 21 | 0 | 25 | 62.3 | 29.1 | 76 | 39 | 4 | PASS | 0.2232 | 41 | 0 | 25 | 82.6 | 40.2 | 50 | 25 | 3 |
| 7 | PASS | 0.4404 | 37 | 0 | 25 | 59.9 | 30.1 | 73 | 38 | 4 | FAIL | 0.1786 | 95 | 0 | 25 | 98.2 | 48.8 | 40 | 20 | 3 |
| 8 | PASS | 0.4007 | 44 | 0 | 25 | 68.5 | 33.8 | 66 | 35 | 4 | — | — | — | — | — | — | — | — | — | — |
| 9 | PASS | 0.3848 | 57 | 0 | 25 | 70.4 | 35.5 | 63 | 34 | 4 | — | — | — | — | — | — | — | — | — | — |
| 10 | PASS | 0.3689 | 32 | 0 | 25 | 73 | 37.3 | 60 | 33 | 4 | — | — | — | — | — | — | — | — | — | — |
| 11 | FAIL | 0.2647 | 65 | 0 | 25 | 99.1 | 52 | 57 | 32 | 3 | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: formula=11, llm=7.*
