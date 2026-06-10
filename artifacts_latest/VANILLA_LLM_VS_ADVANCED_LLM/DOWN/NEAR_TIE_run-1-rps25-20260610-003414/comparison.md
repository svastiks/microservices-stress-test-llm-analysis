# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **advanced-llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=6 · `best_pass_dir=/app/results/squeeze-compare-advanced-llm/run-1/iteration-5` · prov_cost_total=126.914035 (steady=126.864, best_pass=0.1762), util_cost_total=59.993505 (steady=59.976, best_pass=0.0833)
- **vanilla-llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=6 · `best_pass_dir=/app/results/squeeze-compare-vanilla-llm/run-1/iteration-5` · prov_cost_total=123.025813 (steady=122.976, best_pass=0.1708), util_cost_total=52.287758 (steady=52.272, best_pass=0.0726)

## Resource delta (first row → last row)

| | 🟩 CPU req (m) | 🟧 Mem req (MiB) |
|---|---:|---:|
| advanced-llm | -65.0 | -35.0 |
| vanilla-llm | -70.0 | -35.0 |

## Combined iterations

One row per iteration index (boundary `rows` order). Rows are **not** matched configs — each arm ran an independent squeeze trajectory. When `paired-baseline-probe.md` exists under each arm, **row 1** shares the same observed burn/cpu% (one k6 window, two optimizer analyses).

| # | advanced-llm status | ⬜ advanced-llm prov cost | ⬜ advanced-llm util cost | advanced-llm p95 | advanced-llm err | advanced-llm ach RPS | advanced-llm cpu% req | advanced-llm mem% | 🟩 advanced-llm cpu m | 🟧 advanced-llm mem Mi | advanced-llm cpu lim | advanced-llm mem lim | advanced-llm repl | vanilla-llm status | ⬜ vanilla-llm prov cost | ⬜ vanilla-llm util cost | vanilla-llm p95 | vanilla-llm err | vanilla-llm ach RPS | vanilla-llm cpu% req | vanilla-llm mem% | 🟩 vanilla-llm cpu m | 🟧 vanilla-llm mem Mi | vanilla-llm cpu lim | vanilla-llm mem lim | vanilla-llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1712 | 74 | 0 | 25 | 49.6 | 10.5 | 150 | 75 | 300 | 150 | 5 | PASS | 0.7116 | 0.1739 | 74 | 0 | 25 | 50.5 | 10.5 | 150 | 75 | 300 | 150 | 5 |
| 2 | PASS | 0.5114 | 0.1856 | 74 | 0 | 25 | 70.3 | 18.9 | 135 | 65 | 255 | 128 | 4 | PASS | 0.4554 | 0.116 | 74 | 0 | 25 | 51.8 | 17.4 | 120 | 60 | 240 | 120 | 4 |
| 3 | PASS | 0.3266 | 0.124 | 74 | 0 | 25 | 73.1 | 19.8 | 115 | 55 | 216 | 109 | 3 | PASS | 0.3131 | 0.1169 | 74 | 0 | 25 | 77.2 | 14.1 | 110 | 55 | 220 | 110 | 3 |
| 4 | PASS | 0.1952 | 0.079 | 75 | 0 | 25 | 79 | 14.9 | 103 | 50 | 195 | 98 | 2 | PASS | 0.1898 | 0.0743 | 75 | 0 | 25 | 81.1 | 14.7 | 100 | 50 | 200 | 100 | 2 |
| 5 | PASS | 0.1762 | 0.0833 | 75 | 0 | 25 | 86.8 | 16.6 | 93 | 45 | 165 | 88 | 2 | PASS | 0.1708 | 0.0726 | 75 | 0 | 25 | 87.9 | 16.4 | 90 | 45 | 180 | 90 | 2 |
| 6 | FAIL | 0.0804 | 0.0571 | 5 | 0 | 25 | 129.5 | 23.1 | 85 | 40 | 150 | 80 | 1 | FAIL | 0.1518 | 0.0766 | 75 | 0 | 25 | 104.4 | 18.3 | 80 | 40 | 160 | 80 | 2 |

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | advanced-llm status | ⬜ advanced-llm prov cost | ⬜ advanced-llm util cost | vanilla-llm status | ⬜ vanilla-llm prov cost | ⬜ vanilla-llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1712 | PASS | 0.7116 | 0.1739 |
| 2 | PASS | 0.5114 | 0.1856 | PASS | 0.4554 | 0.116 |
| 3 | PASS | 0.3266 | 0.124 | PASS | 0.3131 | 0.1169 |
| 4 | PASS | 0.1952 | 0.079 | PASS | 0.1898 | 0.0743 |
| 5 | PASS | 0.1762 | 0.0833 | PASS | 0.1708 | 0.0726 |
| 6 | FAIL | 0.0804 | 0.0571 | FAIL | 0.1518 | 0.0766 |
