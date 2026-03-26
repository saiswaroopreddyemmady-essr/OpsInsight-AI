from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class AgentMessage:
    agent: str
    priority: str
    message: str

    def to_dict(self):
        return asdict(self)


class QualityAgent:
    def analyze(self, quality_results: list[dict]) -> list[AgentMessage]:
        messages = []
        for result in quality_results:
            if result["failed_rows"] <= 0:
                continue
            priority = "P1" if result["severity"] == "HIGH" else "P2"
            messages.append(
                AgentMessage(
                    "QualityAgent",
                    priority,
                    f'{result["rule_name"]}: {result["failed_rows"]} failed rows. '
                    f'{result["details"]}'
                )
            )
        return messages


class AnomalyAgent:
    def analyze(self, anomalies: list[dict]) -> list[AgentMessage]:
        return [
            AgentMessage(
                "AnomalyAgent",
                "P1" if a["score"] >= 5 else "P2",
                f'{a["anomaly_type"]} affecting {a["entity"]}: {a["details"]}'
            )
            for a in anomalies
        ]


class KPIAgent:
    def analyze(self, kpis: dict[str, Any]) -> list[AgentMessage]:
        messages = [
            AgentMessage(
                "KPIAgent",
                "INFO",
                f'Processed {kpis["orders"]:,} orders with '
                f'${kpis["completed_revenue"]:,.2f} completed revenue.'
            )
        ]
        if kpis["avg_processing_minutes"] > 120:
            messages.append(
                AgentMessage(
                    "KPIAgent",
                    "P2",
                    f'Average processing time is {kpis["avg_processing_minutes"]:.1f} minutes, '
                    "above the 120-minute operational threshold."
                )
            )
        if kpis["cancellation_rate"] > 15:
            messages.append(
                AgentMessage(
                    "KPIAgent",
                    "P2",
                    f'Cancellation rate is {kpis["cancellation_rate"]:.1f}%, '
                    "which should be reviewed by operations."
                )
            )
        return messages


class DecisionOrchestrator:
    """Combines specialist-agent findings and prioritizes actions."""

    def prioritize(self, messages: list[AgentMessage]) -> list[AgentMessage]:
        rank = {"P1": 0, "P2": 1, "INFO": 2}
        return sorted(messages, key=lambda m: (rank.get(m.priority, 9), m.agent))


class RecommendationAgent:
    def recommend(self, messages: list[AgentMessage]) -> list[str]:
        recommendations = []
        combined = " ".join(m.message.lower() for m in messages)

        if "duplicate_order_id" in combined:
            recommendations.append(
                "Enforce order_id uniqueness before warehouse load and quarantine duplicates."
            )
        if "missing_region" in combined:
            recommendations.append(
                "Add source-system validation for region and route missing values to an exception queue."
            )
        if "invalid_quantity" in combined:
            recommendations.append(
                "Reject non-positive quantities at ingestion and notify the upstream owner."
            )
        if "processing_delay" in combined or "processing time" in combined:
            recommendations.append(
                "Investigate delayed-order concentration by region and compare staffing, queue depth, and system latency."
            )
        if "revenue_outlier" in combined or "revenue spike" in combined:
            recommendations.append(
                "Review price and quantity outliers against reference pricing before operational reporting."
            )

        if not recommendations:
            recommendations.append(
                "No material risks detected. Continue scheduled monitoring and retain the run for trend analysis."
            )
        return recommendations


def run_agentic_workflow(
    quality_results: list[dict],
    anomalies: list[dict],
    kpis: dict,
) -> dict:
    messages = []
    messages.extend(QualityAgent().analyze(quality_results))
    messages.extend(AnomalyAgent().analyze(anomalies))
    messages.extend(KPIAgent().analyze(kpis))

    prioritized = DecisionOrchestrator().prioritize(messages)
    recommendations = RecommendationAgent().recommend(prioritized)

    return {
        "agent_findings": [m.to_dict() for m in prioritized],
        "recommendations": recommendations,
    }
