#!/usr/bin/env python3
"""Data loader: Data center locations + ACS community data for DD-004 maps.

Uses build_community_dataset() which merges the CSV locations with
Census ACS 5-year county-level socioeconomic data.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import numpy as np
import pandas as pd
from src.data.census import build_community_dataset, compute_derived, fetch_acs5

dc = build_community_dataset()

# National comparison baselines
acs_all = compute_derived(fetch_acs5())
us_median_income = float(pd.to_numeric(acs_all["median_household_income"], errors="coerce").median())
us_median_poverty = float(pd.to_numeric(acs_all["poverty_rate"], errors="coerce").median())

# Per-facility record
records = []
for _, row in dc.iterrows():
    rec = {
        "name": row.get("name", ""),
        "operator": row.get("operator", ""),
        "ticker": row.get("ticker", ""),
        "state": row.get("state", ""),
        "county": row.get("county", ""),
        "county_fips": row.get("county_fips", ""),
        "lat": float(row["lat"]) if pd.notna(row.get("lat")) else None,
        "lon": float(row["lon"]) if pd.notna(row.get("lon")) else None,
        "announced_mw": float(row["announced_mw"]) if pd.notna(row.get("announced_mw")) else None,
        "median_household_income": float(row["median_household_income"]) if pd.notna(row.get("median_household_income")) else None,
        "poverty_rate": float(row["poverty_rate"]) if pd.notna(row.get("poverty_rate")) else None,
        "unemployment_rate": float(row["unemployment_rate"]) if pd.notna(row.get("unemployment_rate")) else None,
    }
    records.append(rec)

# Geo stats summary
_dc = dc.dropna(subset=["median_household_income", "poverty_rate"])
host_income = float(_dc["median_household_income"].median())
host_poverty = float(_dc["poverty_rate"].median())

output = {
    "facilities": records,
    "geo_stats": {
        "n_facilities": len(dc),
        "n_states": int(dc["state"].nunique()),
        "n_operators": int(dc["operator"].nunique()),
        "host_median_income": int(host_income),
        "us_median_income": int(us_median_income),
        "income_premium_pct": round((host_income / us_median_income - 1) * 100),
        "host_median_poverty_pct": round(host_poverty * 100, 1),
        "us_median_poverty_pct": round(us_median_poverty * 100, 1),
        "n_distressed": int((_dc["poverty_rate"] > 0.15).sum()),
        "pct_distressed": round((_dc["poverty_rate"] > 0.15).mean() * 100),
    },
    "us_median_income": us_median_income,
    "us_median_poverty": us_median_poverty,
}

print(json.dumps(output))
