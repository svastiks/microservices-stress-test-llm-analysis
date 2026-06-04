- Test result: PASS
- p95 latency: 5.0 ms (SLO limit: 500 ms)
- Error rate: 0.0
- Achieved throughput: 35.0 RPS
- Current replicas: 2 
- Required scaling strategy: Down

- WARNING: hpa_yaml_new failed kubectl validation: The HorizontalPodAutoscaler "web-hpa" is invalid: 
* spec.maxReplicas: Invalid value: 0: must be greater than 0
* spec.maxReplicas: Invalid value: 0: must be greater than or equal to `minReplicas`; HPA change ignored.
