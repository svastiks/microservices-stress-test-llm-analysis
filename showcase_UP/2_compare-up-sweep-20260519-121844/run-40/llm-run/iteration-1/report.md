Current deployment has 1 replica with low CPU/memory requests causing SLO violation.
Observed p95 latency is 5526ms, significantly exceeding the SLO target of 500ms.
CPU utilization is at 189.3%, indicating excessive load and under-provisioning.
Memory utilization is at 284.9%, suggesting the need for increased memory requests as well.
The cost score is 0.0744, which may increase with resource scaling to meet SLO requirements.
First step will increase CPU and memory requests/limits as no horizontal scale is allowed at this point.
Subsequent scaling may involve adding a replica only if SLO still fails after resource increase.