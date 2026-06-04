# Squeeze optimizer comparison

## Summary

- **formula**: `optimizer=formula` · `stopped_reason=recovered_from_underprovisioning` · iterations=4 · `best_pass_dir=/app/results/squeeze-compare-formula/run-36/iteration-4`
- **llm**: `optimizer=llm` · `stopped_reason=first_run_failed` · iterations=1 · `best_pass_dir=None`

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | +65.0 | +33.0 |
| llm | +0.0 | +0.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula repl | llm status | llm cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0744 | 4934 | 0 | 181 | 169.6 | 213.6 | 50 | 25 | 1 | FAIL | 0.0744 | 4769 | 0 | 182.6 | 185.3 | 277.1 | 50 | 25 | 1 |
| 2 | FAIL | 0.1042 | 2736 | 0 | 219.7 | 103.2 | 200.4 | 70 | 35 | 1 | — | — | — | — | — | — | — | — | — | — |
| 3 | FAIL | 0.1459 | 635 | 0 | 220 | 80.5 | 149.9 | 98 | 49 | 1 | — | — | — | — | — | — | — | — | — | — |
| 4 | PASS | 0.1716 | 341 | 0 | 220 | 79.4 | 125.4 | 115 | 58 | 1 | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: formula=4, llm=1.*
