Current setup has CPU utilization at 129.5% and memory utilization at 242.4%, indicating significant over-provisioning.
Observed p95 latency of 4994ms far exceeds the SLO of 500ms, resulting in SLO violation.
The target Requests Per Second (RPS) is 240, but only 199.1 RPS was achieved, leading to throughput collapse.
To resolve the bottleneck, we will increase replicas and also raise CPU/memory requests, focusing on optimizing cost.
With memory utilization above 100%, it's important to scale memory at least in tandem with CPU to prevent future issues.
The goal is to ensure that all SLOs are satisfied while minimizing the overall cost score.