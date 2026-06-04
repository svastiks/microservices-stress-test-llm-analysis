# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **formula**: `optimizer=formula` · `stopped_reason=recovered_from_underprovisioning` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-3` · prov_cost_total=135.296255 (steady=135.288, best_pass=0.1879), util_cost_total=88.710638 (steady=88.704, best_pass=0.1232)
- **llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-3` · prov_cost_total=95.62169 (steady=95.616, best_pass=0.1328), util_cost_total=49.25208 (steady=49.248, best_pass=0.0684)

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | +16.0 | +8.0 |
| llm | +20.0 | +10.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula prov cost | formula util cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | llm prov cost | llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0474 | 1226 | 0 | 220 | 260.4 | 173.7 | 50 | 25 | 100 | 50 | 1 | FAIL | 0.0474 | 0.0474 | 991 | 0 | 220 | 272.9 | 189.8 | 50 | 25 | 100 | 50 | 1 |
| 2 | FAIL | 0.0949 | 0.0949 | 1490 | 0 | 220 | 102 | 105.7 | 50 | 25 | 100 | 50 | 2 | FAIL | 0.0474 | 0.0474 | 4764 | 0.0478 | 201.8 | 283.9 | 172 | 50 | 25 | 75 | 40 | 1 |
| 3 | PASS | 0.1879 | 0.1232 | 270 | 0 | 220 | 66.4 | 50.8 | 66 | 33 | 131 | 66 | 3 | PASS | 0.1328 | 0.0684 | 394 | 0 | 220 | 51.8 | 45.8 | 70 | 35 | 150 | 75 | 2 |

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | formula status | formula prov cost | formula util cost | llm status | llm prov cost | llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0474 | FAIL | 0.0474 | 0.0474 |
| 2 | FAIL | 0.0949 | 0.0949 | FAIL | 0.0474 | 0.0474 |
| 3 | PASS | 0.1879 | 0.1232 | PASS | 0.1328 | 0.0684 |
