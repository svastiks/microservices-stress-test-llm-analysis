Observed latency p95 is 453 ms, which is below the SLO of 500 ms.
CPU utilization requests are at 179.5%, exceeding the 95% threshold, indicating under-provisioning.
Memory utilization is at 41.8%, allowing for additional memory without immediate concern.
Cost score is currently low at 0.1101, but needs optimization as workload is under-provisioned.
Holding replicas at 2 for this iteration since the deployment replicas are already at the live maximum.
Action this iteration is a coupled increase of CPU and memory requests and limits by ~15% to alleviate CPU pressure.
Next iteration will assess if this has brought CPU utilization percentage below 95%.