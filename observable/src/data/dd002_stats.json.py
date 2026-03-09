#!/usr/bin/env python3
"""Data loader: Combined stats for DD-002 prose interpolation.

Mirrors the stats cells from all three DD-002 notebooks so the Observable
page prose can reference the same numbers.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.data.db import query

# ── Queue summary ────────────────────────────────────────────────────────
queue_summary = query("""
    SELECT year, generation_gw, storage_gw, total_gw, completion_pct, withdrawal_pct,
           solar_gw, wind_gw, gas_gw, other_gw
    FROM energy_data.lbnl_queue_summary
    ORDER BY year
""")

q_latest = queue_summary.iloc[-1]
q_prev = queue_summary.iloc[-2]
queue_yoy_pct = (q_latest["total_gw"] / q_prev["total_gw"] - 1) * 100

# ── Installed capacity ───────────────────────────────────────────────────
installed = float(query("""
    SELECT SUM(nameplate_capacity_mw) / 1000.0 AS installed_gw
    FROM energy_data.eia860_generators
    WHERE status = 'OP'
""").iloc[0, 0])

# ── Cost allocation ──────────────────────────────────────────────────────
cost_alloc = query("""
    SELECT year, region, cost_category, cost_bn, sort_order, is_total, project_count,
           socialized_pct, is_estimate, source, source_detail
    FROM energy_data.dd002_cost_allocation
    ORDER BY year, sort_order
""")
cost_total = cost_alloc[cost_alloc["is_total"]].iloc[-1]

# ── Citations ────────────────────────────────────────────────────────────
cite_raw = query("SELECT key, value FROM energy_data.source_citations")
citations = dict(zip(cite_raw["key"], cite_raw["value"]))

# ── Electricity price ────────────────────────────────────────────────────
elec_price = float(query("""
    SELECT value AS price
    FROM energy_data.fred_series
    WHERE series_id = 'APU000072610'
    ORDER BY date DESC LIMIT 1
""").iloc[0, 0])
avg_monthly_bill = round(elec_price * 886)
avg_annual_bill = avg_monthly_bill * 12

# ── EIA generation stats ────────────────────────────────────────────────
eia_recent = query("""
    SELECT fuel_category, SUM(nameplate_capacity_mw) / 1000.0 AS gw
    FROM energy_data.eia860_generators
    WHERE status = 'OP' AND operating_year >= 2020
    GROUP BY fuel_category
""")
by_fuel = dict(zip(eia_recent["fuel_category"], eia_recent["gw"]))
total_gw = sum(by_fuel.values())

# ── Capacity factors ─────────────────────────────────────────────────────
cap_factors = {
    "solar": 0.25, "wind": 0.35, "gas_cc": 0.57,
    "gas_ct": 0.12, "nuclear": 0.93,
}

# ── Build stats dict ─────────────────────────────────────────────────────
stats = {
    # Queue
    "queue_total_gw": int(q_latest["total_gw"]),
    "queue_gen_gw": int(q_latest["generation_gw"]),
    "queue_storage_gw": int(q_latest["storage_gw"]),
    "median_years": int(citations.get("queue_median_years", 5)),
    "completion_pct": int(q_latest["completion_pct"]),
    "queue_yoy_pct": round(queue_yoy_pct),
    "queue_yoy_abs_pct": abs(round(queue_yoy_pct)),
    "installed_gw": round(installed),
    "queue_ratio": round(q_latest["total_gw"] / installed, 1),

    # Cost
    "ucs_cost_bn": round(float(cost_total["cost_bn"]), 2),
    "ucs_projects": int(cost_total["project_count"]),
    "ucs_socialized_pct": int(cost_total["socialized_pct"]),

    # Virginia
    "va_bill_annual": int(citations.get("va_bill_annual_2040", 444)),
    "va_bill_monthly": round(float(citations.get("va_bill_annual_2040", 444)) / 12),
    "va_capacity_pct": int(citations.get("va_capacity_share_americas_pct", 70)),
    "avg_monthly_bill": avg_monthly_bill,
    "avg_annual_bill": avg_annual_bill,
    "avg_bill_10pct": round(avg_annual_bill * 0.1),

    # Generation mix
    "total_gw": round(total_gw),
    "solar_gw": round(by_fuel.get("solar", 0)),
    "wind_gw": round(by_fuel.get("wind", 0)),
    "battery_gw": round(by_fuel.get("battery", 0)),
    "gas_cc_gw": round(by_fuel.get("gas_cc", 0)),
    "gas_ct_gw": round(by_fuel.get("gas_ct", 0)),
    "nuclear_gw": round(by_fuel.get("nuclear", 0)),
    "solar_share_pct": round(by_fuel.get("solar", 0) / total_gw * 100),
    "solar_cf": cap_factors["solar"],
    "gas_cc_cf": cap_factors["gas_cc"],

    # Simulation baseline (from notebook 03)
    "spill_start_pct": 91,
    "spill_end_pct": 78,
    "cost_start": 40,
    "cost_end": 21,
}

print(json.dumps(stats))
