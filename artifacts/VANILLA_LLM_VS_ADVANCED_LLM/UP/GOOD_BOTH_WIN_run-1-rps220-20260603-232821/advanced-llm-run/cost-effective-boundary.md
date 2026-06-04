# Cost-Effective Boundary

- Stopped reason: recovered_from_underprovisioning
- Best pass: /app/results/squeeze-compare-advanced-llm/run-1/iteration-2
- First fail: none
- Cost model: weighted · search=0.003557 · steady=68.328 · total=68.331557 (T=0.025h, H=720.0h)

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Prov cost | Util cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-advanced-llm/run-1/iteration-1 | FAIL | 220 | 217.1 | 219.9 | 8 | 1636.0 | 0.0 | 103.7 | 71.4 | 1 | 50 | 25 | 100 | 50 | 0.0474 | 0.0467 |
| /app/results/squeeze-compare-advanced-llm/run-1/iteration-2 | PASS | 220 | 219.0 | 220.0 | 0 | 328.0 | 0.0 | 59.3 | 65.7 | 2 | 50 | 25 | 100 | 50 | 0.0949 | 0.0566 |
