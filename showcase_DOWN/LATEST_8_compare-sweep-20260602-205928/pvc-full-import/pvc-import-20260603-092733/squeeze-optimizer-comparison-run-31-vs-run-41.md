# Squeeze optimizer comparison

## Summary

- **formula**: `optimizer=formula` · `stopped_reason=first_fail` · iterations=16 · `best_pass_dir=/app/results/squeeze-compare-formula/run-31/iteration-15`
- **llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-llm/run-41/iteration-2`

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | -50.0 | -18.0 |
| llm | -25.0 | -12.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula repl | llm status | llm cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.4465 | 6 | 0 | 25 | 43.2 | 24 | 100 | 50 | 3 | PASS | 0.4465 | 6 | 0 | 25 | 43.1 | 30.5 | 100 | 50 | 3 |
| 2 | PASS | 0.372 | 7 | 0 | 25 | 71.8 | 36.2 | 83 | 42 | 3 | PASS | 0.372 | 12 | 0 | 25 | 59.9 | 36.7 | 83 | 42 | 3 |
| 3 | PASS | 0.3542 | 23 | 0 | 25 | 76 | 38 | 79 | 40 | 3 | FAIL | 0.2242 | 38 | 0 | 25 | 98.8 | 47.7 | 75 | 38 | 2 |
| 4 | PASS | 0.3393 | 14 | 0 | 25 | 70.2 | 45.5 | 76 | 38 | 3 | — | — | — | — | — | — | — | — | — | — |
| 5 | PASS | 0.3274 | 55 | 0 | 25 | 70.4 | 40.6 | 73 | 37 | 3 | — | — | — | — | — | — | — | — | — | — |
| 6 | PASS | 0.3155 | 51 | 0 | 25 | 74.3 | 49.5 | 70 | 36 | 3 | — | — | — | — | — | — | — | — | — | — |
| 7 | PASS | 0.3035 | 65 | 0 | 25 | 71.3 | 44.1 | 67 | 35 | 3 | — | — | — | — | — | — | — | — | — | — |
| 8 | PASS | 0.2916 | 44 | 0 | 25 | 78.6 | 46.7 | 64 | 34 | 3 | — | — | — | — | — | — | — | — | — | — |
| 9 | PASS | 0.2797 | 87 | 0 | 25 | 80.6 | 48.9 | 61 | 33 | 3 | — | — | — | — | — | — | — | — | — | — |
| 10 | PASS | 0.2677 | 64 | 0 | 25 | 82.3 | 51.6 | 58 | 32 | 3 | — | — | — | — | — | — | — | — | — | — |
| 11 | PASS | 0.2617 | 95 | 0 | 25 | 81 | 53 | 56 | 32 | 3 | — | — | — | — | — | — | — | — | — | — |
| 12 | PASS | 0.2557 | 71 | 0 | 25 | 85.9 | 55.2 | 54 | 32 | 3 | — | — | — | — | — | — | — | — | — | — |
| 13 | PASS | 0.2497 | 154 | 0 | 25 | 85.2 | 57 | 52 | 32 | 3 | — | — | — | — | — | — | — | — | — | — |
| 14 | PASS | 0.2438 | 128 | 0 | 25 | 90.5 | 59.3 | 50 | 32 | 3 | — | — | — | — | — | — | — | — | — | — |
| 15 | PASS | 0.2438 | 180 | 0 | 25 | 83.9 | 59.4 | 50 | 32 | 3 | — | — | — | — | — | — | — | — | — | — |
| 16 | FAIL | 0.1625 | 251 | 0 | 25 | 138.4 | 79.3 | 50 | 32 | 2 | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: formula=16, llm=3.*
