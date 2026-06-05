# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **formula**: `optimizer=formula` · `stopped_reason=first_fail` · iterations=13 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-12` · prov_cost_total=79.855525 (steady=79.776, best_pass=0.1108), util_cost_total=58.722378 (steady=58.68, best_pass=0.0815)
- **llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=18 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-17` · prov_cost_total=24.22182 (steady=24.12, best_pass=0.0335), util_cost_total=20.195638 (steady=20.16, best_pass=0.028)

## Resource delta (first row → last row)

| | 🟩 CPU req (m) | 🟧 Mem req (MiB) |
|---|---:|---:|
| formula | -94.0 | -43.0 |
| llm | -119.0 | -45.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | ⬜ formula prov cost | ⬜ formula util cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | 🟩 formula cpu m | 🟧 formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | ⬜ llm prov cost | ⬜ llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | 🟩 llm cpu m | 🟧 llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1562 | 6 | 0 | 55 | 22.5 | 11.7 | 150 | 75 | 300 | 150 | 5 | PASS | 0.7116 | 0.1429 | 6 | 0 | 55 | 20.5 | 12.3 | 150 | 75 | 300 | 150 | 5 |
| 2 | PASS | 0.5313 | 0.2172 | 6 | 0 | 55 | 41.9 | 21.9 | 112 | 56 | 224 | 112 | 5 | PASS | 0.6042 | 0.1767 | 6 | 0 | 55 | 30 | 16.1 | 127 | 67 | 300 | 135 | 5 |
| 3 | PASS | 0.3532 | 0.2225 | 6 | 0 | 55 | 64.6 | 33.8 | 93 | 47 | 185 | 93 | 4 | PASS | 0.5423 | 0.1663 | 6 | 0 | 55 | 31.2 | 21.4 | 114 | 60 | 300 | 135 | 5 |
| 4 | PASS | 0.338 | 0.1968 | 6 | 0 | 55 | 59.4 | 36.6 | 89 | 45 | 176 | 89 | 4 | PASS | 0.5129 | 0.1662 | 6 | 0 | 55 | 32.9 | 23.3 | 108 | 55 | 285 | 120 | 5 |
| 5 | PASS | 0.228 | 0.155 | 24 | 0 | 55 | 69.6 | 38.8 | 80 | 41 | 158 | 80 | 3 | PASS | 0.3795 | 0.1396 | 6 | 0 | 55 | 37.3 | 27.1 | 100 | 50 | 285 | 120 | 4 |
| 6 | PASS | 0.2166 | 0.137 | 20 | 0 | 55 | 64.9 | 33.7 | 76 | 39 | 151 | 76 | 3 | PASS | 0.3596 | 0.1122 | 6 | 0 | 55 | 31.6 | 23.4 | 95 | 45 | 285 | 120 | 4 |
| 7 | PASS | 0.1388 | 0.1151 | 41 | 0 | 55 | 84.7 | 50.7 | 73 | 38 | 144 | 73 | 2 | PASS | 0.213 | 0.0912 | 7 | 0 | 55 | 43.6 | 27.3 | 75 | 36 | 223 | 94 | 3 |
| 8 | PASS | 0.1332 | 0.1184 | 6 | 0 | 55 | 90.8 | 55.7 | 70 | 37 | 137 | 70 | 2 | PASS | 0.199 | 0.0746 | 6 | 0 | 55 | 38.1 | 25.9 | 70 | 34 | 223 | 94 | 3 |
| 9 | PASS | 0.1276 | 0.0887 | 4 | 0 | 55 | 71.2 | 39.9 | 67 | 36 | 131 | 67 | 2 | PASS | 0.1229 | 0.0807 | 6 | 0 | 55 | 66.8 | 42.9 | 65 | 30 | 200 | 90 | 2 |
| 10 | PASS | 0.122 | 0.0716 | 59 | 0 | 55 | 60.4 | 29.5 | 64 | 35 | 125 | 64 | 2 | PASS | 0.1103 | 0.0506 | 4 | 0 | 55 | 47.3 | 21.1 | 58 | 30 | 200 | 90 | 2 |
| 11 | PASS | 0.1164 | 0.0816 | 38 | 0 | 55 | 72.4 | 32.1 | 61 | 34 | 119 | 61 | 2 | PASS | 0.0524 | 0.0337 | 4 | 0 | 55 | 65.6 | 42 | 55 | 30 | 190 | 90 | 1 |
| 12 | PASS | 0.1108 | 0.0815 | 91 | 0 | 55 | 75.1 | 48.7 | 58 | 33 | 114 | 58 | 2 | PASS | 0.0479 | 0.0294 | 4 | 0 | 55 | 64 | 21.9 | 50 | 30 | 180 | 90 | 1 |
| 13 | FAIL | 0.0535 | 0.0535 | 53 | 0 | 55 | 148.4 | 98.8 | 56 | 32 | 109 | 56 | 1 | PASS | 0.0434 | 0.0265 | 4 | 0 | 55 | 63.8 | 21.9 | 45 | 30 | 180 | 90 | 1 |
| 14 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.0389 | 0.0265 | 4 | 0 | 55 | 71.7 | 22.1 | 40 | 30 | 162 | 90 | 1 |
| 15 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.0353 | 0.0261 | 4 | 0 | 55 | 78.5 | 22.4 | 36 | 30 | 146 | 90 | 1 |
| 16 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.0353 | 0.0257 | 4 | 0 | 55 | 77.5 | 21.7 | 36 | 30 | 146 | 90 | 1 |
| 17 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.0335 | 0.028 | 27 | 0 | 55 | 89.1 | 23.9 | 34 | 30 | 127 | 83 | 1 |
| 18 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.0308 | 0.0286 | 38 | 0 | 55 | 100.2 | 23.9 | 31 | 30 | 114 | 83 | 1 |

*Iteration count mismatch: formula=13, llm=18.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | formula status | ⬜ formula prov cost | ⬜ formula util cost | llm status | ⬜ llm prov cost | ⬜ llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1562 | PASS | 0.7116 | 0.1429 |
| 2 | PASS | 0.5313 | 0.2172 | PASS | 0.6042 | 0.1767 |
| 3 | PASS | 0.3532 | 0.2225 | PASS | 0.5423 | 0.1663 |
| 4 | PASS | 0.338 | 0.1968 | PASS | 0.5129 | 0.1662 |
| 5 | PASS | 0.228 | 0.155 | PASS | 0.3795 | 0.1396 |
| 6 | PASS | 0.2166 | 0.137 | PASS | 0.3596 | 0.1122 |
| 7 | PASS | 0.1388 | 0.1151 | PASS | 0.213 | 0.0912 |
| 8 | PASS | 0.1332 | 0.1184 | PASS | 0.199 | 0.0746 |
| 9 | PASS | 0.1276 | 0.0887 | PASS | 0.1229 | 0.0807 |
| 10 | PASS | 0.122 | 0.0716 | PASS | 0.1103 | 0.0506 |
| 11 | PASS | 0.1164 | 0.0816 | PASS | 0.0524 | 0.0337 |
| 12 | PASS | 0.1108 | 0.0815 | PASS | 0.0479 | 0.0294 |
| 13 | FAIL | 0.0535 | 0.0535 | PASS | 0.0434 | 0.0265 |
| 14 | — | — | — | PASS | 0.0389 | 0.0265 |
| 15 | — | — | — | PASS | 0.0353 | 0.0261 |
| 16 | — | — | — | PASS | 0.0353 | 0.0257 |
| 17 | — | — | — | PASS | 0.0335 | 0.028 |
| 18 | — | — | — | FAIL | 0.0308 | 0.0286 |
