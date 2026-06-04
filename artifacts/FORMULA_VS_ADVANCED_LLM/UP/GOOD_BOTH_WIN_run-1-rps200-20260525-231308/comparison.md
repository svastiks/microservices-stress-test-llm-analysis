# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **formula**: `optimizer=formula` · `stopped_reason=recovered_from_underprovisioning` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-3` · prov_cost_total=131.192112 (steady=131.184, best_pass=0.1822), util_cost_total=90.077945 (steady=90.072, best_pass=0.1251)
- **llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-3` · prov_cost_total=60.124097 (steady=60.12, best_pass=0.0835), util_cost_total=27.290958 (steady=27.288, best_pass=0.0379)

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | +14.0 | +7.0 |
| llm | -6.0 | -3.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula prov cost | formula util cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | llm prov cost | llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0474 | 836 | 0 | 200 | 205.1 | 116.7 | 50 | 25 | 100 | 50 | 1 | FAIL | 0.0474 | 0.0474 | 816 | 0 | 200 | 275 | 184 | 50 | 25 | 100 | 50 | 1 |
| 2 | FAIL | 0.0949 | 0.0653 | 1241 | 0 | 200 | 68.3 | 77.8 | 50 | 25 | 100 | 50 | 2 | FAIL | 0.033 | 0.033 | 1021 | 0 | 200 | 210.3 | 128.7 | 35 | 15 | 100 | 50 | 1 |
| 3 | PASS | 0.1822 | 0.1251 | 345 | 0 | 200 | 69.7 | 49.5 | 64 | 32 | 127 | 64 | 3 | PASS | 0.0835 | 0.0379 | 192 | 0 | 200 | 46.1 | 32 | 44 | 22 | 200 | 100 | 2 |

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | formula status | formula prov cost | formula util cost | llm status | llm prov cost | llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0474 | FAIL | 0.0474 | 0.0474 |
| 2 | FAIL | 0.0949 | 0.0653 | FAIL | 0.033 | 0.033 |
| 3 | PASS | 0.1822 | 0.1251 | PASS | 0.0835 | 0.0379 |
