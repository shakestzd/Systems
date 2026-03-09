#!/usr/bin/env python3
"""Data loader: PJM zone demand requests for DD-004 small multiples chart.

Filters to request_type='demand', years 2026-2046.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.data.db import query

df = query("""
    SELECT zone, year, requested_mw
    FROM energy_data.dd004_pjm_zone_demand
    WHERE request_type = 'demand'
    ORDER BY zone, year
""")

records = []
for _, row in df.iterrows():
    records.append({
        "zone": row["zone"],
        "year": int(row["year"]),
        "mw": round(float(row["requested_mw"]), 1),
    })

print(json.dumps(records))
