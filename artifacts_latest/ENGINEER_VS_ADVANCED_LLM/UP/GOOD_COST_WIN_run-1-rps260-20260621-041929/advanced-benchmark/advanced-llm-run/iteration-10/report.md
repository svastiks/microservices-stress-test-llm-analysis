The workload aimed for 260 RPS was achieved at 259.3 RPS but failed to meet the SLO with a p95 latency of 516 ms against a target of 500 ms.
The observed CPU utilization percentage was high at 98.6%, indicating near saturation of CPU resources.
Memory utilization was low (14.6% average), suggesting that it could be increased alongside CPU to optimize cost.
As SLO has failed due to latency, scaling up is necessary until we achieve a p95 latency within limits.
Currently, we have two replicas, meeting the live pod requirements, and thus we will focus on coupled vertical scaling of both CPU and memory.
Given the coupled vertical scaling can adjust CPU and memory simultaneously, we will increase both the requests and limits to balance the load and cost.
The cost score is already fairly low at 0.2478, hence careful adjustment is key to ensure no drastic increase occurs.
Next iteration will involve a concurrent bump in CPU and memory to ensure that we pass the SLO without exceeding costs.