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
    # Step 1: Aggregate quarterly cloud revenue to annual per ticker
    _cloud = cloud_rev[cloud_rev["ticker"].isin(tickers)].copy()
    _cloud["year"] = _cloud["quarter"].str[:4].astype(int)
    cloud_annual = (
        _cloud.groupby(["ticker", "year"])["revenue_bn"]
        .sum()
        .reset_index()
    )

    # Step 2: Filter capex to requested tickers
    capex_filtered = capex_annual[capex_annual["ticker"].isin(tickers)].copy()

    # Step 3: Inner merge on [ticker, year]
    merged = capex_filtered.merge(cloud_annual, on=["ticker", "year"], how="inner")

    # Step 4: Filter to requested years
    merged = merged[merged["year"].isin(years)]

    # Step 5: Compute ratio
    merged["ratio"] = merged["capex_bn"] / merged["revenue_bn"]

    # Step 6: Check for missing tickers
    present = set(merged["ticker"].unique())
    missing = [t for t in tickers if t not in present]
    if missing:
        raise ValueError(
            f"capex_to_revenue_ratio: no data found for ticker(s) {missing} "
            f"after merge. Check DB coverage for these symbols."
        )

    # Step 7: Return sorted by [ticker, year]
    return merged[["ticker", "year", "capex_bn", "revenue_bn", "ratio"]].sort_values(
        ["ticker", "year"]
    ).reset_index(drop=True)
