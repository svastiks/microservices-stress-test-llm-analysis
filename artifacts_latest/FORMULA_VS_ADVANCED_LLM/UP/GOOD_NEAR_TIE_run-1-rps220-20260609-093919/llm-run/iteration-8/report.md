SLO currently fails due to high cpu_util_request_pct (98.9%) at peak under the given load.
Latency is well within the SLO as p95 is at 226ms vs SLO of 500ms and no errors are present.
Utilization metrics are trustworthy, with CPU and memory demand comfortably below the limits.
To achieve SLO PASS while minimizing cost, a minimal coupled increase to both CPU and memory requests is necessary.
Current requests are 117m CPU and 60Mi memory; applying a 10% bump gives estimates around 129m CPU and 66Mi memory.
This optimization should keep the existing replicas and HPA maxReplicas unchanged, as further horizontal scaling is avoided due to adequate pod count.