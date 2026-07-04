Current deployment fails the SLO due to cpu_utilization_exceeded.
Observed(cpu_util_request_pct): 182.1%, exceeds acceptable limit.
p95 latency (385ms) is below SLO threshold (500ms), indicating acceptable response times.
Both replicas and utilization verify as trustworthy; need for capacity increase is confirmed.
Target cost-effectiveness requires raising both CPU and memory together.
Proposing coupled vertical scaling to enhance performance without changing replicas.