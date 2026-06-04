# Cost-Effective Boundary

- Stopped reason: recovered_from_underprovisioning
- Best pass: /app/results/squeeze-compare-advanced-llm/run-1/iteration-3
- First fail: none
- Cost model: weighted · search=0.00631 · steady=79.272 · total=79.27831 (T=0.025h, H=720.0h)

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Prov cost | Util cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-advanced-llm/run-1/iteration-1 | FAIL | 260 | 224.3 | 231.2 | 1726 | 5862.0 | 0.0 | 39.5 | 83.8 | 1 | 50 | 25 | 100 | 50 | 0.0474 | 0.0198 |
| /app/results/squeeze-compare-advanced-llm/run-1/iteration-2 | FAIL | 260 | 255.5 | 260.0 | 0 | 1000.0 | 0.0 | 48.1 | 68.9 | 2 | 50 | 25 | 100 | 50 | 0.0949 | 0.0467 |
| /app/results/squeeze-compare-advanced-llm/run-1/iteration-3 | PASS | 260 | 258.9 | 260.0 | 0 | 395.0 | 0.0 | 68.4 | 59.4 | 2 | 58 | 29 | 115 | 58 | 0.1101 | 0.0748 |
