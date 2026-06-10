Current workload demands require an increase in capacity to meet SLO.
Observed CPU utilization metrics indicate a bottleneck, with cpu_util_request_pct at 191.1%.
p95 latency measured at 2659ms exceeds the SLO of 500ms, indicating a clear violation.
Due to the thin baseline (1 pod and low provisioned resources), a replica-first approach is mandated.
Increasing the number of replicas will allow better load distribution without immediate resource allocation increases.
Next steps will include monitoring the impact of these changes on SLO adherence once a new replica is added.