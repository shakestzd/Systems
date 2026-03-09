#!/usr/bin/env python3
"""Data loader: QCEW state employment for NAICS 518210.

Output: array of { state, fips, employment, year } records.
Sorted by employment descending. Only disclosed records.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.data.bls import fetch_qcew_state

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

# State FIPS to numeric ID (for TopoJSON matching)
STATE_FIPS_ID = {
    "01": 1, "02": 2, "04": 4, "05": 5, "06": 6, "08": 8, "09": 9,
    "10": 10, "11": 11, "12": 12, "13": 13, "16": 16, "17": 17, "18": 18,
    "19": 19, "20": 20, "21": 21, "22": 22, "23": 23, "24": 24, "25": 25,
    "26": 26, "27": 27, "28": 28, "29": 29, "30": 30, "31": 31, "32": 32,
    "33": 33, "34": 34, "35": 35, "36": 36, "37": 37, "38": 38, "39": 39,
    "40": 40, "41": 41, "42": 42, "44": 44, "45": 45, "46": 46, "47": 47,
    "48": 48, "49": 49, "50": 50, "51": 51, "53": 53, "54": 54, "55": 55,
    "56": 56,
}

records = []
try:
    # Try most recent year first
    for yr in [2024, 2023, 2022]:
        try:
            df = fetch_qcew_state("518210", yr)
            if not df.empty:
                df["state_code"] = df["area_fips"].str[:2]
                df["state"] = df["state_code"].map(STATE_FIPS)
                df["state_id"] = df["state_code"].map(STATE_FIPS_ID)
                df = df.dropna(subset=["annual_avg_employment", "state"])
                df = df[df["disclosure_code"].fillna("") == ""]
                df = df.sort_values("annual_avg_employment", ascending=False)

                for _, row in df.iterrows():
                    records.append({
                        "state": row["state"],
                        "fips": row["state_code"],
                        "stateId": int(row["state_id"]) if row["state_id"] else None,
                        "employment": int(row["annual_avg_employment"]),
                        "year": yr,
                    })
                break  # Use most recent available year
        except Exception:
            continue
except Exception:
    pass

print(json.dumps(records))
