# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **formula**: `optimizer=formula` · `stopped_reason=first_fail` · iterations=5 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-4` · prov_cost_total=205.107533 (steady=205.056, best_pass=0.2848), util_cost_total=93.690423 (steady=93.672, best_pass=0.1301)
- **llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=6 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-5` · prov_cost_total=198.132465 (steady=198.072, best_pass=0.2751), util_cost_total=65.106875 (steady=65.088, best_pass=0.0904)

## Resource delta (first row → last row)

| | 🟩 CPU req (m) | 🟧 Mem req (MiB) |
|---|---:|---:|
| formula | -86.0 | -42.0 |
| llm | -65.0 | -35.0 |

## Combined iterations

One row per iteration index (boundary `rows` order). Rows are **not** matched configs — each arm ran an independent squeeze trajectory. When `paired-baseline-probe.md` exists under each arm, **row 1** shares the same observed burn/cpu% (one k6 window, two optimizer analyses).

| # | formula status | ⬜ formula prov cost | ⬜ formula util cost | formula p95 | formula err | formula ach RPS | formula cpu% req | formula mem% | 🟩 formula cpu m | 🟧 formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | ⬜ llm prov cost | ⬜ llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% req | llm mem% | 🟩 llm cpu m | 🟧 llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1817 | 6 | 0 | 25 | 52.1 | 15.2 | 150 | 75 | 300 | 150 | 5 | PASS | 0.7116 | 0.154 | 6 | 0 | 25 | 44.3 | 11.4 | 150 | 75 | 300 | 150 | 5 |
| 2 | PASS | 0.5408 | 0.1673 | 6 | 0 | 25 | 63.5 | 16.9 | 114 | 57 | 228 | 114 | 5 | PASS | 0.5114 | 0.1588 | 6 | 0 | 25 | 60 | 16.6 | 135 | 65 | 255 | 135 | 4 |
| 3 | PASS | 0.3416 | 0.1443 | 6 | 0 | 25 | 86.2 | 21 | 90 | 45 | 179 | 90 | 4 | PASS | 0.4535 | 0.1416 | 6 | 0 | 25 | 61.4 | 15.7 | 120 | 55 | 230 | 120 | 4 |
| 4 | PASS | 0.2848 | 0.1301 | 6 | 0 | 25 | 93 | 25.3 | 75 | 38 | 149 | 75 | 4 | PASS | 0.3062 | 0.1181 | 6 | 0 | 25 | 76.2 | 16.2 | 108 | 50 | 207 | 110 | 3 |
| 5 | FAIL | 0.1825 | 0.1135 | 6 | 0 | 25 | 126.2 | 28.3 | 64 | 33 | 126 | 64 | 3 | PASS | 0.2751 | 0.0904 | 6 | 0 | 25 | 61.8 | 12.5 | 97 | 45 | 177 | 95 | 3 |
| 6 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.1608 | 0.0921 | 5 | 0 | 25 | 111.3 | 21.5 | 85 | 40 | 160 | 85 | 2 |

*Iteration count mismatch: formula=5, llm=6.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | formula status | ⬜ formula prov cost | ⬜ formula util cost | llm status | ⬜ llm prov cost | ⬜ llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1817 | PASS | 0.7116 | 0.154 |
| 2 | PASS | 0.5408 | 0.1673 | PASS | 0.5114 | 0.1588 |
| 3 | PASS | 0.3416 | 0.1443 | PASS | 0.4535 | 0.1416 |
| 4 | PASS | 0.2848 | 0.1301 | PASS | 0.3062 | 0.1181 |
| 5 | FAIL | 0.1825 | 0.1135 | PASS | 0.2751 | 0.0904 |
| 6 | — | — | — | FAIL | 0.1608 | 0.0921 |
