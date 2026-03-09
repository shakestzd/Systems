#!/usr/bin/env python3
"""Data loader: EIA Form 860 generation data for DD-002 charts.

Produces three arrays:
  - gen_mix: yearly stacked bar data (year, fuel, gw)
  - cap_factor: nameplate vs effective by fuel
  - plants: individual plant locations for the map
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.data.db import query

# ── Generation mix by year + fuel ────────────────────────────────────────
gen_raw = query("""
    SELECT fuel_category, operating_year, SUM(nameplate_capacity_mw) / 1000.0 AS gw
    FROM energy_data.eia860_generators
    WHERE status = 'OP'
      AND operating_year >= 2018
      AND operating_year IS NOT NULL
      AND nameplate_capacity_mw > 0
    GROUP BY fuel_category, operating_year
    ORDER BY operating_year, fuel_category
""")

gen_mix = []
for _, row in gen_raw.iterrows():
    gen_mix.append({
        "year": int(row["operating_year"]),
        "fuel": row["fuel_category"],
        "gw": round(float(row["gw"]), 2),
    })

# ── Capacity factor comparison ───────────────────────────────────────────
cap_factors = {
    "solar": 0.25, "wind": 0.35, "gas_cc": 0.57,
    "gas_ct": 0.12, "nuclear": 0.93,
}

by_fuel_since2020 = query("""
    SELECT fuel_category, SUM(nameplate_capacity_mw) / 1000.0 AS gw
    FROM energy_data.eia860_generators
    WHERE status = 'OP' AND operating_year >= 2020
    GROUP BY fuel_category
""")

cap_factor = []
for _, row in by_fuel_since2020.iterrows():
    fuel = row["fuel_category"]
    if fuel in cap_factors:
        nameplate = round(float(row["gw"]), 1)
        cap_factor.append({
            "fuel": fuel,
            "nameplate": nameplate,
            "effective": round(nameplate * cap_factors[fuel], 1),
            "cf": cap_factors[fuel],
        })

# ── Plant locations for map (since 2020, > 50 MW) ───────────────────────
plants_raw = query("""
    SELECT fuel_category, operating_year, state, latitude, longitude,
           nameplate_capacity_mw
    FROM energy_data.eia860_generators
    WHERE status = 'OP'
      AND operating_year >= 2020
      AND nameplate_capacity_mw >= 50
      AND latitude IS NOT NULL
      AND longitude IS NOT NULL
""")

plants = []
for _, row in plants_raw.iterrows():
    plants.append({
        "fuel": row["fuel_category"],
        "year": int(row["operating_year"]),
        "state": row["state"],
        "lat": round(float(row["latitude"]), 3),
        "lon": round(float(row["longitude"]), 3),
        "mw": round(float(row["nameplate_capacity_mw"]), 1),
    })

print(json.dumps({
    "gen_mix": gen_mix,
    "cap_factor": cap_factor,
    "plants": plants,
}))
