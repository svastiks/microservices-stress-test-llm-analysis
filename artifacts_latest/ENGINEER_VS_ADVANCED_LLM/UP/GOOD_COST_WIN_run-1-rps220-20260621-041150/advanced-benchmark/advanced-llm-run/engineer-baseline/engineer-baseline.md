# Engineer baseline (Autopilot single-shot)

- **Source**: `/Users/svastik/Documents/Svastik/github/microservices-stress-test-llm-analysis/results-from-cluster/engineer-up-fat-profile-20260621-000709/run-1/experiment.json`
- **Target RPS**: 220
- **Profiling SLO PASS**: True

## Method

- CPU request = ceil(pod_cpu_peak_m × 1.3) → **165m**
- Mem request = ceil(pod_mem_peak_mib × 1.2) → **32 MiB**
- Replicas = ceil(fleet_cpu_peak_m / (cpu_request × 0.6)) → **1**
- Limits = 2.0× requests

## Signals (from profiling run)

- pod_cpu_peak_m: 126.6
- pod_mem_peak_mib: 15.64
- fleet_cpu_peak_m: 502.2
- profiling config: 5×150m/75Mi

## Derived provisioned cost

- **prov_cost**: 0.7581
- **util_cost** (profiling util, derived sizing): 0.1946
