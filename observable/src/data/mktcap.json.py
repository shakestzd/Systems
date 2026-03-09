#!/usr/bin/env python3
"""Data loader: Market cap gains Jan 2023 → Feb 2026 for the Magnificent 7."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.data.db import query

mkt = query("""
    SELECT ticker, company, date, market_cap_t
    FROM energy_data.mag7_market_caps ORDER BY ticker, date
""")

early = mkt[mkt["date"] == "2023-01-03"].set_index("ticker")
late  = mkt[mkt["date"] == "2026-02-14"].set_index("ticker")

records = []
for ticker in sorted(early.index):
    if ticker not in late.index:
        continue
    row = {
        "ticker": ticker,
        "company": early.loc[ticker, "company"],
        "mkt_cap_2023_t": round(float(early.loc[ticker, "market_cap_t"]), 2),
        "mkt_cap_2026_t": round(float(late.loc[ticker, "market_cap_t"]), 2),
        "gain_t": round(float(late.loc[ticker, "market_cap_t"]) - float(early.loc[ticker, "market_cap_t"]), 2),
    }
    records.append(row)

# Sort descending by gain
records.sort(key=lambda r: r["gain_t"], reverse=True)

print(json.dumps(records))
