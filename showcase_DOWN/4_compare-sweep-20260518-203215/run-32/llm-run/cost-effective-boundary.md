# Cost-Effective Boundary

- Stopped reason: first_fail
- Best pass: /app/results/squeeze-compare-llm/run-43/iteration-2
- First fail: /app/results/squeeze-compare-llm/run-43/iteration-3

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | Cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-llm/run-43/iteration-1 | PASS | 25 | 25.0 | 25.0 | 0 | 6.0 | 0.0 | 56.0 | 29.2 | 3 | 100 | 50 | 0.4465 |
| /app/results/squeeze-compare-llm/run-43/iteration-2 | PASS | 25 | 25.0 | 25.0 | 0 | 23.0 | 0.0 | 81.5 | 39.0 | 3 | 70 | 35 | 0.3125 |
| /app/results/squeeze-compare-llm/run-43/iteration-3 | FAIL | 25 | 25.0 | 25.0 | 0 | 140.0 | 0.0 | 119.5 | 47.7 | 3 | 50 | 25 | 0.2232 |
