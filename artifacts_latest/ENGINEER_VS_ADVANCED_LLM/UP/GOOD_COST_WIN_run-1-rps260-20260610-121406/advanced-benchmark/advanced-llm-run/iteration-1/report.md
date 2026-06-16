Current workload is set to handle 260 RPS but only achieved 254.4 RPS, resulting in latency issues and failure to meet SLO.
Detected SLO violation due to p95 latency of 4138ms exceeding the threshold of 500ms.
CPU utilization and request percentages are extremely high, indicating significant under-provisioning, with cpu_util_request_pct at 178.8%.
Current deployment is at the minimum replica count of 1, requiring scaling up to address performance issues.
A replica-first strategy is mandated due to the thin baseline configuration (current replicas = 1), hence the decision to increase replicas now.
Increasing the replica count to 2 will provide more processing capacity without raising resource requests, maintaining overall resource efficiency.