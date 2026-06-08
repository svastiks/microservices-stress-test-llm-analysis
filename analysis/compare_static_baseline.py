"""Compare static baseline (single experiment.json) vs LLM squeeze boundary."""

from __future__ import annotations

import json
from pathlib import Path

from analysis.compare_squeeze_methods import compare
from analysis.cost_model import row_util_cost


def _display_path(path: str | Path, *, base: Path | None = None) -> str:
    p = Path(path)
    for root in (base, Path.cwd()):
        if root is None:
            continue
        try:
            return str(p.relative_to(root.resolve()))
        except ValueError:
            continue
    return str(p)


def experiment_to_boundary_row(exp: dict, *, run_dir: str) -> dict:
    obs = exp.get("observed") or {}
    cfg = exp.get("config") or {}
    wl = exp.get("workload") or {}
    fail = exp.get("failure") or {}
    cost = exp.get("cost") or {}
    lat = obs.get("latency_ms") or {}
    status = "FAIL" if fail.get("failed") else "PASS"
    row = {
        "run_dir": run_dir,
        "status": status,
        "target_rps": wl.get("target_requests_per_second"),
        "achieved_rps": obs.get("achieved_requests_per_second"),
        "achieved_rps_target_window": obs.get("achieved_requests_per_second_target_window"),
        "dropped_iterations": obs.get("dropped_iterations"),
        "p95_ms": lat.get("p95"),
        "error_rate": obs.get("error_rate"),
        "cpu_util_pct": obs.get("cpu_util_pct"),
        "mem_util_pct": obs.get("mem_util_pct"),
        "replicas": obs.get("replicas"),
        "cpu_request_m": cfg.get("cpu_request_m"),
        "mem_request_mib": cfg.get("mem_request_mib"),
        "cpu_limit_m": cfg.get("cpu_limit_m"),
        "mem_limit_mib": cfg.get("mem_limit_mib"),
        "cost_score": cost.get("cost_score"),
        "cost_score_util": cost.get("cost_score_util"),
    }
    if row["cost_score_util"] is None:
        row["cost_score_util"] = row_util_cost(row)
    return row


def experiment_to_boundary(exp_path: Path) -> dict:
    exp = json.loads(exp_path.read_text())
    run_dir = str(exp_path.parent.resolve())
    row = experiment_to_boundary_row(exp, run_dir=run_dir)
    cost = exp.get("cost") or {}
    best_pass = row["cost_score"] if row["status"] == "PASS" else None
    best_pass_util = row.get("cost_score_util") if row["status"] == "PASS" else None
    return {
        "stopped_reason": "single_pass_no_apply_loop",
        "best_pass_dir": run_dir if row["status"] == "PASS" else None,
        "first_fail_dir": run_dir if row["status"] == "FAIL" else None,
        "rows": [row],
        "squeeze_optimizer": "static_baseline",
        "cost_model": cost.get("cost_model") or "weighted",
        "cost_best_pass_score": best_pass,
        "cost_best_pass_score_util": best_pass_util,
    }


def compare_engineer_vs_advanced(
    engineer_experiment: Path,
    advanced_boundary: Path,
    *,
    scenario: str = "up_demo",
    rps: int | None = None,
    engineer_data: str | None = None,
    advanced_data: str | None = None,
) -> str:
    """Engineer B1 (single experiment.json) vs advanced-llm squeeze boundary."""
    text = compare_static_vs_llm(
        engineer_experiment,
        advanced_boundary,
        label_static="engineer",
        label_llm="advanced-llm",
        rps=rps,
        scenario=scenario,
        static_sweep=engineer_data,
        llm_sweep=advanced_data,
    )
    return text.replace(
        "# Static baseline vs LLM squeeze comparison",
        "# Engineer baseline vs advanced LLM squeeze comparison",
        1,
    ).replace(
        "- **Static**: thin deployment YAML + HPA (1–5 replicas); one k6 pass; no squeeze apply loop.",
        (
            f"- **Engineer (B1)**: fat deployment "
            f"(`robot-shop-web-deployment.baseline.yaml`: 5×150m/75Mi) + HPA; "
            f"one k6 pass at fixed RPS; no squeeze (`{scenario}`)."
        ),
        1,
    ).replace(
        "- **LLM**: iterative squeeze until SLO-safe minimum cost (`cost-effective-boundary.json`).",
        "- **Advanced LLM**: iterative squeeze with full telemetry + guards (`cost-effective-boundary.json`).",
        1,
    )


def compare_static_vs_llm(
    static_experiment: Path,
    llm_boundary: Path,
    *,
    label_static: str = "static",
    label_llm: str = "llm",
    rps: int | None = None,
    scenario: str = "up_demo",
    static_sweep: str | None = None,
    llm_sweep: str | None = None,
) -> str:
    """Build comparison markdown; writes temp boundary for static side in-memory via compare()."""
    import tempfile

    static_boundary = experiment_to_boundary(static_experiment)
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as tf:
        json.dump(static_boundary, tf, indent=2)
        tmp = Path(tf.name)
    try:
        body = compare(
            tmp,
            llm_boundary,
            label_a=label_static,
            label_b=label_llm,
        )
    finally:
        tmp.unlink(missing_ok=True)

    header = ["# Static baseline vs LLM squeeze comparison", ""]
    if rps is not None:
        header.append(f"- **Target RPS**: {rps} (`{scenario}`)")
    header.append(
        "- **Static**: thin deployment YAML + HPA (1–5 replicas); one k6 pass; no squeeze apply loop."
    )
    header.append(
        "- **LLM**: iterative squeeze until SLO-safe minimum cost (`cost-effective-boundary.json`)."
    )
    if static_sweep:
        header.append(f"- **Static data**: `{_display_path(static_sweep)}`")
    if llm_sweep:
        header.append(f"- **LLM data**: `{_display_path(llm_sweep)}`")
    header.extend(["", "---", ""])
    return "\n".join(header) + body.replace(
        "# Squeeze optimizer comparison",
        "## Details (squeeze-style table)",
        1,
    )


def best_pass_row(boundary: dict) -> dict | None:
    for row in reversed(boundary.get("rows") or []):
        if row.get("status") == "PASS":
            return row
    return None


def summary_table_row(
    rps: int,
    static_exp_path: Path,
    llm_boundary_path: Path,
    *,
    llm_note: str = "",
) -> str:
    exp = json.loads(static_exp_path.read_text())
    srow = experiment_to_boundary_row(exp, run_dir=str(static_exp_path.parent))
    lb = json.loads(llm_boundary_path.read_text())
    lrow = best_pass_row(lb)
    s_status = srow["status"]
    l_status = lrow["status"] if lrow else "—"
    s_status_cell = "🟥 FAIL" if s_status == "FAIL" else "🟩 PASS"
    l_status_cell = (
        "🟩 PASS" if l_status == "PASS" else ("🟥 FAIL" if l_status == "FAIL" else "—")
    )
    note = f" ({llm_note})" if llm_note else ""
    return (
        f"| {rps} | {s_status_cell} | {srow.get('p95_ms')} | {srow.get('achieved_rps')} | "
        f"{l_status_cell}{note} | {(lrow or {}).get('p95_ms', '—')} | "
        f"{(lrow or {}).get('achieved_rps_target_window', '—')} | {len(lb.get('rows') or [])} |"
    )


def summary_table_row_resources(
    rps: int,
    static_exp_path: Path,
    llm_boundary_path: Path,
) -> str:
    exp = json.loads(static_exp_path.read_text())
    srow = experiment_to_boundary_row(exp, run_dir=str(static_exp_path.parent))
    lb = json.loads(llm_boundary_path.read_text())
    lrow = best_pass_row(lb)
    return (
        f"| {rps} | {srow.get('cpu_request_m')} | {srow.get('mem_request_mib')} | "
        f"{srow.get('cpu_limit_m')} | {srow.get('mem_limit_mib')} | {srow.get('replicas')} | "
        f"{srow.get('cost_score')} | {srow.get('cost_score_util')} | "
        f"{(lrow or {}).get('cpu_request_m', '—')} | {(lrow or {}).get('mem_request_mib', '—')} | "
        f"{(lrow or {}).get('cpu_limit_m', '—')} | {(lrow or {}).get('mem_limit_mib', '—')} | "
        f"{(lrow or {}).get('replicas', '—')} | {(lrow or {}).get('cost_score', '—')} | "
        f"{row_util_cost(lrow) if lrow else '—'} |"
    )


def summary_winner_row(
    rps: int,
    static_exp_path: Path,
    llm_boundary_path: Path,
) -> str:
    exp = json.loads(static_exp_path.read_text())
    srow = experiment_to_boundary_row(exp, run_dir=str(static_exp_path.parent))
    lb = json.loads(llm_boundary_path.read_text())
    lrow = best_pass_row(lb)
    s_pass = srow.get("status") == "PASS"
    l_pass = bool(lrow and lrow.get("status") == "PASS")
    s_prov = srow.get("cost_score")
    s_util = srow.get("cost_score_util")
    l_prov = (lrow or {}).get("cost_score")
    l_util = row_util_cost(lrow) if lrow else None

    winner = "Tie"
    reason = "both failed"
    if l_pass and not s_pass:
        winner = "LLM"
        reason = (
            f"SLO pass (p95 {lrow.get('p95_ms')} ms) vs static fail (p95 {srow.get('p95_ms')} ms)"
        )
    elif s_pass and not l_pass:
        winner = "Static"
        reason = (
            f"SLO pass (p95 {srow.get('p95_ms')} ms) vs LLM fail"
        )
    elif s_pass and l_pass:
        if l_util is not None and s_util is not None and l_util < s_util:
            winner = "LLM"
            reason = f"both pass; lower util cost ({l_util} < {s_util})"
        elif l_util is not None and s_util is not None and l_util > s_util:
            winner = "Static"
            reason = f"both pass; lower util cost ({s_util} < {l_util})"
        else:
            winner = "Tie"
            reason = "both pass; util cost tie/unknown"

    cost_outcome = "unknown"
    if l_prov is not None and s_prov is not None and l_util is not None and s_util is not None:
        prov_cmp = (
            f"LLM lower prov ({l_prov} < {s_prov})"
            if l_prov < s_prov
            else (
                f"LLM higher prov ({l_prov} > {s_prov})"
                if l_prov > s_prov
                else f"prov tie ({l_prov})"
            )
        )
        util_cmp = (
            f"LLM lower util ({l_util} < {s_util})"
            if l_util < s_util
            else (
                f"LLM higher util ({l_util} > {s_util})"
                if l_util > s_util
                else f"util tie ({l_util})"
            )
        )
        cost_outcome = f"{prov_cmp}; {util_cmp}"

    return f"| {rps} | {winner} | {reason} | {cost_outcome} |"


def build_summary(
    pairs: list[tuple[int, Path, Path, str]],
    *,
    static_sweep_root: Path | str,
    llm_sweep_primary: str,
) -> str:
    static_root = _display_path(static_sweep_root)
    lines = [
        "# UP demo: static baseline vs LLM (showcase)",
        "",
        f"- **Static sweep**: `{static_root}`",
        f"- **Primary LLM compare**: `{llm_sweep_primary}` (RPS 220–260)",
        "- **280 LLM**: `showcase_UP/compare-up-sweep-20260525-010051/run-1` (same profile; separate sweep)",
        "",
        "## Headline table (performance)",
        "",
        "| RPS | static status | static p95 ms | static achieved RPS | llm status | llm p95 ms | llm achieved RPS | llm iterations |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for rps, static_p, llm_p, note in pairs:
        lines.append(
            summary_table_row(rps, static_p, llm_p, llm_note=note)
        )
    lines.extend(
        [
            "",
            "## Resources and cost (static vs LLM best PASS)",
            "",
            "| RPS | static cpu m | static mem Mi | static cpu limit m | static mem limit Mi | static replicas | static prov cost | static util cost | "
            "llm cpu m | llm mem Mi | llm cpu limit m | llm mem limit Mi | llm replicas | llm prov cost | llm util cost |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for rps, static_p, llm_p, _ in pairs:
        lines.append(summary_table_row_resources(rps, static_p, llm_p))
    lines.extend(
        [
            "",
            "## Winner per load",
            "",
            "| RPS | Winner | Metric used | Cost outcome |",
            "| --- | --- | --- | --- |",
        ]
    )
    for rps, static_p, llm_p, _ in pairs:
        lines.append(summary_winner_row(rps, static_p, llm_p))
    lines.extend(
        [
            "",
            "## Data sources used for this table",
            "",
        ]
    )
    for rps, static_p, llm_p, note in pairs:
        note_suffix = f" ({note})" if note else ""
        lines.append(
            f"- **RPS {rps}{note_suffix}**: static=`{_display_path(static_p)}` · llm=`{_display_path(llm_p)}`"
        )
    lines.extend(
        [
            "",
            "## Per-RPS comparison files",
            "",
            "Under the static sweep, each `run-N/comparison.md` is static vs LLM for that RPS.",
            "Mirrored as `comparison-static.md` under the matching showcase compare run.",
            "",
        ]
    )
    return "\n".join(lines) + "\n"
