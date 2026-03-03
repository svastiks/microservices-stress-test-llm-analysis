# **Failure Summary**: SLO violations occurred with p95 latency exceeding the threshold at 1130ms.

# **Scaling**: Scaled during test: no (replicas stayed at 1) which likely contributed to the failure under load.

# **Root Cause Analysis**: The dominant bottleneck appears to be related to insufficient replicas to handle the load. Despite a high achieved requests per second (428.3), the observed latency at the p95 level (1130ms) indicates that the service could not handle the request rate effectively, resulting in SLO violations. The CPU and memory utilization are both at 0%, indicating the service was under-provisioned with respect to replica count.

# **Evidence**: 
- observed.latency_ms.p95: 1130ms  
- observed.achieved_requests_per_second: 428.3  
- observed.replicas: 1  
- observed.cpu_util_pct: 0%  
- observed.mem_util_pct: 0% 

# **Configuration Impact**: The current resource requests and limits (cpu_request_m: 50, cpu_limit_m: 250, mem_request_mib: 64, mem_limit_mib: 128) appear adequate; however, the lack of sufficient replicas led to performance issues under load.

# **Recommended Fix**: Scale UP by increasing the number of replicas to ensure that the service can adequately handle the load. Specifically, increase the minimum replicas from 1 to 3 and max replicas from 5 to 10.

# **Next Experiment**: Increase the target load to around 550 requests per second to find the critical load threshold (λcrit). This will validate if the adjustments made are effective in meeting SLOs under higher demand.