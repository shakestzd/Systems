from __future__ import annotations

import pandas as pd
import yfinance as yf


def get_prices(tickers: list[str], period: str = "5y", interval: str = "1d") -> pd.DataFrame:
    """Download historical adjusted close prices for tickers.

    Uses auto_adjust=True so yfinance returns adjusted Close directly.
    """
    data = yf.download(
        tickers=tickers, period=period, interval=interval,
        auto_adjust=True, progress=False,
    )
    return data.copy()
