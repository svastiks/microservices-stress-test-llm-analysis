# Squeeze optimizer comparison

## Summary

- **formula**: `optimizer=formula` · `stopped_reason=recovered_from_underprovisioning` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-3`
- **llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-3`

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | +14.0 | +7.0 |
| llm | +31.0 | +16.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | llm cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0744 | 2734 | 0 | 278.9 | 444.7 | 158.6 | 50 | 25 | 100 | 50 | 1 | FAIL | 0.0744 | 3153 | 0 | 278 | 256.2 | 189.6 | 50 | 25 | 100 | 50 | 1 |
| 2 | FAIL | 0.1488 | 1254 | 0 | 280 | 121.2 | 95.1 | 50 | 25 | 100 | 50 | 2 | FAIL | 0.2084 | 515 | 0 | 280 | 22 | 12.7 | 70 | 35 | 400 | 300 | 2 |
| 3 | PASS | 0.2858 | 498 | 0 | 280 | 64.4 | 56.9 | 64 | 32 | 128 | 64 | 3 | PASS | 0.3631 | 420 | 0 | 280 | 17.7 | 4.6 | 81 | 41 | 600 | 450 | 3 |
