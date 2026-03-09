#!/usr/bin/env python3
"""Data loader: Computed stats dict for DD-003 prose interpolation.

Mirrors the stats cell in notebooks/dd003_labor_markets/01_who_gets_hired.py.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import pandas as pd
from src.data.bls import SOC_CODES_TECHNICAL, SOC_CODES_TRADES, fetch_oews_soc, fetch_qcew_state
from src.data.db import query

# ── State FIPS lookup ────────────────────────────────────────────────────────
STATE_FIPS = {
    "01": "Alabama", "02": "Alaska", "04": "Arizona", "05": "Arkansas",
    "06": "California", "08": "Colorado", "09": "Connecticut", "10": "Delaware",
    "11": "D.C.", "12": "Florida", "13": "Georgia", "16": "Idaho",
    "17": "Illinois", "18": "Indiana", "19": "Iowa", "20": "Kansas",
    "21": "Kentucky", "22": "Louisiana", "23": "Maine", "24": "Maryland",
    "25": "Massachusetts", "26": "Michigan", "27": "Minnesota", "28": "Mississippi",
    "29": "Missouri", "30": "Montana", "31": "Nebraska", "32": "Nevada",
    "33": "New Hampshire", "34": "New Jersey", "35": "New Mexico", "36": "New York",
    "37": "North Carolina", "38": "North Dakota", "39": "Ohio", "40": "Oklahoma",
    "41": "Oregon", "42": "Pennsylvania", "44": "Rhode Island", "45": "South Carolina",
    "46": "South Dakota", "47": "Tennessee", "48": "Texas", "49": "Utah",
    "50": "Vermont", "51": "Virginia", "53": "Washington", "54": "West Virginia",
    "55": "Wisconsin", "56": "Wyoming",
}

# ── Employment index from FRED ───────────────────────────────────────────────
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

tech_col = "CES6054150001"
const_col = "USCONS"
latest = empl_idx.index.max()
capex_date = pd.Timestamp("2023-01-01")


def idx_val(col, date):
    if col not in empl_idx.columns:
        return None
    if date not in empl_idx.index:
        i = empl_idx.index.get_indexer([date], method="nearest")[0]
        return float(empl_idx.iloc[i][col])
    return float(empl_idx.loc[date, col])


tech_latest = idx_val(tech_col, latest)
const_latest = idx_val(const_col, latest)
tech_at_capex = idx_val(tech_col, capex_date)

stats = {
    "tech_index_latest": round(tech_latest, 1) if tech_latest else 0.0,
    "const_index_latest": round(const_latest, 1) if const_latest else 0.0,
    "tech_change": round(tech_latest - 100, 1) if tech_latest else 0.0,
    "const_change": round(const_latest - 100, 1) if const_latest else 0.0,
    "tech_since_capex": (
        round((tech_latest / tech_at_capex - 1) * 100, 1)
        if tech_latest and tech_at_capex
        else 0.0
    ),
    "latest_date": latest.strftime("%B %Y"),
}

# ── OEWS wage stats ──────────────────────────────────────────────────────────
try:
    wages = fetch_oews_soc(years=list(range(2019, 2025)))
    if not wages.empty:
        w = wages.dropna(subset=["a_mean"])

        def wage(soc, year):
            r = w[(w["occ_code"] == soc) & (w["year"] == year)]
            return int(r["a_mean"].iloc[0]) if not r.empty else 0

        e24 = wage("47-2111", 2024)
        e19 = wage("47-2111", 2019)
        s24 = wage("15-1252", 2024)
        s19 = wage("15-1252", 2019)

        stats["elec_wage_2024"] = e24
        stats["elec_wage_2019"] = e19
        stats["sw_wage_2024"] = s24
        stats["sw_wage_2019"] = s19
        stats["elec_wage_pct"] = round((e24 / e19 - 1) * 100, 1) if e19 > 0 else 0.0
        stats["sw_wage_pct"] = round((s24 / s19 - 1) * 100, 1) if s19 > 0 else 0.0
        stats["wage_ratio"] = round(s24 / e24, 1) if e24 > 0 else 0.0
except Exception:
    pass

# ── QCEW state employment ───────────────────────────────────────────────────
try:
    qcew_years = []
    for yr in [2024, 2023, 2022]:
        try:
            df = fetch_qcew_state("518210", yr)
            qcew_years.append(df)
        except Exception:
            pass

    if qcew_years:
        qcew = pd.concat(qcew_years, ignore_index=True)
        recent_yr = int(qcew["year"].max())
        recent = qcew[qcew["year"] == recent_yr].copy()
        recent["state"] = recent["area_fips"].str[:2].map(STATE_FIPS)
        recent = recent.dropna(subset=["annual_avg_employment", "state"])
        recent = recent[recent["disclosure_code"].fillna("") == ""]
        recent = recent.sort_values("annual_avg_employment", ascending=False)

        if not recent.empty:
            top = recent.iloc[0]
            stats["top_state"] = top["state"]
            stats["top_count"] = int(top["annual_avg_employment"])
            stats["dc_year"] = recent_yr
            # Top 5 total
            stats["top5_total"] = int(recent.head(5)["annual_avg_employment"].sum())
            stats["total_dc_empl"] = int(recent["annual_avg_employment"].sum())
except Exception:
    pass

# Workforce reveal stats (approximate from BLS OES national estimates)
# These are rough employment estimates used for the unit chart
stats["tech_workers_k"] = 300   # ~300K in core AI tech occupations
stats["trades_workers_k"] = 500  # ~500K in construction trades supporting DC buildout

print(json.dumps(stats))
