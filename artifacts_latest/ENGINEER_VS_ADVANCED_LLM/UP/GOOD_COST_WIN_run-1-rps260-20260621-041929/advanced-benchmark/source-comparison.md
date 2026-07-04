# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **formula**: `optimizer=formula` · `stopped_reason=recovered_from_underprovisioning` · iterations=10 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-10` · prov_cost_total=265.799242 (steady=265.752, best_pass=0.3691), util_cost_total=83.90629 (steady=83.88, best_pass=0.1165)
- **llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=11 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-11` · prov_cost_total=202.007413 (steady=201.96, best_pass=0.2805), util_cost_total=118.976448 (steady=118.944, best_pass=0.1652)

## Resource delta (first row → last row)

| | 🟩 CPU req (m) | 🟧 Mem req (MiB) |
|---|---:|---:|
| formula | +144.0 | +77.0 |
| llm | +95.0 | +75.0 |

## Combined iterations

One row per iteration index (boundary `rows` order). Rows are **not** matched configs — each arm ran an independent squeeze trajectory. When `paired-baseline-probe.md` exists under each arm, **row 1** shares the same observed burn/cpu% (one k6 window, two optimizer analyses).

| # | formula status | ⬜ formula prov cost | ⬜ formula util cost | formula p95 | formula err | formula ach RPS | formula cpu% req | formula mem% | 🟩 formula cpu m | 🟧 formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | ⬜ llm prov cost | ⬜ llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% req | llm mem% | 🟩 llm cpu m | 🟧 llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0438 | 2888 | 0 | 255.3 | 183.9 | 126.8 | 50 | 25 | 100 | 50 | 1 | FAIL | 0.0474 | 0.0442 | 4731 | 0 | 250.4 | 186.1 | 95.2 | 50 | 25 | 100 | 50 | 1 |
| 2 | FAIL | 0.0949 | 0.0887 | 931 | 0 | 260 | 191.5 | 51.5 | 50 | 25 | 100 | 50 | 2 | FAIL | 0.0949 | 0.0879 | 811 | 0 | 260 | 189.5 | 53.8 | 50 | 25 | 100 | 50 | 2 |
| 3 | FAIL | 0.1197 | 0.1031 | 471 | 0 | 260 | 177.8 | 36.9 | 63 | 32 | 126 | 63 | 2 | FAIL | 0.1101 | 0.1024 | 864 | 0 | 260 | 190.2 | 41 | 58 | 29 | 115 | 58 | 2 |
| 4 | FAIL | 0.1386 | 0.1106 | 354 | 0 | 260 | 164 | 29.1 | 73 | 37 | 145 | 73 | 2 | FAIL | 0.1272 | 0.1049 | 535 | 0 | 260 | 174.2 | 25.6 | 66 | 43 | 133 | 86 | 2 |
| 5 | FAIL | 0.1596 | 0.1142 | 414 | 0 | 260 | 147.3 | 26.1 | 84 | 43 | 167 | 84 | 2 | FAIL | 0.1541 | 0.1108 | 379 | 0 | 260 | 140.6 | 21.7 | 79 | 61 | 146 | 103 | 2 |
| 6 | FAIL | 0.1844 | 0.1165 | 341 | 0 | 260 | 130.5 | 20.1 | 97 | 50 | 193 | 97 | 2 | FAIL | 0.1775 | 0.1231 | 361 | 0 | 260 | 136.1 | 17.5 | 91 | 70 | 168 | 118 | 2 |
| 7 | FAIL | 0.2129 | 0.1189 | 537 | 0 | 260 | 114.9 | 17.1 | 112 | 58 | 222 | 112 | 2 | FAIL | 0.2046 | 0.128 | 480 | 0 | 260 | 123.1 | 13.8 | 105 | 80 | 194 | 136 | 2 |
| 8 | FAIL | 0.2549 | 0.1172 | 594 | 0 | 260 | 94.9 | 14.3 | 134 | 70 | 266 | 134 | 2 | FAIL | 0.219 | 0.1384 | 461 | 0 | 260 | 115 | 13.8 | 113 | 80 | 194 | 136 | 2 |
| 9 | FAIL | 0.3082 | 0.1221 | 531 | 0 | 260 | 81.6 | 11.9 | 162 | 85 | 321 | 162 | 2 | FAIL | 0.2334 | 0.1384 | 428 | 0 | 260 | 100.2 | 14.8 | 121 | 80 | 194 | 136 | 2 |
| 10 | PASS | 0.3691 | 0.1165 | 492 | 0 | 260 | 65 | 9.7 | 194 | 102 | 384 | 194 | 2 | FAIL | 0.2478 | 0.1546 | 516 | 0 | 260 | 98.6 | 14.6 | 129 | 80 | 194 | 136 | 2 |
| 11 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.2805 | 0.1652 | 407 | 0 | 260 | 88.3 | 12.2 | 145 | 100 | 205 | 154 | 2 |

*Iteration count mismatch: formula=10, llm=11.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | formula status | ⬜ formula prov cost | ⬜ formula util cost | llm status | ⬜ llm prov cost | ⬜ llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0438 | FAIL | 0.0474 | 0.0442 |
| 2 | FAIL | 0.0949 | 0.0887 | FAIL | 0.0949 | 0.0879 |
| 3 | FAIL | 0.1197 | 0.1031 | FAIL | 0.1101 | 0.1024 |
| 4 | FAIL | 0.1386 | 0.1106 | FAIL | 0.1272 | 0.1049 |
| 5 | FAIL | 0.1596 | 0.1142 | FAIL | 0.1541 | 0.1108 |
| 6 | FAIL | 0.1844 | 0.1165 | FAIL | 0.1775 | 0.1231 |
| 7 | FAIL | 0.2129 | 0.1189 | FAIL | 0.2046 | 0.128 |
| 8 | FAIL | 0.2549 | 0.1172 | FAIL | 0.219 | 0.1384 |
| 9 | FAIL | 0.3082 | 0.1221 | FAIL | 0.2334 | 0.1384 |
| 10 | PASS | 0.3691 | 0.1165 | FAIL | 0.2478 | 0.1546 |
| 11 | — | — | — | PASS | 0.2805 | 0.1652 |
