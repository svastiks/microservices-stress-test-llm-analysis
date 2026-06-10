# Cost-Effective Boundary

- Stopped reason: recovered_from_underprovisioning
- Best pass: /app/results/squeeze-compare-vanilla-llm/run-1/iteration-6
- First fail: none
- Cost model: weighted · search=0.026913 · steady=246.744 · total=246.770913 (T=0.025h, H=720.0h)

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Prov cost | Util cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-1 | FAIL | 260 | 253.2 | 257.3 | 246 | 2411.0 | 0.0 | 95.7 | 92.9 | 1 | 50 | 25 | 100 | 50 | 0.0474 | 0.0453 |
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-2 | FAIL | 260 | 259.2 | 260.0 | 0 | 588.0 | 0.0 | 85.0 | 41.2 | 2 | 60 | 30 | 120 | 60 | 0.1139 | 0.0942 |
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-3 | FAIL | 260 | 259.4 | 260.0 | 0 | 434.0 | 0.0 | 82.0 | 30.9 | 2 | 72 | 36 | 144 | 72 | 0.1366 | 0.1084 |
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-4 | FAIL | 260 | 259.5 | 260.0 | 0 | 586.0 | 0.0 | 74.9 | 27.1 | 2 | 80 | 40 | 160 | 80 | 0.1518 | 0.11 |
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-5 | FAIL | 260 | 258.9 | 260.0 | 0 | 328.0 | 0.0 | 62.2 | 19.1 | 3 | 100 | 48 | 180 | 96 | 0.2841 | 0.1706 |
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-6 | PASS | 260 | 259.2 | 260.0 | 0 | 327.0 | 0.0 | 51.1 | 16.5 | 3 | 120 | 64 | 220 | 112 | 0.3427 | 0.1687 |
