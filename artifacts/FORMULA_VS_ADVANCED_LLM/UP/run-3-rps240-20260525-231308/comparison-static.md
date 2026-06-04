# Static baseline vs LLM squeeze comparison

- **Target RPS**: 240 (`up_demo`)
- **Static**: thin deployment YAML + HPA (1–5 replicas); one k6 pass; no squeeze apply loop.
- **LLM**: iterative squeeze until SLO-safe minimum cost (`cost-effective-boundary.json`).
- **Static data**: `results-from-cluster/static-up-sweep-20260527-125059/run-2`
- **LLM data**: `showcase_UP/compare-up-sweep-20260525-231308/run-3/llm-run`

---
## Details (squeeze-style table)

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **static**: `optimizer=static_baseline` · `stopped_reason=single_pass_no_apply_loop` · iterations=1 · `best_pass_dir=None`
- **llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=4 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-4` · prov_cost_total=88.206503 (steady=88.2, best_pass=0.1225), util_cost_total=53.932662 (steady=53.928, best_pass=0.0749)

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| static | +0.0 | +0.0 |
| llm | -7.0 | -3.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | static status | static prov cost | static util cost | static p95 | static err | static ach RPS | static cpu% | static mem% | static cpu m | static mem Mi | static cpu lim | static mem lim | static repl | llm status | llm prov cost | llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.2372 | 0.1551 | 3288 | 0 | 158.8 | 66.4 | 47.1 | 50 | 25 | 100 | 50 | 5 | FAIL | 0.0474 | 0.0474 | 1926 | 0 | 240 | 261 | 198 | 50 | 25 | 100 | 50 | 1 |
| 2 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.0237 | 0.0237 | 6e+04 | 0.4603 | 34 | 400.9 | 259.6 | 25 | 12 | 50 | 25 | 1 |
| 3 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.0665 | 0.0405 | 894 | 0 | 240 | 60.1 | 74.6 | 35 | 18 | 100 | 50 | 2 |
| 4 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.1225 | 0.0749 | 442 | 0 | 240 | 62.4 | 37.4 | 43 | 22 | 150 | 100 | 3 |

*Iteration count mismatch: static=1, llm=4.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | static status | static prov cost | static util cost | llm status | llm prov cost | llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.2372 | 0.1551 | FAIL | 0.0474 | 0.0474 |
| 2 | — | — | — | FAIL | 0.0237 | 0.0237 |
| 3 | — | — | — | FAIL | 0.0665 | 0.0405 |
| 4 | — | — | — | PASS | 0.1225 | 0.0749 |
