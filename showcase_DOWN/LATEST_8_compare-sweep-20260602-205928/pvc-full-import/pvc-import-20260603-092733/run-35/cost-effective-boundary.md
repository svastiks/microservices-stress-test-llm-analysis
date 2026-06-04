# Cost-Effective Boundary

- Stopped reason: up_recovery_max_iterations_reached
- Best pass: none
- First fail: none

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | Cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/run-35/iteration-1 | FAIL | 130 | 101.6 | 127.1 | 265 | 1312.0 | 0.0474 | 61.1 | 42.6 | 3 | 100 | 50 | 0.4465 |
| /app/results/run-35/iteration-2 | FAIL | 130 | 101.1 | 101.8 | 2540 | 1570.0 | 0.0404 | 41.9 | 31.4 | 3 | 139 | 70 | 0.6221 |
| /app/results/run-35/iteration-3 | FAIL | 130 | 129.8 | 129.9 | 7 | 539.0 | 0.0 | 30.4 | 39.2 | 2 | 194 | 98 | 0.5794 |
| /app/results/run-35/iteration-4 | FAIL | 130 | 83.3 | 83.4 | 4199 | 1512.0 | 0.0416 | 25.2 | 29.9 | 2 | 225 | 114 | 0.6727 |
| /app/results/run-35/iteration-5 | FAIL | 130 | 56.5 | 66.6 | 5705 | 1290.0 | 0.0871 | 30.2 | 42.9 | 1 | 313 | 159 | 0.4683 |
