# Cost-Effective Boundary

- Stopped reason: recovered_from_underprovisioning
- Best pass: /app/results/squeeze-compare-formula/run-1/iteration-3
- First fail: none
- Cost model: weighted · search=0.006642 · steady=88.848 · total=88.854642 (T=0.025h, H=720.0h)

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Prov cost | Util cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-formula/run-1/iteration-1 | FAIL | 220 | 178.8 | 183.4 | 3290 | 5126.0 | 0.0 | 94.6 | 134.0 | 1 | 50 | 25 | 100 | 50 | 0.0474 | 0.045 |
| /app/results/squeeze-compare-formula/run-1/iteration-2 | FAIL | 220 | 218.1 | 220.0 | 0 | 1090.0 | 0.0 | 67.1 | 90.5 | 2 | 50 | 25 | 100 | 50 | 0.0949 | 0.0648 |
| /app/results/squeeze-compare-formula/run-1/iteration-3 | PASS | 220 | 219.2 | 220.0 | 0 | 353.0 | 0.0 | 77.8 | 73.6 | 2 | 65 | 33 | 129 | 65 | 0.1234 | 0.0958 |
