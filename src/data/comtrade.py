from __future__ import annotations

import pandas as pd
import requests

# Simple UN Comtrade API wrapper for HS codes
BASE = "https://comtradeapi.un.org/public/v1/preview/flow"


def hs_trade(
    flow: str,
    reporter: str,
    partner: str,
    period: str,
    cmd_code: str,
    token: str | None = None,
) -> pd.DataFrame:
    """Fetch HS trade data (preview API). flow: import or export; period: YYYY; cmd_code: HS code.
    Note: Production API may require token; this uses preview endpoints where possible.
    """
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    params = {
        "flowCode": flow.lower(),
        "period": period,
        "reporter": reporter,
        "partner": partner,
        "cmdCode": cmd_code,
    }
    r = requests.get(BASE, params=params, headers=headers, timeout=60)
    r.raise_for_status()
    j = r.json()
    data = j.get("data", [])
    if not data:
        return pd.DataFrame()
    df = pd.json_normalize(data)
    # Select common fields
    cols = [
        "period",
        "reporterCode",
        "reporterName",
        "partnerCode",
        "partnerName",
        "cmdCode",
        "cmdDesc",
        "primaryValue",
        "netWgt",
        "qty",
    ]
    cols = [c for c in cols if c in df.columns]
    return df[cols]
