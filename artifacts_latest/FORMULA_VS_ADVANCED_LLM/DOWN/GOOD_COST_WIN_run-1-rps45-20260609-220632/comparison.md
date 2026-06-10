# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **formula**: `optimizer=formula` · `stopped_reason=first_fail` · iterations=5 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-4` · prov_cost_total=196.826833 (steady=196.776, best_pass=0.2733), util_cost_total=85.121253 (steady=85.104, best_pass=0.1182)
- **llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=7 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-6` · prov_cost_total=123.041038 (steady=122.976, best_pass=0.1708), util_cost_total=53.730855 (steady=53.712, best_pass=0.0746)

## Resource delta (first row → last row)

| | 🟩 CPU req (m) | 🟧 Mem req (MiB) |
|---|---:|---:|
| formula | -89.0 | -43.0 |
| llm | -69.0 | -34.0 |

## Combined iterations

One row per iteration index (boundary `rows` order). Rows are **not** matched configs — each arm ran an independent squeeze trajectory. When `paired-baseline-probe.md` exists under each arm, **row 1** shares the same observed burn/cpu% (one k6 window, two optimizer analyses).

| # | formula status | ⬜ formula prov cost | ⬜ formula util cost | formula p95 | formula err | formula ach RPS | formula cpu% req | formula mem% | 🟩 formula cpu m | 🟧 formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | ⬜ llm prov cost | ⬜ llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% req | llm mem% | 🟩 llm cpu m | 🟧 llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1652 | 74 | 0 | 45 | 47.9 | 10.7 | 150 | 75 | 300 | 150 | 5 | PASS | 0.7116 | 0.1686 | 75 | 0 | 45 | 48.9 | 10.7 | 150 | 75 | 300 | 150 | 5 |
| 2 | PASS | 0.5363 | 0.1663 | 74 | 0 | 45 | 63.1 | 18.4 | 113 | 57 | 225 | 113 | 5 | PASS | 0.5122 | 0.1083 | 75 | 0 | 45 | 48.1 | 10.8 | 135 | 67 | 300 | 150 | 4 |
| 3 | PASS | 0.338 | 0.1182 | 74 | 0 | 45 | 70.9 | 18.3 | 89 | 45 | 176 | 89 | 4 | PASS | 0.4554 | 0.1096 | 74 | 0 | 45 | 52.8 | 8.7 | 120 | 60 | 255 | 135 | 4 |
| 4 | PASS | 0.2733 | 0.1182 | 74 | 0 | 45 | 87.6 | 16.5 | 72 | 36 | 141 | 72 | 4 | PASS | 0.3131 | 0.1138 | 75 | 0 | 45 | 78.7 | 13.2 | 110 | 55 | 230 | 120 | 3 |
| 5 | FAIL | 0.1741 | 0.1222 | 74 | 0 | 45 | 140.7 | 26.1 | 61 | 32 | 118 | 61 | 3 | PASS | 0.2846 | 0.1153 | 75 | 0 | 45 | 85.9 | 14.5 | 100 | 50 | 205 | 110 | 3 |
| 6 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.1708 | 0.0746 | 75 | 0 | 45 | 93 | 15.8 | 90 | 45 | 185 | 95 | 2 |
| 7 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.1538 | 0.064 | 75 | 0 | 45 | 98.3 | 15.7 | 81 | 41 | 185 | 95 | 2 |

*Iteration count mismatch: formula=5, llm=7.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | formula status | ⬜ formula prov cost | ⬜ formula util cost | llm status | ⬜ llm prov cost | ⬜ llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1652 | PASS | 0.7116 | 0.1686 |
| 2 | PASS | 0.5363 | 0.1663 | PASS | 0.5122 | 0.1083 |
| 3 | PASS | 0.338 | 0.1182 | PASS | 0.4554 | 0.1096 |
| 4 | PASS | 0.2733 | 0.1182 | PASS | 0.3131 | 0.1138 |
| 5 | FAIL | 0.1741 | 0.1222 | PASS | 0.2846 | 0.1153 |
| 6 | — | — | — | PASS | 0.1708 | 0.0746 |
| 7 | — | — | — | FAIL | 0.1538 | 0.064 |
