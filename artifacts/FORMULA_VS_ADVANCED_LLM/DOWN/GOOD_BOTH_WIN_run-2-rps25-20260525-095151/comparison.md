# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **formula**: `optimizer=formula` · `stopped_reason=first_fail` · iterations=13 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-12` · prov_cost_total=121.779203 (steady=121.68, best_pass=0.169), util_cost_total=94.808555 (steady=94.752, best_pass=0.1316)
- **llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=10 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-9` · prov_cost_total=20.933712 (steady=20.88, best_pass=0.029), util_cost_total=16.721917 (steady=16.704, best_pass=0.0232)

## Resource delta (first row → last row)

| | 🟩 CPU req (m) | 🟧 Mem req (MiB) |
|---|---:|---:|
| formula | -93.0 | -43.0 |
| llm | -138.0 | -66.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | ⬜ formula prov cost | ⬜ formula util cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | 🟩 formula cpu m | 🟧 formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | ⬜ llm prov cost | ⬜ llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | 🟩 llm cpu m | 🟧 llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1732 | 6 | 0 | 25 | 24.9 | 14.1 | 150 | 75 | 300 | 150 | 5 | PASS | 0.7116 | 0.1739 | 7 | 0 | 25 | 25 | 14.1 | 150 | 75 | 300 | 150 | 5 |
| 2 | PASS | 0.5408 | 0.2296 | 6 | 0 | 25 | 43.6 | 21.3 | 114 | 57 | 227 | 114 | 5 | PASS | 0.4744 | 0.1524 | 6 | 0 | 25 | 33 | 16.1 | 100 | 50 | 300 | 150 | 5 |
| 3 | PASS | 0.3608 | 0.2363 | 6 | 0 | 25 | 67.3 | 32.5 | 95 | 48 | 189 | 95 | 4 | PASS | 0.3795 | 0.1267 | 6 | 0 | 25 | 34.3 | 16.4 | 80 | 40 | 300 | 150 | 5 |
| 4 | PASS | 0.3456 | 0.213 | 6 | 0 | 25 | 63.1 | 35.2 | 91 | 46 | 180 | 91 | 4 | PASS | 0.1917 | 0.0682 | 6 | 0 | 25 | 36.5 | 21.2 | 50 | 30 | 300 | 150 | 4 |
| 5 | PASS | 0.3304 | 0.1742 | 6 | 0 | 25 | 54 | 29.5 | 87 | 44 | 171 | 87 | 4 | PASS | 0.1538 | 0.0556 | 6 | 0 | 25 | 37.2 | 21.3 | 40 | 25 | 250 | 125 | 4 |
| 6 | PASS | 0.2924 | 0.1706 | 28 | 0 | 25 | 60 | 28.2 | 77 | 39 | 150 | 77 | 4 | PASS | 0.0869 | 0.0398 | 6 | 0 | 25 | 47.4 | 24 | 30 | 20 | 250 | 125 | 3 |
| 7 | PASS | 0.2812 | 0.1678 | 28 | 0 | 25 | 61.3 | 30 | 74 | 38 | 143 | 74 | 4 | PASS | 0.0719 | 0.0388 | 7 | 0 | 25 | 55.9 | 23.8 | 25 | 15 | 200 | 100 | 3 |
| 8 | PASS | 0.2701 | 0.1679 | 31 | 0 | 25 | 63.9 | 31.3 | 71 | 37 | 136 | 71 | 4 | PASS | 0.038 | 0.0268 | 6 | 0 | 25 | 72.6 | 35.4 | 20 | 10 | 200 | 100 | 2 |
| 9 | PASS | 0.1941 | 0.1679 | 65 | 0 | 25 | 89 | 42.7 | 68 | 36 | 130 | 68 | 3 | PASS | 0.029 | 0.0232 | 69 | 0 | 25 | 84.1 | 27.3 | 15 | 10 | 150 | 100 | 2 |
| 10 | PASS | 0.1858 | 0.1662 | 59 | 0 | 25 | 92 | 46.7 | 65 | 35 | 124 | 65 | 3 | FAIL | 0.0117 | 0.0113 | 118 | 0 | 25 | 160.7 | 62.1 | 12 | 9 | 120 | 90 | 1 |
| 11 | PASS | 0.1774 | 0.1574 | 93 | 0 | 25 | 91.7 | 38.6 | 62 | 34 | 118 | 62 | 3 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 12 | PASS | 0.169 | 0.1316 | 84 | 0 | 25 | 79.6 | 50.1 | 59 | 33 | 113 | 59 | 3 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 13 | FAIL | 0.1089 | 0.1065 | 81 | 0 | 25 | 126.4 | 62.3 | 57 | 32 | 108 | 57 | 2 | — | — | — | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: formula=13, llm=10.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | formula status | ⬜ formula prov cost | ⬜ formula util cost | llm status | ⬜ llm prov cost | ⬜ llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1732 | PASS | 0.7116 | 0.1739 |
| 2 | PASS | 0.5408 | 0.2296 | PASS | 0.4744 | 0.1524 |
| 3 | PASS | 0.3608 | 0.2363 | PASS | 0.3795 | 0.1267 |
| 4 | PASS | 0.3456 | 0.213 | PASS | 0.1917 | 0.0682 |
| 5 | PASS | 0.3304 | 0.1742 | PASS | 0.1538 | 0.0556 |
| 6 | PASS | 0.2924 | 0.1706 | PASS | 0.0869 | 0.0398 |
| 7 | PASS | 0.2812 | 0.1678 | PASS | 0.0719 | 0.0388 |
| 8 | PASS | 0.2701 | 0.1679 | PASS | 0.038 | 0.0268 |
| 9 | PASS | 0.1941 | 0.1679 | PASS | 0.029 | 0.0232 |
| 10 | PASS | 0.1858 | 0.1662 | FAIL | 0.0117 | 0.0113 |
| 11 | PASS | 0.1774 | 0.1574 | — | — | — |
| 12 | PASS | 0.169 | 0.1316 | — | — | — |
| 13 | FAIL | 0.1089 | 0.1065 | — | — | — |
