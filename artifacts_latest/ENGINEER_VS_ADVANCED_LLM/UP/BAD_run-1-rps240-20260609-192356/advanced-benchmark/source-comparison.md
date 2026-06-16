# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **formula**: `optimizer=formula` · `stopped_reason=recovered_from_underprovisioning` · iterations=9 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-9` · prov_cost_total=211.14086 (steady=211.104, best_pass=0.2932), util_cost_total=80.662985 (steady=80.64, best_pass=0.112)
- **llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=11 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-11` · prov_cost_total=175.86861 (steady=175.824, best_pass=0.2442), util_cost_total=78.867978 (steady=78.84, best_pass=0.1095)

## Resource delta (first row → last row)

| | 🟩 CPU req (m) | 🟧 Mem req (MiB) |
|---|---:|---:|
| formula | +104.0 | +57.0 |
| llm | +80.0 | +27.0 |

## Combined iterations

One row per iteration index (boundary `rows` order). Rows are **not** matched configs — each arm ran an independent squeeze trajectory. When `paired-baseline-probe.md` exists under each arm, **row 1** shares the same observed burn/cpu% (one k6 window, two optimizer analyses).

| # | formula status | ⬜ formula prov cost | ⬜ formula util cost | formula p95 | formula err | formula ach RPS | formula cpu% req | formula mem% | 🟩 formula cpu m | 🟧 formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | ⬜ llm prov cost | ⬜ llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% req | llm mem% | 🟩 llm cpu m | 🟧 llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0452 | 4458 | 0 | 236.5 | 190.1 | 127.3 | 50 | 25 | 100 | 50 | 1 | FAIL | 0.0474 | 0.0458 | 2982 | 0 | 235 | 193.4 | 92.5 | 50 | 25 | 100 | 50 | 1 |
| 2 | FAIL | 0.0949 | 0.0877 | 628 | 0 | 240 | 189.6 | 49.6 | 50 | 25 | 100 | 50 | 2 | FAIL | 0.0949 | 0.0869 | 771 | 0 | 240 | 187.5 | 52.8 | 50 | 25 | 100 | 50 | 2 |
| 3 | FAIL | 0.1161 | 0.1024 | 339 | 0 | 240 | 181 | 36.1 | 61 | 32 | 121 | 61 | 2 | FAIL | 0.1101 | 0.0961 | 399 | 0 | 240 | 178 | 41 | 58 | 29 | 115 | 58 | 2 |
| 4 | FAIL | 0.135 | 0.1074 | 457 | 0 | 240 | 162.3 | 30.5 | 71 | 37 | 140 | 71 | 2 | FAIL | 0.1272 | 0.1058 | 310 | 0 | 240 | 169.4 | 31.9 | 67 | 34 | 132 | 66 | 2 |
| 5 | FAIL | 0.156 | 0.1135 | 280 | 0 | 240 | 148.5 | 22.5 | 82 | 43 | 161 | 82 | 2 | FAIL | 0.1462 | 0.1081 | 347 | 0 | 240 | 151.1 | 27.2 | 77 | 39 | 152 | 76 | 2 |
| 6 | FAIL | 0.1808 | 0.1125 | 321 | 0 | 240 | 126.5 | 20.8 | 95 | 50 | 186 | 95 | 2 | FAIL | 0.1672 | 0.1088 | 364 | 0 | 240 | 133.5 | 21.8 | 88 | 45 | 174 | 87 | 2 |
| 7 | FAIL | 0.2093 | 0.1193 | 297 | 0 | 240 | 115.4 | 16.8 | 110 | 58 | 214 | 110 | 2 | FAIL | 0.1902 | 0.1077 | 277 | 0 | 240 | 117.6 | 18.7 | 100 | 52 | 200 | 100 | 2 |
| 8 | FAIL | 0.2417 | 0.1194 | 623 | 0 | 240 | 100 | 14.6 | 127 | 67 | 247 | 127 | 2 | FAIL | 0.2046 | 0.1119 | 393 | 0 | 240 | 113.2 | 18.4 | 108 | 52 | 216 | 100 | 2 |
| 9 | PASS | 0.2932 | 0.112 | 454 | 0 | 240 | 77 | 12.3 | 154 | 82 | 299 | 154 | 2 | FAIL | 0.219 | 0.1125 | 314 | 0 | 240 | 98.7 | 18.3 | 116 | 52 | 216 | 100 | 2 |
| 10 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.2334 | 0.126 | 383 | 0 | 240 | 96.8 | 19.2 | 124 | 52 | 216 | 100 | 2 |
| 11 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.2442 | 0.1095 | 313 | 0 | 240 | 92 | 18.4 | 130 | 52 | 260 | 100 | 2 |

*Iteration count mismatch: formula=9, llm=11.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | formula status | ⬜ formula prov cost | ⬜ formula util cost | llm status | ⬜ llm prov cost | ⬜ llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0452 | FAIL | 0.0474 | 0.0458 |
| 2 | FAIL | 0.0949 | 0.0877 | FAIL | 0.0949 | 0.0869 |
| 3 | FAIL | 0.1161 | 0.1024 | FAIL | 0.1101 | 0.0961 |
| 4 | FAIL | 0.135 | 0.1074 | FAIL | 0.1272 | 0.1058 |
| 5 | FAIL | 0.156 | 0.1135 | FAIL | 0.1462 | 0.1081 |
| 6 | FAIL | 0.1808 | 0.1125 | FAIL | 0.1672 | 0.1088 |
| 7 | FAIL | 0.2093 | 0.1193 | FAIL | 0.1902 | 0.1077 |
| 8 | FAIL | 0.2417 | 0.1194 | FAIL | 0.2046 | 0.1119 |
| 9 | PASS | 0.2932 | 0.112 | FAIL | 0.219 | 0.1125 |
| 10 | — | — | — | FAIL | 0.2334 | 0.126 |
| 11 | — | — | — | PASS | 0.2442 | 0.1095 |
