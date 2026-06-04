# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **formula**: `optimizer=formula` · `stopped_reason=recovered_from_underprovisioning` · iterations=9 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-9` · prov_cost_total=755.173625 (steady=755.064, best_pass=1.0487), util_cost_total=237.933318 (steady=237.888, best_pass=0.3304)
- **llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-3` · prov_cost_total=157.185015 (steady=157.176, best_pass=0.2183), util_cost_total=56.669525 (steady=56.664, best_pass=0.0787)

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | +134.0 | +69.0 |
| llm | +65.0 | +33.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula prov cost | formula util cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | llm prov cost | llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0474 | 2284 | 0 | 259.5 | 331.8 | 145.3 | 50 | 25 | 100 | 50 | 1 | FAIL | 0.0474 | 0.0474 | 2205 | 0 | 259.2 | 582.9 | 265.5 | 50 | 25 | 100 | 50 | 1 |
| 2 | FAIL | 0.0949 | 0.0947 | 1522 | 0 | 260 | 101.3 | 96.6 | 50 | 25 | 100 | 50 | 2 | FAIL | 0.0949 | 0.0949 | 491 | 0 | 260 | 213.3 | 108.2 | 100 | 50 | 150 | 75 | 1 |
| 3 | FAIL | 0.1879 | 0.1162 | 516 | 0 | 260 | 62.4 | 52.2 | 66 | 33 | 132 | 66 | 3 | PASS | 0.2183 | 0.0787 | 296 | 0 | 260 | 37.2 | 14.8 | 115 | 58 | 300 | 150 | 2 |
| 4 | FAIL | 0.2924 | 0.1684 | 994 | 0 | 259.8 | 58.5 | 41.1 | 77 | 39 | 153 | 77 | 4 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 5 | FAIL | 0.4509 | 0.1957 | 667 | 0 | 260 | 44.1 | 30.5 | 95 | 48 | 189 | 95 | 5 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 6 | FAIL | 0.6382 | 0.2484 | 603 | 0 | 260 | 39.9 | 21.2 | 112 | 57 | 223 | 112 | 6 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 7 | FAIL | 0.7467 | 0.2908 | 612 | 0 | 260 | 40 | 20 | 131 | 67 | 261 | 131 | 6 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 8 | FAIL | 0.8779 | 0.3207 | 744 | 0 | 260 | 37.5 | 19.1 | 154 | 79 | 305 | 154 | 6 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 9 | PASS | 1.049 | 0.3304 | 489 | 0 | 260 | 32.3 | 17.2 | 184 | 94 | 363 | 184 | 6 | — | — | — | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: formula=9, llm=3.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | formula status | formula prov cost | formula util cost | llm status | llm prov cost | llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0474 | FAIL | 0.0474 | 0.0474 |
| 2 | FAIL | 0.0949 | 0.0947 | FAIL | 0.0949 | 0.0949 |
| 3 | FAIL | 0.1879 | 0.1162 | PASS | 0.2183 | 0.0787 |
| 4 | FAIL | 0.2924 | 0.1684 | — | — | — |
| 5 | FAIL | 0.4509 | 0.1957 | — | — | — |
| 6 | FAIL | 0.6382 | 0.2484 | — | — | — |
| 7 | FAIL | 0.7467 | 0.2908 | — | — | — |
| 8 | FAIL | 0.8779 | 0.3207 | — | — | — |
| 9 | PASS | 1.049 | 0.3304 | — | — | — |
