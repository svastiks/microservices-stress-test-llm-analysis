# Engineer baseline (Autopilot single-shot)

- **Source**: `/Users/svastik/Documents/Svastik/github/microservices-stress-test-llm-analysis/artifacts_latest/VANILLA_LLM_VS_ADVANCED_LLM/UP/GOOD_COST_WIN_run-1-rps260-20260610-121406/advanced-llm-run/iteration-1/experiment.json`
- **Target RPS**: 260
- **Profiling SLO PASS**: False

## Method

- CPU request = ceil(pod_cpu_peak_m × 1.3) → **128m**
- Mem request = ceil(pod_mem_peak_mib × 1.2) → **59 MiB**
- Replicas = ceil(fleet_cpu_peak_m / (cpu_request × 0.6)) → **1**
- Limits = 2.0× requests

## Signals (from profiling run)

- pod_cpu_peak_m: 98.2
- pod_mem_peak_mib: 48.55
- fleet_cpu_peak_m: 98.2
- profiling config: 1×50m/25Mi

## Derived provisioned cost

- **prov_cost**: 0.121
- **util_cost** (profiling util, derived sizing): 0.1084
