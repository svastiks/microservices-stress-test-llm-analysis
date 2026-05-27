# Squeeze optimizer comparison

## Summary

- **formula**: `optimizer=formula` · `stopped_reason=first_fail` · iterations=13 · `best_pass_dir=/app/results/squeeze-compare-formula/run-33/iteration-12`
- **llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=7 · `best_pass_dir=/app/results/squeeze-compare-llm/run-44/iteration-6`

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | -93.0 | -43.0 |
| llm | -50.0 | -25.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula repl | llm status | llm cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 1.116 | 6 | 0 | 25 | 25.4 | 11.7 | 150 | 75 | 5 | PASS | 1.116 | 6 | 0 | 25 | 26.8 | 14.5 | 150 | 75 | 5 |
| 2 | PASS | 0.8483 | 6 | 0 | 25 | 43 | 21.6 | 114 | 57 | 5 | PASS | 0.7441 | 7 | 0 | 25 | 32.3 | 16.9 | 100 | 50 | 5 |
| 3 | PASS | 0.5675 | 6 | 0 | 25 | 69.3 | 32.3 | 95 | 48 | 4 | PASS | 0.4763 | 6 | 0 | 25 | 42.3 | 20.6 | 80 | 40 | 4 |
| 4 | PASS | 0.5437 | 7 | 0 | 25 | 63.7 | 35 | 91 | 46 | 4 | PASS | 0.3572 | 6 | 0 | 25 | 35.2 | 21.2 | 60 | 30 | 4 |
| 5 | PASS | 0.5199 | 6 | 0 | 25 | 54.7 | 25.7 | 87 | 44 | 4 | PASS | 0.2977 | 6 | 0 | 25 | 30.2 | 14.5 | 50 | 25 | 4 |
| 6 | PASS | 0.4603 | 21 | 0 | 25 | 64.4 | 28.9 | 77 | 39 | 4 | PASS | 0.1482 | 29 | 0 | 25 | 82.6 | 19.7 | 25 | 25 | 3 |
| 7 | PASS | 0.4444 | 33 | 0 | 25 | 64.8 | 29.6 | 74 | 38 | 4 | FAIL | 0.4465 | 106 | 0 | 25 | 122.6 | 58.3 | 100 | 50 | 3 |
| 8 | PASS | 0.4285 | 30 | 0 | 25 | 64.7 | 31.5 | 71 | 37 | 4 | — | — | — | — | — | — | — | — | — | — |
| 9 | PASS | 0.4126 | 55 | 0 | 25 | 66.8 | 32.3 | 68 | 36 | 4 | — | — | — | — | — | — | — | — | — | — |
| 10 | PASS | 0.3967 | 43 | 0 | 25 | 70.2 | 34.8 | 65 | 35 | 4 | — | — | — | — | — | — | — | — | — | — |
| 11 | PASS | 0.3808 | 89 | 0 | 25 | 71.2 | 36.2 | 62 | 34 | 4 | — | — | — | — | — | — | — | — | — | — |
| 12 | PASS | 0.3649 | 51 | 0 | 25 | 74 | 38 | 59 | 33 | 4 | — | — | — | — | — | — | — | — | — | — |
| 13 | FAIL | 0.2647 | 76 | 0 | 25 | 99 | 52.1 | 57 | 32 | 3 | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: formula=13, llm=7.*
