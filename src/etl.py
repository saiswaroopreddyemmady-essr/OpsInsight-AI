from __future__ import annotations

import sqlite3
from pathlib import Path
import pandas as pd

DB_PATH = Path("data/processed/ops_insight.db")
SCHEMA_PATH = Path("sql/schema.sql")


def extract(raw_path: str | Path) -> pd.DataFrame:
    return pd.read_csv(raw_path)


def transform(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["order_ts"] = pd.to_datetime(out["order_ts"], errors="coerce")
    out["quantity"] = pd.to_numeric(out["quantity"], errors="coerce")
    out["unit_price"] = pd.to_numeric(out["unit_price"], errors="coerce")
    out["processing_minutes"] = pd.to_numeric(out["processing_minutes"], errors="coerce")
    out["revenue"] = (out["quantity"] * out["unit_price"]).round(2)
    out["status"] = out["status"].astype(str).str.upper().str.strip()
    out["region"] = out["region"].fillna("").astype(str).str.strip()
    out["order_ts"] = out["order_ts"].astype(str)
    return out


def load(df: pd.DataFrame, db_path: str | Path = DB_PATH) -> Path:
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))

        # Deduplicate on business key for warehouse load.
        fact = df.drop_duplicates(subset=["order_id"], keep="first").copy()
        fact[
            [
                "order_id",
                "customer_id",
                "product_id",
                "region",
                "order_ts",
                "quantity",
                "unit_price",
                "revenue",
                "processing_minutes",
                "status",
            ]
        ].to_sql("fact_orders", conn, if_exists="replace", index=False)

        conn.executescript(
            """
            CREATE INDEX IF NOT EXISTS idx_fact_orders_ts ON fact_orders(order_ts);
            CREATE INDEX IF NOT EXISTS idx_fact_orders_region_status ON fact_orders(region, status);
            CREATE INDEX IF NOT EXISTS idx_fact_orders_product ON fact_orders(product_id);
            """
        )

        pd.DataFrame({"customer_id": sorted(fact["customer_id"].dropna().unique())}).to_sql(
            "dim_customer", conn, if_exists="replace", index=False
        )

        (
            fact[["product_id", "product_name"]]
            .drop_duplicates()
            .sort_values("product_id")
            .to_sql("dim_product", conn, if_exists="replace", index=False)
        )

        pd.DataFrame(
            {"region_name": sorted([x for x in fact["region"].dropna().unique() if x])}
        ).to_sql("dim_region", conn, if_exists="replace", index=False)

    return db_path
