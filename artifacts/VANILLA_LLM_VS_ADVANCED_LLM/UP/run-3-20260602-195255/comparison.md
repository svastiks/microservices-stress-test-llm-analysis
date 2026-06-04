# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **advanced-llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=2 · `best_pass_dir=/app/results/squeeze-compare-advanced-llm/run-1/iteration-2` · prov_cost_total=95.620505 (steady=95.616, best_pass=0.1328), util_cost_total=52.202998 (steady=52.2, best_pass=0.0725)
- **vanilla-llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=2 · `best_pass_dir=/app/results/squeeze-compare-vanilla-llm/run-1/iteration-2` · prov_cost_total=136.66193 (steady=136.656, best_pass=0.1898), util_cost_total=61.49132 (steady=61.488, best_pass=0.0854)

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| advanced-llm | +20.0 | +10.0 |
| vanilla-llm | +50.0 | +25.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | advanced-llm status | advanced-llm prov cost | advanced-llm util cost | advanced-llm p95 | advanced-llm err | advanced-llm ach RPS | advanced-llm cpu% | advanced-llm mem% | advanced-llm cpu m | advanced-llm mem Mi | advanced-llm cpu lim | advanced-llm mem lim | advanced-llm repl | vanilla-llm status | vanilla-llm prov cost | vanilla-llm util cost | vanilla-llm p95 | vanilla-llm err | vanilla-llm ach RPS | vanilla-llm cpu% | vanilla-llm mem% | vanilla-llm cpu m | vanilla-llm mem Mi | vanilla-llm cpu lim | vanilla-llm mem lim | vanilla-llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0474 | 1937 | 0 | 259.5 | 242.4 | 141.2 | 50 | 25 | 100 | 50 | 1 | FAIL | 0.0474 | 0.0474 | 2360 | 0 | 258.8 | 188 | 147.5 | 50 | 25 | 100 | 50 | 1 |
| 2 | PASS | 0.1328 | 0.0725 | 462 | 0 | 260 | 55.5 | 38.3 | 70 | 35 | 150 | 100 | 2 | PASS | 0.1898 | 0.0854 | 469 | 0 | 260 | 45.6 | 33.8 | 100 | 50 | 200 | 100 | 2 |

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | advanced-llm status | advanced-llm prov cost | advanced-llm util cost | vanilla-llm status | vanilla-llm prov cost | vanilla-llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0474 | FAIL | 0.0474 | 0.0474 |
| 2 | PASS | 0.1328 | 0.0725 | PASS | 0.1898 | 0.0854 |
