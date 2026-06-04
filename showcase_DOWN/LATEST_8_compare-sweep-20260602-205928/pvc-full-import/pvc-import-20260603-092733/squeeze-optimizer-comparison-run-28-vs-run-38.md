# Squeeze optimizer comparison

## Summary

- **formula**: `optimizer=formula` · `stopped_reason=first_fail` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-formula/run-28/iteration-2`
- **llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-llm/run-38/iteration-2`

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | -31.0 | -15.0 |
| llm | -40.0 | -20.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula repl | llm status | llm cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.4465 | 6 | 0 | 25 | 38 | 23.5 | 100 | 50 | 3 | PASS | 0.1488 | 6 | 0 | 25 | 81 | 57.7 | 100 | 50 | 1 |
| 2 | PASS | 0.3631 | 43 | 0 | 25 | 48 | 28.9 | 81 | 41 | 3 | PASS | 0.1191 | 6 | 0 | 25 | 81.9 | 56 | 80 | 40 | 1 |
| 3 | FAIL | 0.1032 | 80 | 0 | 25 | 169.3 | 82.1 | 69 | 35 | 1 | FAIL | 0.0893 | 64 | 0 | 25 | 107.2 | 68.9 | 60 | 30 | 1 |
