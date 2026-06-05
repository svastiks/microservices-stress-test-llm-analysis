# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **formula**: `optimizer=formula` · `stopped_reason=recovered_from_underprovisioning` · iterations=4 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-4` · prov_cost_total=96.201665 (steady=96.192, best_pass=0.1336), util_cost_total=55.447045 (steady=55.44, best_pass=0.077)
- **llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=2 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-2` · prov_cost_total=68.331557 (steady=68.328, best_pass=0.0949), util_cost_total=40.106577 (steady=40.104, best_pass=0.0557)

## Resource delta (first row → last row)

| | 🟩 CPU req (m) | 🟧 Mem req (MiB) |
|---|---:|---:|
| formula | +20.0 | +14.0 |
| llm | +0.0 | +0.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | ⬜ formula prov cost | ⬜ formula util cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | 🟩 formula cpu m | 🟧 formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | ⬜ llm prov cost | ⬜ llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | 🟩 llm cpu m | 🟧 llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0474 | 2177 | 0 | 239.9 | 410.4 | 153.9 | 50 | 25 | 100 | 50 | 1 | FAIL | 0.0474 | 0.0474 | 2388 | 0 | 239.3 | 162.7 | 143.7 | 50 | 25 | 100 | 50 | 1 |
| 2 | FAIL | 0.0949 | 0.0942 | 355 | 0 | 240 | 121.1 | 85.2 | 50 | 25 | 100 | 50 | 2 | PASS | 0.0949 | 0.0557 | 443 | 0 | 240 | 57.6 | 80 | 50 | 25 | 100 | 50 | 2 |
| 3 | FAIL | 0.1107 | 0.0632 | 540 | 0 | 240 | 57.6 | 48.8 | 58 | 32 | 115 | 58 | 2 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 4 | PASS | 0.1336 | 0.077 | 280 | 0 | 240 | 58.6 | 41.7 | 70 | 39 | 138 | 70 | 2 | — | — | — | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: formula=4, llm=2.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | formula status | ⬜ formula prov cost | ⬜ formula util cost | llm status | ⬜ llm prov cost | ⬜ llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0474 | FAIL | 0.0474 | 0.0474 |
| 2 | FAIL | 0.0949 | 0.0942 | PASS | 0.0949 | 0.0557 |
| 3 | FAIL | 0.1107 | 0.0632 | — | — | — |
| 4 | PASS | 0.1336 | 0.077 | — | — | — |
