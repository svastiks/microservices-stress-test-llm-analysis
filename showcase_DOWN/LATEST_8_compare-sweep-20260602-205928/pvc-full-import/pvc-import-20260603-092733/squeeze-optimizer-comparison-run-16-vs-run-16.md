# Squeeze optimizer comparison

## Summary

- **formula**: `optimizer=formula` · `stopped_reason=first_run_failed` · iterations=1 · `best_pass_dir=None`
- **llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=4 · `best_pass_dir=/app/results/squeeze-compare-llm/run-16/iteration-4`

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | +0.0 | +0.0 |
| llm | +127.0 | +37.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula repl | llm status | llm cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.4465 | 800 | 0 | 260 | 56.5 | 16.7 | 100 | 50 | 3 | FAIL | 0.4465 | 1576 | 0 | 260 | 43.3 | 18.4 | 100 | 50 | 3 |
| 2 | — | — | — | — | — | — | — | — | — | — | FAIL | 0.9277 | 929 | 0 | 257.8 | 18.3 | 20.2 | 125 | 62 | 5 |
| 3 | — | — | — | — | — | — | — | — | — | — | FAIL | 1.3 | 539 | 0 | 260 | 19.7 | 16 | 175 | 87 | 5 |
| 4 | — | — | — | — | — | — | — | — | — | — | PASS | 1.56 | 472 | 0 | 260 | 24.8 | 17.4 | 227 | 87 | 5 |

*Iteration count mismatch: formula=1, llm=4.*
