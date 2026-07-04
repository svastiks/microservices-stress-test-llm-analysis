Conducted an UP recovery iteration to address the cpu_utilization_exceeded failure.
SLO metrics indicate that p95 latency at 347ms is well within the threshold of 500ms and error rate is 0.0, meaning throughput meets SLO requirements.
However, the cpu_util_request_pct at 151.1% exceeds the 95% request limit, necessitating a coupled vertical scaling adjustment of both CPU and memory.
CPU and memory requests and limits were increased by approximately 15% to improve capacity without changing replica count.
Current configuration remains stable as no replica adjustment was needed and maximum HPA settings remain intact.
Implications of the vertical scale increase are expected to reduce the cpu_util_request_pct towards a more sustainable level, hence enhancing overall system efficiency.
This iteration yields a new cost score which will be evaluated in subsequent tests after applying the updated configuration.