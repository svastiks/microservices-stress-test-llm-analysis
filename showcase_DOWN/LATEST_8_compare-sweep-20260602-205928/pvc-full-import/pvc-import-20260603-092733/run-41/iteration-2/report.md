# Report on the `robot-shop-web` service stress-test
- The SLO for p95 latency (500 ms) was violated as the observed p95 latency was 1161 ms.
- The error rate was also above the acceptable level at 0.0447, indicating issues under load.
- Current resource allocation appears under-provisioned; CPU utilization was at 50.3% with memory at 15.7%.
- Cost score indicates reasonable usage, but adjustments are needed to meet SLO.
- Suggested action is to incrementally scale up resource requests and replicas, while focusing on SLO compliance through continued load testing with the same workload.