SLO failed due to p95 latency of 645ms, exceeding the threshold of 500ms, indicating under-provisioning.
Current CPU utilization request percentage is 112.5%, suggesting insufficient CPU resources to handle the load adequately.
Memory utilization is low at 18.9%, indicating no immediate memory limitations impacting performance.
The current deployment has 2 replicas with resource requests set at 112m CPU and 51Mi memory each.
To bring down p95 latency, increase CPU and memory requests as we cannot scale pods due to operational limits. This step keeps costs minimal while maximizing efficiency.
The actual load is aligned with the target RPS (260), but the latency breach indicates a need for vertical scaling.
CPU and memory resources should be raised together to maintain efficiency and avoid starving memory.
Proposed changes aim to not only meet the SLO but also reduce overall cost with minimal iterations on a stable metric horizon.