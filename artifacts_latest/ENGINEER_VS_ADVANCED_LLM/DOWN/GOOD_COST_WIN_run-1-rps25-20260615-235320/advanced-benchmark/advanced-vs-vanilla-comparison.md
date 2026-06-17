# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **advanced-llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=6 · `best_pass_dir=/app/results/squeeze-compare-advanced-llm/run-1/iteration-5` · prov_cost_total=120.002428 (steady=119.952, best_pass=0.1666), util_cost_total=53.65744 (steady=53.64, best_pass=0.0745)
- **vanilla-llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=5 · `best_pass_dir=/app/results/squeeze-compare-vanilla-llm/run-1/iteration-4` · prov_cost_total=136.699883 (steady=136.656, best_pass=0.1898), util_cost_total=50.197137 (steady=50.184, best_pass=0.0697)

## Resource delta (first row → last row)

| | 🟩 CPU req (m) | 🟧 Mem req (MiB) |
|---|---:|---:|
| advanced-llm | -75.0 | -39.0 |
| vanilla-llm | -60.0 | -30.0 |

## Combined iterations

One row per iteration index (boundary `rows` order). Rows are **not** matched configs — each arm ran an independent squeeze trajectory. When `paired-baseline-probe.md` exists under each arm, **row 1** shares the same observed burn/cpu% (one k6 window, two optimizer analyses).

| # | advanced-llm status | ⬜ advanced-llm prov cost | ⬜ advanced-llm util cost | advanced-llm p95 | advanced-llm err | advanced-llm ach RPS | advanced-llm cpu% req | advanced-llm mem% | 🟩 advanced-llm cpu m | 🟧 advanced-llm mem Mi | advanced-llm cpu lim | advanced-llm mem lim | advanced-llm repl | vanilla-llm status | ⬜ vanilla-llm prov cost | ⬜ vanilla-llm util cost | vanilla-llm p95 | vanilla-llm err | vanilla-llm ach RPS | vanilla-llm cpu% req | vanilla-llm mem% | 🟩 vanilla-llm cpu m | 🟧 vanilla-llm mem Mi | vanilla-llm cpu lim | vanilla-llm mem lim | vanilla-llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1719 | 74 | 0 | 25 | 49.8 | 10.5 | 150 | 75 | 300 | 150 | 5 | PASS | 0.7116 | 0.1766 | 74 | 0 | 25 | 51.1 | 10.5 | 150 | 75 | 300 | 150 | 5 |
| 2 | PASS | 0.4858 | 0.1744 | 74 | 0 | 25 | 73.4 | 19.5 | 128 | 64 | 255 | 127 | 4 | PASS | 0.4554 | 0.1137 | 74 | 0 | 25 | 50.8 | 17 | 120 | 60 | 240 | 120 | 4 |
| 3 | PASS | 0.3215 | 0.1208 | 74 | 0 | 25 | 72.5 | 20.1 | 113 | 56 | 213 | 106 | 3 | PASS | 0.3131 | 0.1148 | 74 | 0 | 25 | 75.7 | 14.1 | 110 | 55 | 220 | 110 | 3 |
| 4 | PASS | 0.1896 | 0.0775 | 74 | 0 | 25 | 75.9 | 15.9 | 100 | 49 | 180 | 92 | 2 | PASS | 0.1898 | 0.0697 | 75 | 0 | 25 | 75.8 | 14.7 | 100 | 50 | 200 | 100 | 2 |
| 5 | PASS | 0.1666 | 0.0745 | 74 | 0 | 25 | 81.2 | 18.5 | 88 | 42 | 155 | 78 | 2 | FAIL | 0.0854 | 0.0507 | 5 | 0 | 25 | 123 | 20.8 | 90 | 45 | 180 | 90 | 1 |
| 6 | FAIL | 0.142 | 0.0785 | 74 | 0 | 25 | 100.3 | 22 | 75 | 36 | 132 | 66 | 2 | — | — | — | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: advanced-llm=6, vanilla-llm=5.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | advanced-llm status | ⬜ advanced-llm prov cost | ⬜ advanced-llm util cost | vanilla-llm status | ⬜ vanilla-llm prov cost | ⬜ vanilla-llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1719 | PASS | 0.7116 | 0.1766 |
| 2 | PASS | 0.4858 | 0.1744 | PASS | 0.4554 | 0.1137 |
| 3 | PASS | 0.3215 | 0.1208 | PASS | 0.3131 | 0.1148 |
| 4 | PASS | 0.1896 | 0.0775 | PASS | 0.1898 | 0.0697 |
| 5 | PASS | 0.1666 | 0.0745 | FAIL | 0.0854 | 0.0507 |
| 6 | FAIL | 0.142 | 0.0785 | — | — | — |
