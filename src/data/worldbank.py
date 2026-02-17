from __future__ import annotations
from typing import Optional
import pandas as pd
import requests

BASE = "https://api.worldbank.org/v2"


def wb_indicator(indicator: str, country: str = "all", date: Optional[str] = None, per_page: int = 10000) -> pd.DataFrame:
    """Fetch a World Bank indicator for a country (or all). Returns tidy DataFrame.
    date format example: "2000:2024"
    """
    params = {"format": "json", "per_page": per_page}
    if date:
        params["date"] = date
    url = f"{BASE}/country/{country}/indicator/{indicator}"
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    if not isinstance(data, list) or len(data) < 2:
        return pd.DataFrame()
    rows = data[1]
    df = pd.DataFrame(rows)
    # Normalize fields
    df["country"] = df["country"].apply(lambda x: x.get("value") if isinstance(x, dict) else x)
    df["date"] = pd.to_numeric(df["date"], errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df[["country", "date", "value"]]