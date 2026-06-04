# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **advanced-llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=2 · `best_pass_dir=/app/results/squeeze-compare-advanced-llm/run-1/iteration-2` · prov_cost_total=68.331557 (steady=68.328, best_pass=0.0949), util_cost_total=40.754583 (steady=40.752, best_pass=0.0566)
- **vanilla-llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=2 · `best_pass_dir=/app/results/squeeze-compare-vanilla-llm/run-1/iteration-2` · prov_cost_total=136.663118 (steady=136.656, best_pass=0.1898), util_cost_total=56.451383 (steady=56.448, best_pass=0.0784)

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| advanced-llm | +0.0 | +0.0 |
| vanilla-llm | +50.0 | +25.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | advanced-llm status | advanced-llm prov cost | advanced-llm util cost | advanced-llm p95 | advanced-llm err | advanced-llm ach RPS | advanced-llm cpu% | advanced-llm mem% | advanced-llm cpu m | advanced-llm mem Mi | advanced-llm cpu lim | advanced-llm mem lim | advanced-llm repl | vanilla-llm status | vanilla-llm prov cost | vanilla-llm util cost | vanilla-llm p95 | vanilla-llm err | vanilla-llm ach RPS | vanilla-llm cpu% | vanilla-llm mem% | vanilla-llm cpu m | vanilla-llm mem Mi | vanilla-llm cpu lim | vanilla-llm mem lim | vanilla-llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0467 | 1636 | 0 | 219.9 | 103.7 | 71.4 | 50 | 25 | 100 | 50 | 1 | FAIL | 0.0949 | 0.0569 | 1595 | 0 | 220 | 61.2 | 37.7 | 50 | 25 | 100 | 50 | 2 |
| 2 | PASS | 0.0949 | 0.0566 | 328 | 0 | 220 | 59.3 | 65.7 | 50 | 25 | 100 | 50 | 2 | PASS | 0.1898 | 0.0784 | 221 | 0 | 220 | 42.1 | 26.8 | 100 | 50 | 200 | 75 | 2 |

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | advanced-llm status | advanced-llm prov cost | advanced-llm util cost | vanilla-llm status | vanilla-llm prov cost | vanilla-llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0467 | FAIL | 0.0949 | 0.0569 |
| 2 | PASS | 0.0949 | 0.0566 | PASS | 0.1898 | 0.0784 |
