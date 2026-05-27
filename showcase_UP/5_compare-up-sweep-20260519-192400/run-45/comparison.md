# Squeeze optimizer comparison

## Summary

- **formula**: `optimizer=formula` · `stopped_reason=unknown` · iterations=13 · `best_pass_dir=None`
- **llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-llm/run-55/iteration-3`

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | +1155.0 | +597.0 |
| llm | +44.0 | +22.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula repl | llm status | llm cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0744 | 5522 | 0 | 185.1 | 142 | 171.6 | 50 | 25 | 1 | FAIL | 0.0744 | 4831 | 0 | 177.2 | 184.4 | 282.9 | 50 | 25 | 1 |
| 2 | FAIL | 0.1042 | 3389 | 0 | 240.9 | 84.2 | 167.8 | 70 | 35 | 1 | FAIL | 0.1042 | 1633 | 0 | 220 | 97.5 | 158.5 | 70 | 35 | 1 |
| 3 | FAIL | 0.1459 | 1771 | 0 | 259.8 | 74.9 | 138.7 | 98 | 49 | 1 | PASS | 0.1399 | 423 | 0 | 220 | 69.6 | 110.7 | 94 | 47 | 1 |
| 4 | FAIL | 0.1984 | 1063 | 0 | 259.7 | 70.2 | 114.6 | 133 | 67 | 1 | — | — | — | — | — | — | — | — | — | — |
| 5 | FAIL | 0.247 | 851 | 0 | 258 | 69.1 | 83.9 | 165 | 84 | 1 | — | — | — | — | — | — | — | — | — | — |
| 6 | FAIL | 0.2986 | 1128 | 0 | 241.1 | 67.3 | 68 | 199 | 102 | 1 | — | — | — | — | — | — | — | — | — | — |
| 7 | FAIL | 0.374 | 1680 | 0 | 242.5 | 61.5 | 54.1 | 249 | 128 | 1 | — | — | — | — | — | — | — | — | — | — |
| 8 | FAIL | 0.502 | 1065 | 0 | 249.6 | 48.5 | 37.1 | 334 | 172 | 1 | — | — | — | — | — | — | — | — | — | — |
| 9 | FAIL | 0.624 | 1662 | 0 | 251.2 | 42.5 | 26.5 | 415 | 214 | 1 | — | — | — | — | — | — | — | — | — | — |
| 10 | FAIL | 0.8343 | 1401 | 0 | 254.5 | 34 | 19.4 | 555 | 286 | 1 | — | — | — | — | — | — | — | — | — | — |
| 11 | FAIL | 1.081 | 1453 | 0 | 259.3 | 26.2 | 13 | 719 | 371 | 1 | — | — | — | — | — | — | — | — | — | — |
| 12 | FAIL | 1.41 | 1341 | 0 | 259.4 | 21.1 | 10.1 | 937 | 484 | 1 | — | — | — | — | — | — | — | — | — | — |
| 13 | FAIL | 1.812 | 1132 | 0 | 259.3 | 16.8 | 9 | 1205 | 622 | 1 | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: formula=13, llm=3.*
