# Cost-Effective Boundary

- Stopped reason: recovered_from_underprovisioning
- Best pass: /app/results/squeeze-compare-vanilla-llm/run-1/iteration-3
- First fail: none
- Cost model: weighted · search=0.012828 · steady=201.456 · total=201.468828 (T=0.025h, H=720.0h)

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Prov cost | Util cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-1 | FAIL | 220 | 218.1 | 220.0 | 0 | 1547.0 | 0.0 | 91.8 | 87.0 | 1 | 50 | 25 | 100 | 50 | 0.0474 | 0.0434 |
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-2 | FAIL | 220 | 219.6 | 220.0 | 0 | 220.0 | 0.0 | 59.8 | 29.8 | 2 | 100 | 30 | 200 | 60 | 0.1859 | 0.1094 |
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-3 | PASS | 220 | 219.6 | 220.0 | 0 | 227.0 | 0.0 | 46.4 | 24.7 | 2 | 150 | 50 | 250 | 70 | 0.2798 | 0.1277 |
