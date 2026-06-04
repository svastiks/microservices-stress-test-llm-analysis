Current observed CPU utilization is at 146.9%, which significantly exceeds the acceptable threshold.
SLO conditions are being violated due to excessive CPU usage, even though the p95 latency is within acceptable limits.
Memory utilization is also high at 91.7%, which may lead to potential memory pressure and OOM scenarios.
The workload is currently configured for 2 replicas, but with the utilization metrics, a scale-up is necessary.
Targeting a balance between CPU and memory requests while increasing replicas will optimize cost.
Increasing both CPU and memory resources, along with raising the number of replicas to handle the current load efficiently.
This strategy will align with SLO requirements and minimize the overall cost score.