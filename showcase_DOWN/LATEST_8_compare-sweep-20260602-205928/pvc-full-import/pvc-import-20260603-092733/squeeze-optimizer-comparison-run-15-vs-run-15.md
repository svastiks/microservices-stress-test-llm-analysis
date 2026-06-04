# Squeeze optimizer comparison

## Summary

- **formula**: `optimizer=formula` · `stopped_reason=up_demo_first_pass_overprovisioned` · iterations=1 · `best_pass_dir=/app/results/squeeze-compare-formula/run-15/iteration-1`
- **llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=2 · `best_pass_dir=/app/results/squeeze-compare-llm/run-15/iteration-2`

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | +0.0 | +0.0 |
| llm | +40.0 | +20.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula repl | llm status | llm cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.1488 | 361 | 0 | 232.8 | 76 | 29.2 | 100 | 50 | 1 | FAIL | 0.4465 | 561 | 0 | 238.1 | 29.2 | 17.2 | 100 | 50 | 3 |
| 2 | — | — | — | — | — | — | — | — | — | — | PASS | 0.6251 | 278 | 0 | 240 | 32.6 | 18.8 | 140 | 70 | 3 |

*Iteration count mismatch: formula=1, llm=2.*
