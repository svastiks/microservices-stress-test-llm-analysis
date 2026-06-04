Observed CPU utilization is 130.5%, indicating under-provisioning.
Memory utilization is at 225.3%, which surpasses the capacity.
p95 latency is 3145ms, significantly exceeding the SLO target of 500ms.
To mitigate the SLO violation, we will increase both CPU and memory requests, and add an additional replica.
The chosen new requests are informed by observed metrics and the throughput bottleneck.
Aim to minimize cost by keeping requests appropriate for observed utilization levels.