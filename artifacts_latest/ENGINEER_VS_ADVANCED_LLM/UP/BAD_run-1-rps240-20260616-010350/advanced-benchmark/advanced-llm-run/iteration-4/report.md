SLO failed due to cpu_utilization_exceeded despite acceptable latency and throughput.
Current configuration holds with 2 replicas, but CPU request usage is significantly above the desired threshold.
Next step is a coupled vertical adjustment of CPU and memory, increasing both by approximately 15%.
This adjustment should help reduce the cpu_util_request_pct below the 95% threshold without changing the number of replicas.
Cost implications are considered — higher provisioning is justified against performance needs.