# Cost-Effective Boundary

- Stopped reason: recovered_from_underprovisioning
- Best pass: /app/results/squeeze-compare-llm/run-1/iteration-5
- First fail: none
- Cost model: weighted · search=0.034763 · steady=409.896 · total=409.930763 (T=0.025h, H=720.0h)

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Prov cost | Util cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-llm/run-1/iteration-1 | FAIL | 280 | 171.0 | 175.5 | 9410 | 6604.0 | 0.0 | 292.8 | 168.9 | 1 | 50 | 25 | 100 | 50 | 0.0474 | 0.0474 |
| /app/results/squeeze-compare-llm/run-1/iteration-2 | FAIL | 280 | 278.6 | 280.0 | 0 | 576.0 | 0.0 | 49.5 | 55.1 | 2 | 70 | 35 | 200 | 100 | 0.1328 | 0.0661 |
| /app/results/squeeze-compare-llm/run-1/iteration-3 | FAIL | 280 | 276.6 | 277.5 | 224 | 1569.0 | 0.0 | 40.6 | 30.9 | 3 | 81 | 41 | 300 | 150 | 0.2307 | 0.0925 |
| /app/results/squeeze-compare-llm/run-1/iteration-4 | FAIL | 280 | 278.0 | 280.0 | 0 | 533.0 | 0.0 | 24.2 | 18.7 | 4 | 108 | 55 | 450 | 150 | 0.4103 | 0.0981 |
| /app/results/squeeze-compare-llm/run-1/iteration-5 | PASS | 280 | 279.0 | 280.0 | 0 | 462.0 | 0.0 | 19.6 | 13.1 | 5 | 120 | 60 | 500 | 180 | 0.5693 | 0.1097 |
