Current CPU utilization is 122.6%, indicating over-provisioning and CPU throttling.
Memory utilization is at 58.3%, suggesting there is some headroom, but less urgent than CPU.
Previous resource PASS streak was zero, and the last action was a replica reduction, so we aim to trim CPU/memory without changing replicas.
Given that CPU limits are exceeded, we need to reduce the CPU request/limit while ensuring SLO is still met.
With p95 latency at 106ms, there is a significant margin compared to the SLO of 500ms, allowing for a more aggressive reduction.
We recommend reducing CPU requests and limits to approximately 75m (from 100m) and keeping memory at 50Mi since it is not a bottleneck.