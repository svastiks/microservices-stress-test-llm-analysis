# Cost-Effective Boundary

- Stopped reason: recovered_from_underprovisioning
- Best pass: /app/results/squeeze-compare-llm/run-1/iteration-3
- First fail: none
- Cost model: weighted · search=0.012098 · steady=184.464 · total=184.476098 (T=0.025h, H=720.0h)

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Prov cost | Util cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-llm/run-1/iteration-1 | FAIL | 260 | 163.4 | 166.8 | 8384 | 4141.0 | 0.0 | 46.1 | 12.9 | 2 | 50 | 25 | 100 | 50 | 0.0949 | 0.0421 |
| /app/results/squeeze-compare-llm/run-1/iteration-2 | FAIL | 260 | 257.9 | 260.0 | 0 | 1010.0 | 0.0 | 43.6 | 56.2 | 2 | 70 | 35 | 105 | 53 | 0.1328 | 0.0588 |
| /app/results/squeeze-compare-llm/run-1/iteration-3 | PASS | 260 | 259.5 | 260.0 | 0 | 393.0 | 0.0 | 53.6 | 37.0 | 3 | 90 | 45 | 135 | 70 | 0.2562 | 0.1351 |
