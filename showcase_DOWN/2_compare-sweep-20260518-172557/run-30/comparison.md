# Squeeze optimizer comparison

## Summary

- **formula**: `optimizer=formula` · `stopped_reason=first_fail` · iterations=11 · `best_pass_dir=/app/results/squeeze-compare-formula/run-30/iteration-10`
- **llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=7 · `best_pass_dir=/app/results/squeeze-compare-llm/run-40/iteration-6`

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | -46.0 | -18.0 |
| llm | -35.0 | -5.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula repl | llm status | llm cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.4465 | 6 | 0 | 25 | 46.5 | 23.9 | 100 | 50 | 3 | PASS | 0.4465 | 6 | 0 | 25 | 52.4 | 29.9 | 100 | 50 | 3 |
| 2 | PASS | 0.381 | 7 | 0 | 25 | 71.7 | 34.5 | 85 | 43 | 3 | PASS | 0.4465 | 5 | 0 | 25 | 57 | 29.8 | 100 | 50 | 3 |
| 3 | PASS | 0.3631 | 12 | 0 | 25 | 75.4 | 37.4 | 81 | 41 | 3 | PASS | 0.2977 | 5 | 0 | 25 | 76.1 | 35.9 | 100 | 50 | 2 |
| 4 | PASS | 0.3453 | 24 | 0 | 25 | 75.2 | 44 | 77 | 39 | 3 | PASS | 0.2977 | 6 | 0 | 25 | 59 | 27.1 | 100 | 50 | 2 |
| 5 | PASS | 0.4444 | 24 | 0 | 25 | 59.3 | 30.8 | 74 | 38 | 4 | PASS | 0.1488 | 6 | 0 | 25 | 76.4 | 18.8 | 100 | 50 | 1 |
| 6 | PASS | 0.3035 | 39 | 0 | 25 | 89.5 | 44.3 | 67 | 35 | 3 | PASS | 0.1238 | 78 | 0 | 25 | 68.6 | 19.5 | 75 | 50 | 1 |
| 7 | PASS | 0.2916 | 44 | 0 | 25 | 89.7 | 47.4 | 64 | 34 | 3 | FAIL | 0.1089 | 122 | 0 | 25 | 96.5 | 43 | 65 | 45 | 1 |
| 8 | PASS | 0.2797 | 93 | 0 | 25 | 89.7 | 48.1 | 61 | 33 | 3 | — | — | — | — | — | — | — | — | — | — |
| 9 | PASS | 0.2677 | 53 | 0 | 25 | 92.2 | 52 | 58 | 32 | 3 | — | — | — | — | — | — | — | — | — | — |
| 10 | PASS | 0.2617 | 115 | 0 | 25 | 94.9 | 53.4 | 56 | 32 | 3 | — | — | — | — | — | — | — | — | — | — |
| 11 | FAIL | 0.2557 | 105 | 0 | 25 | 96.9 | 57.5 | 54 | 32 | 3 | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: formula=11, llm=7.*
