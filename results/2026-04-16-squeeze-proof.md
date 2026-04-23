# Squeeze Proof: 2026-04-16

This table combines `results/2026-04-16-3` through `results/2026-04-16-11` to show the evidence trail for the efficiency squeeze run.

| Run | Target RPS | Achieved RPS | p95 (ms) | Error Rate | SLO Status | Replicas | CPU req (m) | Mem req (Mi) | Cost Score |
|---|---:|---:|---:|---:|---|---:|---:|---:|---:|
| `2026-04-16-3` | 100 | 99.8 | 7 | 0.0 | PASS | 1 | 30 | 52 | 0.0808 |
| `2026-04-16-4` | 100 | 99.8 | 5 | 0.0 | PASS | 1 | 27 | 47 | 0.0729 |
| `2026-04-16-5` | 100 | 99.8 | 4 | 0.0 | PASS | 1 | 17 | 37 | 0.0531 |
| `2026-04-16-6` | 100 | 99.8 | 6 | 0.0 | PASS | 1 | 15 | 33 | 0.0472 |
| `2026-04-16-7` | 100 | 99.8 | 8 | 0.0 | PASS | 1 | 13 | 30 | 0.0423 |
| `2026-04-16-8` | 100 | 99.8 | 10 | 0.0 | PASS | 1 | 10 | 25 | 0.0344 |
| `2026-04-16-9` | 100 | 99.8 | 5 | 0.0 | PASS | 1 | 9 | 25 | 0.0334 |
| `2026-04-16-10` | 100 | 99.8 | 7 | 0.0 | PASS | 1 | 7 | 25 | 0.0314 |
| `2026-04-16-11` | 100 | 99.8 | 7 | 0.0 | PASS | 1 | 5 | 25 | 0.0294 |

## What this proves

- The offered load was held constant at `100 RPS` for all iterations.
- The achieved arrival rate stayed effectively constant at `99.8 RPS` across all runs.
- The SLO stayed satisfied across all runs:
  - `p95 <= 500ms`
  - `error_rate <= 0.01`
- The requested resources were reduced monotonically:
  - CPU request from `30m` to `5m`
  - Memory request from `52Mi` to `25Mi`
  - Replicas remained at `1`
- The cost score dropped monotonically from `0.0808` to `0.0294`.

## Why the loop stopped

`results/2026-04-16-11/recommended.diff` is empty, so the squeeze loop stopped because the LLM did not propose a further conservative reduction. It did **not** stop on SLO failure in this run series.
