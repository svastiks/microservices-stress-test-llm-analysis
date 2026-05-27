# Squeeze optimizer comparison

## Summary

- **formula**: `optimizer=formula` · `stopped_reason=recovered_from_underprovisioning` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-3`
- **llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=2 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-2`

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | +33.0 | +17.0 |
| llm | +20.0 | +10.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula repl | llm status | llm cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0744 | 5669 | 0 | 174.1 | 223.9 | 131.8 | 50 | 25 | 1 | FAIL | 0.0744 | 5689 | 0 | 178.5 | 307.6 | 155.1 | 50 | 25 | 1 |
| 2 | FAIL | 0.2084 | 698 | 0 | 260 | 60.2 | 79.1 | 70 | 35 | 2 | PASS | 0.2084 | 316 | 0 | 260 | 52.6 | 51.5 | 70 | 35 | 2 |
| 3 | PASS | 0.372 | 415 | 0 | 260 | 65.7 | 54.7 | 83 | 42 | 3 | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: formula=3, llm=2.*
