"""Optional LLM narrative after a formula-only squeeze (YAML steps were non-LLM)."""

from __future__ import annotations

import json
from pathlib import Path

from .api import analyze_with_llm

_SUMMARY_SYSTEM = """You summarize automated squeeze experiments for researchers.
Return exactly this JSON shape:
{"report": "<plain text, multiple lines OK; no markdown tables>"}

The input is cost-effective-boundary.json: iterations, metrics rows, stop reason.
Summarize: iteration count, trajectory of cost_score and CPU/mem requests if present, stop reason, and whether the run found a sensible cost/SLO boundary.
Be factual; do not invent numbers not in the input."""


def write_formula_final_report(run_root: Path) -> Path | None:
    boundary_path = run_root / "cost-effective-boundary.json"
    if not boundary_path.exists():
        return None
    summary = json.loads(boundary_path.read_text())
    user = json.dumps(summary, indent=2)
    parsed = analyze_with_llm(
        _SUMMARY_SYSTEM,
        "Squeeze summary (deterministic formula steps only; LLM was not used for YAML):\n" + user,
    )
    report = (parsed.get("report") or "").strip()
    out = run_root / "squeeze-formula-llm-summary.txt"
    out.write_text(report + ("\n" if report else ""))
    return out
