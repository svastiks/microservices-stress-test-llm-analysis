Current configuration is under-provisioned with a single replica failing the SLO due to p95 latency and high CPU utilization.
Observed p95 latency is 3965ms, significantly above the SLO target of 500ms, indicating a need for increased capacity.
CPU utilization request percentage is at 189.7%, indicating extreme over-utilization at the current provisioning.
Since we are at a thin baseline (1 pod and current replicas = max replicas), we need to increase the number of replicas first.
This iteration will increase the number of replicas to 2 and adjust the HPA maxReplicas accordingly while keeping CPU and memory settings unchanged.
This approach minimizes cost while still addressing the immediate need for scale, following the preference for replica scaling at thin baselines.
Increasing replicas should help reduce latency and stabilize under the SLO targets.
Next steps will involve vertical scaling of CPU and memory after confirming the impact of the added replicas.