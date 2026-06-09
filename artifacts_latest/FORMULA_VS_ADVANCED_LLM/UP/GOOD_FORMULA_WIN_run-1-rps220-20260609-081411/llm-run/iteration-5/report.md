Current configuration has cpu_util_request_pct at 150.3%, exceeding squeeze gate but p95 latency and throughput meet SLO.
Recommended change: increase CPU/memory by approximately 15% to address the request-relative CPU gate while keeping replicas constant.
Increasing CPU/memory should help to safely maintain cluster performance under the current workload without changing the number of replicas.
Keeping the same number of replicas minimizes cost while we address the utilization bottleneck.
No changes to HPA maxReplicas, which should remain at the current setting to ensure stability.