"""Replay a source squeeze trajectory (same configs, observe-only) and compare metrics."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _boundary_path(source: Path) -> Path:
    if source.is_file() and source.name.endswith(".json"):
        return source
    candidate = source / "cost-effective-boundary.json"
    if candidate.is_file():
        return candidate
    raise FileNotFoundError(f"No cost-effective-boundary.json under {source}")


def load_boundary_rows(source: Path) -> tuple[Path, list[dict[str, Any]]]:
    path = _boundary_path(source)
    data = json.loads(path.read_text())
    rows = data.get("rows") or []
    if not rows:
        raise ValueError(f"No rows in {path}")
    return path.parent, rows


def load_iteration_config(source_run: Path, iteration: int, row: dict[str, Any]) -> dict:
    exp_path = source_run / f"iteration-{iteration}" / "experiment.json"
    if exp_path.is_file():
        exp = json.loads(exp_path.read_text())
        cfg = exp.get("config")
        if isinstance(cfg, dict) and cfg.get("cpu_request_m"):
            return cfg
    hpa_min = int(row.get("hpa_min_replicas") or row.get("replicas") or 1)
    hpa_max = int(row.get("hpa_max_replicas") or row.get("replicas") or hpa_min)
    return {
        "cpu_request_m": int(row.get("cpu_request_m") or 0),
        "cpu_limit_m": int(row.get("cpu_limit_m") or 0),
        "mem_request_mib": int(row.get("mem_request_mib") or 0),
        "mem_limit_mib": int(row.get("mem_limit_mib") or 0),
        "deployment_replicas": int(row.get("replicas") or 1),
        "hpa": {
            "min_replicas": hpa_min,
            "max_replicas": hpa_max,
            "target_cpu_util_pct": int(row.get("hpa_target_cpu_util_pct") or 60),
        },
    }


def _fmt(v: Any) -> str:
    if v is None:
        return "—"
    if isinstance(v, float):
        return f"{v:.4g}"
    return str(v)


def _status_from_row(row: dict[str, Any]) -> str:
    return str(row.get("status") or "—")


def config_key(row: dict[str, Any]) -> str:
    return (
        f"{int(row.get('cpu_request_m') or 0)}/"
        f"{int(row.get('mem_request_mib') or 0)}/"
        f"{int(row.get('replicas') or 0)}"
    )


def _rows_by_config(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        out[config_key(row)] = row
    return out


def compare_trajectories(
    source_rows: list[dict[str, Any]],
    replay_rows: list[dict[str, Any]],
    *,
    source_label: str = "source",
    replay_label: str = "replay",
) -> str:
    """Markdown: per-iteration config replay comparison (same YAML, two k6 runs)."""
    lines = [
        "# Trajectory replay validation",
        "",
        "Each row re-applies the **same** deployment config from the source run, "
        "then runs k6 again (observe-only). Compares whether burn, cpu% req, and PASS/FAIL align.",
        "",
        f"| # | config (cpu/mem/repl) | {source_label} status | {replay_label} status | "
        f"match | {source_label} burn | {replay_label} burn | Δ burn | "
        f"{source_label} cpu% req | {replay_label} cpu% req | Δ cpu% | "
        f"{source_label} mem% | {replay_label} mem% | repl |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    n = max(len(source_rows), len(replay_rows))
    status_matches = 0
    for i in range(n):
        src = source_rows[i] if i < len(source_rows) else {}
        rep = replay_rows[i] if i < len(replay_rows) else {}
        cfg = (
            f"{_fmt(src.get('cpu_request_m'))}/{_fmt(src.get('mem_request_mib'))}/"
            f"{_fmt(src.get('replicas'))}"
        )
        s_status = _status_from_row(src)
        r_status = _status_from_row(rep)
        match = s_status == r_status and s_status != "—"
        if match:
            status_matches += 1
        sb = float(src.get("cpu_usage_avg_m") or 0)
        rb = float(rep.get("cpu_usage_avg_m") or 0)
        sc = float(src.get("cpu_util_request_pct") or 0)
        rc = float(rep.get("cpu_util_request_pct") or 0)
        sm = float(src.get("mem_util_pct") or 0)
        rm = float(rep.get("mem_util_pct") or 0)
        repl = _fmt(src.get("replicas") or rep.get("replicas"))
        lines.append(
            f"| {i + 1} | {cfg} | {s_status} | {r_status} | "
            f"{'yes' if match else 'no'} | {_fmt(sb)} | {_fmt(rb)} | {_fmt(rb - sb)} | "
            f"{_fmt(sc)} | {_fmt(rc)} | {_fmt(rc - sc)} | "
            f"{_fmt(sm)} | {_fmt(rm)} | {repl} |"
        )
    compared = min(len(source_rows), len(replay_rows))
    lines.extend(
        [
            "",
            f"**Status match:** {status_matches}/{compared} iterations "
            f"(Δ burn/cpu% should be small if the theory holds; large Δ ⇒ run variance or measurement).",
        ]
    )
    return "\n".join(lines) + "\n"


def write_replay_comparison(
    source: Path,
    replay_run: Path,
    out_path: Path | None = None,
    *,
    source_label: str = "source",
    replay_label: str = "replay",
) -> Path:
    _, source_rows = load_boundary_rows(source)
    _, replay_rows = load_boundary_rows(replay_run)
    md = compare_trajectories(
        source_rows, replay_rows, source_label=source_label, replay_label=replay_label
    )
    dest = out_path or (replay_run.parent / "replay-comparison.md")
    dest.write_text(md)
    return dest


def compare_matched_configs(
    formula_source: list[dict[str, Any]],
    formula_replay: list[dict[str, Any]],
    llm_source: list[dict[str, Any]],
    llm_replay: list[dict[str, Any]],
) -> str:
    """Per unique config: original vs replay for each arm (fair compare at same YAML)."""
    keys = sorted(
        set(_rows_by_config(formula_source))
        | set(_rows_by_config(formula_replay))
        | set(_rows_by_config(llm_source))
        | set(_rows_by_config(llm_replay))
    )
    fs, fr, ls, lr = (
        _rows_by_config(formula_source),
        _rows_by_config(formula_replay),
        _rows_by_config(llm_source),
        _rows_by_config(llm_replay),
    )
    lines = [
        "# Matched-config replay (formula vs LLM at same YAML)",
        "",
        "Each row is one **config** (cpu/mem/replicas). "
        "Shows whether each arm measured similarly on the **same** setup, "
        "and whether a replay k6 run agrees with the original.",
        "",
        "| config | in formula | in llm | f orig status | f replay status | "
        "f orig cpu% | f replay cpu% | f orig burn | f replay burn | "
        "l orig status | l replay status | l orig cpu% | l replay cpu% | "
        "l orig burn | l replay burn | f replay match | l replay match |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | "
        "--- | --- | --- | --- | --- | --- | --- | --- |",
    ]

    def _cell(row: dict[str, Any] | None, field: str) -> str:
        if not row:
            return "—"
        return _fmt(row.get(field))

    def _status_match(orig: dict[str, Any] | None, rep: dict[str, Any] | None) -> str:
        if not orig or not rep:
            return "—"
        o, r = _status_from_row(orig), _status_from_row(rep)
        return "yes" if o == r and o != "—" else "no"

    for key in keys:
        fo, frep = fs.get(key), fr.get(key)
        lo, lrep = ls.get(key), lr.get(key)
        lines.append(
            f"| {key} | {'yes' if fo or frep else '—'} | {'yes' if lo or lrep else '—'} | "
            f"{_cell(fo, 'status')} | {_cell(frep, 'status')} | "
            f"{_cell(fo, 'cpu_util_request_pct')} | {_cell(frep, 'cpu_util_request_pct')} | "
            f"{_cell(fo, 'cpu_usage_avg_m')} | {_cell(frep, 'cpu_usage_avg_m')} | "
            f"{_cell(lo, 'status')} | {_cell(lrep, 'status')} | "
            f"{_cell(lo, 'cpu_util_request_pct')} | {_cell(lrep, 'cpu_util_request_pct')} | "
            f"{_cell(lo, 'cpu_usage_avg_m')} | {_cell(lrep, 'cpu_usage_avg_m')} | "
            f"{_status_match(fo, frep)} | {_status_match(lo, lrep)} |"
        )
    both = [k for k in keys if k in fs and k in ls]
    lines.extend(
        [
            "",
            f"**Configs tested by both arms (original compare):** {len(both)} "
            f"({', '.join(both) if both else 'none'})",
        ]
    )
    return "\n".join(lines) + "\n"


def write_compare_artifact_replay_bundle(
    artifact_root: Path,
    formula_replay_run: Path,
    llm_replay_run: Path,
    out_dir: Path | None = None,
) -> Path:
    """Write formula replay, llm replay, and matched-config markdown under out_dir."""
    formula_src = artifact_root / "formula-run"
    llm_src = artifact_root / "llm-run"
    dest = out_dir or artifact_root
    dest.mkdir(parents=True, exist_ok=True)

    write_replay_comparison(
        formula_src,
        formula_replay_run,
        dest / "formula-replay-comparison.md",
        source_label="formula orig",
        replay_label="formula replay",
    )
    write_replay_comparison(
        llm_src,
        llm_replay_run,
        dest / "llm-replay-comparison.md",
        source_label="llm orig",
        replay_label="llm replay",
    )
    _, f_src_rows = load_boundary_rows(formula_src)
    _, f_rep_rows = load_boundary_rows(formula_replay_run)
    _, l_src_rows = load_boundary_rows(llm_src)
    _, l_rep_rows = load_boundary_rows(llm_replay_run)
    matched = compare_matched_configs(f_src_rows, f_rep_rows, l_src_rows, l_rep_rows)
    matched_path = dest / "matched-config-replay.md"
    matched_path.write_text(matched)
    return matched_path
