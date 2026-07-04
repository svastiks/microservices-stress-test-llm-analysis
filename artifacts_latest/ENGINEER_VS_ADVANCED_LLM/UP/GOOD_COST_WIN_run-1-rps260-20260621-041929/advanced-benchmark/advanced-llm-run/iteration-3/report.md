SLO failed due to latency: p95=864ms vs required p95 ≤ 500ms.
Current configuration results in high CPU utilization: cpu_util_request_pct=190.2%, indicating under-provisioning.
Utilization metrics indicate a significant CPU bottleneck despite reasonable memory utilization (41%).
Utilization is trustworthy, thus vertical scaling is appropriate after addressing capacity without increasing replicas.
Next step is coupled vertical scaling of CPU and memory requests to improve performance and meet SLO.