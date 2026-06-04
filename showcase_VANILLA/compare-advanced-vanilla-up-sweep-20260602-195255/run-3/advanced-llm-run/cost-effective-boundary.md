# Cost-Effective Boundary

- Stopped reason: recovered_from_underprovisioning
- Best pass: /app/results/squeeze-compare-advanced-llm/run-1/iteration-2
- First fail: none
- Cost model: weighted · search=0.004505 · steady=95.616 · total=95.620505 (T=0.025h, H=720.0h)

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Prov cost | Util cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-advanced-llm/run-1/iteration-1 | FAIL | 260 | 256.5 | 259.5 | 43 | 1937.0 | 0.0 | 242.4 | 141.2 | 1 | 50 | 25 | 100 | 50 | 0.0474 | 0.0474 |
| /app/results/squeeze-compare-advanced-llm/run-1/iteration-2 | PASS | 260 | 258.1 | 260.0 | 0 | 462.0 | 0.0 | 55.5 | 38.3 | 2 | 70 | 35 | 150 | 100 | 0.1328 | 0.0725 |
