#!/usr/bin/env python3
"""Data loader: OEWS wage data for 15 SOC codes, 2019-2024.

Output: array of { year, soc, label, group, a_mean } records.
group is "tech" or "trades".
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.data.bls import SOC_CODES_TECHNICAL, SOC_CODES_TRADES, fetch_oews_soc

try:
    wages = fetch_oews_soc(years=list(range(2019, 2025)))
except Exception:
    # Output empty array if download fails
    print(json.dumps([]))
    sys.exit(0)

if wages.empty:
    print(json.dumps([]))
    sys.exit(0)

w = wages.dropna(subset=["a_mean"])
w = w[w["o_group"] == "detailed"]

# Determine completeness — but exempt focus codes
all_years = sorted(w["year"].unique())
complete = w.groupby("occ_code")["year"].nunique() >= max(1, len(all_years) - 1)
complete_codes = set(complete[complete].index)
focus_codes = {"15-1252", "47-2111"}

all_codes = {**SOC_CODES_TECHNICAL, **SOC_CODES_TRADES}

records = []
for soc, label in all_codes.items():
    if soc not in complete_codes and soc not in focus_codes:
        continue
    soc_data = w[w["occ_code"] == soc].sort_values("year")
    if soc_data.empty:
        continue
    group = "tech" if soc in SOC_CODES_TECHNICAL else "trades"
    for _, row in soc_data.iterrows():
        records.append({
            "year": int(row["year"]),
            "soc": soc,
            "label": label,
            "group": group,
            "a_mean": int(row["a_mean"]),
        })

print(json.dumps(records))
