The observed workload achieved 220 RPS with a p95 latency of 261ms, well within the SLO of 500ms.
The CPU utilization request percentage is at 179.9%, exceeding the 95% threshold, indicating that the capacity is insufficient for handling peak loads.
Memory utilization is within acceptable limits at 44.5%, showing room for improvement in CPU resources without affecting memory allocation.
Current deployment has 2 replicas with maxReplicas also set to 2, restricting horizontal scalability until current CPU request limits are addressed.
SLO failed due to high CPU utilization relative to requests, necessitating a CPU/memory increase while keeping replica count stable.
As the experiment focuses on minimizing costs, a ~15% increase in CPU requests/limits while maintaining existing replica levels is the next logical step.
HPA configuration remains adequate but needs adjusting for scaling once CPU limits are increased.