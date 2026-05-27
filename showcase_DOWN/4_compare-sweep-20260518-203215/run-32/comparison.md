# Squeeze optimizer comparison

## Summary

- **formula**: `optimizer=formula` · `stopped_reason=first_fail` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-formula/run-32/iteration-2`
- **llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-llm/run-43/iteration-2`

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | -19.0 | -9.0 |
| llm | -50.0 | -25.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula repl | llm status | llm cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.4465 | 6 | 0 | 25 | 46.5 | 24 | 100 | 50 | 3 | PASS | 0.4465 | 6 | 0 | 25 | 56 | 29.2 | 100 | 50 | 3 |
| 2 | PASS | 0.381 | 15 | 0 | 25 | 68.6 | 35.1 | 85 | 43 | 3 | PASS | 0.3125 | 23 | 0 | 25 | 81.5 | 39 | 70 | 35 | 3 |
| 3 | FAIL | 0.2421 | 10 | 0 | 25 | 110 | 44.6 | 81 | 41 | 2 | FAIL | 0.2232 | 140 | 0 | 25 | 119.5 | 47.7 | 50 | 25 | 3 |
