# Cost-Effective Boundary

- Stopped reason: recovered_from_underprovisioning
- Best pass: /app/results/squeeze-compare-llm/run-1/iteration-3
- First fail: none
- Cost model: weighted · search=0.004097 · steady=60.12 · total=60.124097 (T=0.025h, H=720.0h)

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Prov cost | Util cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-llm/run-1/iteration-1 | FAIL | 200 | 199.1 | 200.0 | 0 | 816.0 | 0.0 | 275.0 | 184.0 | 1 | 50 | 25 | 100 | 50 | 0.0474 | 0.0474 |
| /app/results/squeeze-compare-llm/run-1/iteration-2 | FAIL | 200 | 198.9 | 200.0 | 0 | 1021.0 | 0.0 | 210.3 | 128.7 | 1 | 35 | 15 | 100 | 50 | 0.033 | 0.033 |
| /app/results/squeeze-compare-llm/run-1/iteration-3 | PASS | 200 | 199.7 | 200.0 | 0 | 192.0 | 0.0 | 46.1 | 32.0 | 2 | 44 | 22 | 200 | 100 | 0.0835 | 0.0379 |
