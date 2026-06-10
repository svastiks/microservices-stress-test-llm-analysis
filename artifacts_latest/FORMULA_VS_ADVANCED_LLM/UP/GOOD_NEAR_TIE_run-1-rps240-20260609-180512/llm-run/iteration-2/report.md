SLO failed due to excessive CPU utilization (cpu_util_request_pct=189.5%).
Current deployment has 2 replicas with a high average CPU usage (cpu_util_pct=94.7%).
Both p95 latency (489ms) and error rate (0.0%) meet SLO requirements.
Next step involves increasing CPU and memory requests/limits coupledly since scaling up replicas is not an option.
Proposed resource increase: CPU from 50m to 58m, Memory from 25Mi to 29Mi (~15% increase).
This vertical scaling approach aims to reduce CPU utilization while maintaining existing replica count.