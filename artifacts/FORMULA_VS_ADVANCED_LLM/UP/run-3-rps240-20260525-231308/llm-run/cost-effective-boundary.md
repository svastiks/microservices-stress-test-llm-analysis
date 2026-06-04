# Cost-Effective Boundary

- Stopped reason: recovered_from_underprovisioning
- Best pass: /app/results/squeeze-compare-llm/run-1/iteration-4
- First fail: none
- Cost model: weighted · search=0.006503 · steady=88.2 · total=88.206503 (T=0.025h, H=720.0h)

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Prov cost | Util cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-llm/run-1/iteration-1 | FAIL | 240 | 237.4 | 240.0 | 0 | 1926.0 | 0.0 | 261.0 | 198.0 | 1 | 50 | 25 | 100 | 50 | 0.0474 | 0.0474 |
| /app/results/squeeze-compare-llm/run-1/iteration-2 | FAIL | 240 | 29.8 | 34.0 | 18539 | 60001.0 | 0.4603 | 400.9 | 259.6 | 1 | 25 | 12 | 50 | 25 | 0.0237 | 0.0237 |
| /app/results/squeeze-compare-llm/run-1/iteration-3 | FAIL | 240 | 237.9 | 240.0 | 0 | 894.0 | 0.0 | 60.1 | 74.6 | 2 | 35 | 18 | 100 | 50 | 0.0665 | 0.0405 |
| /app/results/squeeze-compare-llm/run-1/iteration-4 | PASS | 240 | 239.2 | 240.0 | 0 | 442.0 | 0.0 | 62.4 | 37.4 | 3 | 43 | 22 | 150 | 100 | 0.1225 | 0.0749 |
