# Cost-Effective Boundary

- Stopped reason: up_recovery_max_iterations_reached
- Best pass: none
- First fail: none

| Run | Status | Target RPS | Achieved RPS | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | Cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/run-27/iteration-1 | FAIL | 800 | 121.3 | 6883.0 | 0.6074 | 56.7 | 37.2 | 1 | 100 | 50 | 0.4465 |
| /app/results/run-27/iteration-2 | FAIL | 800 | 56.9 | 60000.0 | 0.217 | 29.6 | 26.1 | 1 | 125 | 75 | 0.793 |
| /app/results/run-27/iteration-3 | FAIL | 800 | 24.5 | 60001.0 | 0.5233 | 67.0 | 48.4 | 2 | 200 | 100 | 0.5953 |
