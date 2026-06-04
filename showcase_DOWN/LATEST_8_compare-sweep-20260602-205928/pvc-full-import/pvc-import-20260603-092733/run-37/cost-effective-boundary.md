# Cost-Effective Boundary

- Stopped reason: up_recovery_max_iterations_reached
- Best pass: none
- First fail: none

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | Cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/run-37/iteration-1 | FAIL | 130 | 129.5 | 129.7 | 31 | 1023.0 | 0.0 | 40.0 | 19.0 | 4 | 100 | 50 | 0.5953 |
| /app/results/run-37/iteration-2 | FAIL | 130 | 97.1 | 129.4 | 49 | 233.0 | 0.0467 | 41.9 | 19.3 | 4 | 124 | 62 | 0.7382 |
| /app/results/run-37/iteration-3 | FAIL | 130 | 105.5 | 111.1 | 1703 | 1378.0 | 0.0556 | 28.7 | 12.3 | 5 | 173 | 87 | 1.2898 |
| /app/results/run-37/iteration-4 | FAIL | 130 | 128.1 | 128.2 | 162 | 1262.0 | 0.0 | 18.3 | 7.9 | 6 | 241 | 121 | 2.155 |
| /app/results/run-37/iteration-5 | FAIL | 130 | 128.2 | 128.4 | 148 | 1253.0 | 0.0 | 16.7 | 7.0 | 7 | 307 | 154 | 3.2017 |
