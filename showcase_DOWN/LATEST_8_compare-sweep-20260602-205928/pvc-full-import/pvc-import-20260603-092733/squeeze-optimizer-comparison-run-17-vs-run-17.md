# Squeeze optimizer comparison

## Summary

- **formula**: `optimizer=formula` · `stopped_reason=empty_recommended_diff` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-formula/run-17/iteration-3`
- **llm**: `optimizer=llm` · `stopped_reason=empty_recommended_diff` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-llm/run-17/iteration-3`

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | -34.0 | -16.0 |
| llm | -51.0 | -26.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula repl | llm status | llm cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.4465 | 5 | 0 | 15 | 28 | 17.2 | 100 | 50 | 3 | PASS | 0.4465 | 6 | 0 | 15 | 35.4 | 17.4 | 100 | 50 | 3 |
| 2 | PASS | 0.3453 | 5 | 0 | 15 | 47.7 | 23.2 | 77 | 39 | 3 | PASS | 0.3125 | 6 | 0 | 15 | 53.4 | 26.1 | 70 | 35 | 3 |
| 3 | PASS | 0.1984 | 6 | 0 | 15 | 89.2 | 41.6 | 66 | 34 | 2 | PASS | 0.1449 | 48 | 0 | 15 | 116.2 | 57.3 | 49 | 24 | 2 |
