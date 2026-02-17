from __future__ import annotations
import pandas as pd
import yfinance as yf


def get_prices(tickers: list[str], period: str = "5y", interval: str = "1d") -> pd.DataFrame:
    """Download historical adjusted close prices for tickers."""
    data = yf.download(tickers=tickers, period=period, interval=interval, auto_adjust=True, progress=False)
    if isinstance(data, pd.DataFrame) and "Adj Close" in data.columns:
        prices = data["Adj Close"].copy()
    else:
        # yfinance returns a single-level columns when one ticker
        prices = data.copy()
    return prices