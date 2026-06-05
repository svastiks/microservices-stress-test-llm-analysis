# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **advanced-llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=7 · `best_pass_dir=/app/results/squeeze-compare-advanced-llm/run-1/iteration-6` · prov_cost_total=149.39434 (steady=149.328, best_pass=0.2074), util_cost_total=107.162122 (steady=107.136, best_pass=0.1488)
- **vanilla-llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=6 · `best_pass_dir=/app/results/squeeze-compare-vanilla-llm/run-1/iteration-5` · prov_cost_total=183.448585 (steady=183.384, best_pass=0.2547), util_cost_total=123.936525 (steady=123.912, best_pass=0.1721)

## Resource delta (first row → last row)

| | 🟩 CPU req (m) | 🟧 Mem req (MiB) |
|---|---:|---:|
| advanced-llm | -84.0 | -44.0 |
| vanilla-llm | -70.0 | -40.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | advanced-llm status | ⬜ advanced-llm prov cost | ⬜ advanced-llm util cost | advanced-llm p95 | advanced-llm err | advanced-llm ach RPS | advanced-llm cpu% | advanced-llm mem% | 🟩 advanced-llm cpu m | 🟧 advanced-llm mem Mi | advanced-llm cpu lim | advanced-llm mem lim | advanced-llm repl | vanilla-llm status | ⬜ vanilla-llm prov cost | ⬜ vanilla-llm util cost | vanilla-llm p95 | vanilla-llm err | vanilla-llm ach RPS | vanilla-llm cpu% | vanilla-llm mem% | 🟩 vanilla-llm cpu m | 🟧 vanilla-llm mem Mi | vanilla-llm cpu lim | vanilla-llm mem lim | vanilla-llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1007 | 6 | 0 | 35 | 14.3 | 11.3 | 150 | 75 | 300 | 150 | 5 | PASS | 0.7116 | 0.1248 | 6 | 0 | 35 | 18 | 9.1 | 150 | 75 | 300 | 150 | 5 |
| 2 | PASS | 0.6392 | 0.1517 | 6 | 0 | 35 | 24.3 | 12.7 | 135 | 65 | 270 | 135 | 5 | PASS | 0.5693 | 0.1581 | 6 | 0 | 35 | 28.5 | 14.2 | 120 | 60 | 240 | 120 | 5 |
| 3 | PASS | 0.3863 | 0.1704 | 6 | 0 | 35 | 45.1 | 25.1 | 102 | 49 | 203 | 102 | 4 | PASS | 0.5194 | 0.1851 | 6 | 0 | 35 | 36.5 | 18.2 | 110 | 50 | 210 | 100 | 5 |
| 4 | PASS | 0.3484 | 0.1828 | 6 | 0 | 35 | 53.7 | 28.7 | 92 | 44 | 173 | 91 | 4 | PASS | 0.3776 | 0.1926 | 6 | 0 | 35 | 52.1 | 28.5 | 100 | 45 | 180 | 90 | 4 |
| 5 | PASS | 0.2358 | 0.1685 | 6 | 0 | 35 | 73 | 42.1 | 83 | 40 | 156 | 82 | 3 | PASS | 0.2547 | 0.1721 | 5 | 0 | 35 | 68.7 | 44.3 | 90 | 40 | 160 | 80 | 3 |
| 6 | PASS | 0.2074 | 0.1488 | 5 | 0 | 35 | 73.4 | 39.9 | 73 | 35 | 140 | 75 | 3 | FAIL | 0.1508 | 0.1483 | 7 | 0 | 35 | 110.3 | 62.4 | 80 | 35 | 140 | 70 | 2 |
| 7 | FAIL | 0.1249 | 0.122 | 6 | 0 | 35 | 110.6 | 52.9 | 66 | 31 | 126 | 67 | 2 | — | — | — | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: advanced-llm=7, vanilla-llm=6.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | advanced-llm status | ⬜ advanced-llm prov cost | ⬜ advanced-llm util cost | vanilla-llm status | ⬜ vanilla-llm prov cost | ⬜ vanilla-llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1007 | PASS | 0.7116 | 0.1248 |
| 2 | PASS | 0.6392 | 0.1517 | PASS | 0.5693 | 0.1581 |
| 3 | PASS | 0.3863 | 0.1704 | PASS | 0.5194 | 0.1851 |
| 4 | PASS | 0.3484 | 0.1828 | PASS | 0.3776 | 0.1926 |
| 5 | PASS | 0.2358 | 0.1685 | PASS | 0.2547 | 0.1721 |
| 6 | PASS | 0.2074 | 0.1488 | FAIL | 0.1508 | 0.1483 |
| 7 | FAIL | 0.1249 | 0.122 | — | — | — |
