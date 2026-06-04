# Cost-Effective Boundary

- Stopped reason: first_fail
- Best pass: /app/results/squeeze-compare-llm/run-1/iteration-6
- First fail: /app/results/squeeze-compare-llm/run-1/iteration-7
- Cost model: weighted · search=0.05656 · steady=83.016 · total=83.07256 (T=0.025h, H=720.0h)

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Prov cost | Util cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-llm/run-1/iteration-1 | PASS | 25 | 25.0 | 25.0 | 0 | 6.0 | 0.0 | 19.6 | 9.5 | 5 | 150 | 75 | 300 | 150 | 0.7116 | 0.1358 |
| /app/results/squeeze-compare-llm/run-1/iteration-2 | PASS | 25 | 25.0 | 25.0 | 0 | 6.0 | 0.0 | 44.9 | 21.0 | 5 | 100 | 50 | 200 | 100 | 0.4744 | 0.2072 |
| /app/results/squeeze-compare-llm/run-1/iteration-3 | PASS | 25 | 25.0 | 25.0 | 0 | 6.0 | 0.0 | 52.7 | 27.0 | 5 | 90 | 45 | 180 | 90 | 0.427 | 0.2194 |
| /app/results/squeeze-compare-llm/run-1/iteration-4 | PASS | 25 | 25.0 | 25.0 | 0 | 7.0 | 0.0 | 65.7 | 41.7 | 4 | 75 | 37 | 150 | 75 | 0.2845 | 0.1834 |
| /app/results/squeeze-compare-llm/run-1/iteration-5 | PASS | 25 | 25.0 | 25.0 | 0 | 19.0 | 0.0 | 53.5 | 36.0 | 4 | 50 | 30 | 150 | 75 | 0.1917 | 0.1005 |
| /app/results/squeeze-compare-llm/run-1/iteration-6 | PASS | 25 | 25.0 | 25.0 | 0 | 59.0 | 0.0 | 94.5 | 49.5 | 3 | 40 | 25 | 100 | 50 | 0.1153 | 0.1057 |
| /app/results/squeeze-compare-llm/run-1/iteration-7 | FAIL | 25 | 25.0 | 25.0 | 0 | 94.0 | 0.0 | 146.9 | 91.7 | 2 | 30 | 20 | 80 | 40 | 0.0579 | 0.0576 |
