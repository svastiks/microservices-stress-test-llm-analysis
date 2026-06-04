# Static baseline vs LLM squeeze comparison

- **Target RPS**: 260 (`up_demo`)
- **Static**: thin deployment YAML + HPA (1–5 replicas); one k6 pass; no squeeze apply loop.
- **LLM**: iterative squeeze until SLO-safe minimum cost (`cost-effective-boundary.json`).
- **Static data**: `results-from-cluster/static-up-sweep-20260527-125059/run-3`
- **LLM data**: `showcase_UP/compare-up-sweep-20260525-231308/run-4/llm-run`

---
## Details (squeeze-style table)

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **static**: `optimizer=static_baseline` · `stopped_reason=single_pass_no_apply_loop` · iterations=1 · `best_pass_dir=None`
- **llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-3` · prov_cost_total=157.185015 (steady=157.176, best_pass=0.2183), util_cost_total=56.669525 (steady=56.664, best_pass=0.0787)

## Resource delta (first row → last row)

| | CPU req (m) | Mem req (MiB) |
|---|---:|---:|
| static | +0.0 | +0.0 |
| llm | +65.0 | +33.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | static status | static prov cost | static util cost | static p95 | static err | static ach RPS | static cpu% | static mem% | static cpu m | static mem Mi | static cpu lim | static mem lim | static repl | llm status | llm prov cost | llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | llm cpu m | llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.2372 | 0.1374 | 4184 | 0.0003 | 169.4 | 58.5 | 47.6 | 50 | 25 | 100 | 50 | 5 | FAIL | 0.0474 | 0.0474 | 2205 | 0 | 259.2 | 582.9 | 265.5 | 50 | 25 | 100 | 50 | 1 |
| 2 | — | — | — | — | — | — | — | — | — | — | — | — | — | FAIL | 0.0949 | 0.0949 | 491 | 0 | 260 | 213.3 | 108.2 | 100 | 50 | 150 | 75 | 1 |
| 3 | — | — | — | — | — | — | — | — | — | — | — | — | — | PASS | 0.2183 | 0.0787 | 296 | 0 | 260 | 37.2 | 14.8 | 115 | 58 | 300 | 150 | 2 |

*Iteration count mismatch: static=1, llm=3.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | static status | static prov cost | static util cost | llm status | llm prov cost | llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.2372 | 0.1374 | FAIL | 0.0474 | 0.0474 |
| 2 | — | — | — | FAIL | 0.0949 | 0.0949 |
| 3 | — | — | — | PASS | 0.2183 | 0.0787 |
