# Cost-Effective Boundary

- Stopped reason: first_fail
- Best pass: /app/results/squeeze-compare-vanilla-llm/run-1/iteration-4
- First fail: /app/results/squeeze-compare-vanilla-llm/run-1/iteration-5
- Cost model: weighted · search=0.043883 · steady=136.656 · total=136.699883 (T=0.025h, H=720.0h)

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Prov cost | Util cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-1 | PASS | 45 | 44.9 | 45.0 | 0 | 74.0 | 0.0 | 25.6 | 10.7 | 5 | 150 | 75 | 300 | 150 | 0.7116 | 0.1767 |
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-2 | PASS | 45 | 44.9 | 45.0 | 0 | 74.0 | 0.0 | 26.2 | 17.5 | 4 | 120 | 60 | 240 | 120 | 0.4554 | 0.1173 |
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-3 | PASS | 45 | 45.0 | 45.0 | 0 | 74.0 | 0.0 | 38.1 | 15.8 | 3 | 110 | 55 | 220 | 100 | 0.3131 | 0.1157 |
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-4 | PASS | 45 | 44.9 | 45.0 | 0 | 74.0 | 0.0 | 40.8 | 16.4 | 2 | 100 | 50 | 200 | 90 | 0.1898 | 0.075 |
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-5 | FAIL | 45 | 45.0 | 45.0 | 0 | 5.0 | 0.0 | 64.3 | 23.7 | 1 | 90 | 45 | 180 | 80 | 0.0854 | 0.0531 |
