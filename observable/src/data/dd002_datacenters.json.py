#!/usr/bin/env python3
"""Data loader: Data center locations for DD-002 plant map overlay.

Reads from data/external/data_center_locations.csv and outputs JSON
with lat/lon, operator, capacity, and status for frontier AI facilities.
"""
import csv
import json
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.parent
csv_path = project_root / "data" / "external" / "data_center_locations.csv"

if not csv_path.exists():
    print(json.dumps([]))
    sys.exit(0)

centers = []
with open(csv_path) as f:
    reader = csv.DictReader(f)
    for row in reader:
        lat = row.get("lat", "")
        lon = row.get("lon", "")
        if not lat or not lon:
            continue
        try:
            lat_f = float(lat)
            lon_f = float(lon)
        except ValueError:
            continue

        mw = row.get("announced_mw", "")
        try:
            mw_f = float(mw)
        except (ValueError, TypeError):
            mw_f = 100  # default for unknown

        centers.append({
            "name": row.get("name", ""),
            "operator": row.get("operator", ""),
            "ticker": row.get("ticker", ""),
            "state": row.get("state", ""),
            "lat": round(lat_f, 3),
            "lon": round(lon_f, 3),
            "mw": round(mw_f),
            "status": row.get("status", "unknown"),
        })

print(json.dumps(centers))
