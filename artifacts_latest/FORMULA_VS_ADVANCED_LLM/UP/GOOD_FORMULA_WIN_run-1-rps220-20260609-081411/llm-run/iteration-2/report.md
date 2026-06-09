The workload achieved the target RPS of 220.0, but SLO failed due to cpu_utilization_exceeded.
Current metrics show cpu_util_request_pct at 179.5%, significantly above the acceptable limit (95%).
SLO latency (p95 = 360ms) is well within the threshold (500ms), indicating low latency performance.
Utilization metrics indicate that CPU resources are saturated while memory usage is within acceptable limits.
Since replicas are already at 2 and increasing further is not an option this iteration, a vertical CPU/memory adjustment is necessary.