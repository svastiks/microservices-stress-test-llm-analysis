SLO is currently failing with p95 latency at 4731ms, significantly above the SLO target of 500ms.
CPU utilization is excessively high at 186.1% request-relative, indicating that the application is under-provisioned.
Current deployment has 1 replica, which is insufficient to handle the established workload of 260 RPS.
As per the guidelines, scaling up replicas is mandatory due to the thin provisioning and preference for a horizontal scaling approach.
Increasing replicas from 1 to 2 while keeping CPU and memory requests/limits identical ensures we can evaluate if the added pod resolves latency and SLO issues without incurring additional costs.
Cost score is currently at 0.0474; scaling up to 2 replicas will not impact the existing cost structure immediately.
This change will help balance the load more effectively and potentially bring latencies back under SLO thresholds. This is the first step toward recovery.