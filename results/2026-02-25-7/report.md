# Stress Test Analysis Report for stress-service

## Failure Summary
SLO violations occurred: The observed error rate was 1.0, which exceeds the error rate SLO of 0.05.

## Root Cause Analysis
The dominant bottleneck in this test appears to be related to **Dependency Saturation**. Although CPU and memory limits were not maximized, the very high error rate indicates issues in either the application logic or possible complications with downstream dependencies. There were no indications of CPU throttling or memory pressure directly from the given metrics, with low latency values contradicting a heavy load. The configuration set an HPA that did not react effectively, contributing to the failure.

## Evidence
- observed.total_requests: 2969
- observed.achieved_requests_per_second: 98.6
- observed.error_rate: 1.0
- observed.latency_ms.p95: 30.0

## Configuration Impact
The HPA's min replicas (2) and target CPU utilization (70%) may not have been sufficient to scale out effectively under the given load. The overall setup did not allow for dynamically adjusting the number of replicas based on the observed metrics at the time of the request load, resulting in dependency saturation.

## Recommended Fix
We propose updating the HPA settings to allow for more aggressive scaling under high loads. This includes adjusting the target utilization and ensuring the max replicas are fully utilized during peak load periods.

### YAML Changes:
--- deployment.yaml
+++ deployment.yaml
@@ -5,7 +5,7 @@
     min_replicas: 2
-    max_replicas: 10
-    target_cpu_util_pct: 70
+    max_replicas: 15
+    target_cpu_util_pct: 50
 
## Next Experiment
Conduct a follow-up experiment with the modified HPA settings, maintaining an HPA with a target CPU utilization of 50% and a maximum of 15 replicas. Rerun the test with the same workload aiming for 100 requests per second to validate if the system can handle the load without violating the error rate SLO.
