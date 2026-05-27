Current deployment is under-provisioned for the load with CPU Utilization at 292.8% and Mem Utilization at 168.9%.
Achieved RPS is significantly below the target, with only 171 RPS achieved versus the 280 RPS target.
p95 latency is at 6604ms, which violates the SLO of 500ms.
The configuration limits on CPU and memory resources are insufficient to handle the workload requirements.
The HPA is currently set to a maximum of 1 replica, preventing scaling out under load.
To recover from SLO failure, we need to increase CPU, memory requests, and the number of replicas.
The new scaling proposal aims for a balanced increment of resources while maintaining cost efficiency.