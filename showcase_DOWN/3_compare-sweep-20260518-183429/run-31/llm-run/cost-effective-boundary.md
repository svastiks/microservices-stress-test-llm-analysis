# Cost-Effective Boundary

- Stopped reason: first_fail
- Best pass: /app/results/squeeze-compare-llm/run-41/iteration-2
- First fail: /app/results/squeeze-compare-llm/run-41/iteration-3

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | Cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-llm/run-41/iteration-1 | PASS | 25 | 25.0 | 25.0 | 0 | 6.0 | 0.0 | 43.1 | 30.5 | 3 | 100 | 50 | 0.4465 |
| /app/results/squeeze-compare-llm/run-41/iteration-2 | PASS | 25 | 25.0 | 25.0 | 0 | 12.0 | 0.0 | 59.9 | 36.7 | 3 | 83 | 42 | 0.372 |
| /app/results/squeeze-compare-llm/run-41/iteration-3 | FAIL | 25 | 25.0 | 25.0 | 0 | 38.0 | 0.0 | 98.8 | 47.7 | 2 | 75 | 38 | 0.2242 |
