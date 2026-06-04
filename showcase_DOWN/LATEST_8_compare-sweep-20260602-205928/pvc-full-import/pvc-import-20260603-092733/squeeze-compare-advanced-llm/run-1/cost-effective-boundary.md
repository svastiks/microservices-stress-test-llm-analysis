# Cost-Effective Boundary

- Stopped reason: first_fail
- Best pass: /app/results/squeeze-compare-advanced-llm/run-1/iteration-2
- First fail: /app/results/squeeze-compare-advanced-llm/run-1/iteration-3
- Cost model: weighted · search=0.039138 · steady=341.568 · total=341.607138 (T=0.025h, H=720.0h)

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Prov cost | Util cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-advanced-llm/run-1/iteration-1 | PASS | 25 | 25.0 | 25.0 | 0 | 6.0 | 0.0 | 24.0 | 12.8 | 5 | 150 | 75 | 300 | 150 | 0.7116 | 0.1667 |
| /app/results/squeeze-compare-advanced-llm/run-1/iteration-2 | PASS | 25 | 25.0 | 25.0 | 0 | 11.0 | 0.0 | 60.6 | 34.4 | 5 | 100 | 50 | 150 | 75 | 0.4744 | 0.2811 |
| /app/results/squeeze-compare-advanced-llm/run-1/iteration-3 | FAIL | 25 | 25.0 | 25.0 | 0 | 60.0 | 0.0 | 116.5 | 60.7 | 4 | 100 | 50 | 100 | 50 | 0.3795 | 0.3719 |
