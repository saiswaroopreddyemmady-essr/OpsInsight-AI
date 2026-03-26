from __future__ import annotations

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

RAW_PATH = Path("data/raw/orders.csv")

PRODUCTS = {
    "P100": ("Safety Gloves", 12.50),
    "P200": ("Protective Mask", 6.75),
    "P300": ("Safety Goggles", 18.00),
    "P400": ("Protective Gown", 9.25),
    "P500": ("Shoe Covers", 4.50),
}

REGIONS = ["South", "Northeast", "Midwest", "West"]
STATUSES = ["COMPLETED", "COMPLETED", "COMPLETED", "PENDING", "CANCELLED"]


def generate_orders(rows: int = 5000, seed: int = 42) -> Path:
    random.seed(seed)
    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    start = datetime(2026, 1, 1, 8, 0, 0)

    records = []
    for i in range(1, rows + 1):
        product_id = random.choice(list(PRODUCTS))
        product_name, base_price = PRODUCTS[product_id]
        quantity = random.randint(1, 40)
        unit_price = round(base_price * random.uniform(0.92, 1.08), 2)
        order_time = start + timedelta(
            days=random.randint(0, 210),
            minutes=random.randint(0, 24 * 60 - 1),
        )
        processing_minutes = max(5, int(random.gauss(90, 28)))
        status = random.choice(STATUSES)
        region = random.choice(REGIONS)
        customer_id = f"C{random.randint(1, 400):04d}"

        records.append({
            "order_id": f"O{i:06d}",
            "customer_id": customer_id,
            "product_id": product_id,
            "product_name": product_name,
            "region": region,
            "order_ts": order_time.isoformat(),
            "quantity": quantity,
            "unit_price": unit_price,
            "processing_minutes": processing_minutes,
            "status": status,
        })

    # Deliberately inject realistic data-quality and operational issues.
    for idx in range(0, min(20, len(records)), 2):
        records[idx]["region"] = ""
    for idx in range(21, min(41, len(records)), 3):
        records[idx]["quantity"] = -1
    for idx in range(55, min(75, len(records)), 4):
        records[idx]["unit_price"] = round(records[idx]["unit_price"] * 4.5, 2)
    for idx in range(90, min(110, len(records)), 3):
        records[idx]["processing_minutes"] = 420
    if len(records) > 150:
        duplicate = records[149].copy()
        records.append(duplicate)

    with RAW_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)

    return RAW_PATH


if __name__ == "__main__":
    path = generate_orders()
    print(f"Generated sample data: {path}")
