# Cost-Effective Boundary

- Stopped reason: recovered_from_underprovisioning
- Best pass: /app/results/squeeze-compare-llm/run-1/iteration-2
- First fail: none
- Cost model: weighted · search=0.004365 · steady=91.584 · total=91.588365 (T=0.025h, H=720.0h)

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Prov cost | Util cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-llm/run-1/iteration-1 | FAIL | 220 | 218.7 | 220.0 | 0 | 1678.0 | 0.0 | 139.5 | 87.9 | 1 | 50 | 25 | 100 | 50 | 0.0474 | 0.0471 |
| /app/results/squeeze-compare-llm/run-1/iteration-2 | PASS | 220 | 219.7 | 220.0 | 0 | 181.0 | 0.0 | 32.1 | 10.6 | 2 | 67 | 34 | 200 | 100 | 0.1272 | 0.0394 |
