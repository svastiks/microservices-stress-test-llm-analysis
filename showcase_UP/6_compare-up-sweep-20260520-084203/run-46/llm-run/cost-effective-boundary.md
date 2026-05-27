# Cost-Effective Boundary

- Stopped reason: recovered_from_underprovisioning
- Best pass: /app/results/squeeze-compare-llm/run-1/iteration-2
- First fail: none

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | Cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-llm/run-1/iteration-1 | FAIL | 260 | 173.9 | 178.5 | 7336 | 5689.0 | 0.0 | 307.6 | 155.1 | 1 | 50 | 25 | 0.0744 |
| /app/results/squeeze-compare-llm/run-1/iteration-2 | PASS | 260 | 259.2 | 260.0 | 0 | 316.0 | 0.0 | 52.6 | 51.5 | 2 | 70 | 35 | 0.2084 |
