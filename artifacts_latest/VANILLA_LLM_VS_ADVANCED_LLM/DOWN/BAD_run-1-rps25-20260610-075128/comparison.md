# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **advanced-llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=5 · `best_pass_dir=/app/results/squeeze-compare-advanced-llm/run-1/iteration-4` · prov_cost_total=190.781468 (steady=190.728, best_pass=0.2649), util_cost_total=72.664457 (steady=72.648, best_pass=0.1009)
- **vanilla-llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=5 · `best_pass_dir=/app/results/squeeze-compare-vanilla-llm/run-1/iteration-4` · prov_cost_total=135.979807 (steady=135.936, best_pass=0.1888), util_cost_total=50.269085 (steady=50.256, best_pass=0.0698)

## Resource delta (first row → last row)

| | 🟩 CPU req (m) | 🟧 Mem req (MiB) |
|---|---:|---:|
| advanced-llm | -76.0 | -35.0 |
| vanilla-llm | -60.0 | -35.0 |

## Combined iterations

One row per iteration index (boundary `rows` order). Rows are **not** matched configs — each arm ran an independent squeeze trajectory. When `paired-baseline-probe.md` exists under each arm, **row 1** shares the same observed burn/cpu% (one k6 window, two optimizer analyses).

| # | advanced-llm status | ⬜ advanced-llm prov cost | ⬜ advanced-llm util cost | advanced-llm p95 | advanced-llm err | advanced-llm ach RPS | advanced-llm cpu% req | advanced-llm mem% | 🟩 advanced-llm cpu m | 🟧 advanced-llm mem Mi | advanced-llm cpu lim | advanced-llm mem lim | advanced-llm repl | vanilla-llm status | ⬜ vanilla-llm prov cost | ⬜ vanilla-llm util cost | vanilla-llm p95 | vanilla-llm err | vanilla-llm ach RPS | vanilla-llm cpu% req | vanilla-llm mem% | 🟩 vanilla-llm cpu m | 🟧 vanilla-llm mem Mi | vanilla-llm cpu lim | vanilla-llm mem lim | vanilla-llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1761 | 74 | 0 | 25 | 50.7 | 12.7 | 150 | 75 | 300 | 150 | 5 | PASS | 0.7116 | 0.1753 | 74 | 0 | 25 | 50.9 | 10.5 | 150 | 75 | 300 | 150 | 5 |
| 2 | PASS | 0.6073 | 0.1741 | 74 | 0 | 25 | 58.7 | 13.4 | 128 | 64 | 255 | 127 | 5 | PASS | 0.4554 | 0.1102 | 74 | 0 | 25 | 49.1 | 16.9 | 120 | 60 | 240 | 120 | 4 |
| 3 | PASS | 0.4139 | 0.1487 | 74 | 0 | 25 | 86.6 | 16.4 | 109 | 55 | 255 | 127 | 4 | PASS | 0.3116 | 0.1121 | 74 | 0 | 25 | 74.1 | 15.3 | 110 | 50 | 220 | 100 | 3 |
| 4 | PASS | 0.2649 | 0.1009 | 74 | 0 | 25 | 90.3 | 19.8 | 93 | 47 | 215 | 108 | 3 | PASS | 0.1888 | 0.0698 | 74 | 0 | 25 | 76 | 16.2 | 100 | 45 | 200 | 90 | 2 |
| 5 | FAIL | 0.141 | 0.0585 | 74 | 0 | 25 | 105.6 | 16.8 | 74 | 40 | 182 | 87 | 2 | FAIL | 0.0849 | 0.056 | 5 | 0 | 25 | 120.9 | 23.2 | 90 | 40 | 160 | 80 | 1 |

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | advanced-llm status | ⬜ advanced-llm prov cost | ⬜ advanced-llm util cost | vanilla-llm status | ⬜ vanilla-llm prov cost | ⬜ vanilla-llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1761 | PASS | 0.7116 | 0.1753 |
| 2 | PASS | 0.6073 | 0.1741 | PASS | 0.4554 | 0.1102 |
| 3 | PASS | 0.4139 | 0.1487 | PASS | 0.3116 | 0.1121 |
| 4 | PASS | 0.2649 | 0.1009 | PASS | 0.1888 | 0.0698 |
| 5 | FAIL | 0.141 | 0.0585 | FAIL | 0.0849 | 0.056 |
