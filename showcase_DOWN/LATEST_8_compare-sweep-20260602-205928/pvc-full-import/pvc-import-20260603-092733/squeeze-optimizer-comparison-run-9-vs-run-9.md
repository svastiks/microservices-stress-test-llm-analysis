# Squeeze optimizer comparison

## Summary

- **formula**: `optimizer=formula` · `stopped_reason=empty_recommended_diff` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-formula/run-9/iteration-3`
- **llm**: `optimizer=llm` · `stopped_reason=empty_recommended_diff` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-llm/run-9/iteration-3`

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | -14.0 | -7.0 |
| llm | -51.0 | -26.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula repl | llm status | llm cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.4465 | 5 | 0 | 15 | 59 | 23 | 100 | 50 | 3 | PASS | 0.4465 | 5 | 0 | 15 | 33.1 | 17.3 | 100 | 50 | 3 |
| 2 | PASS | 0.4018 | 5 | 0 | 15 | 60.8 | 26.5 | 90 | 45 | 3 | PASS | 0.3125 | 5 | 0 | 15 | 50.8 | 24.7 | 70 | 35 | 3 |
| 3 | PASS | 0.256 | 5 | 0 | 15 | 74.6 | 40.7 | 86 | 43 | 2 | PASS | 0.1449 | 40 | 0 | 15 | 118.5 | 56.2 | 49 | 24 | 2 |
