# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **formula**: `optimizer=formula` · `stopped_reason=recovered_from_underprovisioning` · iterations=8 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-8` · prov_cost_total=164.116108 (steady=164.088, best_pass=0.2279), util_cost_total=76.41034 (steady=76.392, best_pass=0.1061)
- **llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=9 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-9` · prov_cost_total=166.569555 (steady=166.536, best_pass=0.2313), util_cost_total=76.70046 (steady=76.68, best_pass=0.1065)

## Resource delta (first row → last row)

| | 🟩 CPU req (m) | 🟧 Mem req (MiB) |
|---|---:|---:|
| formula | +70.0 | +36.0 |
| llm | +72.0 | +35.0 |

## Combined iterations

One row per iteration index (boundary `rows` order). Rows are **not** matched configs — each arm ran an independent squeeze trajectory. When `paired-baseline-probe.md` exists under each arm, **row 1** shares the same observed burn/cpu% (one k6 window, two optimizer analyses).

| # | formula status | ⬜ formula prov cost | ⬜ formula util cost | formula p95 | formula err | formula ach RPS | formula cpu% req | formula mem% | 🟩 formula cpu m | 🟧 formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | ⬜ llm prov cost | ⬜ llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% req | llm mem% | 🟩 llm cpu m | 🟧 llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0449 | 1613 | 0 | 219.9 | 188.7 | 119.4 | 50 | 25 | 100 | 50 | 1 | FAIL | 0.0474 | 0.0437 | 3547 | 0 | 219.7 | 184.5 | 90.5 | 50 | 25 | 100 | 50 | 1 |
| 2 | FAIL | 0.0949 | 0.0794 | 349 | 0 | 220 | 171.4 | 46.2 | 50 | 25 | 100 | 50 | 2 | FAIL | 0.0949 | 0.0799 | 364 | 0 | 220 | 172.5 | 47.2 | 50 | 25 | 100 | 50 | 2 |
| 3 | FAIL | 0.1101 | 0.0924 | 332 | 0 | 220 | 171.1 | 40.8 | 58 | 29 | 115 | 58 | 2 | FAIL | 0.1101 | 0.086 | 251 | 0 | 220 | 159.2 | 37.8 | 58 | 29 | 115 | 57 | 2 |
| 4 | FAIL | 0.1272 | 0.0978 | 242 | 0 | 220 | 157.5 | 32.5 | 67 | 34 | 133 | 67 | 2 | FAIL | 0.1272 | 0.0945 | 245 | 0 | 220 | 151.2 | 29.6 | 67 | 34 | 132 | 65 | 2 |
| 5 | FAIL | 0.1482 | 0.1013 | 244 | 0 | 220 | 138.8 | 24.2 | 78 | 40 | 153 | 78 | 2 | FAIL | 0.1462 | 0.0994 | 246 | 0 | 220 | 138.7 | 25.5 | 77 | 39 | 152 | 75 | 2 |
| 6 | FAIL | 0.171 | 0.1092 | 236 | 0 | 220 | 129.7 | 19.8 | 90 | 46 | 176 | 90 | 2 | FAIL | 0.169 | 0.1036 | 214 | 0 | 220 | 124.2 | 21 | 89 | 45 | 174 | 87 | 2 |
| 7 | FAIL | 0.1976 | 0.1025 | 238 | 0 | 220 | 105 | 17 | 104 | 53 | 203 | 104 | 2 | FAIL | 0.1938 | 0.1006 | 223 | 0 | 220 | 105.4 | 17.5 | 102 | 52 | 200 | 100 | 2 |
| 8 | PASS | 0.2279 | 0.1061 | 245 | 0 | 220 | 94.2 | 14.8 | 120 | 61 | 234 | 120 | 2 | FAIL | 0.2223 | 0.1042 | 256 | 0 | 220 | 95.5 | 15.6 | 117 | 60 | 230 | 115 | 2 |
| 9 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.2313 | 0.1065 | 239 | 0 | 220 | 89.9 | 15 | 122 | 60 | 230 | 115 | 2 |

*Iteration count mismatch: formula=8, llm=9.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | formula status | ⬜ formula prov cost | ⬜ formula util cost | llm status | ⬜ llm prov cost | ⬜ llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0449 | FAIL | 0.0474 | 0.0437 |
| 2 | FAIL | 0.0949 | 0.0794 | FAIL | 0.0949 | 0.0799 |
| 3 | FAIL | 0.1101 | 0.0924 | FAIL | 0.1101 | 0.086 |
| 4 | FAIL | 0.1272 | 0.0978 | FAIL | 0.1272 | 0.0945 |
| 5 | FAIL | 0.1482 | 0.1013 | FAIL | 0.1462 | 0.0994 |
| 6 | FAIL | 0.171 | 0.1092 | FAIL | 0.169 | 0.1036 |
| 7 | FAIL | 0.1976 | 0.1025 | FAIL | 0.1938 | 0.1006 |
| 8 | PASS | 0.2279 | 0.1061 | FAIL | 0.2223 | 0.1042 |
| 9 | — | — | — | PASS | 0.2313 | 0.1065 |
