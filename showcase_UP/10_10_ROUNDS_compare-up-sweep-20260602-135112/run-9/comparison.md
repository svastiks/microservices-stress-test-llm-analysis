# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **formula**: `optimizer=formula` · `stopped_reason=recovered_from_underprovisioning` · iterations=2 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-2` · prov_cost_total=68.331557 (steady=68.328, best_pass=0.0949), util_cost_total=57.603185 (steady=57.6, best_pass=0.08)
- **llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-3` · prov_cost_total=184.476098 (steady=184.464, best_pass=0.2562), util_cost_total=97.2779 (steady=97.272, best_pass=0.1351)

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | +0.0 | +0.0 |
| llm | +40.0 | +20.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula prov cost | formula util cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | llm prov cost | llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0474 | 2997 | 0 | 257 | 237.3 | 182.3 | 50 | 25 | 100 | 50 | 1 | FAIL | 0.0949 | 0.0421 | 4141 | 0 | 166.8 | 46.1 | 12.9 | 50 | 25 | 100 | 50 | 2 |
| 2 | PASS | 0.0949 | 0.08 | 495 | 0 | 260 | 83.5 | 100.2 | 50 | 25 | 100 | 50 | 2 | FAIL | 0.1328 | 0.0588 | 1010 | 0 | 260 | 43.6 | 56.2 | 70 | 35 | 105 | 53 | 2 |
| 3 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.2562 | 0.1351 | 393 | 0 | 260 | 53.6 | 37 | 90 | 45 | 135 | 70 | 3 |

*Iteration count mismatch: formula=2, llm=3.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | formula status | formula prov cost | formula util cost | llm status | llm prov cost | llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0474 | FAIL | 0.0949 | 0.0421 |
| 2 | PASS | 0.0949 | 0.08 | FAIL | 0.1328 | 0.0588 |
| 3 | — | — | — | PASS | 0.2562 | 0.1351 |
