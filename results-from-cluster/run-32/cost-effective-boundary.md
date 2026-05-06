# Cost-Effective Boundary

- Stopped reason: empty_recommended_diff
- Best pass: none
- First fail: none

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | Cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/run-32/iteration-1 | FAIL | 130 | 97.5 | 130.0 | 0 | 389.0 | 0.0418 | 64.8 | 37.6 | 3 | 100 | 50 | 0.4465 |
| /app/results/run-32/iteration-2 | FAIL | 130 | 101.2 | 106.8 | 2090 | 1748.0 | 0.05 | 33.6 | 24.1 | 4 | 139 | 70 | 0.8294 |
| /app/results/run-32/iteration-3 | FAIL | 130 | 51.5 | 68.7 | 5350 | 1770.0 | 0.0694 | 24.1 | 25.6 | 3 | 194 | 98 | 0.8691 |
