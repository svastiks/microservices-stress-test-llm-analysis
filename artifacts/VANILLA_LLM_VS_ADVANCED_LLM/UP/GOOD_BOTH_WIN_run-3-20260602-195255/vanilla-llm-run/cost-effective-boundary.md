# Cost-Effective Boundary

- Stopped reason: recovered_from_underprovisioning
- Best pass: /app/results/squeeze-compare-vanilla-llm/run-1/iteration-2
- First fail: none
- Cost model: weighted · search=0.00593 · steady=136.656 · total=136.66193 (T=0.025h, H=720.0h)

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Prov cost | Util cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-1 | FAIL | 260 | 255.2 | 258.8 | 111 | 2360.0 | 0.0 | 188.0 | 147.5 | 1 | 50 | 25 | 100 | 50 | 0.0474 | 0.0474 |
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-2 | PASS | 260 | 259.3 | 260.0 | 0 | 469.0 | 0.0 | 45.6 | 33.8 | 2 | 100 | 50 | 200 | 100 | 0.1898 | 0.0854 |
