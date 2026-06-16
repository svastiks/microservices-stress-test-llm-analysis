# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **advanced-llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=6 · `best_pass_dir=/app/results/squeeze-compare-advanced-llm/run-1/iteration-5` · prov_cost_total=125.772925 (steady=125.712, best_pass=0.1746), util_cost_total=58.196775 (steady=58.176, best_pass=0.0808)
- **vanilla-llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=5 · `best_pass_dir=/app/results/squeeze-compare-vanilla-llm/run-1/iteration-4` · prov_cost_total=136.699883 (steady=136.656, best_pass=0.1898), util_cost_total=54.013445 (steady=54.0, best_pass=0.075)

## Resource delta (first row → last row)

| | 🟩 CPU req (m) | 🟧 Mem req (MiB) |
|---|---:|---:|
| advanced-llm | -72.0 | -35.0 |
| vanilla-llm | -60.0 | -30.0 |

## Combined iterations

One row per iteration index (boundary `rows` order). Rows are **not** matched configs — each arm ran an independent squeeze trajectory. When `paired-baseline-probe.md` exists under each arm, **row 1** shares the same observed burn/cpu% (one k6 window, two optimizer analyses).

| # | advanced-llm status | ⬜ advanced-llm prov cost | ⬜ advanced-llm util cost | advanced-llm p95 | advanced-llm err | advanced-llm ach RPS | advanced-llm cpu% req | advanced-llm mem% | 🟩 advanced-llm cpu m | 🟧 advanced-llm mem Mi | advanced-llm cpu lim | advanced-llm mem lim | advanced-llm repl | vanilla-llm status | ⬜ vanilla-llm prov cost | ⬜ vanilla-llm util cost | vanilla-llm p95 | vanilla-llm err | vanilla-llm ach RPS | vanilla-llm cpu% req | vanilla-llm mem% | 🟩 vanilla-llm cpu m | 🟧 vanilla-llm mem Mi | vanilla-llm cpu lim | vanilla-llm mem lim | vanilla-llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1762 | 74 | 0 | 45 | 51.1 | 11 | 150 | 75 | 300 | 150 | 5 | PASS | 0.7116 | 0.1767 | 74 | 0 | 45 | 51.1 | 10.7 | 150 | 75 | 300 | 150 | 5 |
| 2 | PASS | 0.6407 | 0.1788 | 74 | 0 | 45 | 57.2 | 15.2 | 135 | 68 | 270 | 135 | 5 | PASS | 0.4554 | 0.1173 | 74 | 0 | 45 | 52.3 | 17.5 | 120 | 60 | 240 | 120 | 4 |
| 3 | PASS | 0.4554 | 0.1917 | 74 | 0 | 45 | 81.3 | 17.8 | 120 | 60 | 225 | 120 | 4 | PASS | 0.3131 | 0.1157 | 74 | 0 | 45 | 76.3 | 15.8 | 110 | 55 | 220 | 100 | 3 |
| 4 | PASS | 0.3065 | 0.1274 | 74 | 0 | 45 | 80.1 | 21.4 | 108 | 51 | 203 | 102 | 3 | PASS | 0.1898 | 0.075 | 74 | 0 | 45 | 81.5 | 16.4 | 100 | 50 | 200 | 90 | 2 |
| 5 | PASS | 0.1746 | 0.0808 | 75 | 0 | 45 | 90.1 | 16.6 | 92 | 46 | 173 | 90 | 2 | FAIL | 0.0854 | 0.0531 | 5 | 0 | 45 | 128.7 | 23.7 | 90 | 45 | 180 | 80 | 1 |
| 6 | FAIL | 0.1482 | 0.0761 | 74 | 0 | 45 | 104.3 | 18.5 | 78 | 40 | 153 | 81 | 2 | — | — | — | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: advanced-llm=6, vanilla-llm=5.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | advanced-llm status | ⬜ advanced-llm prov cost | ⬜ advanced-llm util cost | vanilla-llm status | ⬜ vanilla-llm prov cost | ⬜ vanilla-llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1762 | PASS | 0.7116 | 0.1767 |
| 2 | PASS | 0.6407 | 0.1788 | PASS | 0.4554 | 0.1173 |
| 3 | PASS | 0.4554 | 0.1917 | PASS | 0.3131 | 0.1157 |
| 4 | PASS | 0.3065 | 0.1274 | PASS | 0.1898 | 0.075 |
| 5 | PASS | 0.1746 | 0.0808 | FAIL | 0.0854 | 0.0531 |
| 6 | FAIL | 0.1482 | 0.0761 | — | — | — |
