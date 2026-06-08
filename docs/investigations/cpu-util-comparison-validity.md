# CPU utilization & comparison validity investigation

**Date:** 2026-06-02  
**Scope:** All `artifacts/FORMULA_VS_ADVANCED_LLM/` and `artifacts/VANILLA_LLM_VS_ADVANCED_LLM/` runs (UP + DOWN).  
**Trigger:** Manual review showed rows where one optimizer **PASS**es with fewer resources while the other **FAIL**s with more at the same RPS — often with inverted `cpu%` columns.

---

## Executive summary

**You are right that something is wrong — but not in the way the combined table implies.**

| Finding | Severity |
|---|---|
| `cpu_util_pct` is **limit-relative**, not request-relative. Optimizers set very different limit:request ratios, so the same load can read **33% on one side and 99% on the other**. | **Critical** — drives unfair `cpu_utilization_exceeded` FAILs |
| Combined iteration rows align by **iteration index**, not by **deployment config**. Row 10 on formula and row 10 on LLM are different experiments on different trajectories. | **High** — makes side-by-side PASS/FAIL look paradoxical |
| Prometheus window = k6 window **± 45s** (90s test → **~180s** query range); metric = **max** over window (spike-sensitive). | **Medium** — amplifies noise |
| Sequential compare arms (formula → LLM, advanced → vanilla) with baseline reset between arms. | **Low** — same RPS achieved on both sides in flagged cases |

**Headline `best_pass` prov-cost winners are not automatically invalid**, but frontier stopping and row-level readings are **contaminated** by the limit-based CPU gate. **Re-runs should wait until telemetry + gate fixes land.**

---

## What we audited

- **38** `comparison.md` files under `artifacts/` (18 formula vs advanced, 20 vanilla vs advanced; ENGINEER excluded)
- **466** `experiment.json` iteration files
- Code paths: `analysis/prometheus_collect.py`, `analysis/experiment_build.py`, `start.py` compare flow, `analysis/compare_squeeze_methods.py`

---

## How CPU utilization is sampled today

### k6 window

- Workload `duration_s`: **90 seconds** for current compare sweeps (`down_demo`, `up_demo`).
- Confirmed in experiment JSON: `observed_duration_s ≈ 90.1`.

### Prometheus query window

From `prometheus_collect.py`:

```python
_TIME_PAD_S = 45.0
q_start = start_ts - 45
q_end   = end_ts   + 45
```

For a 90s k6 run the Prometheus range is **~180 seconds** (45s before start + 90s test + 45s after end).

### Aggregation

1. Try aggregate `sum(rate(container_cpu_usage_seconds_total[...]))` over the range → take **`_max_value`** (peak spike).
2. Fallback: per-pod series → **`_sum_series_maxima`** (max per pod, then sum).
3. Replicas: **`max`** over `kube_deployment_status_replicas_available`, spec, and HPA current series.

### Utilization formula (stored as `cpu_util_pct`)

```
cpu_util_pct = 100 × cpu_usage_cores / (cpu_limit_m/1000 × max_replicas)
```

**Denominator is CPU limit × replicas, not CPU request.**  
HPA target (60%) is defined against **requests**. The squeeze PASS/FAIL gate reuses limit-relative `cpu_util_pct` with threshold **95%** (`SQUEEZE_CPU_UTIL_FAIL_PCT`).

### PASS/FAIL gate

`apply_squeeze_cpu_util_failure()` in `experiment_build.py` fails an otherwise-PASS iteration when:

- `mode == squeeze`
- `telemetry.utilization_trustworthy == true`
- `cpu_util_pct > 95`

All **31** `cpu_utilization_exceeded` failures in artifacts had **p95 within SLO** (latency was fine; CPU gate alone caused FAIL).

---

## Why limit-relative util breaks fairness

Average `cpu_limit / cpu_request` ratio by optimizer (artifact iterations):

| Optimizer | Mean limit:request | Range |
|---|---:|---|
| formula | **1.96×** | 1.56 – 2.00 |
| llm / advanced / vanilla | **2.60×** | 1.50 – **12.00** |

Tight limits (formula, vanilla) → **high `cpu_util_pct`** at moderate load.  
Loose limits (LLM arms) → **low `cpu_util_pct`** for the same or higher actual core usage.

### Worked example — formula vs LLM, DOWN rps35, iteration index 10

`GOOD_COST_WIN_run-2-rps35-20260602-205928`

| Arm | Status | cpu req | cpu lim | repl | cpu% (limit-based) | p95 | fail reason |
|---|---|---:|---:|---:|---:|---:|---|
| formula | **FAIL** | 55m | 109m | 2 | **98.6%** | 17ms | `cpu_utilization_exceeded` |
| llm | **PASS** | 20m | 151m | 1 | **32.8%** | 4ms | — |

Back-converting to **request-relative** utilization (same formula, request denominator):

| Arm | Implied request-relative CPU util |
|---|---:|
| formula | **~195%** |
| llm | **~248%** |

Under a request-based gate both would fail the 95% bar. The LLM arm **passes only because its limit is very loose** (151m on 20m request = 7.5×), not because it is cooler.

### Worked example — advanced vs vanilla, DOWN rps35, iteration index 9

`GOOD_COST_WIN_run-1-rps35-20260603-162229`

| Arm | Status | cpu req | cpu lim | repl (observed) | cpu% | fail reason |
|---|---|---:|---:|---:|---:|---|
| advanced-llm | **PASS** | 50m | **162m** | 2 | 73.5% | — |
| vanilla-llm | **FAIL** | 60m | **100m** | 2 | 103.3% | `cpu_utilization_exceeded` |

Same RPS (35), same replica count during test. Vanilla has **tighter limits** → crosses 95% limit-relative bar while advanced does not, despite similar or higher real load.

---

## The “combined iterations” table is not a same-config shootout

Compare jobs run **two independent squeeze trajectories** on the same cluster:

1. Reset baseline + settle (`SQUEEZE_SETTLE_SECONDS`, default 30s)
2. Run arm A to completion (formula / advanced-llm)
3. Reset baseline + settle again
4. Run arm B (llm / vanilla-llm)
5. Build `comparison.md` by **zip-aligning iteration indices** from each arm's `cost-effective-boundary.json`

Row *N* does **not** mean “both sides tested `{cpu, mem, repl}` config N”. Each optimizer walked its own path. A PASS/FAIL mismatch on row *N* is **expected** and is **not** proof that measurements are inconsistent for the **same** deployment.

What **is** valid at headline level:

- Each arm's **`best_pass` prov cost** (lowest-cost PASS on its own frontier)
- Iteration **counts** and **stopped_reason**

What is **misleading** for manual review:

- Row-by-row PASS vs FAIL at different resource points
- Row-by-row `cpu%` without normalizing limit:request ratio

### Automated scan results (artifacts)

| Metric | Count |
|---|---:|
| Comparison files | 38 |
| Paired iteration rows (both sides populated) | 194 |
| Rows with opposite PASS/FAIL at same index | **26** (68% of comparisons have ≥1) |
| Rows where PASS side has **lower cpu req AND lower cpu%** vs FAIL | **5** |
| Rows where PASS side has strictly ≤ cpu, ≤ mem, ≤ repl vs FAIL | **0** |

The **5 visually paradoxical rows** (all DOWN):

1. `FORMULA_VS_ADVANCED_LLM/DOWN/GOOD_COST_WIN_run-1-rps55-20260603-130930` iter 13  
2. `FORMULA_VS_ADVANCED_LLM/DOWN/GOOD_COST_WIN_run-2-rps35-20260602-205928` iter 10  
3. `VANILLA_LLM_VS_ADVANCED_LLM/DOWN/GOOD_BOTH_WIN_run-1-rps35-20260604-074743` iter 7  
4. `VANILLA_LLM_VS_ADVANCED_LLM/DOWN/GOOD_COST_WIN_run-1-rps35-20260603-162229` iter 9  
5. `VANILLA_LLM_VS_ADVANCED_LLM/DOWN/GOOD_COST_WIN_run-1-rps35-20260603-214147` iter 6  

All 5 FAIL sides used `cpu_utilization_exceeded` with p95 within SLO.

### FAIL reason breakdown (all artifact squeeze iterations)

| Optimizer | Total iters | PASS | p95 fail | cpu_util fail |
|---|---:|---:|---:|---:|
| formula | 158 | 108 | 41 | **9** |
| llm (+ advanced/vanilla) | 308 | 252 | 34 | **22** |

---

## Are the test runs “technically invalid”?

**Nuanced answer:**

| Question | Answer |
|---|---|
| Can one side PASS with less resources while the other FAILs with more **at the same iteration index**? | **Yes in the table — but they were never the same test.** |
| Is the **`best_pass` cost ranking** totally meaningless? | **Not totally** — each arm still found a frontier endpoint — but **cpu gate bias favors optimizers that set loose limits** (LLM arms). |
| Should we trust row-level cpu% for fairness review? | **No** until util is request-based and/or limit ratios are normalized. |
| Should we re-run sweeps? | **Yes**, after fixes below. Existing artifacts remain useful as **case studies** for the bug, not as final paper/deck numbers. |

---

## Recommended fixes (before 3×3 re-runs)

### P0 — Request-based CPU gate (squeeze PASS/FAIL) — **implemented 2026-06-02**

1. `prometheus_collect.py` emits **`cpu_util_request_pct`** and **`cpu_util_to_request`**.
2. `apply_squeeze_cpu_util_failure()` gates on **`cpu_util_request_pct`** by default (`SQUEEZE_CPU_UTIL_GATE=request`). Set `SQUEEZE_CPU_UTIL_GATE=limit` to restore old behavior.
3. `comparison.md` column renamed to **`cpu% req`** (falls back to limit-relative on pre-fix boundary JSON).
4. **`cpu_util_pct`** (limit-relative) retained in experiment JSON for diagnostics.

### P1 — Normalize limit policy across optimizers

- Enforce a fixed limit multiplier at apply time (e.g. `cpu_limit = 2 × cpu_request`) so limit-relative metrics are comparable even before P0 ships.
- Prevents LLM from “buying” PASS via 7× limit headroom.

### P2 — Tighten telemetry window

- Set `_TIME_PAD_S` to **0–15s** (or configurable `PROMETHEUS_TIME_PAD_S`).
- Optionally use **median or p95** over the k6 window instead of **max** for the gate (keep max as `cpu_util_peak_pct` diagnostic).

### P3 — Comparison table honesty

- Banner on `comparison.md`: *“Rows align by iteration index, not identical configs.”*
- Optional: add a **config-matched** section pairing iterations with nearest equal `{cpu_req, mem_req, repl}` (future).

### P4 — Document compare protocol

- Formula/advanced arm always runs **first**; record timestamps and cluster warmup in sweep logs.
- Consider interleaving single-iteration paired probes (larger refactor; not required for first re-run).

---

## Advanced DOWN early-stop bug — **fixed 2026-06-02**

**Symptom:** 9/11 advanced-llm DOWN compare runs stopped on `empty_recommended_diff` with **zero FAIL** iterations; vanilla always reached `first_fail`.

**Cause:** `_apply_down_boundary_stop()` in `results.py` cleared LLM YAML when hot at ≤2 pods (`guard.hot_boundary_stop`). Vanilla path never called this guard.

**Fix:**
1. When `SQUEEZE_UNTIL_VIOLATION=1`, hot-boundary no longer clears YAML — applies `guard.hot_boundary_continue_until_violation` + resource nudge instead.
2. `SQUEEZE_UNTIL_VIOLATION_PROBE_LLM` default **1** in `squeeze_llm_env.sh` — deterministic DOWN probe if diff is still empty.

---

## Re-run plan (after P0–P2)

User intent: **3 rounds each** for UP and DOWN on both tracks:

| Track | Script | Rounds × directions |
|---|---|---|
| Formula vs advanced LLM | `scripts/run_up_demo_compare_sweep.sh`, `scripts/run_down_demo_compare_sweep.sh` | 3 UP + 3 DOWN |
| Vanilla vs advanced LLM | `scripts/run_up_demo_advanced_vs_vanilla_sweep.sh`, `scripts/run_down_demo_advanced_vs_vanilla_sweep.sh` | 3 UP + 3 DOWN |

Post-run:

1. Rebuild artifacts / `comparison.md`
2. Re-run paradox scan (expect **0** limit-artifact rows after P0)
3. Re-apply `GOOD_*` / `BAD_*` labels on `best_pass` prov cost

---

## References (code)

| File | Role |
|---|---|
| `analysis/prometheus_collect.py` | `_TIME_PAD_S = 45`, max aggregation, limit-based `cpu_util_pct` |
| `analysis/experiment_build.py` | `apply_squeeze_cpu_util_failure()`, `squeeze_cpu_util_fail_pct()` |
| `start.py` | `_compare_squeeze_optimizers_main`, `_compare_advanced_vs_vanilla_llm_main`, baseline reset between arms |
| `analysis/compare_squeeze_methods.py` | Index-aligned combined table |

---

## Appendix: UP example (not resource paradox — p95)

`FORMULA_VS_ADVANCED_LLM/UP/GOOD_BOTH_WIN_run-4-rps220-20260602-135112` iter 2:

- formula **FAIL** 50m/25Mi/2 repl — p95 **709ms** (SLO 500ms), cpu 69.9%
- llm **PASS** 70m/35Mi/2 repl — p95 **269ms**, cpu 42.7%

Here the FAIL is **latency**, not CPU gate. LLM has **more** resources — not a paradox. This is the expected pattern when row indices align different configs.
