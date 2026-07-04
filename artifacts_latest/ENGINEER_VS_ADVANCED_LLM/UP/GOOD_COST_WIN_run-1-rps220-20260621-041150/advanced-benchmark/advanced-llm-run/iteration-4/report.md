Current configuration shows CPU utilization exceeding the safe limit (166.7% of requests).
SLO metrics are satisfactory with p95 latency at 251 ms, below the SLO target of 500 ms.
To address the CPU utilization issue and minimize the cost score, a coupled adjustment of CPU and memory requests is necessary.
Holding replicas at current levels will avoid unnecessary cost increases while balancing resource requirements.
The focus this iteration is on applying a ~15% increase to both CPU and memory resources from their current levels.