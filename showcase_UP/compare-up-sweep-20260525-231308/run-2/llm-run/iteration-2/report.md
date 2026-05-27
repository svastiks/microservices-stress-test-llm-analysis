Current deployment is under-provisioned with a single replica causing high CPU and memory utilization.
Observed cpu_util_pct is 283.9% and mem_util_pct is 172.0%, indicating severe resource saturation.
Latency metrics indicate p95 at 4764ms, significantly above the SLO of 500ms, resulting in SLO failure due to high latency.
To recover, both CPU and memory requests should be increased to handle the workload efficiently, and a second replica should be added.
Cost optimization is crucial; we'll adjust CPU and memory while proportionately increasing replica count for balanced resource allocation.