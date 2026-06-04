# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **formula**: `optimizer=formula` · `stopped_reason=recovered_from_underprovisioning` · iterations=2 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-2` · prov_cost_total=68.331557 (steady=68.328, best_pass=0.0949), util_cost_total=65.091445 (steady=65.088, best_pass=0.0904)
- **llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=2 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-2` · prov_cost_total=95.620505 (steady=95.616, best_pass=0.1328), util_cost_total=34.4183 (steady=34.416, best_pass=0.0478)

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | +0.0 | +0.0 |
| llm | +20.0 | +10.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula prov cost | formula util cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | llm prov cost | llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0474 | 1531 | 0 | 220 | 256 | 202.6 | 50 | 25 | 100 | 50 | 1 | FAIL | 0.0474 | 0.0442 | 2914 | 0 | 168.5 | 96.9 | 24.3 | 50 | 25 | 100 | 50 | 1 |
| 2 | PASS | 0.0949 | 0.0904 | 260 | 0 | 220 | 95 | 109.3 | 50 | 25 | 100 | 50 | 2 | PASS | 0.1328 | 0.0478 | 233 | 0 | 220 | 36.2 | 32.6 | 70 | 35 | 150 | 75 | 2 |

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | formula status | formula prov cost | formula util cost | llm status | llm prov cost | llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0474 | FAIL | 0.0474 | 0.0442 |
| 2 | PASS | 0.0949 | 0.0904 | PASS | 0.1328 | 0.0478 |
