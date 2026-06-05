# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **formula**: `optimizer=formula` · `stopped_reason=recovered_from_underprovisioning` · iterations=6 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-6` · prov_cost_total=607.087642 (steady=607.032, best_pass=0.8431), util_cost_total=196.58132 (steady=196.56, best_pass=0.273)
- **llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=4 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-4` · prov_cost_total=327.910438 (steady=327.888, best_pass=0.4554), util_cost_total=107.289905 (steady=107.28, best_pass=0.149)

## Resource delta (first row → last row)

| | 🟩 CPU req (m) | 🟧 Mem req (MiB) |
|---|---:|---:|
| formula | +98.0 | +50.0 |
| llm | +70.0 | +35.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | ⬜ formula prov cost | ⬜ formula util cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | 🟩 formula cpu m | 🟧 formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | ⬜ llm prov cost | ⬜ llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | 🟩 llm cpu m | 🟧 llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0474 | 5213 | 0 | 196.6 | 153.7 | 181.8 | 50 | 25 | 100 | 50 | 1 | FAIL | 0.0474 | 0.0474 | 4728 | 0 | 186.1 | 533.7 | 191.5 | 50 | 25 | 100 | 50 | 1 |
| 2 | FAIL | 0.1328 | 0.0688 | 1118 | 0 | 260 | 51.1 | 65.2 | 70 | 35 | 139 | 70 | 2 | FAIL | 0.1328 | 0.099 | 1490 | 0 | 258.7 | 76 | 47.8 | 70 | 35 | 200 | 100 | 2 |
| 3 | FAIL | 0.2505 | 0.0942 | 556 | 0 | 260 | 37.2 | 45.4 | 88 | 44 | 174 | 88 | 3 | FAIL | 0.2619 | 0.1008 | 1414 | 0 | 258.8 | 38.5 | 38.7 | 92 | 46 | 200 | 100 | 3 |
| 4 | FAIL | 0.3871 | 0.1549 | 591 | 0 | 260 | 40.6 | 29 | 102 | 51 | 202 | 102 | 4 | PASS | 0.4554 | 0.149 | 384 | 0 | 260 | 33.4 | 20.3 | 120 | 60 | 250 | 150 | 4 |
| 5 | FAIL | 0.5648 | 0.2145 | 1059 | 0 | 260 | 38.9 | 21 | 119 | 60 | 236 | 119 | 5 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 6 | PASS | 0.8431 | 0.273 | 305 | 0 | 260 | 33.2 | 17.4 | 148 | 75 | 293 | 148 | 6 | — | — | — | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: formula=6, llm=4.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | formula status | ⬜ formula prov cost | ⬜ formula util cost | llm status | ⬜ llm prov cost | ⬜ llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0474 | FAIL | 0.0474 | 0.0474 |
| 2 | FAIL | 0.1328 | 0.0688 | FAIL | 0.1328 | 0.099 |
| 3 | FAIL | 0.2505 | 0.0942 | FAIL | 0.2619 | 0.1008 |
| 4 | FAIL | 0.3871 | 0.1549 | PASS | 0.4554 | 0.149 |
| 5 | FAIL | 0.5648 | 0.2145 | — | — | — |
| 6 | PASS | 0.8431 | 0.273 | — | — | — |
