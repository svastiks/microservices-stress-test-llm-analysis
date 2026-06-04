# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **formula**: `optimizer=formula` · `stopped_reason=recovered_from_underprovisioning` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-3` · prov_cost_total=79.710325 (steady=79.704, best_pass=0.1107), util_cost_total=47.669153 (steady=47.664, best_pass=0.0662)
- **llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=2 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-2` · prov_cost_total=94.32446 (steady=94.32, best_pass=0.131), util_cost_total=55.083097 (steady=55.08, best_pass=0.0765)

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | +8.0 | +7.0 |
| llm | +19.0 | +10.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula prov cost | formula util cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | llm prov cost | llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0474 | 2389 | 0 | 240 | 254.2 | 192.4 | 50 | 25 | 100 | 50 | 1 | FAIL | 0.0474 | 0.0474 | 1646 | 0 | 240 | 152.5 | 141.9 | 50 | 25 | 100 | 50 | 1 |
| 2 | FAIL | 0.0949 | 0.0925 | 422 | 0 | 240 | 97.3 | 104.6 | 50 | 25 | 100 | 50 | 2 | PASS | 0.131 | 0.0765 | 329 | 0 | 240 | 59.7 | 33.9 | 69 | 35 | 150 | 100 | 2 |
| 3 | PASS | 0.1107 | 0.0662 | 497 | 0 | 240 | 59.7 | 62 | 58 | 32 | 115 | 58 | 2 | — | — | — | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: formula=3, llm=2.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | formula status | formula prov cost | formula util cost | llm status | llm prov cost | llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0474 | FAIL | 0.0474 | 0.0474 |
| 2 | FAIL | 0.0949 | 0.0925 | PASS | 0.131 | 0.0765 |
| 3 | PASS | 0.1107 | 0.0662 | — | — | — |
