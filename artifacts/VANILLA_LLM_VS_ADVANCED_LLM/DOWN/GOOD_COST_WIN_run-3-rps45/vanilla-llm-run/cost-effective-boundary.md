# Cost-Effective Boundary

- Stopped reason: first_fail
- Best pass: /app/results/squeeze-compare-vanilla-llm/run-1/iteration-5
- First fail: /app/results/squeeze-compare-vanilla-llm/run-1/iteration-6
- Cost model: weighted · search=0.05562 · steady=122.256 · total=122.31162 (T=0.025h, H=720.0h)

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Prov cost | Util cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-1 | PASS | 45 | 44.9 | 45.0 | 0 | 6.0 | 0.0 | 18.4 | 9.3 | 5 | 150 | 75 | 300 | 150 | 0.7116 | 0.1276 |
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-2 | PASS | 45 | 44.9 | 45.0 | 0 | 6.0 | 0.0 | 26.2 | 11.5 | 5 | 120 | 60 | 240 | 120 | 0.5693 | 0.1448 |
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-3 | PASS | 45 | 44.9 | 45.0 | 0 | 6.0 | 0.0 | 36.5 | 21.9 | 4 | 110 | 50 | 220 | 100 | 0.4155 | 0.1488 |
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-4 | PASS | 45 | 44.9 | 45.0 | 0 | 5.0 | 0.0 | 52.9 | 39.2 | 3 | 100 | 45 | 200 | 90 | 0.2832 | 0.148 |
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-5 | PASS | 45 | 44.9 | 45.0 | 0 | 5.0 | 0.0 | 77.9 | 44.2 | 2 | 90 | 40 | 180 | 80 | 0.1698 | 0.1297 |
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-6 | FAIL | 45 | 44.9 | 45.0 | 0 | 6.0 | 0.0 | 140.4 | 76.9 | 1 | 80 | 35 | 160 | 70 | 0.0754 | 0.0746 |
