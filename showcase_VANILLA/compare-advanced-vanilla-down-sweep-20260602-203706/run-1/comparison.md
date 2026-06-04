# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **advanced-llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-advanced-llm/run-1/iteration-2` · prov_cost_total=341.607138 (steady=341.568, best_pass=0.4744), util_cost_total=202.412493 (steady=202.392, best_pass=0.2811)
- **vanilla-llm**: `optimizer=llm` · `stopped_reason=empty_recommended_diff` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-vanilla-llm/run-1/iteration-3` · prov_cost_total=273.279138 (steady=273.24, best_pass=0.3795), util_cost_total=126.22881 (steady=126.216, best_pass=0.1753)

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| advanced-llm | -50.0 | -25.0 |
| vanilla-llm | -70.0 | -35.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | advanced-llm status | advanced-llm prov cost | advanced-llm util cost | advanced-llm p95 | advanced-llm err | advanced-llm ach RPS | advanced-llm cpu% | advanced-llm mem% | advanced-llm cpu m | advanced-llm mem Mi | advanced-llm cpu lim | advanced-llm mem lim | advanced-llm repl | vanilla-llm status | vanilla-llm prov cost | vanilla-llm util cost | vanilla-llm p95 | vanilla-llm err | vanilla-llm ach RPS | vanilla-llm cpu% | vanilla-llm mem% | vanilla-llm cpu m | vanilla-llm mem Mi | vanilla-llm cpu lim | vanilla-llm mem lim | vanilla-llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1667 | 6 | 0 | 25 | 24 | 12.8 | 150 | 75 | 300 | 150 | 5 | PASS | 0.7116 | 0.1705 | 6 | 0 | 25 | 24.4 | 15.8 | 150 | 75 | 300 | 150 | 5 |
| 2 | PASS | 0.4744 | 0.2811 | 11 | 0 | 25 | 60.6 | 34.4 | 100 | 50 | 150 | 75 | 5 | PASS | 0.4744 | 0.1666 | 6 | 0 | 25 | 36 | 18.7 | 100 | 50 | 250 | 128 | 5 |
| 3 | FAIL | 0.3795 | 0.3719 | 60 | 0 | 25 | 116.5 | 60.7 | 100 | 50 | 100 | 50 | 4 | PASS | 0.3795 | 0.1753 | 6 | 0 | 25 | 47.2 | 27.4 | 80 | 40 | 200 | 100 | 5 |

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | advanced-llm status | advanced-llm prov cost | advanced-llm util cost | vanilla-llm status | vanilla-llm prov cost | vanilla-llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1667 | PASS | 0.7116 | 0.1705 |
| 2 | PASS | 0.4744 | 0.2811 | PASS | 0.4744 | 0.1666 |
| 3 | FAIL | 0.3795 | 0.3719 | PASS | 0.3795 | 0.1753 |
