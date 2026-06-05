# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **formula**: `optimizer=formula` · `stopped_reason=recovered_from_underprovisioning` · iterations=4 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-4` · prov_cost_total=102.68207 (steady=102.672, best_pass=0.1426), util_cost_total=45.72579 (steady=45.72, best_pass=0.0635)
- **llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=2 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-2` · prov_cost_total=95.620505 (steady=95.616, best_pass=0.1328), util_cost_total=41.04261 (steady=41.04, best_pass=0.057)

## Resource delta (first row → last row)

| | 🟩 CPU req (m) | 🟧 Mem req (MiB) |
|---|---:|---:|
| formula | +25.0 | +14.0 |
| llm | +20.0 | +10.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | ⬜ formula prov cost | ⬜ formula util cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | 🟩 formula cpu m | 🟧 formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | ⬜ llm prov cost | ⬜ llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | 🟩 llm cpu m | 🟧 llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0474 | 4035 | 0 | 186.8 | 146.9 | 150.9 | 50 | 25 | 100 | 50 | 1 | FAIL | 0.0474 | 0.0474 | 3145 | 0 | 181.6 | 130.5 | 225.3 | 50 | 25 | 100 | 50 | 1 |
| 2 | FAIL | 0.0949 | 0.0668 | 709 | 0 | 220 | 69.9 | 78.7 | 50 | 25 | 100 | 50 | 2 | PASS | 0.1328 | 0.057 | 269 | 0 | 220 | 42.7 | 46.1 | 70 | 35 | 150 | 75 | 2 |
| 3 | FAIL | 0.1179 | 0.0539 | 546 | 0 | 220 | 45 | 59.3 | 62 | 32 | 123 | 62 | 2 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 4 | PASS | 0.1426 | 0.0635 | 277 | 0 | 220 | 43.3 | 66.5 | 75 | 39 | 148 | 75 | 2 | — | — | — | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: formula=4, llm=2.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | formula status | ⬜ formula prov cost | ⬜ formula util cost | llm status | ⬜ llm prov cost | ⬜ llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0474 | FAIL | 0.0474 | 0.0474 |
| 2 | FAIL | 0.0949 | 0.0668 | PASS | 0.1328 | 0.057 |
| 3 | FAIL | 0.1179 | 0.0539 | — | — | — |
| 4 | PASS | 0.1426 | 0.0635 | — | — | — |
