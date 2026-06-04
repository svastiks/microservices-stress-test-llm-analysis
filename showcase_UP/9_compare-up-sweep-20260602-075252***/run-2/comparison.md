# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **formula**: `optimizer=formula` · `stopped_reason=recovered_from_underprovisioning` · iterations=2 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-2` · prov_cost_total=95.620505 (steady=95.616, best_pass=0.1328), util_cost_total=18.649765 (steady=18.648, best_pass=0.0259)
- **llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=2 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-2` · prov_cost_total=95.620505 (steady=95.616, best_pass=0.1328), util_cost_total=31.970178 (steady=31.968, best_pass=0.0444)

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | +20.0 | +10.0 |
| llm | +20.0 | +10.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula prov cost | formula util cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | llm prov cost | llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0447 | 4192 | 0 | 156.5 | 97.7 | 31.7 | 50 | 25 | 100 | 50 | 1 | FAIL | 0.0474 | 0.0427 | 4268 | 0 | 186.1 | 90.3 | 83.4 | 50 | 25 | 100 | 50 | 1 |
| 2 | PASS | 0.1328 | 0.0259 | 238 | 0 | 240 | 19.7 | 16.3 | 70 | 35 | 139 | 70 | 2 | PASS | 0.1328 | 0.0444 | 495 | 0 | 240 | 33.2 | 37.8 | 70 | 35 | 200 | 100 | 2 |

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | formula status | formula prov cost | formula util cost | llm status | llm prov cost | llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0447 | FAIL | 0.0474 | 0.0427 |
| 2 | PASS | 0.1328 | 0.0259 | PASS | 0.1328 | 0.0444 |
