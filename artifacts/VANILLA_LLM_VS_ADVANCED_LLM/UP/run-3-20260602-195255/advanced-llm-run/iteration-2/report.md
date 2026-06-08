Current workload is validated as SLO PASS, but under-provisioned with observed metrics.
CPU utilization is at 55.5%, and memory utilization is at 38.3%, indicating headroom for scaling up.
Achieved RPS matches the target RPS of 260, with p95 latency of 462ms comfortably within the SLO threshold of 500ms.
To optimize costs while ensuring performance, I propose an increase in both CPU and memory requests to better match the observed utilization.
Scaling up both CPU and memory, while considering the ratio of previous configurations, will help us reach a more balanced state while also adhering to cost constraints.
Given the upper bound on replicas (2) has been reached, we’ll proceed with resource adjustments only.