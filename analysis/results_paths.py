"""Resolve per-job results directory (supports STRESS_RESULTS_SUBDIR for A/B comparisons)."""

from __future__ import annotations

import os
from pathlib import Path


def results_dir(repo_root: Path) -> Path:
    sub = os.environ.get("STRESS_RESULTS_SUBDIR", "").strip().strip("/")
    base = repo_root / "results"
    return (base / sub if sub else base).resolve()
