# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **formula**: `optimizer=formula` · `stopped_reason=recovered_from_underprovisioning` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-3` · prov_cost_total=133.352188 (steady=133.344, best_pass=0.1852), util_cost_total=86.550052 (steady=86.544, best_pass=0.1202)
- **llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=4 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-4` · prov_cost_total=88.206503 (steady=88.2, best_pass=0.1225), util_cost_total=53.932662 (steady=53.928, best_pass=0.0749)

## Resource delta (first row → last row)

| | 🟩 CPU req (m) | 🟧 Mem req (MiB) |
|---|---:|---:|
| formula | +15.0 | +8.0 |
| llm | -7.0 | -3.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | ⬜ formula prov cost | ⬜ formula util cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | 🟩 formula cpu m | 🟧 formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | ⬜ llm prov cost | ⬜ llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | 🟩 llm cpu m | 🟧 llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0474 | 1800 | 0 | 240 | 230.3 | 147.9 | 50 | 25 | 100 | 50 | 1 | FAIL | 0.0474 | 0.0474 | 1926 | 0 | 240 | 261 | 198 | 50 | 25 | 100 | 50 | 1 |
| 2 | FAIL | 0.0949 | 0.0745 | 1367 | 0 | 240 | 77.9 | 90.6 | 50 | 25 | 100 | 50 | 2 | FAIL | 0.0237 | 0.0237 | 6e+04 | 0.4603 | 34 | 400.9 | 259.6 | 25 | 12 | 50 | 25 | 1 |
| 3 | PASS | 0.1852 | 0.1202 | 429 | 0 | 240 | 65.5 | 54 | 65 | 33 | 129 | 65 | 3 | FAIL | 0.0665 | 0.0405 | 894 | 0 | 240 | 60.1 | 74.6 | 35 | 18 | 100 | 50 | 2 |
| 4 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.1225 | 0.0749 | 442 | 0 | 240 | 62.4 | 37.4 | 43 | 22 | 150 | 100 | 3 |

*Iteration count mismatch: formula=3, llm=4.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | formula status | ⬜ formula prov cost | ⬜ formula util cost | llm status | ⬜ llm prov cost | ⬜ llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0474 | FAIL | 0.0474 | 0.0474 |
| 2 | FAIL | 0.0949 | 0.0745 | FAIL | 0.0237 | 0.0237 |
| 3 | PASS | 0.1852 | 0.1202 | FAIL | 0.0665 | 0.0405 |
| 4 | — | — | — | PASS | 0.1225 | 0.0749 |
