Current setup has a favorable SLO PASS for latency and error rate but fails due to cpu_util_request_pct exceeding the limit (95.1%).
To resolve this, a CPU step of approximately 15% upward is required while keeping replicas unchanged to minimize cost.
Current CPU request is 135m; increasing it will bring the request within acceptable limits, enabling the system to pass the squeeze gate.
Both deployment and HPA configurations will remain unchanged since we're not adjusting replicas; only resource requests will be refined.
The proposed change is intended to reduce the likelihood of overprovisioning while ensuring performance metrics meet SLO.