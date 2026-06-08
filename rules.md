# Squeeze run validation rules

**Agents: read this before judging any compare run or `comparison.md`.**

- **Advanced must win on cost** — Formula vs advanced compare is invalid for showcase/deck unless advanced `best_pass` prov cost < formula; formula winning = rerun or investigate (UP @ 200/220/240 failed this bar).

- **Gate on request cpu%** — PASS/FAIL must use `cpu_util_request_pct`; limit-based `cpu_util_pct` alone is unfair across optimizers.

- **Rows are not matched configs** — Combined table aligns iteration index only; row N formula ≠ row N llm.

- **Opposite PASS/FAIL expected** — Same-index status mismatch is normal; do not treat as measurement contradiction.

- **Strict resource paradox rare** — Flag only when PASS side has ≤ cpu, ≤ mem, ≤ repl vs FAIL at same index.

- **Advanced DOWN needs first_fail** — `stopped_reason=empty_recommended_diff` with zero FAIL rows invalidates advanced arm.

- **Vanilla DOWN should first_fail** — Vanilla must end with at least one FAIL; all-PASS vanilla DOWN is broken.

- **Both arms need stopped_reason** — Compare `first_fail` vs `empty_recommended_diff` per arm before calling winner.

- **Check hot_boundary_stop evidence** — `guard.hot_boundary_stop` in `analysis.json` means advanced stopped early.

- **cpu fail p95 pass suspicious** — `cpu_utilization_exceeded` with p95 within SLO often means limit-ratio telemetry bug.

- **Limit ratio skews cpu%** — Formula ~2× limit:request; llm up to 12×; do not compare raw cpu% across arms.

- **Utilization is k6-window mean** — `cpu_util_request_pct` / `mem_util_pct` are mean samples over the k6 run (not padded-window max). `*_peak` fields keep window max for burst diagnostics.

- **best_pass valid row table weak** — Headline `best_pass` prov cost can be OK while row-by-row table misleads.

- **Iteration count mismatch OK** — Different iteration counts per arm expected; missing `—` rows are not paired tests.

- **Sequential arms same cluster** — Formula/advanced runs before llm/vanilla; note order bias on reruns.

- **One analyzer job on PVC** — Never run stress-analyzer-down-demo and stress-analyzer-up-demo concurrently; stale job overwrites boundary JSON (formula row shows wrong RPS).

- **Achieved RPS must match target** — If `ach RPS` ≪ target RPS, run is invalid regardless of PASS.

- **utilization_trustworthy required for cpu gate** — No cpu-util FAIL when `telemetry.utilization_trustworthy` is false.

- **Until violation needs real FAIL** — DOWN compare with `SQUEEZE_UNTIL_VIOLATION=1` must record `first_fail_dir`.

- **Empty diff needs probe fallback** — `SQUEEZE_UNTIL_VIOLATION_PROBE_LLM=1` when LLM returns empty `recommended.diff`.

- **Rebuild image after telemetry fixes** — Old artifact runs pre-fix are case studies only, not deck numbers.
