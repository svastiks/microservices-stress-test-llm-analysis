# Cost-Effective Boundary

- Stopped reason: recovered_from_underprovisioning
- Best pass: /app/results/squeeze-compare-formula/run-1/iteration-3
- First fail: none
- Cost model: weighted · search=0.0107 · steady=178.416 · total=178.4267 (T=0.025h, H=720.0h)

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Prov cost | Util cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-formula/run-1/iteration-1 | FAIL | 280 | 173.4 | 178.9 | 9102 | 6576.0 | 0.0 | 446.1 | 168.6 | 1 | 50 | 25 | 100 | 50 | 0.0474 | 0.0474 |
| /app/results/squeeze-compare-formula/run-1/iteration-2 | FAIL | 280 | 277.7 | 280.0 | 0 | 1012.0 | 0.0 | 67.9 | 87.3 | 2 | 70 | 35 | 139 | 70 | 0.1328 | 0.0915 |
| /app/results/squeeze-compare-formula/run-1/iteration-3 | PASS | 280 | 279.0 | 280.0 | 0 | 497.0 | 0.0 | 61.2 | 54.6 | 3 | 87 | 44 | 172 | 87 | 0.2478 | 0.1508 |
