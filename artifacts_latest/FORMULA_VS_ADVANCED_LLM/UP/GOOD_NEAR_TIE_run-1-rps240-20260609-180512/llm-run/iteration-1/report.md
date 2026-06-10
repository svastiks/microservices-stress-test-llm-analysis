SLO failed due to p95 latency violation (4730ms vs 500ms target).
Observations show high CPU utilization (cpu_util_request_pct=190.4%) indicating that the application is under-provisioned.
Current configuration has 1 replica with low resource requests and limits (50m CPU, 25Mi memory) which is insufficient for workload demands.
Requesting a replica-first step is crucial given the thin baseline and preference for horizontal scaling.
The deployment and HPA need to be updated to allow for scaling to 2 replicas to handle current load while preserving existing resource requests.