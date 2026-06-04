# Cost-Effective Boundary

- Stopped reason: recovered_from_underprovisioning
- Best pass: /app/results/squeeze-compare-llm/run-1/iteration-3
- First fail: none
- Cost model: weighted · search=0.009015 · steady=157.176 · total=157.185015 (T=0.025h, H=720.0h)

| Run | Status | Target RPS | Achieved RPS | Achieved RPS (Target Window) | Dropped Iterations | p95 ms | Error rate | CPU util % | Mem util % | Replicas | CPU req (m) | Mem req (Mi) | CPU lim (m) | Mem lim (Mi) | Prov cost | Util cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| /app/results/squeeze-compare-llm/run-1/iteration-1 | FAIL | 260 | 255.9 | 259.2 | 69 | 2205.0 | 0.0 | 582.9 | 265.5 | 1 | 50 | 25 | 100 | 50 | 0.0474 | 0.0474 |
| /app/results/squeeze-compare-llm/run-1/iteration-2 | FAIL | 260 | 259.5 | 260.0 | 0 | 491.0 | 0.0 | 213.3 | 108.2 | 1 | 100 | 50 | 150 | 75 | 0.0949 | 0.0949 |
| /app/results/squeeze-compare-llm/run-1/iteration-3 | PASS | 260 | 259.5 | 260.0 | 0 | 296.0 | 0.0 | 37.2 | 14.8 | 2 | 115 | 58 | 300 | 150 | 0.2183 | 0.0787 |
