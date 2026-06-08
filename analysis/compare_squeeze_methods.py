"""Compare two squeeze runs (e.g. formula vs LLM) from cost-effective-boundary.json files."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from analysis.cost_model import row_util_cost


def _load_boundary(path: Path) -> dict:
    return json.loads(path.read_text())


def _iter_count(rows: list) -> int:
    return len(rows or [])


def _last_row(rows: list) -> dict | None:
    if not rows:
        return None
    return rows[-1]


# Heading-only: coloured block emoji next to title (visible in MD preview).
def _color_table_heading(label: str) -> str:
    """Prefix column title: grey=cost, green=cpu m, orange=mem Mi."""
    raw = label
    if "🟩" in label or "🟧" in label or "⬜" in label:
        for mark in ("🟩 ", "🟧 ", "⬜ "):
            if mark in label:
                raw = label.split(mark, 1)[-1]
                break
    if "<span" in raw:
        raw = re.sub(r"<[^>]+>", "", raw)
    low = raw.lower()
    if "prov cost" in low or "util cost" in low:
        block = "⬜"
    elif "cpu m" in low or "cpu req" in low:
        block = "🟩"
    elif "mem mi" in low or "mem req" in low:
        block = "🟧"
    else:
        return raw
    return f"{block} {raw}"


def _cell(r: dict | None, key: str) -> str:
    if not r:
        return "—"
    v = r.get(key)
    if v is None:
        return "—"
    if isinstance(v, bool):
        return str(v)
    if isinstance(v, float):
        return f"{v:.4g}"
    return str(v)


def _cpu_util_cell(r: dict | None) -> str:
    """Request-relative CPU util (HPA-aligned); fall back to limit-relative on old runs."""
    if not r:
        return "—"
    v = r.get("cpu_util_request_pct")
    if v is None:
        v = r.get("cpu_util_pct")
    if v is None:
        return "—"
    return f"{float(v):.4g}"


def compare(
    path_a: Path,
    path_b: Path,
    *,
    label_a: str = "method_a",
    label_b: str = "method_b",
) -> str:
    """Return Markdown: summary, deltas, and one combined iterations table."""
    da = _load_boundary(path_a)
    db = _load_boundary(path_b)
    ra, rb = da.get("rows") or [], db.get("rows") or []
    r0a, r0b = (ra[0] if ra else None), (rb[0] if rb else None)
    la, lb = _last_row(ra), _last_row(rb)

    def _delta(req_a, req_b):
        if req_a is None or req_b is None:
            return "n/a"
        try:
            return f"{float(req_b) - float(req_a):+.1f}"
        except (TypeError, ValueError):
            return "n/a"

    def _util_cell(r: dict | None) -> str:
        if not r:
            return "—"
        u = row_util_cost(r)
        return "—" if u is None else f"{u:.4g}"

    def _cost_line(d: dict, rows: list) -> str:
        parts: list[str] = []
        if d.get("cost_total") is not None:
            parts.append(
                f"prov_cost_total={d.get('cost_total')} (steady={d.get('cost_steady_state')}, "
                f"best_pass={d.get('cost_best_pass_score')})"
            )
        if d.get("cost_total_util") is not None:
            parts.append(
                f"util_cost_total={d.get('cost_total_util')} (steady={d.get('cost_steady_state_util')}, "
                f"best_pass={d.get('cost_best_pass_score_util')})"
            )
        elif rows:
            last_pass = next(
                (r for r in reversed(rows) if r.get("status") == "PASS"),
                None,
            )
            if last_pass:
                if last_pass.get("cost_score") is not None:
                    parts.append(f"best_pass_prov_cost={last_pass.get('cost_score')}")
                u = row_util_cost(last_pass)
                if u is not None:
                    parts.append(f"best_pass_util_cost={u}")
        return (" · " + ", ".join(parts)) if parts else ""

    lines: list[str] = [
        "# Squeeze optimizer comparison",
        "",
        "## Summary",
        "",
        f"- **Cost model**: `{da.get('cost_model') or db.get('cost_model') or 'weighted'}` (see cost_model.md) — "
        f"**prov cost** / **util cost**: same N×(p_cpu·r + p_mem·m); util uses effective r·u",
        "",
        f"- **{label_a}**: `optimizer={da.get('squeeze_optimizer')}` · `stopped_reason={da.get('stopped_reason')}` · "
        f"iterations={_iter_count(ra)} · `best_pass_dir={da.get('best_pass_dir')}`{_cost_line(da, ra)}",
        f"- **{label_b}**: `optimizer={db.get('squeeze_optimizer')}` · `stopped_reason={db.get('stopped_reason')}` · "
        f"iterations={_iter_count(rb)} · `best_pass_dir={db.get('best_pass_dir')}`{_cost_line(db, rb)}",
        "",
        "## Resource delta (first row → last row)",
        "",
        f"| | {_color_table_heading('CPU req (m)')} | {_color_table_heading('Mem req (MiB)')} |",
        f"|---|---:|---:|",
        f"| {label_a} | {_delta((r0a or {}).get('cpu_request_m'), (la or {}).get('cpu_request_m'))} | "
        f"{_delta((r0a or {}).get('mem_request_mib'), (la or {}).get('mem_request_mib'))} |",
        f"| {label_b} | {_delta((r0b or {}).get('cpu_request_m'), (lb or {}).get('cpu_request_m'))} | "
        f"{_delta((r0b or {}).get('mem_request_mib'), (lb or {}).get('mem_request_mib'))} |",
        "",
        "## Combined iterations",
        "",
        "One row per iteration index (boundary `rows` order). "
        "Rows are **not** matched configs — each arm ran an independent squeeze trajectory. "
        "When `paired-baseline-probe.md` exists under each arm, **row 1** shares the same "
        "observed burn/cpu% (one k6 window, two optimizer analyses).",
        "",
        "| # | "
        f"{label_a} status | {_color_table_heading(f'{label_a} prov cost')} | {_color_table_heading(f'{label_a} util cost')} | {label_a} p95 | {label_a} err | {label_a} ach RPS | "
        f"{label_a} cpu% req | {label_a} mem% | {_color_table_heading(f'{label_a} cpu m')} | {_color_table_heading(f'{label_a} mem Mi')} | "
        f"{label_a} cpu lim | {label_a} mem lim | {label_a} repl | "
        f"{label_b} status | {_color_table_heading(f'{label_b} prov cost')} | {_color_table_heading(f'{label_b} util cost')} | {label_b} p95 | {label_b} err | {label_b} ach RPS | "
        f"{label_b} cpu% req | {label_b} mem% | {_color_table_heading(f'{label_b} cpu m')} | {_color_table_heading(f'{label_b} mem Mi')} | "
        f"{label_b} cpu lim | {label_b} mem lim | {label_b} repl |",
        "| " + " | ".join(["---"] * 27) + " |",
    ]

    nmax = max(len(ra), len(rb))
    for i in range(nmax):
        a = ra[i] if i < len(ra) else None
        b = rb[i] if i < len(rb) else None
        lines.append(
            f"| {i + 1} | "
            f"{_cell(a, 'status')} | {_cell(a, 'cost_score')} | {_util_cell(a)} | {_cell(a, 'p95_ms')} | {_cell(a, 'error_rate')} | "
            f"{_cell(a, 'achieved_rps_target_window')} | {_cpu_util_cell(a)} | {_cell(a, 'mem_util_pct')} | "
            f"{_cell(a, 'cpu_request_m')} | {_cell(a, 'mem_request_mib')} | "
            f"{_cell(a, 'cpu_limit_m')} | {_cell(a, 'mem_limit_mib')} | {_cell(a, 'replicas')} | "
            f"{_cell(b, 'status')} | {_cell(b, 'cost_score')} | {_util_cell(b)} | {_cell(b, 'p95_ms')} | {_cell(b, 'error_rate')} | "
            f"{_cell(b, 'achieved_rps_target_window')} | {_cpu_util_cell(b)} | {_cell(b, 'mem_util_pct')} | "
            f"{_cell(b, 'cpu_request_m')} | {_cell(b, 'mem_request_mib')} | "
            f"{_cell(b, 'cpu_limit_m')} | {_cell(b, 'mem_limit_mib')} | {_cell(b, 'replicas')} |"
        )

    if len(ra) != len(rb):
        lines.extend(
            [
                "",
                f"*Iteration count mismatch: {label_a}={len(ra)}, {label_b}={len(rb)}.*",
            ]
        )

    lines.extend(
        [
            "",
            "## Cost per iteration",
            "",
            "One row per iteration; prov cost and util cost only (easier to scan than the full table above).",
            "",
            f"| # | {label_a} status | {_color_table_heading(f'{label_a} prov cost')} | {_color_table_heading(f'{label_a} util cost')} | "
            f"{label_b} status | {_color_table_heading(f'{label_b} prov cost')} | {_color_table_heading(f'{label_b} util cost')} |",
            "| " + " | ".join(["---"] * 7) + " |",
        ]
    )
    for i in range(nmax):
        a = ra[i] if i < len(ra) else None
        b = rb[i] if i < len(rb) else None
        lines.append(
            f"| {i + 1} | "
            f"{_cell(a, 'status')} | {_cell(a, 'cost_score')} | {_util_cell(a)} | "
            f"{_cell(b, 'status')} | {_cell(b, 'cost_score')} | {_util_cell(b)} |"
        )

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser(description="Compare two cost-effective-boundary.json files")
    p.add_argument("boundary_a", type=Path)
    p.add_argument("boundary_b", type=Path)
    p.add_argument("--label-a", default="formula")
    p.add_argument("--label-b", default="llm")
    p.add_argument("-o", "--output", type=Path, default=None)
    args = p.parse_args()
    text = compare(
        args.boundary_a,
        args.boundary_b,
        label_a=args.label_a,
        label_b=args.label_b,
    )
    if args.output:
        args.output.write_text(text)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
