# Cost-Effective Boundary

- Stopped reason: recovered_from_underprovisioning
- Best pass: /app/results/squeeze-compare-llm/run-1/iteration-6
- First fail: none
- Cost model: weighted · search=0.057735 · steady=647.64 · total=647.697735 (T=0.025h, H=720.0h)

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Prov cost | Util cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-llm/run-1/iteration-1 | FAIL | 260 | 165.1 | 168.8 | 8212 | 4888.0 | 0.0 | 425.1 | 213.0 | 1 | 50 | 25 | 100 | 50 | 0.0474 | 0.0474 |
| /app/results/squeeze-compare-llm/run-1/iteration-2 | FAIL | 260 | 258.9 | 259.3 | 62 | 1301.0 | 0.0 | 55.5 | 39.8 | 2 | 70 | 35 | 200 | 128 | 0.1328 | 0.0727 |
| /app/results/squeeze-compare-llm/run-1/iteration-3 | FAIL | 260 | 259.0 | 260.0 | 0 | 520.0 | 0.0 | 48.9 | 23.0 | 3 | 90 | 45 | 250 | 192 | 0.2562 | 0.1219 |
| /app/results/squeeze-compare-llm/run-1/iteration-4 | FAIL | 260 | 257.7 | 260.0 | 0 | 631.0 | 0.0 | 36.0 | 10.9 | 4 | 104 | 52 | 300 | 256 | 0.3947 | 0.137 |
| /app/results/squeeze-compare-llm/run-1/iteration-5 | FAIL | 260 | 258.7 | 259.2 | 69 | 1385.0 | 0.0 | 23.4 | 8.0 | 5 | 122 | 61 | 400 | 300 | 0.5788 | 0.1308 |
| /app/results/squeeze-compare-llm/run-1/iteration-6 | PASS | 260 | 259.7 | 260.0 | 0 | 311.0 | 0.0 | 16.9 | 5.8 | 6 | 158 | 79 | 600 | 450 | 0.8995 | 0.1469 |
