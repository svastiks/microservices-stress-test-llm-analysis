# Compare run checkpoint — code state & commands

**Purpose:** Remember exactly what code + env produced the trusted DOWN run, so the next UP run can be fixed deliberately and re-run without guessing.

**Last updated:** 2026-06-08

---

## Trusted reference run (DOWN @25)

| Field | Value |
|---|---|
| Sweep | `compare-sweep-20260608-164035` |
| Local path | `results-from-cluster/compare-sweep-20260608-164035/run-1/` |
| Archive | `artifacts_latest/FORMULA_VS_ADVANCED_LLM/DOWN/GOOD_COST_WIN_run-1-rps25-20260608-164035/` |
| Git at run time | `6c1a09c` (HEAD when checkpoint written) |
| Verdict | PASS per `rules.md` — independent arms, both `first_fail`, LLM wins `best_pass` |

### Numbers (why we trust it)

- **formula** `best_pass` iter-4: **75m / 38Mi × 4 repl**, prov cost **0.2848**, `stopped_reason=first_fail`
- **llm** `best_pass` iter-5: **97m / 45Mi × 3 repl**, prov cost **0.2751**, `stopped_reason=first_fail`
- Iter-1 row mismatch expected (independent measure): formula cpu% **52.1** vs llm **44.3**
- LLM iter-2 applied iter-1 step (**4 repl**); no `hot_boundary_stop`

### Exact command used

```bash
BUILD_ANALYZER_IMAGE=true \
KUBE_CONTEXT=monitoring \
COMPARE_SWEEP_K6_DURATION=90s \
COMPARE_SWEEP_RPS=25 \
COMPARE_SWEEP_ROUNDS=1 \
SQUEEZE_SETTLE_SECONDS=30 \
SQUEEZE_WARMUP_K6_DURATION=60s \
./scripts/run_down_demo_compare_sweep.sh
```

### Env from `sweep-round-1.txt`

- `PROFILES_CSV=down_demo`
- `STRESS_K6_RPS=25`, `STRESS_K6_DURATION=90s`
- `SQUEEZE_UNTIL_VIOLATION=true`
- `SQUEEZE_COMPARE_FORMULA_UNTIL_VIOLATION=1`
- `SQUEEZE_COMPARE_PAIRED_MEASURE` **unset** → default **off** (`0`)

---

## Code features active for 164035 (do not regress)

These are in the repo at `6c1a09c`. They are what made iter 2+ fair and burn trustworthy.

### 1. Independent arms (default)

- `SQUEEZE_COMPARE_PAIRED_MEASURE` defaults to **`0`** in `analysis/compare_shared_measure.py`
- Each arm measures its own iter-1 after baseline reset; row 1 **will** differ — judge on `best_pass`, not row 1
- Optional deck-only pairing: `SQUEEZE_COMPARE_PAIRED_MEASURE=1` (was ON for older run `151017`, not used for 164035)

### 2. Iter-1 YAML restore before each arm subprocess

- `start.py` → `_prepare_compare_arm_subprocess()`: baseline reset, then restore `deployment-recommended.yaml` + `hpa-recommended.yaml` from iter-1 on disk
- `analysis/compare_shared_measure.py` → `restore_compare_arm_iter1_yaml()`
- Without this, iter-2+ starts from repo baseline only → wrong trajectory (pre-fix bug)

### 3. Per-iteration YAML snapshots on write

- `analysis/results.py` → `write_outputs` saves `deployment-measured.yaml`, `deployment-recommended.yaml`, `hpa-measured.yaml`, `hpa-recommended.yaml`
- Reanalyze can reload frozen canonical when paired mode was used (`shared_canonical_experiment.json`)

### 4. CPU gate & DOWN formula behavior (earlier fixes, still in effect)

- PASS/FAIL on `cpu_util_request_pct` @ 95% (`SQUEEZE_CPU_UTIL_FAIL_PCT`)
- Formula multi-axis DOWN squeeze (not limit-only plateau)
- LLM/HPA replica cap on DOWN
- `start.py` no-progress stop when config unchanged

### 5. Compare hygiene

- Sequential arms: formula then LLM in one job
- `SQUEEZE_COMPARE_PRUNE_PRIOR=1`, `SQUEEZE_COMPARE_CONTINUE_ON_FORMULA_FAIL=1`
- Validation rules: `rules.md`

### Key files to preserve / diff before next run

| File | Role |
|---|---|
| `start.py` | `_prepare_compare_arm_subprocess`, shared iter-1 (only when paired ON) |
| `analysis/compare_shared_measure.py` | paired default, yaml restore, probe helpers |
| `analysis/results.py` | frozen canonical, measured/recommended yaml snapshots |
| `scripts/run_down_demo_compare_sweep.sh` | DOWN sweep; `formula_uv=1` default |
| `scripts/lib/squeeze_*_env.sh` | profile-specific until-violation defaults |
| `rules.md` | pass/fail checklist |

---

## Weak UP run (for contrast — not archive-ready)

| Field | Value |
|---|---|
| Sweep | `compare-up-sweep-20260608-173204` |
| RPS | 220 |
| Verdict | Pipeline OK; **not** deck-ready |

### What went wrong (3-line evidence)

1. **Thin / divergent iter-1:** formula **192m** burn, p95 **3090**, **76** dropped iters vs llm **142m**, p95 **2043**, **23** dropped (~35 min apart, independent arms)
2. **Different stop semantics:** both `recovered_from_underprovisioning` (not `first_fail` — UP rules not written yet)
3. **Boundary gap:** llm `best_pass` iter-5 **70/29×3** (0.1975) vs formula iter-10 **163/90×2** (0.311)

### UP command used

```bash
COMPARE_SWEEP_RPS=220 \
COMPARE_SWEEP_ROUNDS=1 \
./scripts/run_up_demo_compare_sweep.sh
```

(`BUILD_ANALYZER_IMAGE=false` — image already built from DOWN run)

### Env delta vs DOWN (from `squeeze_up_demo_env.sh`)

| Env | DOWN (164035) | UP (173204) |
|---|---|---|
| `SQUEEZE_UNTIL_VIOLATION` | `true` | `false` |
| `SQUEEZE_COMPARE_FORMULA_UNTIL_VIOLATION` | `1` | `0` |
| `SQUEEZE_LLM_DOWN_BOUNDARY` | (down profile) | `0` |
| Stop reason | `first_fail` | `recovered_from_underprovisioning` |

Same compare code (yaml restore, paired OFF) — UP weakness is mostly **profile/optimizer UP logic**, not missing DOWN fixes.

---

## Before next UP run — checklist

**Keep from 164035 (do not remove):**

- [ ] `_prepare_compare_arm_subprocess` + recommended yaml snapshots
- [ ] `SQUEEZE_COMPARE_PAIRED_MEASURE` default `0` (unless you explicitly want row-1 deck alignment for UP)
- [ ] Request-% cpu gate, trustworthy telemetry on FAIL rows
- [ ] `BUILD_ANALYZER_IMAGE=true` if you changed analyzer code since last image build

**UP-specific changes to make (your branch):**

- [ ] Fix iter-1 underprovision baseline / k6 ramp so both arms see comparable load @220
- [ ] Decide UP stop semantics (`first_fail` vs `recovered_from_underprovisioning`) and document in `rules.md`
- [ ] Consider `SQUEEZE_COMPARE_PAIRED_MEASURE=1` for UP only if iter-1 fairness matters more than independent race
- [ ] Formula UP path: ensure it does not need 10 iters while LLM finishes in 5 with a much leaner boundary

**Re-run UP (after your fixes):**

```bash
BUILD_ANALYZER_IMAGE=true \
KUBE_CONTEXT=monitoring \
COMPARE_SWEEP_K6_DURATION=90s \
COMPARE_SWEEP_RPS=220 \
COMPARE_SWEEP_ROUNDS=1 \
SQUEEZE_SETTLE_SECONDS=30 \
SQUEEZE_WARMUP_K6_DURATION=60s \
./scripts/run_up_demo_compare_sweep.sh
```

**Then DOWN ladder (when ready):**

```bash
BUILD_ANALYZER_IMAGE=true \
KUBE_CONTEXT=monitoring \
COMPARE_SWEEP_K6_DURATION=90s \
COMPARE_SWEEP_RPS=25,35,45 \
COMPARE_SWEEP_ROUNDS=3 \
SQUEEZE_SETTLE_SECONDS=30 \
SQUEEZE_WARMUP_K6_DURATION=60s \
./scripts/run_down_demo_compare_sweep.sh
```

Deck bar: all 3 RPS rounds pass `rules.md` + LLM wins `best_pass` on each.

---

## Run history (quick reference)

| Sweep | Mode | Notes |
|---|---|---|
| `151017` | Paired iter-1 ON | Good row-1 alignment; superseded by independent model |
| `164035` | Independent | **Trusted DOWN @25** — archived |
| `173204` | Independent | UP @220 — weak, needs UP fixes |
| Pre-`151017` | No yaml restore | Case study only — do not archive |

---

## Notes for agents

When judging a new run, read `rules.md` first. This file is the **code/env snapshot** for reproducing 164035-style trust on DOWN; UP still needs profile-specific rules and optimizer fixes documented above.
