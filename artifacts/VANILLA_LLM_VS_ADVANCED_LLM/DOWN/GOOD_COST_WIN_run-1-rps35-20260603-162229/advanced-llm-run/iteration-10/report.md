The observed CPU utilization is significantly above the limit (130.4% vs 146m limit), indicating CPU under-provisioning.
The error rate is 0.0%, and p95 latency is very low (6.0ms) compared to SLO (500ms), suggesting the application can handle the target load without performance degradation.
Current deployment has 1 replica and 1 max replica in HPA, necessitating a horizontal scaling step to meet SLO under the current load.
Given the throughput ratio of 1.00 and the prefer_replica_step flag, the optimal action is to increase the number of replicas.
Implementing a horizontal scale-up while minimizing cost: Adding 1 replica aligns with cost-aware scaling strategy: replicas × requests.