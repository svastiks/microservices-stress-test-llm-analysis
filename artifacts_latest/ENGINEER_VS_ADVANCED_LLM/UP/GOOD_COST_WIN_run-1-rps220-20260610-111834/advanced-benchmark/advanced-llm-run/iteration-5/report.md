Current observed throughput is 220 RPS, achieving SLO goals for latency and error rate.
However, cpu_util_request_pct is 146.6%, indicating potential under-provisioning.
Latency is well within SLO limits (p95 = 247ms < 500ms), but the SERVER is nearing its capacity due to high CPU request percentage.
To address cpu_utilization_exceeded, an upward adjustment of CPU and memory requests is required without changing replicas.
No changes are needed to the HPA maxReplicas since we already have the sufficient amount of pods based on the current workload.
A coupled vertical increase of approximately 15% for both CPU and memory requests will be initiated this iteration.