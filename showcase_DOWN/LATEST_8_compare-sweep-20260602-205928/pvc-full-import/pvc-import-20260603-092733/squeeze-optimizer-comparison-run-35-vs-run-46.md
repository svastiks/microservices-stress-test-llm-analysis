# Squeeze optimizer comparison

## Summary

- **formula**: `optimizer=formula` · `stopped_reason=up_demo_first_pass_overprovisioned` · iterations=1 · `best_pass_dir=/app/results/squeeze-compare-formula/run-35/iteration-1`
- **llm**: `optimizer=llm` · `stopped_reason=up_demo_first_pass_overprovisioned` · iterations=1 · `best_pass_dir=/app/results/squeeze-compare-llm/run-46/iteration-1`

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | +0.0 | +0.0 |
| llm | +0.0 | +0.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula repl | llm status | llm cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.2232 | 219 | 0 | 220 | 93.8 | 31 | 150 | 75 | 1 | PASS | 0.2133 | 264 | 0 | 220 | 41.9 | 40 | 143 | 72 | 1 |
