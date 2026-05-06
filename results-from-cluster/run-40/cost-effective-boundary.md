# Cost-Effective Boundary

- Stopped reason: first_fail
- Best pass: /app/results/run-40/iteration-2
- First fail: /app/results/run-40/iteration-3

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | Cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/run-40/iteration-1 | PASS | 130 | 129.6 | 130.0 | 0 | 144.0 | 0.0 | 43.1 | 23.2 | 5 | 100 | 50 | 0.7441 |
| /app/results/run-40/iteration-2 | PASS | 130 | 129.9 | 130.0 | 0 | 97.0 | 0.0 | 74.0 | 39.0 | 3 | 83 | 42 | 0.372 |
| /app/results/run-40/iteration-3 | FAIL | 130 | 100.7 | 106.3 | 2131 | 1467.0 | 0.1098 | 77.8 | 53.7 | 2 | 75 | 38 | 0.2242 |
