Current configuration has p95 latency of 251ms, which meets SLO of 500ms.
Achieved requests per second match the target at 220 RPS.
However, observed cpu_util_request_pct is 115.2%, indicating CPU resources are exceeded.
Memory utilization is low at 17.6% and can hold for now during scaling.
Scaling CPU and memory requests coupled upward by ~15% to alleviate the CPU utilization issue.
Keeping the number of replicas constant at 2 as the current SLO for p95 is met.
This adjustment aims to bring cpu_util_request_pct under the required 95% threshold without increasing costs significantly.
Post adjustment, the cost_score is expected to remain minimal as only resource requests are being calibrated.