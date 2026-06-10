Observed a failure in SLO due to cpu_utilization_exceeded, with cpu_util_request_pct at 175.6%.
Current deployment setup has 2 replicas, which is adequate but CPU and memory requests are low.
Latency (p95=473ms) is within the acceptable range against the SLO (500ms), but high CPU utilization indicates under-provisioning.
To optimize costs while ensuring performance, a coupled vertical scaling approach is appropriate: increase both CPU and memory resources.
Proposed a ~15% increase in CPU and memory requests to mitigate the utilization exceedance and fit within the current replication framework.
No change in the number of replicas or max replicas, as they are already set to 2 and are functioning correctly.
The strategy keeps operational costs in check while addressing the current resource utilization issues to push for SLO PASS.