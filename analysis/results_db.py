import json
import os
import time
from pathlib import Path
from typing import Any


def _is_enabled() -> bool:
    return os.environ.get("RESULTS_DB_ENABLED", "").lower() in {"1", "true", "yes"}


def _connect():
    uri = os.environ.get("RESULTS_DB_URI", "").strip()
    db_name = os.environ.get("RESULTS_DB_NAME", "stress_analyzer").strip()
    if not uri:
        return None, None
    try:
        from pymongo import MongoClient
    except Exception:
        return None, None
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    # validate connectivity fast
    client.admin.command("ping")
    return client, client[db_name]


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text()
    except Exception:
        return ""


def _infer_run_label(run_dir: Path, run_meta: dict[str, Any]) -> str:
    run_label = str(run_meta.get("run_label") or "").strip()
    if run_label:
        return run_label
    parent = run_dir.parent.name
    if parent.startswith("run-"):
        return parent
    return f"run-unknown-{int(time.time())}"


def write_iteration(run_dir: Path, run_meta: dict[str, Any]) -> None:
    if not _is_enabled():
        return
    client, db = _connect()
    if client is None or db is None:
        return
    try:
        now = int(time.time())
        run_label = _infer_run_label(run_dir, run_meta)
        iteration_index = int(run_meta.get("iteration_index") or 0)
        experiment = _read_json(run_dir / "experiment.json")
        analysis = _read_json(run_dir / "analysis.json")
        existing = db.results.find_one({"_id": run_label}) or {}
        results = list(existing.get("results") or [])

        result_entry = {
            "iteration_index": iteration_index,
            "run_dir": str(run_dir),
            "_created": now,
            "_updated": now,
            "mode": run_meta.get("mode"),
            "profile": run_meta.get("profile"),
            "script": run_meta.get("script"),
            "analysis_goal": run_meta.get("analysis_goal"),
            "k8s_namespace": run_meta.get("k8s_namespace"),
            "k8s_deployment": run_meta.get("k8s_deployment"),
            "deployment_yaml": run_meta.get("deployment_yaml"),
            "hpa_yaml": run_meta.get("hpa_yaml"),
            "base_url": run_meta.get("base_url"),
            "start_ts": run_meta.get("start_ts"),
            "end_ts": run_meta.get("end_ts"),
            "k6_thresholds_crossed": run_meta.get("k6_thresholds_crossed"),
            "status": "FAIL" if (experiment.get("failure") or {}).get("failed") else "PASS",
            "failure": experiment.get("failure", {}),
            "observed": experiment.get("observed", {}),
            "cost": experiment.get("cost", {}),
            "config": experiment.get("config", {}),
            "recommendation": analysis.get("recommendation", {}),
            "artifacts": {
                "report_md": _read_text(run_dir / "report.md"),
                "recommended_diff": _read_text(run_dir / "recommended.diff"),
                "analysis_json": analysis,
                "experiment_json": experiment,
                "experiment_config_json": _read_json(run_dir / "experiment_config.json"),
                "k6_run_summary_json": _read_json(run_dir / "k6-run-summary.json"),
            },
        }

        replaced = False
        for i, row in enumerate(results):
            if int(row.get("iteration_index") or -1) == iteration_index:
                result_entry["_created"] = int(row.get("_created") or now)
                results[i] = result_entry
                replaced = True
                break
        if not replaced:
            results.append(result_entry)

        results.sort(key=lambda x: int(x.get("iteration_index") or 0))
        db.results.update_one(
            {"_id": run_label},
            {
                "$set": {
                    "_updated": now,
                    "run_label": run_label,
                    "context": {
                        "mode": run_meta.get("mode"),
                        "profile": run_meta.get("profile"),
                        "script": run_meta.get("script"),
                        "analysis_goal": run_meta.get("analysis_goal"),
                        "k8s_namespace": run_meta.get("k8s_namespace"),
                        "k8s_deployment": run_meta.get("k8s_deployment"),
                        "deployment_yaml": run_meta.get("deployment_yaml"),
                        "hpa_yaml": run_meta.get("hpa_yaml"),
                        "base_url": run_meta.get("base_url"),
                    },
                    "results": results,
                },
                "$setOnInsert": {"_created": now},
            },
            upsert=True,
        )
    finally:
        client.close()


def write_boundary(run_root: Path, summary: dict[str, Any]) -> None:
    if not _is_enabled():
        return
    client, db = _connect()
    if client is None or db is None:
        return
    try:
        now = int(time.time())
        run_label = run_root.name if run_root.name.startswith("run-") else f"run-unknown-{now}"
        db.results.update_one(
            {"_id": run_label},
            {
                "$set": {
                    "_updated": now,
                    "run_label": run_label,
                    "boundary": {
                        "run_root": str(run_root),
                        **summary,
                    },
                },
                "$setOnInsert": {"_created": now},
            },
            upsert=True,
        )
    finally:
        client.close()
