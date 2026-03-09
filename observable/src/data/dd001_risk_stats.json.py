#!/usr/bin/env python3
"""Data loader: Stats for DD-001/03 Risk and Durability article.

Mirrors the stats cell in notebooks/dd001_capital_reality/03_risk_and_durability.py.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import pandas as pd
from src.data.db import query

TICKERS_6 = ["MSFT", "AMZN", "GOOGL", "META", "ORCL", "NVDA"]

capex_raw = query("""
    SELECT ticker, date, capex_bn FROM energy_data.hyperscaler_capex ORDER BY date, ticker
""")
capex_raw["date"] = pd.to_datetime(capex_raw["date"])
capex_raw["year"] = capex_raw["date"].dt.year
ann6 = (
    capex_raw.groupby(["ticker", "year"])["capex_bn"]
    .sum().reset_index()
)

cite_raw = query("SELECT key, value FROM energy_data.source_citations")
citations = dict(zip(cite_raw["key"], cite_raw["value"]))

stats = {
    "capex_2025": round(float(
        ann6[(ann6["ticker"].isin(TICKERS_6)) & (ann6["year"] == 2025)]["capex_bn"].sum()
    ), 1),

    # SPV / Beignet
    "meta_beignet_financing_bn": int(citations["meta_beignet_financing_bn"]),
    "meta_beignet_exit_year": int(citations["meta_beignet_exit_year"]),
    "beignet_bond_maturity": int(citations["beignet_bond_maturity"]),
    "meta_beignet_lease_years": int(citations["meta_beignet_lease_years"]),
    "meta_louisiana_dc_gw": int(citations["meta_louisiana_dc_gw"]),

    # Neocloud
    "msft_neocloud_total_bn": int(citations["msft_neocloud_total_bn"]),
    "msft_nebius_deal_bn": int(citations["msft_nebius_deal_bn"]),
    "msft_nscale_deal_bn": int(citations["msft_nscale_deal_bn"]),
    "msft_iren_deal_bn": int(citations["msft_iren_deal_bn"]),

    # CoreWeave chain
    "openai_coreweave_commitment_bn": float(citations["openai_coreweave_commitment_bn"]),
    "coreweave_interest_rate_pct": int(citations["coreweave_interest_rate_pct"]),
    "openai_msft_compute_promise_bn": int(citations["openai_msft_compute_promise_bn"]),

    # Geography
    "openai_texas_dc_gw": float(citations["openai_texas_dc_gw"]),
    "aep_gas_share_pct": int(citations["aep_gas_share_pct"]),
    "rainier_gw": float(citations["rainier_gw"]),
}

print(json.dumps(stats))
