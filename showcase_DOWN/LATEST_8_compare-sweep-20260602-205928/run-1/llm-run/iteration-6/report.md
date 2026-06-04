SLO is passing with a p95 latency of 59ms, significantly below the 500ms threshold and an error rate of 0%.
Observing a CPU utilization of 94.5%, indicating the deployment is over-provisioned given the maximum request of 300m compared to current CPU limits.
Currently provisioned with 40m as requests and 100m as limits; proposals will focus on reducing these practical limits to reduce cost while maintaining SLO compliance.
Optimization signals reflect an opportunity to reduce resources further based on high CPU utilization and half of memory being utilized.
As the previous squeeze was resource-based and passed, this iteration allowed for both resource trimming and a replica reduction.
Changing replica count from 3 to 2 to accommodate for this over-provisioning and to further optimize costs.
The full deployment and HPA YAML will be updated to reflect these changes.