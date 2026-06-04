Structured report for UP scaling under SLO violation:
- Current CPU utilization is at 76%, exceeding the 60% target.
- p95 latency recorded at 1490ms, significantly above the SLO of 500ms.
- Immediate action required to scale for SLO compliance.
- Memory utilization is at 47.8%, suggesting room for increased memory.
- Previous deployment used 70m CPU request and 35Mi memory request.
- Proposed changes will focus on both CPU and memory with an increase in replicas.
- A safe increase to 100m CPU and 50Mi memory with an additional replica aims to maintain a balance between performance and cost.