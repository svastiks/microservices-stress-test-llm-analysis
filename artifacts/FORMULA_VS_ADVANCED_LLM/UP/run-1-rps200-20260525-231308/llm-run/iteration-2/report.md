The last experiment recorded a failure (p95 latency of 1021ms) against an SLO of 500ms, indicating under-provisioning.
CPU utilization was significantly high at 210.3%, while memory utilization reached 128.7%, confirming the need for scaling.
To achieve an SLO PASS, both CPU and memory requests should be increased to alleviate the limitation in performance.
Given the requirement for memory to increase at least as much as CPU, both will be raised significantly, and a replica will be added to manage the capacity requirements.
Proposed changes aim to minimize the cost score while ensuring compliance with the desired latency and error rate thresholds.