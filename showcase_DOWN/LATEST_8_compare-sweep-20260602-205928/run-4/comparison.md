# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **formula**: `optimizer=formula` · `stopped_reason=first_fail` · iterations=16 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-15` · prov_cost_total=138.72518 (steady=138.6, best_pass=0.1925), util_cost_total=95.180845 (steady=95.112, best_pass=0.1321)
- **llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=4 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-3` · prov_cost_total=256.075285 (steady=256.032, best_pass=0.3556), util_cost_total=156.04296 (steady=156.024, best_pass=0.2167)

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | -100.0 | -43.0 |
| llm | -100.0 | -50.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula prov cost | formula util cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | llm prov cost | llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1515 | 6 | 0 | 55 | 21.9 | 9.9 | 150 | 75 | 300 | 150 | 5 | PASS | 0.7116 | 0.1494 | 6 | 0 | 55 | 21.3 | 15.3 | 150 | 75 | 300 | 150 | 5 |
| 2 | PASS | 0.5313 | 0.2124 | 6 | 0 | 55 | 41.1 | 19.4 | 112 | 56 | 223 | 112 | 5 | PASS | 0.4744 | 0.2059 | 6 | 0 | 55 | 44.4 | 25 | 100 | 50 | 200 | 100 | 5 |
| 3 | PASS | 0.4365 | 0.2193 | 6 | 0 | 55 | 51.5 | 27.2 | 92 | 46 | 184 | 92 | 5 | PASS | 0.3556 | 0.2167 | 25 | 0 | 55 | 62.4 | 33.6 | 75 | 37 | 150 | 75 | 5 |
| 4 | PASS | 0.3795 | 0.1819 | 12 | 0 | 55 | 48.8 | 31.6 | 80 | 40 | 160 | 80 | 5 | FAIL | 0.1898 | 0.1864 | 53 | 0 | 55 | 103.6 | 65.3 | 50 | 25 | 100 | 50 | 4 |
| 5 | PASS | 0.3276 | 0.187 | 32 | 0 | 55 | 58.5 | 31.4 | 69 | 35 | 137 | 69 | 5 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 6 | PASS | 0.2946 | 0.1851 | 41 | 0 | 55 | 64.1 | 39.9 | 62 | 32 | 123 | 62 | 5 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 7 | PASS | 0.2811 | 0.1764 | 62 | 0 | 55 | 64.3 | 36.5 | 59 | 32 | 117 | 59 | 5 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 8 | PASS | 0.2721 | 0.176 | 58 | 0 | 55 | 65.9 | 44.6 | 57 | 32 | 112 | 57 | 5 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 9 | PASS | 0.2631 | 0.174 | 50 | 0 | 55 | 67.8 | 39.5 | 55 | 32 | 107 | 55 | 5 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 10 | PASS | 0.2541 | 0.1758 | 60 | 0 | 55 | 70.6 | 47.6 | 53 | 32 | 102 | 53 | 5 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 11 | PASS | 0.2451 | 0.1761 | 79 | 0 | 55 | 73.8 | 42.9 | 51 | 32 | 97 | 51 | 5 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 12 | PASS | 0.2406 | 0.1765 | 74 | 0 | 55 | 75.4 | 44.1 | 50 | 32 | 93 | 49 | 5 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 13 | PASS | 0.2406 | 0.1503 | 89 | 0 | 55 | 63.5 | 47.8 | 50 | 32 | 93 | 49 | 5 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 14 | PASS | 0.1925 | 0.1446 | 152 | 0 | 55 | 77.2 | 45.4 | 50 | 32 | 78 | 42 | 4 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 15 | PASS | 0.1925 | 0.1321 | 267 | 0 | 55 | 70.8 | 37.4 | 50 | 32 | 78 | 42 | 4 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 16 | FAIL | 0.1444 | 0.1348 | 219 | 0 | 55 | 95.7 | 60.3 | 50 | 32 | 65 | 36 | 3 | — | — | — | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: formula=16, llm=4.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | formula status | formula prov cost | formula util cost | llm status | llm prov cost | llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1515 | PASS | 0.7116 | 0.1494 |
| 2 | PASS | 0.5313 | 0.2124 | PASS | 0.4744 | 0.2059 |
| 3 | PASS | 0.4365 | 0.2193 | PASS | 0.3556 | 0.2167 |
| 4 | PASS | 0.3795 | 0.1819 | FAIL | 0.1898 | 0.1864 |
| 5 | PASS | 0.3276 | 0.187 | — | — | — |
| 6 | PASS | 0.2946 | 0.1851 | — | — | — |
| 7 | PASS | 0.2811 | 0.1764 | — | — | — |
| 8 | PASS | 0.2721 | 0.176 | — | — | — |
| 9 | PASS | 0.2631 | 0.174 | — | — | — |
| 10 | PASS | 0.2541 | 0.1758 | — | — | — |
| 11 | PASS | 0.2451 | 0.1761 | — | — | — |
| 12 | PASS | 0.2406 | 0.1765 | — | — | — |
| 13 | PASS | 0.2406 | 0.1503 | — | — | — |
| 14 | PASS | 0.1925 | 0.1446 | — | — | — |
| 15 | PASS | 0.1925 | 0.1321 | — | — | — |
| 16 | FAIL | 0.1444 | 0.1348 | — | — | — |
