# Cost-Effective Boundary

- Stopped reason: first_fail
- Best pass: /app/results/squeeze-compare-llm/run-1/iteration-2
- First fail: /app/results/squeeze-compare-llm/run-1/iteration-3
- Cost model: weighted · search=0.03819 · steady=341.568 · total=341.60619 (T=0.025h, H=720.0h)

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Prov cost | Util cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-llm/run-1/iteration-1 | PASS | 55 | 54.9 | 55.0 | 0 | 7.0 | 0.0 | 24.4 | 14.8 | 5 | 150 | 75 | 300 | 150 | 0.7116 | 0.1701 |
| /app/results/squeeze-compare-llm/run-1/iteration-2 | PASS | 55 | 54.9 | 55.0 | 0 | 124.0 | 0.0 | 89.2 | 50.3 | 5 | 100 | 50 | 100 | 50 | 0.4744 | 0.4137 |
| /app/results/squeeze-compare-llm/run-1/iteration-3 | FAIL | 55 | 54.9 | 55.0 | 0 | 122.0 | 0.0 | 128.2 | 70.5 | 4 | 90 | 45 | 90 | 45 | 0.3416 | 0.3364 |
