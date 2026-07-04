SLO failed due to p95 latency exceeding the defined threshold (3454ms vs 500ms).
CPU utilization request percentage is extremely high (179.0%), indicating the need for additional capacity.
Current deployment and HPA are configured for a single replica, which limits recovery options.
Utilization telemetry is trustworthy, confirming that scaling up is necessary to achieve SLO passing.
Selected strategy: replica-first scaling due to thin baseline configuration and preference for horizontal scaling.