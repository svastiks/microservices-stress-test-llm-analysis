During the stress-test experiment, the SLO was not met due to high CPU utilization exceeding 95% request-relative.
Currently observed CPU utilization request percentage was 98.7%, indicating a need to increase the CPU requests to ensure smooth operation under load.
Latency for the 95th percentile (314ms) was below the SLO target of 500ms, indicating acceptable performance if CPU capacity is increased.
Memory utilization remained below 20%, therefore no adjustments are needed for the memory requests/limits at this stage.
Cost score is 0.219; optimizing CPU down to ~124m can help lower costs while meeting performance criteria.
The proposal involves increasing only the CPU requests from 116m to approximately 124m while keeping memory constaints unchanged.
Holding the number of replicas ensures stability without unnecessary costs at this stage.