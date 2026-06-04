# Cost-Effective Boundary

- Stopped reason: first_fail
- Best pass: /app/results/squeeze-compare-llm/run-1/iteration-3
- First fail: /app/results/squeeze-compare-llm/run-1/iteration-4
- Cost model: weighted · search=0.043285 · steady=256.032 · total=256.075285 (T=0.025h, H=720.0h)

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Prov cost | Util cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-llm/run-1/iteration-1 | PASS | 55 | 54.9 | 55.0 | 0 | 6.0 | 0.0 | 21.3 | 15.3 | 5 | 150 | 75 | 300 | 150 | 0.7116 | 0.1494 |
| /app/results/squeeze-compare-llm/run-1/iteration-2 | PASS | 55 | 54.9 | 55.0 | 0 | 6.0 | 0.0 | 44.4 | 25.0 | 5 | 100 | 50 | 200 | 100 | 0.4744 | 0.2059 |
| /app/results/squeeze-compare-llm/run-1/iteration-3 | PASS | 55 | 54.9 | 55.0 | 0 | 25.0 | 0.0 | 62.4 | 33.6 | 5 | 75 | 37 | 150 | 75 | 0.3556 | 0.2167 |
| /app/results/squeeze-compare-llm/run-1/iteration-4 | FAIL | 55 | 54.9 | 55.0 | 0 | 53.0 | 0.0 | 103.6 | 65.3 | 4 | 50 | 25 | 100 | 50 | 0.1898 | 0.1864 |
