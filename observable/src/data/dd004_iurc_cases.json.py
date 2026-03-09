#!/usr/bin/env python3
"""Data loader: IURC regulatory cases for DD-004 regulatory timeline."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.data.db import query

df = query("""
    SELECT cause_number, company, case_type, filed_date, order_date, status,
           case_title, key_metric, key_metric_value, key_metric_unit,
           ratepayer_impact, notes
    FROM energy_data.dd004_iurc_cases
    ORDER BY cause_number, key_metric
""")

records = []
for _, row in df.iterrows():
    records.append({
        "cause": row["cause_number"],
        "company": row.get("company", ""),
        "type": row.get("case_type", ""),
        "filed": str(row["filed_date"]) if row.get("filed_date") else None,
        "ordered": str(row["order_date"]) if row.get("order_date") else None,
        "status": row.get("status", ""),
        "title": row.get("case_title", ""),
        "metric": row.get("key_metric", ""),
        "value": float(row["key_metric_value"]) if row.get("key_metric_value") else None,
        "unit": row.get("key_metric_unit", ""),
        "impact": row.get("ratepayer_impact", ""),
        "notes": row.get("notes", ""),
    })

print(json.dumps(records))
