# Squeeze optimizer comparison

## Summary

- **formula**: `optimizer=formula` · `stopped_reason=up_demo_first_pass_overprovisioned` · iterations=1 · `best_pass_dir=/app/results/squeeze-compare-formula/run-23/iteration-1`
- **llm**: `optimizer=llm` · `stopped_reason=up_demo_first_pass_overprovisioned` · iterations=1 · `best_pass_dir=/app/results/squeeze-compare-llm/run-23/iteration-1`

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | +0.0 | +0.0 |
| llm | +0.0 | +0.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula repl | llm status | llm cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.4465 | 135 | 0 | 160 | 54.6 | 16.7 | 100 | 50 | 3 | PASS | 0.4465 | 269 | 0 | 160 | 39.1 | 15.3 | 100 | 50 | 3 |
