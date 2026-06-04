# Squeeze optimizer comparison

## Summary

- **formula**: `optimizer=formula` · `stopped_reason=empty_recommended_diff` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-formula/run-11/iteration-3`
- **llm**: `optimizer=llm` · `stopped_reason=empty_recommended_diff` · iterations=2 · `best_pass_dir=/app/results/squeeze-compare-llm/run-11/iteration-2`

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | -32.0 | -16.0 |
| llm | -30.0 | -15.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula repl | llm status | llm cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.4465 | 5 | 0 | 35 | 34.7 | 17.9 | 100 | 50 | 3 | PASS | 0.4465 | 6 | 0 | 35 | 36.1 | 18 | 100 | 50 | 3 |
| 2 | PASS | 0.3572 | 5 | 0 | 35 | 47.8 | 22.3 | 80 | 40 | 3 | PASS | 0.3125 | 74 | 0 | 35 | 73.7 | 34.7 | 70 | 35 | 3 |
| 3 | PASS | 0.2024 | 5 | 0 | 35 | 84.8 | 41.5 | 68 | 34 | 2 | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: formula=3, llm=2.*
