# Scale Formula

## Core Update Rule

- DOWN (over-provisioned): `new = old * (1 - step_pct)`
- UP (under-provisioned): `new = old * (1 + step_pct)`

## DOWN Formula

```text
slack = max(0, (60 - max(cpu_util_pct, mem_util_pct)) / 60)
step_pct = bound(0.10 + 0.25 * slack, 0.10, 0.30)
```

## UP Formula

```text
err_pressure = max(0, error_rate / slo_err - 1)
lat_pressure = max(0, p95 / slo_p95 - 1)
throughput_pressure = max(0, target_rps / achieved_rps_target_window - 1)   # if target_rps > 0 else 0
severity = max(err_pressure, lat_pressure, throughput_pressure)
step_pct = bound(0.15 + 0.08 * min(severity, 3.0), 0.15, 0.40)
```

## Policy Gate for UP vs HOLD

```text
throughput_collapse = (target_rps > 0) and (achieved_rps_target_window < 0.85 * target_rps)

if slo_stress and (throughput_collapse or dropped_iterations > 0):
    scaling_hint = "UP"
```

## HPA Adjustment

```text
delta = max(1, ceil(maxReplicas * step_pct * 0.5))
```

- UP path increases `maxReplicas` by `delta`.
- DOWN path reduces `maxReplicas` conservatively while keeping bounds valid.

## Variable Glossary

- `old`: current resource value (CPU or memory request/limit) before applying next step.
- `new`: next resource value after applying `step_pct`.
- `step_pct`: percent change used for this iteration.
- `bound(x, lo, hi)`: keep `x` inside `[lo, hi]` (if below `lo`, use `lo`; if above `hi`, use `hi`).
- `cpu_util_pct`: observed CPU utilization percent.
- `mem_util_pct`: observed memory utilization percent.
- `slack`: unused headroom below the 60% utilization target.
- `error_rate`: observed failed-request ratio.
- `slo_err`: allowed error-rate threshold from SLO.
- `p95`: observed p95 latency in ms.
- `slo_p95`: allowed p95 latency threshold from SLO.
- `target_rps`: configured target requests/second for the run.
- `achieved_rps_target_window`: achieved requests/second measured against the configured target window.
- `err_pressure`: how far error rate exceeds SLO.
- `lat_pressure`: how far p95 exceeds SLO.
- `throughput_pressure`: how far achieved throughput is below target.
- `severity`: worst pressure signal among error, latency, throughput.
- `slo_stress`: true when run failed and/or SLO is violated.
- `throughput_collapse`: true when achieved throughput drops below 85% of target.
- `dropped_iterations`: k6 dropped iterations count (backpressure/overload signal).
- `scaling_hint`: deterministic direction decision (`UP`, `DOWN`, `HOLD`, `UNKNOWN`).
- `maxReplicas`: HPA upper bound before adjustment.
- `delta`: bounded HPA step derived from `step_pct`.
