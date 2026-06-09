# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **formula**: `optimizer=formula` · `stopped_reason=recovered_from_underprovisioning` · iterations=9 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-9` · prov_cost_total=188.890665 (steady=188.856, best_pass=0.2623), util_cost_total=81.598415 (steady=81.576, best_pass=0.1133)
- **llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=10 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-10` · prov_cost_total=189.184468 (steady=189.144, best_pass=0.2627), util_cost_total=84.553593 (steady=84.528, best_pass=0.1174)

## Resource delta (first row → last row)

| | 🟩 CPU req (m) | 🟧 Mem req (MiB) |
|---|---:|---:|
| formula | +88.0 | +46.0 |
| llm | +88.0 | +48.0 |

## Combined iterations

One row per iteration index (boundary `rows` order). Rows are **not** matched configs — each arm ran an independent squeeze trajectory. When `paired-baseline-probe.md` exists under each arm, **row 1** shares the same observed burn/cpu% (one k6 window, two optimizer analyses).

| # | formula status | ⬜ formula prov cost | ⬜ formula util cost | formula p95 | formula err | formula ach RPS | formula cpu% req | formula mem% | 🟩 formula cpu m | 🟧 formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | ⬜ llm prov cost | ⬜ llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% req | llm mem% | 🟩 llm cpu m | 🟧 llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0443 | 2289 | 0 | 219.7 | 186 | 122.4 | 50 | 25 | 100 | 50 | 1 | FAIL | 0.0474 | 0.0449 | 3965 | 0 | 219.7 | 189.7 | 88.3 | 50 | 25 | 100 | 50 | 1 |
| 2 | FAIL | 0.0949 | 0.0864 | 357 | 0 | 220 | 186.5 | 49.3 | 50 | 25 | 100 | 50 | 2 | FAIL | 0.0949 | 0.0867 | 396 | 0 | 220 | 187.4 | 49.2 | 50 | 25 | 100 | 50 | 2 |
| 3 | FAIL | 0.1101 | 0.0942 | 282 | 0 | 220 | 174.9 | 36.8 | 58 | 29 | 115 | 58 | 2 | FAIL | 0.1101 | 0.0961 | 283 | 0 | 220 | 178.5 | 38.6 | 58 | 29 | 115 | 58 | 2 |
| 4 | FAIL | 0.1272 | 0.1048 | 303 | 0 | 220 | 169.4 | 29.2 | 67 | 34 | 133 | 67 | 2 | FAIL | 0.1272 | 0.1024 | 260 | 0 | 220 | 163.8 | 32.3 | 67 | 34 | 132 | 67 | 2 |
| 5 | FAIL | 0.1482 | 0.1122 | 217 | 0 | 220 | 154.1 | 25.7 | 78 | 40 | 153 | 78 | 2 | FAIL | 0.1462 | 0.1087 | 222 | 0 | 220 | 152.1 | 24.5 | 77 | 39 | 152 | 77 | 2 |
| 6 | FAIL | 0.171 | 0.112 | 219 | 0 | 220 | 133.1 | 20.5 | 90 | 46 | 176 | 90 | 2 | FAIL | 0.169 | 0.1142 | 236 | 0 | 220 | 137 | 21.1 | 89 | 45 | 174 | 89 | 2 |
| 7 | FAIL | 0.1976 | 0.1138 | 227 | 0 | 220 | 116.7 | 18.2 | 104 | 53 | 203 | 104 | 2 | FAIL | 0.1938 | 0.1187 | 255 | 0 | 220 | 124.9 | 17.2 | 102 | 52 | 200 | 103 | 2 |
| 8 | FAIL | 0.2279 | 0.1156 | 234 | 0 | 220 | 102.7 | 14.9 | 120 | 61 | 234 | 120 | 2 | FAIL | 0.2223 | 0.1077 | 226 | 0 | 220 | 98.9 | 15.2 | 117 | 60 | 230 | 118 | 2 |
| 9 | PASS | 0.2623 | 0.1133 | 220 | 0 | 220 | 87.9 | 13 | 138 | 71 | 270 | 138 | 2 | FAIL | 0.2451 | 0.1269 | 224 | 0 | 220 | 96 | 15.4 | 129 | 66 | 230 | 118 | 2 |
| 10 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.2627 | 0.1174 | 217 | 0 | 220 | 85 | 13.5 | 138 | 73 | 252 | 129 | 2 |

*Iteration count mismatch: formula=9, llm=10.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | formula status | ⬜ formula prov cost | ⬜ formula util cost | llm status | ⬜ llm prov cost | ⬜ llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0443 | FAIL | 0.0474 | 0.0449 |
| 2 | FAIL | 0.0949 | 0.0864 | FAIL | 0.0949 | 0.0867 |
| 3 | FAIL | 0.1101 | 0.0942 | FAIL | 0.1101 | 0.0961 |
| 4 | FAIL | 0.1272 | 0.1048 | FAIL | 0.1272 | 0.1024 |
| 5 | FAIL | 0.1482 | 0.1122 | FAIL | 0.1462 | 0.1087 |
| 6 | FAIL | 0.171 | 0.112 | FAIL | 0.169 | 0.1142 |
| 7 | FAIL | 0.1976 | 0.1138 | FAIL | 0.1938 | 0.1187 |
| 8 | FAIL | 0.2279 | 0.1156 | FAIL | 0.2223 | 0.1077 |
| 9 | PASS | 0.2623 | 0.1133 | FAIL | 0.2451 | 0.1269 |
| 10 | — | — | — | PASS | 0.2627 | 0.1174 |
