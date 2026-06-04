# Static baseline vs LLM squeeze comparison

- **Target RPS**: 220 (`up_demo`)
- **Static**: thin deployment YAML + HPA (1–5 replicas); one k6 pass; no squeeze apply loop.
- **LLM**: iterative squeeze until SLO-safe minimum cost (`cost-effective-boundary.json`).
- **Static data**: `results-from-cluster/static-up-sweep-20260527-125059/run-1`
- **LLM data**: `showcase_UP/compare-up-sweep-20260525-231308/run-2/llm-run`

---
## Details (squeeze-style table)

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **static**: `optimizer=static_baseline` · `stopped_reason=single_pass_no_apply_loop` · iterations=1 · `best_pass_dir=None`
- **llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-3` · prov_cost_total=95.62169 (steady=95.616, best_pass=0.1328), util_cost_total=49.25208 (steady=49.248, best_pass=0.0684)

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| static | +0.0 | +0.0 |
| llm | +20.0 | +10.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | static status | static prov cost | static util cost | static p95 | static err | static ach RPS | static cpu% | static mem% | static cpu m | static mem Mi | static cpu lim | static mem lim | static repl | llm status | llm prov cost | llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.2372 | 0.1897 | 2985 | 0 | 170.6 | 82.1 | 40.4 | 50 | 25 | 100 | 50 | 5 | FAIL | 0.0474 | 0.0474 | 991 | 0 | 220 | 272.9 | 189.8 | 50 | 25 | 100 | 50 | 1 |
| 2 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.0474 | 0.0474 | 4764 | 0.0478 | 201.8 | 283.9 | 172 | 50 | 25 | 75 | 40 | 1 |
| 3 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.1328 | 0.0684 | 394 | 0 | 220 | 51.8 | 45.8 | 70 | 35 | 150 | 75 | 2 |

*Iteration count mismatch: static=1, llm=3.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | static status | static prov cost | static util cost | llm status | llm prov cost | llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.2372 | 0.1897 | FAIL | 0.0474 | 0.0474 |
| 2 | — | — | — | FAIL | 0.0474 | 0.0474 |
| 3 | — | — | — | PASS | 0.1328 | 0.0684 |
