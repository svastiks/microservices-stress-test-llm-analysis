#!/usr/bin/env python3
"""Prefix artifact run dirs. Run from repo root.

GOOD_COST_WIN_*  — challenger wins prov cost, more iterations than opponent.
GOOD_BOTH_WIN_*  — challenger wins prov cost and iterations (<= opponent).
BAD_*            — loses cost, incomplete/system failure, nested duplicate.

Iterations use boundary row counts (same as compare pass bar).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ARTIFACTS = Path("artifacts")
PREFIXES = ("GOOD_BOTH_WIN_", "GOOD_COST_WIN_", "GOOD_", "BAD_")
RUN_BASE_RE = re.compile(r"^run-.+")

TRACK_SIDES = {
    "FORMULA_VS_ADVANCED_LLM": (
        ("formula-run", "formula"),
        ("llm-run", "llm"),
        ("llm", "formula"),
    ),
    "VANILLA_LLM_VS_ADVANCED_LLM": (
        ("advanced-llm-run", "advanced-llm"),
        ("vanilla-llm-run", "vanilla-llm"),
        ("advanced-llm", "vanilla-llm"),
    ),
}


def _strip_prefix(name: str) -> str:
    for p in PREFIXES:
        if name.startswith(p):
            rest = name[len(p) :]
            if RUN_BASE_RE.match(rest):
                return rest
    if RUN_BASE_RE.match(name):
        return name
    return name


def _matches_run_dir(name: str) -> bool:
    return _strip_prefix(name) != name or RUN_BASE_RE.match(name)


def _parse_comparison(path: Path) -> dict[str, float]:
    t = path.read_text()
    out: dict[str, float] = {}
    for side in ("formula", "llm", "advanced-llm", "vanilla-llm"):
        m = re.search(rf"\*\*{re.escape(side)}\*\*.*?best_pass=([0-9.]+)", t)
        if m:
            out[side] = float(m.group(1))
        elif f"**{side}**" in t and "best_pass_dir=None" in t:
            out[side] = -1.0
    return out


def _iteration_counts(run_dir: Path, track: str) -> tuple[int, int] | None:
    spec = TRACK_SIDES[track]
    challenger, opponent = spec[2]
    subs = {label: sub for sub, label in spec[:2]}
    out: list[int] = []
    for label in (challenger, opponent):
        boundary = run_dir / subs[label] / "cost-effective-boundary.json"
        if not boundary.is_file():
            return None
        data = json.loads(boundary.read_text())
        n = len(data.get("rows") or [])
        if not n:
            return None
        out.append(n)
    return out[0], out[1]


def _side_broken(run_dir: Path, sub: str, label: str) -> list[str]:
    issues: list[str] = []
    side_dir = run_dir / sub
    if not side_dir.is_dir():
        return [f"{label}: missing {sub}"]
    boundary = side_dir / "cost-effective-boundary.json"
    if not boundary.is_file():
        return [f"{label}: missing cost-effective-boundary.json"]
    data = json.loads(boundary.read_text())
    rows = data.get("rows") or []
    if not rows:
        issues.append(f"{label}: empty squeeze boundary")
    passes = [r for r in rows if r.get("status") == "PASS"]
    if not passes:
        issues.append(f"{label}: never reached PASS (system/incomplete run)")
    score = data.get("cost_best_pass_score")
    if score is None or float(score) <= 0:
        issues.append(f"{label}: no valid best_pass cost")
    if not list(side_dir.glob("iteration-*")):
        issues.append(f"{label}: no iteration artifacts")
    return issues


def broken_issues(rel: str, run_dir: Path) -> list[str]:
    base = _strip_prefix(run_dir.name)
    if base == "run-1" and run_dir.parent.name.endswith("rps35"):
        return ["nested duplicate layout"]

    if not (run_dir / "comparison.md").is_file():
        return ["missing comparison.md"]

    track = rel.split("/")[0]
    spec = TRACK_SIDES.get(track)
    if not spec:
        return ["unknown track"]

    issues: list[str] = []
    for sub, label in spec[:2]:
        issues.extend(_side_broken(run_dir, sub, label))

    costs = _parse_comparison(run_dir / "comparison.md")
    challenger, opponent = spec[2]
    if costs.get(challenger, -1) < 0:
        issues.append(f"{challenger}: best_pass_dir=None in comparison")
    if costs.get(opponent, -1) < 0:
        issues.append(f"{opponent}: best_pass_dir=None in comparison")

    return issues


def classify(rel: str, run_dir: Path) -> tuple[str, str]:
    """Return (folder_prefix, human reason). folder_prefix is BAD | GOOD_COST_WIN | GOOD_BOTH_WIN."""
    issues = broken_issues(rel, run_dir)
    if issues:
        return "BAD", issues[0]

    costs = _parse_comparison(run_dir / "comparison.md")
    track = rel.split("/")[0]
    challenger, opponent = TRACK_SIDES[track][2]
    c_cost = costs.get(challenger)
    o_cost = costs.get(opponent)
    if c_cost is None or o_cost is None or c_cost < 0 or o_cost < 0:
        return "BAD", "incomplete comparison"

    if c_cost >= o_cost:
        return "BAD", f"{challenger} loses on prov cost"

    iters = _iteration_counts(run_dir, track)
    if iters is None:
        return "BAD", "missing iteration counts"
    c_iters, o_iters = iters
    if c_iters <= o_iters:
        return "GOOD_BOTH_WIN", (
            f"{challenger} wins cost ({c_cost:.4f}<{o_cost:.4f}) "
            f"and iters ({c_iters}<={o_iters})"
        )
    return "GOOD_COST_WIN", (
        f"{challenger} wins cost ({c_cost:.4f}<{o_cost:.4f}) "
        f"but more iters ({c_iters}>{o_iters})"
    )


def _collect_run_dirs(artifacts_root: Path) -> list[Path]:
    found: list[Path] = []
    for track_dir in artifacts_root.iterdir():
        if not track_dir.is_dir():
            continue
        for orient in ("UP", "DOWN"):
            base = track_dir / orient
            if not base.is_dir():
                continue
            for child in base.iterdir():
                if child.is_dir() and _matches_run_dir(child.name):
                    found.append(child)
            for parent in base.iterdir():
                if not parent.is_dir() or not _matches_run_dir(parent.name):
                    continue
                for nested in parent.iterdir():
                    if nested.is_dir() and _strip_prefix(nested.name) == "run-1":
                        if "rps35" in _strip_prefix(parent.name):
                            found.append(nested)
    return sorted(found, key=lambda p: (-len(p.parts), p.as_posix()))


def main() -> None:
    root = Path.cwd()
    artifacts_root = root / ARTIFACTS
    if not artifacts_root.is_dir():
        raise SystemExit(f"Run from repo root; missing {ARTIFACTS}")

    run_dirs = _collect_run_dirs(artifacts_root)
    print(f"Labeling {len(run_dirs)} run directories\n")

    stats: dict[str, int] = {}
    for run_dir in run_dirs:
        rel = str(run_dir.relative_to(artifacts_root))
        prefix, reason = classify(rel, run_dir)
        stats[prefix] = stats.get(prefix, 0) + 1
        base = _strip_prefix(run_dir.name)
        dst = run_dir.parent / f"{prefix}_{base}"
        if run_dir != dst:
            if dst.exists():
                raise SystemExit(f"target exists: {dst}")
            print(f"  {prefix}: {rel} -> {dst.name}")
            print(f"           ({reason})")
            run_dir.rename(dst)
        else:
            print(f"  {prefix}: {rel}  ({reason})")

    print("\nDone.", ", ".join(f"{k}={v}" for k, v in sorted(stats.items())))


if __name__ == "__main__":
    main()
