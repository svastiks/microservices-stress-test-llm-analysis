Current workload is under-provisioned for the target RPS of 25, leading to a FAIL status due to cpu_utilization_exceeded.
Observed CPU utilization at 98.4% with a limit of 180m; this indicates that the current CPU configuration is insufficient.
Memory utilization is at 61.7% which is acceptable, suggesting that the memory request/limit can remain unchanged.
The HPA is configured with only 1 replica for the deployment which restricts scaling ability, limiting recovery options under load.
The last SLO status was PASS at lower CPU utilization, suggesting potential for a more efficient resource allocation if scaled appropriately.