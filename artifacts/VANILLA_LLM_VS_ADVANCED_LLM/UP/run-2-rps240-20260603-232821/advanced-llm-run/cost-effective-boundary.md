# Cost-Effective Boundary

- Stopped reason: recovered_from_underprovisioning
- Best pass: /app/results/squeeze-compare-advanced-llm/run-1/iteration-3
- First fail: none
- Cost model: weighted · search=0.006972 · steady=88.344 · total=88.350972 (T=0.025h, H=720.0h)

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Prov cost | Util cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-advanced-llm/run-1/iteration-1 | FAIL | 240 | 231.1 | 237.7 | 138 | 4574.0 | 0.0 | 97.2 | 39.7 | 2 | 50 | 25 | 100 | 50 | 0.0949 | 0.0894 |
| /app/results/squeeze-compare-advanced-llm/run-1/iteration-2 | FAIL | 240 | 237.3 | 240.0 | 0 | 996.0 | 0.0 | 160.1 | 96.1 | 1 | 65 | 29 | 115 | 58 | 0.0613 | 0.0612 |
| /app/results/squeeze-compare-advanced-llm/run-1/iteration-3 | PASS | 240 | 239.4 | 240.0 | 0 | 285.0 | 0.0 | 57.6 | 56.3 | 2 | 65 | 29 | 115 | 58 | 0.1227 | 0.0706 |
