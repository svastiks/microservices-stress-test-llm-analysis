# Engineer baseline (Autopilot single-shot)

- **Source**: `/Users/svastik/Documents/Svastik/github/microservices-stress-test-llm-analysis/artifacts_latest/VANILLA_LLM_VS_ADVANCED_LLM/DOWN/GOOD_COST_WIN_run-1-rps45-20260610-132102/advanced-llm-run/iteration-1/experiment.json`
- **Target RPS**: 45
- **Profiling SLO PASS**: True

## Method

- CPU request = ceil(pod_cpu_peak_m × 1.3) → **189m**
- Mem request = ceil(pod_mem_peak_mib × 1.2) → **32 MiB**
- Replicas = ceil(fleet_cpu_peak_m / (cpu_request × 0.6)) → **4**
- Limits = 2.0× requests

## Signals (from profiling run)

- pod_cpu_peak_m: 144.8
- pod_mem_peak_mib: 16.86
- fleet_cpu_peak_m: 406.0
- profiling config: 5×150m/75Mi

## Derived provisioned cost

- **prov_cost**: 0.6929
- **util_cost** (profiling util, derived sizing): 0.1749
