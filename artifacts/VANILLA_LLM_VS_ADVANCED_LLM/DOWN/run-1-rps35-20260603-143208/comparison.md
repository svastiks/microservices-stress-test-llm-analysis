# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **advanced-llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=19 · `best_pass_dir=/app/results/squeeze-compare-advanced-llm/run-1/iteration-18` · prov_cost_total=27.622825 (steady=27.504, best_pass=0.0382), util_cost_total=22.003823 (steady=21.96, best_pass=0.0305)
- **vanilla-llm**: `optimizer=llm` · `stopped_reason=empty_recommended_diff` · iterations=1 · `best_pass_dir=/app/results/squeeze-compare-vanilla-llm/run-1/iteration-1` · prov_cost_total=512.36979 (steady=512.352, best_pass=0.7116), util_cost_total=104.54763 (steady=104.544, best_pass=0.1452)

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| advanced-llm | -116.0 | -34.0 |
| vanilla-llm | +0.0 | +0.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | advanced-llm status | advanced-llm prov cost | advanced-llm util cost | advanced-llm p95 | advanced-llm err | advanced-llm ach RPS | advanced-llm cpu% | advanced-llm mem% | advanced-llm cpu m | advanced-llm mem Mi | advanced-llm cpu lim | advanced-llm mem lim | advanced-llm repl | vanilla-llm status | vanilla-llm prov cost | vanilla-llm util cost | vanilla-llm p95 | vanilla-llm err | vanilla-llm ach RPS | vanilla-llm cpu% | vanilla-llm mem% | vanilla-llm cpu m | vanilla-llm mem Mi | vanilla-llm cpu lim | vanilla-llm mem lim | vanilla-llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1472 | 6 | 0 | 35 | 21.3 | 9.4 | 150 | 75 | 300 | 150 | 5 | PASS | 0.7116 | 0.1452 | 6 | 0 | 35 | 21 | 9.3 | 150 | 75 | 300 | 150 | 5 |
| 2 | PASS | 0.6737 | 0.2148 | 6 | 0 | 35 | 32.8 | 14.9 | 142 | 71 | 285 | 142 | 5 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 3 | PASS | 0.6082 | 0.1993 | 6 | 0 | 35 | 33.5 | 19.8 | 128 | 66 | 285 | 142 | 5 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 4 | PASS | 0.5793 | 0.197 | 6 | 0 | 35 | 34.7 | 21.3 | 122 | 62 | 270 | 135 | 5 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 5 | PASS | 0.4179 | 0.1784 | 6 | 0 | 35 | 43.7 | 24.4 | 110 | 56 | 243 | 129 | 4 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 6 | PASS | 0.3795 | 0.138 | 6 | 0 | 35 | 37.2 | 21 | 100 | 50 | 243 | 129 | 4 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 7 | PASS | 0.3344 | 0.108 | 6 | 0 | 35 | 33.3 | 14.3 | 88 | 45 | 243 | 129 | 4 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 8 | PASS | 0.2367 | 0.095 | 6 | 0 | 35 | 41.2 | 20.9 | 83 | 43 | 230 | 120 | 3 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 9 | PASS | 0.2232 | 0.0836 | 6 | 0 | 35 | 38.5 | 20.1 | 78 | 43 | 230 | 120 | 3 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 10 | PASS | 0.1412 | 0.0835 | 6 | 0 | 35 | 60.7 | 33.6 | 74 | 41 | 217 | 114 | 2 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 11 | PASS | 0.067 | 0.0596 | 4 | 0 | 35 | 92.6 | 32.5 | 70 | 41 | 205 | 114 | 1 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 12 | PASS | 0.0607 | 0.0352 | 4 | 0 | 35 | 59.8 | 31.8 | 63 | 41 | 184 | 114 | 1 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 13 | PASS | 0.058 | 0.0331 | 4 | 0 | 35 | 60.1 | 16.9 | 60 | 41 | 184 | 114 | 1 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 14 | PASS | 0.0526 | 0.0304 | 4 | 0 | 35 | 61.2 | 16.7 | 54 | 41 | 184 | 114 | 1 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 15 | PASS | 0.049 | 0.0305 | 4 | 0 | 35 | 66.2 | 17.1 | 50 | 41 | 175 | 114 | 1 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 16 | PASS | 0.0454 | 0.0298 | 4 | 0 | 35 | 70.4 | 17.1 | 46 | 41 | 165 | 114 | 1 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 17 | PASS | 0.0418 | 0.0288 | 4 | 0 | 35 | 74.3 | 16.7 | 42 | 41 | 148 | 114 | 1 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 18 | PASS | 0.0382 | 0.0305 | 4 | 0 | 35 | 87.3 | 16.9 | 38 | 41 | 132 | 114 | 1 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 19 | FAIL | 0.0346 | 0.0302 | 19 | 0 | 35 | 96.4 | 17.4 | 34 | 41 | 119 | 114 | 1 | — | — | — | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: advanced-llm=19, vanilla-llm=1.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | advanced-llm status | advanced-llm prov cost | advanced-llm util cost | vanilla-llm status | vanilla-llm prov cost | vanilla-llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1472 | PASS | 0.7116 | 0.1452 |
| 2 | PASS | 0.6737 | 0.2148 | — | — | — |
| 3 | PASS | 0.6082 | 0.1993 | — | — | — |
| 4 | PASS | 0.5793 | 0.197 | — | — | — |
| 5 | PASS | 0.4179 | 0.1784 | — | — | — |
| 6 | PASS | 0.3795 | 0.138 | — | — | — |
| 7 | PASS | 0.3344 | 0.108 | — | — | — |
| 8 | PASS | 0.2367 | 0.095 | — | — | — |
| 9 | PASS | 0.2232 | 0.0836 | — | — | — |
| 10 | PASS | 0.1412 | 0.0835 | — | — | — |
| 11 | PASS | 0.067 | 0.0596 | — | — | — |
| 12 | PASS | 0.0607 | 0.0352 | — | — | — |
| 13 | PASS | 0.058 | 0.0331 | — | — | — |
| 14 | PASS | 0.0526 | 0.0304 | — | — | — |
| 15 | PASS | 0.049 | 0.0305 | — | — | — |
| 16 | PASS | 0.0454 | 0.0298 | — | — | — |
| 17 | PASS | 0.0418 | 0.0288 | — | — | — |
| 18 | PASS | 0.0382 | 0.0305 | — | — | — |
| 19 | FAIL | 0.0346 | 0.0302 | — | — | — |
