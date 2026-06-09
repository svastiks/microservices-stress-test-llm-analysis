# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **formula**: `optimizer=formula` · `stopped_reason=recovered_from_underprovisioning` · iterations=9 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-9` · prov_cost_total=188.890665 (steady=188.856, best_pass=0.2623), util_cost_total=83.038608 (steady=83.016, best_pass=0.1153)
- **llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=10 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-10` · prov_cost_total=207.257168 (steady=207.216, best_pass=0.2878), util_cost_total=96.865933 (steady=96.84, best_pass=0.1345)

## Resource delta (first row → last row)

| | 🟩 CPU req (m) | 🟧 Mem req (MiB) |
|---|---:|---:|
| formula | +88.0 | +46.0 |
| llm | +105.0 | +20.0 |

## Combined iterations

One row per iteration index (boundary `rows` order). Rows are **not** matched configs — each arm ran an independent squeeze trajectory. When `paired-baseline-probe.md` exists under each arm, **row 1** shares the same observed burn/cpu% (one k6 window, two optimizer analyses).

| # | formula status | ⬜ formula prov cost | ⬜ formula util cost | formula p95 | formula err | formula ach RPS | formula cpu% req | formula mem% | 🟩 formula cpu m | 🟧 formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | ⬜ llm prov cost | ⬜ llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% req | llm mem% | 🟩 llm cpu m | 🟧 llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0456 | 4241 | 0 | 219.3 | 192 | 160.5 | 50 | 25 | 100 | 50 | 1 | FAIL | 0.0474 | 0.0444 | 3005 | 0 | 220 | 187.8 | 88.4 | 50 | 25 | 100 | 50 | 1 |
| 2 | FAIL | 0.0949 | 0.0869 | 348 | 0 | 220 | 187.9 | 47.5 | 50 | 25 | 100 | 50 | 2 | FAIL | 0.0949 | 0.0833 | 360 | 0 | 220 | 179.5 | 50.7 | 50 | 25 | 100 | 50 | 2 |
| 3 | FAIL | 0.1101 | 0.0975 | 342 | 0 | 220 | 181 | 38.1 | 58 | 29 | 115 | 58 | 2 | FAIL | 0.1101 | 0.0972 | 261 | 0 | 220 | 179.9 | 44.5 | 58 | 29 | 115 | 50 | 2 |
| 4 | FAIL | 0.1272 | 0.1036 | 264 | 0 | 220 | 167.2 | 31.2 | 67 | 34 | 133 | 67 | 2 | FAIL | 0.1263 | 0.1071 | 238 | 0 | 220 | 171.2 | 41.1 | 67 | 29 | 132 | 50 | 2 |
| 5 | FAIL | 0.1482 | 0.1113 | 221 | 0 | 220 | 152.9 | 24.9 | 78 | 40 | 153 | 78 | 2 | FAIL | 0.1452 | 0.1077 | 262 | 0 | 220 | 150.3 | 32 | 77 | 34 | 152 | 58 | 2 |
| 6 | FAIL | 0.171 | 0.115 | 228 | 0 | 220 | 136.6 | 20.9 | 90 | 46 | 176 | 90 | 2 | FAIL | 0.1678 | 0.1097 | 278 | 0 | 220 | 131.4 | 27.2 | 89 | 39 | 174 | 67 | 2 |
| 7 | FAIL | 0.1976 | 0.1176 | 247 | 0 | 220 | 120.8 | 16.9 | 104 | 53 | 203 | 104 | 2 | FAIL | 0.1942 | 0.1148 | 222 | 0 | 220 | 118.1 | 24.1 | 103 | 45 | 200 | 77 | 2 |
| 8 | FAIL | 0.2279 | 0.1115 | 248 | 0 | 220 | 99 | 15.1 | 120 | 61 | 234 | 120 | 2 | FAIL | 0.2212 | 0.1187 | 229 | 0 | 220 | 107.1 | 23.9 | 118 | 45 | 230 | 77 | 2 |
| 9 | PASS | 0.2623 | 0.1153 | 244 | 0 | 220 | 89.5 | 13.2 | 138 | 71 | 270 | 138 | 2 | FAIL | 0.2518 | 0.1199 | 227 | 0 | 220 | 95.1 | 22.8 | 135 | 45 | 265 | 77 | 2 |
| 10 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.2878 | 0.1345 | 252 | 0 | 220 | 81.3 | 22.9 | 155 | 45 | 265 | 77 | 2 |

*Iteration count mismatch: formula=9, llm=10.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | formula status | ⬜ formula prov cost | ⬜ formula util cost | llm status | ⬜ llm prov cost | ⬜ llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0456 | FAIL | 0.0474 | 0.0444 |
| 2 | FAIL | 0.0949 | 0.0869 | FAIL | 0.0949 | 0.0833 |
| 3 | FAIL | 0.1101 | 0.0975 | FAIL | 0.1101 | 0.0972 |
| 4 | FAIL | 0.1272 | 0.1036 | FAIL | 0.1263 | 0.1071 |
| 5 | FAIL | 0.1482 | 0.1113 | FAIL | 0.1452 | 0.1077 |
| 6 | FAIL | 0.171 | 0.115 | FAIL | 0.1678 | 0.1097 |
| 7 | FAIL | 0.1976 | 0.1176 | FAIL | 0.1942 | 0.1148 |
| 8 | FAIL | 0.2279 | 0.1115 | FAIL | 0.2212 | 0.1187 |
| 9 | PASS | 0.2623 | 0.1153 | FAIL | 0.2518 | 0.1199 |
| 10 | — | — | — | PASS | 0.2878 | 0.1345 |
