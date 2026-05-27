# Cost-Effective Boundary

- Stopped reason: recovered_from_underprovisioning
- Best pass: /app/results/squeeze-compare-llm/run-1/iteration-4
- First fail: none
- Cost model: weighted · search=0.020668 · steady=287.064 · total=287.084668 (T=0.025h, H=720.0h)

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Prov cost | Util cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-llm/run-1/iteration-1 | FAIL | 280 | 187.4 | 191.7 | 7945 | 5084.0 | 0.0 | 299.0 | 173.9 | 1 | 50 | 25 | 100 | 50 | 0.0474 | 0.0474 |
| /app/results/squeeze-compare-llm/run-1/iteration-2 | FAIL | 280 | 277.6 | 280.0 | 2 | 1047.0 | 0.0 | 52.9 | 53.8 | 2 | 70 | 35 | 200 | 100 | 0.1328 | 0.0703 |
| /app/results/squeeze-compare-llm/run-1/iteration-3 | FAIL | 280 | 278.8 | 280.0 | 0 | 815.0 | 0.0 | 49.5 | 46.3 | 3 | 87 | 44 | 250 | 100 | 0.2478 | 0.1222 |
| /app/results/squeeze-compare-llm/run-1/iteration-4 | PASS | 280 | 279.1 | 280.0 | 0 | 371.0 | 0.0 | 36.4 | 18.6 | 4 | 105 | 53 | 300 | 150 | 0.3987 | 0.1414 |
