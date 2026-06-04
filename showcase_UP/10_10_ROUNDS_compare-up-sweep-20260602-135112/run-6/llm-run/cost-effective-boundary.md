# Cost-Effective Boundary

- Stopped reason: recovered_from_underprovisioning
- Best pass: /app/results/squeeze-compare-llm/run-1/iteration-2
- First fail: none
- Cost model: weighted · search=0.004505 · steady=95.616 · total=95.620505 (T=0.025h, H=720.0h)

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Prov cost | Util cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-llm/run-1/iteration-1 | FAIL | 260 | 167.4 | 170.9 | 8020 | 2805.0 | 0.0016 | 98.4 | 30.1 | 1 | 50 | 25 | 100 | 50 | 0.0474 | 0.045 |
| /app/results/squeeze-compare-llm/run-1/iteration-2 | PASS | 260 | 259.2 | 260.0 | 0 | 466.0 | 0.0 | 33.0 | 27.2 | 2 | 70 | 35 | 200 | 100 | 0.1328 | 0.0434 |
