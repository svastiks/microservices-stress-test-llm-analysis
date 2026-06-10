# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **advanced-llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=6 · `best_pass_dir=/app/results/squeeze-compare-advanced-llm/run-1/iteration-5` · prov_cost_total=143.19457 (steady=143.136, best_pass=0.1988), util_cost_total=55.31512 (steady=55.296, best_pass=0.0768)
- **vanilla-llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=5 · `best_pass_dir=/app/results/squeeze-compare-vanilla-llm/run-1/iteration-4` · prov_cost_total=133.81959 (steady=133.776, best_pass=0.1858), util_cost_total=56.967705 (steady=56.952, best_pass=0.0791)

## Resource delta (first row → last row)

| | 🟩 CPU req (m) | 🟧 Mem req (MiB) |
|---|---:|---:|
| advanced-llm | -60.0 | -33.0 |
| vanilla-llm | -62.0 | -32.0 |

## Combined iterations

One row per iteration index (boundary `rows` order). Rows are **not** matched configs — each arm ran an independent squeeze trajectory. When `paired-baseline-probe.md` exists under each arm, **row 1** shares the same observed burn/cpu% (one k6 window, two optimizer analyses).

| # | advanced-llm status | ⬜ advanced-llm prov cost | ⬜ advanced-llm util cost | advanced-llm p95 | advanced-llm err | advanced-llm ach RPS | advanced-llm cpu% req | advanced-llm mem% | 🟩 advanced-llm cpu m | 🟧 advanced-llm mem Mi | advanced-llm cpu lim | advanced-llm mem lim | advanced-llm repl | vanilla-llm status | ⬜ vanilla-llm prov cost | ⬜ vanilla-llm util cost | vanilla-llm p95 | vanilla-llm err | vanilla-llm ach RPS | vanilla-llm cpu% req | vanilla-llm mem% | 🟩 vanilla-llm cpu m | 🟧 vanilla-llm mem Mi | vanilla-llm cpu lim | vanilla-llm mem lim | vanilla-llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.172 | 74 | 0 | 55 | 49.7 | 10.8 | 150 | 75 | 300 | 150 | 5 | PASS | 0.7116 | 0.1801 | 74 | 0 | 55 | 52.2 | 10.7 | 150 | 75 | 300 | 150 | 5 |
| 2 | PASS | 0.5106 | 0.1256 | 74 | 0 | 55 | 47.3 | 16.5 | 135 | 63 | 255 | 128 | 4 | PASS | 0.4554 | 0.1817 | 74 | 0 | 55 | 81.9 | 21.2 | 120 | 60 | 240 | 120 | 4 |
| 3 | PASS | 0.4535 | 0.1918 | 74 | 0 | 55 | 81.8 | 16.1 | 120 | 55 | 225 | 110 | 4 | PASS | 0.3074 | 0.1207 | 74 | 0 | 55 | 80.5 | 20.4 | 108 | 54 | 216 | 108 | 3 |
| 4 | PASS | 0.2981 | 0.1196 | 74 | 0 | 55 | 81.9 | 23.1 | 105 | 50 | 210 | 95 | 3 | PASS | 0.1858 | 0.0791 | 74 | 0 | 55 | 87.1 | 15.5 | 98 | 48 | 194 | 97 | 2 |
| 5 | PASS | 0.1988 | 0.0768 | 74 | 0 | 55 | 79.6 | 15.8 | 105 | 50 | 210 | 95 | 2 | FAIL | 0.0834 | 0.0666 | 6 | 0 | 55 | 145.9 | 24.8 | 88 | 43 | 155 | 78 | 1 |
| 6 | FAIL | 0.1702 | 0.079 | 75 | 0 | 55 | 95.6 | 18.8 | 90 | 42 | 180 | 80 | 2 | — | — | — | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: advanced-llm=6, vanilla-llm=5.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | advanced-llm status | ⬜ advanced-llm prov cost | ⬜ advanced-llm util cost | vanilla-llm status | ⬜ vanilla-llm prov cost | ⬜ vanilla-llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.172 | PASS | 0.7116 | 0.1801 |
| 2 | PASS | 0.5106 | 0.1256 | PASS | 0.4554 | 0.1817 |
| 3 | PASS | 0.4535 | 0.1918 | PASS | 0.3074 | 0.1207 |
| 4 | PASS | 0.2981 | 0.1196 | PASS | 0.1858 | 0.0791 |
| 5 | PASS | 0.1988 | 0.0768 | FAIL | 0.0834 | 0.0666 |
| 6 | FAIL | 0.1702 | 0.079 | — | — | — |
