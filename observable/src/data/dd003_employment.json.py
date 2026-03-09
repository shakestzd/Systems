#!/usr/bin/env python3
"""Data loader: FRED employment series indexed to Jan 2020 = 100.

Four sector series for DD-003 employment index chart.
Output: array of { date, series, label, value } records.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import pandas as pd
from src.data.db import query

SERIES_LABELS = {
    "CES6054150001": "Computer Systems Design",
    "USCONS": "Construction",
    "USINFO": "Information",
    "MANEMP": "Manufacturing",
}

fred = query("""
    SELECT series_id, CAST(date AS DATE) AS date, value
    FROM energy_data.fred_series
    WHERE series_id IN ('CES6054150001', 'USCONS', 'USINFO', 'MANEMP')
    AND CAST(date AS DATE) >= '2019-01-01'
    ORDER BY series_id, date
""")

empl_wide = fred.pivot(index="date", columns="series_id", values="value")
idx = pd.to_datetime(empl_wide.index)
if idx.tz is not None:
    idx = idx.tz_localize(None)
empl_wide.index = idx.to_period("M").to_timestamp()
empl_wide = empl_wide.sort_index()

base_date = pd.Timestamp("2020-01-01")
base = empl_wide.loc[base_date]
empl_idx = (empl_wide / base * 100).dropna(how="all")

records = []
for col in empl_idx.columns:
    label = SERIES_LABELS.get(col, col)
    for date, val in empl_idx[col].dropna().items():
        records.append({
            "date": date.strftime("%Y-%m-%d"),
            "series": col,
            "label": label,
            "value": round(float(val), 2),
        })

print(json.dumps(records))
