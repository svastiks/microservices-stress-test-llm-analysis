The observed workload achieved the target RPS of 220 while maintaining a p95 latency of 232ms, well within the SLO of 500ms.
However, the cpu_util_request_pct peaked at 100.2%, exceeding the acceptable threshold of 95%, indicating that CPU requests need to be adjusted.
The memory utilization remained low at 17.8%, allowing for a CPU-only scaling adjustment.
To achieve optimal performance and ensure the SLO is passed, we propose increasing the CPU request to approximately 125m while maintaining the current memory request of 51Mi.
This adjustment aims to reduce the cpu_util_request_pct to around 93%, ensuring smoother operation without changing the number of replicas.
The current deployment has sufficient replicas and the HPA configuration remains appropriate for the workload.
Cost considerations indicate that this CPU adjustment should result in a lower overall cost_score due to more efficient utilization.
The last scaling action was a failure due to CPU utilization exceeding acceptable limits, hence following a precise CPU-only update is justified.