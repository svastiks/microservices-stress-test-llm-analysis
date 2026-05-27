# Squeeze optimizer comparison

## Summary

- **formula**: `optimizer=formula` · `stopped_reason=recovered_from_underprovisioning` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-3`
- **llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=2 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-2`

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | +13.0 | +7.0 |
| llm | +13.0 | +7.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | llm cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0744 | 1658 | 0 | 220 | 213 | 147.5 | 50 | 25 | 100 | 50 | 1 | FAIL | 0.0744 | 1157 | 0 | 220 | 269.4 | 183.1 | 50 | 25 | 100 | 50 | 1 |
| 2 | FAIL | 0.1488 | 1100 | 0 | 220 | 72 | 84.6 | 50 | 25 | 100 | 50 | 2 | PASS | 0.1885 | 246 | 0 | 220 | 46.5 | 41.3 | 63 | 32 | 200 | 100 | 2 |
| 3 | PASS | 0.2828 | 382 | 0 | 220 | 65.3 | 50.6 | 63 | 32 | 125 | 63 | 3 | — | — | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: formula=3, llm=2.*
