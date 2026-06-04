# Squeeze optimizer comparison

## Summary

- **formula**: `optimizer=formula` · `stopped_reason=first_fail` · iterations=10 · `best_pass_dir=/app/results/squeeze-compare-formula/run-27/iteration-9`
- **llm**: `optimizer=llm` · `stopped_reason=empty_recommended_diff` · iterations=2 · `best_pass_dir=/app/results/squeeze-compare-llm/run-30/iteration-2`

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | -43.0 | -18.0 |
| llm | +0.0 | +0.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula repl | llm status | llm cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.4465 | 6 | 0 | 25 | 51.4 | 18 | 100 | 50 | 3 | PASS | 0.4465 | 6 | 0 | 25 | 43.1 | 31 | 100 | 50 | 3 |
| 2 | PASS | 0.3899 | 28 | 0 | 25 | 59.1 | 20.5 | 87 | 44 | 3 | PASS | 0.4465 | 6 | 0 | 25 | 51 | 30.3 | 100 | 50 | 3 |
| 3 | PASS | 0.2341 | 57 | 0 | 25 | 93 | 46.3 | 78 | 40 | 2 | — | — | — | — | — | — | — | — | — | — |
| 4 | PASS | 0.2242 | 49 | 0 | 25 | 83.6 | 50.2 | 75 | 38 | 2 | — | — | — | — | — | — | — | — | — | — |
| 5 | PASS | 0.2163 | 38 | 0 | 25 | 86.4 | 52.4 | 72 | 37 | 2 | — | — | — | — | — | — | — | — | — | — |
| 6 | PASS | 0.2083 | 91 | 0 | 25 | 90.9 | 64.7 | 69 | 36 | 2 | — | — | — | — | — | — | — | — | — | — |
| 7 | PASS | 0.2004 | 94 | 0 | 25 | 90.4 | 56.3 | 66 | 35 | 2 | — | — | — | — | — | — | — | — | — | — |
| 8 | PASS | 0.1924 | 109 | 0 | 25 | 85.7 | 73.4 | 63 | 34 | 2 | — | — | — | — | — | — | — | — | — | — |
| 9 | PASS | 0.1845 | 99 | 0 | 25 | 94.7 | 65.1 | 60 | 33 | 2 | — | — | — | — | — | — | — | — | — | — |
| 10 | FAIL | 0.1765 | 174 | 0 | 25 | 98.9 | 79.1 | 57 | 32 | 2 | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: formula=10, llm=2.*
