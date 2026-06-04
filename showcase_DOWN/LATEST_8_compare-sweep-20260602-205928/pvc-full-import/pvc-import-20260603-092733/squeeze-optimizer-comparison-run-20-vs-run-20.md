# Squeeze optimizer comparison

## Summary

- **formula**: `optimizer=formula` · `stopped_reason=empty_recommended_diff` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-formula/run-20/iteration-3`
- **llm**: `optimizer=llm` · `stopped_reason=empty_recommended_diff` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-llm/run-20/iteration-3`

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | -34.0 | -17.0 |
| llm | -51.0 | -22.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula repl | llm status | llm cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.4465 | 4 | 0 | 45 | 33.9 | 17.5 | 100 | 50 | 3 | PASS | 0.4465 | 5 | 0 | 45 | 32.2 | 18.1 | 100 | 50 | 3 |
| 2 | PASS | 0.3572 | 5 | 0 | 45 | 41.1 | 21.6 | 80 | 40 | 3 | PASS | 0.3272 | 5 | 0 | 45 | 57.1 | 23.5 | 70 | 40 | 3 |
| 3 | PASS | 0.1965 | 9 | 0 | 45 | 75.9 | 41 | 66 | 33 | 2 | PASS | 0.1527 | 69 | 0 | 45 | 124.6 | 50.1 | 49 | 28 | 2 |
