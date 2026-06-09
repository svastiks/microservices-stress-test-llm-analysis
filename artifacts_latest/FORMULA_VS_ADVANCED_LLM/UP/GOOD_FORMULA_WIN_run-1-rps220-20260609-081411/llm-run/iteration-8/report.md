The deployment currently has 2 replicas with a CPU request of 118m and a limit of 230m.
It achieved a p95 latency of 229ms, well within the SLO of 500ms, and an error rate of 0%.
However, cpu_util_request_pct is at 107.1%, indicating under-provisioning and necessitating an increase in CPU/memory requests.
The current utilization and throughput are balanced, but the cpu utilization exceeded the threshold, causing a failure.
With a high usage rate of 107.1% request-relative, we need to increase CPU requests without changing the number of replicas or HPA limits.