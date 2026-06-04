# Squeeze optimizer comparison

## Summary

- **formula**: `optimizer=formula` · `stopped_reason=empty_recommended_diff` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-formula/run-18/iteration-3`
- **llm**: `optimizer=llm` · `stopped_reason=empty_recommended_diff` · iterations=2 · `best_pass_dir=/app/results/squeeze-compare-llm/run-18/iteration-2`

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | -33.0 | -16.0 |
| llm | -30.0 | -15.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula repl | llm status | llm cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.4465 | 5 | 0 | 25 | 32 | 17.7 | 100 | 50 | 3 | PASS | 0.4465 | 6 | 0 | 25 | 34.3 | 17.6 | 100 | 50 | 3 |
| 2 | PASS | 0.3542 | 5 | 0 | 25 | 45.1 | 23.5 | 79 | 40 | 3 | PASS | 0.3125 | 68 | 0 | 25 | 63.9 | 33.5 | 70 | 35 | 3 |
| 3 | PASS | 0.2004 | 5 | 0.0004 | 25 | 83.9 | 40.9 | 67 | 34 | 2 | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: formula=3, llm=2.*
