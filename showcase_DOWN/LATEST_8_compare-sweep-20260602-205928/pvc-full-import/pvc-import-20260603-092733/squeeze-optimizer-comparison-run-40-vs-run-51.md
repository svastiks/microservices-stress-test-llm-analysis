# Squeeze optimizer comparison

## Summary

- **formula**: `optimizer=formula` · `stopped_reason=recovered_from_underprovisioning` · iterations=4 · `best_pass_dir=/app/results/squeeze-compare-formula/run-40/iteration-4`
- **llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=2 · `best_pass_dir=/app/results/squeeze-compare-llm/run-51/iteration-2`

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | +64.0 | +32.0 |
| llm | +50.0 | +39.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula repl | llm status | llm cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0744 | 4920 | 0 | 173.7 | 204.5 | 144.7 | 50 | 25 | 1 | FAIL | 0.0744 | 5526 | 0 | 173.7 | 189.3 | 284.9 | 50 | 25 | 1 |
| 2 | FAIL | 0.1042 | 3263 | 0 | 219.9 | 92.8 | 120.4 | 70 | 35 | 1 | PASS | 0.1625 | 473 | 0 | 220 | 77.3 | 94.2 | 100 | 64 | 1 |
| 3 | FAIL | 0.1459 | 546 | 0 | 220 | 73.7 | 126.8 | 98 | 49 | 1 | — | — | — | — | — | — | — | — | — | — |
| 4 | PASS | 0.1697 | 357 | 0 | 220 | 85.7 | 112.8 | 114 | 57 | 1 | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: formula=4, llm=2.*
