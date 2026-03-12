# **Failure Summary**: SLO violations occurred with p95 latency exceeding 30000ms (30 seconds), and error rate at 100%.

# **Scaling**: Scaled during test: yes (replicas_at_start 2 → replicas 10). However, this scaling did not alleviate the SLO violation.

# **Root Cause Analysis**: The dominant bottleneck is a clear violation of the p95 latency SLO with low CPU utilization (cpu_util_pct: 5.5%). Despite being at the maximum replicas of 10, the service could not handle the load efficiently. This may indicate the service is I/O bound, suggesting a need for improved application performance rather than just increased resources.

# **Evidence**: ["observed.latency_ms.p95: 30003ms", "observed.error_rate: 1.0", "observed.cpu_util_pct: 5.5%", "observed.mem_util_pct: 18.8%"]

# **Recommended Fix**: With the current configuration, the service seems to be considerably over-provisioned. The HPA settings and pod resource configurations should be re-evaluated. No deployment changes are needed at present, but scaling down could be beneficial based on future experiments.

# **Next Experiment**: Run a stress-test with an increased target of 100 requests per second (a 20% increase) to find lambda_crit and observe if there are changes to latency and error rate metrics.