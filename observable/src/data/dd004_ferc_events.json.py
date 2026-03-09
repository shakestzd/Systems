#!/usr/bin/env python3
"""Data loader: FERC + regulatory timeline events for DD-004."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.data.db import query

# Pull from policy_events table plus synthetic DD-004 events
df = query("""
    SELECT event_date, event_name, docket, jurisdiction, description, status
    FROM energy_data.dd002_policy_events
    WHERE docket LIKE 'AD24%' OR docket LIKE 'EL25%'
       OR event_name LIKE '%cost%'
       OR event_name LIKE '%FERC%'
       OR event_name LIKE '%AD24%'
       OR event_name LIKE '%Order 1920%'
       OR event_name LIKE '%Order 2023%'
       OR event_name LIKE '%Talen%'
       OR event_name LIKE '%TMI%'
    ORDER BY event_date
""")

records = []
for _, row in df.iterrows():
    if not row.get("event_name") or not str(row["event_name"]).strip():
        continue
    records.append({
        "date": str(row["event_date"]),
        "name": row["event_name"],
        "docket": row.get("docket", ""),
        "jurisdiction": row.get("jurisdiction", ""),
        "description": row.get("description", ""),
        "status": row.get("status", ""),
    })

# Add key IURC regulatory events if not already present
iurc_events = [
    {
        "date": "2025-02-19",
        "name": "IURC Cause 46097 Final Order",
        "docket": "46097",
        "jurisdiction": "IURC",
        "description": "Large Load Service Rider tariff approved: 70/150 MW tiers, $0.034/kW demand charge, collateral requirement",
        "status": "final_order",
    },
    {
        "date": "2025-11-19",
        "name": "IURC Cause 46217 Final Order",
        "docket": "46217",
        "jurisdiction": "IURC",
        "description": "Oregon NGCC (870 MW) acquisition approved into I&M rate base; 32 years remaining life",
        "status": "final_order",
    },
    {
        "date": "2026-01-28",
        "name": "IURC Cause 46301 EGR Plan",
        "docket": "46301",
        "jurisdiction": "IURC",
        "description": "1,650 MW gas CTs + 1,500 MW clean energy approved; 6,900 MW total ICAP need",
        "status": "final_order",
    },
    {
        "date": "2024-05-16",
        "name": "FERC AD24-11 Policy Statement",
        "docket": "AD24-11",
        "jurisdiction": "FERC",
        "description": "Non-binding policy statement: cost-causation should apply to large loads; upgrade costs may be inappropriately socialized",
        "status": "policy_statement",
    },
]

existing_dockets = {r["docket"] for r in records}
for evt in iurc_events:
    if evt["docket"] not in existing_dockets:
        records.append(evt)

records.sort(key=lambda r: r["date"])

print(json.dumps(records))
