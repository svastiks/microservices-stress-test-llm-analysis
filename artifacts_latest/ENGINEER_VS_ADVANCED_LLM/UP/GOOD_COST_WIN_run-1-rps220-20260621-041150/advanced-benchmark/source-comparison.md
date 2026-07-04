# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **formula**: `optimizer=formula` · `stopped_reason=recovered_from_underprovisioning` · iterations=9 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-9` · prov_cost_total=188.890665 (steady=188.856, best_pass=0.2623), util_cost_total=80.37412 (steady=80.352, best_pass=0.1116)
- **llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=10 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-10` · prov_cost_total=179.535743 (steady=179.496, best_pass=0.2493), util_cost_total=23.421255 (steady=23.4, best_pass=0.0325)

## Resource delta (first row → last row)

| | 🟩 CPU req (m) | 🟧 Mem req (MiB) |
|---|---:|---:|
| formula | +88.0 | +46.0 |
| llm | +82.0 | +35.0 |

## Combined iterations

One row per iteration index (boundary `rows` order). Rows are **not** matched configs — each arm ran an independent squeeze trajectory. When `paired-baseline-probe.md` exists under each arm, **row 1** shares the same observed burn/cpu% (one k6 window, two optimizer analyses).

| # | formula status | ⬜ formula prov cost | ⬜ formula util cost | formula p95 | formula err | formula ach RPS | formula cpu% req | formula mem% | 🟩 formula cpu m | 🟧 formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | ⬜ llm prov cost | ⬜ llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% req | llm mem% | 🟩 llm cpu m | 🟧 llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0442 | 1022 | 0 | 220 | 185.7 | 119.5 | 50 | 25 | 100 | 50 | 1 | FAIL | 0.0474 | 0.0425 | 3454 | 0 | 219.7 | 179 | 89.2 | 50 | 25 | 100 | 50 | 1 |
| 2 | FAIL | 0.0949 | 0.086 | 316 | 0 | 220 | 186.1 | 47.2 | 50 | 25 | 100 | 50 | 2 | FAIL | 0.0949 | 0.0842 | 385 | 0 | 220 | 182.1 | 45.8 | 50 | 25 | 100 | 50 | 2 |
| 3 | FAIL | 0.1101 | 0.0972 | 287 | 0 | 220 | 180.7 | 37.3 | 58 | 29 | 115 | 58 | 2 | FAIL | 0.1101 | 0.0948 | 282 | 0 | 220 | 176 | 39.1 | 58 | 29 | 115 | 57 | 2 |
| 4 | FAIL | 0.1272 | 0.1029 | 242 | 0 | 220 | 165.9 | 31.2 | 67 | 34 | 133 | 67 | 2 | FAIL | 0.1272 | 0.104 | 251 | 0 | 220 | 166.7 | 30.1 | 67 | 34 | 132 | 66 | 2 |
| 5 | FAIL | 0.1482 | 0.1087 | 254 | 0 | 220 | 149.3 | 24.2 | 78 | 40 | 153 | 78 | 2 | FAIL | 0.1462 | 0.1096 | 253 | 0 | 220 | 153.5 | 25.5 | 77 | 39 | 152 | 76 | 2 |
| 6 | FAIL | 0.171 | 0.1129 | 241 | 0 | 220 | 134.2 | 20.2 | 90 | 46 | 176 | 90 | 2 | FAIL | 0.1672 | 0.1095 | 257 | 0 | 220 | 134.4 | 20.9 | 88 | 45 | 174 | 87 | 2 |
| 7 | FAIL | 0.1976 | 0.1122 | 244 | 0 | 220 | 115.1 | 17.3 | 104 | 53 | 203 | 104 | 2 | FAIL | 0.192 | 0.1076 | 251 | 0 | 220 | 115.2 | 17.6 | 101 | 52 | 200 | 100 | 2 |
| 8 | FAIL | 0.2279 | 0.1091 | 230 | 0 | 220 | 96.9 | 14.5 | 120 | 61 | 234 | 120 | 2 | FAIL | 0.2205 | 0.105 | 230 | 0 | 220 | 98 | 15.4 | 116 | 60 | 230 | 115 | 2 |
| 9 | PASS | 0.2623 | 0.1116 | 231 | 0 | 220 | 86.5 | 12.8 | 138 | 71 | 270 | 138 | 2 | FAIL | 0.2349 | 0.0605 | 231 | 0 | 220 | 97.7 | 15.7 | 124 | 60 | 460 | 115 | 2 |
| 10 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.2493 | 0.0325 | 283 | 0 | 220 | 89.8 | 16.2 | 132 | 60 | 920 | 115 | 2 |

*Iteration count mismatch: formula=9, llm=10.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | formula status | ⬜ formula prov cost | ⬜ formula util cost | llm status | ⬜ llm prov cost | ⬜ llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0442 | FAIL | 0.0474 | 0.0425 |
| 2 | FAIL | 0.0949 | 0.086 | FAIL | 0.0949 | 0.0842 |
| 3 | FAIL | 0.1101 | 0.0972 | FAIL | 0.1101 | 0.0948 |
| 4 | FAIL | 0.1272 | 0.1029 | FAIL | 0.1272 | 0.104 |
| 5 | FAIL | 0.1482 | 0.1087 | FAIL | 0.1462 | 0.1096 |
| 6 | FAIL | 0.171 | 0.1129 | FAIL | 0.1672 | 0.1095 |
| 7 | FAIL | 0.1976 | 0.1122 | FAIL | 0.192 | 0.1076 |
| 8 | FAIL | 0.2279 | 0.1091 | FAIL | 0.2205 | 0.105 |
| 9 | PASS | 0.2623 | 0.1116 | FAIL | 0.2349 | 0.0605 |
| 10 | — | — | — | PASS | 0.2493 | 0.0325 |
