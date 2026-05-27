# Research Pivot Roadmap: Failure Diagnosis → Efficiency Mapping (Cost Optimization)

This document summarizes the **current repository architecture** (failure-oriented loop), a **gap analysis** against the **Iterative Squeeze** research objective (fixed load → minimize provisioned resources until SLO break → optimal frontier), and **concrete change targets** by component. **No code changes** are implied by this file alone.

---

## 1. Current Architecture Summary (Failure Detection)

### 1.1 End-to-end flow

1. **Operator** runs `start.py` with `--profile` (low/medium/high from `experiments.json`), optional `--script` (login/signup), and optional trailing argument `verify`.
2. **Port forwards** (hardcoded): Prometheus in `monitoring` namespace (`svc/kps-kube-prometheus-stack-prometheus:9090`), and the system under test (SUT) `svc/stress-service` in **default** namespace (`8000:80`).
3. **k6** runs **locally** via `subprocess`, writing `results/k6-summary.json` (moved into a dated run directory by `analysis/results.py` as `k6-run-summary.json`). Exit codes **0** or **99** (thresholds crossed) are accepted.
4. **`analysis/results.py:main()`** orchestrates the LLM pass:
   - `experiment_build.build_experiment_payload()` merges k6 summary, YAML-derived **single-container** `config` (CPU/mem requests/limits, HPA min/max/target CPU), optional `run_meta.json` (workload, SLO, profile, `k6_thresholds_crossed`), and **Prometheus** `observed_override` from `prometheus_collect.get_prometheus_observed()` when `start_ts`/`end_ts` exist in meta.
   - Writes `experiment.json`, calls `api.analyze_with_llm()` with `prompts.SYSTEM_PROMPT` + `build_user_prompt()`, post-processes via `_postprocess_llm_result()`, then `write_outputs()` → `report.md`, `analysis.json`, `recommended.diff`, and **overwrites** `apps/service/k8s/deployment.yaml` and `apps/service/k8s/hpa.yaml` when the model returns full YAML strings.

### 1.2 Where the “loop” is defined today

There is **no** general closed-loop controller in code. The only automation beyond “one k6 + one analysis” is the **`verify` branch inside `start.py`** (lines ~121–182):

- Run **1**: k6 → `analysis_main()` → artifacts in `results/<date>-<n>/`.
- If `verify` and no prior `verification/llm-result-verification.md`: read `recommended.diff` (already applied to repo YAMLs by `write_outputs` during run 1—note: `apply_recommended_diff` re-`kubectl apply`s current YAMLs), `kubectl apply` + rollout wait via `apply_diff.py`, then **second** k6 with same profile/script from `experiment_config.json`, second `analysis_main()`, then `verify.run_verification` + `write_verification_output` (LLM compares run 1 vs run 2).

So the loop is **exactly two runs** plus a **diagnostic verification** LLM call—not an arbitrary iteration until a stopping condition.

### 1.3 FastAPI service (`apps/service/`)

- **`apps/service/app/main.py`**: FastAPI app with `/login`, `/signup`, `/health`, optional CPU burn (`CPU_WORK_MS`), memory allocation (`MEMORY_MB`), optional downstream HTTP client, Prometheus metrics middleware.
- **Kubernetes**: `apps/service/k8s/deployment.yaml` (Deployment + ClusterIP Service), `apps/service/k8s/hpa.yaml` (HPA on `stress-service`), optional `mock-dependency.yaml`, `monitoring/servicemonitor.yaml` for scraping.
- **`apply_diff.py`**: `kubectl apply` of deployment + HPA, `kubectl rollout status deployment/stress-service` in **default** namespace.

### 1.4 Failure / success semantics today

- **`experiment_build.from_k6_summary()`**: Sets `failure.failed` from **experiment SLO** only (`p95` vs `slo.p95_latency_ms`, `error_rate` vs `slo.error_rate`). Separately, `k6_thresholds_crossed` in meta can force `failure.reason == "k6_thresholds_crossed"` (stricter k6 thresholds in `benchmarks/load-tests/k6/*.js`).
- **LLM role (`prompts.py`)**: Primary output framing is **`failure_archetype`** (NONE, CPU_THROTTLING, MEMORY_PRESSURE_OOM, AUTOSCALER_LAG, DEPENDENCY_SATURATION, UNKNOWN), **`lambda_crit_estimate`**, and remediation YAML. Scale-down when passing is already mentioned, but the **objective function** is not “minimize cost at fixed RPS”; it is “diagnose failure / find lambda_crit / suggest next experiment.”

---

## 2. Gap Analysis

### 2.1 Already in place (high reuse value)

| Capability | Location | Reuse for efficiency mapping |
|------------|----------|------------------------------|
| k6 constant-arrival-rate profiles | `experiments.json`, `start.py` + `benchmarks/load-tests/k6/*.js` | **Fixed traffic** is natural: pin `target_requests_per_second` for the whole squeeze campaign. |
| SLO extraction from k6 | `experiment_build.from_k6_summary()` | Becomes **`slo_status` PASS/FAIL** gate for the squeeze loop (may need to align k6 thresholds with experiment SLO or decouple). |
| Prometheus window queries | `prometheus_collect.get_prometheus_observed()` | **Headroom signals** (CPU/mem % vs limits, replica count, OOM) for “slack” and over-provisioning narrative. |
| YAML round-trip + apply | `results.write_outputs()`, `apply_diff.kubectl_apply` | Same machinery for **iterative** resource reductions (with safer “dry-run” or branch-per-iteration policy later). |
| Two-run comparison LLM | `verify.py` + `VERIFICATION_SYSTEM_PROMPT` | Pattern reuse for **“did last squeeze step violate SLO?”** or for auditing frontier steps—not identical to verify’s “did the fix work?”. |
| Config snapshot in `experiment.json` | `experiment_build.get_config_from_yaml()` | Needed for **cost function** inputs (replicas from HPA + per-pod CPU/mem from Deployment). |

Roughly **~80%** of plumbing (k6 → metrics → JSON payload → LLM → YAML) transfers; the **missing 20%** is **goal inversion** (optimize cost under SLO), **loop condition** (repeat while PASS), **multi-service / Robot Shop** targeting, and **explicit cost scoring** in artifacts.

### 2.2 Missing or misaligned for the new theory

| Gap | Why it matters |
|-----|----------------|
| **No iterative squeeze loop** | Pivot requires: safe high config → load → if SLO PASS → reduce resources → repeat until FAIL → report last PASS as **optimal frontier**. Today: at most one optional second run for verification. |
| **No `slo_status` / frontier artifact** | Need a first-class enum or boolean per iteration, cumulative log (config, cost, SLO), and “last good configuration” pointer. |
| **LLM schema is failure-archetype-centric** | `failure_archetype`, `lambda_crit_estimate`, `next_experiment` bias exploration of **breakage** and **higher load**, not **minimize N × f(cpu,mem)** at **fixed** RPS. |
| **No cost function in `experiment_build.py`** | Research asks for \( \text{cost} \propto N \times g(\text{CPU}, \text{Memory}) \) (or normalized variant). Today only raw `config` fields exist; no derived `cost_score` / `provisioned_cpu_m` / `provisioned_mem_mib` totals. |
| **Single Deployment + single HPA assumptions** | `get_config_from_yaml` reads **first** Deployment doc and **first** container; Prometheus queries assume **one** deployment name and pod regex `{deployment}.+`. Robot Shop is **many** Deployments/Services/stateful pieces. |
| **Robot Shop not in repo** | No Helm values, no k6 scripts pointed at front-end/gateway, no dependency graph. Swap is greenfield integration. |
| **Hardcoded SUT identity** | `stress-service`, `default` ns, port-forward to `8000`, HPA name pattern in Prometheus fallback (`{deployment}-hpa`). All must become **configurable** (namespace, labels, primary scrape target, k6 `BASE_URL`). |
| **`write_outputs` mutates repo YAML immediately** | For research traceability, iterative squeeze may want **per-iteration YAML snapshots** in the run directory without overwriting until committed, or git-tag each frontier step. |
| **Verification mode semantics** | `verify` is “did recommendation fix run 1?” not “are we still under SLO while shrinking resources?” Different prompts and stopping rules. |

---

## 3. Component-by-Component Changes

### 3.1 `start.py`

- **Replace** the binary `verify` path with a **`squeeze`** (or `--mode squeeze`) loop:
  - Outer condition: **while experiment SLO PASS** (derive from `experiment.json` or return value from `experiment_build` / a small helper), optionally capped by `max_iterations`.
  - Inner steps: optional rollout settle → k6 (same fixed profile/RPS) → `analysis_main()` (or a slimmer “squeeze analysis” entrypoint) → parse LLM output for **resource reduction** diff → `kubectl apply` + wait → record iteration index and cost metrics.
  - On first SLO **FAIL**: stop, label previous iteration’s applied config as **Optimal Frontier**, write summary artifact (markdown or JSON under `results/.../squeeze/`).
- **Parameterize** port-forward targets: namespace, service name, local port (Robot Shop front door vs current `stress-service`).
- **Optional**: capture `replicas_at_start` before each k6 (file already supported in `experiment_build` for `scaled_during_test`).

### 3.2 `analysis/prompts.py`

- **New system prompt** (or parallel `SYSTEM_PROMPT_EFFICIENCY`) with JSON schema fields such as:
  - `optimization_headroom`: enum or structured tags (e.g. `CPU_SLACK`, `MEM_SLACK`, `REPLICA_SLACK`, `HPA_HEADROOM`, `NONE_MATERIAL`).
  - `over_provisioned`: boolean + short rationale tied to `observed.*` vs `config.*`.
  - `recommended_reduction`: concrete **downward** changes (replicas, requests/limits, HPA min/max/target) **bounded** (e.g. max 20–30% step) to avoid overshoot in one LLM hop.
  - Deprecate or demote **`failure_archetype`** when `failure.failed == false`; when `failure.failed == true`, pivot message to **“frontier found—document violation type”** rather than extended lambda_crit chase at variable load.
- **`lambda_crit` / `next_experiment`**: For fixed-RPS squeeze, either **remove** or replace with `squeeze_next_action` / `confidence` so the model does not keep suggesting higher RPS (conflicts with fixed-load theory).
- **`VERIFICATION_SYSTEM_PROMPT`**: Either retire for squeeze, or repurpose for **cross-check** between human-defined frontier and LLM-suggested reductions.

### 3.3 `analysis/results.py`

- Pass **mode** or **research_goal** into prompt builder so one codebase can support both paradigms during transition.
- Extend **`analysis.json`** artifact to include `slo_status`, `cost_score` (once computed in `experiment_build`), and `iteration_id` when running under squeeze.
- **`_postprocess_llm_result`**: Rules today enforce AUTOSCALER_LAG constraints and strip YAML on UNKNOWN—**new** post-process rules may enforce “no scale-up when SLO PASS and headroom high,” or validate monotonic cost decrease.
- **YAML write policy**: Consider writing LLM YAML to run dir first, then optional apply (config flag), to preserve audit trail per squeeze step.

### 3.4 `analysis/experiment_build.py`

- Add **`compute_cost_metrics(config: dict) -> dict`** (name flexible), e.g.:
  - `provisioned_cpu_m = replicas_effective * cpu_request_m` (or use **limits** if research defines “worst-case reservation”; document choice).
  - `provisioned_mem_mib = replicas_effective * mem_request_mib`.
  - `cost_score = replicas_effective * (normalized_cpu + normalized_mem)` with normalization constants to balance units (e.g. CPU in cores, memory in GiB, then weighted sum).
  - For HPA-only replica count: use `max(config['hpa']['max_replicas'], observed replicas)` vs **current** replicas—research must pick definition (provisioned upper bound vs observed time-averaged).
- Inject results into **`experiment.json`** under e.g. `cost` or top-level `efficiency` block for the LLM and for plotting frontier curves.

### 3.5 `analysis/prometheus_collect.py`

- Parameterize **`deployment_name`**, **`namespace`**, and optionally **label selectors** or **recording rules** for Robot Shop (e.g. sum CPU across pods matching `app=frontend` or workload identity).
- For **multi-replica multi-container** cost, either aggregate by **workload** label or sum over all pods belonging to the “slice” under test (define what “N” is for Robot Shop: single service vs whole graph).

### 3.6 `analysis/verify.py`

- Not on the critical path for squeeze; **optional**: new module `squeeze_report.py` or extend verify to compare **iteration k vs k+1** cost and SLO (deterministic, not necessarily LLM).

### 3.7 `analysis/apply_diff.py`

- **`DEPLOYMENT_NAME`**, **`NAMESPACE`**, file paths: must match Robot Shop layout if YAMLs live under e.g. `deploy/robot-shop/` or Helm-rendered manifests. Consider `kubectl apply -k` or `helm upgrade` instead of static files for Robot Shop.

### 3.8 Kubernetes manifests (`apps/service/k8s/*`)

- **Short term**: keep `stress-service` for unit tests of the squeeze loop.
- **Target**: replace with **Robot Shop** Helm chart (official demo app) or vendored manifests; add **ServiceMonitor** per monitored component; document which **single** HTTP entrypoint k6 uses (typically front-end service) and which Deployment(s) the LLM is allowed to resize (scope: one microservice vs several).

### 3.9 `benchmarks/load-tests/k6/*.js`

- Point **`BASE_URL`** at Robot Shop URL path (not `/login` JSON unless you add a compatible shim).
- Align **k6 thresholds** with **experiment SLO** to avoid `k6_thresholds_crossed` fighting the squeeze gate, or map threshold failures into the same `slo_status` logic.

### 3.10 `apps/service/` (FastAPI)

- **Research pivot**: retire as default SUT in docs/scripts; keep optional for regression of the analysis pipeline. Robot Shop becomes the primary integration surface.

---

## 4. Implementation Steps (Prioritized Checklist)

1. **Document cost definition** (requests vs limits; per-pod vs total cluster; HPA max vs observed replicas). Encode in `experiment_build.compute_cost_metrics()` and snapshot in `experiment.json`.
2. **Add `slo_status`** helper (single source of truth from k6 + SLO) used by both `start.py` and reporting.
3. **Refactor `start.py`** to extract “one iteration” function: port-forwards → k6 → `analysis_main` → return paths + parsed SLO + cost from latest `experiment.json`.
4. **Implement squeeze loop** in `start.py`: max iterations, stop on SLO FAIL, persist **Optimal Frontier** = last PASS iteration’s config + cost + artifacts.
5. **Revise `prompts.SYSTEM_PROMPT`** for optimization headroom / over-provisioning JSON contract; adjust `results._postprocess_llm_result` for new fields and invariants.
6. **Config file** (e.g. `squeeze_config.yaml` or env): `NAMESPACE`, `DEPLOYMENT_NAME`, `PROMETHEUS_URL`, `K6_BASE_URL`, paths to manifests or Helm release name.
7. **Integrate Robot Shop**: add Helm chart dependency or install docs; wire k6 to public route; extend Prometheus queries to chosen Deployment(s); update `apply_diff` to target those resources.
8. **Evaluation harness**: export CSV/JSON series `(iteration, cost_score, p95, error_rate, replicas)` for paper plots; optional LLM-free baseline (rule-based 10% CPU/mem step-down) for ablation.
9. **Clean up semantics**: clarify interaction between k6 built-in thresholds and experiment SLO so the squeeze gate is not ambiguous.
10. **Safety**: cluster quota checks, minimum resource floors, and rollback command to restore frontier config after failed squeeze.

---

## 5. Mathematical alignment note

**Current success narrative:** avoid / explain **500s and SLO violations**, explore **higher** throughput (`lambda_crit`, `next_experiment`).

**Target success narrative:** minimize **provisioned cost** \( C \approx N \times (\alpha \cdot \text{CPU} + \beta \cdot \text{Mem}) \) (or \(N \times \text{CPU} + N \times \text{Mem}\) with normalized units) subject to **fixed** offered load \( \lambda_{\text{fixed}} \) and **SLO** constraints. The **Optimal Frontier** is the last **PASS** before the first **FAIL** in the squeeze sequence—not the first failure configuration itself.

---

## 6. Summary

The repository today implements a **single-shot (or two-shot verify) stress test + LLM failure diagnosis** pipeline centered on **`stress-service`**. The **Iterative Squeeze** pivot reuses k6, Prometheus enrichment, YAML apply, and experiment JSON assembly, but requires a **new control loop in `start.py`**, a **new LLM contract in `prompts.py`**, a **cost function in `experiment_build.py`**, and **Robot Shop–aware** deployment, scraping, and load-test wiring. This roadmap is the intended sequence for that migration.
