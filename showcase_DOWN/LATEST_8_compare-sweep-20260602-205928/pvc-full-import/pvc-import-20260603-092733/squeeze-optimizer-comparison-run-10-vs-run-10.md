# Squeeze optimizer comparison

## Summary

- **formula**: `optimizer=formula` · `stopped_reason=empty_recommended_diff` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-formula/run-10/iteration-3`
- **llm**: `optimizer=llm` · `stopped_reason=empty_recommended_diff` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-llm/run-10/iteration-3`

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | -33.0 | -16.0 |
| llm | -44.0 | -22.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula repl | llm status | llm cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.4465 | 5 | 0 | 25 | 33.5 | 17.7 | 100 | 50 | 3 | PASS | 0.4465 | 6 | 0 | 25 | 35.7 | 17.8 | 100 | 50 | 3 |
| 2 | PASS | 0.3542 | 5 | 0 | 25 | 45.5 | 23.5 | 79 | 40 | 3 | PASS | 0.3572 | 5 | 0 | 25 | 53.9 | 23.3 | 80 | 40 | 3 |
| 3 | PASS | 0.2004 | 6 | 0 | 25 | 84 | 41.4 | 67 | 34 | 2 | PASS | 0.1667 | 11 | 0 | 25 | 124.3 | 50.9 | 56 | 28 | 2 |
