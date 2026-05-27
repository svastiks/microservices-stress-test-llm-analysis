The workload has exceeded CPU utilization limits, leading to a failure reason of 'cpu_utilization_exceeded'.
Observed CPU utilization was at 98.2%, indicating significant over-provisioning of CPU resources.
Observations show latency well below SLO with a p95 latency of 95ms, compared to an SLO target of 500ms.
Memory utilization is low at 48.8%, suggesting that memory requests and limits can also be reduced.
Prior stable state had resources at 50m CPU and 25Mi memory, indicating previous successful downsizes.
Current effective replicas (3) could be reduced through resource requests and limits adjustments without impacting performance.
Calculated cost score is 0.1786, representing potential savings through resource downsizing.
Next actions include cutting CPU and memory requests while keeping replica counts stable to ensure performance and cost efficiency.