# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **formula**: `optimizer=formula` · `stopped_reason=recovered_from_underprovisioning` · iterations=2 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-2` · prov_cost_total=95.620505 (steady=95.616, best_pass=0.1328), util_cost_total=58.61122 (steady=58.608, best_pass=0.0814)
- **llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=2 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-2` · prov_cost_total=95.620505 (steady=95.616, best_pass=0.1328), util_cost_total=45.434763 (steady=45.432, best_pass=0.0631)

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| formula | +20.0 | +10.0 |
| llm | +20.0 | +10.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | formula prov cost | formula util cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | formula cpu m | formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | llm prov cost | llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0474 | 4740 | 0 | 173.9 | 219.1 | 176.8 | 50 | 25 | 100 | 50 | 1 | FAIL | 0.0474 | 0.0474 | 4907 | 0 | 172.9 | 166.4 | 222.1 | 50 | 25 | 100 | 50 | 1 |
| 2 | PASS | 0.1328 | 0.0814 | 402 | 0 | 220 | 59.6 | 92 | 70 | 35 | 139 | 70 | 2 | PASS | 0.1328 | 0.0631 | 271 | 0 | 220 | 46.8 | 60.4 | 70 | 35 | 200 | 100 | 2 |

## Cost per iteration

### Iteration 1

| | Status | Prov cost | Util cost | p95 ms |
|---|---|---:|---:|---:|
| formula | FAIL | 0.0474 | 0.0474 | 4740 |
| llm | FAIL | 0.0474 | 0.0474 | 4907 |

### Iteration 2

| | Status | Prov cost | Util cost | p95 ms |
|---|---|---:|---:|---:|
| formula | PASS | 0.1328 | 0.0814 | 402 |
| llm | PASS | 0.1328 | 0.0631 | 271 |

