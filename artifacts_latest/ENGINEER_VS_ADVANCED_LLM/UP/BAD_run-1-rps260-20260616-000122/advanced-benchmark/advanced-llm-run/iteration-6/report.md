The deployment was under-provisioned for the observed workload, leading to a CPU utilization that exceeded the allowable threshold.
SLO pass was achieved with latency well within acceptable limits, but the CPU request percentage was above 100%, indicating a need for increased CPU and memory resources.
A coupled increase in CPU and memory requests by approximately 15% was determined necessary to resolve the CPU utilization exceedance while maintaining cost efficiency.
The current configuration successfully met the request per second (RPS) target, yet improvements are essential for CPU request metrics.
Current utilization metrics indicate that additional replicas cannot be added due to already being at the limit (2 replicas). Hence, a vertical scaling approach is recommended.