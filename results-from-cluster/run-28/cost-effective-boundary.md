# Cost-Effective Boundary

- Stopped reason: up_recovery_max_iterations_reached
- Best pass: none
- First fail: none

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | Cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/run-28/iteration-1 | FAIL | 800 | 138.4 | 140.4 | 59363 | 6303.0 | 0.4226 | 47.8 | 36.4 | 3 | 100 | 50 | 0.4465 |
| /app/results/run-28/iteration-2 | FAIL | 800 | 43.6 | 58.1 | 66299 | 38939.0 | 0.4253 | 32.0 | 28.1 | 4 | 125 | 75 | 0.793 |
| /app/results/run-28/iteration-3 | FAIL | 800 | 45.8 | 59.7 | 66629 | 60000.0 | 0.252 | 35.5 | 35.2 | 4 | 125 | 75 | 0.793 |
