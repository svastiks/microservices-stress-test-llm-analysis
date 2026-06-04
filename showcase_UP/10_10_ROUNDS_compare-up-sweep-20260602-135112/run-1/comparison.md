# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **formula**: `optimizer=formula` · `stopped_reason=recovered_from_underprovisioning` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-3` · prov_cost_total=88.854642 (steady=88.848, best_pass=0.1234), util_cost_total=68.98114 (steady=68.976, best_pass=0.0958)
- **llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=2 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-2` · prov_cost_total=95.620505 (steady=95.616, best_pass=0.1328), util_cost_total=52.130995 (steady=52.128, best_pass=0.0724)

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | +15.0 | +8.0 |
| llm | +20.0 | +10.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula prov cost | formula util cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | llm prov cost | llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.045 | 5126 | 0 | 183.4 | 94.6 | 134 | 50 | 25 | 100 | 50 | 1 | FAIL | 0.0474 | 0.0474 | 3894 | 0 | 190.3 | 195.2 | 209.6 | 50 | 25 | 100 | 50 | 1 |
| 2 | FAIL | 0.0949 | 0.0648 | 1090 | 0 | 220 | 67.1 | 90.5 | 50 | 25 | 100 | 50 | 2 | PASS | 0.1328 | 0.0724 | 357 | 0 | 220 | 54.2 | 60 | 70 | 35 | 150 | 75 | 2 |
| 3 | PASS | 0.1234 | 0.0958 | 353 | 0 | 220 | 77.8 | 73.6 | 65 | 33 | 129 | 65 | 2 | — | — | — | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: formula=3, llm=2.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | formula status | formula prov cost | formula util cost | llm status | llm prov cost | llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.045 | FAIL | 0.0474 | 0.0474 |
| 2 | FAIL | 0.0949 | 0.0648 | PASS | 0.1328 | 0.0724 |
| 3 | PASS | 0.1234 | 0.0958 | — | — | — |
