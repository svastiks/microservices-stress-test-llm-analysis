# Squeeze optimizer comparison

## Summary

- **formula**: `optimizer=formula` · `stopped_reason=first_fail` · iterations=4 · `best_pass_dir=/app/results/squeeze-compare-formula/run-29/iteration-3`
- **llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=2 · `best_pass_dir=/app/results/squeeze-compare-llm/run-39/iteration-1`

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | -13.0 | -6.0 |
| llm | -10.0 | -5.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula repl | llm status | llm cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.1488 | 7 | 0 | 25 | 79.4 | 36.8 | 100 | 50 | 1 | PASS | 0.1488 | 9 | 0 | 25 | 83.5 | 71.7 | 100 | 50 | 1 |
| 2 | PASS | 0.1419 | 18 | 0 | 25 | 84.1 | 57.8 | 95 | 48 | 1 | FAIL | 0.1339 | 30 | 0 | 25 | 98.4 | 61.7 | 90 | 45 | 1 |
| 3 | PASS | 0.1359 | 16 | 0 | 25 | 93.2 | 60.4 | 91 | 46 | 1 | — | — | — | — | — | — | — | — | — | — |
| 4 | FAIL | 0.13 | 28 | 0 | 25 | 98.5 | 66.3 | 87 | 44 | 1 | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: formula=4, llm=2.*
