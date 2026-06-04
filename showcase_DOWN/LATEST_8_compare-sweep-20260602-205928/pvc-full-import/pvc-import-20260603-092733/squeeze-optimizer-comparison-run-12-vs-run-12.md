# Squeeze optimizer comparison

## Summary

- **formula**: `optimizer=formula` · `stopped_reason=empty_recommended_diff` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-formula/run-12/iteration-3`
- **llm**: `optimizer=llm` · `stopped_reason=empty_recommended_diff` · iterations=2 · `best_pass_dir=/app/results/squeeze-compare-llm/run-12/iteration-2`

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | -20.0 | -10.0 |
| llm | -30.0 | -15.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula repl | llm status | llm cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.4465 | 5 | 0 | 45 | 59 | 25.3 | 100 | 50 | 3 | PASS | 0.4465 | 5 | 0 | 45 | 33.7 | 18 | 100 | 50 | 3 |
| 2 | PASS | 0.4018 | 5 | 0 | 45 | 56.2 | 29.1 | 90 | 45 | 3 | PASS | 0.3125 | 18 | 0 | 45 | 58 | 33 | 70 | 35 | 3 |
| 3 | PASS | 0.2381 | 5 | 0 | 45 | 77.7 | 45.4 | 80 | 40 | 2 | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: formula=3, llm=2.*
