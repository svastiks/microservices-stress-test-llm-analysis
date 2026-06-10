# Cost-Effective Boundary

- Stopped reason: first_fail
- Best pass: /app/results/squeeze-compare-vanilla-llm/run-1/iteration-4
- First fail: /app/results/squeeze-compare-vanilla-llm/run-1/iteration-5
- Cost model: weighted · search=0.043807 · steady=135.936 · total=135.979807 (T=0.025h, H=720.0h)

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Prov cost | Util cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-1 | PASS | 25 | 25.0 | 25.0 | 0 | 74.0 | 0.0 | 25.4 | 10.5 | 5 | 150 | 75 | 300 | 150 | 0.7116 | 0.1753 |
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-2 | PASS | 25 | 25.0 | 25.0 | 0 | 74.0 | 0.0 | 24.6 | 16.9 | 4 | 120 | 60 | 240 | 120 | 0.4554 | 0.1102 |
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-3 | PASS | 25 | 25.0 | 25.0 | 0 | 74.0 | 0.0 | 37.0 | 15.3 | 3 | 110 | 50 | 220 | 100 | 0.3116 | 0.1121 |
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-4 | PASS | 25 | 25.0 | 25.0 | 0 | 74.0 | 0.0 | 38.0 | 16.2 | 2 | 100 | 45 | 200 | 90 | 0.1888 | 0.0698 |
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-5 | FAIL | 25 | 25.0 | 25.0 | 0 | 5.0 | 0.0 | 68.0 | 23.2 | 1 | 90 | 40 | 160 | 80 | 0.0849 | 0.056 |
