#!/usr/bin/env python3
"""Data loader: Interconnection queue data for DD-002.

Produces:
  - region: queue backlog by ISO/RTO region
  - composition: yearly queue composition by fuel type
  - cost_alloc: waterfall chart data
  - lag: company-region exposure proxy
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.data.db import query

# ── Queue by region ──────────────────────────────────────────────────────
queue_region = query("""
    SELECT year, region, queue_gw, is_major_dc_region, source, source_detail
    FROM energy_data.dd002_queue_region_backlog
    WHERE year = (SELECT MAX(year) FROM energy_data.dd002_queue_region_backlog)
    ORDER BY queue_gw DESC
""")

region = []
for _, row in queue_region.iterrows():
    region.append({
        "region": row["region"],
        "queue_gw": round(float(row["queue_gw"])),
        "is_dc_region": bool(row["is_major_dc_region"]),
    })

# ── Queue composition by year ────────────────────────────────────────────
queue_summary = query("""
    SELECT year, solar_gw, storage_gw AS battery_gw, wind_gw, gas_gw, other_gw
    FROM energy_data.lbnl_queue_summary
    ORDER BY year
""")

composition = []
for _, row in queue_summary.iterrows():
    for fuel in ["solar_gw", "battery_gw", "wind_gw", "gas_gw", "other_gw"]:
        val = float(row[fuel]) if row[fuel] is not None else 0
        composition.append({
            "year": int(row["year"]),
            "fuel": fuel.replace("_gw", ""),
            "gw": round(val, 1),
        })

# ── Cost allocation waterfall ────────────────────────────────────────────
cost_alloc = query("""
    SELECT cost_category, cost_bn, sort_order, is_total
    FROM energy_data.dd002_cost_allocation
    ORDER BY sort_order
""")

waterfall = []
for _, row in cost_alloc.iterrows():
    waterfall.append({
        "category": row["cost_category"],
        "cost_bn": round(float(row["cost_bn"]), 2),
        "is_total": bool(row["is_total"]),
    })

# ── Company-region lag proxy ─────────────────────────────────────────────
region_weights = query("""
    SELECT ticker, region, allocation_weight
    FROM energy_data.dd002_hyperscaler_region_weights
""")
capex_annual = query("""
    SELECT ticker, YEAR(CAST(date AS DATE)) AS year, SUM(capex_bn) AS capex_bn
    FROM energy_data.hyperscaler_capex
    GROUP BY ticker, YEAR(CAST(date AS DATE))
""")
in_service = query("""
    SELECT state, SUM(nameplate_capacity_mw) / 1000.0 AS in_service_gw
    FROM energy_data.eia860_generators
    WHERE status = 'OP' AND operating_year = 2024 AND state IS NOT NULL
    GROUP BY state
""")

# State-to-region mapping
state_to_region = {}
region_state_map = {
    "PJM": ["DC","DE","IL","IN","KY","MD","MI","NC","NJ","OH","PA","TN","VA","WV"],
    "MISO": ["AR","IA","LA","MN","MS","MO","MT","ND","SD","WI"],
    "CAISO": ["CA"], "SPP": ["KS","NE","NM","OK","WY"], "ERCOT": ["TX"],
    "NYISO": ["NY"], "ISO-NE": ["CT","MA","ME","NH","RI","VT"],
    "Non-ISO West": ["AK","AZ","CO","HI","ID","NV","OR","UT","WA"],
    "Non-ISO Southeast": ["AL","FL","GA","SC"],
}
for rgn, states in region_state_map.items():
    for st in states:
        state_to_region[st] = rgn

in_service["region"] = in_service["state"].map(state_to_region)
in_service_by_region = in_service.groupby("region")["in_service_gw"].sum().to_dict()

queue_gw_map = dict(zip(queue_region["region"], queue_region["queue_gw"]))

capex_latest_year = int(capex_annual["year"].max())
capex_latest = capex_annual[capex_annual["year"] == capex_latest_year]

lag = []
for _, w_row in region_weights.iterrows():
    ticker = w_row["ticker"]
    rgn = w_row["region"]
    weight = float(w_row["allocation_weight"])
    cap_row = capex_latest[capex_latest["ticker"] == ticker]
    if cap_row.empty:
        continue
    capex_bn = float(cap_row.iloc[0]["capex_bn"]) * weight
    q_gw = float(queue_gw_map.get(rgn, 0))
    is_gw = float(in_service_by_region.get(rgn, 1))
    lag.append({
        "ticker": ticker,
        "region": rgn,
        "capex_bn": round(capex_bn, 1),
        "queue_gw": round(q_gw),
        "implied_lag_years": round(q_gw / max(is_gw, 0.1), 1),
    })

lag.sort(key=lambda x: (-x["implied_lag_years"], -x["capex_bn"]))

print(json.dumps({
    "region": region,
    "composition": composition,
    "waterfall": waterfall,
    "lag": lag,
}))
