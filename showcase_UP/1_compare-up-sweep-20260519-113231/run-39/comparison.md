# Squeeze optimizer comparison

## Summary

- **formula**: `optimizer=formula` · `stopped_reason=recovered_from_underprovisioning` · iterations=4 · `best_pass_dir=/app/results/squeeze-compare-formula/run-39/iteration-4`
- **llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=2 · `best_pass_dir=/app/results/squeeze-compare-llm/run-50/iteration-2`

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | +67.0 | +34.0 |
| llm | +50.0 | +25.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula repl | llm status | llm cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0744 | 5074 | 0 | 169.5 | 194.3 | 130.7 | 50 | 25 | 1 | FAIL | 0.0744 | 6591 | 0 | 172.7 | 188.2 | 280.7 | 50 | 25 | 1 |
| 2 | FAIL | 0.1042 | 3209 | 0 | 219.6 | 93.7 | 121.3 | 70 | 35 | 1 | PASS | 0.2977 | 220 | 0 | 220 | 51 | 58.1 | 100 | 50 | 2 |
| 3 | FAIL | 0.1459 | 736 | 0 | 220 | 77.8 | 127.8 | 98 | 49 | 1 | — | — | — | — | — | — | — | — | — | — |
| 4 | PASS | 0.1746 | 318 | 0 | 220 | 79.2 | 109.7 | 117 | 59 | 1 | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: formula=4, llm=2.*
