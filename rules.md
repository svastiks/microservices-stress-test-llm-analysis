# Squeeze compare validation rules

**Agents: read this before judging any compare run or `comparison.md`. Use as pass/fail checklist.**

## Perfect run (must pass all — per round)

- **Independent arms** — Default: each arm measures its own iter 1 after baseline reset + iter-1 YAML restore. Row 1 **will differ** in burn/cpu% (different measure windows) — that is expected; do not use row 1 as a side-by-side fairness test.

- **Ach RPS = target** — Every iteration: `achieved_requests_per_second` = target RPS (e.g. 25 / 35 / 45). Any shortfall = invalid run.

- **Request-% gate only** — PASS/FAIL uses `cpu_util_request_pct` @ 95%; `telemetry.utilization_trustworthy` true on cpu FAIL rows. Limit-based `cpu_util_pct` is diagnostic only.

- **Both arms `first_fail`** — `stopped_reason=first_fail`, `first_fail_dir` set, ≥1 FAIL row each arm. `empty_recommended_diff` with zero FAIL = invalid.

- **Advanced wins cost** — LLM `best_pass` prov cost **<** formula `best_pass` prov cost. Formula winning = investigate (not deck-ready).

- **No early-stop bugs** — No `guard.hot_boundary_stop` in `analysis.json`; iter-2 applied iter-1 step (`deployment-recommended.yaml` on disk; measured replicas/resources match recommendation).

- **SLO held until FAIL** — FAIL rows should be `cpu_utilization_exceeded` with p95 still within SLO (expected DOWN physics at fixed RPS).

## UP telemetry bug (investigate before archive)

- **Near-matched config paradox** — Similar resources (~65–71m cpu, ~29–37Mi, same repl) must not show ~60%+ `cpu_util_request_pct` gap (e.g. 144% vs 88%) at same RPS without explanation. That indicates **burn** divergence (`cpu_usage_avg_m` e.g. 205m vs 115m), not just request-denominator math.

- **Root cause unknown until replay** — Independent sequential arms measure at different times; suspected causes: extra traffic to web pods, dependency/cache warmth, Prometheus window/pod attribution. **Required:** matched-config replay (same YAML, back-to-back k6) before trusting compare rows.

- **Do not cite paradox rows as proof** — Zippered table row N ≠ same config; opposite PASS/FAIL at near-matched resources = open bug until replay passes.

## Warnings (run still usable)

- **Row-1 burn mismatch** — Normal in independent mode; judge the run on `best_pass` + boundaries, not row 1.

- **Iteration count mismatch** — Different iter counts per arm OK; `—` rows are not paired.

- **Rows ≠ matched configs** — Combined table is zippered trajectories; row N formula ≠ row N llm. Opposite PASS/FAIL at same index is normal.

## Optional paired iter-1 (`SQUEEZE_COMPARE_PAIRED_MEASURE=1`)

- One shared k6 window at baseline; row 1 forced to match (diagnostic / deck row-1 only).
- Does not pair iter 2+; does not change `best_pass` race.
- Probe jitter in `paired-baseline-probe.md` is warning only.

## RPS ladder expectations (25 / 35 / 45 DOWN)

- **@25** — Baseline 150/75/5; both arms squeeze ~4–8 iters; boundary ~70–90m cpu × 3–4 repl; LLM win ~5–20% prov cost typical.

- **@35** — Leaner boundary than @25; may FAIL sooner; configs lower than @25 best_pass.

- **@45** — Tightest boundary; formula often hits cpu% req gate fast; LLM should still win cost.

- **Cross-RPS** — Higher RPS → lower absolute resources at best_pass.

## Deck / archive bar (full sweep)

- **3 RPS rounds** — 25 + 35 + 45.

- **All 3 pass perfect-run checklist** — Each round independently valid.

- **LLM wins all 3 on `best_pass`** — Required for `GOOD_COST_WIN` archive under `artifacts_latest/`.

- **Post-fix image only** — Runs before `deployment-recommended.yaml` arm restore (≈ before `compare-sweep-20260608-151017`) are case studies only.

## Disqualifiers (do not archive)

- Pre-fix `artifacts/` runs (limit-only gate).

- Concurrent analyzer jobs on PVC (stale/wrong RPS in boundary).

- All-PASS either arm on DOWN until-violation.

- Vanilla DOWN with no FAIL (vanilla-specific).

- `utilization_trustworthy: false` on a cpu-gate FAIL used as boundary.

- **UP near-matched burn mismatch** — replay not run or replay shows >15% burn/cpu% drift at same YAML.

## Telemetry notes

- **Burn** = `cpu_usage_avg_m` (mean Prometheus aggregate over k6 window).

- **Utilization** = k6-window mean; `*_peak` for burst diagnostics.

- **Limit ratio** — Formula ~2× limit:request; LLM wider; never compare raw limit `cpu_util_pct` across arms.

- **Sequential arms** — Formula then LLM in one job; each arm: baseline reset + iter-1 YAML restore before subprocess.
