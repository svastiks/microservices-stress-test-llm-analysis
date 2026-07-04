# Cost-Effective Boundary

- Stopped reason: recovered_from_underprovisioning
- Best pass: /app/results/squeeze-compare-llm/run-1/iteration-10
- First fail: none
- Cost model: weighted · search=0.039743 · steady=179.496 · total=179.535743 (T=0.025h, H=720.0h)

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Prov cost | Util cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-llm/run-1/iteration-1 | FAIL | 220 | 216.0 | 219.7 | 27 | 3454.0 | 0.0 | 89.5 | 89.2 | 1 | 50 | 25 | 100 | 50 | 0.0474 | 0.0425 |
| /app/results/squeeze-compare-llm/run-1/iteration-2 | FAIL | 220 | 219.5 | 220.0 | 0 | 385.0 | 0.0 | 91.1 | 45.8 | 2 | 50 | 25 | 100 | 50 | 0.0949 | 0.0842 |
| /app/results/squeeze-compare-llm/run-1/iteration-3 | FAIL | 220 | 219.5 | 220.0 | 0 | 282.0 | 0.0 | 88.7 | 39.1 | 2 | 58 | 29 | 115 | 57 | 0.1101 | 0.0948 |
| /app/results/squeeze-compare-llm/run-1/iteration-4 | FAIL | 220 | 219.6 | 220.0 | 0 | 251.0 | 0.0 | 84.6 | 30.1 | 2 | 67 | 34 | 132 | 66 | 0.1272 | 0.104 |
| /app/results/squeeze-compare-llm/run-1/iteration-5 | FAIL | 220 | 219.6 | 220.0 | 0 | 253.0 | 0.0 | 77.7 | 25.5 | 2 | 77 | 39 | 152 | 76 | 0.1462 | 0.1096 |
| /app/results/squeeze-compare-llm/run-1/iteration-6 | FAIL | 220 | 219.6 | 220.0 | 0 | 257.0 | 0.0 | 68.0 | 20.9 | 2 | 88 | 45 | 174 | 87 | 0.1672 | 0.1095 |
| /app/results/squeeze-compare-llm/run-1/iteration-7 | FAIL | 220 | 219.6 | 220.0 | 0 | 251.0 | 0.0 | 58.2 | 17.6 | 2 | 101 | 52 | 200 | 100 | 0.192 | 0.1076 |
| /app/results/squeeze-compare-llm/run-1/iteration-8 | FAIL | 220 | 219.7 | 220.0 | 0 | 230.0 | 0.0 | 49.4 | 15.4 | 2 | 116 | 60 | 230 | 115 | 0.2205 | 0.105 |
| /app/results/squeeze-compare-llm/run-1/iteration-9 | FAIL | 220 | 219.6 | 220.0 | 0 | 231.0 | 0.0 | 26.3 | 15.7 | 2 | 124 | 60 | 460 | 115 | 0.2349 | 0.0605 |
| /app/results/squeeze-compare-llm/run-1/iteration-10 | PASS | 220 | 219.6 | 220.0 | 0 | 283.0 | 0.0 | 12.9 | 16.2 | 2 | 132 | 60 | 920 | 115 | 0.2493 | 0.0325 |
