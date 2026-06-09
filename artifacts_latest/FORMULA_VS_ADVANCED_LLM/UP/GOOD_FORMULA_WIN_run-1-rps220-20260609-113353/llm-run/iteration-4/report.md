SLO metrics indicate that throughput and latency meet requirements but CPU utilization is exceeding the request limit.
Current observed cpu_util_request_pct is 151.2%, well above the acceptable threshold, necessitating a vertical adjustment.
There was no need for additional replicas or HPA adjustments at this stage, as the workload requirements are already met in terms of requests per second.
Raising CPU and memory requests/limits by approximately 15% should help bring cpu_util_request_pct within acceptable bounds while retaining the current replicated state.
This adjustment is aimed at ensuring that all resources are efficiently utilized while adhering to SLO metrics.