# Cost-Effective Boundary

- Stopped reason: recovered_from_underprovisioning
- Best pass: /app/results/squeeze-compare-llm/run-1/iteration-3
- First fail: none

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-llm/run-1/iteration-1 | FAIL | 280 | 273.4 | 278.0 | 177 | 3153.0 | 0.0 | 256.2 | 189.6 | 1 | 50 | 25 | 100 | 50 | 0.0744 |
| /app/results/squeeze-compare-llm/run-1/iteration-2 | FAIL | 280 | 279.4 | 280.0 | 0 | 515.0 | 0.0 | 22.0 | 12.7 | 2 | 70 | 35 | 400 | 300 | 0.2084 |
| /app/results/squeeze-compare-llm/run-1/iteration-3 | PASS | 280 | 279.4 | 280.0 | 0 | 420.0 | 0.0 | 17.7 | 4.6 | 3 | 81 | 41 | 600 | 450 | 0.3631 |
