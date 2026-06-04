SLO was met with a 95th percentile latency of 5ms, well below the 500ms threshold.
Observed CPU utilization at 85.5% indicates the deployment is under-provisioned, despite having enough replicas.
Memory utilization at 47.6% suggests sufficient headroom on memory resources.
Cost score of 0.1666 indicates a favorable balance, but there's still room for optimization.
As previous axis was replica, CPU and memory will be reduced by approximately 10–15%.
Next step will focus solely on trimming CPU and memory while keeping replicas unchanged.