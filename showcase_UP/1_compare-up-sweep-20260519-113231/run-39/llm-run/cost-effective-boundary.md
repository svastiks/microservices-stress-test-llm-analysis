# Cost-Effective Boundary

- Stopped reason: recovered_from_underprovisioning
- Best pass: /app/results/squeeze-compare-llm/run-50/iteration-2
- First fail: none

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | Cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-llm/run-50/iteration-1 | FAIL | 220 | 166.7 | 172.7 | 4259 | 6591.0 | 0.0 | 188.2 | 280.7 | 1 | 50 | 25 | 0.0744 |
| /app/results/squeeze-compare-llm/run-50/iteration-2 | PASS | 220 | 219.4 | 220.0 | 0 | 220.0 | 0.0 | 51.0 | 58.1 | 2 | 100 | 50 | 0.2977 |
