# Cost-Effective Boundary

- Stopped reason: recovered_from_underprovisioning
- Best pass: /app/results/squeeze-compare-vanilla-llm/run-1/iteration-2
- First fail: none
- Cost model: weighted · search=0.007118 · steady=136.656 · total=136.663118 (T=0.025h, H=720.0h)

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Prov cost | Util cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-1 | FAIL | 220 | 217.4 | 220.0 | 0 | 1595.0 | 0.0 | 61.2 | 37.7 | 2 | 50 | 25 | 100 | 50 | 0.0949 | 0.0569 |
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-2 | PASS | 220 | 219.6 | 220.0 | 0 | 221.0 | 0.0 | 42.1 | 26.8 | 2 | 100 | 50 | 200 | 75 | 0.1898 | 0.0784 |
