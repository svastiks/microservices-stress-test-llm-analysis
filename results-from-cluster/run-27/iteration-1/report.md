# Analysis of the stress-test experiment for robot-shop-web
- The service failed to meet the SLO with a p95 latency of 6883ms, significantly exceeding the 500ms threshold.
- The error rate was high at 0.6074, indicating severe stress on the system during the test.
- Currently, the deployment is running at the maximum number of replicas (3) as defined by the HPA with uncertain headroom for optimizing resources.
- Since SLO violations occurred while utilizing a trustworthy CPU load of 56.7%, we recommend a conservative scale up of CPU and memory limits.
- Next step: re-run the same fixed workload after applying the adjustments.
