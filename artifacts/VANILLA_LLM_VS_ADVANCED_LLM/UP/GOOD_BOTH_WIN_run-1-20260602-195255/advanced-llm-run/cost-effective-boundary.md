# Cost-Effective Boundary

- Stopped reason: recovered_from_underprovisioning
- Best pass: /app/results/squeeze-compare-advanced-llm/run-1/iteration-2
- First fail: none
- Cost model: weighted · search=0.00441 · steady=92.88 · total=92.88441 (T=0.025h, H=720.0h)

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Prov cost | Util cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-advanced-llm/run-1/iteration-1 | FAIL | 220 | 218.3 | 220.0 | 0 | 1542.0 | 0.0 | 104.5 | 79.5 | 1 | 50 | 25 | 100 | 50 | 0.0474 | 0.0469 |
| /app/results/squeeze-compare-advanced-llm/run-1/iteration-2 | PASS | 220 | 219.6 | 220.0 | 0 | 301.0 | 0.0 | 53.3 | 25.3 | 2 | 68 | 34 | 150 | 100 | 0.129 | 0.0669 |
