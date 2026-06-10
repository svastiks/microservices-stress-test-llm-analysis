The observed metrics indicate that the deployment is currently under-provisioned, leading to failure due to CPU utilization exceeding limits.
p95 latency is well within the SLO target, but the CPU utilization request percentage exceeds the defined threshold, indicating a need for CPU scaling.
With the current configuration of 2 replicas and CPU/memory limits of 230m and 120Mi respectively, cost optimization should focus on coupled scaling of resources.
Given the failure reason is specifically related to cpu_utilization_exceeded, scaling up resources (CPU and memory) is necessary without changing the number of replicas.
The proposed change includes increasing CPU and memory requests/limits by approximately 15% to lower request utilization while maintaining current replica counts.