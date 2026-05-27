Current p95 latency is 2565ms, significantly higher than the SLO of 500ms, indicating severe under-provisioning.
CPU utilization is at 106.5%, and memory utilization is at 166.7%, showing both CPU and memory are saturated.
Cost score is calculated as 0.1042, reflecting low resource requests but high latency.
Given the saturation evidence, an increase in both CPU and memory requests and limits is necessary to meet SLO.
Proposed new CPU requests: 100m (increase of ~42.86%). New CPU limit: 200m (targeting 2x requests).
Proposed new memory requests: 100Mi (increase of ~185.71%). New memory limit: 150Mi (targeting 1.5x requests).
Scaling up resources will hopefully lead to meeting the SLO without needing to add additional replicas immediately.
Next step will be to evaluate if this resource-only increase clears the SLO violation.