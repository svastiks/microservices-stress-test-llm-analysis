# Squeeze optimizer comparison

## Summary

- **formula**: `optimizer=formula` · `stopped_reason=first_fail` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-formula/run-26/iteration-2`
- **llm**: `optimizer=llm` · `stopped_reason=no_progress` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-llm/run-29/iteration-3`

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | -31.0 | -15.0 |
| llm | +0.0 | +0.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula repl | llm status | llm cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.4465 | 6 | 0 | 25 | 31 | 23.7 | 100 | 50 | 3 | PASS | 0.4465 | 6 | 0 | 25 | 43 | 24.6 | 100 | 50 | 3 |
| 2 | PASS | 0.3483 | 5 | 0 | 25 | 53.4 | 31.2 | 78 | 39 | 3 | PASS | 0.4465 | 6 | 0 | 25 | 48 | 24.5 | 100 | 50 | 3 |
| 3 | FAIL | 0.2064 | 51 | 0 | 25 | 96 | 52 | 69 | 35 | 2 | PASS | 0.2977 | 6 | 0 | 25 | 75.8 | 27.5 | 100 | 50 | 2 |
