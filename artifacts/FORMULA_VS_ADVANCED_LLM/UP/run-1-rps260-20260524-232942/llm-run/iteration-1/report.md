Current deployment configuration does not meet SLO due to high p95 latency (4888ms) and observed CPU utilization (425.1%) indicating significant under-provisioning.
Vertical scaling is necessary as CPU limits/numbers are exceeded and latency far exceeds acceptable thresholds.
Memory utilization is particularly high (213.0%), indicating it should be increased at least in line with CPU requests to prevent OOM kills.
Increasing both CPU requests and limits, as well as memory requests and limits, is justified to recover application performance.
Will also scale HPA maxReplicas to 2 to allow for performance recovery as workload necessitates splits.
By adjusting resource allocations effectively, the optimization goal is to achieve SLO PASS with a minimized cost_score.