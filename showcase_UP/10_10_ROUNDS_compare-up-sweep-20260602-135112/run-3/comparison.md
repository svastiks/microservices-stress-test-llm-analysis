# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **formula**: `optimizer=formula` · `stopped_reason=recovered_from_underprovisioning` · iterations=6 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-6` · prov_cost_total=169.725043 (steady=169.704, best_pass=0.2357), util_cost_total=69.706328 (steady=69.696, best_pass=0.0968)
- **llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=2 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-2` · prov_cost_total=95.620505 (steady=95.616, best_pass=0.1328), util_cost_total=40.034575 (steady=40.032, best_pass=0.0556)

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | +74.0 | +39.0 |
| llm | +20.0 | +10.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula prov cost | formula util cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | llm prov cost | llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0474 | 5708 | 0 | 182.4 | 156.1 | 148.9 | 50 | 25 | 100 | 50 | 1 | FAIL | 0.0474 | 0.0474 | 2008 | 0 | 260 | 198.4 | 208.9 | 50 | 25 | 100 | 50 | 1 |
| 2 | FAIL | 0.0949 | 0.0619 | 934 | 0 | 260 | 64.6 | 76.4 | 50 | 25 | 100 | 50 | 2 | PASS | 0.1328 | 0.0556 | 303 | 0 | 260 | 42.8 | 24.9 | 70 | 35 | 200 | 150 | 2 |
| 3 | FAIL | 0.1197 | 0.0539 | 977 | 0 | 260 | 44.2 | 59.8 | 63 | 32 | 126 | 63 | 2 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 4 | FAIL | 0.152 | 0.0692 | 879 | 0 | 260 | 44.2 | 69.5 | 80 | 41 | 160 | 80 | 2 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 5 | FAIL | 0.192 | 0.0839 | 700 | 0 | 260 | 42.9 | 58.2 | 101 | 52 | 201 | 101 | 2 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 6 | PASS | 0.2357 | 0.0968 | 384 | 0 | 260 | 41 | 42.2 | 124 | 64 | 246 | 124 | 2 | — | — | — | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: formula=6, llm=2.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | formula status | formula prov cost | formula util cost | llm status | llm prov cost | llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0474 | FAIL | 0.0474 | 0.0474 |
| 2 | FAIL | 0.0949 | 0.0619 | PASS | 0.1328 | 0.0556 |
| 3 | FAIL | 0.1197 | 0.0539 | — | — | — |
| 4 | FAIL | 0.152 | 0.0692 | — | — | — |
| 5 | FAIL | 0.192 | 0.0839 | — | — | — |
| 6 | PASS | 0.2357 | 0.0968 | — | — | — |
