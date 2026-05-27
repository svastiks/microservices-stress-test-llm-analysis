# Cost-Effective Boundary

- Stopped reason: first_fail
- Best pass: /app/results/squeeze-compare-llm/run-39/iteration-1
- First fail: /app/results/squeeze-compare-llm/run-39/iteration-2

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | Cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-llm/run-39/iteration-1 | PASS | 25 | 25.0 | 25.0 | 0 | 9.0 | 0.0 | 83.5 | 71.7 | 1 | 100 | 50 | 0.1488 |
| /app/results/squeeze-compare-llm/run-39/iteration-2 | FAIL | 25 | 25.0 | 25.0 | 0 | 30.0 | 0.0 | 98.4 | 61.7 | 1 | 90 | 45 | 0.1339 |
