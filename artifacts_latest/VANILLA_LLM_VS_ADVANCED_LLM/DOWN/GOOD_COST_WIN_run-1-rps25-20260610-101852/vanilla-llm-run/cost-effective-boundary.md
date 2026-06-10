# Cost-Effective Boundary

- Stopped reason: first_fail
- Best pass: /app/results/squeeze-compare-vanilla-llm/run-1/iteration-4
- First fail: /app/results/squeeze-compare-vanilla-llm/run-1/iteration-5
- Cost model: weighted · search=0.043883 · steady=136.656 · total=136.699883 (T=0.025h, H=720.0h)

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Prov cost | Util cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-1 | PASS | 25 | 25.0 | 25.0 | 0 | 74.0 | 0.0 | 25.6 | 10.5 | 5 | 150 | 75 | 300 | 150 | 0.7116 | 0.1766 |
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-2 | PASS | 25 | 25.0 | 25.0 | 0 | 74.0 | 0.0 | 25.4 | 17.0 | 4 | 120 | 60 | 240 | 120 | 0.4554 | 0.1137 |
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-3 | PASS | 25 | 25.0 | 25.0 | 0 | 74.0 | 0.0 | 37.9 | 14.1 | 3 | 110 | 55 | 220 | 110 | 0.3131 | 0.1148 |
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-4 | PASS | 25 | 25.0 | 25.0 | 0 | 75.0 | 0.0 | 37.9 | 14.7 | 2 | 100 | 50 | 200 | 100 | 0.1898 | 0.0697 |
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-5 | FAIL | 25 | 25.0 | 25.0 | 0 | 5.0 | 0.0 | 61.5 | 20.8 | 1 | 90 | 45 | 180 | 90 | 0.0854 | 0.0507 |
