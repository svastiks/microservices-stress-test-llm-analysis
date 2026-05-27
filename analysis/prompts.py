import json
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
- If scaling_hint is UP and utilization is trustworthy: **minimize cost_score at PASS** — grow CPU, memory, and replicas together when metrics show need (mem_util high, cpu_util high, or throughput near target but p95 still fails). At most one replica step per iteration; set spec.replicas and hpa maxReplicas together.
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
- Primary objective: minimize iterations to the boundary while beating formula on cost_score. Python only clamps replica steps to at most one pod vs live and vetoes illegal replica cuts.
- Phase 1 (resource squeeze): while cpu_request_m is above ~100m OR fewer than two consecutive resource-only PASS steps, hold spec.replicas at the current file value and aggressively cut CPU/memory (e.g. 150m/75Mi → ~100m/50Mi) using observed.cpu_util_pct and mem_util_pct. Target ~55–65% utilization before replica cuts when telemetry is trustworthy.
- Phase 2 (replica squeeze): after Phase 1, alternate replica vs resource DOWN — never lower replicas two PASS iterations in a row. If previous squeeze_down_axis was **replica**, cut CPU/memory only. On a replica step: lower spec.replicas by at most 1 vs live AND trim CPU/memory when headroom exists.
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
- SLO PASS + trustworthy telemetry: cut requests/limits more when utilization is far below the HPA target and latency has large slack; cut less when util is moderate or headroom is LOW. State the implied util/latency margin and chosen millicores/Mi in evidence.
- SLO PASS but util not trustworthy: prefer a small CPU/mem trim or replica-only step; explain missing telemetry in the report.
- SLO FAIL: increase enough to clear the bottleneck suggested by failure_archetype and metrics (CPU vs memory vs replicas/HPA); larger steps only when saturation is clear (e.g. cpu_util_pct very high or repeated FAIL after small UP).
- Replicas follow the one-step rule above; coordinate CPU/mem sizes with observed utilization on every DOWN step.
"""


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
                "**lowest cost_score** (replicas × CPU/mem requests). Scale CPU, memory, and replicas "
                "from observed metrics (same PASS rules as DOWN: p95 ≤ SLO, error_rate ≤ SLO, "
                "cpu_util ≤ 95% when telemetry is trustworthy). At most one replica step per iteration. "
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
        slo = experiment_json.get("slo") or {}
        p95 = float((obs.get("latency_ms") or {}).get("p95") or 0)
        slo_p95 = float(slo.get("p95_latency_ms") or 500)
        parts.append(
            "\nUP recovery (cost-aware): scaling_hint=UP — grow capacity until SLO passes, "
            "but minimize provisioned cost_score.\n"
            "- **Multi-axis UP** (like DOWN multi-axis): in one iteration you may raise CPU requests/limits, "
            "memory requests/limits, and spec.replicas + hpa maxReplicas together when metrics justify it.\n"
            "- Raise **memory at least as much as CPU** when mem_util_pct is above 100%; set limits "
            "~1.5–2× requests.\n"
            "- Add **at most one** replica per iteration when at a single-pod baseline and achieved RPS is "
            "≥85% of workload target (including under memory/CPU saturation).\n"
            "- PASS requires p95 ≤ slo.p95_latency_ms, error_rate ≤ slo.error_rate, and (when telemetry "
            "is trustworthy) cpu_util_pct ≤ 95% — same frontier as the DOWN squeeze demos.\n"
            "- Never scale DOWN while failure.failed is true.\n"
            f"- Current: deployment_replicas={dep_rep}, hpa max={hpa_max}, live={live_rep}, "
            f"p95={p95:.0f}ms vs slo={slo_p95:.0f}ms, single_pod={at_single_pod}.\n"
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
        replica_ok = (cpu_m > 0 and cpu_m <= ceiling) or streak >= min_passes
        if replica_ok and prev_axis != "replica":
            phase = (
                "Phase 2: replica DOWN is allowed this iteration if metrics support it; "
                "still trim CPU/memory when headroom exists."
            )
        elif prev_axis == "replica":
            phase = (
                "Phase 2: previous axis was replica — cut CPU/memory only; "
                "do not lower spec.replicas."
            )
        else:
            phase = (
                f"Phase 1: hold replicas (cpu_request_m={cpu_m}, "
                f"resource_pass_streak={streak}); aggressively reduce CPU/memory toward "
                "~55–65% utilization before any replica cut."
            )
        parts.append(
            f"\nDOWN strategy: previous squeeze_down_axis={prev_axis}, "
            f"resource_pass_streak={streak}. {phase} "
            "Never lower replicas two PASS iterations in a row.\n"
        )
        obs = experiment_json.get("observed") or {}
        dep_rep = int(cfg.get("deployment_replicas") or 0)
        live_rep = int(obs.get("replicas") or 0)
        live_max = int(obs.get("replicas_max") or 0)
        live_for_step = max(live_rep, live_max) if live_rep > 0 else live_max
        if live_for_step > 1 and replica_ok and prev_axis != "replica":
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
