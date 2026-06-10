Current utilization metrics indicate CPU request utilization exceeds the SLO threshold.
CPU utilization request percentage is at 140.1%, necessitating a CPU and memory increase to resolve the saturation.
Both achieved RPS (239.4) and p95 latency (316ms) are within SLO limits, but the failure was triggered by high CPU utilization.
A coupled increase in CPU and memory requests will sustain performance while addressing the CPU utilization issue.
HPA max replicas remain unchanged as we are not scaling horizontally at this iteration.