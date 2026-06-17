SLO failed due to CPU utilization exceeding request limits at 134.4%.
Current p95 latency is 257ms, well within the SLO target of 500ms.
Achieved RPS meets target RPS at 220 RPS with 0% error rate.
Utilization is trustworthy, indicating that adjustments can be made with confidence.
To meet the SLO while preventing further failures, a coupled vertical step for CPU and memory is necessary.
Proposed an update to increase CPU and memory requests and limits by approximately 15%.
This adjustment maintains the current replica count while addressing high CPU utilization.