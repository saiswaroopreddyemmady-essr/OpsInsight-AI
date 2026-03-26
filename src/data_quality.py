from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Iterable
import pandas as pd


@dataclass
class QualityResult:
    rule_name: str
    severity: str
    failed_rows: int
    details: str

    def to_dict(self):
        return asdict(self)


VALID_STATUSES = {"COMPLETED", "PENDING", "CANCELLED"}


def run_quality_checks(df: pd.DataFrame) -> list[QualityResult]:
    results: list[QualityResult] = []

    duplicate_count = int(df["order_id"].duplicated(keep=False).sum())
    results.append(QualityResult(
        "duplicate_order_id",
        "HIGH",
        duplicate_count,
        "Order IDs must be unique."
    ))

    missing_region = int(df["region"].fillna("").astype(str).str.strip().eq("").sum())
    results.append(QualityResult(
        "missing_region",
        "MEDIUM",
        missing_region,
        "Region is required for operational reporting."
    ))

    invalid_quantity = int((pd.to_numeric(df["quantity"], errors="coerce") <= 0).sum())
    results.append(QualityResult(
        "invalid_quantity",
        "HIGH",
        invalid_quantity,
        "Quantity must be greater than zero."
    ))

    invalid_status = int((~df["status"].isin(VALID_STATUSES)).sum())
    results.append(QualityResult(
        "invalid_status",
        "MEDIUM",
        invalid_status,
        f"Status must be one of {sorted(VALID_STATUSES)}."
    ))

    invalid_price = int((pd.to_numeric(df["unit_price"], errors="coerce") <= 0).sum())
    results.append(QualityResult(
        "invalid_unit_price",
        "HIGH",
        invalid_price,
        "Unit price must be positive."
    ))

    missing_ts = int(pd.to_datetime(df["order_ts"], errors="coerce").isna().sum())
    results.append(QualityResult(
        "invalid_order_timestamp",
        "HIGH",
        missing_ts,
        "Order timestamp must be parseable."
    ))

    return results


def failing_checks(results: Iterable[QualityResult]) -> list[QualityResult]:
    return [r for r in results if r.failed_rows > 0]
