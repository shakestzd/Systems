#!/usr/bin/env python3
"""Data loader: Stats for DD-001/02 Conversion Reality article.

Mirrors the stats cell in notebooks/dd001_capital_reality/02_conversion_reality.py.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import pandas as pd
from src.data.db import query

# ── Raw data ──────────────────────────────────────────────────────────────
TICKERS_6 = ["MSFT", "AMZN", "GOOGL", "META", "ORCL", "NVDA"]

capex_raw = query("""
    SELECT ticker, date, capex_bn FROM energy_data.hyperscaler_capex ORDER BY date, ticker
""")
capex_raw["date"] = pd.to_datetime(capex_raw["date"])
capex_raw["year"] = capex_raw["date"].dt.year

capex_annual = (
    capex_raw.groupby(["ticker", "year"])["capex_bn"]
    .sum().reset_index().sort_values(["ticker", "year"])
)
ann6 = capex_annual[capex_annual["ticker"].isin(TICKERS_6)]

guidance_2026 = query("SELECT ticker, year, capex_bn FROM energy_data.capex_guidance")

cite_raw = query("SELECT key, value FROM energy_data.source_citations")
citations = dict(zip(cite_raw["key"], cite_raw["value"]))

# ── PP&E decomposition ────────────────────────────────────────────────────
ppe_schedule = query("""
    SELECT ticker, fiscal_year, category, category_raw, gross_value_m
    FROM energy_data.edgar_ppe_schedule
""")
ppe_2024 = ppe_schedule[ppe_schedule["fiscal_year"] == 2024]
const_cats = ["Construction in progress", "Land and buildings", "Leasehold improvements"]
equip_cats = ["Machinery and equipment", "Servers", "Network equipment", "Right-of-use assets"]
ppe_const = ppe_2024[ppe_2024["category"].isin(const_cats)]["gross_value_m"].sum()
ppe_equip = ppe_2024[ppe_2024["category"].isin(equip_cats)]["gross_value_m"].sum()
ppe_total = ppe_const + ppe_equip

decomp_const_pct = round(ppe_const / ppe_total * 100) if ppe_total > 0 else 42
decomp_equip_pct = 100 - decomp_const_pct

# ── Queue stats ───────────────────────────────────────────────────────────
queue_summary = query("""
    SELECT year, generation_gw, storage_gw, total_gw,
           solar_gw, wind_gw, gas_gw, nuclear_gw, other_gw,
           completion_pct, withdrawal_pct
    FROM energy_data.lbnl_queue_summary ORDER BY year
""")

q_latest = queue_summary.iloc[-1]
q_prev = queue_summary.iloc[-2] if len(queue_summary) > 1 else q_latest

# ── Stats dict ────────────────────────────────────────────────────────────
stats = {
    "capex_2025": round(float(ann6[ann6["year"] == 2025]["capex_bn"].sum()), 1),
    "guidance_2026_point": round(float(
        guidance_2026[guidance_2026["ticker"].isin(TICKERS_6)]["capex_bn"].sum()
    ), 1),

    # PP&E decomposition
    "decomp_const_pct": decomp_const_pct,
    "decomp_equip_pct": decomp_equip_pct,
    "decomp_const_low": max(decomp_const_pct - 8, 30),
    "decomp_const_high": min(decomp_const_pct + 8, 60),

    # Queue
    "queue_total_gw": int(q_latest["total_gw"]),
    "queue_withdrawal_pct": int(q_latest["withdrawal_pct"]),
    "queue_completion_pct": int(q_latest["completion_pct"]),
    "queue_solar_gw": int(q_latest["solar_gw"]),
    "queue_wind_gw": int(q_latest["wind_gw"]),
    "queue_gas_gw": int(q_latest["gas_gw"]),
    "queue_storage_gw": int(q_latest["storage_gw"]),
    "queue_solar_pct": round(q_latest["solar_gw"] / q_latest["total_gw"] * 100),
    "queue_wind_pct": round(q_latest["wind_gw"] / q_latest["total_gw"] * 100),
    "queue_storage_pct": round(q_latest["storage_gw"] / q_latest["total_gw"] * 100),

    # Stargate
    "stargate_announced_bn": int(citations["stargate_announced_bn"]),
    "stargate_initial_bn": int(citations["stargate_initial_bn"]),

    # Project Rainier
    "rainier_gw": float(citations["rainier_gw"]),
    "rainier_dc_planned": int(citations["rainier_dc_planned"]),
    "rainier_dc_built_jun2025": int(citations["rainier_dc_built_jun2025"]),
    "rainier_workers_weekly": int(citations["rainier_workers_weekly"]),
    "rainier_tax_break_sales_bn": int(citations["rainier_tax_break_sales_bn"]),
    "rainier_tax_break_property_bn": int(citations["rainier_tax_break_property_bn"]),
    "aep_indiana_peak_2024_gw": float(citations["aep_indiana_peak_2024_gw"]),
    "aep_indiana_peak_2030_gw": int(citations["aep_indiana_peak_2030_gw"]),
    "aep_gas_share_pct": int(citations["aep_gas_share_pct"]),

    # Citations
    "queue_cohort_2000_2005_pct": int(citations["queue_cohort_2000_2005_pct"]),
    "queue_cohort_2006_2010_pct": int(citations["queue_cohort_2006_2010_pct"]),
    "queue_cohort_2011_2015_pct": int(citations["queue_cohort_2011_2015_pct"]),
    "dc_construction_low_bn": int(citations["dc_construction_low_bn"]),
    "dc_construction_high_bn": int(citations["dc_construction_high_bn"]),
    "analyst_const_pct_low": int(citations["analyst_const_pct_low"]),
}

# AI era totals for lock-in calculation
ai_era = ann6[ann6["year"].isin([2022, 2023, 2024, 2025])]
stats["ai_era_total_bn"] = round(float(ai_era["capex_bn"].sum()), 1)
stats["ai_era_const_bn"] = round(stats["ai_era_total_bn"] * decomp_const_pct / 100)

# Queue time series for the stacked bar chart
queue_ts = []
for _, row in queue_summary.iterrows():
    queue_ts.append({
        "year": int(row["year"]),
        "generation_gw": round(float(row["generation_gw"])),
        "storage_gw": round(float(row["storage_gw"])),
        "total_gw": round(float(row["total_gw"])),
    })

output = {
    "stats": stats,
    "queue_ts": queue_ts,
}

print(json.dumps(output))
