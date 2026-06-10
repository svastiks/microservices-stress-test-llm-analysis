Current configuration shows SLO PASS with p95 latency at 361 ms, below the SLO threshold of 500 ms.
However, cpu_util_request_pct at 136.1% exceeds the 95% threshold, indicating a need for increased CPU/memory requests.
Both CPU and memory utilization are low (cpu_util_pct at 73.7% and mem_util_pct at 17.5%).
We will raise both CPU and memory requests by approximately 15% to ensure we stay within the safe limits.
The goal is to adjust resources without changing the number of replicas, as we are not at a thin baseline.