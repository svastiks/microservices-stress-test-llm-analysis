# Squeeze optimizer comparison

## Summary

- **formula**: `optimizer=formula` · `stopped_reason=recovered_from_underprovisioning` · iterations=4 · `best_pass_dir=/app/results/squeeze-compare-formula/run-43/iteration-4`
- **llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=4 · `best_pass_dir=/app/results/squeeze-compare-llm/run-54/iteration-4`

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | +63.0 | +32.0 |
| llm | +88.0 | +45.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula repl | llm status | llm cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0744 | 4166 | 0 | 192.5 | 171.3 | 225.5 | 50 | 25 | 1 | FAIL | 0.0744 | 4839 | 0 | 176.8 | 192.4 | 279.6 | 50 | 25 | 1 |
| 2 | FAIL | 0.1042 | 2449 | 0 | 219.9 | 106 | 204.9 | 70 | 35 | 1 | FAIL | 0.1042 | 2565 | 0 | 220 | 106.5 | 166.7 | 70 | 35 | 1 |
| 3 | FAIL | 0.1459 | 502 | 0 | 220 | 75.8 | 151.5 | 98 | 49 | 1 | FAIL | 0.1459 | 533 | 0 | 220 | 75.5 | 80.2 | 98 | 49 | 1 |
| 4 | PASS | 0.1687 | 338 | 0 | 220 | 82.5 | 127.6 | 113 | 57 | 1 | PASS | 0.2064 | 240 | 0 | 220 | 69.5 | 57.7 | 138 | 70 | 1 |
