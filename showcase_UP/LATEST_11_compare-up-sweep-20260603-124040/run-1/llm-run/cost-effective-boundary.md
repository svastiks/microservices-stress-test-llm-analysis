# Cost-Effective Boundary

- Stopped reason: recovered_from_underprovisioning
- Best pass: /app/results/squeeze-compare-llm/run-1/iteration-2
- First fail: none
- Cost model: weighted · search=0.003557 · steady=68.328 · total=68.331557 (T=0.025h, H=720.0h)

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Prov cost | Util cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-llm/run-1/iteration-1 | FAIL | 240 | 237.4 | 239.3 | 62 | 2388.0 | 0.0 | 162.7 | 143.7 | 1 | 50 | 25 | 100 | 50 | 0.0474 | 0.0474 |
| /app/results/squeeze-compare-llm/run-1/iteration-2 | PASS | 240 | 239.1 | 240.0 | 0 | 443.0 | 0.0 | 57.6 | 80.0 | 2 | 50 | 25 | 100 | 50 | 0.0949 | 0.0557 |
