# Squeeze optimizer comparison

## Summary

- **formula**: `optimizer=formula` · `stopped_reason=recovered_from_underprovisioning` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-formula/run-42/iteration-3`
- **llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=4 · `best_pass_dir=/app/results/squeeze-compare-llm/run-53/iteration-4`

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | +48.0 | +24.0 |
| llm | +175.0 | +87.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula repl | llm status | llm cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0744 | 4506 | 0 | 178.7 | 146.7 | 174.2 | 50 | 25 | 1 | FAIL | 0.0744 | 5097 | 0 | 175.9 | 150.9 | 290.5 | 50 | 25 | 1 |
| 2 | FAIL | 0.1042 | 2115 | 0 | 220 | 88.4 | 171.4 | 70 | 35 | 1 | FAIL | 0.1488 | 4696 | 0 | 176.1 | 139.7 | 245.2 | 100 | 50 | 1 |
| 3 | PASS | 0.1459 | 487 | 0 | 220 | 72.6 | 128.7 | 98 | 49 | 1 | FAIL | 0.2232 | 2468 | 0 | 220 | 76.6 | 160.8 | 150 | 75 | 1 |
| 4 | — | — | — | — | — | — | — | — | — | — | PASS | 0.3344 | 312 | 0 | 220 | 73.9 | 109.7 | 225 | 112 | 1 |

*Iteration count mismatch: formula=3, llm=4.*
