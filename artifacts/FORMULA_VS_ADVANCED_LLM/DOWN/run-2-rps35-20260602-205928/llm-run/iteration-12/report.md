To recover from the CPU bottleneck, we will increase CPU and memory requests while also scaling up replicas since current metrics indicate high utilization and failed SLO. The current settings show CPU utilization at 122.1%, indicating under-provisioning. Here is the proposed scaling:
- Increase CPU requests from 15m to 40m based on observed utilization and application needs.
- Increase memory requests from 15Mi to 60Mi, as memory utilization is also above the safe threshold.
- Increment replicas from 1 to 2 to enhance throughput and mitigate potential bottlenecks.
After applying these changes, we expect to maintain a low cost_score while passing the SLO thresholds.