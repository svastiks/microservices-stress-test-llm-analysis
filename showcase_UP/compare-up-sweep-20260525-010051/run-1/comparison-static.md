# Static baseline vs LLM squeeze comparison

- **Target RPS**: 280 (`up_demo`)
- **Static**: thin deployment YAML + HPA (1–5 replicas); one k6 pass; no squeeze apply loop.
- **LLM**: iterative squeeze until SLO-safe minimum cost (`cost-effective-boundary.json`).
- **Static data**: `results-from-cluster/static-up-sweep-20260527-125059/run-4`
- **LLM data**: `showcase_UP/compare-up-sweep-20260525-010051/run-1/llm-run`

---
## Details (squeeze-style table)

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **static**: `optimizer=static_baseline` · `stopped_reason=single_pass_no_apply_loop` · iterations=1 · `best_pass_dir=None`
- **llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=4 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-4` · prov_cost_total=287.084668 (steady=287.064, best_pass=0.3987), util_cost_total=101.817532 (steady=101.808, best_pass=0.1414)

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| static | +0.0 | +0.0 |
| llm | +55.0 | +28.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | static status | static prov cost | static util cost | static p95 | static err | static ach RPS | static cpu% | static mem% | static cpu m | static mem Mi | static cpu lim | static mem lim | static repl | llm status | llm prov cost | llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.2372 | 0.1349 | 3091 | 0.0027 | 194.4 | 57.5 | 45.1 | 50 | 25 | 100 | 50 | 5 | FAIL | 0.0474 | 0.0474 | 5084 | 0 | 191.7 | 299 | 173.9 | 50 | 25 | 100 | 50 | 1 |
| 2 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.1328 | 0.0703 | 1047 | 0 | 280 | 52.9 | 53.8 | 70 | 35 | 200 | 100 | 2 |
| 3 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.2478 | 0.1222 | 815 | 0 | 280 | 49.5 | 46.3 | 87 | 44 | 250 | 100 | 3 |
| 4 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.3987 | 0.1414 | 371 | 0 | 280 | 36.4 | 18.6 | 105 | 53 | 300 | 150 | 4 |

*Iteration count mismatch: static=1, llm=4.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | static status | static prov cost | static util cost | llm status | llm prov cost | llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.2372 | 0.1349 | FAIL | 0.0474 | 0.0474 |
| 2 | — | — | — | FAIL | 0.1328 | 0.0703 |
| 3 | — | — | — | FAIL | 0.2478 | 0.1222 |
| 4 | — | — | — | PASS | 0.3987 | 0.1414 |
