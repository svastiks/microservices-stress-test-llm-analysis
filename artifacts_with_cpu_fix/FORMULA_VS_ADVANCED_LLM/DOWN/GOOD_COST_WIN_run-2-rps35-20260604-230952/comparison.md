# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **formula**: `optimizer=formula` · `stopped_reason=first_fail` · iterations=5 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-4` · prov_cost_total=249.60908 (steady=249.552, best_pass=0.3466), util_cost_total=115.14811 (steady=115.128, best_pass=0.1599)
- **llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=6 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-5` · prov_cost_total=194.24612 (steady=194.184, best_pass=0.2697), util_cost_total=85.484695 (steady=85.464, best_pass=0.1187)

## Resource delta (first row → last row)

| | 🟩 CPU req (m) | 🟧 Mem req (MiB) |
|---|---:|---:|
| formula | -88.0 | -43.0 |
| llm | -64.0 | -35.0 |

## Combined iterations

One row per iteration index (boundary `rows` order). Rows are **not** matched configs — each arm ran an independent squeeze trajectory.

| # | formula status | ⬜ formula prov cost | ⬜ formula util cost | formula p95 | formula err | formula ach RPS | formula cpu% req | formula mem% | 🟩 formula cpu m | 🟧 formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | ⬜ llm prov cost | ⬜ llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% req | llm mem% | 🟩 llm cpu m | 🟧 llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1257 | 6 | 0 | 35 | 36.1 | 11.6 | 150 | 75 | 300 | 150 | 5 | PASS | 0.7116 | 0.1644 | 6 | 0 | 35 | 47.2 | 13.8 | 150 | 75 | 300 | 150 | 5 |
| 2 | PASS | 0.5174 | 0.1773 | 6 | 0 | 35 | 70.2 | 19 | 109 | 55 | 218 | 109 | 5 | PASS | 0.6073 | 0.1667 | 6 | 0 | 35 | 56.1 | 13.7 | 128 | 64 | 255 | 128 | 5 |
| 3 | PASS | 0.413 | 0.1805 | 6 | 0 | 35 | 90 | 20.2 | 87 | 44 | 174 | 87 | 5 | PASS | 0.4355 | 0.1556 | 6 | 0 | 35 | 73.2 | 19 | 115 | 55 | 230 | 115 | 4 |
| 4 | PASS | 0.3466 | 0.1599 | 6 | 0 | 35 | 94.2 | 28.5 | 73 | 37 | 146 | 73 | 5 | PASS | 0.2981 | 0.1379 | 6 | 0 | 35 | 94.8 | 24.2 | 105 | 50 | 210 | 100 | 3 |
| 5 | FAIL | 0.2946 | 0.161 | 6 | 0 | 35 | 112.2 | 28.4 | 62 | 32 | 124 | 62 | 5 | PASS | 0.2697 | 0.1187 | 6 | 0 | 35 | 89.5 | 28.9 | 95 | 45 | 190 | 90 | 3 |
| 6 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.1626 | 0.0845 | 6 | 0 | 35 | 107.2 | 13.1 | 86 | 40 | 171 | 81 | 2 |

*Iteration count mismatch: formula=5, llm=6.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | formula status | ⬜ formula prov cost | ⬜ formula util cost | llm status | ⬜ llm prov cost | ⬜ llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1257 | PASS | 0.7116 | 0.1644 |
| 2 | PASS | 0.5174 | 0.1773 | PASS | 0.6073 | 0.1667 |
| 3 | PASS | 0.413 | 0.1805 | PASS | 0.4355 | 0.1556 |
| 4 | PASS | 0.3466 | 0.1599 | PASS | 0.2981 | 0.1379 |
| 5 | FAIL | 0.2946 | 0.161 | PASS | 0.2697 | 0.1187 |
| 6 | — | — | — | FAIL | 0.1626 | 0.0845 |
