#!/usr/bin/env python3
"""Data loader: Data center locations from CSV.

Output: array of { name, operator, ticker, state, lat, lon, mw, status } records.
"""
import csv
import json
import sys
from pathlib import Path

CSV_PATH = Path(__file__).parent.parent.parent.parent / "data" / "external" / "data_center_locations.csv"

records = []
with open(CSV_PATH) as f:
    reader = csv.DictReader(f)
    for row in reader:
        lat = row.get("lat", "")
        lon = row.get("lon", "")
        if not lat or not lon:
            continue
        try:
            lat_f = float(lat)
            lon_f = float(lon)
        except (ValueError, TypeError):
            continue

        mw = row.get("announced_mw", "")
        try:
            mw_f = int(float(mw)) if mw else 200  # default 200 MW
        except (ValueError, TypeError):
            mw_f = 200

        records.append({
            "name": row.get("name", ""),
            "operator": row.get("operator", ""),
            "ticker": row.get("ticker", ""),
            "state": row.get("state", ""),
            "lat": lat_f,
            "lon": lon_f,
            "mw": mw_f,
            "status": row.get("status", ""),
        })

print(json.dumps(records))
