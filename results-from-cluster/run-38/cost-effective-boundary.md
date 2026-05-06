# Cost-Effective Boundary

- Stopped reason: first_fail
- Best pass: /app/results/run-38/iteration-1
- First fail: /app/results/run-38/iteration-2

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | Cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/run-38/iteration-1 | PASS | 130 | 129.9 | 130.0 | 0 | 254.0 | 0.0 | 45.8 | 18.6 | 7 | 100 | 50 | 1.0418 |
| /app/results/run-38/iteration-2 | FAIL | 130 | 93.2 | 102.8 | 2450 | 1574.0 | 0.1092 | 61.0 | 37.1 | 3 | 85 | 43 | 0.381 |
