# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **formula**: `optimizer=formula` · `stopped_reason=first_fail` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-2` · prov_cost_total=372.567085 (steady=372.528, best_pass=0.5174), util_cost_total=131.052278 (steady=131.04, best_pass=0.182)
- **llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=5 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-4` · prov_cost_total=224.411633 (steady=224.352, best_pass=0.3116), util_cost_total=111.548435 (steady=111.528, best_pass=0.1549)

## Resource delta (first row → last row)

| | 🟩 CPU req (m) | 🟧 Mem req (MiB) |
|---|---:|---:|
| formula | -62.0 | -30.0 |
| llm | -55.0 | -31.0 |

## Combined iterations

One row per iteration index (boundary `rows` order). Rows are **not** matched configs — each arm ran an independent squeeze trajectory.

| # | formula status | ⬜ formula prov cost | ⬜ formula util cost | formula p95 | formula err | formula ach RPS | formula cpu% req | formula mem% | 🟩 formula cpu m | 🟧 formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | ⬜ llm prov cost | ⬜ llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% req | llm mem% | 🟩 llm cpu m | 🟧 llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1231 | 6 | 0 | 45 | 35.5 | 9.9 | 150 | 75 | 300 | 150 | 5 | PASS | 0.7116 | 0.1687 | 6 | 0 | 45 | 48.3 | 14.5 | 150 | 75 | 300 | 150 | 5 |
| 2 | PASS | 0.5174 | 0.182 | 6 | 0 | 45 | 72.4 | 16.7 | 109 | 55 | 218 | 109 | 5 | PASS | 0.6392 | 0.1737 | 6 | 0 | 45 | 55.8 | 13.1 | 135 | 65 | 270 | 135 | 5 |
| 3 | FAIL | 0.3344 | 0.186 | 6 | 0 | 45 | 114 | 25.5 | 88 | 45 | 175 | 88 | 4 | PASS | 0.4535 | 0.1608 | 6 | 0 | 45 | 72.7 | 18.6 | 120 | 55 | 240 | 120 | 4 |
| 4 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.3116 | 0.1549 | 6 | 0 | 45 | 94.7 | 27.4 | 110 | 50 | 205 | 110 | 3 |
| 5 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.2694 | 0.1593 | 6 | 0 | 45 | 111.9 | 40.2 | 95 | 44 | 177 | 95 | 3 |

*Iteration count mismatch: formula=3, llm=5.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | formula status | ⬜ formula prov cost | ⬜ formula util cost | llm status | ⬜ llm prov cost | ⬜ llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1231 | PASS | 0.7116 | 0.1687 |
| 2 | PASS | 0.5174 | 0.182 | PASS | 0.6392 | 0.1737 |
| 3 | FAIL | 0.3344 | 0.186 | PASS | 0.4535 | 0.1608 |
| 4 | — | — | — | PASS | 0.3116 | 0.1549 |
| 5 | — | — | — | FAIL | 0.2694 | 0.1593 |
