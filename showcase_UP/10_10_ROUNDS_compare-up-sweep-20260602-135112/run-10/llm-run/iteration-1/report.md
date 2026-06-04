SLO failed due to p95 latency of 3376ms exceeding target of 500ms, causing need for UP scaling.
Current deployment is over-utilized with 101.5% CPU usage and only 1 replica, limiting throughput.
Observed throughput ratio at 0.73 indicates significant throughput drop, indicating a need for an additional replica.
Increased requests for CPU and memory along with adding one replica to support the increased load.
CPU utilization suggests a need for at least 200m requests to push latency under SLO constraints.