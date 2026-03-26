from src.agents import run_agentic_workflow


def test_agentic_workflow_generates_recommendations():
    quality = [
        {
            "rule_name": "duplicate_order_id",
            "severity": "HIGH",
            "failed_rows": 3,
            "details": "Order IDs must be unique.",
        }
    ]
    anomalies = [
        {
            "anomaly_type": "processing_delay",
            "entity": "South",
            "score": 8.0,
            "details": "Delayed orders concentrated in South.",
        }
    ]
    kpis = {
        "orders": 100,
        "completed_revenue": 10000.0,
        "avg_processing_minutes": 130.0,
        "cancellation_rate": 5.0,
    }

    result = run_agentic_workflow(quality, anomalies, kpis)

    assert len(result["agent_findings"]) >= 3
    assert any("uniqueness" in r.lower() for r in result["recommendations"])
    assert any("delayed-order" in r.lower() for r in result["recommendations"])
