# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **formula**: `optimizer=formula` · `stopped_reason=first_fail` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-2` · prov_cost_total=389.41595 (steady=389.376, best_pass=0.5408), util_cost_total=129.253665 (steady=129.24, best_pass=0.1795)
- **llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=6 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-5` · prov_cost_total=203.970907 (steady=203.904, best_pass=0.2832), util_cost_total=90.597508 (steady=90.576, best_pass=0.1258)

## Resource delta (first row → last row)

| | 🟩 CPU req (m) | 🟧 Mem req (MiB) |
|---|---:|---:|
| formula | -59.0 | -29.0 |
| llm | -60.0 | -35.0 |

## Combined iterations

One row per iteration index (boundary `rows` order). Rows are **not** matched configs — each arm ran an independent squeeze trajectory. When `paired-baseline-probe.md` exists under each arm, **row 1** shares the same observed burn/cpu% (one k6 window, two optimizer analyses).

| # | formula status | ⬜ formula prov cost | ⬜ formula util cost | formula p95 | formula err | formula ach RPS | formula cpu% req | formula mem% | 🟩 formula cpu m | 🟧 formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | ⬜ llm prov cost | ⬜ llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% req | llm mem% | 🟩 llm cpu m | 🟧 llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.183 | 74 | 0 | 55 | 52.7 | 13 | 150 | 75 | 300 | 150 | 5 | PASS | 0.7116 | 0.1776 | 74 | 0 | 55 | 51.2 | 13.2 | 150 | 75 | 300 | 150 | 5 |
| 2 | PASS | 0.5408 | 0.1795 | 74 | 0 | 55 | 68.1 | 18.3 | 114 | 57 | 228 | 114 | 5 | PASS | 0.6383 | 0.1764 | 74 | 0 | 55 | 56.5 | 16.4 | 135 | 63 | 270 | 127 | 5 |
| 3 | FAIL | 0.3456 | 0.1841 | 74 | 0 | 55 | 108.9 | 27.3 | 91 | 46 | 181 | 91 | 4 | PASS | 0.4579 | 0.1155 | 74 | 0 | 55 | 51.6 | 16 | 121 | 57 | 243 | 111 | 4 |
| 4 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.4155 | 0.1819 | 74 | 0 | 55 | 90.2 | 17.1 | 110 | 50 | 220 | 100 | 4 |
| 5 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.2832 | 0.1258 | 75 | 0 | 55 | 90.8 | 24.5 | 100 | 45 | 200 | 90 | 3 |
| 6 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.1698 | 0.0831 | 75 | 0 | 55 | 100.8 | 18.4 | 90 | 40 | 180 | 81 | 2 |

*Iteration count mismatch: formula=3, llm=6.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | formula status | ⬜ formula prov cost | ⬜ formula util cost | llm status | ⬜ llm prov cost | ⬜ llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.183 | PASS | 0.7116 | 0.1776 |
| 2 | PASS | 0.5408 | 0.1795 | PASS | 0.6383 | 0.1764 |
| 3 | FAIL | 0.3456 | 0.1841 | PASS | 0.4579 | 0.1155 |
| 4 | — | — | — | PASS | 0.4155 | 0.1819 |
| 5 | — | — | — | PASS | 0.2832 | 0.1258 |
| 6 | — | — | — | FAIL | 0.1698 | 0.0831 |
