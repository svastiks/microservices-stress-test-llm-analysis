- Stress test passed with low p95 latency and no errors.
- Current configuration had 2 replicas and achieved 35.0 RPS.
- Recommended to reduce resource allocation.
- CPU and memory requests and limits, as well as max HPA replicas, adjusted downwards.

- WARNING: hpa_yaml_new failed kubectl validation: The HorizontalPodAutoscaler "web-hpa" is invalid: 
* spec.maxReplicas: Invalid value: 0: must be greater than 0
* spec.maxReplicas: Invalid value: 0: must be greater than or equal to `minReplicas`; HPA change ignored.
