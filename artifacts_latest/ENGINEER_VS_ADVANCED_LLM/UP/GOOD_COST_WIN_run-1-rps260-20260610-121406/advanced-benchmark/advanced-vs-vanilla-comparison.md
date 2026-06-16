# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **advanced-llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=10 · `best_pass_dir=/app/results/squeeze-compare-advanced-llm/run-1/iteration-10` · prov_cost_total=186.44732 (steady=186.408, best_pass=0.2589), util_cost_total=85.633375 (steady=85.608, best_pass=0.1189)
- **vanilla-llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=6 · `best_pass_dir=/app/results/squeeze-compare-vanilla-llm/run-1/iteration-6` · prov_cost_total=246.770913 (steady=246.744, best_pass=0.3427), util_cost_total=121.48143 (steady=121.464, best_pass=0.1687)

## Resource delta (first row → last row)

| | 🟩 CPU req (m) | 🟧 Mem req (MiB) |
|---|---:|---:|
| advanced-llm | +86.0 | +47.0 |
| vanilla-llm | +70.0 | +39.0 |

## Combined iterations

One row per iteration index (boundary `rows` order). Rows are **not** matched configs — each arm ran an independent squeeze trajectory. When `paired-baseline-probe.md` exists under each arm, **row 1** shares the same observed burn/cpu% (one k6 window, two optimizer analyses).

| # | advanced-llm status | ⬜ advanced-llm prov cost | ⬜ advanced-llm util cost | advanced-llm p95 | advanced-llm err | advanced-llm ach RPS | advanced-llm cpu% req | advanced-llm mem% | 🟩 advanced-llm cpu m | 🟧 advanced-llm mem Mi | advanced-llm cpu lim | advanced-llm mem lim | advanced-llm repl | vanilla-llm status | ⬜ vanilla-llm prov cost | ⬜ vanilla-llm util cost | vanilla-llm p95 | vanilla-llm err | vanilla-llm ach RPS | vanilla-llm cpu% req | vanilla-llm mem% | 🟩 vanilla-llm cpu m | 🟧 vanilla-llm mem Mi | vanilla-llm cpu lim | vanilla-llm mem lim | vanilla-llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0425 | 4138 | 0 | 254.4 | 178.8 | 93.7 | 50 | 25 | 100 | 50 | 1 | FAIL | 0.0474 | 0.0453 | 2411 | 0 | 257.3 | 191.4 | 92.9 | 50 | 25 | 100 | 50 | 1 |
| 2 | FAIL | 0.0949 | 0.0868 | 676 | 0 | 260 | 187.4 | 51.2 | 50 | 25 | 100 | 50 | 2 | FAIL | 0.1139 | 0.0942 | 588 | 0 | 260 | 170 | 41.2 | 60 | 30 | 120 | 60 | 2 |
| 3 | FAIL | 0.1101 | 0.0968 | 453 | 0 | 260 | 179.5 | 41.8 | 58 | 29 | 115 | 57 | 2 | FAIL | 0.1366 | 0.1084 | 434 | 0 | 260 | 164 | 30.9 | 72 | 36 | 144 | 72 | 2 |
| 4 | FAIL | 0.1272 | 0.1042 | 611 | 0 | 260 | 166.5 | 34.2 | 67 | 34 | 132 | 66 | 2 | FAIL | 0.1518 | 0.11 | 586 | 0 | 260 | 149.9 | 27.1 | 80 | 40 | 160 | 80 | 2 |
| 5 | FAIL | 0.1416 | 0.1093 | 424 | 0 | 260 | 159.9 | 31.9 | 75 | 34 | 151 | 66 | 2 | FAIL | 0.2841 | 0.1706 | 328 | 0 | 260 | 112 | 19.1 | 100 | 48 | 180 | 96 | 3 |
| 6 | FAIL | 0.1624 | 0.1107 | 410 | 0 | 260 | 141.2 | 26.4 | 86 | 39 | 173 | 76 | 2 | PASS | 0.3427 | 0.1687 | 327 | 0 | 260 | 93.7 | 16.5 | 120 | 64 | 220 | 112 | 3 |
| 7 | FAIL | 0.187 | 0.116 | 1073 | 0 | 259.9 | 128.7 | 22.3 | 99 | 45 | 199 | 88 | 2 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 8 | FAIL | 0.2116 | 0.1134 | 645 | 0 | 260 | 112.5 | 18.9 | 112 | 51 | 228 | 102 | 2 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 9 | FAIL | 0.2317 | 0.1164 | 512 | 0 | 260 | 105 | 16.2 | 122 | 62 | 246 | 118 | 2 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 10 | PASS | 0.2589 | 0.1189 | 415 | 0 | 260 | 91.7 | 13.6 | 136 | 72 | 261 | 138 | 2 | — | — | — | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: advanced-llm=10, vanilla-llm=6.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | advanced-llm status | ⬜ advanced-llm prov cost | ⬜ advanced-llm util cost | vanilla-llm status | ⬜ vanilla-llm prov cost | ⬜ vanilla-llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0425 | FAIL | 0.0474 | 0.0453 |
| 2 | FAIL | 0.0949 | 0.0868 | FAIL | 0.1139 | 0.0942 |
| 3 | FAIL | 0.1101 | 0.0968 | FAIL | 0.1366 | 0.1084 |
| 4 | FAIL | 0.1272 | 0.1042 | FAIL | 0.1518 | 0.11 |
| 5 | FAIL | 0.1416 | 0.1093 | FAIL | 0.2841 | 0.1706 |
| 6 | FAIL | 0.1624 | 0.1107 | PASS | 0.3427 | 0.1687 |
| 7 | FAIL | 0.187 | 0.116 | — | — | — |
| 8 | FAIL | 0.2116 | 0.1134 | — | — | — |
| 9 | FAIL | 0.2317 | 0.1164 | — | — | — |
| 10 | PASS | 0.2589 | 0.1189 | — | — | — |
