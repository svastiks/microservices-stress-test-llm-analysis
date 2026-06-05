# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **formula**: `optimizer=formula` · `stopped_reason=recovered_from_underprovisioning` · iterations=4 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-4` · prov_cost_total=103.97816 (steady=103.968, best_pass=0.1444), util_cost_total=48.317823 (steady=48.312, best_pass=0.0671)
- **llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=2 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-2` · prov_cost_total=95.620505 (steady=95.616, best_pass=0.1328), util_cost_total=33.84236 (steady=33.84, best_pass=0.047)

## Resource delta (first row → last row)

| | 🟩 CPU req (m) | 🟧 Mem req (MiB) |
|---|---:|---:|
| formula | +26.0 | +14.0 |
| llm | +20.0 | +10.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | ⬜ formula prov cost | ⬜ formula util cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | 🟩 formula cpu m | 🟧 formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | ⬜ llm prov cost | ⬜ llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | 🟩 llm cpu m | 🟧 llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0474 | 4642 | 0 | 177.3 | 138.6 | 154.5 | 50 | 25 | 100 | 50 | 1 | FAIL | 0.0474 | 0.0474 | 4994 | 0 | 199.1 | 129.5 | 242.4 | 50 | 25 | 100 | 50 | 1 |
| 2 | FAIL | 0.0949 | 0.0625 | 823 | 0 | 240 | 65.2 | 78.8 | 50 | 25 | 100 | 50 | 2 | PASS | 0.1328 | 0.047 | 450 | 0 | 240 | 34.9 | 44.6 | 70 | 35 | 200 | 100 | 2 |
| 3 | FAIL | 0.1197 | 0.0559 | 585 | 0 | 240 | 46.1 | 58.1 | 63 | 32 | 125 | 63 | 2 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 4 | PASS | 0.1444 | 0.0671 | 390 | 0 | 240 | 45.2 | 68.9 | 76 | 39 | 151 | 76 | 2 | — | — | — | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: formula=4, llm=2.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | formula status | ⬜ formula prov cost | ⬜ formula util cost | llm status | ⬜ llm prov cost | ⬜ llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0474 | FAIL | 0.0474 | 0.0474 |
| 2 | FAIL | 0.0949 | 0.0625 | PASS | 0.1328 | 0.047 |
| 3 | FAIL | 0.1197 | 0.0559 | — | — | — |
| 4 | PASS | 0.1444 | 0.0671 | — | — | — |
