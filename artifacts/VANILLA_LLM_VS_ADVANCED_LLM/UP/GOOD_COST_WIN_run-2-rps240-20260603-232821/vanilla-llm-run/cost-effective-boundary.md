# Cost-Effective Boundary

- Stopped reason: recovered_from_underprovisioning
- Best pass: /app/results/squeeze-compare-vanilla-llm/run-1/iteration-2
- First fail: none
- Cost model: weighted · search=0.00588 · steady=135.216 · total=135.22188 (T=0.025h, H=720.0h)

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Prov cost | Util cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-1 | FAIL | 240 | 229.3 | 235.9 | 245 | 2978.0 | 0.0 | 137.9 | 83.6 | 1 | 50 | 25 | 100 | 50 | 0.0474 | 0.047 |
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-2 | PASS | 240 | 239.2 | 240.0 | 0 | 251.0 | 0.0 | 54.0 | 37.7 | 2 | 100 | 40 | 150 | 60 | 0.1878 | 0.1001 |
