#!/usr/bin/env python3
"""Data loader: annual + quarterly capex and 2026 guidance.

Observable Framework runs this from observable/ and captures stdout as JSON.
"""
import json
import sys
from pathlib import Path

# Add Systems repo root to path so src/ imports work
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import pandas as pd
from src.data.db import query

# --- Quarterly data from DB -------------------------------------------------
capex_raw = query("""
    SELECT ticker, date, capex_bn
    FROM energy_data.hyperscaler_capex ORDER BY date, ticker
""")
capex_raw["date"] = pd.to_datetime(capex_raw["date"])
capex_raw["year"] = capex_raw["date"].dt.year

# Annual aggregation for 4+2 big tech companies
TICKERS_6 = ["MSFT", "AMZN", "GOOGL", "META", "ORCL", "NVDA"]
TICKERS_4 = ["AMZN", "GOOGL", "MSFT", "META"]

capex_annual = (
    capex_raw
    .groupby(["ticker", "year"])["capex_bn"]
    .sum()
    .reset_index()
    .sort_values(["ticker", "year"])
)

# Guidance 2026
guidance = query("""
    SELECT ticker, year, capex_bn FROM energy_data.capex_guidance
""")

# Historical 4-company totals for capex ratio history chart (2015–2021 pre-DB)
HIST_4CO = {
    2015: 22.9, 2016: 30.8, 2017: 40.0, 2018: 64.0,
    2019: 70.9, 2020: 93.5, 2021: 125.5,
}
# Fill in 2022–2025 from DB
ann4 = capex_annual[capex_annual["ticker"].isin(TICKERS_4)]
for yr in [2022, 2023, 2024, 2025]:
    HIST_4CO[yr] = float(ann4[ann4["year"] == yr]["capex_bn"].sum())

# Output shape
out = {
    "annual": capex_annual[capex_annual["ticker"].isin(TICKERS_6)].to_dict(orient="records"),
    "history_4co": [{"year": y, "capex_bn": v} for y, v in sorted(HIST_4CO.items())],
    "guidance": guidance[guidance["ticker"].isin(TICKERS_6)].to_dict(orient="records"),
    "quarterly": [
        {
            "ticker": row["ticker"],
            "date": row["date"].strftime("%Y-%m-%d"),
            "capex_bn": row["capex_bn"],
            "year": int(row["year"]),
        }
        for _, row in capex_raw[capex_raw["ticker"].isin(TICKERS_6)].iterrows()
    ],
}

print(json.dumps(out))
