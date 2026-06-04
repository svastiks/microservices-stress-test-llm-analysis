# Cost-Effective Boundary

- Stopped reason: recovered_from_underprovisioning
- Best pass: /app/results/squeeze-compare-llm/run-1/iteration-3
- First fail: none
- Cost model: weighted · search=0.00569 · steady=95.616 · total=95.62169 (T=0.025h, H=720.0h)

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Prov cost | Util cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-llm/run-1/iteration-1 | FAIL | 220 | 218.2 | 220.0 | 0 | 991.0 | 0.0 | 272.9 | 189.8 | 1 | 50 | 25 | 100 | 50 | 0.0474 | 0.0474 |
| /app/results/squeeze-compare-llm/run-1/iteration-2 | FAIL | 220 | 183.1 | 201.8 | 1642 | 4764.0 | 0.0478 | 283.9 | 172.0 | 1 | 50 | 25 | 75 | 40 | 0.0474 | 0.0474 |
| /app/results/squeeze-compare-llm/run-1/iteration-3 | PASS | 220 | 219.0 | 220.0 | 0 | 394.0 | 0.0 | 51.8 | 45.8 | 2 | 70 | 35 | 150 | 75 | 0.1328 | 0.0684 |
