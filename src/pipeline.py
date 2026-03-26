from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from src.generate_data import generate_orders
from src.etl import extract, transform, load, DB_PATH
from src.data_quality import run_quality_checks
from src.anomaly import detect_anomalies
from src.analytics import get_kpis
from src.agents import run_agentic_workflow

ARTIFACT_PATH = Path("artifacts/executive_summary.json")


def run_pipeline() -> dict:
    raw_path = generate_orders()
    raw_df = extract(raw_path)
    transformed = transform(raw_df)

    # Run checks before deduplication so source-quality problems remain visible.
    quality_results = run_quality_checks(transformed)
    anomalies = detect_anomalies(transformed)

    db_path = load(transformed)
    kpis = get_kpis(db_path)

    run_ts = datetime.now(timezone.utc).isoformat()

    with sqlite3.connect(db_path) as conn:
        conn.execute("DELETE FROM dq_results")
        conn.executemany(
            """
            INSERT INTO dq_results(run_ts, rule_name, severity, failed_rows, details)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                (
                    run_ts,
                    r.rule_name,
                    r.severity,
                    r.failed_rows,
                    r.details,
                )
                for r in quality_results
            ],
        )

        conn.execute("DELETE FROM anomaly_results")
        conn.executemany(
            """
            INSERT INTO anomaly_results(run_ts, anomaly_type, entity, score, details)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                (
                    run_ts,
                    a.anomaly_type,
                    a.entity,
                    a.score,
                    a.details,
                )
                for a in anomalies
            ],
        )
        conn.commit()

    summary = {
        "run_ts": run_ts,
        "database": str(db_path),
        "kpis": kpis,
        "quality_results": [r.to_dict() for r in quality_results],
        "anomalies": [a.to_dict() for a in anomalies],
    }
    summary.update(
        run_agentic_workflow(
            summary["quality_results"],
            summary["anomalies"],
            summary["kpis"],
        )
    )

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


if __name__ == "__main__":
    result = run_pipeline()
    print(json.dumps(result, indent=2))
