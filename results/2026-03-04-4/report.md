# **Failure Summary**: SLO violations occurred, specifically a p95 latency violation (1023ms vs. target 500ms).

# **Scaling**: Scaled during test: no (replicas stayed at 7).

# **Root Cause Analysis**: The service experienced a failed test due to violating the p95 latency SLO while under low CPU and memory utilization. Thus, we suspect the limit on replicas (7) was reached, inhibiting capacity to handle peak load effectively. Current metrics do not indicate over-provisioning but rather a limitation due to max replica count.

# **Evidence**: This assessment is supported by the following metrics: 
- observed.latency_ms.p95: 1023ms 
- observed.cpu_util_pct: 9.3% 
- observed.mem_util_pct: 19.2% 
- observed.replicas_max: 7

# **Recommended Fix**: Increase the maximum replicas to allow more instances during peak load circumstances. This should allow for scaling beyond the current limit when the load exceeds what 7 replicas can handle.

# **Next Experiment**: Increase the target requests per second to 550 to find safe lambda_crit. This rate is slightly higher than the achieved requests per second during the test (457.7) which may highlight the infrastructure's capacity to handle a more significant load.