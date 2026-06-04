# Cost-Effective Boundary

- Stopped reason: recovered_from_underprovisioning
- Best pass: /app/results/squeeze-compare-advanced-llm/run-1/iteration-2
- First fail: none
- Cost model: weighted · search=0.004505 · steady=95.616 · total=95.620505 (T=0.025h, H=720.0h)

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Prov cost | Util cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-advanced-llm/run-1/iteration-1 | FAIL | 240 | 236.9 | 240.0 | 0 | 1774.0 | 0.0 | 262.2 | 128.4 | 1 | 50 | 25 | 100 | 50 | 0.0474 | 0.0474 |
| /app/results/squeeze-compare-advanced-llm/run-1/iteration-2 | PASS | 240 | 239.6 | 240.0 | 0 | 325.0 | 0.0 | 44.2 | 30.5 | 2 | 70 | 35 | 200 | 100 | 0.1328 | 0.0578 |
