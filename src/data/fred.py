"""FRED data access — two modes.

- fetch_csv(): Direct CSV download, no API key needed. Good for notebooks.
- get_series() / get_multiple(): Uses fredapi, requires FRED_API_KEY.
"""

from __future__ import annotations

import io
import urllib.request
from typing import Optional

import pandas as pd


# ── CSV-based (no API key) ────────────────────────────────────────────


def fetch_csv(series_id: str) -> pd.DataFrame:
    """Fetch a FRED series via direct CSV download (no API key required).

    Returns a DataFrame with DatetimeIndex and one column named after
    the series ID.
    """
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    response = urllib.request.urlopen(url)
    df = pd.read_csv(
        io.BytesIO(response.read()),
        index_col="observation_date",
        parse_dates=True,
    )
    return df


def fetch_multiple_csv(series_ids: list[str]) -> dict[str, pd.DataFrame]:
    """Fetch multiple FRED series via CSV. Returns dict of series_id -> DataFrame."""
    return {sid: fetch_csv(sid) for sid in series_ids}


# ── fredapi-based (requires API key) ─────────────────────────────────


def get_series(series_id: str, api_key: Optional[str] = None) -> pd.Series:
    """Fetch a FRED series by ID and return as a pandas Series indexed by date."""
    from fredapi import Fred

    fred = Fred(api_key=api_key)
    data = fred.get_series(series_id)
    data.name = series_id
    return data


def get_multiple(series_ids: list[str], api_key: Optional[str] = None) -> pd.DataFrame:
    """Fetch multiple FRED series and combine into a DataFrame."""
    df = pd.DataFrame({sid: get_series(sid, api_key=api_key) for sid in series_ids})
    return df