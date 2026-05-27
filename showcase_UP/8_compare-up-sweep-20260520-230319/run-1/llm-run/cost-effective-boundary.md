# Cost-Effective Boundary

- Stopped reason: recovered_from_underprovisioning
- Best pass: /app/results/squeeze-compare-llm/run-1/iteration-2
- First fail: none

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-llm/run-1/iteration-1 | FAIL | 220 | 218.0 | 220.0 | 0 | 1157.0 | 0.0 | 269.4 | 183.1 | 1 | 50 | 25 | 100 | 50 | 0.0744 |
| /app/results/squeeze-compare-llm/run-1/iteration-2 | PASS | 220 | 219.5 | 220.0 | 0 | 246.0 | 0.0 | 46.5 | 41.3 | 2 | 63 | 32 | 200 | 100 | 0.1885 |
