import marimo

__generated_with = "0.19.11"
app = marimo.App(width="medium", app_title="AI Capital vs. Physical Reality")


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    # AI Valuations vs. Physical Infrastructure Reality
    ## Where Does the Capital Actually Land?

    *Thandolwethu Zwelakhe Dlamini*

    ---

    The Magnificent Seven have added about \\${stats['mkt_gain_t']:.1f} trillion in
    market capitalization since January 2023. Capital expenditure across the six major
    AI infrastructure builders reached about \\${stats['capex_2025']:.0f}B in 2025, up
    from about \\${stats['capex_2024']:.0f}B in 2024, with about
    \\${stats['guidance_2026_point']:.0f}B guided for 2026 (caveat band:
    \\${stats['guidance_2026_low']:.0f}–\\${stats['guidance_2026_high']:.0f}B). The key
    question is how much of that spending is converting into physical infrastructure,
    and what the grid ultimately receives from that conversion.

    The core issue is whether financial momentum is tracking physical delivery.
    Capex-to-revenue ratios remain far above historical norms: cloud revenue is running
    at about \\${stats['cloud_rev_q4_annual']:.0f}B annualized, while these firms are
    spending the equivalent of about {stats['capex_2025']/stats['cloud_rev_q4_annual']:.1f}x
    annualized cloud revenue on supporting infrastructure. Interconnection data points
    in the same direction — LBNL's 2024 queue data shows that most queued capacity is
    withdrawn before completion. In short, capital is being committed, announced, and
    priced faster than infrastructure can be delivered.

    About {stats['decomp_const_pct']}% of capex funds construction — data centers,
    substations, and transmission interconnects. These are 20–40 year assets that can
    remain embedded in utility rate bases and land titles long after the current demand
    cycle. The other {stats['decomp_equip_pct']}% is mostly equipment that depreciates
    in 3–6 years and turns over with technology cycles. That asymmetry is central: when
    long-lived assets outlast the demand thesis that justified them, do they become
    durable grid infrastructure — or stranded capital?
    """)
    return


@app.cell
def _():
    import sys

    import marimo as mo

    sys.path.insert(0, str(mo.notebook_dir().parent.parent))

    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd

    from src.data.db import query
    from src.notebook import save_fig, setup
    from src.plotting import (
        COLORS,
        CONTEXT,
        FIGSIZE,
        FONTS,
        chart_title,
        company_color,
        company_label,
        legend_below,
    )

    cfg = setup()
    return (
        COLORS,
        CONTEXT,
        FIGSIZE,
        FONTS,
        cfg,
        chart_title,
        company_color,
        company_label,
        legend_below,
        mo,
        np,
        pd,
        plt,
        query,
        save_fig,
    )


@app.cell
def _(pd, query):
    # Live capex data from DuckDB (yfinance + historical CSV)
    capex_raw = query("""
        SELECT ticker, date, capex_bn
        FROM energy_data.hyperscaler_capex
        ORDER BY date, ticker
    """)
    capex_raw["date"] = pd.to_datetime(capex_raw["date"])
    capex_raw["year"] = capex_raw["date"].dt.year

    # Annual capex by company
    capex_annual = (
        capex_raw.groupby(["ticker", "year"])["capex_bn"]
        .sum()
        .reset_index()
        .sort_values(["ticker", "year"])
    )

    # 2026 guidance from DuckDB (loaded from data/external/ CSV)
    guidance_2026 = query("""
        SELECT ticker, year, capex_bn, source
        FROM energy_data.capex_guidance
    """)

    # Market cap reference data (3 snapshots: Jan 2023, Jan 2025, Feb 2026)
    _mkt = query("""
        SELECT ticker, company, date, market_cap_t
        FROM energy_data.mag7_market_caps
        ORDER BY ticker, date
    """)
    _early = _mkt[_mkt["date"] == "2023-01-03"].set_index("ticker")
    _late = _mkt[_mkt["date"] == "2026-02-14"].set_index("ticker")
    mkt_cap = _early[["company"]].copy()
    mkt_cap["mkt_cap_2023_t"] = _early["market_cap_t"]
    mkt_cap["mkt_cap_2026_t"] = _late["market_cap_t"]
    mkt_cap["gain_t"] = mkt_cap["mkt_cap_2026_t"] - mkt_cap["mkt_cap_2023_t"]
    mkt_cap = mkt_cap.reset_index()

    # Cloud revenue (quarterly) for revenue question analysis
    cloud_rev = query("""
        SELECT ticker, segment, quarter, revenue_bn, yoy_growth_pct
        FROM energy_data.cloud_revenue
        ORDER BY quarter, ticker
    """)

    # BEA Private Nonresidential Fixed Investment (FRED, latest quarterly SAAR)
    _pnfi = query("""
        SELECT value FROM energy_data.fred_series
        WHERE series_id = 'PNFI'
        ORDER BY date DESC LIMIT 1
    """)
    pnfi_bn = float(_pnfi["value"].iloc[0])

    # LBNL interconnection queue (all columns for data-grounding prose)
    queue_summary = query("""
        SELECT year, generation_gw, storage_gw, total_gw,
               solar_gw, wind_gw, gas_gw, nuclear_gw, other_gw,
               completion_pct, withdrawal_pct
        FROM energy_data.lbnl_queue_summary
        ORDER BY year
    """)

    # Operating cash flow (TTM, for capex/OCF ratio)
    ocf_data = query("""
        SELECT ticker, ocf_bn
        FROM energy_data.hyperscaler_ocf
    """)

    # PP&E decomposition from EDGAR 10-K parsing
    ppe_schedule = query("""
        SELECT ticker, category, gross_value_m,
               ROUND(gross_value_m * 100.0 /
                 SUM(gross_value_m) OVER (PARTITION BY ticker), 1) as pct
        FROM energy_data.edgar_ppe_schedule
    """)

    # Source citations (structured provenance for all external constants)
    _cite_raw = query("""
        SELECT key, value FROM energy_data.source_citations
    """)
    citations = dict(zip(_cite_raw["key"], _cite_raw["value"]))

    # BEA NIPA private fixed investment breakdown
    bea_nipa = query("""
        SELECT line_number, line_description, value_bn
        FROM energy_data.bea_nipa_investment
        ORDER BY line_number
    """)

    return capex_annual, capex_raw, citations, cloud_rev, guidance_2026, mkt_cap, ocf_data, bea_nipa, pnfi_bn, ppe_schedule, queue_summary


@app.cell
def _(bea_nipa, capex_annual, capex_raw, citations, cloud_rev, guidance_2026, mkt_cap, ocf_data, pnfi_bn, ppe_schedule, queue_summary):
    # Compute key summary stats — used by all markdown captions to avoid hardcoded numbers.
    # RULE: Every figure in prose must trace to either:
    #   (a) a DB-computed value (EDGAR, yfinance, LBNL, FRED)
    #   (b) a citation-backed value (source_citations.csv with full provenance)
    _tickers_6 = ["MSFT", "AMZN", "GOOGL", "META", "ORCL", "NVDA"]
    _annual = capex_annual[capex_annual["ticker"].isin(_tickers_6)]
    _cloud_q4 = cloud_rev[cloud_rev["quarter"] == "2025-Q4"]
    _cloud_2024 = cloud_rev[cloud_rev["quarter"].str.startswith("2024")]
    _cloud_2025 = cloud_rev[cloud_rev["quarter"].str.startswith("2025")]
    stats = {
        "capex_2022": _annual[_annual["year"] == 2022]["capex_bn"].sum(),
        "capex_2023": _annual[_annual["year"] == 2023]["capex_bn"].sum(),
        "capex_2024": _annual[_annual["year"] == 2024]["capex_bn"].sum(),
        "capex_2025": _annual[_annual["year"] == 2025]["capex_bn"].sum(),
        "guidance_2026": guidance_2026[
            guidance_2026["ticker"].isin(_tickers_6)
        ]["capex_bn"].sum(),
        "mkt_gain_t": mkt_cap["gain_t"].sum(),
        # BEA PNFI from FRED (quarterly SAAR, $B)
        "pnfi_bn": pnfi_bn,
        # Historical baseline — AMZN+GOOGL+MSFT+META, sourced from SEC 10-K filings
        # ($4.6B+$9.9B+$5.9B+$2.5B = AMZN, GOOGL, MSFT, META respectively)
        "capex_4co_2019_bn": 70.9,
        # Cloud revenue
        "cloud_rev_q4": _cloud_q4["revenue_bn"].sum(),
        "cloud_rev_q4_annual": _cloud_q4["revenue_bn"].sum() * 4,
        "cloud_rev_2024": _cloud_2024.groupby("ticker")["revenue_bn"].sum().sum(),
        "cloud_rev_2025": _cloud_2025.groupby("ticker")["revenue_bn"].sum().sum(),
    }
    stats["ratio_vs_2025"] = stats["mkt_gain_t"] / (stats["capex_2025"] / 1000)
    stats["pnfi_share_pct"] = stats["capex_2025"] / stats["pnfi_bn"] * 100

    # --- Per-company annual totals (for DeepSeek table and inline citations) ---
    for _t in ["AMZN", "GOOGL", "MSFT", "META"]:
        for _y in [2024, 2025]:
            stats[f"{_t.lower()}_{_y}"] = _annual[
                (_annual["ticker"] == _t) & (_annual["year"] == _y)
            ]["capex_bn"].sum()
    # Per-company guidance
    for _, _row in guidance_2026[
        guidance_2026["ticker"].isin(["AMZN", "GOOGL", "MSFT", "META"])
    ].iterrows():
        stats[f"{_row['ticker'].lower()}_2026g"] = _row["capex_bn"]
    stats["meta_2022"] = _annual[
        (_annual["ticker"] == "META") & (_annual["year"] == 2022)
    ]["capex_bn"].sum()
    stats["meta_2023"] = _annual[
        (_annual["ticker"] == "META") & (_annual["year"] == 2023)
    ]["capex_bn"].sum()

    # --- Operating cash flow (TTM) and capex/OCF ratios ---
    _tickers_ocf = ocf_data[ocf_data["ticker"].isin(_tickers_6)]
    stats["ocf_ttm"] = _tickers_ocf["ocf_bn"].sum()
    stats["capex_ocf_2026_pct"] = stats["guidance_2026"] / stats["ocf_ttm"] * 100
    # Amazon individual OCF ratio (2025 actual capex vs TTM OCF)
    _amzn_ocf = float(ocf_data[ocf_data["ticker"] == "AMZN"]["ocf_bn"].iloc[0])
    stats["amzn_ocf_pct"] = stats["amzn_2025"] / _amzn_ocf * 100

    # --- Cloud revenue YoY growth range (Q4 2025, min/max across providers) ---
    _yoy = _cloud_q4["yoy_growth_pct"].dropna()
    stats["cloud_yoy_min"] = _yoy.min()
    stats["cloud_yoy_max"] = _yoy.max()

    # --- LBNL queue stats (from energy_data.lbnl_queue_summary) ---
    _q_latest = queue_summary[queue_summary["year"] == queue_summary["year"].max()].iloc[0]
    _q_prev = queue_summary[queue_summary["year"] == queue_summary["year"].max() - 1].iloc[0]
    stats["queue_total_gw"] = int(_q_latest["total_gw"])
    stats["queue_gen_gw"] = int(_q_latest["generation_gw"])
    stats["queue_storage_gw"] = int(_q_latest["storage_gw"])
    stats["queue_solar_gw"] = int(_q_latest["solar_gw"])
    stats["queue_wind_gw"] = int(_q_latest["wind_gw"])
    stats["queue_gas_gw"] = int(_q_latest["gas_gw"])
    stats["queue_completion_pct"] = int(_q_latest["completion_pct"])
    stats["queue_withdrawal_pct"] = int(_q_latest["withdrawal_pct"])
    stats["queue_yoy_pct"] = round(
        (_q_latest["total_gw"] / _q_prev["total_gw"] - 1) * 100
    )
    # Queue composition as % of total queue (generation + storage)
    stats["queue_solar_pct"] = round(_q_latest["solar_gw"] / _q_latest["total_gw"] * 100)
    stats["queue_storage_pct"] = round(_q_latest["storage_gw"] / _q_latest["total_gw"] * 100)
    stats["queue_wind_pct"] = round(_q_latest["wind_gw"] / _q_latest["total_gw"] * 100)
    # Gas growth: year-over-year change
    stats["queue_gas_growth_pct"] = round(
        (_q_latest["gas_gw"] / _q_prev["gas_gw"] - 1) * 100
    )
    # Cohort completion rates (from source_citations → Rand et al., 2025, Table 3)
    stats["queue_cohort_2000_2005_pct"] = int(citations["queue_cohort_2000_2005_pct"])
    stats["queue_cohort_2006_2010_pct"] = int(citations["queue_cohort_2006_2010_pct"])
    stats["queue_cohort_2011_2015_pct"] = int(citations["queue_cohort_2011_2015_pct"])
    stats["queue_cohort_2016_2020_pct"] = int(citations["queue_cohort_2016_2020_pct"])

    # --- Capital decomposition (from EDGAR PP&E schedule → FY2024 10-K parsing) ---
    # "Buildings" = buildings + land + CIP (the durable construction component)
    # "Equipment" = servers/network/compute equipment (depreciates in 3-6 years)
    _durable_cats = {"buildings", "land", "construction_in_progress", "other"}
    _equip_cats = {"equipment"}
    for _t in ["META", "AMZN", "GOOGL"]:
        _co = ppe_schedule[ppe_schedule["ticker"] == _t]
        _co_total = _co["gross_value_m"].sum()
        _co_durable = _co[_co["category"].isin(_durable_cats)]["gross_value_m"].sum()
        _co_equip = _co[_co["category"].isin(_equip_cats)]["gross_value_m"].sum()
        stats[f"{_t.lower()}_buildings_pct"] = round(_co_durable / _co_total * 100)
        stats[f"{_t.lower()}_equip_pct"] = round(_co_equip / _co_total * 100)
    # Legacy aliases for prose (meta_servers_pct, googl_tech_pct)
    stats["meta_servers_pct"] = stats["meta_equip_pct"]
    stats["googl_tech_pct"] = stats["googl_equip_pct"]
    stats["amzn_equipment_pct"] = stats["amzn_equip_pct"]
    # googl_buildings_pct and amzn_buildings_pct already set by the loop above
    # Cross-company midpoints and ranges
    _bld_pcts = [stats["meta_buildings_pct"], stats["amzn_buildings_pct"], stats["googl_buildings_pct"]]
    _eqp_pcts = [stats["meta_servers_pct"], stats["amzn_equipment_pct"], stats["googl_tech_pct"]]
    stats["decomp_equip_pct"] = round(sum(_eqp_pcts) / len(_eqp_pcts))
    stats["decomp_equip_low"] = min(_eqp_pcts)
    stats["decomp_equip_high"] = max(_eqp_pcts)
    stats["decomp_const_pct"] = round(sum(_bld_pcts) / len(_bld_pcts))
    stats["decomp_const_low"] = min(_bld_pcts)
    stats["decomp_const_high"] = max(_bld_pcts)
    stats["decomp_other_pct"] = 100 - stats["decomp_equip_pct"] - stats["decomp_const_pct"]
    stats["decomp_equip_bn"] = round(stats["capex_2025"] * stats["decomp_equip_pct"] / 100)
    stats["decomp_const_bn"] = round(stats["capex_2025"] * stats["decomp_const_pct"] / 100)

    # --- BEA PNFI category shares (from bea_nipa_investment → BEA NIPA Table 5.3.5) ---
    _bea_total = float(bea_nipa[bea_nipa["line_number"] == 1]["value_bn"].iloc[0])
    _bea_struct = float(bea_nipa[bea_nipa["line_number"] == 2]["value_bn"].iloc[0])
    _bea_equip = float(bea_nipa[bea_nipa["line_number"] == 3]["value_bn"].iloc[0])
    _bea_ip = float(bea_nipa[bea_nipa["line_number"] == 4]["value_bn"].iloc[0])
    stats["bea_structures_pct"] = round(_bea_struct / _bea_total * 100)
    stats["bea_equipment_pct"] = round(_bea_equip / _bea_total * 100)
    stats["bea_ip_pct"] = round(_bea_ip / _bea_total * 100)

    # --- Cumulative AI-era capital stock (2022–2025) ---
    # Applies FY2024 10-K PP&E construction share as a proxy for the marginal flow.
    # This understates the true construction share if recent capex skews more toward
    # buildings (data center builds) than the cumulative PP&E stock implies.
    _ai_era = _annual[_annual["year"].isin([2022, 2023, 2024, 2025])]
    stats["ai_era_total_bn"] = round(_ai_era["capex_bn"].sum())
    stats["ai_era_const_bn"] = round(stats["ai_era_total_bn"] * stats["decomp_const_pct"] / 100)

    # --- Citation-backed constants (from source_citations.csv → DuckDB) ---
    # Each value traces to a specific source document with full provenance.
    # See data/external/source_citations.csv for source_name, date, detail, URL.

    # Meta 2026 guidance range (Meta FY25 Q4 earnings call)
    stats["meta_2026g_low"] = int(citations["meta_2026g_low"])
    stats["meta_2026g_high"] = int(citations["meta_2026g_high"])

    # Guidance revision history (for reliability caveat)
    stats["meta_2023_guidance_low"] = int(citations["meta_2023_guidance_low"])
    stats["meta_2023_guidance_high"] = int(citations["meta_2023_guidance_high"])
    stats["meta_guidance_cut_pct"] = round(
        (stats["meta_2023_guidance_high"] - stats["meta_2023"])
        / stats["meta_2023_guidance_high"] * 100
    )
    stats["msft_fy25_initial_g"] = int(citations["msft_fy25_initial_g"])
    stats["msft_fy25_revised_g"] = int(citations["msft_fy25_revised_g"])
    stats["msft_guidance_raise_pct"] = round(
        (stats["msft_fy25_revised_g"] - stats["msft_fy25_initial_g"])
        / stats["msft_fy25_initial_g"] * 100
    )
    # Guidance reliability band — derived from two observed guidance-vs-actual pairs:
    # (1) Meta FY2023: guided $34-39B (Q3 2022 earnings call, Oct 2022)
    #     actual $27.5B → ~29% below guidance high (source_citations: meta_2023_guidance_high)
    # (2) MSFT FY2025: guided ~$60B (FY2024 Q4 earnings, Jul 2024)
    #     revised to ~$80B within one quarter (Q1 FY2025, Oct 2024) → +33%
    # Band = max(|revision|) across N=2 observed pairs = 33%
    # N=2: treat as a directional bound, not a statistical confidence interval.
    stats["guidance_max_revision_pct"] = max(
        stats["meta_guidance_cut_pct"], stats["msft_guidance_raise_pct"]
    )
    stats["guidance_2026_point"] = stats["guidance_2026"]
    _guidance_band = stats["guidance_max_revision_pct"] / 100
    stats["guidance_2026_low"] = round(stats["guidance_2026_point"] * (1 - _guidance_band))
    stats["guidance_2026_high"] = round(stats["guidance_2026_point"] * (1 + _guidance_band))
    stats["guidance_band_pct"] = stats["guidance_max_revision_pct"]

    # Meta headcount reduction (Meta 10-K FY2022 → FY2023)
    stats["meta_headcount_2022"] = int(citations["meta_headcount_2022"])
    stats["meta_headcount_2023"] = int(citations["meta_headcount_2023"])
    stats["meta_headcount_cut_pct"] = round(
        (stats["meta_headcount_2022"] - stats["meta_headcount_2023"])
        / stats["meta_headcount_2022"] * 100
    )

    # 3-company capex (AMZN, GOOGL, MSFT) — apples-to-apples vs cloud revenue
    _tickers_3 = ["AMZN", "GOOGL", "MSFT"]
    _annual_3 = capex_annual[capex_annual["ticker"].isin(_tickers_3)]
    stats["capex_3co_2024"] = _annual_3[_annual_3["year"] == 2024]["capex_bn"].sum()
    stats["capex_3co_2025"] = _annual_3[_annual_3["year"] == 2025]["capex_bn"].sum()
    # 3-co 2026 guidance (AMZN + GOOGL + MSFT only — set after per-company loop)
    stats["capex_3co_2026g"] = (
        stats["amzn_2026g"] + stats["googl_2026g"] + stats["msft_2026g"]
    )

    # External cited constants
    stats["sequoia_rev_target_bn"] = int(citations["sequoia_rev_target_bn"])
    stats["gcp_backlog_bn"] = int(citations["gcp_backlog_bn"])
    stats["gcp_backlog_growth_pct"] = int(citations["gcp_backlog_growth_pct"])
    stats["vc_ai_2024_bn"] = float(citations["vc_ai_2024_bn"])
    stats["ai_capex_share_pct"] = int(citations["ai_capex_share_pct"])
    stats["hist_capex_ocf_avg_pct"] = int(citations["hist_capex_ocf_avg_pct"])
    stats["analyst_const_pct_low"] = int(citations["analyst_const_pct_low"])
    stats["dc_construction_low_bn"] = int(citations["dc_construction_low_bn"])
    stats["dc_construction_high_bn"] = int(citations["dc_construction_high_bn"])
    stats["cloud_rev_2026_low"] = int(citations["cloud_rev_2026_low"])
    stats["cloud_rev_2026_high"] = int(citations["cloud_rev_2026_high"])
    stats["capex_rev_2026_low"] = round(
        stats["guidance_2026"] / stats["cloud_rev_2026_high"], 1
    )
    stats["capex_rev_2026_high"] = round(
        stats["guidance_2026"] / stats["cloud_rev_2026_low"], 1
    )
    stats["nvda_deepseek_loss_bn"] = int(citations["nvda_deepseek_loss_bn"])
    stats["stargate_announced_bn"] = int(citations["stargate_announced_bn"])
    stats["stargate_initial_bn"] = int(citations["stargate_initial_bn"])
    return (stats,)


@app.cell
def _(
    COLORS,
    FIGSIZE,
    FONTS,
    cfg,
    chart_title,
    company_color,
    company_label,
    legend_below,
    mkt_cap,
    plt,
    save_fig,
    stats,
):
    # Single stacked horizontal bar — the TOTAL length vs. the capex reference
    # line tells the scale-mismatch story far better than individual bars.
    _sorted = mkt_cap.sort_values("gain_t", ascending=False)
    _total = _sorted["gain_t"].sum()
    _capex_t = stats["capex_2025"] / 1000  # $B → $T

    fig_mktcap, _ax = plt.subplots(figsize=FIGSIZE["wide"])

    _left = 0.0
    for _, _row in _sorted.iterrows():
        _ticker = _row["ticker"]
        _gain = _row["gain_t"]
        _clr = company_color(_ticker)
        _ax.barh(
            0, _gain, left=_left, height=0.55,
            color=_clr, edgecolor="white", linewidth=1.5,
            label=company_label(_ticker),
        )
        # Direct label on segments wide enough to hold text
        if _gain >= 0.8:
            _ax.text(
                _left + _gain / 2, 0,
                f"{company_label(_ticker)}\n+${_gain:.1f}T",
                ha="center", va="center",
                fontsize=FONTS["annotation"] - 1, fontweight="bold",
                color="white",
            )
        _left += _gain

    # Reference line: the punchline — capex is a sliver of the total
    _ax.axvline(
        _capex_t, color=COLORS["accent"], linestyle="-", linewidth=2.5, alpha=0.9,
    )
    _ax.text(
        _capex_t, 0.38,
        f"  2025 capex: ${stats['capex_2025']:.0f}B",
        fontsize=FONTS["annotation"], fontweight="bold",
        color=COLORS["accent"], va="bottom",
    )

    # Total at right end
    _ax.text(
        _total + 0.12, 0,
        f"${_total:.1f}T",
        ha="left", va="center",
        fontsize=FONTS["value_label"], fontweight="bold",
        color=COLORS["text_dark"],
    )

    _ax.set_yticks([])
    _ax.set_xlabel(
        "Market cap gain, Jan 2023 \u2192 Feb 2026 ($T)", fontsize=FONTS["axis_label"]
    )
    _ax.tick_params(axis="x", labelsize=FONTS["tick_label"])

    legend_below(_ax, ncol=len(_sorted))
    chart_title(
        fig_mktcap,
        f"~{stats['ratio_vs_2025']:.0f}x gap between market cap gains and annual capex",
    )
    plt.tight_layout()
    save_fig(fig_mktcap, cfg.img_dir / "dd001_valuation_disconnect.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo, stats):
    _chart = mo.image(
        src=(cfg.img_dir / "dd001_valuation_disconnect.png").read_bytes(), width=850
    )
    mo.md(
        "# Markets added ~\\${mkt:.1f}T in value against ~\\${capex:.0f}B in annual spending"
        .format(mkt=stats['mkt_gain_t'], capex=stats['capex_2025'])
        + f"""

    {_chart}

    *The Magnificent Seven added about \\${stats['mkt_gain_t']:.1f}T in market
    capitalization from January 2023 to February 2026. Combined 2025 capex for the
    six AI infrastructure builders was about \\${stats['capex_2025']:.0f}B, implying a
    ~{stats['ratio_vs_2025']:.0f}x gap between valuation gains and annual infrastructure
    spend. The red line marks 2025 capex for scale. Tesla is included in market-cap
    gains but excluded from AI capex totals because most of its capex remains
    automotive. Sources: Yahoo Finance (market cap, Feb 14 2026), SEC filings via
    yfinance (capex).*

    Market capitalization reflects expected future earnings, while capex is a current
    spending flow. This is a scale comparison, not a one-to-one valuation test. The
    gap is real. Whether it signals mispricing or early-stage buildout depends on
    which earnings scenario is correct.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    > **The Tesla/xAI question.** Tesla's \\$1.18T market cap gain (Jan 2023–Feb 2026)
    > is overwhelmingly priced on AI, not cars: forward P/E is ~160x vs. the auto sector
    > median of 6.2x. Tesla spent ~\\$5B on AI infrastructure in 2024 (44% of total capex)
    > and guides \\$20B+ for 2026. Separately, Musk's xAI built the 200,000-GPU "Colossus"
    > supercomputer for ~\\$7B — AI infrastructure capital flowing through a web of related
    > entities with overlapping leadership and ambiguous corporate boundaries.
    >
    > Tesla's capex is excluded from the totals above because its core spend remains
    > automotive, but the AI narrative drives its valuation — making it arguably the most
    > extreme example of the disconnect this analysis tracks.
    >
    > *Sources: Tesla 10-K (2024), CNBC, CompaniesMarketCap.*
    """)
    return


@app.cell
def _(COLORS, CONTEXT, FIGSIZE, FONTS, capex_annual, cfg, chart_title, plt, save_fig):
    # Absolute capex ($B), 4 hyperscalers (AMZN, GOOGL, MSFT, META), 2015–2025.
    # Temporal gray+accent split: cloud-buildout era in CONTEXT gray,
    # AI buildout era (2022+) in accent. Shows the acceleration in dollar terms
    # without market-cap denominator noise.
    #
    # Capex (2015–2021): SEC 10-K annual reports (PP&E additions / purchases)
    #   MSFT fiscal year (ends June) mapped to calendar year of FY end
    # Capex (2022–2025): yfinance cash flow statements via DuckDB (hyperscaler_capex table)
    _hist_capex_4co = {
        2015: 22.9,   # AMZN $4.6B + GOOGL $9.9B + MSFT $5.9B + META $2.5B
        2016: 30.8,   # AMZN $7.8B + GOOGL $10.2B + MSFT $8.3B + META $4.5B
        2017: 40.0,   # AMZN $12.0B + GOOGL $13.2B + MSFT $8.1B + META $6.7B
        2018: 64.0,   # AMZN $13.4B + GOOGL $25.1B + MSFT $11.6B + META $13.9B
        2019: 70.9,   # AMZN $16.9B + GOOGL $23.5B + MSFT $15.4B + META $15.1B
        2020: 93.5,   # AMZN $40.1B + GOOGL $22.3B + MSFT $15.4B + META $15.7B
        2021: 125.5,  # AMZN $61.1B + GOOGL $24.6B + MSFT $20.6B + META $19.2B
    }
    _tickers_4 = ["AMZN", "GOOGL", "MSFT", "META"]
    _ann4 = capex_annual[capex_annual["ticker"].isin(_tickers_4)]
    for _y in [2022, 2023, 2024, 2025]:
        _hist_capex_4co[_y] = float(_ann4[_ann4["year"] == _y]["capex_bn"].sum())

    _years = sorted(_hist_capex_4co.keys())
    _values = [_hist_capex_4co[y] for y in _years]

    # Split at 2022: cloud era ends at 2021, AI buildout starts at 2022
    # Overlap at one point (2021/2022) to keep the line visually connected
    _split = _years.index(2022)

    fig_capex_ratio, _ax = plt.subplots(figsize=FIGSIZE["wide"])

    # Cloud-buildout era: CONTEXT gray (pre-AI history = context)
    _ax.plot(
        _years[:_split + 1], _values[:_split + 1],
        color=CONTEXT, linewidth=2.0, marker="o", markersize=4, zorder=3,
    )
    # AI buildout era: accent (the story)
    _ax.plot(
        _years[_split:], _values[_split:],
        color=COLORS["accent"], linewidth=2.5, marker="o", markersize=5, zorder=4,
    )

    # 2019 pre-AI baseline reference line
    _v19 = _hist_capex_4co[2019]
    _ax.axhline(_v19, color=CONTEXT, linewidth=1, linestyle="--", alpha=0.45)
    _ax.text(
        2015.2, _v19 + 5,
        f"2019 baseline: ${_v19:.0f}B",
        fontsize=FONTS["annotation"] - 1, color=CONTEXT,
    )

    # Direct label at 2025: value + growth multiple vs 2019 (no arrow — direct label)
    _v25 = _hist_capex_4co[2025]
    _mult = _v25 / _v19
    _ax.text(
        2025.15, _v25,
        f"  ${_v25:.0f}B\n  ({_mult:.1f}× vs 2019)",
        fontsize=FONTS["annotation"], color=COLORS["accent"], fontweight="bold",
        va="center",
    )

    # "AI buildout" era label — anchor it to the 2022 transition point with a
    # vertical dashed line so the reader sees exactly where the era begins
    _v22 = _hist_capex_4co[2022]
    _ax.axvline(2022, color=COLORS["accent"], linewidth=1, linestyle=":", alpha=0.5, zorder=2)
    _ax.text(
        2022.1, _v22 * 1.55,
        "AI buildout era",
        fontsize=FONTS["annotation"] - 1, color=COLORS["accent"], alpha=0.85,
        ha="left",
    )

    _ax.set_xlabel("Year", fontsize=FONTS["axis_label"])
    _ax.set_ylabel("Annual capex, 4 hyperscalers ($B)", fontsize=FONTS["axis_label"])
    _ax.tick_params(labelsize=FONTS["tick_label"])
    _ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:.0f}B"))
    _ax.set_xlim(2014.5, 2026.5)

    _title = f"Hyperscaler capex grew {_mult:.1f}× from 2019 to 2025 — the AI buildout has no cloud-era precedent"
    chart_title(fig_capex_ratio, _title)
    plt.tight_layout()
    save_fig(fig_capex_ratio, cfg.img_dir / "dd001_capex_ratio_history.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo, stats):
    _chart_ratio = mo.image(
        src=(cfg.img_dir / "dd001_capex_ratio_history.png").read_bytes(), width=850
    )
    _capex_4co_2025 = (
        stats["amzn_2025"] + stats["googl_2025"] + stats["msft_2025"] + stats["meta_2025"]
    )
    _mult_4co = _capex_4co_2025 / stats["capex_4co_2019_bn"]  # 2019 baseline from stats
    mo.md(
        f"# Hyperscaler capex grew {_mult_4co:.1f}× from 2019 to 2025 — the AI buildout has no cloud-era precedent\n\n"
        f"{_chart_ratio}\n\n"
        f"*Annual capex for Amazon, Alphabet, Microsoft, and Meta, 2015–2025. "
        f"Gray marks the cloud-buildout period (2015–2021); color marks the AI-buildout "
        f"period (2022–2025). Combined 2025 capex reached ~\\${_capex_4co_2025:.0f}B. "
        f"Pre-2022 values come from SEC 10-K filings; 2022–2025 values come from "
        f"yfinance cash-flow data in DuckDB. Microsoft fiscal-year data is mapped to "
        f"the calendar year of fiscal-year end.*"
    )
    return


@app.cell
def _(
    COLORS,
    CONTEXT,
    FIGSIZE,
    FONTS,
    capex_annual,
    cfg,
    chart_title,
    company_label,
    guidance_2026,
    legend_below,
    np,
    pd,
    plt,
    save_fig,
):
    # Combine actuals (2022-2025) with 2026 guidance
    _tickers = ["MSFT", "AMZN", "GOOGL", "META", "ORCL", "NVDA"]

    _years = [2022, 2023, 2024, 2025]
    _data = capex_annual[
        (capex_annual["ticker"].isin(_tickers)) & (capex_annual["year"].isin(_years))
    ].copy()

    # Add 2026 guidance
    _guide = guidance_2026[guidance_2026["ticker"].isin(_tickers)].copy()
    _combined = pd.concat(
        [_data[["ticker", "year", "capex_bn"]], _guide[["ticker", "year", "capex_bn"]]],
        ignore_index=True,
    )

    # SWD: companies on x-axis, years stacked — shows WHO is driving the acceleration.
    # Graduated grays for actuals, accent for 2026 guidance.
    fig_capex, _ax = plt.subplots(figsize=FIGSIZE["wide"])
    _all_years = sorted(_combined["year"].unique())
    _x = np.arange(len(_tickers))

    # Year colors: graduated grays for actuals, accent for guidance
    # Uses design system constants — lightest (oldest) to darkest (most recent)
    _year_colors = {
        2022: COLORS["grid"],       # lightest gray
        2023: CONTEXT,              # SWD context gray
        2024: COLORS["reference"],  # mid gray
        2025: COLORS["text_light"], # dark gray
        2026: COLORS["accent"],     # highlight: guidance year
    }

    # Build stacked data: each year is a layer (bottom=oldest)
    _bottoms = np.zeros(len(_tickers))
    for _yr in _all_years:
        _vals = []
        for _ticker in _tickers:
            _match = _combined[
                (_combined["ticker"] == _ticker) & (_combined["year"] == _yr)
            ]
            _vals.append(_match["capex_bn"].sum() if len(_match) else 0)
        _vals = np.array(_vals)
        _bars = _ax.bar(
            _x, _vals, bottom=_bottoms, width=0.55,
            color=_year_colors[_yr], edgecolor="white", linewidth=0.5,
            label=str(_yr) + ("*" if _yr == 2026 else ""),
        )
        # Hatch the 2026 guidance bars
        if _yr == 2026:
            for _b in _bars:
                _b.set_hatch("//")
                _b.set_alpha(0.85)
        _bottoms += _vals

    _ax.set_xticks(_x)
    _ax.set_xticklabels(
        [company_label(t) for t in _tickers], fontsize=FONTS["tick_label"],
    )
    _ax.set_ylabel("Cumulative capex, 2022–2026 ($B)", fontsize=FONTS["axis_label"])
    _ax.tick_params(axis="y", labelsize=FONTS["tick_label"])

    # Total per company above each bar — the hero element
    for _j, _ticker in enumerate(_tickers):
        _ax.text(
            _j, _bottoms[_j] + 8, f"${_bottoms[_j]:.0f}B",
            ha="center", fontsize=FONTS["annotation"], fontweight="bold",
            color=COLORS["accent"],
        )

    legend_below(_ax, ncol=len(_all_years))
    chart_title(fig_capex, "Hyperscaler capex tripled in three years — and 2026 guidance doubles again")
    plt.tight_layout()
    save_fig(fig_capex, cfg.img_dir / "dd001_capex_acceleration.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo, stats):
    _chart = mo.image(
        src=(cfg.img_dir / "dd001_capex_acceleration.png").read_bytes(), width=850
    )
    mo.md(f"""
    # Hyperscaler capex tripled in three years — and 2026 guidance doubles again

    {_chart}

    *Combined capex for six companies: ~\\${stats['capex_2023']:.0f}B (2023),
    ~\\${stats['capex_2024']:.0f}B (2024), ~\\${stats['capex_2025']:.0f}B (2025), and
    ~\\${stats['guidance_2026_point']:.0f}B guided for 2026 (hatched bars). The 2026 figure
    is management guidance, not audited actuals. Using observed guidance revisions
    (±{stats['guidance_band_pct']}%), a plausible range is
    \\${stats['guidance_2026_low']:.0f}–\\${stats['guidance_2026_high']:.0f}B. Figures
    include total capex, not only AI-specific spend; CreditSights estimates about
    {stats['ai_capex_share_pct']}% of 2026 capex is AI-attributed. Leased capacity is
    excluded, so total infrastructure deployment is higher than shown. Sources: SEC
    10-K/10-Q filings via yfinance; guidance from Q4 2025 earnings calls.*
    """)
    return


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    ---

    ## The Revenue Question

    For an apples-to-apples view, this section compares Amazon, Alphabet, and
    Microsoft on both sides of the ledger. They are the three firms that disclose
    cloud revenue segments in comparable form. Meta is excluded because it reports
    no equivalent cloud revenue line.

    In 2025, these three companies spent about \\${stats['capex_3co_2025']:.0f}B on
    capex while reporting about \\${stats['cloud_rev_2025']:.0f}B in cloud revenue.
    In Q4 2025, quarterly capex exceeded quarterly cloud revenue for the first time.
    Sequoia Capital's David Cahn independently flagged this dynamic — his estimates
    of the revenue needed to justify the buildout escalated from \\$200B (June 2024)
    to \\$600B (September 2024) to ~\\$1T (early 2025). The directional point is now
    visible in the companies' own reported financials.

    The gap is narrowing — but capex is accelerating faster:

    | Metric | 2024 | 2025 | 2026 (guided) |
    | :--- | :--- | :--- | :--- |
    | Capex (AMZN + GOOGL + MSFT) | ~\\${stats['capex_3co_2024']:.0f}B | ~\\${stats['capex_3co_2025']:.0f}B | ~\\${stats['capex_3co_2026g']:.0f}B\\* |
    | Cloud revenue (same 3) | ~\\${stats['cloud_rev_2024']:.0f}B | ~\\${stats['cloud_rev_2025']:.0f}B | est. ~\\${stats['cloud_rev_2026_low']}–{stats['cloud_rev_2026_high']}B\\*\\* |
    | Capex / Revenue ratio | ~{stats['capex_3co_2024'] / stats['cloud_rev_2024']:.1f}x | ~{stats['capex_3co_2025'] / stats['cloud_rev_2025']:.1f}x | ~{stats['capex_3co_2026g'] / stats['cloud_rev_2026_high']:.1f}–{stats['capex_3co_2026g'] / stats['cloud_rev_2026_low']:.1f}x |

    \\*2026 capex guidance: Amazon \\${stats['amzn_2026g']:.0f}B + Alphabet \\${stats['googl_2026g']:.0f}B
    + Microsoft \\${stats['msft_2026g']:.0f}B, from Q4 2025 earnings calls. Capex is
    company-total; cloud-specific capex is not separately disclosed.

    \\*\\*2026 cloud revenue estimate from Q4 2025 run-rate extrapolation plus consensus
    analyst estimates (Morgan Stanley, Goldman Sachs, Jan–Feb 2026).

    **The ratio has worsened through 2025.** In normal infrastructure businesses,
    capex-to-revenue ratios of 1-2x are sustainable. At the current trajectory, these
    companies are spending more on infrastructure than their cloud businesses generate
    in revenue. Whether AI-driven demand creates a step-function in revenue growth —
    the thesis these spending programs depend on — remains the open question.

    Cloud revenue is growing {stats['cloud_yoy_min']:.0f}–{stats['cloud_yoy_max']:.0f}% YoY
    (Q4 2025), and Google Cloud's contracted backlog surged {stats['gcp_backlog_growth_pct']}%
    to \\${stats['gcp_backlog_bn']}B (Alphabet Q4 2025 earnings call) — signals that
    demand is real. But the composition of that demand matters. A meaningful portion
    reflects these companies selling AI services to VC-funded startups, which reached
    \\${stats['vc_ai_2024_bn']}B globally in 2024 — over a third of all VC dollars
    (PitchBook, 2025). Those startups are major cloud customers. If VC funding
    contracts, a portion of cloud revenue contracts with it. Whether that circularity
    is large enough to affect the trajectory is unknown; it is a variable worth
    tracking.

    This gap matters because it is a durability question. If revenue catches up, the
    buildout is validated by demand. If it does not, the physical assets remain — and
    the question becomes who bears that long-run exposure and under what conditions.
    That is what the later notebooks trace.

    *This analysis extends the revenue-gap framing developed by Sequoia Capital
    ("AI's $600B Question," September 2024) and examined by Goldman Sachs
    ("Gen AI: Too Much Spend, Too Little Return?", September 2024). It differs
    in using auditable EDGAR data for capex actuals and company-reported cloud
    segments for revenue, rather than extrapolations from NVIDIA data center revenue.*
    """)
    return


@app.cell
def _(
    COLORS,
    CONTEXT,
    FIGSIZE,
    FONTS,
    capex_raw,
    cfg,
    chart_title,
    cloud_rev,
    legend_below,
    np,
    pd,
    plt,
    save_fig,
    stats,
):
    # Revenue gap chart: same 3 companies on both sides (apples-to-apples)
    # Gray bars = cloud revenue, accent line = capex — crossover is the story.

    # Same 3 companies on both sides (apples-to-apples)
    _tickers_3 = ["AMZN", "GOOGL", "MSFT"]

    # Quarterly cloud revenue (3 providers — explicitly filtered to match capex scope)
    _cloud_qtr = (
        cloud_rev[cloud_rev["ticker"].isin(_tickers_3)]
        .groupby("quarter")["revenue_bn"]
        .sum()
        .reset_index()
        .sort_values("quarter")
    )

    # Quarterly capex for the SAME 3 companies
    _capex_3 = capex_raw[capex_raw["ticker"].isin(_tickers_3)].copy()
    _capex_3["quarter"] = (
        _capex_3["date"].dt.year.astype(str)
        + "-Q"
        + _capex_3["date"].dt.quarter.astype(str)
    )
    _capex_qtr = (
        _capex_3.groupby("quarter")["capex_bn"]
        .sum()
        .reset_index()
        .sort_values("quarter")
    )

    # Align to common quarters
    _common = sorted(set(_cloud_qtr["quarter"]) & set(_capex_qtr["quarter"]))
    _rev = _cloud_qtr[_cloud_qtr["quarter"].isin(_common)].sort_values("quarter")
    _cap = _capex_qtr[_capex_qtr["quarter"].isin(_common)].sort_values("quarter")
    _rev_vals = _rev["revenue_bn"].values
    _cap_vals = _cap["capex_bn"].values

    fig_rev, _ax = plt.subplots(figsize=FIGSIZE["wide"])
    _x = np.arange(len(_common))

    # Gray bars: cloud revenue (the context)
    _ax.bar(
        _x, _rev_vals, width=0.6, color=CONTEXT, alpha=0.7,
        label="Cloud revenue (AWS + MSFT Cloud + GCP)",
    )

    # Accent line: capex (the story)
    _ax.plot(
        _x, _cap_vals, color=COLORS["accent"], linewidth=2.5,
        marker="o", markersize=5, label="Capital expenditure (same 3 co.)",
    )

    # Annotate crossover
    _gaps = _rev_vals - _cap_vals
    for _i in range(1, len(_gaps)):
        if _gaps[_i - 1] > 0 and _gaps[_i] <= 0:
            _ax.annotate(
                f"Capex overtakes revenue\n\\${_cap_vals[_i]:.0f}B vs \\${_rev_vals[_i]:.0f}B",
                xy=(_i, _cap_vals[_i]),
                xytext=(_i - 3, _cap_vals[_i] + 15),
                fontsize=FONTS["annotation"], color=COLORS["accent"],
                fontweight="bold",
                arrowprops=dict(
                    arrowstyle="->", color=COLORS["accent"],
                    connectionstyle="arc3,rad=-0.2", linewidth=1.5,
                ),
            )
            break

    # Direct-label last data points
    _last = len(_common) - 1
    _ax.text(
        _last, _rev_vals[_last] - 4, f"${_rev_vals[_last]:.0f}B",
        ha="center", va="top", fontsize=FONTS["annotation"],
        color=COLORS["text_light"],
    )
    _ax.text(
        _last + 0.15, _cap_vals[_last] + 1.5, f"${_cap_vals[_last]:.0f}B",
        ha="left", va="bottom", fontsize=FONTS["annotation"],
        color=COLORS["accent"], fontweight="bold",
    )

    # Investment intensity callout: ratio at start and end (no secondary axis)
    _ratio = _cap_vals / _rev_vals
    _ax.text(
        0, _rev_vals[0] * 0.3,
        f"Investment intensity:\n{_ratio[0]:.1f}× (capex/cloud rev)",
        ha="left", va="bottom", fontsize=FONTS["annotation"] - 1,
        color=COLORS["text_light"],
    )
    _ax.text(
        _last, _cap_vals[_last] * 1.08,
        f"{_ratio[-1]:.1f}×",
        ha="center", va="bottom", fontsize=FONTS["annotation"],
        color=COLORS["accent"], fontweight="bold",
    )

    _ax.set_xticks(_x)
    _ax.set_xticklabels(_common, fontsize=FONTS["tick_label"], rotation=45, ha="right")
    _ax.set_ylabel("Quarterly ($B)", fontsize=FONTS["axis_label"])
    _ax.tick_params(axis="y", labelsize=FONTS["tick_label"])
    _ax.set_ylim(0, max(max(_rev_vals), max(_cap_vals)) * 1.25)

    legend_below(_ax, ncol=2)
    chart_title(fig_rev, f"Total capex overtook cloud revenue in late 2025 — ~{stats['ai_capex_share_pct']}% AI-attributed (CreditSights)")
    plt.tight_layout()
    save_fig(fig_rev, cfg.img_dir / "dd001_revenue_gap.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo, stats):
    _chart = mo.image(
        src=(cfg.img_dir / "dd001_revenue_gap.png").read_bytes(), width=850
    )
    mo.md(f"""
    # Total capex overtook cloud revenue in late 2025

    {_chart}

    *Both series cover the same three companies: Amazon, Alphabet, and Microsoft. Gray
    bars show quarterly cloud revenue — AWS, Microsoft Intelligent Cloud, and Google
    Cloud, as reported in SEC 10-Q filings. The red line shows quarterly total capex
    for the same firms. In Q4 2025, capex exceeded quarterly cloud revenue for the
    first time. Full-year 2025: ~\\${stats['capex_3co_2025']:.0f}B capex versus
    ~\\${stats['cloud_rev_2025']:.0f}B cloud revenue. Capex is company-total because
    cloud-segment capex is not separately disclosed in SEC filings.
    Sources: SEC 10-Q filings (Q1 2023 – Q4 2025).*
    """)
    return




@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    ---

    ## Announcements vs. Physical Reality

    The central gap is conversion, not commitment. Announcements are large, but
    delivery is constrained by interconnection timelines, permitting, and equipment
    bottlenecks:

    - **Stargate Project:** \\${stats['stargate_announced_bn']}B announced intent (White House
      press conference, Jan 21, 2025 — no binding construction commitment at announcement).
      \\${stats['stargate_initial_bn']}B Phase 1 committed and under active deployment.
      SoftBank's balance sheet had ~\\$30-40B deployable capital at announcement time;
      financial structure and timeline for the remaining \\${stats['stargate_announced_bn'] - stats['stargate_initial_bn']}B remain opaque.
      *(Sources: White House announcement, Jan 2025; FT analysis)*
    - **U.S. Interconnection Queue:** Over {stats['queue_total_gw']:,} GW of generation and storage capacity
      seeking grid connection as of end-2024 — roughly
      3x total U.S. installed capacity (Rand et al., LBNL *Queued Up* 2025 Edition).
      Of all capacity queued from 2000-2024, **{stats['queue_withdrawal_pct']}% was withdrawn** and only **{stats['queue_completion_pct']}%
      reached commercial operation.**
    - **Large Load (Data Center) Requests:** For the first time, LBNL tracked load-side
      interconnection: over **100 GW** of large load requests (predominantly data
      centers), with PJM alone accounting for ~80 GW — up from ~5 GW just two years
      earlier *(Rand et al., 2025)*. PJM's Board initiated a "Critical Issue Fast Path"
      process in February 2025 to handle the unprecedented volume.
    - **ERCOT:** ~15-20 GW of large load study requests through 2024, mostly data
      centers. ERCOT uses a different process than ISO/RTO queues, so direct
      comparison is imperfect. *(Source: ERCOT CDR reports, 2024)*

    The binding constraint is **power availability**. The typical time from
    interconnection request to commercial operation has grown to ~5 years nationally,
    up from ~3 years a decade ago *(Rand et al., 2025)*. This is a physical bottleneck
    that no amount of capital can instantly resolve — it requires substations,
    transmission lines, and generation capacity that take years to permit and build.

    **Context on completion rates:** The {stats['queue_completion_pct']}% headline figure is partly a censoring
    artifact — recent cohorts haven't had time to complete. But even fully matured
    cohorts show low rates: {stats['queue_cohort_2000_2005_pct']}% for 2000-2005 entries, declining to {stats['queue_cohort_2006_2010_pct']}% (2006-2010)
    and {stats['queue_cohort_2011_2015_pct']}% (2011-2015) *(Rand et al., 2025, Table 3)*. The queue has *never* been an
    efficient pipeline. Low completion is partly structural in first-come, first-served
    systems with low entry costs — developers rationally submit speculative requests
    to preserve optionality (Palmer et al., RFF, 2024). FERC Order 2023 shifts to
    first-ready, first-served processing to address this.

    The queue composition is shifting: natural gas requests grew ~{stats['queue_gas_growth_pct']}% in a single
    year to ~{stats['queue_gas_gw']} GW (end-2024), likely reflecting data center demand for firm,
    dispatchable power. Solar remains dominant at ~{stats['queue_solar_gw']:,} GW ({stats['queue_solar_pct']}% of total queue),
    storage ~{stats['queue_storage_gw']:,} GW ({stats['queue_storage_pct']}%), wind ~{stats['queue_wind_gw']} GW ({stats['queue_wind_pct']}%).

    As of early 2025: no major AI infrastructure project cancellations reported. The
    pattern is delays and site relocation, not outright cancellation. The capital is
    real, but the evidence so far suggests the conversion from announcement to operating
    infrastructure is slower and more contingent than headlines imply. How much slower
    is a question the data can start to answer — but not yet close.
    """)
    return


@app.cell
def _(COLORS, CONTEXT, FONTS, cfg, chart_title, legend_below, np, plt, queue_summary, save_fig, stats):
    # LBNL "Queued Up" 2025 Edition — queue growth and attrition
    # Data loaded from DuckDB (source: data/external/lbnl_queue_summary.csv)
    _years = queue_summary["year"].tolist()
    _gen_gw = queue_summary["generation_gw"].tolist()
    _storage_gw = queue_summary["storage_gw"].tolist()

    _fig_queue, _ax = plt.subplots(figsize=FIGSIZE["single"])

    _x = np.arange(len(_years))
    _w = 0.55

    _ax.bar(_x, _gen_gw, _w, color=CONTEXT)
    _ax.bar(_x, _storage_gw, _w, bottom=_gen_gw, color=COLORS["accent"])

    # Direct-label totals on each bar
    for _i, (_g, _s) in enumerate(zip(_gen_gw, _storage_gw)):
        _ax.text(
            _i, _g + _s + 30, f"{_g + _s:,}",
            ha="center", fontsize=FONTS["annotation"], fontweight="bold",
            color=COLORS["text_dark"],
        )

    # Attrition callout — positioned clear of bars, right side
    _ax.text(
        4.45, 2500,
        f"Of all capacity queued 2000\u20132024:\n{stats['queue_withdrawal_pct']}% withdrawn, {stats['queue_completion_pct']}% completed",
        fontsize=FONTS["annotation"], color=COLORS["text_dark"],
        ha="left", va="top",
        bbox={"boxstyle": "round,pad=0.4", "facecolor": "white",
              "edgecolor": CONTEXT, "alpha": 0.9},
    )

    _ax.set_xticks(_x)
    _ax.set_xticklabels(_years, fontsize=FONTS["tick_label"])
    _ax.set_ylabel("GW", fontsize=FONTS["axis_label"])
    _ax.tick_params(axis="y", labelsize=FONTS["tick_label"])
    _ax.set_ylim(0, 3600)
    _ax.set_xlim(-0.5, 5.6)
    _ax.spines[["top", "right"]].set_visible(False)

    from matplotlib.patches import Patch as _Patch
    legend_below(
        _ax,
        handles=[_Patch(facecolor=CONTEXT), _Patch(facecolor=COLORS["accent"])],
        labels=["Generation", "Storage"],
    )

    chart_title(
        _fig_queue,
        "U.S. interconnection queue surpassed 3,000 GW \u2014 but most projects never get built",
    )
    save_fig(_fig_queue, cfg.img_dir / "dd001_queue_funnel.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo, stats):
    _chart = mo.image(
        src=(cfg.img_dir / "dd001_queue_funnel.png").read_bytes(), width=850
    )
    mo.md(f"""
    # The queue hit {stats['queue_total_gw']:,} GW — but {stats['queue_withdrawal_pct']}% of projects are eventually withdrawn

    {_chart}

    *Total generation and storage capacity in U.S. interconnection queues at year-end.
    From 2000–2024 cohorts, {stats['queue_withdrawal_pct']}% of queued capacity was
    withdrawn and {stats['queue_completion_pct']}% reached commercial operation
    (Rand et al., LBNL, 2025, Table 3). Queue volume rose about {stats['queue_yoy_pct']}%
    in 2024 to {stats['queue_total_gw']:,} GW. LBNL also tracked 100+ GW of large-load
    requests — primarily data center connections — for the first time in the dataset's
    history. Source: Rand et al., LBNL, "Queued Up" 2025 Edition (data through end-2024).*
    """)
    return


@app.cell
def _(COLORS, CONTEXT, FIGSIZE, FONTS, cfg, chart_title, np, plt, save_fig, stats):
    # Dot matrix: 10×10 grid of circles — each circle = 1% of US private
    # nonresidential fixed investment. 10 filled (accent) = AI capex cohort.
    _capex = round(stats["capex_2025"])
    _bea_total = round(stats["pnfi_bn"])
    _pct = stats["pnfi_share_pct"]
    _filled = round(_pct)        # number of accent circles (≈10)
    _rows, _cols = 10, 10
    _total = _rows * _cols       # 100 circles = 100%

    # Grid coordinates — all 100 circles (full economy)
    _all_xs = np.tile(np.arange(_cols), _rows)
    _all_ys = np.repeat(np.arange(_rows), _cols)  # row 0 = bottom

    # Accent positions: first _filled dots in raster order (left→right, bottom→top)
    # Dynamic — if pnfi_share_pct changes, the filled count updates automatically
    _all_positions = [(c, r) for r in range(_rows) for c in range(_cols)]
    _accent_positions = _all_positions[:_filled]
    _accent_xs = np.array([p[0] for p in _accent_positions])
    _accent_ys = np.array([p[1] for p in _accent_positions])

    fig_share, _ax = plt.subplots(figsize=FIGSIZE["single"])

    # Pass 1: all circles as outlines (context — the full economy)
    _ax.scatter(
        _all_xs, _all_ys, s=380,
        facecolors="none", edgecolors=CONTEXT,
        linewidths=1.5, zorder=1,
    )
    # Pass 2: filled circles for AI capex (accent — the story)
    _ax.scatter(
        _accent_xs, _accent_ys, s=380,
        c=COLORS["accent"], linewidths=0, zorder=2,
    )

    # Annotation: in left margin (outside grid), arrow pointing to block centre
    _ax.annotate(
        f"Hyperscaler capex — 6 companies\n\\${_capex:,}B ({_pct:.0f}% of total US\nprivate investment)",
        xy=(0, 1.5),
        xytext=(-0.5, 5),
        va="center", ha="right",
        fontsize=FONTS["annotation"], color=COLORS["accent"], fontweight="bold",
        clip_on=False,
        arrowprops=dict(
            arrowstyle="->", color=COLORS["accent"],
            connectionstyle="arc3,rad=-0.2", linewidth=1.5,
            clip_on=False,
        ),
    )

    # Footer: unit explanation (centred on the dot grid, not the full axes width)
    _ax.text(
        (_cols - 1) / 2, -1.1,
        f"Each circle = ~\\${_bea_total // _total:,}B  "
        f"(1% of \\${_bea_total / 1000:.1f}T US private nonresidential investment)",
        ha="center", va="top",
        fontsize=FONTS["annotation"], color=COLORS["text_light"],
    )

    _ax.set_xlim(-5.5, _cols + 0.5)  # left margin holds annotation text
    _ax.set_ylim(-1.8, _rows - 0.2)
    _ax.set_aspect("equal")
    _ax.axis("off")

    chart_title(
        fig_share,
        f"AI capex is ~{_pct:.0f}% of all US private nonresidential investment",
    )
    plt.tight_layout()
    save_fig(fig_share, cfg.img_dir / "dd001_capex_us_share.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo, stats):
    _chart = mo.image(
        src=(cfg.img_dir / "dd001_capex_us_share.png").read_bytes(), width=850
    )
    mo.md(f"""
    # AI capex is ~{stats['pnfi_share_pct']:.0f}% of all US private nonresidential investment

    {_chart}

    *U.S. private nonresidential fixed investment is about \\${stats['pnfi_bn'] / 1000:.1f}T
    SAAR (BEA/FRED PNFI, Q2 2025). Combined 2025 AI capex (~\\${stats['capex_2025']:.0f}B,
    six companies) is roughly {stats['pnfi_share_pct']:.0f}% of that total — a
    concentration signal: a small set of firms is deploying infrastructure at
    macro-relevant scale.*

    **Caveat:** the numerator is global AI capex, while the denominator is U.S.-only
    investment. The true U.S.-specific share is lower. For context, total U.S. data
    center construction spending is estimated at \\${stats['dc_construction_low_bn']}–{stats['dc_construction_high_bn']}B
    annually (JLL, CBRE), though the Census Bureau does not track data centers as a
    separate construction category.
    """)
    return


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    ---

    ## Does AI Efficiency Reduce Infrastructure Demand?

    As AI models become more efficient to train and run, a central question opens up:
    do efficiency gains compress the need for infrastructure, or do they expand it by
    making AI cheaper and more broadly deployed? This is not an abstract question —
    the answer determines whether the current buildout is appropriately sized or
    structurally oversized.

    DeepSeek R1 (January 2025) created the sharpest test of this question to date.
    The reported ~$6M figure for DeepSeek-V3's final training run (arXiv:2412.19437,
    December 2024) is self-reported and partial — one run, not full development costs —
    but the directional claim is significant: frontier-capable models may be achievable
    at costs far below the infrastructure buildout implies. Nvidia lost
    ~\\${stats['nvda_deepseek_loss_bn']}B in market cap in a single day on the implication.

    Through four quarters of data, the answer from actual spending is: no slowdown.
    All major builders accelerated through 2025:

    | Company | 2024 actual | 2025 actual | 2026 guidance |
    | :--- | :--- | :--- | :--- |
    | Amazon | ~\\${stats['amzn_2024']:.0f}B | ~\\${stats['amzn_2025']:.0f}B | \\${stats['amzn_2026g']:.0f}B |
    | Alphabet | ~\\${stats['googl_2024']:.0f}B | ~\\${stats['googl_2025']:.0f}B | \\${stats['googl_2026g']:.0f}B |
    | Microsoft | ~\\${stats['msft_2024']:.0f}B | ~\\${stats['msft_2025']:.0f}B | ~\\${stats['msft_2026g']:.0f}B |
    | Meta | ~\\${stats['meta_2024']:.0f}B | ~\\${stats['meta_2025']:.0f}B | \\${stats['meta_2026g_low']}-{stats['meta_2026g_high']}B |

    Management teams reached for the **Jevons paradox** to explain this: lower AI
    inference costs increase adoption, which increases total compute demand. Lower cost
    per unit → more units → net increase in infrastructure required. Historical
    precedent supports the mechanism — LED lighting, Moore's Law, and cloud computing
    all followed this pattern. Whether it applies here is the open empirical question.

    Efficiency gains are real and accelerating. Epoch AI documents ~3× annual
    algorithmic efficiency gains in language models (roughly an 8-month doubling time,
    *Algorithmic Progress in Language Models*, epochai.org). The Stanford HAI *AI
    Index* 2024 (Ch. 2) documented a ~280× API price decline in 2022–2023, driven by
    competitive dynamics as much as pure efficiency. If inference costs continue falling
    at that rate, sustaining the current revenue-to-capex ratio requires demand to grow
    ~10× over the same period. Cloud revenue is growing
    ~{stats['cloud_yoy_min']:.0f}–{stats['cloud_yoy_max']:.0f}% YoY (Q4 2025). At that
    rate, closing the gap takes roughly 4–6 years. Whether demand elasticity matches
    that trajectory is what this research cannot yet answer. For precedent on how
    productivity gains from general-purpose technologies manifest with a lag, see
    Brynjolfsson, Rock, and Syverson's "Productivity J-Curve" *(AEJ Macroeconomics,
    2021; NBER w25148)*. The combined 2026 guidance of ~\\${stats['guidance_2026_point']:.0f}B
    (caveat band: \\${stats['guidance_2026_low']:.0f}-\\${stats['guidance_2026_high']:.0f}B)
    would consume ~{stats['capex_ocf_2026_pct']:.0f}% of these companies' trailing
    operating cash flow (~\\${stats['ocf_ttm']:.0f}B TTM), far exceeding the 10-year
    average of ~{stats['hist_capex_ocf_avg_pct']}% *(Bernstein Research, 2024)* and approaching the capex/OCF ratios
    that preceded the telecom collapse. Amazon individually is at ~{stats['amzn_ocf_pct']:.0f}%
    (2025 actual capex vs. TTM OCF). This implies significant debt
    issuance or equity raises to fund the buildout.

    **Caveat on guidance reliability:** AI capex guidance has historically
    been revised ±{stats['guidance_max_revision_pct']}% within a single year. Meta cut 2023 guidance {stats['meta_guidance_cut_pct']}% from its
    original \\${stats['meta_2023_guidance_low']}-{stats['meta_2023_guidance_high']}B range to \\${stats['meta_2023']:.0f}B actual (Meta Q3-Q4 2022, Q1 2023 earnings
    calls); Microsoft raised FY2025 guidance {stats['msft_guidance_raise_pct']}% in one quarter, from \\${stats['msft_fy25_initial_g']}B to
    \\${stats['msft_fy25_revised_g']}B (MSFT Q1 FY2025 earnings call). The
    \\${stats['guidance_2026_point']:.0f}B total should be treated as directionally
    correct but uncertain at the company level. *Note: the ±{stats['guidance_band_pct']}%
    band is derived from N=2 observed revision pairs — treat it as a directional bound,
    not a statistically robust confidence interval.*

    For infrastructure analysis, the DeepSeek episode is a test case worth watching:
    **AI infrastructure capex may be stickier than valuations.** Stock prices fluctuated
    on sentiment; capital expenditure programs rolled forward. One episode doesn't
    establish the pattern — Meta held capex flat at ~\\${stats['meta_2022']:.0f}B through
    its "year of efficiency" (2023) while cutting headcount by {stats['meta_headcount_cut_pct']}%
    (Meta 10-K FY2022 → FY2023), showing that unilateral deceleration is possible. What
    the current cycle adds is a competitive dynamic — every company fears falling behind
    on capacity — that raises the cost of being the one that blinks first.
    """)
    return


@app.cell
def _(
    COLORS,
    CONTEXT,
    FIGSIZE,
    FONTS,
    capex_raw,
    cfg,
    chart_title,
    company_color,
    company_label,
    legend_below,
    pd,
    plt,
    save_fig,
):
    _tickers = ["MSFT", "AMZN", "GOOGL", "META"]
    _deepseek_date = pd.Timestamp("2025-01-27")

    fig_quarterly, _ax = plt.subplots(figsize=FIGSIZE["wide"])

    for _ticker in _tickers:
        _sub = capex_raw[capex_raw["ticker"] == _ticker].sort_values("date")
        if len(_sub) < 2:
            continue
        # SWD: pre-DeepSeek is CONTEXT gray, post-DeepSeek is the story
        _pre = _sub[_sub["date"] <= _deepseek_date]
        _post = _sub[_sub["date"] >= _deepseek_date]
        _clr = company_color(_ticker)

        # Context: pre-DeepSeek in gray (not muted brand color)
        _ax.plot(
            _pre["date"], _pre["capex_bn"],
            marker="o", markersize=3, color=CONTEXT,
            linewidth=1.2, alpha=0.5,
        )
        # Story: post-DeepSeek in bold brand color — no slowdown
        _ax.plot(
            _post["date"], _post["capex_bn"],
            marker="o", markersize=6, color=_clr,
            linewidth=3, alpha=1.0,
            label=company_label(_ticker),
        )

    _ax.set_ylabel("Quarterly capex ($B)", fontsize=FONTS["axis_label"])
    _ax.tick_params(axis="both", labelsize=FONTS["tick_label"])
    _ax.grid(True, axis="y", linestyle=":", alpha=0.4)

    # DeepSeek moment — accent it as the dividing line
    _ymax = capex_raw[capex_raw["ticker"].isin(_tickers)]["capex_bn"].max()
    _ax.axvline(
        _deepseek_date, color=COLORS["accent"], linestyle="-", linewidth=2, alpha=0.7,
    )
    _ax.text(
        _deepseek_date,
        _ymax * 0.98,
        "  DeepSeek R1",
        fontsize=FONTS["annotation"],
        color=COLORS["accent"],
        fontweight="bold",
        va="top",
    )
    # Callout: the punchline — position below the lines to avoid overlap
    _ax.text(
        _deepseek_date + pd.Timedelta(days=200),
        _ymax * 0.18,
        "All four accelerated\nafter DeepSeek",
        fontsize=FONTS["annotation"],
        color=COLORS["accent"],
        fontweight="bold",
        ha="left", va="center",
        bbox={"boxstyle": "round,pad=0.4", "fc": "white", "ec": COLORS["accent"], "alpha": 0.8},
    )

    legend_below(_ax, ncol=4)
    chart_title(fig_quarterly, "DeepSeek R1 changed nothing \u2014 all four AI builders accelerated capex")
    plt.tight_layout()
    save_fig(fig_quarterly, cfg.img_dir / "dd001_quarterly_capex.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo):
    _chart = mo.image(
        src=(cfg.img_dir / "dd001_quarterly_capex.png").read_bytes(), width=850
    )
    mo.md(f"""
    # Quarterly capex ramps show no sign of slowing

    {_chart}

    *Quarterly capex for the four largest AI infrastructure spenders. The vertical
    marker indicates DeepSeek R1's release (January 2025). Through Q4 2025, all four
    firms increased spending rather than slowing deployment. Data: yfinance (SEC
    filings, through Q4 2025).*
    """)
    return


@app.cell(hide_code=True)
def _(mo, stats):
    _capex_low = stats["capex_2025"] * stats["analyst_const_pct_low"] / 100
    mo.md("""
    ---

    ## What Persists: The Durability Taxonomy

    Applying the project's analytical framework, AI infrastructure investments
    fall into three durability categories. The distinction matters because financial
    cycles are short, while some infrastructure consequences persist for decades:

    | Category | What Gets Built | Life | Persists? |
    | :--- | :--- | :--- | :--- |
    | **Structural** | Grid upgrades, substations, DC shells | 20-50 yrs | Yes |
    | **Policy-dependent** | Nuclear restarts, SMR, rate structures | Varies | If regime holds |
    | **Demand-thesis-dependent** | GPU clusters, AI cooling, inference HW | 3-6 yrs | No |
    """)
    return


@app.cell
def _(
    COLORS,
    CONTEXT,
    FONTS,
    cfg,
    chart_title,
    legend_below,
    plt,
    save_fig,
    stats,
):
    # Decomposition: shares from FY2024 10-K property schedules, base is 2025 actual
    # Percentages from stats dict (sourced from 10-K filings — see stats cell)
    _total_capex = round(stats["capex_2025"])  # $B, data-driven
    _equip = _total_capex * stats["decomp_equip_pct"] / 100
    _const = _total_capex * stats["decomp_const_pct"] / 100
    _equip_life = 6   # max asset life (years)
    _const_life = 40  # max asset life (years)

    # Gantt timeline: x = calendar years 2025→2065; bar height ∝ capex.
    # Life-span annotations to the right of each bar make both dimensions explicit.
    # Vertical marker at 2031 (equipment end-of-life) + AI demand forecast horizon.
    _h_equip = 1.0                   # reference height (equipment = larger-dollar tier)
    _h_const = (_const / _equip) if _equip > 0 else 0.42  # ~0.42 at 30/70 split

    fig_decomp, _ax = plt.subplots(figsize=FIGSIZE["wide"])

    # Equipment bar: thick, gray, 6-year span from 2025
    _ax.barh(
        [1.6], [_equip_life], height=_h_equip,
        color=CONTEXT, alpha=0.85, edgecolor="white", linewidth=0.5, left=2025,
    )
    # Construction bar: thin, accent, 40-year span from 2025
    _ax.barh(
        [0.6], [_const_life], height=_h_const,
        color=COLORS["accent"], alpha=0.85, edgecolor="white", linewidth=0.5, left=2025,
    )

    # Shaded AI demand uncertainty zone (3-year horizon)
    _ax.axvspan(2025, 2028, alpha=0.06, color=COLORS["accent"])
    _ax.text(
        2026.5, 2.3, "AI demand\nforecast\nhorizon",
        ha="center", fontsize=FONTS["annotation"] - 1, color=COLORS["accent"], alpha=0.7,
    )

    # Vertical line: equipment end-of-life
    _ax.axvline(2025 + _equip_life, color=CONTEXT, linewidth=1, linestyle="--", alpha=0.6)
    _ax.text(
        2025 + _equip_life + 0.3, 2.3, "Equipment\nfully replaced",
        fontsize=FONTS["annotation"] - 1, color=CONTEXT, va="top",
    )

    # Equipment label: dark text inside bar — white had poor contrast against
    # the gray bar + pink forecast shade overlap
    _ax.text(
        2025 + _equip_life / 2, 1.6,
        f"Equipment  \\${_equip:.0f}B", va="center", ha="center",
        fontsize=FONTS["annotation"] - 2, color=COLORS["text_dark"], fontweight="bold",
    )
    _ax.text(
        2025 + _const_life / 2, 0.6,
        f"Construction  \\${_const:.0f}B", va="center", ha="center",
        fontsize=FONTS["annotation"], color="white", fontweight="bold",
    )

    # Life-span annotations to the right of each bar
    _ax.text(
        2025 + _equip_life + 0.5, 1.6, "~6 yr life",
        va="center", fontsize=FONTS["annotation"], color=COLORS["text_dark"],
        fontweight="bold",
    )
    _ax.text(
        2025 + _const_life + 0.5, 0.6, "20\u201340 yr life",
        va="center", fontsize=FONTS["annotation"], color=COLORS["accent"],
        fontweight="bold",
    )

    _ax.set_xlim(2024, 2072)   # extra headroom for life-span labels
    _ax.set_ylim(0.0, 2.6)
    _ax.set_xlabel("Year", fontsize=FONTS["axis_label"])
    _ax.get_yaxis().set_visible(False)
    _ax.tick_params(axis="x", labelsize=FONTS["tick_label"])

    chart_title(
        fig_decomp,
        f"{stats['decomp_const_pct']}% of capex creates 20\u201340 year assets \u2014 the rest depreciates in under 6",
    )
    plt.tight_layout()
    save_fig(fig_decomp, cfg.img_dir / "dd001_capex_decomposition.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo, stats):
    _chart = mo.image(
        src=(cfg.img_dir / "dd001_capex_decomposition.png").read_bytes(), width=850
    )
    mo.md(f"""
    # {stats['decomp_const_pct']}% of capex creates 20-40 year assets — the rest depreciates in under 6

    {_chart}

    *FY2024 10-K property schedules imply a cross-company midpoint near
    ~{stats['decomp_const_pct']}% construction and ~{stats['decomp_equip_pct']}%
    equipment. Construction assets — sites, buildings, substations, interconnects —
    typically persist for 20–40 years. Equipment turns over much faster. In this
    chart, horizontal span represents asset life and bar thickness represents 2025
    capex scale. Note: Alphabet extended server useful life from 4 to 6 years in
    2024, adding ~\\$3.9B to annual operating income — asset life assumptions
    materially affect the economics (Alphabet 10-K FY2024, Note 1).*

    This is the lock-in asymmetry. Investment risk is often evaluated on a 3–5 year
    return horizon, but much of the physical footprint lasts far longer.

    The path-dependency literature (Arthur 1989; David 1985) demonstrates how early
    capital choices in technology platforms create self-reinforcing lock-in — the
    QWERTY keyboard and VHS format are canonical cases. That literature applies
    here with a physical-asset twist: the lock-in is not just technological but
    geographic and infrastructural. Substations, transmission lines, and campus
    foundations cannot be relocated or reallocated the way software platforms can.
    *(Liebowitz & Margolis, 1990, argue the QWERTY case is weaker than David claims —
    the counterargument is noted; physical infrastructure faces stronger path dependency
    than keyboard layouts because relocation costs are genuinely prohibitive.)*
    """)
    return


@app.cell(hide_code=True)
def _(mo, stats):
    _capex_low = stats["capex_2025"] * stats["analyst_const_pct_low"] / 100
    mo.md(f"""
    Some investments begin as demand-thesis-dependent but become structural once
    built. A gas plant built to power a data center campus is demand-thesis-dependent
    at inception. Once built, it operates for 40 years regardless of whether the data
    center scales as planned. The capital decision was AI-driven; the infrastructure
    consequence is not.

    ### The historical parallel

    The dot-com fiber overbuild (1998-2001) is the natural reference point. Large
    capital commitments, strong demand expectations, excess capacity — and then the
    physical infrastructure stayed in the ground and ultimately supported a different
    economic model.

    The fiber analogy is directionally helpful but incomplete. Fiber is passive once
    deployed. Data centers are operating assets with ongoing power, cooling, and
    maintenance requirements — the carrying cost of excess AI infrastructure is higher
    than excess fiber. The better parallel is the *grid infrastructure* built to serve
    data centers: substations, transmission lines, interconnects that are durable,
    broadly reusable, and useful regardless of what the connected load does.

    The question for AI infrastructure is whether the same pattern holds: does the
    grid modernization funded by AI capex retain value even if AI revenue never
    justifies ~\\${stats['capex_2025']:.0f}B+ in annual spending? Applying the durability
    taxonomy: the physical construction layer looks structural — grid upgrades retain
    value regardless of which compute paradigm wins. The equipment layer looks more
    fragile — proprietary AI accelerators and single-purpose cooling systems are harder
    to repurpose. Whether that classification holds depends on what "repurposed" means
    in practice. The evidence so far: FY2024 10-K property
    schedules show construction at {stats['decomp_const_low']}-{stats['decomp_const_high']}% of gross PP&E for Meta, Amazon, and
    Alphabet — higher than the {stats['analyst_const_pct_low']}% often cited in analyst estimates. Even at
    the low end, {stats['analyst_const_pct_low']}% of ~\\${stats['capex_2025']:.0f}B is ~\\${_capex_low:.0f}B in
    durable physical assets deployed in a single year. Cumulated across the 2022–2025
    AI buildout era, the six major builders committed ~\\${stats['ai_era_total_bn']:.0f}B in
    total capex — of which approximately ~\\${stats['ai_era_const_bn']:.0f}B (applying the
    {stats['decomp_const_pct']}% EDGAR-derived construction share) is now embedded in
    physical infrastructure with 20–40 year asset lives, regardless of whether AI
    revenue justifies the original investment thesis.

    **Supply-side constraints: commitment ≠ execution.** The capex figures in this
    notebook measure disclosed capital commitments. Converting those commitments to
    deployed compute capacity faces three binding supply-side constraints not captured
    in the capex numbers:

    - **GPU allocation and advanced packaging:** TSMC's CoWoS (Chip-on-Wafer-on-Substrate)
      packaging capacity is the proximate bottleneck on H100/H200/B200 AI accelerator
      production. TSMC has been running CoWoS at capacity since mid-2023. GPU delivery
      lags order placement by 12–18 months — announced equipment-tier capex and deployed
      compute capacity therefore diverge by at least one procurement cycle.

    - **Grid interconnection:** The median time from interconnection request to operation
      is 4+ years (LBNL *Queued Up* 2025). Committed construction capex cannot be
      energized until grid capacity is allocated. This constraint is analyzed in depth in
      *DD-002: Grid Modernization*.

    - **Transformer supply:** Lead times for large power transformers have extended to
      2+ years. This is the binding constraint on the construction tier specifically —
      data center buildings can be erected faster than the substation equipment needed
      to power them (see archived *CS-1: Transformer Manufacturing*).

    These constraints mean the durability taxonomy conclusions hold even if execution
    lags the capex timeline by 2–4 years: the physical infrastructure gets built,
    just slower than the financial commitments imply.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ---

    ## Where This Research Goes Next

    This notebook maps the premise: AI capital is real and accelerating, but the
    conversion from financial commitment to physical infrastructure is lossy and slow.
    At each stage — valuations, revenue, physical buildout — questions open that the
    announced numbers don't answer. We cannot take announcements at face value.

    The remaining deep dives trace what happens when capital *does* convert:

    - **DD-002: Grid Modernization** (active) — What generation mix is getting
      built? Which fuel types? Where geographically? Who benefits from the
      cost allocation? What feedback loops shape the buildout trajectory?
    - **DD-003: Labor Markets** (scoping) — Who gets hired and displaced? What
      are the temporal dynamics of build-phase construction employment vs.
      long-term operations staffing vs. knowledge-work displacement?
    - **CS-4: Material Supply Chains** (not started) — GOES steel, copper,
      transformers. Where does concentration risk bind?

    ### Key data gaps to resolve

    1. No government statistical series tracks data center construction separately
    2. No clean separation of "AI capex" vs. "general cloud capex" in public filings
    3. Interconnection queue attrition rates are estimated, not precisely tracked
    4. Stargate and similar mega-projects have opaque financial structures
    5. AI-specific electricity consumption at facility level is not systematically reported

    ---

    *Sources: SEC EDGAR (10-K/10-Q filings via yfinance, through Q4 2025),
    Yahoo Finance (market caps, Feb 2026), FRED (BEA PNFI series, Q2 2025 SAAR),
    Sequoia Capital ("The \\$600B Question," Sep 2024), CreditSights (AI capex
    estimates, Jan-Feb 2026), earnings call transcripts (Jan-Feb 2026),
    Rand et al., "Queued Up: Characteristics of Power Plants Seeking Transmission
    Interconnection — As of the End of 2024," LBNL, April 2025 (emp.lbl.gov/queues),
    Palmer et al., "Reforming Electricity Interconnection," Resources for the Future,
    2024.
    See `research/ai_valuation_vs_infrastructure_reality.md` for full source list.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.callout(
        mo.md(
            """
    ## Methods and Reproducibility

    Detailed methods, source-date tables, and SQL hash registry are published in:
    `notebooks/dd001_capital_reality/99_methods_and_sources.py`.
    """
        ),
        kind="info",
    )
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
