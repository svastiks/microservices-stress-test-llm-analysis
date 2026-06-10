Current deployment has 2 replicas, but cpu_util_request_pct is high at 131.9%, exceeding the maximum permissible of 95%.
SLO for p95 latency is met with a latency of 218ms against a target of 500ms, and there are no error rates observed.
The failure reason is 'cpu_utilization_exceeded', indicating that the requests for CPU are too low relative to the observed usage.
To recover from CPU under-provisioning, we will perform a coupled vertical scale-up of both CPU and memory requests/limits.
The proposed increase is approximately ~15% based on the current requests of 88m CPU and 44Mi memory.
The new configuration will improve efficiency while maintaining the existing number of replicas to avoid additional costs.
The cost_score is currently low but may further improve after appropriate scaling.