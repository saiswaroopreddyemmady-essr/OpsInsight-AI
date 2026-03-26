from __future__ import annotations

from dataclasses import dataclass, asdict
import pandas as pd


@dataclass
class Anomaly:
    anomaly_type: str
    entity: str
    score: float
    details: str

    def to_dict(self):
        return asdict(self)


def _robust_zscore(series: pd.Series) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce")
    median = s.median()
    mad = (s - median).abs().median()
    if not mad or pd.isna(mad):
        return pd.Series([0.0] * len(s), index=s.index)
    return 0.6745 * (s - median) / mad


def detect_anomalies(df: pd.DataFrame) -> list[Anomaly]:
    work = df.copy()
    work["revenue"] = pd.to_numeric(work["quantity"], errors="coerce") * pd.to_numeric(
        work["unit_price"], errors="coerce"
    )
    work["revenue_z"] = _robust_zscore(work["revenue"])
    work["cycle_z"] = _robust_zscore(work["processing_minutes"])

    anomalies: list[Anomaly] = []

    high_revenue = work[work["revenue_z"].abs() >= 5]
    if not high_revenue.empty:
        anomalies.append(
            Anomaly(
                "revenue_outlier",
                "order",
                round(float(high_revenue["revenue_z"].abs().max()), 2),
                f"{len(high_revenue)} orders have extreme revenue values."
            )
        )

    slow_orders = work[work["processing_minutes"] > 180]
    if not slow_orders.empty:
        region_counts = (
            slow_orders["region"].fillna("UNKNOWN").replace("", "UNKNOWN").value_counts()
        )
        worst_region = str(region_counts.index[0])
        anomalies.append(
            Anomaly(
                "processing_delay",
                worst_region,
                round(float(region_counts.iloc[0]), 2),
                f"{len(slow_orders)} orders exceeded 180 processing minutes; "
                f"{worst_region} has the largest concentration."
            )
        )

    daily = work.copy()
    daily["order_date"] = pd.to_datetime(daily["order_ts"], errors="coerce").dt.date
    daily_revenue = daily.groupby("order_date", dropna=True)["revenue"].sum()
    if len(daily_revenue) >= 5:
        daily_z = _robust_zscore(daily_revenue)
        if (daily_z.abs() >= 4).any():
            day = str(daily_z.abs().idxmax())
            anomalies.append(
                Anomaly(
                    "daily_revenue_spike",
                    day,
                    round(float(daily_z.abs().max()), 2),
                    f"Daily revenue on {day} deviates materially from the typical daily pattern."
                )
            )

    return anomalies
