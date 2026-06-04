# Squeeze optimizer comparison

## Summary

- **formula**: `optimizer=formula` · `stopped_reason=empty_recommended_diff` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-formula/run-19/iteration-3`
- **llm**: `optimizer=llm` · `stopped_reason=empty_recommended_diff` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-llm/run-19/iteration-3`

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | -22.0 | -11.0 |
| llm | -44.0 | -22.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula repl | llm status | llm cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.4465 | 5 | 0 | 35 | 53.1 | 29.6 | 100 | 50 | 3 | PASS | 0.4465 | 5 | 0 | 35 | 33.7 | 17.9 | 100 | 50 | 3 |
| 2 | PASS | 0.3929 | 5 | 0 | 35 | 54.5 | 34.6 | 88 | 44 | 3 | PASS | 0.3125 | 5 | 0 | 35 | 58.2 | 26.9 | 70 | 35 | 3 |
| 3 | PASS | 0.2322 | 5 | 0 | 35 | 82 | 47.2 | 78 | 39 | 2 | PASS | 0.1667 | 14 | 0 | 35 | 117.6 | 49.4 | 56 | 28 | 2 |
