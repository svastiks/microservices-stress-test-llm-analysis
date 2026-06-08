# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **formula**: `optimizer=formula` · `stopped_reason=first_fail` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-2` · prov_cost_total=372.566985 (steady=372.528, best_pass=0.5174), util_cost_total=122.843568 (steady=122.832, best_pass=0.1706)
- **llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=7 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-6` · prov_cost_total=184.536908 (steady=184.464, best_pass=0.2562), util_cost_total=74.328558 (steady=74.304, best_pass=0.1032)

## Resource delta (first row → last row)

| | 🟩 CPU req (m) | 🟧 Mem req (MiB) |
|---|---:|---:|
| formula | -63.0 | -31.0 |
| llm | -70.0 | -35.0 |

## Combined iterations

One row per iteration index (boundary `rows` order). Rows are **not** matched configs — each arm ran an independent squeeze trajectory.

| # | formula status | ⬜ formula prov cost | ⬜ formula util cost | formula p95 | formula err | formula ach RPS | formula cpu% req | formula mem% | 🟩 formula cpu m | 🟧 formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | ⬜ llm prov cost | ⬜ llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% req | llm mem% | 🟩 llm cpu m | 🟧 llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1183 | 6 | 0 | 25 | 34 | 9.6 | 150 | 75 | 300 | 150 | 5 | PASS | 0.7116 | 0.1671 | 6 | 0 | 25 | 48 | 14 | 150 | 75 | 300 | 150 | 5 |
| 2 | PASS | 0.5174 | 0.1706 | 6 | 0 | 25 | 67.5 | 16.1 | 109 | 55 | 217 | 109 | 5 | PASS | 0.6392 | 0.1698 | 6 | 0 | 25 | 54.7 | 12.6 | 135 | 65 | 270 | 135 | 5 |
| 3 | FAIL | 0.3304 | 0.1738 | 6 | 0 | 25 | 107 | 25.2 | 87 | 44 | 172 | 87 | 4 | PASS | 0.4554 | 0.1645 | 6 | 0 | 25 | 71.1 | 17.9 | 120 | 60 | 230 | 120 | 4 |
| 4 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.4175 | 0.1456 | 6 | 0 | 25 | 66.8 | 15.8 | 110 | 55 | 205 | 110 | 4 |
| 5 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.2846 | 0.1328 | 6 | 0 | 25 | 88.3 | 27.1 | 100 | 50 | 185 | 95 | 3 |
| 6 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.2562 | 0.1032 | 5 | 0 | 25 | 74.1 | 14.5 | 90 | 45 | 160 | 85 | 3 |
| 7 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.1518 | 0.0993 | 6 | 0 | 25 | 122.4 | 27.1 | 80 | 40 | 145 | 75 | 2 |

*Iteration count mismatch: formula=3, llm=7.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | formula status | ⬜ formula prov cost | ⬜ formula util cost | llm status | ⬜ llm prov cost | ⬜ llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1183 | PASS | 0.7116 | 0.1671 |
| 2 | PASS | 0.5174 | 0.1706 | PASS | 0.6392 | 0.1698 |
| 3 | FAIL | 0.3304 | 0.1738 | PASS | 0.4554 | 0.1645 |
| 4 | — | — | — | PASS | 0.4175 | 0.1456 |
| 5 | — | — | — | PASS | 0.2846 | 0.1328 |
| 6 | — | — | — | PASS | 0.2562 | 0.1032 |
| 7 | — | — | — | FAIL | 0.1518 | 0.0993 |
