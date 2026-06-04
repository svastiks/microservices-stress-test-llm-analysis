# Cost-Effective Boundary

- Stopped reason: recovered_from_underprovisioning
- Best pass: /app/results/squeeze-compare-llm/run-1/iteration-4
- First fail: none
- Cost model: weighted · search=0.022438 · steady=327.888 · total=327.910438 (T=0.025h, H=720.0h)

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Prov cost | Util cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-llm/run-1/iteration-1 | FAIL | 260 | 181.4 | 186.1 | 6651 | 4728.0 | 0.0 | 533.7 | 191.5 | 1 | 50 | 25 | 100 | 50 | 0.0474 | 0.0474 |
| /app/results/squeeze-compare-llm/run-1/iteration-2 | FAIL | 260 | 257.8 | 258.7 | 118 | 1490.0 | 0.0 | 76.0 | 47.8 | 2 | 70 | 35 | 200 | 100 | 0.1328 | 0.099 |
| /app/results/squeeze-compare-llm/run-1/iteration-3 | FAIL | 260 | 257.5 | 258.8 | 109 | 1414.0 | 0.0 | 38.5 | 38.7 | 3 | 92 | 46 | 200 | 100 | 0.2619 | 0.1008 |
| /app/results/squeeze-compare-llm/run-1/iteration-4 | PASS | 260 | 259.6 | 260.0 | 0 | 384.0 | 0.0 | 33.4 | 20.3 | 4 | 120 | 60 | 250 | 150 | 0.4554 | 0.149 |
