SLO is currently passing with p95 latency at 393ms, well below the SLO threshold of 500ms.
The observed CPU utilization is at 53.6%, indicating that the existing resource allocations allow for some scaling down on CPU and memory before considering replica increases.
Current configuration has 3 replicas, which matches the HPA's maximum setting. An increase in replicas is not permissible if they are already maxed out.
To optimize cost, CPU and memory requests/limits should be scaled up to utilize available resources without breaching SLO thresholds.
Latency is not an issue and error rate is 0%, thus the focus is on balancing resource allocation to effectively manage the load at the target RPS.
The current CPU request limit is moderately set at 90m; however, scaling the CPU request cautiously alongside memory requests can help improve overall performance while keeping costs in check.
Given the observed metrics and the need to maintain performance, a mild increase in CPU and memory requests, with a focus on reliability and stability, is advisable.