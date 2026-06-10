The current deployment has a failure due to p95 latency (535ms) exceeding the SLO (500ms).
CPU utilization is high at 86.5%, and the cpu_util_request_pct is significantly exceeding 95% at 174.2%, indicating under-provisioning.
Memory usage remains low at 25.6%, suggesting that it's not the bottleneck for performance.
In response to the failed SLO, we are focusing on a vertical scaling approach to increase both CPU and memory resources until SLO requirements are met.
Given the need for a coupled vertical adjustment, we will increase both CPU and memory requests and limits together to optimize cost.
The optimization headroom is currently medium since CPU is the identified bottleneck, but memory is underutilized.