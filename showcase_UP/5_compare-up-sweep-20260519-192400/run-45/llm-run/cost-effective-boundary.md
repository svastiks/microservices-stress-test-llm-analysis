# Cost-Effective Boundary

- Stopped reason: recovered_from_underprovisioning
- Best pass: /app/results/squeeze-compare-llm/run-55/iteration-3
- First fail: none

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | Cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-llm/run-55/iteration-1 | FAIL | 220 | 172.3 | 177.2 | 3849 | 4831.0 | 0.0 | 184.4 | 282.9 | 1 | 50 | 25 | 0.0744 |
| /app/results/squeeze-compare-llm/run-55/iteration-2 | FAIL | 220 | 217.4 | 220.0 | 0 | 1633.0 | 0.0 | 97.5 | 158.5 | 1 | 70 | 35 | 0.1042 |
| /app/results/squeeze-compare-llm/run-55/iteration-3 | PASS | 220 | 219.4 | 220.0 | 0 | 423.0 | 0.0 | 69.6 | 110.7 | 1 | 94 | 47 | 0.1399 |
