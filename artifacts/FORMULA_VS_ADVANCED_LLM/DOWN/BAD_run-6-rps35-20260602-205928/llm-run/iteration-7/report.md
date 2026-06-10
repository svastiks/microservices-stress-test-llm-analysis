Current deployment with 3 replicas shows CPU utilization at 81.8% and memory utilization at 48.6%.
The SLO was met (p95 latency = 111ms, target = 500ms) and the error rate was 0%.
Proposed adjustments target a lower resource footprint while keeping the existing replicas constant due to resource pass streak of 0.
CPU requests will be reduced from 50m to 40m, and memory requests from 25Mi to 20Mi, considering current utilization levels.
No change to the replica count is proposed, as we cannot lower replicas two PASS iterations in a row.
The goal is to remain safe while minimizing cost, hence staying within the observed utilization margins.
The HPA maxReplicas will be updated to align with the actual deployment changes.