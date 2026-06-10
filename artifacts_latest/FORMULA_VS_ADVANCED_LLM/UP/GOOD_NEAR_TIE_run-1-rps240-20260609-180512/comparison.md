# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **formula**: `optimizer=formula` · `stopped_reason=recovered_from_underprovisioning` · iterations=9 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-9` · prov_cost_total=188.890665 (steady=188.856, best_pass=0.2623), util_cost_total=83.83062 (steady=83.808, best_pass=0.1164)
- **llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=10 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-10` · prov_cost_total=189.904553 (steady=189.864, best_pass=0.2637), util_cost_total=86.857558 (steady=86.832, best_pass=0.1206)

## Resource delta (first row → last row)

| | 🟩 CPU req (m) | 🟧 Mem req (MiB) |
|---|---:|---:|
| formula | +88.0 | +46.0 |
| llm | +89.0 | +44.0 |

## Combined iterations

One row per iteration index (boundary `rows` order). Rows are **not** matched configs — each arm ran an independent squeeze trajectory. When `paired-baseline-probe.md` exists under each arm, **row 1** shares the same observed burn/cpu% (one k6 window, two optimizer analyses).

| # | formula status | ⬜ formula prov cost | ⬜ formula util cost | formula p95 | formula err | formula ach RPS | formula cpu% req | formula mem% | 🟩 formula cpu m | 🟧 formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | ⬜ llm prov cost | ⬜ llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% req | llm mem% | 🟩 llm cpu m | 🟧 llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0445 | 2671 | 0 | 238.9 | 186.8 | 125.5 | 50 | 25 | 100 | 50 | 1 | FAIL | 0.0474 | 0.0451 | 4730 | 0 | 235.2 | 190.4 | 93.7 | 50 | 25 | 100 | 50 | 1 |
| 2 | FAIL | 0.0949 | 0.0885 | 372 | 0 | 240 | 191 | 52.8 | 50 | 25 | 100 | 50 | 2 | FAIL | 0.0949 | 0.0876 | 489 | 0 | 240 | 189.5 | 49.5 | 50 | 25 | 100 | 50 | 2 |
| 3 | FAIL | 0.1101 | 0.0962 | 352 | 0 | 240 | 178.6 | 37.7 | 58 | 29 | 115 | 58 | 2 | FAIL | 0.1101 | 0.0951 | 317 | 0 | 240 | 176.6 | 39.3 | 58 | 29 | 115 | 58 | 2 |
| 4 | FAIL | 0.1272 | 0.1049 | 319 | 0 | 240 | 169.2 | 33 | 67 | 34 | 133 | 67 | 2 | FAIL | 0.1272 | 0.102 | 293 | 0 | 240 | 162.9 | 34.3 | 67 | 34 | 132 | 66 | 2 |
| 5 | FAIL | 0.1482 | 0.1086 | 318 | 0 | 240 | 149 | 24.3 | 78 | 40 | 153 | 78 | 2 | FAIL | 0.1462 | 0.1086 | 259 | 0 | 240 | 151.9 | 24.6 | 77 | 39 | 152 | 76 | 2 |
| 6 | FAIL | 0.171 | 0.114 | 300 | 0 | 240 | 135.4 | 21 | 90 | 46 | 176 | 90 | 2 | FAIL | 0.169 | 0.1167 | 316 | 0 | 240 | 140.1 | 22.3 | 89 | 45 | 174 | 87 | 2 |
| 7 | FAIL | 0.1976 | 0.1139 | 315 | 0 | 240 | 117 | 17.4 | 104 | 53 | 203 | 104 | 2 | FAIL | 0.1938 | 0.1181 | 478 | 0 | 240 | 124.1 | 18.9 | 102 | 52 | 200 | 100 | 2 |
| 8 | FAIL | 0.2279 | 0.1178 | 343 | 0 | 240 | 104.7 | 15.2 | 120 | 61 | 234 | 120 | 2 | FAIL | 0.2187 | 0.1124 | 283 | 0 | 240 | 106.8 | 15.5 | 115 | 60 | 230 | 120 | 2 |
| 9 | PASS | 0.2623 | 0.1164 | 341 | 0 | 240 | 90.1 | 13.4 | 138 | 71 | 270 | 138 | 2 | FAIL | 0.2511 | 0.1161 | 307 | 0 | 240 | 96.3 | 13.3 | 132 | 69 | 264 | 138 | 2 |
| 10 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.2637 | 0.1206 | 322 | 0 | 240 | 90.3 | 13 | 139 | 69 | 264 | 138 | 2 |

*Iteration count mismatch: formula=9, llm=10.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | formula status | ⬜ formula prov cost | ⬜ formula util cost | llm status | ⬜ llm prov cost | ⬜ llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0445 | FAIL | 0.0474 | 0.0451 |
| 2 | FAIL | 0.0949 | 0.0885 | FAIL | 0.0949 | 0.0876 |
| 3 | FAIL | 0.1101 | 0.0962 | FAIL | 0.1101 | 0.0951 |
| 4 | FAIL | 0.1272 | 0.1049 | FAIL | 0.1272 | 0.102 |
| 5 | FAIL | 0.1482 | 0.1086 | FAIL | 0.1462 | 0.1086 |
| 6 | FAIL | 0.171 | 0.114 | FAIL | 0.169 | 0.1167 |
| 7 | FAIL | 0.1976 | 0.1139 | FAIL | 0.1938 | 0.1181 |
| 8 | FAIL | 0.2279 | 0.1178 | FAIL | 0.2187 | 0.1124 |
| 9 | PASS | 0.2623 | 0.1164 | FAIL | 0.2511 | 0.1161 |
| 10 | — | — | — | PASS | 0.2637 | 0.1206 |
