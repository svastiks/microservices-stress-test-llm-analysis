# Cost-Effective Boundary

- Stopped reason: recovered_from_underprovisioning
- Best pass: /app/results/squeeze-compare-llm/run-1/iteration-2
- First fail: none
- Cost model: weighted · search=0.004505 · steady=95.616 · total=95.620505 (T=0.025h, H=720.0h)

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Prov cost | Util cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-llm/run-1/iteration-1 | FAIL | 220 | 158.3 | 161.2 | 5289 | 3376.0 | 0.0 | 101.5 | 24.9 | 1 | 50 | 25 | 100 | 50 | 0.0474 | 0.0456 |
| /app/results/squeeze-compare-llm/run-1/iteration-2 | PASS | 220 | 219.5 | 220.0 | 0 | 204.0 | 0.0 | 32.5 | 23.9 | 2 | 70 | 35 | 200 | 100 | 0.1328 | 0.0426 |
