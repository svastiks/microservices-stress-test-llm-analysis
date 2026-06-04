# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **formula**: `optimizer=formula` · `stopped_reason=recovered_from_underprovisioning` · iterations=10 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-10` · prov_cost_total=1312.684723 (steady=1312.488, best_pass=1.8229), util_cost_total=210.942768 (steady=210.888, best_pass=0.2929)
- **llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=6 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-6` · prov_cost_total=647.697735 (steady=647.64, best_pass=0.8995), util_cost_total=105.784418 (steady=105.768, best_pass=0.1469)

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | +270.0 | +137.0 |
| llm | +108.0 | +54.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula prov cost | formula util cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | llm prov cost | llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0474 | 5559 | 0 | 178.8 | 184.6 | 152.8 | 50 | 25 | 100 | 50 | 1 | FAIL | 0.0474 | 0.0474 | 4888 | 0 | 168.8 | 425.1 | 213 | 50 | 25 | 100 | 50 | 1 |
| 2 | FAIL | 0.1328 | 0.0905 | 785 | 0 | 260 | 67.5 | 79.2 | 70 | 35 | 139 | 70 | 2 | FAIL | 0.1328 | 0.0727 | 1301 | 0 | 259.3 | 55.5 | 39.8 | 70 | 35 | 200 | 128 | 2 |
| 3 | FAIL | 0.2391 | 0.1523 | 516 | 0 | 260 | 64.1 | 56.6 | 84 | 42 | 167 | 84 | 3 | FAIL | 0.2562 | 0.1219 | 520 | 0 | 260 | 48.9 | 23 | 90 | 45 | 250 | 192 | 3 |
| 4 | FAIL | 0.3683 | 0.1915 | 556 | 0 | 260 | 53.1 | 31.8 | 97 | 49 | 193 | 97 | 4 | FAIL | 0.3947 | 0.137 | 631 | 0 | 260 | 36 | 10.9 | 104 | 52 | 300 | 256 | 4 |
| 5 | FAIL | 0.5363 | 0.2114 | 1413 | 0 | 259 | 40.3 | 23.1 | 113 | 57 | 224 | 113 | 5 | FAIL | 0.5788 | 0.1308 | 1385 | 0 | 259.2 | 23.4 | 8 | 122 | 61 | 400 | 300 | 5 |
| 6 | FAIL | 0.8372 | 0.2682 | 825 | 0 | 260 | 32.8 | 18.1 | 147 | 74 | 291 | 147 | 6 | PASS | 0.8995 | 0.1469 | 311 | 0 | 260 | 16.9 | 5.8 | 158 | 79 | 600 | 450 | 6 |
| 7 | FAIL | 1.008 | 0.3022 | 1533 | 0 | 258.6 | 30.7 | 16.8 | 177 | 89 | 350 | 177 | 6 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 8 | FAIL | 1.327 | 0.3151 | 588 | 0 | 260 | 24.3 | 13.5 | 233 | 118 | 461 | 233 | 6 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 9 | FAIL | 1.55 | 0.3192 | 642 | 0.001 | 260 | 21.1 | 11.5 | 272 | 138 | 537 | 272 | 6 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 10 | PASS | 1.823 | 0.2929 | 389 | 0 | 260 | 16.4 | 10 | 320 | 162 | 630 | 320 | 6 | — | — | — | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: formula=10, llm=6.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | formula status | formula prov cost | formula util cost | llm status | llm prov cost | llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0474 | FAIL | 0.0474 | 0.0474 |
| 2 | FAIL | 0.1328 | 0.0905 | FAIL | 0.1328 | 0.0727 |
| 3 | FAIL | 0.2391 | 0.1523 | FAIL | 0.2562 | 0.1219 |
| 4 | FAIL | 0.3683 | 0.1915 | FAIL | 0.3947 | 0.137 |
| 5 | FAIL | 0.5363 | 0.2114 | FAIL | 0.5788 | 0.1308 |
| 6 | FAIL | 0.8372 | 0.2682 | PASS | 0.8995 | 0.1469 |
| 7 | FAIL | 1.008 | 0.3022 | — | — | — |
| 8 | FAIL | 1.327 | 0.3151 | — | — | — |
| 9 | FAIL | 1.55 | 0.3192 | — | — | — |
| 10 | PASS | 1.823 | 0.2929 | — | — | — |
