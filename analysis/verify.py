"""Compare run 1 vs run 2 artifacts via LLM and write llm-result-verification.md."""
import json
from pathlib import Path

from .api import analyze_with_llm
from .prompts import VERIFICATION_SYSTEM_PROMPT, build_verification_user_prompt

REPO_ROOT = Path(__file__).resolve().parent.parent


def _load_run_artifacts(run_dir: Path) -> dict:
    """Load report, analysis.json, recommended.diff, and a short metrics summary."""
    artifacts = {}
    if (run_dir / "report.md").exists():
        artifacts["report"] = (run_dir / "report.md").read_text()
    else:
        artifacts["report"] = ""
    if (run_dir / "analysis.json").exists():
        artifacts["analysis_json"] = (run_dir / "analysis.json").read_text()
    else:
        artifacts["analysis_json"] = "{}"
    if (run_dir / "recommended.diff").exists():
        artifacts["recommended_diff"] = (run_dir / "recommended.diff").read_text()
    else:
        artifacts["recommended_diff"] = ""
    parts = []
    if (run_dir / "k6-run-summary.json").exists():
        try:
            k6 = json.loads((run_dir / "k6-run-summary.json").read_text())
            m = k6.get("metrics", {})
            parts.append(
                "k6 metrics (excerpt): "
                + json.dumps({k: v for k, v in list(m.items())[:15]}, indent=0)
            )
        except (json.JSONDecodeError, TypeError):
            parts.append((run_dir / "k6-run-summary.json").read_text()[:800])
    if (run_dir / "experiment.json").exists():
        try:
            exp = json.loads((run_dir / "experiment.json").read_text())
            parts.append(
                "experiment (failure, observed): "
                + json.dumps(
                    {"failure": exp.get("failure"), "observed": exp.get("observed")},
                    indent=0,
                )
            )
        except (json.JSONDecodeError, TypeError):
            pass
    artifacts["metrics_summary"] = "\n".join(parts) if parts else "No metrics"
    return artifacts


def run_verification(run_1_dir: Path, run_2_dir: Path) -> dict:
    """Call LLM to compare run 1 vs run 2; return parsed JSON result."""
    run1 = _load_run_artifacts(run_1_dir)
    run2 = _load_run_artifacts(run_2_dir)
    user_prompt = build_verification_user_prompt(run1, run2)
    return analyze_with_llm(VERIFICATION_SYSTEM_PROMPT, user_prompt)


def write_verification_output(result: dict, run_1_dir: Path, run_2_dir: Path) -> Path:
    """Write verification/llm-result-verification.md and return verification dir."""
    verification_dir = run_1_dir / "verification"
    verification_dir.mkdir(parents=True, exist_ok=True)
    md_lines = [
        "# Verification: Did the recommended fix work?",
        "",
        f"**Verdict:** {result.get('verdict', '')}",
        "",
        "## Reasoning",
        result.get("reasoning", ""),
        "",
        "## Run 1 summary",
        result.get("run1_summary", ""),
        "",
        "## Run 2 summary",
        result.get("run2_summary", ""),
        "",
    ]
    alt = (result.get("alternative_diff") or "").strip()
    if alt:
        md_lines.extend(
            ["## Alternative recommended diff", "", "```diff", alt, "```", ""]
        )
    (verification_dir / "llm-result-verification.md").write_text("\n".join(md_lines))
    return verification_dir
