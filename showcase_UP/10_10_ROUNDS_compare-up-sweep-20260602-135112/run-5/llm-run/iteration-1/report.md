Currently experiencing a p95 latency of 1758ms, which exceeds the SLO of 500ms — indicating a latency violation.
Observed CPU utilization is 158.1%, indicating over-provisioning and potential CPU bottleneck if scaled further.
Memory utilization is at 143.7%, suggesting that not only CPU but also memory limits need to be increased to pass SLOs.
No errors logged (error rate = 0.0) but performance metrics indicate that SLO is being violated on latency.
Throughput ratio is 1.00, showing that the system is achieving the target RPS but at unacceptable latencies.
Scaling hint directs to grow capacity (both CPU/memory and containers) until SLO is met.
Because latency is primarily the issue, we will address memory and CPU requests to bring down p95 latency while aiming for more cost-effective resource usage.