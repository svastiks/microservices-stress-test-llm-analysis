# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **advanced-llm**: `optimizer=llm` · `stopped_reason=empty_recommended_diff` · iterations=7 · `best_pass_dir=/app/results/squeeze-compare-advanced-llm/run-1/iteration-7` · prov_cost_total=118.438822 (steady=118.368, best_pass=0.1644), util_cost_total=101.259283 (steady=101.232, best_pass=0.1406)
- **vanilla-llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=8 · `best_pass_dir=/app/results/squeeze-compare-vanilla-llm/run-1/iteration-7` · prov_cost_total=95.031625 (steady=94.968, best_pass=0.1319), util_cost_total=74.61595 (steady=74.592, best_pass=0.1036)

## Resource delta (first row → last row)

| | 🟩 CPU req (m) | 🟧 Mem req (MiB) |
|---|---:|---:|
| advanced-llm | -63.0 | -35.0 |
| vanilla-llm | -90.0 | -50.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | advanced-llm status | ⬜ advanced-llm prov cost | ⬜ advanced-llm util cost | advanced-llm p95 | advanced-llm err | advanced-llm ach RPS | advanced-llm cpu% | advanced-llm mem% | 🟩 advanced-llm cpu m | 🟧 advanced-llm mem Mi | advanced-llm cpu lim | advanced-llm mem lim | advanced-llm repl | vanilla-llm status | ⬜ vanilla-llm prov cost | ⬜ vanilla-llm util cost | vanilla-llm p95 | vanilla-llm err | vanilla-llm ach RPS | vanilla-llm cpu% | vanilla-llm mem% | 🟩 vanilla-llm cpu m | 🟧 vanilla-llm mem Mi | vanilla-llm cpu lim | vanilla-llm mem lim | vanilla-llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1081 | 6 | 0 | 35 | 15.4 | 11.3 | 150 | 75 | 300 | 150 | 5 | PASS | 0.7116 | 0.1181 | 6 | 0 | 35 | 17 | 9.1 | 150 | 75 | 300 | 150 | 5 |
| 2 | PASS | 0.6392 | 0.1642 | 6 | 0 | 35 | 26.3 | 13.9 | 135 | 65 | 255 | 130 | 5 | PASS | 0.5693 | 0.1367 | 6 | 0 | 35 | 24.7 | 11.4 | 120 | 60 | 240 | 120 | 5 |
| 3 | PASS | 0.4547 | 0.1791 | 6 | 0 | 35 | 40.3 | 22.3 | 120 | 58 | 230 | 115 | 4 | PASS | 0.3116 | 0.1587 | 6 | 0 | 35 | 52 | 28.9 | 110 | 50 | 220 | 100 | 3 |
| 4 | PASS | 0.3122 | 0.1725 | 6 | 0 | 35 | 56.3 | 34.6 | 110 | 52 | 210 | 100 | 3 | PASS | 0.2832 | 0.1565 | 6 | 0 | 35 | 56.4 | 31.8 | 100 | 45 | 200 | 90 | 3 |
| 5 | PASS | 0.2895 | 0.1687 | 6 | 0 | 35 | 59.3 | 38 | 102 | 48 | 195 | 93 | 3 | PASS | 0.2547 | 0.1292 | 6 | 0 | 35 | 51.8 | 28.1 | 90 | 40 | 180 | 80 | 3 |
| 6 | PASS | 0.2613 | 0.1581 | 5 | 0 | 35 | 61.8 | 35.5 | 92 | 44 | 175 | 85 | 3 | PASS | 0.2263 | 0.0994 | 5 | 0 | 35 | 44.9 | 23.9 | 80 | 35 | 160 | 70 | 3 |
| 7 | PASS | 0.1644 | 0.1406 | 5 | 0 | 35 | 88.1 | 33.6 | 87 | 40 | 163 | 80 | 2 | PASS | 0.1319 | 0.1036 | 50 | 0 | 35 | 81.5 | 16.3 | 70 | 30 | 120 | 60 | 2 |
| 8 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.0564 | 0.0558 | 95 | 0 | 35 | 163 | 73.2 | 60 | 25 | 100 | 50 | 1 |

*Iteration count mismatch: advanced-llm=7, vanilla-llm=8.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | advanced-llm status | ⬜ advanced-llm prov cost | ⬜ advanced-llm util cost | vanilla-llm status | ⬜ vanilla-llm prov cost | ⬜ vanilla-llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1081 | PASS | 0.7116 | 0.1181 |
| 2 | PASS | 0.6392 | 0.1642 | PASS | 0.5693 | 0.1367 |
| 3 | PASS | 0.4547 | 0.1791 | PASS | 0.3116 | 0.1587 |
| 4 | PASS | 0.3122 | 0.1725 | PASS | 0.2832 | 0.1565 |
| 5 | PASS | 0.2895 | 0.1687 | PASS | 0.2547 | 0.1292 |
| 6 | PASS | 0.2613 | 0.1581 | PASS | 0.2263 | 0.0994 |
| 7 | PASS | 0.1644 | 0.1406 | PASS | 0.1319 | 0.1036 |
| 8 | — | — | — | FAIL | 0.0564 | 0.0558 |
