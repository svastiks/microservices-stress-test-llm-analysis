SLO violated due to p95 latency of 2982ms against the target of 500ms.
CPU utilization exceeded limits, with cpu_util_request_pct at 193.4%.
Only one replica present; with thin baseline configuration.
Next step is to add a second replica to improve load distribution.
Retaining the current CPU and memory requests and limits ensures no unnecessary cost increase at this stage.
Replicas will be increased first due to preference settings and thin baseline constraints.
HPA maxReplicas will be updated correspondingly to allow for autoscaling of the new replica.