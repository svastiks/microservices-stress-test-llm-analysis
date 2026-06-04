Current deployment shows an SLO violation with p95 latency at 1414ms, exceeding the threshold of 500ms.
CPU utilization is at 38.5% and memory utilization at 38.7%, indicating significant under-provisioning.
With observed metrics indicating low usage and a failed SLO, a scaling up is required to meet the desired performance levels.
Current CPU requests are at 92m; increasing CPU and memory while also scaling replicas is essential for recovery.
The cost score currently sits at 0.2619, indicating room for improvement in efficiency with a balanced increase in resources.
The HPA is unable to scale beyond the current replica count of 3, which may limit recovery options when under load.