SLO status: FAIL due to cpu_utilization_exceeded with a cpu_util_request_pct of 137.0%.
p95 latency is at 236ms, well within the SLO of 500ms.
Current configuration has 2 replicas with both CPU and memory set below capacity requirements.
Observations indicate a balanced bottleneck with achieved RPS matching the target RPS.
Need to perform a coupled vertical scaling of CPU and memory requests by approximately 15%.
No resources should be dropped as SLO has not been met.
Holding replicas maintains consistency while addressing the CPU under-provisioning.