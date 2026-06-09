Current deployment has insufficient capacity with only 1 replica and high observed CPU utilization.
SLO is currently failing due to p95 latency exceeding the limit (3547ms > 500ms).
CPU_util_request_pct is excessively high (184.5%) indicating that the workload cannot be handled effectively with the existing resources.
The observed workload reached 219.7 RPS against a target of 220 RPS, meaning the request handling capacity is very close to the limit.
To address the under-provisioning, the first step will involve increasing the number of replicas as part of a replica-first strategy.
This action aims to enhance reliability and allow for better distribution of the current workload.
After scaling up replicas, subsequent iterations will consider vertical increases in CPU and memory.
The latest cost_score stands at 0.0474, which should be monitored as capacity is adjusted to ensure efficient resource utilization.
Higher demand on resources indicates potential future cost implications if not managed properly.