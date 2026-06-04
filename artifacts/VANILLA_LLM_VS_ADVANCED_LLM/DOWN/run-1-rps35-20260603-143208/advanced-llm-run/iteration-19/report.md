Current deployment is under-provisioned with a high CPU utilization at 96.4% and failed SLO due to exceeding CPU limits.
Achieved RPS matches the target, indicating the application can handle the load if provisioned correctly.
Latency is well below the SLO limit (p95 of 19ms vs 500ms).
With the prefer_replica_step set to true, the first step is to increase replicas as it is the best way to scale horizontally.
Increasing replicas will help distribute the load and reduce the per-pod CPU utilization, moving towards fulfilling the SLO requirements.