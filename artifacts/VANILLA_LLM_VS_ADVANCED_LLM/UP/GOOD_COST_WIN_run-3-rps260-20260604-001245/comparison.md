# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **advanced-llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-advanced-llm/run-1/iteration-3` · prov_cost_total=79.27831 (steady=79.272, best_pass=0.1101), util_cost_total=53.859533 (steady=53.856, best_pass=0.0748)
- **vanilla-llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=2 · `best_pass_dir=/app/results/squeeze-compare-vanilla-llm/run-1/iteration-2` · prov_cost_total=136.66193 (steady=136.656, best_pass=0.1898), util_cost_total=65.595455 (steady=65.592, best_pass=0.0911)

## Resource delta (first row → last row)

| | 🟩 CPU req (m) | 🟧 Mem req (MiB) |
|---|---:|---:|
| advanced-llm | +8.0 | +4.0 |
| vanilla-llm | +50.0 | +25.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | advanced-llm status | ⬜ advanced-llm prov cost | ⬜ advanced-llm util cost | advanced-llm p95 | advanced-llm err | advanced-llm ach RPS | advanced-llm cpu% | advanced-llm mem% | 🟩 advanced-llm cpu m | 🟧 advanced-llm mem Mi | advanced-llm cpu lim | advanced-llm mem lim | advanced-llm repl | vanilla-llm status | ⬜ vanilla-llm prov cost | ⬜ vanilla-llm util cost | vanilla-llm p95 | vanilla-llm err | vanilla-llm ach RPS | vanilla-llm cpu% | vanilla-llm mem% | 🟩 vanilla-llm cpu m | 🟧 vanilla-llm mem Mi | vanilla-llm cpu lim | vanilla-llm mem lim | vanilla-llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0198 | 5862 | 0 | 231.2 | 39.5 | 83.8 | 50 | 25 | 100 | 50 | 1 | FAIL | 0.0474 | 0.0471 | 4620 | 0 | 241 | 162.9 | 84.9 | 50 | 25 | 100 | 50 | 1 |
| 2 | FAIL | 0.0949 | 0.0467 | 1000 | 0 | 260 | 48.1 | 68.9 | 50 | 25 | 100 | 50 | 2 | PASS | 0.1898 | 0.0911 | 443 | 0 | 260 | 48.8 | 33 | 100 | 50 | 150 | 75 | 2 |
| 3 | PASS | 0.1101 | 0.0748 | 395 | 0 | 260 | 68.4 | 59.4 | 58 | 29 | 115 | 58 | 2 | — | — | — | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: advanced-llm=3, vanilla-llm=2.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | advanced-llm status | ⬜ advanced-llm prov cost | ⬜ advanced-llm util cost | vanilla-llm status | ⬜ vanilla-llm prov cost | ⬜ vanilla-llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0198 | FAIL | 0.0474 | 0.0471 |
| 2 | FAIL | 0.0949 | 0.0467 | PASS | 0.1898 | 0.0911 |
| 3 | PASS | 0.1101 | 0.0748 | — | — | — |
