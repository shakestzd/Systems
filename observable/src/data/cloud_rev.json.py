#!/usr/bin/env python3
"""Data loader: Quarterly cloud revenue for AWS, Azure (Intelligent Cloud), Google Cloud."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.data.db import query

cloud = query("""
    SELECT ticker, segment, quarter, revenue_bn, yoy_growth_pct
    FROM energy_data.cloud_revenue
    WHERE ticker IN ('AMZN', 'GOOGL', 'MSFT')
    ORDER BY quarter, ticker
""")

records = []
for _, row in cloud.iterrows():
    records.append({
        "ticker": row["ticker"],
        "segment": row["segment"],
        "quarter": row["quarter"],
        "revenue_bn": round(float(row["revenue_bn"]), 1),
        "yoy_growth_pct": round(float(row["yoy_growth_pct"]), 1) if row["yoy_growth_pct"] is not None else None,
    })

print(json.dumps(records))
