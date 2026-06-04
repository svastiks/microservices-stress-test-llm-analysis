Current setup is under-provisioned due to high observed CPU (262.2%) and memory utilization (128.4%).
p95 latency of 1774ms significantly exceeds the SLO of 500ms, causing SLO violation.
The cost score is relatively low (0.0474) but needs to be assessed against necessary resource increases.
To recover, we will increase CPU and memory in addition to scaling replicas.
Considering the bottleneck is memory, we will increase the memory requests and limits along with CPU.
Increasing replicas is preferable to improve throughput when p95 latency is high.
Optimal approach: grow capacity by raising memory and CPU, and also increase replicas.
Telemetry is trustworthy, providing a reliable foundation for our adjustments.