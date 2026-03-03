# **Failure Summary**
SLO violations occurred with respect to p95 latency, which exceeded the acceptable threshold of 400ms.

# **Scaling**
Scaled during test: no (replicas stayed at 1). Given the high load and observed issues, more replicas should be configured to handle workload.

# **Root Cause Analysis**
The failure indicates a latency issue under load, where the observed p95 latency was 971ms, significantly above the SLO threshold of 400ms. The CPU and memory utilization metrics show that the service was not being throttled as cpu_util_pct and mem_util_pct are at 0%. This suggests that the service could scale up to handle the observed load efficiently.

# **Evidence**
- observed.latency_ms.p95: 971ms 
- observed.achieved_requests_per_second: 428.8
- observed.cpu_util_pct: 0%
- observed.mem_util_pct: 0%

# **Configuration Impact**
The current configuration with a max of 5 replicas is valid; however, with only 1 replica, it could not handle the requests at the desired load. Increase replicas to match potential load capacity.

# **Recommended Fix**
- Increase the HPA max_replicas from 5 to at least 10 to allow for scaling up during high load efficiently.

# **Next Experiment**
Increase the target requests per second to 600 to evaluate how well the service performs as load increases.
