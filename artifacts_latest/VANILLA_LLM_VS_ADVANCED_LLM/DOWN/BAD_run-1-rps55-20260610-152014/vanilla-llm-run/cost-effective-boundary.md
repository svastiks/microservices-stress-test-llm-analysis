# Cost-Effective Boundary

- Stopped reason: first_fail
- Best pass: /app/results/squeeze-compare-vanilla-llm/run-1/iteration-4
- First fail: /app/results/squeeze-compare-vanilla-llm/run-1/iteration-5
- Cost model: weighted · search=0.04359 · steady=133.776 · total=133.81959 (T=0.025h, H=720.0h)

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Prov cost | Util cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-1 | PASS | 55 | 54.9 | 55.0 | 0 | 74.0 | 0.0 | 26.1 | 10.7 | 5 | 150 | 75 | 300 | 150 | 0.7116 | 0.1801 |
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-2 | PASS | 55 | 54.9 | 55.0 | 0 | 74.0 | 0.0 | 40.9 | 21.2 | 4 | 120 | 60 | 240 | 120 | 0.4554 | 0.1817 |
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-3 | PASS | 55 | 54.9 | 55.0 | 0 | 74.0 | 0.0 | 40.3 | 20.4 | 3 | 108 | 54 | 216 | 108 | 0.3074 | 0.1207 |
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-4 | PASS | 55 | 54.9 | 55.0 | 0 | 74.0 | 0.0 | 44.0 | 15.5 | 2 | 98 | 48 | 194 | 97 | 0.1858 | 0.0791 |
| /app/results/squeeze-compare-vanilla-llm/run-1/iteration-5 | FAIL | 55 | 54.9 | 55.0 | 0 | 6.0 | 0.0 | 82.8 | 24.8 | 1 | 88 | 43 | 155 | 78 | 0.0834 | 0.0666 |
