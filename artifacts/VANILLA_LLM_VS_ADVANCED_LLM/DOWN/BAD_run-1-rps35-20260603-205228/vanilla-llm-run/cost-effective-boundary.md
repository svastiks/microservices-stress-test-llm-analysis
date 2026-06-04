# Cost-Effective Boundary

- Stopped reason: first_fail
- Best pass: /app/results/squeeze-compare-vanilla-llm/run-1/iteration-7
- First fail: /app/results/squeeze-compare-vanilla-llm/run-1/iteration-8
- Cost model: weighted · search=0.063625 · steady=94.968 · total=95.031625 (T=0.025h, H=720.0h)

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Prov cost | Util cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-1 | PASS | 35 | 35.0 | 35.0 | 0 | 6.0 | 0.0 | 17.0 | 9.1 | 5 | 150 | 75 | 300 | 150 | 0.7116 | 0.1181 |
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-2 | PASS | 35 | 35.0 | 35.0 | 0 | 6.0 | 0.0 | 24.7 | 11.4 | 5 | 120 | 60 | 240 | 120 | 0.5693 | 0.1367 |
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-3 | PASS | 35 | 35.0 | 35.0 | 0 | 6.0 | 0.0 | 52.0 | 28.9 | 3 | 110 | 50 | 220 | 100 | 0.3116 | 0.1587 |
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-4 | PASS | 35 | 35.0 | 35.0 | 0 | 6.0 | 0.0 | 56.4 | 31.8 | 3 | 100 | 45 | 200 | 90 | 0.2832 | 0.1565 |
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-5 | PASS | 35 | 35.0 | 35.0 | 0 | 6.0 | 0.0 | 51.8 | 28.1 | 3 | 90 | 40 | 180 | 80 | 0.2547 | 0.1292 |
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-6 | PASS | 35 | 35.0 | 35.0 | 0 | 5.0 | 0.0 | 44.9 | 23.9 | 3 | 80 | 35 | 160 | 70 | 0.2263 | 0.0994 |
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-7 | PASS | 35 | 35.0 | 35.0 | 0 | 50.0 | 0.0 | 81.5 | 16.3 | 2 | 70 | 30 | 120 | 60 | 0.1319 | 0.1036 |
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-8 | FAIL | 35 | 34.9 | 35.0 | 0 | 95.0 | 0.0 | 163.0 | 73.2 | 1 | 60 | 25 | 100 | 50 | 0.0564 | 0.0558 |
