# Squeeze optimizer comparison

## Summary

- **formula**: `optimizer=formula` · `stopped_reason=first_fail` · iterations=13 · `best_pass_dir=/app/results/squeeze-compare-formula/run-22/iteration-12`
- **llm**: `optimizer=llm` · `stopped_reason=empty_recommended_diff` · iterations=2 · `best_pass_dir=/app/results/squeeze-compare-llm/run-22/iteration-2`

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | -50.0 | -18.0 |
| llm | -30.0 | -10.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula repl | llm status | llm cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.4465 | 6 | 0 | 15 | 33.8 | 22.9 | 100 | 50 | 3 | PASS | 0.4465 | 6 | 0 | 15 | 26 | 17.1 | 100 | 50 | 3 |
| 2 | PASS | 0.3572 | 6 | 0 | 15 | 47.2 | 29.6 | 80 | 40 | 3 | PASS | 0.3272 | 52 | 0 | 15 | 66.6 | 25.7 | 70 | 40 | 3 |
| 3 | PASS | 0.2024 | 6 | 0 | 15 | 83.4 | 52.2 | 68 | 34 | 2 | — | — | — | — | — | — | — | — | — | — |
| 4 | PASS | 0.1865 | 7 | 0.0007 | 15 | 91.9 | 43.4 | 62 | 32 | 2 | — | — | — | — | — | — | — | — | — | — |
| 5 | PASS | 0.1745 | 17 | 0 | 15 | 81.4 | 33.5 | 56 | 32 | 2 | — | — | — | — | — | — | — | — | — | — |
| 6 | PASS | 0.1645 | 40 | 0.0007 | 15 | 88.2 | 36.5 | 51 | 32 | 2 | — | — | — | — | — | — | — | — | — | — |
| 7 | PASS | 0.1625 | 79 | 0.0007 | 15 | 95.3 | 40.9 | 50 | 32 | 2 | — | — | — | — | — | — | — | — | — | — |
| 8 | PASS | 0.1625 | 80 | 0 | 15 | 101.1 | 45.6 | 50 | 32 | 2 | — | — | — | — | — | — | — | — | — | — |
| 9 | PASS | 0.1625 | 78 | 0 | 15 | 109.7 | 49.9 | 50 | 32 | 2 | — | — | — | — | — | — | — | — | — | — |
| 10 | PASS | 0.1625 | 164 | 0 | 15 | 118 | 53.8 | 50 | 32 | 2 | — | — | — | — | — | — | — | — | — | — |
| 11 | PASS | 0.1625 | 408 | 0 | 15 | 111 | 59.6 | 50 | 32 | 2 | — | — | — | — | — | — | — | — | — | — |
| 12 | PASS | 0.1625 | 335 | 0 | 15 | 104.8 | 58.8 | 50 | 32 | 2 | — | — | — | — | — | — | — | — | — | — |
| 13 | FAIL | 0.1625 | 971 | 0 | 15 | 97.7 | 59 | 50 | 32 | 2 | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: formula=13, llm=2.*
