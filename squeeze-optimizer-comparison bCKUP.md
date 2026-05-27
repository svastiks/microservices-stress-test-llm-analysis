# Squeeze optimizer comparison

## Summary

- **formula**: `optimizer=formula` · `stopped_reason=empty_recommended_diff` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-formula/run-5/iteration-3`
- **llm**: `optimizer=llm` · `stopped_reason=empty_recommended_diff` · iterations=4 · `best_pass_dir=/app/results/squeeze-compare-llm/run-5/iteration-4`

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | -35.0 | -17.0 |
| llm | -64.0 | -32.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula repl | llm status | llm cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.4465 | 5 | 0 | 25 | 31.4 | 17.5 | 100 | 50 | 3 | PASS | 0.4465 | 6 | 0 | 25 | 33.5 | 22.5 | 100 | 50 | 3 |
| 2 | PASS | 0.3542 | 5 | 0 | 25 | 41.2 | 21.8 | 79 | 40 | 3 | PASS | 0.3125 | 39 | 0 | 25 | 52 | 33.4 | 70 | 35 | 3 |
| 3 | PASS | 0.1945 | 5 | 0 | 25 | 75.4 | 41.8 | 65 | 33 | 2 | PASS | 0.2322 | 45 | 0 | 25 | 78.1 | 45.9 | 52 | 26 | 3 |
| 4 | — | — | — | — | — | — | — | — | — | — | PASS | 0.1072 | 91 | 0 | 25 | 169.2 | 100.3 | 36 | 18 | 2 |

*Iteration count mismatch: formula=3, llm=4.*
