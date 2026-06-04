Observed workload indicates under-provisioning, with CPU utilization at 139.5% and P95 latency at 1678ms exceeding the SLO of 500ms.
The current CPU requests and memory requests are significantly below the observed utilization, suggesting they need to be increased to meet workload demands.
Scaling strategy focuses on raising CPU and memory limits proportional to the observed memory utilization while starting with an increase in replicas to meet RPS targets.
Proposed resource allocations are aimed to keep costs low while achieving the performance needed to meet SLO thresholds.
Failure to meet SLO indicates an immediate need for scaling resources up by adjusting both CPU/memory requests and limits, and potentially increasing replicas.