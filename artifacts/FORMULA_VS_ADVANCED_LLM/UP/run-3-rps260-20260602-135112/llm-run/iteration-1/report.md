Current deployment resources are under-provisioned, causing SLO violation with a p95 latency of 2008ms, exceeding the target of 500ms.
CPU utilization is at 198.4%, and memory utilization at 208.9%, indicating severe over-utilization.
The achieved requests per second are at the target of 260, but memory limitation has resulted in latency violations.
To address the memory bottleneck, it is necessary to increase both CPU and memory resources while also scaling replicas.
Given the prefer_replica_step is true, we'll first increase the replica count before increasing resource requests/limits.
This scaling will help reach SLO compliance while minimizing costs as we increase resources. The cost_score is currently at 0.0474.
The deployment and HPA must be modified to both allow for an additional replica and increase memory allocation given the observed pressures.