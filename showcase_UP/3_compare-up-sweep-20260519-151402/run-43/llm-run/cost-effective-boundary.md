# Cost-Effective Boundary

- Stopped reason: recovered_from_underprovisioning
- Best pass: /app/results/squeeze-compare-llm/run-54/iteration-4
- First fail: none

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | Cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-llm/run-54/iteration-1 | FAIL | 220 | 172.3 | 176.8 | 3888 | 4839.0 | 0.0 | 192.4 | 279.6 | 1 | 50 | 25 | 0.0744 |
| /app/results/squeeze-compare-llm/run-54/iteration-2 | FAIL | 220 | 217.6 | 220.0 | 1 | 2565.0 | 0.0 | 106.5 | 166.7 | 1 | 70 | 35 | 0.1042 |
| /app/results/squeeze-compare-llm/run-54/iteration-3 | FAIL | 220 | 219.3 | 220.0 | 0 | 533.0 | 0.0 | 75.5 | 80.2 | 1 | 98 | 49 | 0.1459 |
| /app/results/squeeze-compare-llm/run-54/iteration-4 | PASS | 220 | 219.6 | 220.0 | 0 | 240.0 | 0.0 | 69.5 | 57.7 | 1 | 138 | 70 | 0.2064 |
