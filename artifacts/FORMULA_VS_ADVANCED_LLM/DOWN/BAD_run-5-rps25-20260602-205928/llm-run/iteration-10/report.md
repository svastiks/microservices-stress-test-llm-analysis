Achieved RPS matches target RPS of 25.0 with no dropped iterations.
p95 latency is 36ms, well below the SLO threshold of 500ms.
CPU utilization at 97.7% exceeds the safe threshold of 95%, indicating a bottleneck.
Memory utilization is at 38.3%, providing headroom to adjust without issues.
Scaling recommendation is to increase CPU and memory requests alongside adding a replica to improve overall capacity while reducing CPU overload.