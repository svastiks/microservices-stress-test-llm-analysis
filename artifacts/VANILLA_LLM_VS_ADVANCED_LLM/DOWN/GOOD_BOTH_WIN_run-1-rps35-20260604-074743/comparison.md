# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **advanced-llm**: `optimizer=llm` · `stopped_reason=empty_recommended_diff` · iterations=7 · `best_pass_dir=/app/results/squeeze-compare-advanced-llm/run-1/iteration-7` · prov_cost_total=107.35202 (steady=107.28, best_pass=0.149), util_cost_total=94.777017 (steady=94.752, best_pass=0.1316)
- **vanilla-llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=7 · `best_pass_dir=/app/results/squeeze-compare-vanilla-llm/run-1/iteration-6` · prov_cost_total=118.865783 (steady=118.8, best_pass=0.165), util_cost_total=102.911105 (steady=102.888, best_pass=0.1429)

## Resource delta (first row → last row)

| | 🟩 CPU req (m) | 🟧 Mem req (MiB) |
|---|---:|---:|
| advanced-llm | -71.0 | -40.0 |
| vanilla-llm | -70.0 | -37.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | advanced-llm status | ⬜ advanced-llm prov cost | ⬜ advanced-llm util cost | advanced-llm p95 | advanced-llm err | advanced-llm ach RPS | advanced-llm cpu% | advanced-llm mem% | 🟩 advanced-llm cpu m | 🟧 advanced-llm mem Mi | advanced-llm cpu lim | advanced-llm mem lim | advanced-llm repl | vanilla-llm status | ⬜ vanilla-llm prov cost | ⬜ vanilla-llm util cost | vanilla-llm p95 | vanilla-llm err | vanilla-llm ach RPS | vanilla-llm cpu% | vanilla-llm mem% | 🟩 vanilla-llm cpu m | 🟧 vanilla-llm mem Mi | vanilla-llm cpu lim | vanilla-llm mem lim | vanilla-llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1066 | 6 | 0 | 35 | 15.3 | 9.2 | 150 | 75 | 300 | 150 | 5 | PASS | 0.7116 | 0.1181 | 6 | 0 | 35 | 17 | 9.2 | 150 | 75 | 300 | 150 | 5 |
| 2 | PASS | 0.6392 | 0.1515 | 6 | 0 | 35 | 24.4 | 10.3 | 135 | 65 | 270 | 135 | 5 | PASS | 0.6402 | 0.1426 | 6 | 0 | 35 | 22.9 | 10.6 | 135 | 67 | 270 | 135 | 5 |
| 3 | PASS | 0.4571 | 0.1641 | 6 | 0 | 35 | 36.8 | 17.9 | 121 | 55 | 242 | 121 | 4 | PASS | 0.4554 | 0.1559 | 5 | 0 | 35 | 35.1 | 18.1 | 120 | 60 | 240 | 120 | 4 |
| 4 | PASS | 0.4115 | 0.1615 | 6 | 0 | 35 | 40 | 23.6 | 109 | 49 | 218 | 109 | 4 | PASS | 0.3074 | 0.1563 | 6 | 0 | 35 | 52.1 | 27.8 | 108 | 54 | 216 | 108 | 3 |
| 5 | PASS | 0.2775 | 0.1507 | 6 | 0 | 35 | 55.2 | 36.1 | 98 | 44 | 195 | 95 | 3 | PASS | 0.276 | 0.1345 | 5 | 0 | 35 | 49.7 | 30.7 | 97 | 48 | 194 | 97 | 3 |
| 6 | PASS | 0.2349 | 0.1347 | 5 | 0 | 35 | 58.3 | 37.6 | 83 | 37 | 165 | 80 | 3 | PASS | 0.165 | 0.1429 | 6 | 0 | 35 | 88.8 | 45.5 | 87 | 43 | 155 | 78 | 2 |
| 7 | PASS | 0.149 | 0.1316 | 5 | 0 | 35 | 90.2 | 49.4 | 79 | 35 | 148 | 72 | 2 | FAIL | 0.0757 | 0.0739 | 7 | 0 | 35 | 152.3 | 51.1 | 80 | 38 | 140 | 70 | 1 |

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | advanced-llm status | ⬜ advanced-llm prov cost | ⬜ advanced-llm util cost | vanilla-llm status | ⬜ vanilla-llm prov cost | ⬜ vanilla-llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1066 | PASS | 0.7116 | 0.1181 |
| 2 | PASS | 0.6392 | 0.1515 | PASS | 0.6402 | 0.1426 |
| 3 | PASS | 0.4571 | 0.1641 | PASS | 0.4554 | 0.1559 |
| 4 | PASS | 0.4115 | 0.1615 | PASS | 0.3074 | 0.1563 |
| 5 | PASS | 0.2775 | 0.1507 | PASS | 0.276 | 0.1345 |
| 6 | PASS | 0.2349 | 0.1347 | PASS | 0.165 | 0.1429 |
| 7 | PASS | 0.149 | 0.1316 | FAIL | 0.0757 | 0.0739 |
