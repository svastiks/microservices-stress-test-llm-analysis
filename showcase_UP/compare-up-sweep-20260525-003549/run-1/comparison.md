# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **formula**: `optimizer=formula` · `stopped_reason=recovered_from_underprovisioning` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-3` · prov_cost_total=178.4267 (steady=178.416, best_pass=0.2478), util_cost_total=108.583242 (steady=108.576, best_pass=0.1508)
- **llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=5 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-5` · prov_cost_total=409.930763 (steady=409.896, best_pass=0.5693), util_cost_total=78.994345 (steady=78.984, best_pass=0.1097)

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | +37.0 | +19.0 |
| llm | +70.0 | +35.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula prov cost | formula util cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | llm prov cost | llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0474 | 6576 | 0 | 178.9 | 446.1 | 168.6 | 50 | 25 | 100 | 50 | 1 | FAIL | 0.0474 | 0.0474 | 6604 | 0 | 175.5 | 292.8 | 168.9 | 50 | 25 | 100 | 50 | 1 |
| 2 | FAIL | 0.1328 | 0.0915 | 1012 | 0 | 280 | 67.9 | 87.3 | 70 | 35 | 139 | 70 | 2 | FAIL | 0.1328 | 0.0661 | 576 | 0 | 280 | 49.5 | 55.1 | 70 | 35 | 200 | 100 | 2 |
| 3 | PASS | 0.2478 | 0.1508 | 497 | 0 | 280 | 61.2 | 54.6 | 87 | 44 | 172 | 87 | 3 | FAIL | 0.2307 | 0.0925 | 1569 | 0 | 277.5 | 40.6 | 30.9 | 81 | 41 | 300 | 150 | 3 |
| 4 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.4103 | 0.0981 | 533 | 0 | 280 | 24.2 | 18.7 | 108 | 55 | 450 | 150 | 4 |
| 5 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.5693 | 0.1097 | 462 | 0 | 280 | 19.6 | 13.1 | 120 | 60 | 500 | 180 | 5 |

*Iteration count mismatch: formula=3, llm=5.*

## Cost per iteration

### Iteration 1

| | Status | Prov cost | Util cost | p95 ms |
|---|---|---:|---:|---:|
| formula | FAIL | 0.0474 | 0.0474 | 6576 |
| llm | FAIL | 0.0474 | 0.0474 | 6604 |

### Iteration 2

| | Status | Prov cost | Util cost | p95 ms |
|---|---|---:|---:|---:|
| formula | FAIL | 0.1328 | 0.0915 | 1012 |
| llm | FAIL | 0.1328 | 0.0661 | 576 |

### Iteration 3

| | Status | Prov cost | Util cost | p95 ms |
|---|---|---:|---:|---:|
| formula | PASS | 0.2478 | 0.1508 | 497 |
| llm | FAIL | 0.2307 | 0.0925 | 1569 |

### Iteration 4

| | Status | Prov cost | Util cost | p95 ms |
|---|---|---:|---:|---:|
| formula | — | — | — | — |
| llm | FAIL | 0.4103 | 0.0981 | 533 |

### Iteration 5

| | Status | Prov cost | Util cost | p95 ms |
|---|---|---:|---:|---:|
| formula | — | — | — | — |
| llm | PASS | 0.5693 | 0.1097 | 462 |

