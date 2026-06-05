# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **advanced-llm**: `optimizer=llm` · `stopped_reason=empty_recommended_diff` · iterations=10 · `best_pass_dir=/app/results/squeeze-compare-advanced-llm/run-1/iteration-10` · prov_cost_total=79.495855 (steady=79.416, best_pass=0.1103), util_cost_total=72.10508 (steady=72.072, best_pass=0.1001)
- **vanilla-llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=7 · `best_pass_dir=/app/results/squeeze-compare-vanilla-llm/run-1/iteration-6` · prov_cost_total=109.06684 (steady=109.008, best_pass=0.1514), util_cost_total=96.359925 (steady=96.336, best_pass=0.1338)

## Resource delta (first row → last row)

| | 🟩 CPU req (m) | 🟧 Mem req (MiB) |
|---|---:|---:|
| advanced-llm | -92.0 | -45.0 |
| vanilla-llm | -80.0 | -45.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | advanced-llm status | ⬜ advanced-llm prov cost | ⬜ advanced-llm util cost | advanced-llm p95 | advanced-llm err | advanced-llm ach RPS | advanced-llm cpu% | advanced-llm mem% | 🟩 advanced-llm cpu m | 🟧 advanced-llm mem Mi | advanced-llm cpu lim | advanced-llm mem lim | advanced-llm repl | vanilla-llm status | ⬜ vanilla-llm prov cost | ⬜ vanilla-llm util cost | vanilla-llm p95 | vanilla-llm err | vanilla-llm ach RPS | vanilla-llm cpu% | vanilla-llm mem% | 🟩 vanilla-llm cpu m | 🟧 vanilla-llm mem Mi | vanilla-llm cpu lim | vanilla-llm mem lim | vanilla-llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1032 | 6 | 0 | 35 | 14.8 | 9.1 | 150 | 75 | 300 | 150 | 5 | PASS | 0.7116 | 0.1302 | 6 | 0 | 35 | 18.8 | 9.1 | 150 | 75 | 300 | 150 | 5 |
| 2 | PASS | 0.6392 | 0.1494 | 6 | 0 | 35 | 24 | 11.5 | 135 | 65 | 270 | 135 | 5 | PASS | 0.5693 | 0.1519 | 6 | 0 | 35 | 27.5 | 11.6 | 120 | 60 | 240 | 120 | 5 |
| 3 | PASS | 0.4554 | 0.1675 | 6 | 0 | 35 | 37.8 | 17.9 | 120 | 60 | 240 | 120 | 4 | PASS | 0.4099 | 0.1649 | 6 | 0 | 35 | 41.3 | 20.4 | 108 | 54 | 216 | 108 | 4 |
| 4 | PASS | 0.4175 | 0.1636 | 6 | 0 | 35 | 39.9 | 25.9 | 110 | 55 | 220 | 100 | 4 | PASS | 0.2787 | 0.1624 | 5 | 0 | 35 | 59.7 | 31.3 | 98 | 48 | 194 | 96 | 3 |
| 5 | PASS | 0.2819 | 0.1594 | 6 | 0 | 35 | 57.4 | 40.6 | 99 | 50 | 198 | 85 | 3 | PASS | 0.1668 | 0.1482 | 5 | 0 | 35 | 90.8 | 51.7 | 88 | 43 | 175 | 86 | 2 |
| 6 | PASS | 0.1666 | 0.1393 | 5 | 0 | 35 | 85.5 | 47.6 | 88 | 42 | 178 | 75 | 2 | PASS | 0.1514 | 0.1338 | 11 | 0 | 35 | 91.6 | 26 | 80 | 38 | 140 | 70 | 2 |
| 7 | PASS | 0.1518 | 0.1288 | 5 | 0 | 35 | 86.4 | 55.7 | 80 | 40 | 160 | 65 | 2 | FAIL | 0.0659 | 0.0656 | 53 | 0 | 35 | 161.1 | 87.2 | 70 | 30 | 120 | 60 | 1 |
| 8 | PASS | 0.1366 | 0.1116 | 5 | 0 | 35 | 83.6 | 46.1 | 72 | 36 | 144 | 58 | 2 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 9 | PASS | 0.1233 | 0.1003 | 7 | 0 | 35 | 83.8 | 35.3 | 65 | 32 | 130 | 52 | 2 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 10 | PASS | 0.1103 | 0.1001 | 23 | 0 | 35 | 92.7 | 57.2 | 58 | 30 | 117 | 49 | 2 | — | — | — | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: advanced-llm=10, vanilla-llm=7.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | advanced-llm status | ⬜ advanced-llm prov cost | ⬜ advanced-llm util cost | vanilla-llm status | ⬜ vanilla-llm prov cost | ⬜ vanilla-llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1032 | PASS | 0.7116 | 0.1302 |
| 2 | PASS | 0.6392 | 0.1494 | PASS | 0.5693 | 0.1519 |
| 3 | PASS | 0.4554 | 0.1675 | PASS | 0.4099 | 0.1649 |
| 4 | PASS | 0.4175 | 0.1636 | PASS | 0.2787 | 0.1624 |
| 5 | PASS | 0.2819 | 0.1594 | PASS | 0.1668 | 0.1482 |
| 6 | PASS | 0.1666 | 0.1393 | PASS | 0.1514 | 0.1338 |
| 7 | PASS | 0.1518 | 0.1288 | FAIL | 0.0659 | 0.0656 |
| 8 | PASS | 0.1366 | 0.1116 | — | — | — |
| 9 | PASS | 0.1233 | 0.1003 | — | — | — |
| 10 | PASS | 0.1103 | 0.1001 | — | — | — |
