# Failure Summary
SLO violations occurred, specifically the p95 latency exceeded the threshold of 400 ms, with an observed p95 latency of 1869 ms and an error rate of 12.03% which is significantly above the acceptable limit of 5%.

# Scaling
Scaled during test: yes (1 → 3)

# Root Cause Analysis
The dominant bottleneck causing the failure is high latency due to inadequate scaling to meet the load requirements. The CPU utilization indicates that there is potential headroom (cpu_util_pct: 57.7% and cpu_util_to_limit: 0.58), but the number of replicas (3) was insufficient to handle the achieved request rate. 

# Evidence
- observed.latency_ms.p95: 1869ms 
- observed.error_rate: 0.1203
- observed.cpu_util_pct: 57.7%
- observed.replicas_at_start: 1
- observed.replicas_at_end: 3

# Configuration Impact
The HPA configuration allows scaling up to a maximum of 5 replicas, but the service did not scale sufficiently under load, resulting in SLO violations. Increasing the initial CPU and memory requests may improve performance by allowing for quicker adaptation to load increases.

# Recommended Fix
Update the deployment YAML to increase the initial resources:
- Increase cpu_request_m from 50 to 100 m
- Increase mem_request_mib from 64 to 128 MiB 

# Next Experiment
Increase the target requests per second to 600 RPS to validate if the changes improve stability and performance under higher load during the next test.