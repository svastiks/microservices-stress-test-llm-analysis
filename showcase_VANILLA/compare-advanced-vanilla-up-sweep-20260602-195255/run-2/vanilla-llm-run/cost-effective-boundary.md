# Cost-Effective Boundary

- Stopped reason: recovered_from_underprovisioning
- Best pass: /app/results/squeeze-compare-vanilla-llm/run-1/iteration-2
- First fail: none
- Cost model: weighted · search=0.00593 · steady=136.656 · total=136.66193 (T=0.025h, H=720.0h)

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Prov cost | Util cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-1 | FAIL | 240 | 237.0 | 239.4 | 57 | 2683.0 | 0.0 | 215.3 | 138.1 | 1 | 50 | 25 | 100 | 50 | 0.0474 | 0.0474 |
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-2 | PASS | 240 | 239.3 | 240.0 | 0 | 297.0 | 0.0 | 45.8 | 35.7 | 2 | 100 | 50 | 200 | 100 | 0.1898 | 0.0859 |
