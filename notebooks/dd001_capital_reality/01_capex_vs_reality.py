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

    The Magnificent Seven have added ~\\${stats['mkt_gain_t']:.1f} trillion in
    market cap since January 2023. Capital expenditure across the six major AI
    infrastructure builders reached ~\\${stats['capex_2025']:.0f}B in 2025 (up from
    ~\\${stats['capex_2024']:.0f}B in 2024), with ~\\${stats['guidance_2026']:.0f}B guided
    for 2026. But how much of that capital is actually converting to physical
    infrastructure — and what does the grid get from the portion that does?

    The disconnect between financial narrative and physical outcome plays out at
    every level. Markets added ~\\${stats['mkt_gain_t']:.1f}T in value on AI expectations
    while actual annual infrastructure spending reached ~\\${stats['capex_2025']:.0f}B.
    Cloud revenue is growing fast (~\\${stats['cloud_rev_q4_annual']:.0f}B annualized) but
    capex-to-revenue ratios remain far above historical norms. And most of what gets
    announced never gets built — the majority of queued projects are withdrawn before
    reaching operation (LBNL, 2024).

    But here's what matters for the physical economy: ~{stats['decomp_const_pct']}% of
    capex funds construction that creates 20-40 year assets (per FY2024 10-K data).
    Equipment (~{stats['decomp_equip_pct']}%) depreciates in 3-6 years. **The grid gets
    lasting infrastructure even if the AI demand thesis falters.**
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
def _(bea_nipa, capex_annual, citations, cloud_rev, guidance_2026, mkt_cap, ocf_data, pnfi_bn, ppe_schedule, queue_summary):
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
    stats["googl_buildings_pct"] = stats["googl_buildings_pct"]
    stats["amzn_buildings_pct"] = stats["amzn_buildings_pct"]
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
    stats["guidance_max_revision_pct"] = max(
        stats["meta_guidance_cut_pct"], stats["msft_guidance_raise_pct"]
    )

    # Meta headcount reduction (Meta 10-K FY2022 → FY2023)
    stats["meta_headcount_2022"] = int(citations["meta_headcount_2022"])
    stats["meta_headcount_2023"] = int(citations["meta_headcount_2023"])
    stats["meta_headcount_cut_pct"] = round(
        (stats["meta_headcount_2022"] - stats["meta_headcount_2023"])
        / stats["meta_headcount_2022"] * 100
    )

    # External cited constants
    stats["sequoia_rev_target_bn"] = int(citations["sequoia_rev_target_bn"])
    stats["sequoia_rev_target_qtr_bn"] = stats["sequoia_rev_target_bn"] // 4
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
    _ax.set_ylabel("Annual capital expenditure ($B)", fontsize=FONTS["axis_label"])
    _ax.tick_params(axis="y", labelsize=FONTS["tick_label"])

    # Total per company above each bar — the hero element
    for _j, _ticker in enumerate(_tickers):
        _ax.text(
            _j, _bottoms[_j] + 8, f"${_bottoms[_j]:.0f}B",
            ha="center", fontsize=FONTS["annotation"], fontweight="bold",
            color=COLORS["accent"],
        )

    legend_below(_ax, ncol=len(_all_years))
    chart_title(fig_capex, "AI infrastructure capex tripled in three years — and 2026 guidance doubles again")
    plt.tight_layout()
    save_fig(fig_capex, cfg.img_dir / "dd001_capex_acceleration.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo, stats):
    _chart = mo.image(
        src=(cfg.img_dir / "dd001_capex_acceleration.png").read_bytes(), width=850
    )
    mo.md(f"""
    # AI infrastructure capex tripled in three years — and 2026 guidance doubles again

    {_chart}

    *2026 figures are management guidance (hatched bars), not audited actuals.
    Combined capex for these six AI capex leaders: ~\\${stats['capex_2023']:.0f}B (2023) →
    ~\\${stats['capex_2024']:.0f}B (2024) → ~\\${stats['capex_2025']:.0f}B (2025) →
    ~\\${stats['guidance_2026']:.0f}B (2026 guidance). Capex aggregated by calendar year;
    note that Microsoft (June FY) and Oracle (May FY) report on non-calendar fiscal
    years. Capex figures include all capital expenditure, not only AI-related spending —
    notably, Amazon's capex includes logistics and fulfillment infrastructure, which is a
    significant portion of its total (~\\${stats['amzn_2024']:.0f}B in 2024). ~{stats['ai_capex_share_pct']}% of 2026 capex is expected to
    fund AI infrastructure directly (CreditSights, Feb 2026). Additionally, these figures
    exclude leased capacity — significant data center capacity is leased from colocation
    providers (Equinix, Digital Realty) and does not appear in the lessee's capex line.
    Total AI infrastructure investment is higher than what corporate capex alone shows.
    Sources: SEC 10-K/10-Q filings via yfinance, earnings call transcripts (Jan-Feb 2026).*
    """)
    return


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

    *The Magnificent Seven gained ~\\${stats['mkt_gain_t']:.1f}T in market capitalization
    over three years (Jan 2023 - Feb 2026). Combined 2025 capex for the six AI
    infrastructure builders was ~\\${stats['capex_2025']:.0f}B — markets priced in
    ~{stats['ratio_vs_2025']:.0f}x the annual infrastructure investment. The red line
    shows total 2025 capex for scale. Tesla is included in market cap but its capex
    (~\\$11B, primarily automotive) is excluded from the AI capex total; see callout
    below. Note: some companies (AMZN, MSFT) saw mkt cap dip or flatten in early 2026
    even as capex accelerated — the valuation gap is narrowing but remains extreme.
    Sources: Yahoo Finance (market cap, Feb 14 2026), SEC filings via yfinance (capex).*

    Market capitalization reflects discounted future earnings expectations, not
    current asset values — so comparing a stock of expected value to a flow of
    annual spending is a scale comparison, not a like-for-like equivalence. Still,
    the magnitude of the gap reveals how much future revenue growth is already
    priced in, and how little of that expected value has been converted to physical
    infrastructure so far.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    > **The Tesla/xAI question.** Tesla's \\$1.18T market cap gain (Jan 2023 - Feb 2026)
    > is overwhelmingly priced on AI, not cars: forward P/E is ~160x vs. the auto sector
    > median of 6.2x, and Musk claims 80% of Tesla's future value will come from the
    > Optimus robot. Tesla spent ~\\$5B on AI infrastructure in 2024 (44% of total capex),
    > scaling from 35K to 85K H100 GPUs, and guides \\$20B+ for 2026 with a hard pivot
    > toward robotaxi and Optimus production (discontinuing Model S/X to repurpose lines).
    >
    > Separately, Musk's xAI built the 200,000-GPU "Colossus" supercomputer in Memphis
    > for ~\\$7B, raised \\$22B+ in venture capital, and was acquired by SpaceX in February
    > 2026 at a \\$250B valuation. Tesla invested \\$2B in xAI's Series E — over shareholder
    > objections (the non-binding vote rejected the investment; Tesla's board proceeded
    > anyway). Shareholders have sued Musk for diverting \\$500M of Nvidia GPUs and 11+
    > engineers from Tesla to xAI.
    >
    > The Tesla-xAI-SpaceX nexus illustrates a distinct pattern: AI infrastructure capital
    > flowing through a web of related entities with overlapping leadership, shared resources,
    > and ambiguous corporate boundaries. Tesla's capex is excluded from the AI capex
    > total above because its core spend remains automotive, but the AI narrative drives
    > its valuation — making it arguably the most extreme example of the disconnect this
    > analysis tracks.
    >
    > *Sources: Tesla 10-K (2024), TechCrunch, CNBC, CompaniesMarketCap, AI Magazine,
    > court filings (Cleveland Bakers and Teamsters Pension Fund v. Musk, Delaware
    > Chancery Court, June 2024).*
    """)
    return


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    ---

    ## The Revenue Question

    Sequoia Capital's David Cahn estimated (September 2024) that the AI industry
    needs ~\\${stats['sequoia_rev_target_bn']}B in annual revenue to justify the infrastructure buildout. As of
    Q4 2025, the three major cloud providers generated ~\\${stats['cloud_rev_q4']:.0f}B
    in quarterly revenue (~\\${stats['cloud_rev_q4_annual']:.0f}B annualized). Full-year
    2025 combined cloud revenue was ~\\${stats['cloud_rev_2025']:.0f}B.

    The gap is narrowing — but capex is accelerating faster:

    | Metric | 2024 | 2025 | 2026 (guided) |
    | :--- | :--- | :--- | :--- |
    | AI capex (6 co.) | ~\\${stats['capex_2024']:.0f}B | ~\\${stats['capex_2025']:.0f}B | ~\\${stats['guidance_2026']:.0f}B |
    | Cloud revenue (3 providers) | ~\\${stats['cloud_rev_2024']:.0f}B | ~\\${stats['cloud_rev_2025']:.0f}B | est. ~\\${stats['cloud_rev_2026_low']}-{stats['cloud_rev_2026_high']}B\\*\\* |
    | Capex / Revenue ratio\\* | ~{stats['capex_2024'] / stats['cloud_rev_2024']:.1f}x | ~{stats['capex_2025'] / stats['cloud_rev_2025']:.1f}x | ~{stats['capex_rev_2026_low']}-{stats['capex_rev_2026_high']}x |

    \\*This ratio overstates the mismatch: the numerator covers 6 companies (including
    Meta, Oracle, Nvidia) while the denominator covers only 3 cloud providers' reported
    cloud segments (AWS, Microsoft Intelligent Cloud, Google Cloud). Meta and Nvidia
    do not report comparable cloud revenue. An apples-to-apples 3-company ratio
    (AMZN + GOOGL + MSFT capex vs. their cloud revenue) would be lower — but still
    elevated by historical standards. The directional trend is clear either way:
    capex is outpacing revenue growth.

    \\*\\*2026 cloud revenue estimate based on Q4 2025 run rate extrapolation plus
    consensus analyst estimates (Morgan Stanley, Goldman Sachs, Jan-Feb 2026).

    **The ratio is getting worse, not better.** In normal infrastructure businesses,
    capex-to-revenue ratios of 1-2x are sustainable. At the current trajectory, these
    companies are spending more on infrastructure than their cloud businesses generate
    in revenue. The bet is that AI-driven demand creates a step function in revenue
    growth.

    **Counterargument:** Cloud revenue is growing {stats['cloud_yoy_min']:.0f}-{stats['cloud_yoy_max']:.0f}% YoY across providers (Q4 2025),
    and Google Cloud's contracted backlog surged {stats['gcp_backlog_growth_pct']}% to \\${stats['gcp_backlog_bn']}B (Alphabet Q4 2025
    earnings call). But a meaningful portion is these companies selling AI services
    to each other or to VC-funded startups — circular spending that inflates the
    top line without proving durable end-user demand. VC investment in AI/ML startups
    reached \\${stats['vc_ai_2024_bn']}B globally in 2024 — over a third of all VC dollars (PitchBook,
    2025 Annual VC Report) — and
    many of those startups are major cloud customers. If VC funding contracts,
    a portion of cloud revenue disappears with it. This is the same dynamic
    that inflated telecom revenue in 1999-2000.

    The revenue gap matters for this research because it determines **durability**.
    If AI revenue catches up, the infrastructure is justified. If it doesn't,
    the physical assets persist anyway — but the economics shift from
    "demand-thesis-dependent" to "stranded or repurposed."
    """)
    return


@app.cell
def _(
    COLORS,
    CONTEXT,
    FIGSIZE,
    FONTS,
    cfg,
    chart_title,
    cloud_rev,
    legend_below,
    pd,
    plt,
    save_fig,
    stats,
):
    # Revenue gap chart: quarterly cloud revenue trajectory vs capex trajectory
    _cloud_quarterly = (
        cloud_rev.groupby("quarter")["revenue_bn"]
        .sum()
        .reset_index()
        .sort_values("quarter")
    )
    _cloud_quarterly["date"] = pd.to_datetime(
        _cloud_quarterly["quarter"].str.replace(r"(\d{4})-Q(\d)", r"\1", regex=True)
        + "-"
        + _cloud_quarterly["quarter"].str.replace(
            r"(\d{4})-Q(\d)", lambda m: str(int(m.group(2)) * 3), regex=True
        )
        + "-28",
        format="%Y-%m-%d",
    )

    fig_rev, _ax = plt.subplots(figsize=FIGSIZE["wide"])

    _ax.bar(
        _cloud_quarterly["date"],
        _cloud_quarterly["revenue_bn"],
        width=60,
        color=CONTEXT,
        alpha=0.7,
        label="Combined cloud revenue (AWS + MSFT Cloud + GCP)",
    )

    # Reference line: Sequoia $600B annual target (= $150B/quarter)
    _target_qtr = stats["sequoia_rev_target_qtr_bn"]
    _ax.axhline(_target_qtr, color=COLORS["accent"], linestyle="--", linewidth=2, alpha=0.8)
    _ax.text(
        _cloud_quarterly["date"].iloc[-1],
        _target_qtr + 3,
        f'  ${stats["sequoia_rev_target_bn"]}B/yr target (Sequoia)',
        fontsize=FONTS["annotation"],
        color=COLORS["accent"],
        fontweight="bold",
        va="bottom",
    )

    # Annotate latest quarter
    _latest = _cloud_quarterly.iloc[-1]
    _ax.text(
        _latest["date"],
        _latest["revenue_bn"] + 3,
        f"${_latest['revenue_bn']:.0f}B",
        ha="center",
        fontsize=FONTS["annotation"],
        fontweight="bold",
        color=COLORS["text_dark"],
    )

    _ax.set_ylabel("Quarterly cloud revenue ($B)", fontsize=FONTS["axis_label"])
    _ax.tick_params(axis="both", labelsize=FONTS["tick_label"])

    legend_below(_ax, ncol=1)
    chart_title(fig_rev, "Cloud revenue growing but still well below the capex justification threshold")
    plt.tight_layout()
    save_fig(fig_rev, cfg.img_dir / "dd001_revenue_gap.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo, stats):
    _chart = mo.image(
        src=(cfg.img_dir / "dd001_revenue_gap.png").read_bytes(), width=850
    )
    mo.md(f"""
    # Cloud revenue is growing fast — but capex is growing faster

    {_chart}

    *Combined quarterly revenue for AWS, Microsoft Intelligent Cloud, and Google Cloud
    Platform. The dashed line shows the ~\\${stats['sequoia_rev_target_qtr_bn']}B/quarter (\\${stats['sequoia_rev_target_bn']}B/year) threshold Sequoia
    estimated would justify current infrastructure spending. Q4 2025 combined revenue
    was ~\\${stats['cloud_rev_q4']:.0f}B (~\\${stats['cloud_rev_q4_annual']:.0f}B annualized).
    Note: Microsoft Intelligent Cloud includes Azure plus other server products, making
    it a broader measure than pure cloud compute. Revenue segments were restated in
    Microsoft's FY2025 reporting. Sources: SEC filings, earnings releases (Q1 2023 –
    Q4 2025).*
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
    from matplotlib.patches import Patch, Rectangle

    # Decomposition: shares from FY2024 10-K property schedules, base is 2025 actual
    # Percentages from stats dict (sourced from 10-K filings — see stats cell)
    _total_capex = round(stats["capex_2025"])  # $B, data-driven
    _equip = _total_capex * stats["decomp_equip_pct"] / 100
    _const = _total_capex * stats["decomp_const_pct"] / 100
    _equip_life = 6   # max asset life (years)
    _const_life = 40  # max asset life (years)

    fig_decomp, _ax = plt.subplots(figsize=FIGSIZE["single"])

    # Construction: wide rectangle, short — the lock-in story (accent)
    _ax.add_patch(Rectangle(
        (0, 0), _const_life, _const,
        facecolor=COLORS["accent"], alpha=0.85,
        edgecolor="white", linewidth=1.5,
    ))
    # Equipment: narrow rectangle, tall — depreciates fast (context gray)
    _ax.add_patch(Rectangle(
        (0, 0), _equip_life, _equip,
        facecolor=CONTEXT, alpha=0.85,
        edgecolor="white", linewidth=1.5,
    ))

    # Asset life labels beside each bar
    _ax.text(
        _equip_life + 1, _equip * 0.55,
        "3\u20136 years",
        fontsize=FONTS["annotation"], color=COLORS["text_dark"], fontweight="bold",
    )
    _ax.text(
        _const_life + 1, _const * 0.5,
        "20\u201340 years",
        fontsize=FONTS["annotation"], color=COLORS["accent"], fontweight="bold",
    )

    # Axes: only show meaningful ticks
    _ax.set_xlim(0, 48)
    _ax.set_ylim(0, _equip * 1.15)
    _ax.set_xticks([_equip_life, _const_life])
    _ax.set_yticks([_const, _equip])
    _ax.set_yticklabels(
        [f"\\${_const:.0f}B", f"\\${_equip:.0f}B"],
        fontsize=FONTS["tick_label"],
    )
    _ax.tick_params(axis="x", labelsize=FONTS["tick_label"])
    _ax.set_xlabel("Asset Life (years)", fontsize=FONTS["axis_label"], style="italic")
    _ax.set_ylabel("Capex", fontsize=FONTS["axis_label"], style="italic")

    legend_below(
        _ax,
        handles=[
            Patch(facecolor=CONTEXT, edgecolor=CONTEXT, alpha=0.85),
            Patch(facecolor=COLORS["accent"], edgecolor=COLORS["accent"], alpha=0.85),
        ],
        labels=[
            "Equipment (servers, GPUs, networking)",
            "Construction (buildings, substations, power)",
        ],
    )

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

    *Split derived from FY2024 10-K property schedules: Meta reports {stats['meta_buildings_pct']}% buildings/land/CIP
    vs. {stats['meta_servers_pct']}% servers/network; Amazon {stats['amzn_buildings_pct']}% buildings vs. {stats['amzn_equipment_pct']}% equipment; Alphabet {stats['googl_buildings_pct']}% buildings
    vs. {stats['googl_tech_pct']}% technical infrastructure. Cross-company midpoint: ~{stats['decomp_equip_pct']}% equipment (range: {stats['decomp_equip_low']}-{stats['decomp_equip_high']}%),
    ~{stats['decomp_const_pct']}% construction (range: {stats['decomp_const_low']}-{stats['decomp_const_high']}%), ~{stats['decomp_other_pct']}% other (land, permitting, soft costs). Ratios
    reflect cumulative gross PP&E (the stock of assets), which may differ from marginal capex
    flows in any given year. Bar height reflects 2025 annual spend; width reflects asset life.
    Note: Google extended server useful life from 4 to 6 years in 2024, adding ~\\$3.9B to
    annual operating income — asset life assumptions materially affect the economics
    (Alphabet 10-K FY2024, Note 1).*

    This asymmetry is the crux of the infrastructure lock-in problem. The financial
    risk (will AI generate returns?) is a 3-5 year question. The infrastructure
    consequence (what did we build?) is a 30-50 year answer.
    """)
    return


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    ---

    ## Announcements vs. Physical Reality

    The gap between what's announced and what gets built is enormous:

    - **Stargate Project:** \\${stats['stargate_announced_bn']}B announced (Jan 2025). \\${stats['stargate_initial_bn']}B initially committed.
      SoftBank's balance sheet had ~\\$30-40B deployable capital. Financial structure
      remains opaque. *(Sources: White House announcement, Jan 2025; FT analysis)*
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
    real, but the conversion rate from announcement to operating infrastructure is
    far lower than headlines suggest.
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

    *Total generation and storage capacity in U.S. interconnection queues, year-end.
    Of all capacity that requested interconnection from 2000-2024, only {stats['queue_completion_pct']}% reached
    commercial operation while {stats['queue_withdrawal_pct']}% was withdrawn. Completion rates by cohort: {stats['queue_cohort_2000_2005_pct']}%
    (2000-2005), {stats['queue_cohort_2006_2010_pct']}% (2006-2010), {stats['queue_cohort_2011_2015_pct']}% (2011-2015), {stats['queue_cohort_2016_2020_pct']}% (2016-2020) — rates have
    always been low and are declining (Rand et al., 2025, Table 3). The queue grew
    ~{stats['queue_yoy_pct']}% in 2024 to over {stats['queue_total_gw']:,} GW.
    Separately, over 100 GW of large load (primarily data center) interconnection
    requests were tracked for the first time (Rand et al., 2025).
    Source: Rand et al., LBNL, "Queued Up" 2025 Edition (data through end-2024).*
    """)
    return


@app.cell
def _(COLORS, CONTEXT, FIGSIZE, FONTS, cfg, chart_title, plt, save_fig, stats):
    import matplotlib.patches as _mp
    import matplotlib.path as _mpath

    _capex = round(stats["capex_2025"])  # data-driven from yfinance
    _bea_total = round(stats["pnfi_bn"])  # FRED PNFI, latest quarterly SAAR
    _pct = stats["pnfi_share_pct"]

    # BEA categories ($B, approximate shares of PNFI) — bottom to top
    # Shares from stats dict (sourced from BEA NIPA Table 5.3.5, 2024 annual)
    _cats = [
        ("Structures", round(_bea_total * stats["bea_structures_pct"] / 100)),
        ("Equipment", round(_bea_total * stats["bea_equipment_pct"] / 100)),
        ("Intellectual property", round(_bea_total * stats["bea_ip_pct"] / 100)),
    ]
    _cat_sum = sum(v for _, v in _cats)

    fig_share, _ax = plt.subplots(figsize=FIGSIZE["wide"])

    # --- Layout constants ---
    _lx = 2.5    # left column right edge
    _rx = 7.5    # right column left edge
    _cw = 0.7    # column width
    _gap = 50    # visual gap between right-side nodes ($B)

    # --- Compute vertical positions ---
    # Left: contiguous (no gaps)
    _left_pos = []
    _ly = 0.0
    for _, _val in _cats:
        _left_pos.append((_ly, _ly + _val))
        _ly += _val

    # Right: spaced with gaps
    _right_pos = []
    _ry = 0.0
    for _i, (_, _val) in enumerate(_cats):
        _right_pos.append((_ry, _ry + _val))
        _ry += _val + _gap
    _max_y = max(_ly, _ry)

    # --- Left node ---
    _ax.add_patch(_mp.Rectangle(
        (_lx - _cw, 0), _cw, _cat_sum,
        facecolor=CONTEXT, alpha=0.5, edgecolor="white", linewidth=1,
    ))
    # Hyperscaler slice at bottom (accent)
    _ax.add_patch(_mp.Rectangle(
        (_lx - _cw, 0), _cw, _capex,
        facecolor=COLORS["accent"], alpha=0.75, edgecolor="white", linewidth=1,
    ))

    # --- Right nodes + flow bands ---
    _xm = (_lx + _rx) / 2
    for _i, (_name, _val) in enumerate(_cats):
        _ly0, _ly1 = _left_pos[_i]
        _ry0, _ry1 = _right_pos[_i]

        # Right rectangle
        _ax.add_patch(_mp.Rectangle(
            (_rx, _ry0), _cw, _val,
            facecolor=CONTEXT, alpha=0.5, edgecolor="white", linewidth=1,
        ))

        # S-curve flow band (cubic Bezier)
        verts = [
            (_lx, _ly0),
            (_xm, _ly0), (_xm, _ry0), (_rx, _ry0),
            (_rx, _ry1),
            (_xm, _ry1), (_xm, _ly1), (_lx, _ly1),
            (_lx, _ly0),
        ]
        codes = [
            _mpath.Path.MOVETO,
            _mpath.Path.CURVE4, _mpath.Path.CURVE4, _mpath.Path.CURVE4,
            _mpath.Path.LINETO,
            _mpath.Path.CURVE4, _mpath.Path.CURVE4, _mpath.Path.CURVE4,
            _mpath.Path.CLOSEPOLY,
        ]
        _ax.add_patch(_mp.PathPatch(
            _mpath.Path(verts, codes),
            facecolor=CONTEXT, alpha=0.3,
            edgecolor="none",
        ))

        # Right-side label
        _ax.text(
            _rx + _cw + 0.2, (_ry0 + _ry1) / 2,
            f"{_name}\n${_val:,}B",
            ha="left", va="center",
            fontsize=FONTS["annotation"],
            color=COLORS["text_dark"],
        )

    # --- Left-side labels ---
    _ax.text(
        _lx - _cw - 0.15, _cat_sum / 2,
        f"US nonresidential\nfixed investment\n${_bea_total / 1000:.1f}T/year",
        ha="right", va="center",
        fontsize=FONTS["annotation"], fontweight="bold",
        color=COLORS["text_dark"],
    )
    _ax.text(
        _lx - _cw - 0.15, _capex / 2,
        f"AI capex cohort\n${_capex}B ({_pct:.0f}%)",
        ha="right", va="center",
        fontsize=FONTS["annotation"], fontweight="bold",
        color=COLORS["accent"],
    )

    _ax.set_xlim(0, 10.5)
    _ax.set_ylim(-120, _max_y + 120)
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

    *Total US private nonresidential fixed investment is ~\\${stats['pnfi_bn'] / 1000:.1f}T
    SAAR (BEA NIPA Table 5.3.5, Q2 2025 via FRED series PNFI). Combined AI capex
    (~\\${stats['capex_2025']:.0f}B in 2025) represents a significant and rapidly growing
    share — concentrated in a handful of companies making infrastructure decisions that
    normally take decades of utility planning. Category shares (structures ~{stats['bea_structures_pct']}%,
    equipment ~{stats['bea_equipment_pct']}%, IP ~{stats['bea_ip_pct']}%) are approximate from BEA Table 5.3.5.*

    **Caveat:** This comparison overstates the US-specific share. AI infrastructure
    capex is global (significant spending in Europe, Asia, and the Middle East), while
    the BEA denominator is US-only. The true US share is lower, but no public data
    cleanly separates domestic from international AI capex.

    For context: total US data center construction spending is estimated at \\${stats['dc_construction_low_bn']}-{stats['dc_construction_high_bn']}B
    annually (JLL, CBRE). The Census Bureau's C30 construction series does not
    separately report data centers — they are buried in "commercial/warehouse"
    categories. This is one of several critical data gaps.
    """)
    return


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    ---

    ## The DeepSeek Test

    DeepSeek's R1 model (January 2025) demonstrated competitive AI performance at
    reportedly much lower training costs. Nvidia lost ~\\${stats['nvda_deepseek_loss_bn']}B in market cap in a
    single day. It was the first real test of whether efficiency gains would reduce
    infrastructure demand.

    **They didn't.** A year later, the 2025 actuals are in — every major AI
    infrastructure builder *accelerated*:

    | Company | 2024 actual | 2025 actual | 2026 guidance |
    | :--- | :--- | :--- | :--- |
    | Amazon | ~\\${stats['amzn_2024']:.0f}B | ~\\${stats['amzn_2025']:.0f}B | \\${stats['amzn_2026g']:.0f}B |
    | Alphabet | ~\\${stats['googl_2024']:.0f}B | ~\\${stats['googl_2025']:.0f}B | \\${stats['googl_2026g']:.0f}B |
    | Microsoft | ~\\${stats['msft_2024']:.0f}B | ~\\${stats['msft_2025']:.0f}B | ~\\${stats['msft_2026g']:.0f}B |
    | Meta | ~\\${stats['meta_2024']:.0f}B | ~\\${stats['meta_2025']:.0f}B | \\${stats['meta_2026g_low']}-{stats['meta_2026g_high']}B |

    Management teams invoked the **Jevons paradox**: cheaper AI inference increases
    adoption and ultimately increases total compute demand. Historical precedent
    (LED lighting, Moore's Law, cloud computing) supports this — but it is not
    guaranteed to apply. The combined 2026 guidance of ~\\${stats['guidance_2026']:.0f}B
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
    \\${stats['msft_fy25_revised_g']}B (MSFT Q1 FY2025 earnings call). The \\${stats['guidance_2026']:.0f}B total should be treated as
    directionally correct but uncertain at the company level.

    For infrastructure analysis, the DeepSeek episode reinforced a key finding:
    **AI infrastructure capex is stickier than valuations.** Stock prices fluctuate
    on sentiment; capital expenditure programs, once committed, roll forward on
    multi-year procurement contracts, construction timelines, and competitive
    pressure. This is not absolute — Meta held capex flat at ~\\${stats['meta_2022']:.0f}B
    through its "year of efficiency" (2023) while cutting headcount by {stats['meta_headcount_cut_pct']}%
    (Meta 10-K FY2022 → FY2023), and
    the stock rallied — but the current competitive dynamic, where every company
    fears falling behind on AI capacity, makes unilateral deceleration costly.
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

    *Quarterly capital expenditure for the four largest AI infrastructure spenders.
    The red line marks DeepSeek R1's release (January 2025). Despite the efficiency
    shock, all four accelerated capex through 2025. Data: yfinance (SEC filings,
    through Q4 2025).*
    """)
    return


@app.cell(hide_code=True)
def _(mo, stats):
    _capex_low = stats["capex_2025"] * stats["analyst_const_pct_low"] / 100
    mo.md(f"""
    ---

    ## What Persists: The Durability Taxonomy

    Applying the project's analytical framework, AI infrastructure investments
    fall into three durability categories:

    | Category | What Gets Built | Life | Persists? |
    | :--- | :--- | :--- | :--- |
    | **Structural** | Grid upgrades, substations, DC shells | 20-50 yrs | Yes |
    | **Policy-dependent** | Nuclear restarts, SMR, rate structures | Varies | If regime holds |
    | **Demand-thesis-dependent** | GPU clusters, AI cooling, inference HW | 3-6 yrs | No |

    The interesting cases are investments that **start as demand-thesis-dependent
    but create structural demand through second-order effects.** A gas plant built
    to power a data center campus is demand-thesis-dependent at inception. Once
    built, it operates for 40 years regardless of whether the data center scales
    as planned. The capital decision was AI-driven; the infrastructure consequence
    is not.

    ### The historical parallel

    The dot-com fiber overbuild (1998-2001) was called a bubble — and it was. But
    the fiber stayed in the ground. Within a decade, traffic growth consumed the
    excess capacity and then some. The physical infrastructure outlasted the
    financial thesis that built it.

    **The analogy has limits.** Dark fiber requires near-zero maintenance — it sits
    in conduit until someone lights it. Data centers are not passive assets. They
    require continuous power, cooling, and maintenance. A stranded data center is
    not a stranded fiber cable — it has ongoing operating costs even when idle.
    The better parallel is the *grid infrastructure* built to serve data centers
    (substations, transmission lines), which is closer to the fiber analogy:
    durable, low-maintenance, and useful regardless of what the connected load does.

    The question for AI infrastructure is whether the same pattern holds: **does
    the grid modernization funded by AI capex retain value even if AI revenue
    never reaches \\${stats['sequoia_rev_target_bn']}B?** The durability taxonomy says yes for the physical
    construction layer and no for the equipment layer — and this qualitative
    conclusion holds across plausible decomposition ranges. FY2024 10-K property
    schedules show construction at {stats['decomp_const_low']}-{stats['decomp_const_high']}% of gross PP&E for Meta, Amazon, and
    Alphabet — higher than the {stats['analyst_const_pct_low']}% often cited in analyst estimates. Even at
    the low end, {stats['analyst_const_pct_low']}% of ~\\${stats['capex_2025']:.0f}B is ~\\${_capex_low:.0f}B in
    durable physical assets deployed in a single year.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ---

    ## Where This Research Goes Next

    This notebook establishes the premise: AI capital is real and accelerating,
    but the conversion from financial commitment to physical infrastructure is
    lossy and slow. At every stage — valuations, revenue, physical buildout —
    the gap between narrative and reality widens. We cannot take announcements
    at face value.

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


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
