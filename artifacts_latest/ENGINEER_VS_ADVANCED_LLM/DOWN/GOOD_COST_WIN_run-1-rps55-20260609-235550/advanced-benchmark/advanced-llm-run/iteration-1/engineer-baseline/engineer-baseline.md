# Engineer baseline (Autopilot single-shot)

- **Source**: `/Users/svastik/Documents/Svastik/github/microservices-stress-test-llm-analysis/artifacts_latest/FORMULA_VS_ADVANCED_LLM/DOWN/GOOD_COST_WIN_run-1-rps55-20260609-235550/llm-run/iteration-1/experiment.json`
- **Target RPS**: 55
- **Profiling SLO PASS**: True

## Method

- CPU request = ceil(pod_cpu_peak_m × 1.3) → **191m**
- Mem request = ceil(pod_mem_peak_mib × 1.2) → **32 MiB**
- Replicas = ceil(fleet_cpu_peak_m / (cpu_request × 0.6)) → **4**
- Limits = 2.0× requests

## Signals (from profiling run)

- pod_cpu_peak_m: 146.5
- pod_mem_peak_mib: 20.29
- fleet_cpu_peak_m: 404.9
- profiling config: 5×150m/75Mi

## Derived provisioned cost

- **prov_cost**: 0.7001
- **util_cost** (profiling util, derived sizing): 0.1777
