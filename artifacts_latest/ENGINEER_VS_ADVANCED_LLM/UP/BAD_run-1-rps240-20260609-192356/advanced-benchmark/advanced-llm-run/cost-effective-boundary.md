# Cost-Effective Boundary

- Stopped reason: recovered_from_underprovisioning
- Best pass: /app/results/squeeze-compare-llm/run-1/iteration-11
- First fail: none
- Cost model: weighted · search=0.04461 · steady=175.824 · total=175.86861 (T=0.025h, H=720.0h)

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Prov cost | Util cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-llm/run-1/iteration-1 | FAIL | 240 | 231.8 | 235.0 | 449 | 2982.0 | 0.0 | 96.7 | 92.5 | 1 | 50 | 25 | 100 | 50 | 0.0474 | 0.0458 |
| /app/results/squeeze-compare-llm/run-1/iteration-2 | FAIL | 240 | 238.9 | 240.0 | 0 | 771.0 | 0.0 | 93.7 | 52.8 | 2 | 50 | 25 | 100 | 50 | 0.0949 | 0.0869 |
| /app/results/squeeze-compare-llm/run-1/iteration-3 | FAIL | 240 | 239.4 | 240.0 | 0 | 399.0 | 0.0 | 89.8 | 41.0 | 2 | 58 | 29 | 115 | 58 | 0.1101 | 0.0961 |
| /app/results/squeeze-compare-llm/run-1/iteration-4 | FAIL | 240 | 239.5 | 240.0 | 0 | 310.0 | 0.0 | 86.0 | 31.9 | 2 | 67 | 34 | 132 | 66 | 0.1272 | 0.1058 |
| /app/results/squeeze-compare-llm/run-1/iteration-5 | FAIL | 240 | 239.3 | 240.0 | 0 | 347.0 | 0.0 | 76.5 | 27.2 | 2 | 77 | 39 | 152 | 76 | 0.1462 | 0.1081 |
| /app/results/squeeze-compare-llm/run-1/iteration-6 | FAIL | 240 | 239.4 | 240.0 | 0 | 364.0 | 0.0 | 67.5 | 21.8 | 2 | 88 | 45 | 174 | 87 | 0.1672 | 0.1088 |
| /app/results/squeeze-compare-llm/run-1/iteration-7 | FAIL | 240 | 239.6 | 240.0 | 0 | 277.0 | 0.0 | 58.8 | 18.7 | 2 | 100 | 52 | 200 | 100 | 0.1902 | 0.1077 |
| /app/results/squeeze-compare-llm/run-1/iteration-8 | FAIL | 240 | 239.5 | 240.0 | 0 | 393.0 | 0.0 | 56.6 | 18.4 | 2 | 108 | 52 | 216 | 100 | 0.2046 | 0.1119 |
| /app/results/squeeze-compare-llm/run-1/iteration-9 | FAIL | 240 | 239.5 | 240.0 | 0 | 314.0 | 0.0 | 53.0 | 18.3 | 2 | 116 | 52 | 216 | 100 | 0.219 | 0.1125 |
| /app/results/squeeze-compare-llm/run-1/iteration-10 | FAIL | 240 | 239.4 | 240.0 | 0 | 383.0 | 0.0 | 55.6 | 19.2 | 2 | 124 | 52 | 216 | 100 | 0.2334 | 0.126 |
| /app/results/squeeze-compare-llm/run-1/iteration-11 | PASS | 240 | 239.5 | 240.0 | 0 | 313.0 | 0.0 | 46.0 | 18.4 | 2 | 130 | 52 | 260 | 100 | 0.2442 | 0.1095 |
