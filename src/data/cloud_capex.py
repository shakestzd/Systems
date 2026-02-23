"""Cloud capex-to-revenue ratio computations.

Provides a single function for computing per-company annual capex-to-cloud-revenue
ratios from the quarterly cloud revenue and annual capex DataFrames used in the
DD-001 notebooks.
"""

from __future__ import annotations

import pandas as pd


def capex_to_revenue_ratio(
    capex_annual: pd.DataFrame,
    cloud_rev: pd.DataFrame,
    tickers: list[str],
    years: list[int],
) -> pd.DataFrame:
    """Compute per-company capex-to-cloud-revenue ratio.

    Parameters
    ----------
    capex_annual : DataFrame with columns [ticker, year, capex_bn]
    cloud_rev    : DataFrame with columns [ticker, quarter, revenue_bn]
                   where quarter is formatted "YYYY-QN" (e.g. "2024-Q1")
    tickers      : list of ticker symbols to include
    years        : list of integer years to include in output

    Returns
    -------
    DataFrame with columns [ticker, year, capex_bn, revenue_bn, ratio],
    sorted by [ticker, year]. Raises ValueError if any requested ticker
    has no data after the merge.
    """
    _expected_pairs = [(t, y) for t in tickers for y in years]

    # Step 1: Filter quarterly revenue to requested tickers and years
    _cloud = cloud_rev[cloud_rev["ticker"].isin(tickers)].copy()
    _cloud["year"] = _cloud["quarter"].str[:4].astype(int)
    _cloud = _cloud[_cloud["year"].isin(years)]

    # Step 2: Validate quarter coverage — each (ticker, year) must have exactly 4 quarters
    _qcounts = _cloud.groupby(["ticker", "year"])["quarter"].count()
    _incomplete = [
        (t, y, int(_qcounts.get((t, y), 0)))
        for t, y in _expected_pairs
        if _qcounts.get((t, y), 0) != 4
    ]
    if _incomplete:
        raise ValueError(
            f"capex_to_revenue_ratio: incomplete quarterly revenue coverage — "
            f"expected 4 quarters per (ticker, year), got: {_incomplete}"
        )

    # Step 3: Aggregate to annual
    cloud_annual = _cloud.groupby(["ticker", "year"])["revenue_bn"].sum().reset_index()

    # Step 4: Filter capex to requested tickers and years, check coverage
    capex_filtered = capex_annual[
        capex_annual["ticker"].isin(tickers) & capex_annual["year"].isin(years)
    ].copy()
    _capex_pairs = set(zip(capex_filtered["ticker"], capex_filtered["year"]))
    _missing_capex = [(t, y) for t, y in _expected_pairs if (t, y) not in _capex_pairs]
    if _missing_capex:
        raise ValueError(
            f"capex_to_revenue_ratio: missing capex data for (ticker, year) pairs: "
            f"{_missing_capex}"
        )

    # Step 5: Inner merge and compute ratio
    merged = capex_filtered.merge(cloud_annual, on=["ticker", "year"], how="inner")
    merged["ratio"] = merged["capex_bn"] / merged["revenue_bn"]

    # Step 6: Return sorted by [ticker, year]
    return merged[["ticker", "year", "capex_bn", "revenue_bn", "ratio"]].sort_values(
        ["ticker", "year"]
    ).reset_index(drop=True)
