#!/usr/bin/env python3
import json
import os

from pymongo import MongoClient


def main() -> int:
    uri = os.environ.get(
        "RESULTS_DB_URI",
        "mongodb://analyzer:change-me@analyzer-mongodb.svastik.svc.cluster.local:27017/admin",
    )
    db_name = os.environ.get("RESULTS_DB_NAME", "stress_analyzer")
    limit = int(os.environ.get("RESULTS_DB_LIMIT", "20"))

    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    db = client[db_name]
    try:
        rows = list(
            db.iterations.find(
                {},
                {
                    "_id": 0,
                    "run_label": 1,
                    "iteration_index": 1,
                    "run_dir": 1,
                    "failure.failed": 1,
                    "cost.cost_score": 1,
                    "observed.error_rate": 1,
                    "observed.latency_ms.p95": 1,
                },
            )
            .sort([("run_label", -1), ("iteration_index", -1)])
            .limit(limit)
        )
        print(json.dumps(rows, indent=2))
        return 0
    finally:
        client.close()


if __name__ == "__main__":
    raise SystemExit(main())
