# Cost-Effective Boundary

- Stopped reason: recovered_from_underprovisioning
- Best pass: /app/results/squeeze-compare-llm/run-1/iteration-2
- First fail: none
- Cost model: weighted · search=0.00446 · steady=94.32 · total=94.32446 (T=0.025h, H=720.0h)

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Prov cost | Util cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-llm/run-1/iteration-1 | FAIL | 240 | 238.0 | 240.0 | 0 | 1646.0 | 0.0 | 152.5 | 141.9 | 1 | 50 | 25 | 100 | 50 | 0.0474 | 0.0474 |
| /app/results/squeeze-compare-llm/run-1/iteration-2 | PASS | 240 | 239.5 | 240.0 | 0 | 329.0 | 0.0 | 59.7 | 33.9 | 2 | 69 | 35 | 150 | 100 | 0.131 | 0.0765 |
