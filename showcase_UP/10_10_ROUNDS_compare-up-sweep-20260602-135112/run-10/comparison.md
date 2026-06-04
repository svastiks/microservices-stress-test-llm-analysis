# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **formula**: `optimizer=formula` · `stopped_reason=recovered_from_underprovisioning` · iterations=2 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-2` · prov_cost_total=68.331557 (steady=68.328, best_pass=0.0949), util_cost_total=58.539217 (steady=58.536, best_pass=0.0813)
- **llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=2 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-2` · prov_cost_total=95.620505 (steady=95.616, best_pass=0.1328), util_cost_total=30.674205 (steady=30.672, best_pass=0.0426)

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | +0.0 | +0.0 |
| llm | +20.0 | +10.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula prov cost | formula util cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | llm prov cost | llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0474 | 1560 | 0 | 220 | 238.8 | 183.4 | 50 | 25 | 100 | 50 | 1 | FAIL | 0.0474 | 0.0456 | 3376 | 0 | 161.2 | 101.5 | 24.9 | 50 | 25 | 100 | 50 | 1 |
| 2 | PASS | 0.0949 | 0.0813 | 327 | 0 | 220 | 85.3 | 92 | 50 | 25 | 100 | 50 | 2 | PASS | 0.1328 | 0.0426 | 204 | 0 | 220 | 32.5 | 23.9 | 70 | 35 | 200 | 100 | 2 |

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | formula status | formula prov cost | formula util cost | llm status | llm prov cost | llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0474 | FAIL | 0.0474 | 0.0456 |
| 2 | PASS | 0.0949 | 0.0813 | PASS | 0.1328 | 0.0426 |
