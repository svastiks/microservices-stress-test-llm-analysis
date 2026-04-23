


- Better way to determine next iteration. exponentially
- few shots
- look at real microservice examples
- analyzer should work both upwards and downwards (over-provished vs under-provished)
- look at cpu, mem, p95 to decide how much the reduction needs to be for next iteration (might fail the service)
- upper bound vs lower bound
- ensure we get the memory and cpu utilization to determine bottleneck

if SLO_violated & !error_rate_violdated:
    still reduce
elif SLO_violated & error_rate_violdated:
    terminate
    lower bound  and upper bound by average
    look at utilization

