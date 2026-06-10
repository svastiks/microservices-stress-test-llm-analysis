import json
import math
import os

SYSTEM_PROMPT = """You are an expert in microservice performance analysis and Kubernetes autoscaling. Your task is to analyze stress-test results and identify failure archetypes, estimate critical load thresholds (lambda_crit), and produce actionable diagnoses.

Given an experiment JSON (config, workload, observed metrics, failure status) and the current Deployment/HPA YAML, respond with exactly this JSON structure (all fields required):
{
  "report": "structured markdown analysis",
  "deployment_yaml_new": "full contents of the updated deployment YAML, or empty string \"\" if no change is needed",
  "hpa_yaml_new": "full contents of the updated HPA YAML, or empty string \"\" if no change is needed",
  "failure_archetype": "one of: NONE | CPU_THROTTLING | MEMORY_PRESSURE_OOM | AUTOSCALER_LAG | DEPENDENCY_SATURATION | UNKNOWN",
  "lambda_crit_estimate": "number (requests/sec) or null if cannot estimate",
  "next_experiment": "markdown string describing suggested next test",
  "evidence": ["array", "of", "specific", "metric", "citations"]
}

FAILURE ARCHETYPE RULES:
- When failure.failed is false: set failure_archetype to NONE. Do not assign a bottleneck when the test passed.
- Only assign a non-NONE archetype when failure.failed is true AND the evidence clearly points to that cause.
- Distinguish *why* failure.failed is true:
  - If failure.reason == "k6_thresholds_crossed": this is a k6 threshold failure (e.g. p95 < 400ms), which may be stricter than the experiment SLO. You MUST NOT claim the experiment SLO was violated unless observed.latency_ms.p95 > slo.p95_latency_ms or observed.error_rate > slo.error_rate.
  - If failure.reason ends with "_slo_violation": this is an experiment SLO violation.
- Hard constraint: If you violate any MUST/MUST NOT rule below, your answer is invalid. Prefer UNKNOWN over guessing.

TELEMETRY / SCALING_HINT (read from experiment JSON):
- observed.telemetry.utilization_trustworthy: when false, Prometheus did not return reliable CPU/memory series (or replica context). You MUST NOT diagnose CPU_THROTTLING, MEMORY_PRESSURE_OOM, AUTOSCALER_LAG, or DEPENDENCY_SATURATION from cpu_util_pct/mem_util_pct alone; use UNKNOWN unless k6/SLO evidence alone suffices.
- scaling_hint (UP | DOWN | HOLD | UNKNOWN) and scaling_rationale summarize a deterministic provisioning direction. Treat UNKNOWN as “no safe utilization-based conclusion.” Align your YAML recommendations with scaling_hint when it is not UNKNOWN; do not recommend aggressive scale-down when scaling_hint is HOLD or UP.

FAILURE ARCHETYPE DEFINITIONS (use only when failure.failed == true and evidence supports):
- CPU_THROTTLING: SLO violated AND cpu_util_pct near 100%, cpu_util_to_limit > 0.9, high latency, no OOM
- MEMORY_PRESSURE_OOM: SLO violated AND oom_kills > 0, mem_util_pct high, container restarts
- AUTOSCALER_LAG:
  - Use only when ALL are true:
    - SLO violated AND replicas < config.hpa.max_replicas (or observed.replicas_max < config.hpa.max_replicas), AND
    - there is evidence the service was compute-bound per pod (cpu_util_pct >= 50 OR cpu_util_to_limit >= 0.7), AND
    - scaling would plausibly help (replicas stuck due to HPA reaction/limits rather than a non-CPU bottleneck).
  - Hard MUST NOT: If cpu_util_pct < 50 AND cpu_util_to_limit < 0.7, you MUST NOT output AUTOSCALER_LAG.
  - MUST NOT use AUTOSCALER_LAG when cpu_util_pct < 20 (even if replicas stayed at min and latency is high). That indicates the HPA's CPU signal did not fire; this is not "lag".
- DEPENDENCY_SATURATION:
  - Use when SLO violated AND (cpu_util_pct < 30 AND mem_util_pct < 30 AND oom_kills == 0) AND latency is high.
  - This covers "high latency with low CPU/memory" which is typically waiting on I/O (downstream, queueing, locks) or other non-CPU constraints.
- UNKNOWN:
  - Use when failure.failed true but metrics are insufficient/conflicting to pick a single cause.
  - MUST use UNKNOWN (not AUTOSCALER_LAG) when cpu_util_pct < 20 and mem_util_pct < 30 and you cannot cite any downstream/error evidence.

DIAGNOSIS PROCEDURE (follow in order):
1) If failure.failed is false → failure_archetype=NONE.
2) If oom_kills > 0 → MEMORY_PRESSURE_OOM.
3) If cpu_util_to_limit > 0.9 or cpu_util_pct near 100% → CPU_THROTTLING.
4) If cpu_util_pct < 20 AND mem_util_pct < 30:
   - If latency high → DEPENDENCY_SATURATION (or UNKNOWN if you cannot justify dependency/I/O plausibly).
   - Never AUTOSCALER_LAG.
5) Consider AUTOSCALER_LAG only if cpu_util_pct >= 50 (or cpu_util_to_limit >= 0.7) AND replicas clearly should/ could have increased.

LAMBDA_CRIT ESTIMATION:
- If failure.failed == true: estimate lambda_crit as achieved_requests_per_second (or slightly below if SLO violated)
- If failure.failed == false: lambda_crit is above current load (estimate as achieved_requests_per_second * 1.2 or null)
- Consider: observed latency vs SLO, error_rate trends, resource saturation points

SCALING DOWN / RIGHT-SIZING (when failure.failed is false):
- If no SLO violations and utilization is low (e.g. cpu_util_pct and mem_util_pct low, replicas at min or more than needed), recommend scaling DOWN with specific numbers (fewer replicas, lower cpu/mem requests and limits, tighter HPA max_replicas).
- λcrit much higher than achieved_requests_per_second with low utilization means over-provisioned; recommend right-sizing.

REPORT STRUCTURE (markdown):
1. **Failure Summary**: Did SLO violations occur? Which ones (p95 latency, error rate)?
2. **Scaling**: When observed.replicas_at_start and observed.replicas (or observed.scaled_during_test) are present, state: "Scaled during test: yes (replicas_at_start → replicas)" or "Scaled during test: no (replicas stayed at N)" and whether that was appropriate.
3. **Root Cause Analysis**: Dominant bottleneck from observed metrics, OR when no failure: note if over-provisioned and recommend scale-down (CPU, memory, replicas, HPA).
4. **Evidence**: Cite specific values from observed.* (e.g., "cpu_util_pct: 92%", "oom_kills: 2").
5. **Recommended Fix**: Concrete YAML changes—scale UP when failing, scale DOWN when over-provisioned.
6. **Next Experiment**: Validation test (e.g. higher load to find lambda_crit, or rerun after scale-down).

NEXT EXPERIMENT RULES:
- Use workload.target_requests_per_second and observed.achieved_requests_per_second. Do NOT suggest the same target RPS; suggest something different (e.g. 20% higher, or config change).
- When suggesting target RPS to find/validate lambda_crit, align with lambda_crit_estimate.

YAML_FIX RULES:
- Return full-file YAMLs, not diffs:
  - deployment_yaml_new: If you recommend ANY change to the current deployment YAML, return the ENTIRE updated file contents as a single YAML document. If no change is needed, return the empty string "".
  - hpa_yaml_new: If you recommend ANY change to the current HPA YAML, return the ENTIRE updated file contents as a single YAML document. If no change is needed, return the empty string "".
- Schema/field correctness:
  - Do NOT invent keys that do not exist in Kubernetes YAML for these resources.
  - HPA uses maxReplicas/minReplicas (camelCase) and autoscaling/v2 fields under spec.metrics.
- Location correctness:
  - Only change Deployment replicas at spec.replicas (top-level under the Deployment's spec). Only change container resources under spec.template.spec.containers[].resources. Only change HPA under spec.minReplicas, spec.maxReplicas, spec.behavior, spec.metrics.
- When failure_archetype is NONE and over-provisioned: you MUST return full deployment_yaml_new and/or hpa_yaml_new with the scale-down changes (e.g. fewer replicas, lower HPA min/max). Empty strings only when no change is needed (well-sized).
- When failure_archetype is set: address that bottleneck with specific numeric changes in the returned full YAML(s). No backticks or markdown inside the YAML strings.
- When cpu_util_pct and mem_util_pct are both low (e.g. < 30%) and replicas well below max_replicas, do NOT recommend increasing minReplicas or maxReplicas; suggest scale-down or UNKNOWN.
- When failure_archetype is UNKNOWN, set both deployment_yaml_new and hpa_yaml_new to "".
- Hard stop: If you cannot produce valid full YAML(s), set both to "".

COST-AND-SCALE OPTIMIZATION:
- Balance performance and cost: recommend the smallest configuration change likely to satisfy the SLO, rather than large jumps.
- When increasing replicas or resource limits, avoid more than doubling values unless the evidence clearly shows near-saturation (e.g., cpu_util_to_limit ~ 1.0 AND severe SLO violations).
- Prefer HPA tuning (e.g., slightly higher maxReplicas, adjusted target_cpu_util_pct) and modest resource increases over aggressive over-provisioning.
- When AUTOSCALER_LAG is the archetype, prioritize fixing HPA behavior (maxReplicas, minReplicas, target_cpu_util_pct) with modest increments before proposing very large replica counts.

EVIDENCE ARRAY:
- List specific metric values that support the diagnosis. Format: ["observed.latency_ms.p95: 740ms", "observed.cpu_util_pct: 92%"]
- If observed.replicas or observed.replicas_max exist in the experiment JSON, you MUST include both in evidence (even for DEPENDENCY_SATURATION).

Be precise and evidence-driven. Map config × load → failure archetype."""

EFFICIENCY_SYSTEM_PROMPT = """You are an expert in Kubernetes performance and cost optimization.

Goal: for a fixed workload, identify optimization headroom and recommend conservative resource reductions while preserving SLO compliance.

Given an experiment JSON and current Deployment/HPA YAML, return exactly this JSON:
{
  "report": "structured markdown analysis",
  "deployment_yaml_new": "full updated deployment YAML or empty string",
  "hpa_yaml_new": "full updated HPA YAML or empty string",
  "failure_archetype": "NONE | CPU_THROTTLING | MEMORY_PRESSURE_OOM | AUTOSCALER_LAG | DEPENDENCY_SATURATION | UNKNOWN",
  "lambda_crit_estimate": null,
  "next_experiment": "For squeeze mode, always suggest rerunning same fixed workload after change, unless SLO failed",
  "optimization_headroom": "NONE | LOW | MEDIUM | HIGH",
  "over_provisioned": true,
  "evidence": ["metric citations"]
}

Rules:
- This mode supports both DOWN and UP movement for fixed-workload right-sizing.
- If failure.failed is true and scaling_hint is not UP, return empty deployment_yaml_new and hpa_yaml_new.
- If scaling_hint is UNKNOWN OR observed.telemetry.utilization_trustworthy is false: return empty deployment_yaml_new and hpa_yaml_new (even if failure.failed is false); explain that metrics are missing in report bullets.
- If scaling_hint is HOLD in squeeze mode: do NOT return empty YAML by default; propose a directional step sized from SLO status and utilization (failure.failed=true => UP, false => DOWN) so the loop can continue toward boundary discovery.
- If scaling_hint is UP and utilization is trustworthy: **minimize cost_score at PASS** — change **one axis per iteration** (CPU, memory, OR replicas/HPA). At thin campaign baseline (~50m/25Mi/1 pod) with prefer_replica_step, add +1 replica only before any vertical bump.
- If failure.failed is false and scaling_hint is DOWN and utilization is trustworthy, reduce resources based on how low util is and how much latency slack exists; larger cuts only when clearly over-provisioned.
- Size every change from experiment metrics; cite the reasoning in evidence (e.g. "cpu_util 22% vs 60% target → reduce request 100m→70m").
- Always reference cost fields (cost.cost_score, provisioned_request_cpu_m, provisioned_request_mem_mib) when discussing headroom. cost_score weights CPU ~90% vs memory ~10% (GCP-aligned); CPU request cuts matter more than memory for cost.
- Return full-file YAMLs only when making a change.
- LATENCY SLACK: If observed.telemetry.utilization_trustworthy is true AND observed.latency_ms.p95 is missing or is less than 50% of slo.p95_latency_ms and failure.failed is false, treat headroom as at least MEDIUM: set optimization_headroom to MEDIUM or HIGH, over_provisioned true, and return full YAML with a modest reduction unless already minimal. If utilization is not trustworthy, skip this shortcut (keep YAML empty and explain).
- Do NOT suggest raising target RPS or changing the fixed workload; next_experiment must say to re-run the same workload after applying the leaner YAML.
- lambda_crit_estimate must always be null for this mode.
- Keep report.md simple and short: 5-8 bullet lines max, plain language, include only SLO result, cost trend, key optimization, and next action.
"""

EFFICIENCY_LLM_ONLY_SQUEEZE_PROMPT = """You are an expert in Kubernetes performance and cost optimization for research-grade comparisons.

Goal: for a FIXED workload (do not change target RPS/duration), reach the cost-effective boundary in as FEW iterations as possible while staying safe.
The squeeze outer loop stops at: first FAIL when scaling DOWN (optimal = previous PASS), or first PASS when scaling UP from under-provisioning.

Return exactly this JSON:
{
  "report": "structured markdown analysis (5-10 short bullets)",
  "deployment_yaml_new": "full updated deployment YAML or empty string",
  "hpa_yaml_new": "full updated HPA YAML or empty string",
  "failure_archetype": "NONE | CPU_THROTTLING | MEMORY_PRESSURE_OOM | AUTOSCALER_LAG | DEPENDENCY_SATURATION | UNKNOWN",
  "lambda_crit_estimate": null,
  "next_experiment": "Re-run the same fixed workload after applying YAML (unless SLO failed and you need no change)",
  "optimization_headroom": "NONE | LOW | MEDIUM | HIGH",
  "over_provisioned": true,
  "evidence": ["metric citations"]
}

Rules (LLM-only / research path — you are the sole source of sizing; Python does not rewrite your YAML each iteration):
- Primary objective: minimize iterations to the boundary while beating formula and vanilla on cost_score. Python only clamps replica steps to at most one pod vs live and vetoes illegal replica cuts.
- **FAT-START / over-replicated (mandatory)**: when SLO PASS, live ≥ 4, and max(cpu_util_pct, mem_util_pct) < 50% — you **MUST** drop **exactly one replica** vs live and set hpa maxReplicas to match. Trim CPU/memory ~10–15% vs on-disk in the same YAML. **Forbidden**: same spec.replicas as live with only CPU/mem change.
- When SLO PASS, live ≥ 3, limit util < 55%, **cpu_util_request_pct < 50%**, and cost.cost_score > 0.25 — **MUST** drop one replica this iteration (resource-only trim alone is insufficient).
- Phase 1 (resource-only hold) applies **only** when live ≤ 2 OR max util ≥ 55%. Do not hold 3+ replicas while utilization is below 55%.
- **Cold-util DOWN**: when cpu_util_pct and mem_util_pct are below ~35% **and cpu_util_request_pct < 50%** and live > 1 — prefer **replica drop** when live ≥ 3; otherwise 15–25% CPU/mem cut.
- **Gate-slack DOWN** (target ≥ 50 RPS only): when cpu_util_request_pct is 50–88% and live ≥ 4 — **hold replicas**; coupled 10–15% CPU+mem trim only (limit-only cpu_util_pct can look cold while request% is warm).
- **Low-RPS DOWN** (target ≤ 35 RPS): **gate-slack does not apply** — at light load, **fewer pods beats fatter pods**. When live ≥ 4 on first DOWN, **MUST drop one replica** (never resource-only while still ≥ 4 pods). When live = 3 and cpu_util_request_pct < 90%, **MUST drop to 2** this iteration plus coupled 12–18% CPU+mem trim. Reach **2 pods** before fine-trimming per-pod CPU.
- **Two-pod floor**: when live = 2 and SLO PASS — **never** drop to 1 replica; always return coupled 12–15% CPU+mem trim (never empty YAML — let the next measurement record the FAIL).
- **Hot-util DOWN (mandatory)**: when SLO PASS and max(cpu_util_pct, mem_util_pct) ≥ 55%: if live ≥ 3, **drop one replica** even if the previous step was also a replica drop. If live = 2 and util < 85%, **trim CPU/memory 10–15%** toward FAIL. If live ≤ 2 and util ≥ 85%, return **empty** YAML (frontier reached).
- Phase 2 (replica squeeze): after Phase 1, alternate replica vs resource DOWN — never lower replicas two PASS iterations in a row. If previous squeeze_down_axis was **replica**, cut CPU/memory only. On a replica step: lower spec.replicas by at most 1 vs live; trim CPU/memory only when cpu_util and mem_util are both well below 55%.
- On a **replica** iteration: lower spec.replicas by at most 1 vs live AND reduce CPU/memory vs the current file.
- On a **resources** iteration: reduce CPU/memory vs the current file; keep spec.replicas unchanged unless already at one pod.
- Read failure.failed, slo, observed.cpu_util_pct, mem_util_pct, latency vs slo, cost.cost_score, observed.replicas. The experiment may omit scaling_hint (llm_pure_squeeze); do not wait for it.
- DOWN boundary (SLO PASS, seeking cost-effective limit): you MUST return full deployment_yaml_new and/or hpa_yaml_new with a scale-down — never empty strings. NEVER increase cpu/memory requests or limits vs the current on-disk file on PASS (high cpu_util_pct means hot, not "raise requests"). If a repair prompt shows your rejected (too-large) YAML, fix it with a DOWN-only proposal vs the on-disk baseline.
- NEVER return YAML identical to the current on-disk file during squeeze-down. If the file already shows fewer replicas than max(observed.replicas, observed.replicas_max), still return full YAML with spec.replicas = max(1, live-1), aligned HPA maxReplicas, and reduced CPU/memory vs the file so the cluster can converge.
- If utilization is not trustworthy but SLO PASS: still propose a conservative DOWN patch from whatever metrics exist; explain uncertainty in the report.
- If failure.failed is true: propose UP sized from failure severity and utilization unless scale-up is unsafe (then empty YAML + explain).
- Code may only clamp replicas to at most one fewer than max(observed.replicas, observed.replicas_max); it will not rewrite your CPU/memory choices.
- Always return full-file YAML when you change a file; never diffs inside the JSON strings.
- lambda_crit_estimate must always be null.
- Cite cost.cost_score, provisioned_request_cpu_m, provisioned_request_mem_mib, observed.replicas, observed.replicas_max in evidence when relevant.

REPLICAS (hard, separate from CPU/mem sizing):
- On SLO PASS when reducing replicas: lower spec.replicas by **at most 1** vs max(observed.replicas, observed.replicas_max). Set hpa maxReplicas to that same target. Never skip steps (e.g. 3→1).

CPU / MEMORY (derive step size from metrics — no fixed % cap):
- Use observed.cpu_util_pct, mem_util_pct, latency vs slo.p95_latency_ms, optimization_headroom, over_provisioned, and cost.cost_score vs prior iteration when available.
- SLO PASS + trustworthy telemetry: when live ≥ 3, **replica drop beats resource-only trim** (even when util ≥ 55%; consecutive replica drops OK). When live = 2 and util is 55–85%, one **10–15%** CPU/mem trim. When live ≤ 2 and util ≥ 85%, return **empty** YAML.
- SLO PASS but util not trustworthy: prefer a small CPU/mem trim or replica-only step; explain missing telemetry in the report.
- SLO FAIL: increase enough to clear the bottleneck suggested by failure_archetype and metrics (CPU vs memory vs replicas/HPA); larger steps only when saturation is clear (e.g. cpu_util_pct very high or repeated FAIL after small UP).
- SLO FAIL / UP recovery: use experiment.up_recovery_signals when present — bottleneck, throughput_ratio (achieved/target), latency_ratio (p95/SLO). Never assume fixed RPS; size from ratios only. **One axis per iteration.** Primary objective: **lowest cost_score at PASS** — beat the deterministic formula ladder on provisioned_request_cpu_m (CPU ~90% of cost). PASS cpu gate uses **observed.cpu_util_request_pct** (request-relative) — **not** observed.cpu_util_pct. When still at thin baseline with prefer_replica_step: +1 replica only, hold CPU/mem. After replica-first: **coupled ~15%** on both CPU and memory. **CPU-gate precision finish** (p95 PASS, failure.reason=cpu_utilization_exceeded, cpu_util_request_pct 96–105%, mem_util_pct < 25%): **CPU request ONLY** — hold memory byte-identical to on-disk; see FRONTIER EXAMPLE below. If a repair prompt rejects coupled memory bump, return CPU-only. When cpu_util_request_pct > 110%: coupled ~15% on both axes. Hold replicas unless prefer_replica_step at single pod.
- Replicas follow the one-step rule above; coordinate CPU/mem sizes with observed utilization on every DOWN step.

UP RECOVERY FRONTIER EXAMPLE (mandatory pattern when cpu gate is the only remaining FAIL):
- Observed: p95=224ms PASS, cpu_util_request_pct=96%, mem_util_pct=15%, replicas=2, on-disk requests **129m CPU / 66Mi mem**, failure.reason=cpu_utilization_exceeded
- **WRONG**: 138m/73Mi — raises memory though mem_util is low → overshoots cost_score vs formula
- **RIGHT**: **135m/66Mi** — CPU-only micro-bump (~ceil(129×96/92)); memory requests/limits **unchanged** vs on-disk; targets ~90–93% cpu_util_request_pct at PASS
"""

VANILLA_LLM_SQUEEZE_PROMPT = """You are helping tune Kubernetes Deployment and HPA YAML after a stress test.

You receive only a short outcome summary and the current YAML — not detailed Prometheus metrics, cost scores, or scaling hints.

Return exactly this JSON:
{
  "report": "short markdown (3-6 bullets)",
  "deployment_yaml_new": "full updated deployment YAML or empty string",
  "hpa_yaml_new": "full updated HPA YAML or empty string",
  "failure_archetype": "NONE | CPU_THROTTLING | MEMORY_PRESSURE_OOM | AUTOSCALER_LAG | DEPENDENCY_SATURATION | UNKNOWN",
  "lambda_crit_estimate": null,
  "next_experiment": "Re-run the same fixed workload after applying YAML",
  "optimization_headroom": "NONE | LOW | MEDIUM | HIGH",
  "over_provisioned": false,
  "evidence": ["brief citations from the summary only"]
}

Rules:
- Same fixed workload each iteration — do not change target RPS or duration.
- If the test FAILED (high p95 or errors): scale UP — raise CPU/memory requests and limits and/or replicas/HPA maxReplicas modestly until the service can likely meet the SLO.
- If the test PASSED with comfortable latency (p95 well below SLO): scale DOWN — you MUST return full deployment_yaml_new and/or hpa_yaml_new with a reduction (lower CPU/memory ~10–20% and/or one fewer replica). Never return empty strings on PASS during squeeze-down.
- Return full-file YAML when changing a file; empty string only when no change is possible (already at minimum).
- deployment_yaml_new and hpa_yaml_new must be plain YAML text only — never wrap in markdown code fences (no ```yaml).
- lambda_crit_estimate must always be null.
- Do not invent metrics you were not given.
"""


def build_vanilla_user_prompt(
    experiment_json: dict, current_yaml: str = "", mode: str = "failure"
) -> str:
    """Coarse summary + YAML only (no full experiment JSON)."""
    failure = experiment_json.get("failure") or {}
    failed = bool(failure.get("failed"))
    slo = experiment_json.get("slo") or {}
    wl = experiment_json.get("workload") or {}
    obs = experiment_json.get("observed") or {}
    lat = obs.get("latency_ms") or {}
    cfg = experiment_json.get("config") or {}
    hpa = cfg.get("hpa") or {}
    target_rps = wl.get("target_requests_per_second")
    duration_s = wl.get("duration_s", 90)
    slo_p95 = slo.get("p95_latency_ms", 500)
    p95 = lat.get("p95")
    err = obs.get("error_rate")
    ach = obs.get("achieved_requests_per_second")
    repl = obs.get("replicas")

    parts = [
        "Stress test outcome (coarse summary only):\n",
        f"- Target load: {target_rps} RPS for {duration_s}s\n",
        f"- Result: {'FAIL' if failed else 'PASS'}\n",
    ]
    if failed and failure.get("reason"):
        parts.append(f"- Failure reason: {failure.get('reason')}\n")
    if p95 is not None:
        parts.append(f"- p95 latency: {p95} ms (SLO limit: {slo_p95} ms)\n")
    if err is not None:
        parts.append(f"- Error rate: {err}\n")
    if ach is not None:
        parts.append(f"- Achieved throughput: {ach} RPS\n")
    if repl is not None:
        parts.append(f"- Replicas observed during test: {repl}\n")
    parts.append(
        f"- Current config (from YAML): CPU request {cfg.get('cpu_request_m')}m, "
        f"mem {cfg.get('mem_request_mib')} MiB; "
        f"replicas {cfg.get('deployment_replicas')}; "
        f"HPA min/max {hpa.get('min_replicas')}/{hpa.get('max_replicas')}\n"
    )
    prev = experiment_json.get("_prev_iteration") or {}
    if prev.get("status"):
        parts.append(
            f"- Previous iteration: {prev.get('status')} "
            f"(replicas {prev.get('replicas')}, p95 {prev.get('p95_ms')} ms)\n"
        )
    if mode == "squeeze":
        if not failed and p95 is not None and slo_p95:
            slack = float(p95) / float(slo_p95)
            if slack < 0.1:
                parts.append(
                    f"\nSLO PASS with large latency slack (p95 {p95} ms vs SLO {slo_p95} ms). "
                    "**Mandatory**: return scaled-down YAML — cut CPU/memory ~10–20% and/or drop "
                    "spec.replicas and hpa maxReplicas by 1 (never empty strings).\n"
                )
        parts.append(
            "\nPropose updated full Deployment and/or HPA YAML for the **same** load on the next run. "
            "If FAIL, increase capacity; if PASS with slack, trim capacity (required — not optional).\n"
        )
    if current_yaml.strip():
        parts.append(
            "\nCurrent Kubernetes YAML:\n```yaml\n"
        )
        parts.append(current_yaml)
        parts.append("\n```")
    return "".join(parts)


def _up_recovery_thin_baseline_m() -> tuple[int, int]:
    cpu = int(os.environ.get("SQUEEZE_UP_THIN_CPU_M", "50"))
    mem = int(os.environ.get("SQUEEZE_UP_THIN_MEM_MIB", "25"))
    return cpu, mem


def build_user_prompt(
    experiment_json: dict, current_yaml: str = "", mode: str = "failure"
) -> str:
    """Build prompt from experiment.json (and optional deployment YAML)."""
    exp_str = json.dumps(experiment_json, indent=2)
    failure = experiment_json.get("failure") or {}
    failed = bool(failure.get("failed"))
    scaling_hint = (experiment_json.get("scaling_hint") or "").strip()
    in_up_recovery = bool(
        experiment_json.get("up_recovery")
        or (failed and scaling_hint == "UP")
    )
    if mode == "squeeze":
        if in_up_recovery:
            focus = (
                "Focus on: under-provisioned UP recovery at fixed workload — reach SLO PASS with the "
                "**lowest cost_score** (replicas × CPU/mem requests). Change **one axis per iteration** "
                "(CPU, memory, OR replicas/HPA) from observed metrics and up_recovery_signals. "
                "At thin baseline (~50m/25Mi/1 pod) with prefer_replica_step, horizontal scale only. "
                "Ignore lambda_crit."
            )
        else:
            focus = (
                "Focus on: optimization_headroom, over/under-provisioning signals, cost-aware right-sizing, "
                "and YAML changes for this same fixed workload (DOWN on PASS; UP only after FAIL). "
                "Choose CPU/memory step sizes from observed utilization, latency vs SLO, and headroom — "
                "not from fixed percentage rules. Replicas: at most one pod fewer per DOWN step. "
                "Ignore lambda_crit and higher-RPS exploration."
            )
    else:
        focus = (
            "Focus on: failure_archetype (NONE when failure.failed is false), lambda_crit estimate, "
            "evidence from observed.*, concrete Kubernetes config changes, and a concrete next experiment."
        )
    parts = [
        "Analyze this stress-test experiment record:\n```json\n",
        exp_str,
        "\n```\n\n",
        f"{focus}\n\n",
    ]
    if mode == "squeeze" and in_up_recovery:
        cfg = experiment_json.get("config") or {}
        obs = experiment_json.get("observed") or {}
        dep_rep = int(cfg.get("deployment_replicas") or 0)
        hpa_cfg = cfg.get("hpa") or {}
        hpa_max = int(hpa_cfg.get("max_replicas") or dep_rep or 1)
        live_rep = int(obs.get("replicas") or 0)
        live_max = int(obs.get("replicas_max") or 0)
        at_single_pod = max(dep_rep, hpa_max, live_rep, live_max) <= 1
        thin_cpu, thin_mem = _up_recovery_thin_baseline_m()
        cfg_cpu = int(cfg.get("cpu_request_m") or 0)
        cfg_mem = int(cfg.get("mem_request_mib") or 0)
        at_thin_baseline = (
            at_single_pod and cfg_cpu <= thin_cpu and cfg_mem <= thin_mem
        )
        slo = experiment_json.get("slo") or {}
        failure = experiment_json.get("failure") or {}
        fail_reason = str(failure.get("reason") or "")
        p95 = float((obs.get("latency_ms") or {}).get("p95") or 0)
        slo_p95 = float(slo.get("p95_latency_ms") or 500)
        cpu_req_pct = float(obs.get("cpu_util_request_pct") or 0.0)
        cpu_lim_pct = float(obs.get("cpu_util_pct") or 0.0)
        mem_util_pct = float(obs.get("mem_util_pct") or 0.0)
        sig = experiment_json.get("up_recovery_signals") or {}
        thr_ratio = sig.get("throughput_ratio")
        lat_ratio = sig.get("latency_ratio")
        bottleneck = sig.get("bottleneck", "unknown")
        prefer_rep = sig.get("prefer_replica_step")
        target_rps = sig.get("target_rps") or (experiment_json.get("workload") or {}).get(
            "target_requests_per_second"
        )
        ach_rps = sig.get("achieved_rps") or obs.get("achieved_requests_per_second")
        thr_s = f"{thr_ratio:.2f}" if thr_ratio is not None else "n/a"
        lat_s = f"{lat_ratio:.2f}" if lat_ratio is not None else "n/a"
        parts.append(
            "\nUP recovery (cost-aware, load-dynamic): scaling_hint=UP — grow capacity until SLO passes, "
            "but minimize provisioned cost_score. Size from **ratios**, not fixed RPS.\n"
            f"- workload target={target_rps} RPS, achieved={ach_rps} RPS, "
            f"throughput_ratio={thr_s}, "
            f"latency_ratio={lat_s}, "
            f"bottleneck={bottleneck}, prefer_replica_step={prefer_rep}.\n"
            "- **One axis per iteration** — never combine a vertical CPU/mem bump with a replica bump at thin baseline.\n"
            "- Throughput collapse or prefer_replica_step at single pod → +1 replica + HPA maxReplicas (horizontal only).\n"
            "- After horizontal step or when not at thin baseline: **coupled vertical** — raise CPU **and** memory requests/limits by the same step factor (low mem_util does NOT excuse skipping memory; starving mem inflates CPU need and cost_score).\n"
            "- mem_util>100% → memory step ≥ CPU step.\n"
            "- At most **one** replica per iteration when prefer_replica_step is true.\n"
            "- PASS requires p95 ≤ slo.p95_latency_ms, error_rate ≤ slo.error_rate, and (when telemetry "
            "is trustworthy) **cpu_util_request_pct** ≤ 95% (request-relative — matches Python squeeze gate).\n"
            "- **cpu_util_pct** is limit-relative (burn vs CPU limit); do NOT use it for PASS or replica "
            "decisions and do NOT compare it to HPA target_cpu_util_pct (60%).\n"
            "- When p95 and throughput already meet SLO but failure.reason is cpu_utilization_exceeded: "
            "**vertical CPU/mem only** — hold spec.replicas and hpa maxReplicas unchanged.\n"
            "- When deployment_replicas and live replicas are already ≥2: **never add replicas** — "
            "use coupled vertical CPU+memory only (even if p95 is slightly above SLO).\n"
            "- Never scale DOWN while failure.failed is true.\n"
            f"- Current: deployment_replicas={dep_rep}, hpa max={hpa_max}, live={live_rep}, "
            f"p95={p95:.0f}ms vs slo={slo_p95:.0f}ms, "
            f"cpu_util_request_pct={cpu_req_pct:.1f}%, cpu_util_pct(limit)={cpu_lim_pct:.1f}%, "
            f"failure.reason={fail_reason or 'n/a'}, single_pod={at_single_pod}, "
            f"thin_baseline={at_thin_baseline}.\n"
        )
        if at_thin_baseline and prefer_rep:
            parts.append(
                f"\n**REPLICA-FIRST (mandatory this iteration)**: config and on-disk YAML are still at thin "
                f"campaign baseline (~{thin_cpu}m/{thin_mem}Mi/1 pod) and prefer_replica_step=true. "
                f"You MUST return deployment_yaml_new with spec.replicas=2 and hpa_yaml_new with maxReplicas=2, "
                f"keeping CPU and memory requests/limits **identical** to the current on-disk file. "
                f"Do NOT propose 70m/35Mi or any vertical bump this iteration — cite replica-first in evidence.\n"
            )
        elif (
            in_up_recovery
            and not at_thin_baseline
            and cfg_cpu <= thin_cpu
            and cfg_mem <= thin_mem
            and max(dep_rep, live_rep, live_max) >= 2
            and failed
        ):
            parts.append(
                f"\n**VERTICAL-ONLY UP (mandatory this iteration)**: replicas are already ≥2 but CPU/mem are still "
                f"thin (~{thin_cpu}m/{thin_mem}Mi) and SLO still fails. Raise CPU **and** memory requests/limits "
                f"**one coupled ~15% step** from on-disk (e.g. 50m/25Mi→58m/29Mi) — **hold spec.replicas and "
                f"hpa maxReplicas unchanged**. Do NOT bump CPU alone.\n"
            )
        elif (
            in_up_recovery
            and failed
            and p95 > 0
            and p95 <= slo_p95
            and fail_reason == "cpu_utilization_exceeded"
        ):
            if cpu_req_pct <= float(
                os.environ.get("SQUEEZE_UP_RECOVERY_CPU_ONLY_MAX_PCT", "130")
            ):
                max_step = int(
                    os.environ.get("SQUEEZE_UP_RECOVERY_CPU_PRECISION_MAX_STEP_M", "8")
                )
                target_pct = float(
                    os.environ.get("SQUEEZE_UP_RECOVERY_CPU_PRECISION_TARGET_PCT", "93.0")
                )
                sized = (
                    max(cfg_cpu + 1, int(math.ceil(cfg_cpu * cpu_req_pct / target_pct)))
                    if cfg_cpu > 0 and cpu_req_pct > 0
                    else cfg_cpu
                )
                micro_cpu = min(sized, cfg_cpu + max_step)
                if mem_util_pct < 25.0:
                    parts.append(
                        "\n**CPU-GATE PRECISION UP (mandatory this iteration)**: p95 and throughput already meet SLO; "
                        f"cpu_util_request_pct={cpu_req_pct:.1f}% exceeds the 95% gate and mem_util_pct="
                        f"{mem_util_pct:.1f}% is low — **CPU request only**, hold memory requests/limits **identical** "
                        f"to on-disk ({cfg_mem}Mi). Set requests.cpu≈{micro_cpu}m "
                        f"(≤+{max_step}m vs on-disk; target ~93% cpu_util_request_pct at PASS); "
                        "scale limits ≥2× request. **Hold replicas**. Do NOT add memory, coupled bumps, or replicas.\n"
                    )
                else:
                    parts.append(
                        "\n**CPU-GATE PRECISION UP (mandatory this iteration)**: p95 and throughput already meet SLO; "
                        f"cpu_util_request_pct={cpu_req_pct:.1f}% is just above the 95% gate. "
                        "Apply a **minimal coupled** CPU+memory bump (~5–8% vs on-disk) sized to land "
                        "**90–93%** cpu_util_request_pct at PASS — **hold replicas**. Prefer the smallest step that "
                        "clears the gate; do not overshoot CPU or memory.\n"
                    )
            else:
                parts.append(
                    "\n**CPU-GATE-ONLY UP (mandatory this iteration)**: p95 and throughput already meet SLO; "
                    f"cpu_util_request_pct={cpu_req_pct:.1f}% exceeds the 95% squeeze gate. "
                    "Raise CPU **and** memory requests/limits **one coupled ~15% step** from on-disk — "
                    "**hold spec.replicas and hpa maxReplicas unchanged**. Do NOT add replicas or bump CPU alone.\n"
                )
    if mode == "squeeze" and not in_up_recovery:
        prev = experiment_json.get("_prev_iteration") or {}
        prev_axis = prev.get("squeeze_down_axis") or "none"
        streak = int(prev.get("resource_pass_streak") or 0)
        cfg = experiment_json.get("config") or {}
        cpu_m = int(cfg.get("cpu_request_m") or 0)
        ceiling = int(os.environ.get("SQUEEZE_LLM_REPLICA_CPU_REQUEST_CEILING_M", "100"))
        min_passes = int(
            os.environ.get("SQUEEZE_LLM_MIN_RESOURCE_PASSES_BEFORE_REPLICA", "2")
        )
        obs = experiment_json.get("observed") or {}
        cpu_util = float(obs.get("cpu_util_pct") or 0.0)
        mem_util = float(obs.get("mem_util_pct") or 0.0)
        cpu_req_pct = float(obs.get("cpu_util_request_pct") or 0.0)
        cost = experiment_json.get("cost") or {}
        cost_score = float(cost.get("cost_score") or 0.0)
        dep_rep = int(cfg.get("deployment_replicas") or 0)
        live_rep = int(obs.get("replicas") or 0)
        live_max = int(obs.get("replicas_max") or 0)
        live_for_step = max(live_rep, live_max) if live_rep > 0 else live_max
        limit_util = max(cpu_util, mem_util)
        gate_util = max(limit_util, cpu_req_pct)
        gate_slack = float(os.environ.get("SQUEEZE_LLM_DOWN_GATE_SLACK_PCT", "50"))
        target_rps = float((experiment_json.get("workload") or {}).get("target_requests_per_second") or 0)
        cold_util = (
            not failed
            and cpu_util < 35.0
            and mem_util < 35.0
            and cpu_req_pct < gate_slack
        )
        hot_util = gate_util >= 55.0
        fat_start = (
            not failed
            and live_for_step >= 4
            and limit_util < 50.0
            and cpu_req_pct < gate_slack
        )
        high_cost_replica = (
            not failed
            and not hot_util
            and live_for_step >= 3
            and limit_util < 55.0
            and cpu_req_pct < gate_slack
            and cost_score > 0.25
        )
        low_rps_down = not failed and 0 < target_rps <= 35
        gate_slack_hold = (
            not failed
            and not low_rps_down
            and live_for_step >= 4
            and cpu_req_pct >= gate_slack
            and cpu_req_pct < 88.0
        )
        replica_required = fat_start or high_cost_replica
        replica_ok = (
            replica_required
            or cold_util
            or (cpu_m > 0 and cpu_m <= ceiling)
            or streak >= min_passes
        )
        if replica_required:
            phase = (
                f"Over-replicated DOWN: live={live_for_step}, cost_score={cost_score:.4f}, "
                f"gate_util={gate_util:.0f}%. **Replica drop required** — Phase 1 hold suspended."
            )
        elif gate_slack_hold:
            phase = (
                f"Gate-slack multi-replica: live={live_for_step}, cpu_util_request_pct={cpu_req_pct:.0f}% "
                f"(squeeze gate still has headroom) — **hold replicas**, coupled 10–15% CPU+mem trim only."
            )
        elif hot_util and live_for_step >= 3 and prev_axis == "replica":
            phase = (
                f"Hot multi-replica burst: live={live_for_step}, gate_util={gate_util:.0f}% — "
                f"drop one more replica (consecutive replica OK when hot and live ≥ 3)."
            )
        elif replica_ok and prev_axis != "replica":
            phase = (
                "Phase 2: replica DOWN is allowed this iteration if metrics support it; "
                "still trim CPU/memory when headroom exists."
            )
        elif prev_axis == "replica":
            phase = (
                "Phase 2: previous axis was replica — cut CPU/memory only; "
                "do not lower spec.replicas."
            )
        elif live_for_step <= 2 or (hot_util and live_for_step <= 2):
            phase = (
                f"Resource phase (live={live_for_step}, cpu_request_m={cpu_m}, "
                f"resource_pass_streak={streak}); reduce CPU/memory toward ~55–65% utilization."
            )
        elif hot_util and live_for_step >= 3:
            phase = (
                f"Hot multi-replica: live={live_for_step}, gate_util={gate_util:.0f}% — "
                f"drop one replica before further resource-only trimming."
            )
        else:
            phase = (
                f"Replica-first: live={live_for_step} with gate_util={gate_util:.0f}% — "
                f"drop one replica before further resource-only trimming."
            )
        parts.append(
            f"\nDOWN strategy: previous squeeze_down_axis={prev_axis}, "
            f"resource_pass_streak={streak}, cost_score={cost_score:.4f}, "
            f"cpu_util_request_pct={cpu_req_pct:.1f}%. {phase} "
            "Never lower replicas two PASS iterations in a row. "
            "Use cpu_util_request_pct (not limit-only cpu_util_pct) for hot/cold replica vs resource choice.\n"
        )
        if gate_slack_hold:
            parts.append(
                f"\n**GATE-SLACK MULTI-REPLICA DOWN (mandatory)**: live={live_for_step}, "
                f"cpu_util_request_pct={cpu_req_pct:.1f}% is above gate-slack ({gate_slack:.0f}%) but still "
                f"below ~88% — thinner **per-pod** CPU+memory (10–15% coupled trim) often beats fewer pods "
                f"(e.g. 4×71m can beat 3×95m at higher RPS). **Hold spec.replicas and hpa maxReplicas** "
                f"unchanged this iteration.\n"
            )
        if target_rps >= 50.0 and gate_slack_hold:
            parts.append(
                f"\n**HIGH-RPS DOWN**: target={target_rps:.0f} RPS — explore multi-replica thin configs "
                f"before dropping below {live_for_step} pods while cpu_util_request_pct < 88%.\n"
            )
        if low_rps_down and live_for_step >= 4:
            next_rep = max(1, live_for_step - 1)
            parts.append(
                f"\n**LOW-RPS REPLICA-FIRST (mandatory — overrides gate-slack)**: target={target_rps:.0f} RPS, "
                f"live={live_for_step}, cpu_util_request_pct={cpu_req_pct:.1f}%, cost_score={cost_score:.4f}. "
                f"At light load, **MUST** set spec.replicas={next_rep} and hpa maxReplicas={next_rep} "
                f"plus coupled **12–18%** CPU+mem trim. **Forbidden**: same replica count with only CPU/mem change.\n"
            )
        elif low_rps_down and live_for_step == 3 and cpu_req_pct < 90.0:
            parts.append(
                f"\n**LOW-RPS 3→2 (mandatory)**: target={target_rps:.0f} RPS, live=3, "
                f"cpu_util_request_pct={cpu_req_pct:.1f}% — **MUST** drop to spec.replicas=2 and "
                f"hpa maxReplicas=2 plus coupled **12–18%** CPU+mem trim (vanilla reaches 2 pods here).\n"
            )
        elif low_rps_down and live_for_step >= 3:
            parts.append(
                f"\n**LOW-RPS DOWN (mandatory)**: target={target_rps:.0f} RPS, live={live_for_step}, "
                f"cpu_util_request_pct={cpu_req_pct:.1f}% — coupled **15–20%** CPU+mem trim; "
                f"if previous axis was replica, trim only; otherwise drop one replica.\n"
            )
        if not failed and live_for_step == 2:
            parts.append(
                f"\n**TWO-POD FLOOR (mandatory)**: live=2 — **never** spec.replicas=1 and **never** empty YAML. "
                f"cpu_util_request_pct={cpu_req_pct:.1f}% — always return coupled 12–15% CPU+mem trim "
                f"vs on-disk so the next iteration can measure a FAIL and record the boundary.\n"
            )
        if fat_start:
            next_rep = max(1, live_for_step - 1)
            parts.append(
                f"\n**FAT-START DOWN (mandatory — overrides Phase 1)**: live={live_for_step} pods, "
                f"cpu_util={cpu_util:.0f}%, mem_util={mem_util:.0f}%. "
                f"**MUST** set spec.replicas={next_rep} and hpa maxReplicas={next_rep}. "
                f"Also trim CPU/memory ~10–15% vs on-disk. "
                f"**FORBIDDEN**: returning the same replica count as live ({live_for_step}).\n"
            )
        elif high_cost_replica:
            next_rep = max(1, live_for_step - 1)
            parts.append(
                f"\n**HIGH-COST REPLICA DOWN (mandatory)**: cost_score={cost_score:.4f}, "
                f"live={live_for_step}, gate_util={gate_util:.0f}%. "
                f"**MUST** drop to spec.replicas={next_rep} and hpa maxReplicas={next_rep} "
                f"plus modest CPU/mem trim. Resource-only step alone is insufficient.\n"
            )
        elif cold_util:
            parts.append(
                f"\n**COLD-UTIL DOWN (mandatory)**: cpu_util={cpu_util:.0f}%, mem_util={mem_util:.0f}% — "
                f"heavily over-provisioned. When live ≥ 3, **drop one replica** "
                f"({live_for_step} → {max(1, live_for_step - 1)}); otherwise cut CPU/memory 15–25%.\n"
            )
        elif hot_util and not failed:
            if live_for_step >= 3:
                next_rep = max(1, live_for_step - 1)
                burst = prev_axis == "replica"
                parts.append(
                    f"\n**HOT-MULTI-REPLICA DOWN (mandatory)**: cpu_util={cpu_util:.0f}%, "
                    f"mem_util={mem_util:.0f}%, live={live_for_step} — util ≥ 55% with 3+ pods. "
                    f"**MUST** drop to spec.replicas={next_rep} and hpa maxReplicas={next_rep}"
                    f"{' (consecutive replica OK)' if burst else ''}. "
                    f"Resource-only trim alone is forbidden when util ≥ 65%.\n"
                )
            elif live_for_step <= 2 and gate_util >= 85.0 and cpu_m > 65:
                parts.append(
                    f"\n**HOT BOUNDARY TRIM (mandatory)**: live={live_for_step}, gate_util={gate_util:.0f}%, "
                    f"cpu_request_m={cpu_m} — still above lean floor. **Trim CPU/memory 10–15%**; "
                    f"do NOT lower replicas. Empty YAML only when cpu_request_m ≤ 65m.\n"
                )
            elif live_for_step <= 2 and gate_util >= 85.0:
                parts.append(
                    f"\n**HOT BOUNDARY (mandatory)**: live={live_for_step}, gate_util={gate_util:.0f}% — "
                    f"frontier reached. Return **empty** deployment_yaml_new and hpa_yaml_new "
                    f"(no further DOWN this iteration).\n"
                )
            else:
                parts.append(
                    f"\n**HOT-UTIL DOWN (mandatory)**: cpu_util={cpu_util:.0f}%, "
                    f"mem_util={mem_util:.0f}%, live={live_for_step} — trim CPU/memory "
                    f"**10–15%** (one axis); do NOT lower replicas when live ≤ 2.\n"
                )
        elif live_for_step > 1 and replica_ok and prev_axis != "replica" and not hot_util:
            next_rep = max(1, live_for_step - 1)
            parts.append(
                f"\nLIVE SCALE: observed.replicas={live_rep}"
                + (f", observed.replicas_max={live_max}" if live_max else "")
                + f" → for this DOWN step set spec.replicas={next_rep} and hpa maxReplicas={next_rep} "
                f"(exactly one fewer than live={live_for_step}; never skip steps).\n"
            )
        elif live_for_step > 1 and not replica_ok:
            hold_rep = dep_rep if dep_rep > 0 else live_for_step
            parts.append(
                f"\nLIVE SCALE: hold spec.replicas={hold_rep} and hpa maxReplicas={hold_rep} "
                f"(resource phase; live={live_for_step}).\n"
            )
        elif live_rep > 0 and dep_rep != live_rep:
            parts.append(
                f"\nLIVE SCALE: observed.replicas={live_rep} (authoritative); "
                f"config.deployment_replicas={dep_rep} may lag the cluster.\n"
            )
    if current_yaml.strip():
        parts.append(
            "Current Kubernetes deployment + HPA YAML (each file prefixed with '# FILE: <relative-path>'). If you change a file, return the ENTIRE updated YAML in deployment_yaml_new and/or hpa_yaml_new. If no change for a file, use empty string for that field.\n```yaml\n"
        )
        parts.append(current_yaml)
        parts.append("\n```")
    return "".join(parts)


VERIFICATION_SYSTEM_PROMPT = """You are verifying whether a recommended Kubernetes/config diff actually fixed the issues from a stress test.

You are given:
1. Run 1 artifacts: report, analysis, the recommended diff that was applied, and key metrics (k6 summary, experiment).
2. Run 2 artifacts: same (after re-running the same test with the applied diff).

Decide whether the applied diff **worked**:
- GOOD: Run 2 shows improvement (SLOs met, fewer/no failures, or run 2's report has no or minimal further recommendation). The fix addressed the root cause and was cost-effective.
- BAD: Run 2 is worse or unchanged (same failures, or new issues). The diff was insufficient, wrong, or introduced regressions.

IMPORTANT: Distinguish k6 threshold failures from experiment SLO failures.
- If failure.reason == "k6_thresholds_crossed", that indicates k6's internal threshold(s) were crossed, which may be stricter than the experiment's SLO.
- Do NOT claim an SLO regression unless run 2 actually violates the experiment SLO (p95 > slo.p95_latency_ms OR error_rate > slo.error_rate).

Respond with exactly this JSON structure (all fields required):
{
  "verdict": "GOOD" or "BAD",
  "reasoning": "2-4 sentences explaining why the fix worked or did not.",
  "run1_summary": "One sentence: run 1 outcome (e.g. SLO violations, archetype).",
  "run2_summary": "One sentence: run 2 outcome after applying the diff.",
  "alternative_diff": "Unified diff string for a better fix, or empty string \"\" if verdict is GOOD or no YAML change is needed."
}

Rules:
- If verdict is GOOD, alternative_diff must be \"\".
- If verdict is BAD, provide alternative_diff only when a different YAML change would likely help; otherwise use \"\" and explain in reasoning.
- alternative_diff must be valid unified diff (---/+++, @@ hunks, -/+ lines) targeting deployment/HPA YAML, or empty string.
- Be evidence-based: cite metrics from run 1 vs run 2 (latency, error rate, replicas, utilization)."""


def build_verification_user_prompt(run1_artifacts: dict, run2_artifacts: dict) -> str:
    """Build user prompt for verification LLM from run1 and run2 artifact dicts."""
    parts = [
        "Compare these two stress-test runs. Run 1 produced a recommended diff that was applied; Run 2 is the same test after applying that diff.\n\n",
        "## Run 1 (before fix)\n\n",
        "### Report\n",
        run1_artifacts.get("report", ""),
        "\n\n",
        "### Analysis\n",
        run1_artifacts.get("analysis_json", "{}"),
        "\n\n",
        "### Applied recommended diff\n```diff\n",
        run1_artifacts.get("recommended_diff", ""),
        "\n```\n\n",
        "### Key metrics (k6 / experiment)\n",
        run1_artifacts.get("metrics_summary", ""),
        "\n\n",
        "## Run 2 (after fix)\n\n",
        "### Report\n",
        run2_artifacts.get("report", ""),
        "\n\n",
        "### Analysis\n",
        run2_artifacts.get("analysis_json", "{}"),
        "\n\n",
        "### Recommended diff from run 2 (if any)\n```diff\n",
        run2_artifacts.get("recommended_diff", ""),
        "\n```\n\n",
        "### Key metrics\n",
        run2_artifacts.get("metrics_summary", ""),
        "\n\n",
        "Decide: verdict (GOOD/BAD), reasoning, run1_summary, run2_summary, and alternative_diff if BAD.",
    ]
    return "".join(parts)
