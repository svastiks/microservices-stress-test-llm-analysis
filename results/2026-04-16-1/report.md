# Analysis Report for `stress-service`

## Experiment Overview
- **Experiment ID**: medium-20260416T162608Z-a6f70d47  
- **Service**: stress-service  
- **Endpoint**: POST /login  
- **Workload Mode**: constant_arrival_rate  

## Performance Analysis
- **Failure Status**: Failed due to **error_rate_slo_violation**.
- **Error Rate Observed**: 1.0 (exceeds SLO of 0.01)
- **Latency (p95)**: 2.0 ms (well below SLO of 500 ms)

## Resource Utilization
- **CPU Request**: 30m (0% utilization)  
- **CPU Limit**: 400m  
- **Memory Request**: 52Mi (0% utilization)  
- **Memory Limit**: 240Mi

## Cost Evaluation
- **Cost Score**: 0.0808  
- **Provisioned Request CPU**: 30m  
- **Provisioned Request Memory**: 52Mi

## Recommendations
- Since the experiment has failed, **no further optimization** is recommended.

## Summary
- **Optimization Headroom**: NONE  
- **Over-Provisioned**: true  
- **Failure Archetype**: NONE  
- **Next Experiment**: Rerun the same workload after applying the leaner YAML (if changes were applicable).
