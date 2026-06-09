Current configuration has exhibited cpu_util_request_pct of 159.2%, which exceeds the 95% gate.
SLO is being met on latency (p95 of 251ms vs 500ms) and error rate (0.0% vs 1.0%).
To address the cpu utilization issue, a coupled vertical step is necessary while holding replicas stable.
Raising both CPU and memory requests/limits by approximately 15% will improve the situation and help achieve lower cost while stabilizing costs.
The failure reason is due to cpu_utilization_exceeded despite meeting SLO on latency, thus purely vertical scaling is warranted.
No changes are required to the replica count at this time; hence, we are focusing on resource requests.

- Normalized deployment resources: requests.memory: 33.5Mi -> 34Mi
