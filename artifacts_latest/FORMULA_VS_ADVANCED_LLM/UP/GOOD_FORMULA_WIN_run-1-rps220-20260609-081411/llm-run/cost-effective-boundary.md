# Cost-Effective Boundary

- Stopped reason: recovered_from_underprovisioning
- Best pass: /app/results/squeeze-compare-llm/run-1/iteration-10
- First fail: none
- Cost model: weighted · search=0.041168 · steady=207.216 · total=207.257168 (T=0.025h, H=720.0h)

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Prov cost | Util cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-llm/run-1/iteration-1 | FAIL | 220 | 218.0 | 220.0 | 2 | 3005.0 | 0.0 | 93.9 | 88.4 | 1 | 50 | 25 | 100 | 50 | 0.0474 | 0.0444 |
| /app/results/squeeze-compare-llm/run-1/iteration-2 | FAIL | 220 | 219.3 | 220.0 | 0 | 360.0 | 0.0 | 89.8 | 50.7 | 2 | 50 | 25 | 100 | 50 | 0.0949 | 0.0833 |
| /app/results/squeeze-compare-llm/run-1/iteration-3 | FAIL | 220 | 219.6 | 220.0 | 0 | 261.0 | 0.0 | 90.7 | 44.5 | 2 | 58 | 29 | 115 | 50 | 0.1101 | 0.0972 |
| /app/results/squeeze-compare-llm/run-1/iteration-4 | FAIL | 220 | 219.6 | 220.0 | 0 | 238.0 | 0.0 | 86.9 | 41.1 | 2 | 67 | 29 | 132 | 50 | 0.1263 | 0.1071 |
| /app/results/squeeze-compare-llm/run-1/iteration-5 | FAIL | 220 | 219.6 | 220.0 | 0 | 262.0 | 0.0 | 76.2 | 32.0 | 2 | 77 | 34 | 152 | 58 | 0.1452 | 0.1077 |
| /app/results/squeeze-compare-llm/run-1/iteration-6 | FAIL | 220 | 219.6 | 220.0 | 0 | 278.0 | 0.0 | 67.2 | 27.2 | 2 | 89 | 39 | 174 | 67 | 0.1678 | 0.1097 |
| /app/results/squeeze-compare-llm/run-1/iteration-7 | FAIL | 220 | 219.6 | 220.0 | 0 | 222.0 | 0.0 | 60.8 | 24.1 | 2 | 103 | 45 | 200 | 77 | 0.1942 | 0.1148 |
| /app/results/squeeze-compare-llm/run-1/iteration-8 | FAIL | 220 | 219.6 | 220.0 | 0 | 229.0 | 0.0 | 54.9 | 23.9 | 2 | 118 | 45 | 230 | 77 | 0.2212 | 0.1187 |
| /app/results/squeeze-compare-llm/run-1/iteration-9 | FAIL | 220 | 219.3 | 220.0 | 0 | 227.0 | 0.0 | 48.5 | 22.8 | 2 | 135 | 45 | 265 | 77 | 0.2518 | 0.1199 |
| /app/results/squeeze-compare-llm/run-1/iteration-10 | PASS | 220 | 219.6 | 220.0 | 0 | 252.0 | 0.0 | 47.5 | 22.9 | 2 | 155 | 45 | 265 | 77 | 0.2878 | 0.1345 |
