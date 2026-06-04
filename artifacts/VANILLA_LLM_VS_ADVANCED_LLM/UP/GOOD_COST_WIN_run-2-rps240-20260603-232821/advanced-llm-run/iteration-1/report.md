The current setup has reached a bottleneck in CPU utilization, exceeding the 95% threshold.
The p95 latency of 4574 ms significantly exceeds the SLO target of 500 ms, resulting in SLO violation.
Cost score is low at 0.0949, indicating efficient resource usage, but scaling is necessary to meet workload demands.
Observations suggest that increasing CPU and memory allocation by ~15% is appropriate for recovery.
Horizontal scaling (increasing replicas) is not needed at this time as the current replica count is acceptable.
The proposed changes will hold the number of replicas constant but increase CPU and memory requests to optimize performance.
Further improvements can be made in subsequent iterations after the current vertical scaling adjustment.