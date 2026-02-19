import marimo

__generated_with = "0.19.11"
app = marimo.App(
    app_title="DD-001: Markets and Money",
    css_file="../../src/notebook_theme/custom.css",
    html_head_file="../../src/notebook_theme/head.html",
)


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    # AI Valuations vs. Infrastructure Spending
    ## Decision Lens for 2026 Allocation

    *Thandolwethu Zwelakhe Dlamini*

    ---

    The Magnificent Seven have added about \\${stats['mkt_gain_t']:.1f} trillion in market
    capitalisation since January 2023. Capital expenditure across six major AI infrastructure
    builders reached about \\${stats['capex_2025']:.0f}B in 2025, up from \\${stats['capex_2024']:.0f}B
    in 2024, with \\${stats['guidance_2026_point']:.0f}B guided for 2026 (caveat band:
    \\${stats['guidance_2026_low']:.0f}–\\${stats['guidance_2026_high']:.0f}B). The central
    question is whether that financial commitment is converting to physical infrastructure, and
    whether the revenue base justifies the spend.

    Cloud revenue for the three cloud providers (Amazon, Alphabet, Microsoft) was about
    \\${stats['cloud_rev_2025']:.0f}B in 2025 — against capex of \\${stats['capex_3co_2025']:.0f}B for
    the same firms. Capex overtook cloud revenue on a quarterly basis in late 2025, a crossover
    that had never happened in the platform era. Whether AI-driven demand reverses that ratio
    — or whether it signals persistent overinvestment — is the open question.
    """)
    return


@app.cell
def _():
    import sys

    import marimo as mo
    sys.path.insert(0, str(mo.notebook_dir().parent.parent))
    import matplotlib.patches as mpatches
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd

    from src.data.db import query
    from src.notebook import save_fig, setup
    from src.plotting import (
        COLORS,
        CONTEXT,
        FIGSIZE,
        FLOW_FONT_SIZE,
        FONTS,
        chart_title,
        company_color,
        company_label,
        flow_diagram,
        legend_below,
    )
    cfg = setup()
    return (
        COLORS,
        CONTEXT,
        FIGSIZE,
        FLOW_FONT_SIZE,
        FONTS,
        cfg,
        chart_title,
        company_color,
        company_label,
        flow_diagram,
        legend_below,
        mo,
        mpatches,
        np,
        pd,
        plt,
        query,
        save_fig,
    )


@app.cell
def _(pd, query):
    capex_raw = query("""
        SELECT ticker, date, capex_bn
        FROM energy_data.hyperscaler_capex ORDER BY date, ticker
    """)
    capex_raw["date"] = pd.to_datetime(capex_raw["date"])
    capex_raw["year"] = capex_raw["date"].dt.year

    capex_annual = (
        capex_raw.groupby(["ticker", "year"])["capex_bn"]
        .sum().reset_index().sort_values(["ticker", "year"])
    )
    guidance_2026 = query("""
        SELECT ticker, year, capex_bn, source FROM energy_data.capex_guidance
    """)
    _mkt = query("""
        SELECT ticker, company, date, market_cap_t
        FROM energy_data.mag7_market_caps ORDER BY ticker, date
    """)
    _early = _mkt[_mkt["date"] == "2023-01-03"].set_index("ticker")
    _late = _mkt[_mkt["date"] == "2026-02-14"].set_index("ticker")
    mkt_cap = _early[["company"]].copy()
    mkt_cap["mkt_cap_2023_t"] = _early["market_cap_t"]
    mkt_cap["mkt_cap_2026_t"] = _late["market_cap_t"]
    mkt_cap["gain_t"] = mkt_cap["mkt_cap_2026_t"] - mkt_cap["mkt_cap_2023_t"]
    mkt_cap = mkt_cap.reset_index()

    cloud_rev = query("""
        SELECT ticker, segment, quarter, revenue_bn, yoy_growth_pct
        FROM energy_data.cloud_revenue ORDER BY quarter, ticker
    """)
    _pnfi = query("""
        SELECT value FROM energy_data.fred_series
        WHERE series_id = 'PNFI' ORDER BY date DESC LIMIT 1
    """)
    pnfi_bn = float(_pnfi["value"].iloc[0])
    ocf_data = query("""
        SELECT ticker, ocf_bn FROM energy_data.hyperscaler_ocf
    """)
    _cite_raw = query("""
        SELECT key, value FROM energy_data.source_citations
    """)
    citations = dict(zip(_cite_raw["key"], _cite_raw["value"]))
    return (
        capex_annual,
        capex_raw,
        citations,
        cloud_rev,
        guidance_2026,
        mkt_cap,
        ocf_data,
        pnfi_bn,
    )


@app.cell
def _(
    capex_annual,
    citations,
    cloud_rev,
    guidance_2026,
    mkt_cap,
    ocf_data,
    pnfi_bn,
):
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
        "guidance_2026": guidance_2026[guidance_2026["ticker"].isin(_tickers_6)]["capex_bn"].sum(),
        "mkt_gain_t": mkt_cap["gain_t"].sum(),
        "capex_4co_2019_bn": 70.9,
        "pnfi_bn": pnfi_bn,
        "cloud_rev_q4": _cloud_q4["revenue_bn"].sum(),
        "cloud_rev_q4_annual": _cloud_q4["revenue_bn"].sum() * 4,
        "cloud_rev_2024": _cloud_2024.groupby("ticker")["revenue_bn"].sum().sum(),
        "cloud_rev_2025": _cloud_2025.groupby("ticker")["revenue_bn"].sum().sum(),
    }
    stats["ratio_vs_2025"] = stats["mkt_gain_t"] / (stats["capex_2025"] / 1000)
    stats["pnfi_share_pct"] = stats["capex_2025"] / stats["pnfi_bn"] * 100

    for _t in ["AMZN", "GOOGL", "MSFT", "META"]:
        for _y in [2024, 2025]:
            stats[f"{_t.lower()}_{_y}"] = _annual[
                (_annual["ticker"] == _t) & (_annual["year"] == _y)
            ]["capex_bn"].sum()
    for _, _row in guidance_2026[guidance_2026["ticker"].isin(["AMZN", "GOOGL", "MSFT", "META"])].iterrows():
        stats[f"{_row['ticker'].lower()}_2026g"] = _row["capex_bn"]
    stats["meta_2022"] = _annual[(_annual["ticker"] == "META") & (_annual["year"] == 2022)]["capex_bn"].sum()
    stats["meta_2023"] = _annual[(_annual["ticker"] == "META") & (_annual["year"] == 2023)]["capex_bn"].sum()

    _tickers_ocf = ocf_data[ocf_data["ticker"].isin(_tickers_6)]
    stats["ocf_ttm"] = _tickers_ocf["ocf_bn"].sum()
    stats["capex_ocf_2026_pct"] = stats["guidance_2026"] / stats["ocf_ttm"] * 100
    _amzn_ocf = float(ocf_data[ocf_data["ticker"] == "AMZN"]["ocf_bn"].iloc[0])
    stats["amzn_ocf_pct"] = stats["amzn_2025"] / _amzn_ocf * 100

    _yoy = _cloud_q4["yoy_growth_pct"].dropna()
    stats["cloud_yoy_min"] = _yoy.min()
    stats["cloud_yoy_max"] = _yoy.max()

    _tickers_3 = ["AMZN", "GOOGL", "MSFT"]
    _annual_3 = capex_annual[capex_annual["ticker"].isin(_tickers_3)]
    stats["capex_3co_2024"] = _annual_3[_annual_3["year"] == 2024]["capex_bn"].sum()
    stats["capex_3co_2025"] = _annual_3[_annual_3["year"] == 2025]["capex_bn"].sum()
    stats["capex_3co_2026g"] = stats["amzn_2026g"] + stats["googl_2026g"] + stats["msft_2026g"]

    stats["meta_2026g_low"] = int(citations["meta_2026g_low"])
    stats["meta_2026g_high"] = int(citations["meta_2026g_high"])
    stats["meta_2023_guidance_low"] = int(citations["meta_2023_guidance_low"])
    stats["meta_2023_guidance_high"] = int(citations["meta_2023_guidance_high"])
    stats["meta_guidance_cut_pct"] = round((stats["meta_2023_guidance_high"] - stats["meta_2023"]) / stats["meta_2023_guidance_high"] * 100)
    stats["msft_fy25_initial_g"] = int(citations["msft_fy25_initial_g"])
    stats["msft_fy25_revised_g"] = int(citations["msft_fy25_revised_g"])
    stats["msft_guidance_raise_pct"] = round((stats["msft_fy25_revised_g"] - stats["msft_fy25_initial_g"]) / stats["msft_fy25_initial_g"] * 100)
    stats["guidance_max_revision_pct"] = max(stats["meta_guidance_cut_pct"], stats["msft_guidance_raise_pct"])
    stats["guidance_2026_point"] = stats["guidance_2026"]
    _guidance_band = stats["guidance_max_revision_pct"] / 100
    stats["guidance_2026_low"] = round(stats["guidance_2026_point"] * (1 - _guidance_band))
    stats["guidance_2026_high"] = round(stats["guidance_2026_point"] * (1 + _guidance_band))
    stats["guidance_band_pct"] = stats["guidance_max_revision_pct"]
    stats["meta_headcount_2022"] = int(citations["meta_headcount_2022"])
    stats["meta_headcount_2023"] = int(citations["meta_headcount_2023"])
    stats["meta_headcount_cut_pct"] = round((stats["meta_headcount_2022"] - stats["meta_headcount_2023"]) / stats["meta_headcount_2022"] * 100)

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
    stats["capex_rev_2026_low"] = round(stats["guidance_2026"] / stats["cloud_rev_2026_high"], 1)
    stats["capex_rev_2026_high"] = round(stats["guidance_2026"] / stats["cloud_rev_2026_low"], 1)
    stats["nvda_deepseek_loss_bn"] = int(citations["nvda_deepseek_loss_bn"])
    stats["stargate_announced_bn"] = int(citations["stargate_announced_bn"])
    stats["stargate_initial_bn"] = int(citations["stargate_initial_bn"])
    stats["meta_beignet_financing_bn"] = int(citations["meta_beignet_financing_bn"])
    stats["meta_beignet_exit_year"] = int(citations["meta_beignet_exit_year"])
    stats["beignet_bond_maturity"] = int(citations["beignet_bond_maturity"])
    stats["msft_neocloud_total_bn"] = int(citations["msft_neocloud_total_bn"])
    stats["msft_nebius_deal_bn"] = int(citations.get("msft_nebius_deal_bn", 17))
    stats["msft_nscale_deal_bn"] = int(citations.get("msft_nscale_deal_bn", 23))
    stats["msft_iren_deal_bn"] = int(citations.get("msft_iren_deal_bn", 10))
    stats["meta_beignet_lease_years"] = int(citations.get("meta_beignet_lease_years", 4))
    stats["openai_coreweave_commitment_bn"] = float(citations["openai_coreweave_commitment_bn"])
    stats["coreweave_interest_rate_pct"] = int(citations["coreweave_interest_rate_pct"])
    stats["chatgpt_monthly_users_m"] = int(citations["chatgpt_monthly_users_m"])
    stats["openai_paid_subscriber_pct"] = int(citations["openai_paid_subscriber_pct"])
    stats["google_search_ad_rev_qtr_bn"] = int(citations["google_search_ad_rev_qtr_bn"])
    stats["mckinsey_no_impact_pct"] = int(citations["mckinsey_no_impact_pct"])
    stats["musk_ai_companion_monthly"] = int(citations["musk_ai_companion_monthly"])
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
    mkt_cap,
    plt,
    save_fig,
    stats,
):
    _sorted = mkt_cap.sort_values("gain_t", ascending=False)
    _total = _sorted["gain_t"].sum()
    _capex_t = stats["capex_2025"] / 1000
    fig_mktcap, _ax = plt.subplots(figsize=FIGSIZE["wide"])
    _left = 0.0
    for _, _row in _sorted.iterrows():
        _ticker = _row["ticker"]
        _gain = _row["gain_t"]
        _clr = company_color(_ticker)
        _ax.barh(0, _gain, left=_left, height=0.55, color=_clr, edgecolor="white", linewidth=1.5, label=company_label(_ticker))
        if _gain >= 0.8:
            _ax.text(_left + _gain / 2, 0, f"{company_label(_ticker)}\n+${_gain:.1f}T", ha="center", va="center", fontsize=FONTS["annotation"] - 1, fontweight="bold", color="white")
        _left += _gain
    _ax.axvline(_capex_t, color=COLORS["accent"], linestyle="-", linewidth=2.5, alpha=0.9)
    _ax.text(_capex_t, 0.38, f"  2025 capex: ${stats['capex_2025']:.0f}B", fontsize=FONTS["annotation"], fontweight="bold", color=COLORS["accent"], va="bottom")
    _ax.text(_total + 0.12, 0, f"${_total:.1f}T", ha="left", va="center", fontsize=FONTS["value_label"], fontweight="bold", color=COLORS["text_dark"])
    _ax.set_yticks([])
    _ax.set_xlabel("Market cap gain, Jan 2023 → Feb 2026 ($T)", fontsize=FONTS["axis_label"])
    _ax.tick_params(axis="x", labelsize=FONTS["tick_label"])
    chart_title(fig_mktcap, f"~{stats['ratio_vs_2025']:.0f}x gap between market cap gains and annual capex")
    plt.tight_layout()
    save_fig(fig_mktcap, cfg.img_dir / "dd001_valuation_disconnect.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo, stats):
    _chart = mo.image(src=(cfg.img_dir / "dd001_valuation_disconnect.png").read_bytes(), width=850)
    mo.md(
        "# Markets added ~\\${mkt:.1f}T in value against ~\\${capex:.0f}B in annual spending".format(mkt=stats['mkt_gain_t'], capex=stats['capex_2025'])
        + f"""

    {_chart}

    *Takeaway: market value has outrun annual infrastructure spend by roughly {stats['ratio_vs_2025']:.0f}x, so today's pricing assumes several years of strong monetization. Source: Yahoo Finance; SEC filings via yfinance.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    > **The Tesla/xAI question.** Tesla's \$1.18T market cap gain (Jan 2023–Feb 2026) is overwhelmingly priced on AI, not cars: forward P/E is ~160x vs. the auto sector median of 6.2x. Tesla spent ~\$5B on AI infrastructure in 2024 (44% of total capex) and guides \$20B+ for 2026. Separately, Musk's xAI built the 200,000-GPU "Colossus" supercomputer for ~\$7B — AI infrastructure capital flowing through a web of related entities with overlapping leadership and ambiguous corporate boundaries.
    >
    > Tesla's capex is excluded from the totals above because its core spend remains automotive, but the AI narrative drives its valuation — making it arguably the most extreme example of the disconnect this analysis tracks.
    >
    > *Sources: Tesla 10-K (2024), CNBC, CompaniesMarketCap.*
    """)
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
    plt,
    save_fig,
):
    _hist_capex_4co = {
        2015: 22.9, 2016: 30.8, 2017: 40.0, 2018: 64.0,
        2019: 70.9, 2020: 93.5, 2021: 125.5,
    }
    _tickers_4 = ["AMZN", "GOOGL", "MSFT", "META"]
    _ann4 = capex_annual[capex_annual["ticker"].isin(_tickers_4)]
    for _y in [2022, 2023, 2024, 2025]:
        _hist_capex_4co[_y] = float(_ann4[_ann4["year"] == _y]["capex_bn"].sum())
    _years = sorted(_hist_capex_4co.keys())
    _values = [_hist_capex_4co[y] for y in _years]
    _split = _years.index(2022)
    fig_capex_ratio, _ax = plt.subplots(figsize=FIGSIZE["wide"])
    _ax.plot(_years[:_split + 1], _values[:_split + 1], color=CONTEXT, linewidth=2.0, marker="o", markersize=4, zorder=3)
    _ax.plot(_years[_split:], _values[_split:], color=COLORS["accent"], linewidth=2.5, marker="o", markersize=5, zorder=4)
    _v19 = _hist_capex_4co[2019]
    _ax.axhline(_v19, color=CONTEXT, linewidth=1, linestyle="--", alpha=0.45)
    _ax.text(2015.2, _v19 + 5, f"2019 baseline: ${_v19:.0f}B", fontsize=FONTS["annotation"] - 1, color=CONTEXT)
    _v25 = _hist_capex_4co[2025]
    _mult = _v25 / _v19
    _ax.text(2025.15, _v25, f"  ${_v25:.0f}B\n  ({_mult:.1f}× vs 2019)", fontsize=FONTS["annotation"], color=COLORS["accent"], fontweight="bold", va="center")
    _v22 = _hist_capex_4co[2022]
    _ax.axvline(2022, color=COLORS["accent"], linewidth=1, linestyle=":", alpha=0.5, zorder=2)
    _ax.text(2022.1, _v22 * 1.55, "AI buildout era", fontsize=FONTS["annotation"] - 1, color=COLORS["accent"], alpha=0.85, ha="left")
    _ax.set_xlabel("Year", fontsize=FONTS["axis_label"])
    _ax.set_ylabel("Annual capex, 4 hyperscalers ($B)", fontsize=FONTS["axis_label"])
    _ax.tick_params(labelsize=FONTS["tick_label"])
    _ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:.0f}B"))
    _ax.set_xlim(2014.5, 2026.5)
    chart_title(fig_capex_ratio, f"Hyperscaler capex grew {_mult:.1f}× from 2019 to 2025 — the AI buildout has no cloud-era precedent")
    plt.tight_layout()
    save_fig(fig_capex_ratio, cfg.img_dir / "dd001_capex_ratio_history.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo, stats):
    _chart_ratio = mo.image(src=(cfg.img_dir / "dd001_capex_ratio_history.png").read_bytes(), width=850)
    _capex_4co_2025 = stats["amzn_2025"] + stats["googl_2025"] + stats["msft_2025"] + stats["meta_2025"]
    _mult_4co = _capex_4co_2025 / stats["capex_4co_2019_bn"]
    mo.md(
        f"# Hyperscaler capex grew {_mult_4co:.1f}× from 2019 to 2025 — the AI buildout has no cloud-era precedent\n\n"
        f"{_chart_ratio}\n\n"
        f"*Takeaway: the AI era (2022-2025) is a steeper spend regime than the prior cloud buildout, reaching ~\\${_capex_4co_2025:.0f}B in 2025. Source: SEC filings via yfinance.*"
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
    _tickers_unsorted = ["MSFT", "AMZN", "GOOGL", "META", "ORCL", "NVDA"]
    _years = [2022, 2023, 2024, 2025]
    _data = capex_annual[(capex_annual["ticker"].isin(_tickers_unsorted)) & (capex_annual["year"].isin(_years))].copy()
    _guide = guidance_2026[guidance_2026["ticker"].isin(_tickers_unsorted)].copy()
    _combined = pd.concat([_data[["ticker", "year", "capex_bn"]], _guide[["ticker", "year", "capex_bn"]]], ignore_index=True)
    # Sort companies by cumulative 2022–2026 total, descending
    _totals = _combined.groupby("ticker")["capex_bn"].sum()
    _tickers = [t for t in _totals.sort_values(ascending=False).index if t in _tickers_unsorted]
    fig_capex, _ax = plt.subplots(figsize=FIGSIZE["wide"])
    _all_years = sorted(_combined["year"].unique())
    _x = np.arange(len(_tickers))
    # Use COLORS["muted"] for 2022 — COLORS["grid"] is reserved for gridlines, not data bars
    _year_colors = {2022: COLORS["muted"], 2023: CONTEXT, 2024: COLORS["reference"], 2025: COLORS["text_light"], 2026: COLORS["accent"]}
    _bottoms = np.zeros(len(_tickers))
    for _yr in _all_years:
        _vals = []
        for _ticker in _tickers:
            _match = _combined[(_combined["ticker"] == _ticker) & (_combined["year"] == _yr)]
            _vals.append(_match["capex_bn"].sum() if len(_match) else 0)
        _vals = np.array(_vals)
        _bars = _ax.bar(_x, _vals, bottom=_bottoms, width=0.55, color=_year_colors[_yr], edgecolor="white", linewidth=0.5, label=str(_yr) + ("*" if _yr == 2026 else ""))
        if _yr == 2026:
            for _b in _bars:
                _b.set_hatch("//")
                _b.set_alpha(0.85)
        _bottoms += _vals
    _ax.set_xticks(_x)
    _ax.set_xticklabels([company_label(t) for t in _tickers], fontsize=FONTS["tick_label"])
    _ax.set_ylabel("Cumulative capex, 2022–2026 ($B)", fontsize=FONTS["axis_label"])
    _ax.tick_params(axis="y", labelsize=FONTS["tick_label"])
    # Total labels use text_dark — accent is reserved for the 2026 story bars, not totals
    for _j, _ticker in enumerate(_tickers):
        _ax.text(_j, _bottoms[_j] + 8, f"${_bottoms[_j]:.0f}B", ha="center", fontsize=FONTS["annotation"], fontweight="bold", color=COLORS["text_dark"])
    legend_below(_ax, ncol=len(_all_years))
    chart_title(fig_capex, "Hyperscaler capex tripled in three years — and 2026 guidance doubles again")
    plt.tight_layout()
    save_fig(fig_capex, cfg.img_dir / "dd001_capex_acceleration.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo, stats):
    _chart = mo.image(src=(cfg.img_dir / "dd001_capex_acceleration.png").read_bytes(), width=850)
    mo.md(f"""
    # Hyperscaler capex tripled in three years — and 2026 guidance doubles again

    {_chart}

    *Takeaway: spend rose from ~\\${stats['capex_2023']:.0f}B (2023) to ~\\${stats['capex_2025']:.0f}B (2025), and 2026 guidance still points higher at ~\\${stats['guidance_2026_point']:.0f}B (range \\${stats['guidance_2026_low']:.0f}–\\${stats['guidance_2026_high']:.0f}B). Source: SEC filings and Q4 2025 guidance calls.*
    """)
    return


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    > **What these numbers miss: infrastructure commitments not captured in reported capex.**
    > The capex figures above capture capital expenditures as reported in SEC filings.
    > They exclude a parallel — and growing — channel: leased and SPV-financed
    > infrastructure that shows up as operating expenses, not capital investments.
    >
    > In September–November 2025 alone, Microsoft signed over \\${stats['msft_neocloud_total_bn']}B in 3-5 year
    > neocloud leases (Nebius \\${stats['msft_nebius_deal_bn']}B, Nscale \\${stats['msft_nscale_deal_bn']}B, Iren \\${stats['msft_iren_deal_bn']}B, Lambda multi-billion) —
    > none of which appears in its capex line (NYT, Dec 2025). Meta structured
    > ~\\${stats['meta_beignet_financing_bn']}B in Louisiana data center financing through a special purpose vehicle
    > (Beignet Investor LLC), with Blue Owl Capital providing 80% of the funding
    > and Pimco selling the underlying bonds. The deal is classified as an operating
    > lease — so it flows through operating expenses rather than capex, and therefore
    > does not appear in the capital expenditure figures tracked here. (Note: under
    > FASB ASC 842, effective 2019, operating leases over 12 months do appear on the
    > balance sheet as right-of-use assets and lease liabilities — the critical
    > accounting distinction is between *capex* and *opex*, not on- vs. off-balance-sheet.)
    >
    > This means the true infrastructure commitment is **materially higher** than
    > the ~\\${stats['capex_2025']:.0f}B in reported capex. The risk distribution of these
    > arrangements is traced in [03_risk_and_durability.py](./03_risk_and_durability.py).
    >
    > *Sources: NYT, "How Tech's Biggest Companies Are Offloading the Risks of the
    > A.I. Boom," Dec 15, 2025 (Weise & Tan).*
    """)
    return


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    ---

    ## Decision Lens: Revenue Conversion vs Capital Commitments

    Amazon, Alphabet, and Microsoft are the three companies with comparable cloud
    revenue segments (AWS, Azure, Google Cloud). This section informs one decision:
    should long-lived AI infrastructure commitments accelerate, hold, or slow based
    on observed revenue conversion?

    | Metric | 2024 | 2025 | 2026 (guided) |
    | :--- | :--- | :--- | :--- |
    | Capex (AMZN + GOOGL + MSFT) | ~\\${stats['capex_3co_2024']:.0f}B | ~\\${stats['capex_3co_2025']:.0f}B | ~\\${stats['capex_3co_2026g']:.0f}B\\* |
    | Cloud revenue (same 3) | ~\\${stats['cloud_rev_2024']:.0f}B | ~\\${stats['cloud_rev_2025']:.0f}B | est. ~\\${stats['cloud_rev_2026_low']}–{stats['cloud_rev_2026_high']}B\\*\\* |
    | Capex / Revenue ratio | ~{stats['capex_3co_2024'] / stats['cloud_rev_2024']:.1f}x | ~{stats['capex_3co_2025'] / stats['cloud_rev_2025']:.1f}x | ~{stats['capex_3co_2026g'] / stats['cloud_rev_2026_high']:.1f}–{stats['capex_3co_2026g'] / stats['cloud_rev_2026_low']:.1f}x |

    \\* Management guidance. \\*\\* Analyst consensus estimates.
    *(Extends the revenue-gap framing from Sequoia Capital "AI's \\${stats['sequoia_rev_target_bn']}B Question," Sep 2024, and Goldman Sachs "Gen AI: Too Much Spend, Too Little Return?," Sep 2024, using auditable EDGAR data rather than analyst extrapolations.)*

    **Decision implication:** when capex remains at or above revenue while monetization
    quality is mixed, additional long-lived AI-dedicated buildout should be staged
    behind explicit demand and utilization gates rather than treated as baseline growth.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ### Decision Risk: One Capex Line, Multiple Demand Theses

    The revenue gap is compounded by a structural issue: the companies building this
    infrastructure cannot articulate a single demand thesis that justifies the spend.
    A September 2025 industry survey (NYT, Metz & Weise) identified at least six
    overlapping visions being pursued simultaneously — ranging from near-term proven
    revenue to long-horizon bets with no commercial model yet:
    """)
    return


@app.cell(hide_code=True)
def _(
    COLORS,
    CONTEXT,
    FLOW_FONT_SIZE,
    cfg,
    flow_diagram,
    mpatches,
    save_fig,
    stats,
):
    fig_rt = flow_diagram(
        nodes={
            # root at same y as medium-term → straight horizontal arrow r→m
            "r":  ("Six AI Revenue Theses\n(2025 buildout)", 1.0, 1.5, COLORS["accent"], "#ffffff"),
            "n":  ("Near-term:\nproven revenue", 4.5, 4.9, COLORS["positive"], "#ffffff"),
            "m":  ("Medium-term:\nspeculative", 4.5, 1.5, COLORS["neutral"], COLORS["text_dark"]),
            "l":  ("Long-term:\nno revenue model yet", 4.5, -1.9, CONTEXT, COLORS["text_dark"]),
            # leaf nodes at 1.8-unit spacing — required for 2-line boxes at font_size=18
            "n1": (f"Better search\n${stats['google_search_ad_rev_qtr_bn']}B/qtr Google ad engine", 9.0, 5.8, COLORS["background"], COLORS["text_dark"]),
            "n2": ("Productivity tools\nEnterprise software · code generation", 9.0, 4.0, COLORS["background"], COLORS["text_dark"]),
            "m1": ("Everything assistant\nAI in glasses · speakers · shopping", 9.0, 2.4, COLORS["background"], COLORS["text_dark"]),
            "m2": (f"AI companions\n${stats['musk_ai_companion_monthly']}/month subscription niche", 9.0, 0.6, COLORS["background"], COLORS["text_dark"]),
            "l1": ("Scientific breakthroughs\nDrug discovery — real but narrow", 9.0, -1.2, COLORS["background"], COLORS["text_dark"]),
            "l2": ("AGI / superintelligence\nNo commercial path articulated", 9.0, -3.0, COLORS["background"], COLORS["text_dark"]),
        },
        edges=[
            {"src": "r", "dst": "n", "exit": "top",    "entry": "left"},
            {"src": "r", "dst": "m"},
            {"src": "r", "dst": "l", "exit": "bottom", "entry": "left"},
            {"src": "n", "dst": "n1"},
            {"src": "n", "dst": "n2"},
            {"src": "m", "dst": "m1"},
            {"src": "m", "dst": "m2"},
            {"src": "l", "dst": "l1"},
            {"src": "l", "dst": "l2"},
        ],
        figsize=(12, 8),
        xlim=(-0.5, 12.0),
        ylim=(-3.8, 6.7),
        font_size=FLOW_FONT_SIZE,
        legend_handles=[
            mpatches.Patch(facecolor=COLORS["positive"], label="Near-term: proven revenue"),
            mpatches.Patch(facecolor=COLORS["neutral"], label="Medium-term: speculative"),
            mpatches.Patch(facecolor=CONTEXT, label="Long-term: no revenue model"),
        ],
    )
    save_fig(fig_rt, cfg.img_dir / "dd001_revenue_theses.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo):
    _chart = mo.image(src=(cfg.img_dir / "dd001_revenue_theses.png").read_bytes(), width=850)
    mo.md(f"{_chart}")
    return


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    **Decision implication:** each vision implies a different revenue trajectory, infrastructure requirement,
    and risk profile. The capex figures aggregate across all six. Current revenue
    reflects mainly the near-term theses — better search and productivity tools.

    Key signal that demand is real but fragile: Google Cloud's contracted backlog
    surged {stats['gcp_backlog_growth_pct']}% to \\${stats['gcp_backlog_bn']}B, and cloud is growing
    {stats['cloud_yoy_min']:.0f}–{stats['cloud_yoy_max']:.0f}% YoY. But a meaningful portion reflects AI
    services sold to VC-funded startups (\\${stats['vc_ai_2024_bn']}B globally in 2024, PitchBook).
    Those startups are major cloud customers — if VC funding contracts, cloud revenue
    contracts with it. McKinsey found ~{stats['mckinsey_no_impact_pct']}% of businesses that tried gen AI
    reported no significant bottom-line impact. If the medium- and long-term theses
    don't materialize as revenue-generating products, the infrastructure built for them
    becomes capacity in search of demand.

    **Failure movie (2028-2030):** near-term revenue growth softens, long-horizon use
    cases fail to scale, and operators are left with fixed infrastructure costs sized
    for demand that never arrives.

    *Sources: NYT, "What Exactly Are A.I. Companies Trying to Build?" Sep 16, 2025
    (Metz & Weise); McKinsey Global Survey on AI (2025); OpenAI public statements.*
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
    plt,
    save_fig,
    stats,
):
    _tickers_3 = ["AMZN", "GOOGL", "MSFT"]
    _cloud_qtr = (
        cloud_rev[cloud_rev["ticker"].isin(_tickers_3)]
        .groupby("quarter")["revenue_bn"].sum().reset_index().sort_values("quarter")
    )
    _capex_3 = capex_raw[capex_raw["ticker"].isin(_tickers_3)].copy()
    _capex_3["quarter"] = _capex_3["date"].dt.year.astype(str) + "-Q" + _capex_3["date"].dt.quarter.astype(str)
    _capex_qtr = _capex_3.groupby("quarter")["capex_bn"].sum().reset_index().sort_values("quarter")
    _common = sorted(set(_cloud_qtr["quarter"]) & set(_capex_qtr["quarter"]))
    _rev = _cloud_qtr[_cloud_qtr["quarter"].isin(_common)].sort_values("quarter")
    _cap = _capex_qtr[_capex_qtr["quarter"].isin(_common)].sort_values("quarter")
    _rev_vals = _rev["revenue_bn"].values
    _cap_vals = _cap["capex_bn"].values
    fig_rev, _ax = plt.subplots(figsize=FIGSIZE["wide"])
    _x = np.arange(len(_common))
    _ax.bar(_x, _rev_vals, width=0.6, color=CONTEXT, alpha=0.7, label="Cloud revenue (AWS + MSFT Cloud + GCP)")
    _ax.plot(_x, _cap_vals, color=COLORS["accent"], linewidth=2.5, marker="o", markersize=5, label="Capital expenditure (same 3 co.)")
    _gaps = _rev_vals - _cap_vals
    for _i in range(1, len(_gaps)):
        if _gaps[_i - 1] > 0 and _gaps[_i] <= 0:
            _ax.annotate(
                f"Capex overtakes revenue\n\\${_cap_vals[_i]:.0f}B vs \\${_rev_vals[_i]:.0f}B",
                xy=(_i, _cap_vals[_i]), xytext=(_i - 3, _cap_vals[_i] + 15),
                fontsize=FONTS["annotation"], color=COLORS["accent"], fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=COLORS["accent"], connectionstyle="arc3,rad=-0.2", linewidth=1.5),
            )
            break
    _last = len(_common) - 1
    _ax.text(_last, _rev_vals[_last] - 4, f"${_rev_vals[_last]:.0f}B", ha="center", va="top", fontsize=FONTS["annotation"], color=COLORS["text_light"])
    _ax.text(_last + 0.15, _cap_vals[_last] + 1.5, f"${_cap_vals[_last]:.0f}B", ha="left", va="bottom", fontsize=FONTS["annotation"], color=COLORS["accent"], fontweight="bold")
    _ratio = _cap_vals / _rev_vals
    _ax.text(0, _rev_vals[0] * 0.3, f"Investment intensity:\n{_ratio[0]:.1f}× (capex/cloud rev)", ha="left", va="bottom", fontsize=FONTS["annotation"] - 1, color=COLORS["text_light"])
    _ax.text(_last, _cap_vals[_last] * 1.08, f"{_ratio[-1]:.1f}×", ha="center", va="bottom", fontsize=FONTS["annotation"], color=COLORS["accent"], fontweight="bold")
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
    _chart = mo.image(src=(cfg.img_dir / "dd001_revenue_gap.png").read_bytes(), width=850)
    mo.md(f"""
    # Total capex overtook cloud revenue in late 2025

    {_chart}

    *Takeaway: by Q4 2025, capex for Amazon, Alphabet, and Microsoft exceeded combined cloud revenue; full-year 2025 was ~\\${stats['capex_3co_2025']:.0f}B vs ~\\${stats['cloud_rev_2025']:.0f}B. Source: SEC 10-Q filings.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    The chart above frames a decision test. If major efficiency gains reduce future
    infrastructure demand, capital intensity should begin to fall. If it does not,
    current spending behavior should be treated as competition-driven commitment rather
    than revenue-led expansion.

    The DeepSeek moment provides that test: when a major efficiency signal arrived in
    January 2025, did spending slow?
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
        _pre = _sub[_sub["date"] <= _deepseek_date]
        _post = _sub[_sub["date"] >= _deepseek_date]
        _clr = company_color(_ticker)
        _ax.plot(_pre["date"], _pre["capex_bn"], marker="o", markersize=3, color=CONTEXT, linewidth=1.2, alpha=0.5)
        _ax.plot(_post["date"], _post["capex_bn"], marker="o", markersize=6, color=_clr, linewidth=3, alpha=1.0, label=company_label(_ticker))
    _ax.set_ylabel("Quarterly capex ($B)", fontsize=FONTS["axis_label"])
    _ax.tick_params(axis="both", labelsize=FONTS["tick_label"])
    _ax.grid(True, axis="y", linestyle=":", alpha=0.4)
    _ymax = capex_raw[capex_raw["ticker"].isin(_tickers)]["capex_bn"].max()
    _ax.axvline(_deepseek_date, color=COLORS["accent"], linestyle="-", linewidth=2, alpha=0.7)
    _ax.text(_deepseek_date, _ymax * 0.98, "  DeepSeek R1", fontsize=FONTS["annotation"], color=COLORS["accent"], fontweight="bold", va="top")
    _ax.text(_deepseek_date + pd.Timedelta(days=200), _ymax * 0.18, "All four accelerated\nafter DeepSeek", fontsize=FONTS["annotation"], color=COLORS["accent"], fontweight="bold", ha="left", va="center", bbox={"boxstyle": "round,pad=0.4", "fc": "white", "ec": COLORS["accent"], "alpha": 0.8})
    legend_below(_ax, ncol=4)
    chart_title(fig_quarterly, "DeepSeek R1 changed nothing — all four AI builders accelerated capex")
    plt.tight_layout()
    save_fig(fig_quarterly, cfg.img_dir / "dd001_quarterly_capex.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo, stats):
    _chart = mo.image(src=(cfg.img_dir / "dd001_quarterly_capex.png").read_bytes(), width=850)
    mo.md(f"""
    # DeepSeek R1 changed nothing — all four AI builders accelerated capex

    {_chart}

    *Takeaway: even after DeepSeek R1 (Jan 2025), all four major builders kept accelerating through Q4 2025, despite a ~\\${stats['nvda_deepseek_loss_bn']}B one-day Nvidia repricing. Source: yfinance (SEC filings).*
    """)
    return


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    ---

    ## Does AI Efficiency Reduce Infrastructure Demand?

    DeepSeek R1 (January 2025) created the sharpest test of this question to date. The reported ~$6M figure for DeepSeek-V3's final training run (arXiv:2412.19437, December 2024) is self-reported and partial — one run, not full development costs — but the directional claim is significant: frontier-capable models may be achievable at costs far below the infrastructure buildout implies.

    Through four quarters of data, the answer from actual spending is: no slowdown. All major builders accelerated through 2025:

    | Company | 2024 actual | 2025 actual | 2026 guidance |
    | :--- | :--- | :--- | :--- |
    | Amazon | ~\\${stats['amzn_2024']:.0f}B | ~\\${stats['amzn_2025']:.0f}B | \\${stats['amzn_2026g']:.0f}B |
    | Alphabet | ~\\${stats['googl_2024']:.0f}B | ~\\${stats['googl_2025']:.0f}B | \\${stats['googl_2026g']:.0f}B |
    | Microsoft | ~\\${stats['msft_2024']:.0f}B | ~\\${stats['msft_2025']:.0f}B | ~\\${stats['msft_2026g']:.0f}B |
    | Meta | ~\\${stats['meta_2024']:.0f}B | ~\\${stats['meta_2025']:.0f}B | \\${stats['meta_2026g_low']}-{stats['meta_2026g_high']}B |

    Plain-language takeaway: compute got much cheaper, but total infrastructure spending
    still increased. One reason that can happen is that lower unit prices unlock enough
    extra usage that total demand rises faster than price falls. Economists call this
    the **Jevons paradox**.

    The mechanism is plausible — OpenAI's
    GPT-4 API pricing fell ~97% from ~\\$60/1M tokens (March 2023) to ~\\$2.50/1M tokens
    (May 2024). But Jevons only dominates when price elasticity of demand exceeds 1
    in absolute value. That elasticity is not established for AI inference.

    Three testable conditions must hold simultaneously:
    1. **Cost continues falling** — verified; ~10× per 18 months (company pricing pages, 2023–2025)
    2. **Use cases expand faster than cost falls** — plausible but unverified at scale
    3. **Net-new applications unlock** — cheaper inference enables new categories, not just cheaper existing ones

    The current spending data is consistent with both "Jevons wins" and "overinvestment" —
    it cannot distinguish between them. Management guidance suggests conviction in #2 and #3.
    The revenue data through Q4 2025 does not yet confirm it.

    **Caveat on guidance reliability:** AI capex guidance has historically been revised ±{stats['guidance_max_revision_pct']}% within a single year. Meta cut 2023 guidance {stats['meta_guidance_cut_pct']}% from its original \\${stats['meta_2023_guidance_low']}-{stats['meta_2023_guidance_high']}B range to \\${stats['meta_2023']:.0f}B actual; Microsoft raised FY2025 guidance {stats['msft_guidance_raise_pct']}% in one quarter. The \\${stats['guidance_2026_point']:.0f}B total should be treated as directionally correct but uncertain at the company level. The combined 2026 guidance would consume ~{stats['capex_ocf_2026_pct']:.0f}% of these companies' trailing operating cash flow (~\\${stats['ocf_ttm']:.0f}B TTM), far exceeding the 10-year average of ~{stats['hist_capex_ocf_avg_pct']}% (Bernstein Research, 2024). Amazon individually is at ~{stats['amzn_ocf_pct']:.0f}% (2025 actual capex vs. TTM OCF).
    """)
    return


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    ## Decision Rules for 2026 Allocation

    Current observed anchor: 2025 capex-to-cloud-revenue ratio for Amazon+Alphabet+Microsoft
    is **{stats['capex_3co_2025'] / stats['cloud_rev_2025']:.2f}x**.

    1. **Scale long-lived buildout** if revenue conversion tightens (ratio trends toward <1.0x)
       and monetization broadens beyond subsidy-like demand.
    2. **Hold / sequence** if ratio remains around parity and demand quality is mixed.
    3. **Defer AI-dedicated long-lived assets** if the ratio stays materially above parity
       while measured bottom-line impact remains weak.

    **Failure movie (2028-2030):** spending keeps rising, enterprise monetization lags,
    and the system is forced into late write-downs, tariff renegotiations, and stranded
    utility upgrades already placed into long-duration recovery schedules.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ---

    Decision handoff: the spend signal is clear, but buildout speed and lock-in risk
    depend on conversion physics, not earnings-call intent.

    **Next:** [02_conversion_reality.py](./02_conversion_reality.py) — Construction timelines, interconnection queues, and the gap between announcement and operation.
    """)
    return


if __name__ == "__main__":
    app.run()
