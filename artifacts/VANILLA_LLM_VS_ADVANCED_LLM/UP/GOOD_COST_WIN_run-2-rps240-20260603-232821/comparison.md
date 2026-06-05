# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **advanced-llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-advanced-llm/run-1/iteration-3` · prov_cost_total=88.350972 (steady=88.344, best_pass=0.1227), util_cost_total=50.83753 (steady=50.832, best_pass=0.0706)
- **vanilla-llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=2 · `best_pass_dir=/app/results/squeeze-compare-vanilla-llm/run-1/iteration-2` · prov_cost_total=135.22188 (steady=135.216, best_pass=0.1878), util_cost_total=72.075678 (steady=72.072, best_pass=0.1001)

## Resource delta (first row → last row)

| | 🟩 CPU req (m) | 🟧 Mem req (MiB) |
|---|---:|---:|
| advanced-llm | +15.0 | +4.0 |
| vanilla-llm | +50.0 | +15.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | advanced-llm status | ⬜ advanced-llm prov cost | ⬜ advanced-llm util cost | advanced-llm p95 | advanced-llm err | advanced-llm ach RPS | advanced-llm cpu% | advanced-llm mem% | 🟩 advanced-llm cpu m | 🟧 advanced-llm mem Mi | advanced-llm cpu lim | advanced-llm mem lim | advanced-llm repl | vanilla-llm status | ⬜ vanilla-llm prov cost | ⬜ vanilla-llm util cost | vanilla-llm p95 | vanilla-llm err | vanilla-llm ach RPS | vanilla-llm cpu% | vanilla-llm mem% | 🟩 vanilla-llm cpu m | 🟧 vanilla-llm mem Mi | vanilla-llm cpu lim | vanilla-llm mem lim | vanilla-llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0949 | 0.0894 | 4574 | 0 | 237.7 | 97.2 | 39.7 | 50 | 25 | 100 | 50 | 2 | FAIL | 0.0474 | 0.047 | 2978 | 0 | 235.9 | 137.9 | 83.6 | 50 | 25 | 100 | 50 | 1 |
| 2 | FAIL | 0.0613 | 0.0612 | 996 | 0 | 240 | 160.1 | 96.1 | 65 | 29 | 115 | 58 | 1 | PASS | 0.1878 | 0.1001 | 251 | 0 | 240 | 54 | 37.7 | 100 | 40 | 150 | 60 | 2 |
| 3 | PASS | 0.1227 | 0.0706 | 285 | 0 | 240 | 57.6 | 56.3 | 65 | 29 | 115 | 58 | 2 | — | — | — | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: advanced-llm=3, vanilla-llm=2.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | advanced-llm status | ⬜ advanced-llm prov cost | ⬜ advanced-llm util cost | vanilla-llm status | ⬜ vanilla-llm prov cost | ⬜ vanilla-llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0949 | 0.0894 | FAIL | 0.0474 | 0.047 |
| 2 | FAIL | 0.0613 | 0.0612 | PASS | 0.1878 | 0.1001 |
| 3 | PASS | 0.1227 | 0.0706 | — | — | — |
