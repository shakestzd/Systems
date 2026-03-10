#!/usr/bin/env python3
"""Data loader: Computed stats dict for DD-001/01 prose interpolation.

Mirrors the stats cell in notebooks/dd001_capital_reality/01_markets_and_money.py
so the Observable page prose can reference the same numbers.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import pandas as pd
from src.data.db import query

# ── Raw data ──────────────────────────────────────────────────────────────
capex_raw = query("""
    SELECT ticker, date, capex_bn FROM energy_data.hyperscaler_capex ORDER BY date, ticker
""")
capex_raw["date"] = pd.to_datetime(capex_raw["date"])
capex_raw["year"] = capex_raw["date"].dt.year

TICKERS_6 = ["MSFT", "AMZN", "GOOGL", "META", "ORCL", "NVDA"]
capex_annual = (
    capex_raw
    .groupby(["ticker", "year"])["capex_bn"]
    .sum()
    .reset_index()
)

guidance_2026 = query("SELECT ticker, year, capex_bn FROM energy_data.capex_guidance")

mkt = query("""
    SELECT ticker, company, date, market_cap_t FROM energy_data.mag7_market_caps ORDER BY ticker, date
""")
early = mkt[mkt["date"] == "2023-01-03"].set_index("ticker")
late  = mkt[mkt["date"] == "2026-02-14"].set_index("ticker")
mkt_cap = early[["company"]].copy()
mkt_cap["gain_t"] = late["market_cap_t"] - early["market_cap_t"]
mkt_cap = mkt_cap.reset_index()

cloud_rev = query("""
    SELECT ticker, segment, quarter, revenue_bn, yoy_growth_pct
    FROM energy_data.cloud_revenue ORDER BY quarter, ticker
""")

ocf_data = query("SELECT ticker, ocf_bn FROM energy_data.hyperscaler_ocf")

cite_raw = query("SELECT key, value FROM energy_data.source_citations")
citations = dict(zip(cite_raw["key"], cite_raw["value"]))

# ── Stats dict ────────────────────────────────────────────────────────────
ann6 = capex_annual[capex_annual["ticker"].isin(TICKERS_6)]
cloud_q4 = cloud_rev[cloud_rev["quarter"] == "2025-Q4"]
cloud_2024 = cloud_rev[cloud_rev["quarter"].str.startswith("2024")]
cloud_2025 = cloud_rev[cloud_rev["quarter"].str.startswith("2025")]

stats = {
    "capex_2022": round(float(ann6[ann6["year"] == 2022]["capex_bn"].sum()), 1),
    "capex_2023": round(float(ann6[ann6["year"] == 2023]["capex_bn"].sum()), 1),
    "capex_2024": round(float(ann6[ann6["year"] == 2024]["capex_bn"].sum()), 1),
    "capex_2025": round(float(ann6[ann6["year"] == 2025]["capex_bn"].sum()), 1),
    "guidance_2026": round(float(guidance_2026[guidance_2026["ticker"].isin(TICKERS_6)]["capex_bn"].sum()), 1),
    "mkt_gain_t": round(float(mkt_cap["gain_t"].sum()), 1),
    "cloud_rev_q4": round(float(cloud_q4["revenue_bn"].sum()), 1),
    "cloud_rev_2024": round(float(cloud_2024.groupby("ticker")["revenue_bn"].sum().sum()), 1),
    "cloud_rev_2025": round(float(cloud_2025.groupby("ticker")["revenue_bn"].sum().sum()), 1),
}

# Per-company annual
TICKERS_4 = ["AMZN", "GOOGL", "MSFT", "META"]
for t in TICKERS_4:
    for y in [2024, 2025]:
        key = f"{t.lower()}_{y}"
        val = ann6[(ann6["ticker"] == t) & (ann6["year"] == y)]["capex_bn"].sum()
        stats[key] = round(float(val), 1)

# Guidance per company
for _, row in guidance_2026[guidance_2026["ticker"].isin(TICKERS_4)].iterrows():
    stats[f"{row['ticker'].lower()}_2026g"] = round(float(row["capex_bn"]), 1)

# Historical 4co baseline
ann4 = capex_annual[capex_annual["ticker"].isin(TICKERS_4)]
stats["capex_4co_2019_bn"] = 70.9
stats["capex_4co_2025"] = round(float(ann4[ann4["year"] == 2025]["capex_bn"].sum()), 1)
stats["capex_4co_multiple"] = round(stats["capex_4co_2025"] / stats["capex_4co_2019_bn"], 1)

# 3-company cloud+capex
TICKERS_3 = ["AMZN", "GOOGL", "MSFT"]
ann3 = capex_annual[capex_annual["ticker"].isin(TICKERS_3)]
stats["capex_3co_2024"] = round(float(ann3[ann3["year"] == 2024]["capex_bn"].sum()), 1)
stats["capex_3co_2025"] = round(float(ann3[ann3["year"] == 2025]["capex_bn"].sum()), 1)

# OCF metrics
ocf6 = ocf_data[ocf_data["ticker"].isin(TICKERS_6)]
stats["ocf_ttm"] = round(float(ocf6["ocf_bn"].sum()), 1)
stats["capex_ocf_2026_pct"] = round(stats["guidance_2026"] / stats["ocf_ttm"] * 100, 1)

# Guidance band (using citation-based revision history)
try:
    meta_2023_g_high = int(citations["meta_2023_guidance_high"])
    meta_2023_actual = stats.get("meta_2023", round(float(ann4[(ann4["ticker"] == "META") & (ann4["year"] == 2023)]["capex_bn"].sum()), 1))
    meta_guidance_cut_pct = round((meta_2023_g_high - meta_2023_actual) / meta_2023_g_high * 100)
    msft_fy25_initial_g = int(citations["msft_fy25_initial_g"])
    msft_fy25_revised_g = int(citations["msft_fy25_revised_g"])
    msft_guidance_raise_pct = round((msft_fy25_revised_g - msft_fy25_initial_g) / msft_fy25_initial_g * 100)
    stats["guidance_band_pct"] = max(meta_guidance_cut_pct, msft_guidance_raise_pct)
except (KeyError, ZeroDivisionError):
    stats["guidance_band_pct"] = 30

band = stats["guidance_band_pct"] / 100
stats["guidance_2026_point"] = stats["guidance_2026"]
stats["guidance_2026_low"] = round(stats["guidance_2026"] * (1 - band))
stats["guidance_2026_high"] = round(stats["guidance_2026"] * (1 + band))

# Ratio
stats["ratio_vs_2025"] = round(stats["mkt_gain_t"] / (stats["capex_2025"] / 1000), 1)
stats["pnfi_share_pct"] = round(stats["capex_2025"] / 4200 * 100, 1)  # approximate PNFI

# AWS annual revenue (computed from quarterly data)
aws_2025 = cloud_rev[cloud_rev["quarter"].str.startswith("2025") & (cloud_rev["ticker"] == "AMZN")]
stats["aws_rev_2025"] = round(float(aws_2025["revenue_bn"].sum()), 1)

# MSFT Intelligent Cloud gap: quarterly revenue minus quarterly capex
# Maps calendar quarters to capex dates
capex_q = query("""
    SELECT ticker, date, capex_bn FROM energy_data.hyperscaler_capex
    WHERE ticker = 'MSFT' AND date IN ('2025-09-30', '2025-12-31')
    ORDER BY date
""")
msft_ic = cloud_rev[(cloud_rev["ticker"] == "MSFT")]
def _msft_gap(qtr: str, cap_date: str) -> float:
    rev = msft_ic.loc[msft_ic["quarter"] == qtr, "revenue_bn"]
    cap = capex_q.loc[capex_q["date"] == cap_date, "capex_bn"]
    if rev.empty or cap.empty:
        return 0.0
    return round(float(rev.iloc[0]) - float(cap.iloc[0]), 1)

stats["msft_ic_gap_q3_2025"] = _msft_gap("2025-Q3", "2025-09-30")
stats["msft_ic_gap_q4_2025"] = _msft_gap("2025-Q4", "2025-12-31")

# Off-balance-sheet citations
for key in [
    "msft_neocloud_total_bn", "msft_nebius_deal_bn", "msft_nscale_deal_bn",
    "msft_iren_deal_bn", "meta_beignet_financing_bn",
    "sequoia_rev_target_bn", "cloud_rev_2026_low", "cloud_rev_2026_high",
    "nvda_deepseek_loss_bn", "stargate_announced_bn", "stargate_initial_bn",
    "openai_coreweave_commitment_bn", "coreweave_interest_rate_pct",
    "chatgpt_monthly_users_m", "google_search_ad_rev_qtr_bn",
    "deepseek_v3_train_cost_m",
    "apple_capex_2024_bn",
]:
    try:
        stats[key] = int(citations[key]) if "." not in str(citations[key]) else float(citations[key])
    except (KeyError, ValueError):
        pass

print(json.dumps(stats))
