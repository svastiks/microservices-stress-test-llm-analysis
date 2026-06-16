# Engineer baseline (Autopilot single-shot)

- **Source**: `/Users/svastik/Documents/Svastik/github/microservices-stress-test-llm-analysis/artifacts_latest/VANILLA_LLM_VS_ADVANCED_LLM/UP/GOOD_COST_WIN_run-1-rps220-20260610-111834/advanced-llm-run/iteration-1/experiment.json`
- **Target RPS**: 220
- **Profiling SLO PASS**: False

## Method

- CPU request = ceil(pod_cpu_peak_m × 1.3) → **129m**
- Mem request = ceil(pod_mem_peak_mib × 1.2) → **55 MiB**
- Replicas = ceil(fleet_cpu_peak_m / (cpu_request × 0.6)) → **1**
- Limits = 2.0× requests

## Signals (from profiling run)

- pod_cpu_peak_m: 98.6
- pod_mem_peak_mib: 45.05
- fleet_cpu_peak_m: 98.6
- profiling config: 1×50m/25Mi

## Derived provisioned cost

- **prov_cost**: 0.1215
- **util_cost** (profiling util, derived sizing): 0.1156
