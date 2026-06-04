# Squeeze optimizer comparison

## Summary

- **formula**: `optimizer=formula` · `stopped_reason=recovered_from_underprovisioning` · iterations=4 · `best_pass_dir=/app/results/squeeze-compare-formula/run-44/iteration-4`
- **llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-llm/run-55/iteration-3`

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | +71.0 | +36.0 |
| llm | +44.0 | +22.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula repl | llm status | llm cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0744 | 5000 | 0 | 173.4 | 144.7 | 157.2 | 50 | 25 | 1 | FAIL | 0.0744 | 4831 | 0 | 177.2 | 184.4 | 282.9 | 50 | 25 | 1 |
| 2 | FAIL | 0.1042 | 3674 | 0 | 219.5 | 87.2 | 159.4 | 70 | 35 | 1 | FAIL | 0.1042 | 1633 | 0 | 220 | 97.5 | 158.5 | 70 | 35 | 1 |
| 3 | FAIL | 0.1459 | 1024 | 0 | 220 | 74.8 | 128.9 | 98 | 49 | 1 | PASS | 0.1399 | 423 | 0 | 220 | 69.6 | 110.7 | 94 | 47 | 1 |
| 4 | PASS | 0.1806 | 280 | 0 | 220 | 74.9 | 107.1 | 121 | 61 | 1 | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: formula=4, llm=3.*
