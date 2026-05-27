# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **formula**: `optimizer=formula` · `stopped_reason=recovered_from_underprovisioning` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-3` · prov_cost_total=194.84327 (steady=194.832, best_pass=0.2706), util_cost_total=110.383298 (steady=110.376, best_pass=0.1533)
- **llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=4 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-4` · prov_cost_total=287.084668 (steady=287.064, best_pass=0.3987), util_cost_total=101.817532 (steady=101.808, best_pass=0.1414)

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | +45.0 | +23.0 |
| llm | +55.0 | +28.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula prov cost | formula util cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | llm prov cost | llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0474 | 6861 | 0 | 190.8 | 463.7 | 197.7 | 50 | 25 | 100 | 50 | 1 | FAIL | 0.0474 | 0.0474 | 5084 | 0 | 191.7 | 299 | 173.9 | 50 | 25 | 100 | 50 | 1 |
| 2 | FAIL | 0.1328 | 0.0912 | 1786 | 0 | 277.3 | 67 | 99.9 | 70 | 35 | 139 | 70 | 2 | FAIL | 0.1328 | 0.0703 | 1047 | 0 | 280 | 52.9 | 53.8 | 70 | 35 | 200 | 100 | 2 |
| 3 | PASS | 0.2706 | 0.1533 | 488 | 0 | 280 | 57 | 50.7 | 95 | 48 | 189 | 95 | 3 | FAIL | 0.2478 | 0.1222 | 815 | 0 | 280 | 49.5 | 46.3 | 87 | 44 | 250 | 100 | 3 |
| 4 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.3987 | 0.1414 | 371 | 0 | 280 | 36.4 | 18.6 | 105 | 53 | 300 | 150 | 4 |

*Iteration count mismatch: formula=3, llm=4.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | formula status | formula prov cost | formula util cost | llm status | llm prov cost | llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0474 | FAIL | 0.0474 | 0.0474 |
| 2 | FAIL | 0.1328 | 0.0912 | FAIL | 0.1328 | 0.0703 |
| 3 | PASS | 0.2706 | 0.1533 | FAIL | 0.2478 | 0.1222 |
| 4 | — | — | — | PASS | 0.3987 | 0.1414 |
