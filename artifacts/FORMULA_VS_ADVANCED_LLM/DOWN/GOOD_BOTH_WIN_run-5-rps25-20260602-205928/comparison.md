# Squeeze optimizer comparison

## Summary

- **Cost model**: `weighted` (see cost_model.md) — **prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u

- **formula**: `optimizer=formula` · `stopped_reason=first_fail` · iterations=11 · `best_pass_dir=/app/results/squeeze-compare-formula/run-1/iteration-10` · prov_cost_total=121.544802 (steady=121.464, best_pass=0.1687), util_cost_total=76.648525 (steady=76.608, best_pass=0.1064)
- **llm**: `optimizer=llm` · `stopped_reason=first_fail` · iterations=10 · `best_pass_dir=/app/results/squeeze-compare-llm/run-1/iteration-9` · prov_cost_total=13.741065 (steady=13.68, best_pass=0.019), util_cost_total=10.316998 (steady=10.296, best_pass=0.0143)

## Resource delta (first row → last row)

| | 🟩 CPU req (m) | 🟧 Mem req (MiB) |
|---|---:|---:|
| formula | -93.0 | -43.0 |
| llm | -140.0 | -70.0 |

## Combined iterations

One row per iteration index (boundary `rows` order).

| # | formula status | ⬜ formula prov cost | ⬜ formula util cost | formula p95 | formula err | formula ach RPS | formula cpu% | formula mem% | 🟩 formula cpu m | 🟧 formula mem Mi | formula cpu lim | formula mem lim | formula repl | llm status | ⬜ llm prov cost | ⬜ llm util cost | llm p95 | llm err | llm ach RPS | llm cpu% | llm mem% | 🟩 llm cpu m | 🟧 llm mem Mi | llm cpu lim | llm mem lim | llm repl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1692 | 6 | 0 | 25 | 24.3 | 14.1 | 150 | 75 | 300 | 150 | 5 | PASS | 0.7116 | 0.1428 | 6 | 0 | 25 | 20.5 | 12.1 | 150 | 75 | 300 | 150 | 5 |
| 2 | PASS | 0.5363 | 0.2078 | 6 | 0 | 25 | 39.7 | 21.2 | 113 | 57 | 226 | 113 | 5 | PASS | 0.4744 | 0.1399 | 6 | 0 | 25 | 30.3 | 14.4 | 100 | 50 | 300 | 150 | 5 |
| 3 | PASS | 0.3532 | 0.2172 | 6 | 0 | 25 | 63.1 | 32.3 | 93 | 47 | 185 | 93 | 4 | PASS | 0.4744 | 0.1472 | 6 | 0 | 25 | 31.9 | 15.1 | 100 | 50 | 300 | 150 | 5 |
| 4 | PASS | 0.338 | 0.1939 | 6 | 0 | 25 | 58.6 | 34.8 | 89 | 45 | 176 | 89 | 4 | PASS | 0.2773 | 0.1334 | 6 | 0 | 25 | 49.4 | 25 | 73 | 37 | 217 | 109 | 4 |
| 5 | PASS | 0.228 | 0.1473 | 8 | 0 | 25 | 66.1 | 37.4 | 80 | 41 | 158 | 80 | 3 | PASS | 0.1993 | 0.104 | 6 | 0 | 25 | 53.7 | 24.4 | 70 | 35 | 200 | 100 | 3 |
| 6 | PASS | 0.2166 | 0.1326 | 7 | 0 | 25 | 62.8 | 32.4 | 76 | 39 | 151 | 76 | 3 | PASS | 0.1423 | 0.0638 | 6 | 0 | 25 | 45.9 | 24.8 | 50 | 25 | 200 | 100 | 3 |
| 7 | PASS | 0.2082 | 0.116 | 24 | 0 | 25 | 57 | 33 | 73 | 38 | 144 | 73 | 3 | PASS | 0.0869 | 0.0473 | 6 | 0 | 25 | 56 | 33 | 30 | 20 | 150 | 75 | 3 |
| 8 | PASS | 0.1855 | 0.1158 | 29 | 0 | 25 | 63.7 | 40.4 | 65 | 34 | 128 | 65 | 3 | PASS | 0.0479 | 0.0382 | 6 | 0 | 25 | 82.1 | 41.3 | 25 | 15 | 125 | 70 | 2 |
| 9 | PASS | 0.1771 | 0.1092 | 46 | 0 | 25 | 63 | 38.6 | 62 | 33 | 122 | 62 | 3 | PASS | 0.019 | 0.0143 | 4 | 0 | 25 | 78.2 | 27.4 | 20 | 10 | 125 | 70 | 1 |
| 10 | PASS | 0.1687 | 0.1064 | 39 | 0 | 25 | 64.3 | 42 | 59 | 32 | 116 | 59 | 3 | FAIL | 0.0095 | 0.009 | 36 | 0 | 25 | 97.7 | 38.3 | 10 | 5 | 100 | 50 | 1 |
| 11 | FAIL | 0.1089 | 0.1056 | 6 | 0 | 25 | 99.9 | 50.3 | 57 | 32 | 111 | 57 | 2 | — | — | — | — | — | — | — | — | — | — | — | — | — |

*Iteration count mismatch: formula=11, llm=10.*

## Cost per iteration

One row per iteration; prov cost and util cost only (easier to scan than the full table above).

| # | formula status | ⬜ formula prov cost | ⬜ formula util cost | llm status | ⬜ llm prov cost | ⬜ llm util cost |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | PASS | 0.7116 | 0.1692 | PASS | 0.7116 | 0.1428 |
| 2 | PASS | 0.5363 | 0.2078 | PASS | 0.4744 | 0.1399 |
| 3 | PASS | 0.3532 | 0.2172 | PASS | 0.4744 | 0.1472 |
| 4 | PASS | 0.338 | 0.1939 | PASS | 0.2773 | 0.1334 |
| 5 | PASS | 0.228 | 0.1473 | PASS | 0.1993 | 0.104 |
| 6 | PASS | 0.2166 | 0.1326 | PASS | 0.1423 | 0.0638 |
| 7 | PASS | 0.2082 | 0.116 | PASS | 0.0869 | 0.0473 |
| 8 | PASS | 0.1855 | 0.1158 | PASS | 0.0479 | 0.0382 |
| 9 | PASS | 0.1771 | 0.1092 | PASS | 0.019 | 0.0143 |
| 10 | PASS | 0.1687 | 0.1064 | FAIL | 0.0095 | 0.009 |
| 11 | FAIL | 0.1089 | 0.1056 | — | — | — |
