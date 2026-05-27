# Cost-Effective Boundary

- Stopped reason: recovered_from_underprovisioning
- Best pass: /app/results/squeeze-compare-formula/run-1/iteration-3
- First fail: none
- Cost model: weighted · search=0.01127 · steady=194.832 · total=194.84327 (T=0.025h, H=720.0h)

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Prov cost | Util cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-formula/run-1/iteration-1 | FAIL | 280 | 184.4 | 190.8 | 8025 | 6861.0 | 0.0 | 463.7 | 197.7 | 1 | 50 | 25 | 100 | 50 | 0.0474 | 0.0474 |
| /app/results/squeeze-compare-formula/run-1/iteration-2 | FAIL | 280 | 273.6 | 277.3 | 244 | 1786.0 | 0.0 | 67.0 | 99.9 | 2 | 70 | 35 | 139 | 70 | 0.1328 | 0.0912 |
| /app/results/squeeze-compare-formula/run-1/iteration-3 | PASS | 280 | 278.7 | 280.0 | 0 | 488.0 | 0.0 | 57.0 | 50.7 | 3 | 95 | 48 | 189 | 95 | 0.2706 | 0.1533 |
