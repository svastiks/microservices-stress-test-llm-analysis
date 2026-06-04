# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **formula**: `optimizer=formula` · `stopped_reason=recovered_from_underprovisioning` · iterations=2 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-2` · prov_cost_total=68.331557 (steady=68.328, best_pass=0.0949), util_cost_total=59.043235 (steady=59.04, best_pass=0.082)
- **llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=2 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-2` · prov_cost_total=91.588365 (steady=91.584, best_pass=0.1272), util_cost_total=28.370162 (steady=28.368, best_pass=0.0394)

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | +0.0 | +0.0 |
| llm | +17.0 | +9.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula prov cost | formula util cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | llm prov cost | llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0474 | 837 | 0 | 220 | 234.4 | 171.8 | 50 | 25 | 100 | 50 | 1 | FAIL | 0.0474 | 0.0471 | 1678 | 0 | 220 | 139.5 | 87.9 | 50 | 25 | 100 | 50 | 1 |
| 2 | PASS | 0.0949 | 0.082 | 351 | 0 | 220 | 85.7 | 114.7 | 50 | 25 | 100 | 50 | 2 | PASS | 0.1272 | 0.0394 | 181 | 0 | 220 | 32.1 | 10.6 | 67 | 34 | 200 | 100 | 2 |

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | formula status | formula prov cost | formula util cost | llm status | llm prov cost | llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0474 | FAIL | 0.0474 | 0.0471 |
| 2 | PASS | 0.0949 | 0.082 | PASS | 0.1272 | 0.0394 |
