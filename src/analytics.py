from __future__ import annotations

import sqlite3
from pathlib import Path
import pandas as pd


def get_kpis(db_path: str | Path) -> dict:
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT
                COUNT(*) AS orders,
                ROUND(SUM(CASE WHEN status='COMPLETED' THEN revenue ELSE 0 END), 2) AS revenue,
                ROUND(AVG(processing_minutes), 2) AS avg_processing_minutes,
                ROUND(100.0 * SUM(CASE WHEN status='CANCELLED' THEN 1 ELSE 0 END) / COUNT(*), 2)
                    AS cancellation_rate
            FROM fact_orders
            """
        ).fetchone()

    return {
        "orders": row[0] or 0,
        "completed_revenue": row[1] or 0.0,
        "avg_processing_minutes": row[2] or 0.0,
        "cancellation_rate": row[3] or 0.0,
    }


def region_summary(db_path: str | Path) -> pd.DataFrame:
    with sqlite3.connect(db_path) as conn:
        return pd.read_sql_query(
            """
            SELECT
                COALESCE(NULLIF(region, ''), 'UNKNOWN') AS region,
                COUNT(*) AS orders,
                ROUND(SUM(CASE WHEN status='COMPLETED' THEN revenue ELSE 0 END), 2) AS revenue,
                ROUND(AVG(processing_minutes), 2) AS avg_processing_minutes
            FROM fact_orders
            GROUP BY COALESCE(NULLIF(region, ''), 'UNKNOWN')
            ORDER BY revenue DESC
            """,
            conn,
        )


def daily_summary(db_path: str | Path) -> pd.DataFrame:
    with sqlite3.connect(db_path) as conn:
        return pd.read_sql_query(
            """
            SELECT
                substr(order_ts, 1, 10) AS order_date,
                COUNT(*) AS orders,
                ROUND(SUM(CASE WHEN status='COMPLETED' THEN revenue ELSE 0 END), 2) AS revenue,
                ROUND(AVG(processing_minutes), 2) AS avg_processing_minutes
            FROM fact_orders
            GROUP BY substr(order_ts, 1, 10)
            ORDER BY order_date
            """,
            conn,
        )
