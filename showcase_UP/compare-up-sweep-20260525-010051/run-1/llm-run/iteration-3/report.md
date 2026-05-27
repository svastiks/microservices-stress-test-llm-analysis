The workload faced a p95 latency of 815ms, exceeding the SLO requirement of 500ms.
Current resource utilization shows cpu_util_pct at 49.5% and mem_util_pct at 46.3%, indicating a capacity for growth.
The observed error rate is 0%, meeting the SLO criteria.
The observed deployment has 3 replicas, currently set to a maximum of 3 according to HPA configuration.
To increase capacity while minimizing cost, both CPU and memory requests will be elevated, alongside a potential increase in replicas.
This multi-axis UP adjustment aims to ensure that latency meets SLO thresholds while keeping cost score efficient.
Proposed changes will enhance cost-effectiveness without compromising performance metrics.
The prior metric readings indicate sustained utilization well below limits, confirming readiness for scaling adjustments.