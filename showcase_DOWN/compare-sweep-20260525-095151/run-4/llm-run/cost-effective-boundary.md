# Cost-Effective Boundary

- Stopped reason: first_fail
- Best pass: /app/results/squeeze-compare-llm/run-1/iteration-2
- First fail: /app/results/squeeze-compare-llm/run-1/iteration-3
- Cost model: weighted · search=0.039138 · steady=341.568 · total=341.607138 (T=0.025h, H=720.0h)

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Prov cost | Util cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-llm/run-1/iteration-1 | PASS | 45 | 45.0 | 45.0 | 0 | 6.0 | 0.0 | 26.3 | 14.4 | 5 | 150 | 75 | 300 | 150 | 0.7116 | 0.1828 |
| /app/results/squeeze-compare-llm/run-1/iteration-2 | PASS | 45 | 44.9 | 45.0 | 0 | 97.0 | 0.0 | 86.7 | 42.8 | 5 | 100 | 50 | 100 | 50 | 0.4744 | 0.4006 |
| /app/results/squeeze-compare-llm/run-1/iteration-3 | FAIL | 45 | 45.0 | 45.0 | 0 | 190.0 | 0.0 | 107.7 | 47.7 | 5 | 80 | 40 | 80 | 40 | 0.3795 | 0.3693 |
