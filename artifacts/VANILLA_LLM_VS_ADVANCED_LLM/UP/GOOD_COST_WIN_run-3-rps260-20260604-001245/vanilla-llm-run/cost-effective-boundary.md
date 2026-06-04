# Cost-Effective Boundary

- Stopped reason: recovered_from_underprovisioning
- Best pass: /app/results/squeeze-compare-vanilla-llm/run-1/iteration-2
- First fail: none
- Cost model: weighted · search=0.00593 · steady=136.656 · total=136.66193 (T=0.025h, H=720.0h)

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Prov cost | Util cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-1 | FAIL | 260 | 231.5 | 241.0 | 1141 | 4620.0 | 0.0 | 162.9 | 84.9 | 1 | 50 | 25 | 100 | 50 | 0.0474 | 0.0471 |
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-2 | PASS | 260 | 258.9 | 260.0 | 0 | 443.0 | 0.0 | 48.8 | 33.0 | 2 | 100 | 50 | 150 | 75 | 0.1898 | 0.0911 |
