from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.analytics import region_summary, daily_summary
from src.etl import DB_PATH

SUMMARY_PATH = ROOT / "artifacts" / "executive_summary.json"

st.set_page_config(page_title="OpsInsight AI", layout="wide")
st.title("OpsInsight AI")
st.caption("Operational Analytics, Data Quality & Agentic Decision Support")

if not SUMMARY_PATH.exists() or not DB_PATH.exists():
    st.warning("Run `python -m src.pipeline` first.")
    st.stop()

summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
kpis = summary["kpis"]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Orders", f'{kpis["orders"]:,}')
c2.metric("Completed Revenue", f'${kpis["completed_revenue"]:,.2f}')
c3.metric("Avg Processing", f'{kpis["avg_processing_minutes"]:.1f} min')
c4.metric("Cancellation Rate", f'{kpis["cancellation_rate"]:.1f}%')

st.subheader("Revenue Trend")
daily = daily_summary(DB_PATH)
daily["order_date"] = pd.to_datetime(daily["order_date"])
st.line_chart(daily.set_index("order_date")["revenue"])

st.subheader("Regional Performance")
st.dataframe(region_summary(DB_PATH), use_container_width=True)

left, right = st.columns(2)

with left:
    st.subheader("Data Quality")
    dq = pd.DataFrame(summary["quality_results"])
    st.dataframe(dq, use_container_width=True)

with right:
    st.subheader("Detected Anomalies")
    anomalies = pd.DataFrame(summary["anomalies"])
    if anomalies.empty:
        st.success("No anomalies detected.")
    else:
        st.dataframe(anomalies, use_container_width=True)

st.subheader("Agent Findings")
for finding in summary["agent_findings"]:
    st.write(
        f'**{finding["priority"]} — {finding["agent"]}:** {finding["message"]}'
    )

st.subheader("Recommended Actions")
for i, recommendation in enumerate(summary["recommendations"], start=1):
    st.write(f"{i}. {recommendation}")
