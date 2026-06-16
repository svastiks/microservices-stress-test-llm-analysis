# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **advanced-llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=10 · `best_pass_dir=/app/results/squeeze-compare-advanced-llm/run-1/iteration-10` · prov_cost_total=169.23865 (steady=169.2, best_pass=0.235), util_cost_total=76.416865 (steady=76.392, best_pass=0.1061)
- **vanilla-llm**: `optimizer=llm` · `stopped_reason=recovered_from_underprovisioning` · iterations=3 · `best_pass_dir=/app/results/squeeze-compare-vanilla-llm/run-1/iteration-3` · prov_cost_total=201.468828 (steady=201.456, best_pass=0.2798), util_cost_total=91.951013 (steady=91.944, best_pass=0.1277)

## Resource delta (first row → last row)

| | 🟩 CPU req (m) | 🟧 Mem req (MiB) |
|---|---:|---:|
| advanced-llm | +75.0 | +26.0 |
| vanilla-llm | +100.0 | +25.0 |

## Combined iterations

One row per iteration index (boundary `rows` order). Rows are **not** matched configs — each arm ran an independent squeeze trajectory. When `paired-baseline-probe.md` exists under each arm, **row 1** shares the same observed burn/cpu% (one k6 window, two optimizer analyses).

| # | advanced-llm status | ⬜ advanced-llm prov cost | ⬜ advanced-llm util cost | advanced-llm p95 | advanced-llm err | advanced-llm ach RPS | advanced-llm cpu% req | advanced-llm mem% | 🟩 advanced-llm cpu m | 🟧 advanced-llm mem Mi | advanced-llm cpu lim | advanced-llm mem lim | advanced-llm repl | vanilla-llm status | ⬜ vanilla-llm prov cost | ⬜ vanilla-llm util cost | vanilla-llm p95 | vanilla-llm err | vanilla-llm ach RPS | vanilla-llm cpu% req | vanilla-llm mem% | 🟩 vanilla-llm cpu m | 🟧 vanilla-llm mem Mi | vanilla-llm cpu lim | vanilla-llm mem lim | vanilla-llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0451 | 2659 | 0 | 220 | 191.1 | 87.9 | 50 | 25 | 100 | 50 | 1 | FAIL | 0.0474 | 0.0434 | 1547 | 0 | 220 | 183.5 | 87 | 50 | 25 | 100 | 50 | 1 |
| 2 | FAIL | 0.0949 | 0.0812 | 473 | 0 | 220 | 175.6 | 45.2 | 50 | 25 | 100 | 50 | 2 | FAIL | 0.1859 | 0.1094 | 220 | 0 | 220 | 119.6 | 29.8 | 100 | 30 | 200 | 60 | 2 |
| 3 | FAIL | 0.1101 | 0.095 | 288 | 0 | 220 | 176.3 | 39.2 | 58 | 29 | 115 | 58 | 2 | PASS | 0.2798 | 0.1277 | 227 | 0 | 220 | 77.3 | 24.7 | 150 | 50 | 250 | 70 | 2 |
| 4 | FAIL | 0.127 | 0.1009 | 251 | 0 | 220 | 161.6 | 31.9 | 67 | 33 | 132 | 67 | 2 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 5 | FAIL | 0.146 | 0.1047 | 247 | 0 | 220 | 146.6 | 23.8 | 77 | 38 | 152 | 77 | 2 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 6 | FAIL | 0.167 | 0.1074 | 218 | 0 | 220 | 131.9 | 20.8 | 88 | 44 | 174 | 89 | 2 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 7 | FAIL | 0.1918 | 0.1091 | 219 | 0 | 220 | 117.1 | 17.1 | 101 | 51 | 200 | 102 | 2 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 8 | FAIL | 0.2062 | 0.1199 | 266 | 0 | 220 | 110.5 | 18.1 | 109 | 51 | 200 | 102 | 2 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 9 | FAIL | 0.2206 | 0.1252 | 232 | 0 | 220 | 100.2 | 17.8 | 117 | 51 | 200 | 102 | 2 | — | — | — | — | — | — | — | — | — | — | — | — | — |
| 10 | PASS | 0.235 | 0.1061 | 227 | 0 | 220 | 92.8 | 17 | 125 | 51 | 250 | 102 | 2 | — | — | — | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: advanced-llm=10, vanilla-llm=3.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | advanced-llm status | ⬜ advanced-llm prov cost | ⬜ advanced-llm util cost | vanilla-llm status | ⬜ vanilla-llm prov cost | ⬜ vanilla-llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | FAIL | 0.0474 | 0.0451 | FAIL | 0.0474 | 0.0434 |
| 2 | FAIL | 0.0949 | 0.0812 | FAIL | 0.1859 | 0.1094 |
| 3 | FAIL | 0.1101 | 0.095 | PASS | 0.2798 | 0.1277 |
| 4 | FAIL | 0.127 | 0.1009 | — | — | — |
| 5 | FAIL | 0.146 | 0.1047 | — | — | — |
| 6 | FAIL | 0.167 | 0.1074 | — | — | — |
| 7 | FAIL | 0.1918 | 0.1091 | — | — | — |
| 8 | FAIL | 0.2062 | 0.1199 | — | — | — |
| 9 | FAIL | 0.2206 | 0.1252 | — | — | — |
| 10 | PASS | 0.235 | 0.1061 | — | — | — |
