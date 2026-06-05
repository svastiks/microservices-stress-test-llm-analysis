# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **advanced-llm**: `optimizer=llm` · `stopped_reason=empty_recommended_diff` · iterations=7 · `best_pass_dir=/app/results/squeeze-compare-advanced-llm/run-1/iteration-7` · prov_cost_total=108.648698 (steady=108.576, best_pass=0.1508), util_cost_total=93.696693 (steady=93.672, best_pass=0.1301)
- **vanilla-llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=9 · `best_pass_dir=/app/results/squeeze-compare-vanilla-llm/run-1/iteration-8` · prov_cost_total=131.25754 (steady=131.184, best_pass=0.1822), util_cost_total=91.109802 (steady=91.08, best_pass=0.1265)

## Resource delta (first row → last row)

| | 🟩 CPU req (m) | 🟧 Mem req (MiB) |
|---|---:|---:|
| advanced-llm | -70.0 | -40.0 |
| vanilla-llm | -94.0 | -46.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | advanced-llm status | ⬜ advanced-llm prov cost | ⬜ advanced-llm util cost | advanced-llm p95 | advanced-llm err | advanced-llm ach RPS | advanced-llm cpu% | advanced-llm mem% | 🟩 advanced-llm cpu m | 🟧 advanced-llm mem Mi | advanced-llm cpu lim | advanced-llm mem lim | advanced-llm repl | vanilla-llm status | ⬜ vanilla-llm prov cost | ⬜ vanilla-llm util cost | vanilla-llm p95 | vanilla-llm err | vanilla-llm ach RPS | vanilla-llm cpu% | vanilla-llm mem% | 🟩 vanilla-llm cpu m | 🟧 vanilla-llm mem Mi | vanilla-llm cpu lim | vanilla-llm mem lim | vanilla-llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.0985 | 6 | 0 | 25 | 14.1 | 9.1 | 150 | 75 | 300 | 150 | 5 | PASS | 0.7116 | 0.1208 | 6 | 0 | 25 | 17.4 | 9.1 | 150 | 75 | 300 | 150 | 5 |
| 2 | PASS | 0.6392 | 0.1412 | 6 | 0 | 25 | 22.7 | 10.5 | 135 | 65 | 270 | 130 | 5 | PASS | 0.5717 | 0.141 | 6 | 0 | 25 | 25.5 | 10.3 | 120 | 65 | 240 | 135 | 5 |
| 3 | PASS | 0.4583 | 0.1575 | 6 | 0 | 25 | 35.2 | 18.2 | 121 | 58 | 243 | 117 | 4 | PASS | 0.4115 | 0.1548 | 6 | 0 | 25 | 38.8 | 17.6 | 108 | 58 | 216 | 121 | 4 |
| 4 | PASS | 0.4155 | 0.1574 | 6 | 0 | 25 | 38.5 | 25.4 | 110 | 50 | 220 | 100 | 4 | PASS | 0.2771 | 0.1528 | 6 | 0 | 25 | 56.8 | 26.4 | 97 | 52 | 194 | 108 | 3 |
| 5 | PASS | 0.2805 | 0.1552 | 6 | 0 | 25 | 56 | 41.5 | 99 | 45 | 198 | 85 | 3 | PASS | 0.2484 | 0.1407 | 6 | 0 | 25 | 58.1 | 31.7 | 87 | 46 | 175 | 90 | 3 |
| 6 | PASS | 0.252 | 0.1478 | 5 | 0 | 25 | 59.6 | 38.8 | 89 | 40 | 178 | 75 | 3 | PASS | 0.2277 | 0.1306 | 6 | 0 | 25 | 58.5 | 35.9 | 80 | 40 | 160 | 80 | 3 |
| 7 | PASS | 0.1508 | 0.1301 | 5 | 0 | 25 | 87.4 | 62.8 | 80 | 35 | 160 | 70 | 2 | PASS | 0.2049 | 0.1198 | 6 | 0 | 25 | 59.9 | 31.8 | 72 | 36 | 144 | 72 | 3 |
| 8 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.1822 | 0.1265 | 6 | 0 | 25 | 71.2 | 36.6 | 64 | 32 | 128 | 64 | 3 |
| 9 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.1065 | 0.1051 | 15 | 0 | 25 | 115.3 | 76.1 | 56 | 29 | 112 | 58 | 2 |

*Iteration count mismatch: advanced-llm=7, vanilla-llm=9.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | advanced-llm status | ⬜ advanced-llm prov cost | ⬜ advanced-llm util cost | vanilla-llm status | ⬜ vanilla-llm prov cost | ⬜ vanilla-llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.0985 | PASS | 0.7116 | 0.1208 |
| 2 | PASS | 0.6392 | 0.1412 | PASS | 0.5717 | 0.141 |
| 3 | PASS | 0.4583 | 0.1575 | PASS | 0.4115 | 0.1548 |
| 4 | PASS | 0.4155 | 0.1574 | PASS | 0.2771 | 0.1528 |
| 5 | PASS | 0.2805 | 0.1552 | PASS | 0.2484 | 0.1407 |
| 6 | PASS | 0.252 | 0.1478 | PASS | 0.2277 | 0.1306 |
| 7 | PASS | 0.1508 | 0.1301 | PASS | 0.2049 | 0.1198 |
| 8 | — | — | — | PASS | 0.1822 | 0.1265 |
| 9 | — | — | — | FAIL | 0.1065 | 0.1051 |
