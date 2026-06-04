Current deployment has 1 replica and is experiencing high CPU utilization (98.4%) and high p95 latency (2805ms), leading to SLO failure.
The workload target requests per second (RPS) is 260, but only achieving 170.9 RPS, resulting in a throughput ratio of 0.66 which indicates under-provisioning.
The error rate is also well within limits (0.0016 vs 0.01 SLO), with sufficient memory utilization (30.1%) indicating CPU is the bottleneck.
To recover from this SLO failure, it’s necessary to increase both the CPU and the number of replicas, following the bottleneck signal.
Given the preference to increase replicas and the guidelines for scaling memory, we need to raise CPU requests appropriately to ensure efficient resource utilization while adhering to the SLO constraints.