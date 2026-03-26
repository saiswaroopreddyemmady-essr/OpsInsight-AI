import pandas as pd

from src.data_quality import run_quality_checks


def test_quality_rules_detect_known_failures():
    df = pd.DataFrame(
        [
            {
                "order_id": "O1",
                "region": "",
                "quantity": -1,
                "unit_price": 10.0,
                "status": "COMPLETED",
                "order_ts": "2026-01-01T10:00:00",
            },
            {
                "order_id": "O1",
                "region": "South",
                "quantity": 2,
                "unit_price": 10.0,
                "status": "BAD_STATUS",
                "order_ts": "bad-date",
            },
        ]
    )

    results = {r.rule_name: r.failed_rows for r in run_quality_checks(df)}

    assert results["duplicate_order_id"] == 2
    assert results["missing_region"] == 1
    assert results["invalid_quantity"] == 1
    assert results["invalid_status"] == 1
    assert results["invalid_order_timestamp"] == 1
