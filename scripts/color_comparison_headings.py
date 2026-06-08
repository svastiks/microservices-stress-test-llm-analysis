#!/usr/bin/env python3
"""Prefix comparison.md table headers with emoji blocks (excludes ENGINEER_VS_ADVANCED_LLM)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from analysis.compare_squeeze_methods import _color_table_heading  # noqa: E402

SKIP_PREFIX = "ENGINEER_VS_ADVANCED_LLM"


def _strip_html(cell: str) -> str:
    return re.sub(r"<[^>]+>", "", cell).strip()


def _is_separator_row(line: str) -> bool:
    return line.startswith("|") and "---" in line


def _is_header_row(line: str) -> bool:
    if not line.startswith("|") or _is_separator_row(line):
        return False
    low = line.lower()
    return (
        "| # |" in line
        or ("prov cost" in low and "status" in low)
        or ("cpu req" in low and "mem req" in low)
    )


def color_header_line(line: str) -> str:
    parts = line.split("|")
    rebuilt: list[str] = []
    for part in parts:
        cell = _strip_html(part)
        if not cell or cell == "#" or cell.startswith("---"):
            rebuilt.append(part)
            continue
        colored = _color_table_heading(cell)
        pad_l = len(part) - len(part.lstrip())
        pad_r = len(part) - len(part.rstrip())
        rebuilt.append(" " * pad_l + colored + " " * pad_r)
    return "|".join(rebuilt)


def process_file(path: Path) -> bool:
    lines = path.read_text().splitlines()
    changed = False
    new_lines: list[str] = []
    for i, line in enumerate(lines):
        if _is_header_row(line) and i + 1 < len(lines) and _is_separator_row(lines[i + 1]):
            nl = color_header_line(line)
            if nl != line:
                changed = True
            new_lines.append(nl)
            continue
        new_lines.append(line)
    if not changed:
        return False
    path.write_text("\n".join(new_lines) + "\n")
    return True


def main() -> None:
    root = Path(__file__).resolve().parent.parent / "artifacts"
    n = 0
    for path in sorted(root.rglob("comparison.md")):
        if SKIP_PREFIX in path.parts:
            continue
        if process_file(path):
            print(path.relative_to(root.parent))
            n += 1
    print(f"updated {n} comparison.md files (⬜ cost  🟩 cpu m  🟧 mem Mi)")


if __name__ == "__main__":
    main()
