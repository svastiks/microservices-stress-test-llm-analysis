SLO failed with p95 latency at 676ms, which exceeds the target of 500ms.
Observed CPU utilization exceeded the request limit (cpu_util_request_pct at 187.4%).
Memory utilization stayed within acceptable limits, but CPU remains the bottleneck.
Due to failure reason being p95_slo_violation, vertical scaling is required this iteration.
Current deployment already has max replicas (2), so only CPU and memory can be increased.
Proposed a coupled increase of 15% for both CPU and memory resources to improve performance.
Expected outcomes: Lower p95 latency and reduce cpu_util_request_pct toward the SLO target.