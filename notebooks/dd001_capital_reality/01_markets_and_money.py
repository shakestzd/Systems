import marimo

__generated_with = "0.19.11"
app = marimo.App(
    width="compact",
    app_title="DD-001: Markets and Money",
    css_file="../../src/notebook_theme/custom.css",
    html_head_file="../../src/notebook_theme/head.html",
)


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    # What is \\${stats['capex_2025']:.0f}B in AI infrastructure spending actually buying?

    *Thandolwethu Zwelakhe Dlamini*

    ---

    Seven US tech companies added about \\${stats['mkt_gain_t']:.1f} trillion in market
    value since January 2023. Six of the biggest AI infrastructure builders spent about
    \\${stats['capex_2025']:.0f}B on capital investment in 2025, up from
    \\${stats['capex_2024']:.0f}B in 2024, with about \\${stats['guidance_2026_point']:.0f}B
    announced for 2026.

    Amazon, Alphabet, and Microsoft earned about \\${stats['cloud_rev_2025']:.0f}B in cloud
    revenue in 2025 and spent about \\${stats['capex_3co_2025']:.0f}B on infrastructure.
    Alphabet has been spending more on infrastructure than Google Cloud earns since 2024.
    Amazon crossed the same line in 2025.

    Three questions follow from those numbers:

    1. **How much of the spending is backed by current revenue?**
    2. **What are they building it for?**
    3. **What happens if the demand doesn't arrive?**
    """)
    return


@app.cell
def _(add_brand_mark, add_source):
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
        CATEGORICAL,
        COLORS,
        CONTEXT,
        FIGSIZE,
        FLOW_FONT_SIZE,
        FONTS,
        add_brand_mark,
        add_rule,
        add_source,
        chart_title,
        company_color,
        company_label,
        flow_diagram,
        legend_below,
    )
    cfg = setup()
    return (
        CATEGORICAL,
        COLORS,
        CONTEXT,
        FIGSIZE,
        FLOW_FONT_SIZE,
        FONTS,
        add_brand_mark,
        add_rule,
        add_source,
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
        SELECT key, value, value_text FROM energy_data.source_citations
    """)
    # Use value_text for string entries (quotes), value for numerics
    citations = {}
    for _, _r in _cite_raw.iterrows():
        if pd.notna(_r["value"]):
            citations[_r["key"]] = _r["value"]
        elif _r["value_text"]:
            citations[_r["key"]] = _r["value_text"]
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

    # Quotes — loaded from source_citations for traceability
    stats["pichai_underinvest"] = citations["pichai_underinvest_quote"]
    stats["zuckerberg_capacity"] = citations["zuckerberg_capacity_quote"]
    stats["huang_industrial_rev"] = citations["huang_industrial_rev_quote"]
    stats["nadella_demand_supply"] = citations["nadella_demand_supply_quote"]
    stats["jassy_infra_split"] = citations["jassy_infra_split_quote"]

    # Historical baselines — telecom cycle
    stats["telecom_capex_bn"] = int(citations["telecom_cumulative_capex_bn"])
    stats["telecom_debt_tn"] = float(citations["telecom_debt_issued_tn"])
    stats["telecom_capex_rev_pct"] = int(citations["telecom_capex_rev_peak_pct"])

    # Skeptic / demand evidence
    stats["covello_trillion"] = citations["covello_trillion_quote"]
    stats["acemoglu_tfp_pct"] = float(citations["acemoglu_tfp_pct"])
    stats["gs_tfp_pct"] = float(citations["acemoglu_gs_tfp_pct"])
    stats["azure_ai_run_rate_bn"] = int(citations["msft_azure_ai_run_rate_bn"])
    stats["gcp_rpo_bn"] = float(citations["gcp_rpo_bn"])
    return (stats,)


@app.cell
def _(
    CATEGORICAL,
    COLORS,
    FIGSIZE,
    FONTS,
    add_brand_mark,
    add_source,
    cfg,
    chart_title,
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
        _ax.barh(0, _gain, left=_left, height=0.55, color=CATEGORICAL[0], edgecolor="white", linewidth=1.5, label=company_label(_ticker))
        if _gain >= 0.8:
            _ax.text(_left + _gain / 2, 0, f"{company_label(_ticker)}\n+${_gain:.1f}T", ha="center", va="center", fontsize=FONTS["annotation"] - 1, fontweight="bold", color="white")
        _left += _gain
    _ax.axvline(_capex_t, color=COLORS["accent"], linestyle="-", linewidth=2.5, alpha=0.9)
    _ax.text(_capex_t, 0.38, f"  2025 capital expenditure: ${stats['capex_2025']:.0f}B", fontsize=FONTS["annotation"], fontweight="bold", color=COLORS["accent"], va="bottom")
    _ax.text(_total + 0.12, 0, f"${_total:.1f}T", ha="left", va="center", fontsize=FONTS["value_label"], fontweight="bold", color=COLORS["text_dark"])
    _ax.set_yticks([])
    _ax.set_xlabel("Market cap gain, Jan 2023 → Feb 2026 ($T)", fontsize=FONTS["axis_label"])
    _ax.tick_params(axis="x", labelsize=FONTS["tick_label"])
    chart_title(fig_mktcap, "Market cap gain, Jan 2023 → Feb 2026 (7 companies) vs. 2025 annual capex (6 companies)")
    plt.tight_layout(rect=[0.02, 0.08, 1, 1])
    add_source(fig_mktcap, "Source: Yahoo Finance via yfinance; SEC 10-K filings")
    add_brand_mark(fig_mktcap, logo_path=str(cfg.project_root / 'src/assets/tzdlabs_mark.png'))
    save_fig(fig_mktcap, cfg.img_dir / "dd001_valuation_disconnect.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo, stats):
    _chart = mo.image(src=(cfg.img_dir / "dd001_valuation_disconnect.png").read_bytes(), width=850)
    mo.md(
        "# What is driving \\${mkt:.1f}T in market value?".format(mkt=stats['mkt_gain_t'])
        + f"""

    {_chart}

    *Market value grew roughly {stats['ratio_vs_2025']:.0f} times faster than annual infrastructure investment. Capex line covers Amazon, Alphabet, Microsoft, Meta, Oracle, and Nvidia only. Tesla appears in market cap gains but is excluded from the spending figure. Apple also excluded: at \\$9.4B in FY2024 capex (Apple 10-K, Sep 2024), Apple's infrastructure spending is roughly one-tenth of the hyperscalers; Apple Intelligence routes complex queries to OpenAI's ChatGPT (partnership announced June 2024) and Google's Gemini (confirmed January 2025), running on their infrastructure rather than Apple-built GPU clusters. Source: Yahoo Finance; SEC filings via yfinance.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.callout(mo.md(r"""
    Tesla's market cap grew by \$1.18T between January 2023 and February 2026. That gain is
    priced on AI expectations, not the car business: investors are paying about 160 times
    Tesla's expected annual earnings per share, compared to about 6 times for a typical auto
    company. Tesla spent about \$5B on AI infrastructure in 2024 (44% of its total capital
    expenditure) and has announced plans to spend \$20B+ in 2026. Separately, Musk's xAI
    built a 200,000-GPU supercomputer called Colossus for about \$7B, structured through a
    set of related entities that share leadership with Tesla but have no clear corporate
    boundary between them.

    Tesla is excluded from the totals below because its reported capital expenditure is
    mostly automotive. Its valuation is almost entirely an AI bet, making it the clearest
    case where market pricing has run far ahead of reported infrastructure spend.

    *Sources: Tesla 10-K (2024), CNBC, CompaniesMarketCap.*
    """), kind="neutral")
    return


@app.cell
def _(
    COLORS,
    CONTEXT,
    FIGSIZE,
    FONTS,
    add_brand_mark,
    add_rule,
    add_source,
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
    _ax.text(2022.1, _v22 * 1.55, "AI investment era", fontsize=FONTS["annotation"] - 1, color=COLORS["accent"], alpha=0.85, ha="left")
    _ax.set_xlabel("Year", fontsize=FONTS["axis_label"])
    _ax.set_ylabel("Capex ($B, annual)", fontsize=FONTS["axis_label"])
    _ax.tick_params(labelsize=FONTS["tick_label"])
    _ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:.0f}B"))
    _ax.set_xlim(2014.5, 2026.5)
    chart_title(fig_capex_ratio, "Annual capex, Amazon + Alphabet + Microsoft + Meta, 2015–2025 ($B)")
    plt.tight_layout(rect=[0.02, 0.08, 1, 1])
    add_rule(_ax)
    add_source(fig_capex_ratio, "Source: SEC 10-K filings via yfinance (2022–2025); company annual reports (2015–2021)")
    add_brand_mark(fig_capex_ratio, logo_path=str(cfg.project_root / 'src/assets/tzdlabs_mark.png'))
    save_fig(fig_capex_ratio, cfg.img_dir / "dd001_capex_ratio_history.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo, stats):
    _chart_ratio = mo.image(src=(cfg.img_dir / "dd001_capex_ratio_history.png").read_bytes(), width=850)
    _capex_4co_2025 = stats["amzn_2025"] + stats["googl_2025"] + stats["msft_2025"] + stats["meta_2025"]
    _mult_4co = _capex_4co_2025 / stats["capex_4co_2019_bn"]
    mo.md(
        f"# Big Tech capital expenditure is {_mult_4co:.1f}× higher than in 2019\n\n"
        f"{_chart_ratio}\n\n"
        f"*Spending accelerated sharply after 2022. The increase is steeper than the previous wave of cloud infrastructure investment between 2015 and 2021, reaching about \\${_capex_4co_2025:.0f}B in 2025. 2022–2025: SEC filings via yfinance. 2015–2021: aggregated from company annual reports (Amazon, Alphabet, Microsoft, Meta).*"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    Amazon, Alphabet, Microsoft, and Meta account for most of the total, with
    Oracle and Nvidia building at a smaller but rapidly growing scale. They are
    not building for the same reason or at the same rate, and their 2026 guidance
    figures vary considerably.
    """)
    return


@app.cell
def _(
    COLORS,
    CONTEXT,
    FIGSIZE,
    FONTS,
    add_brand_mark,
    add_rule,
    add_source,
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
    _ax.set_ylabel("Capex ($B, cumulative)", fontsize=FONTS["axis_label"])
    _ax.tick_params(axis="y", labelsize=FONTS["tick_label"])
    # Total labels use text_dark — accent is reserved for the 2026 story bars, not totals
    for _j, _ticker in enumerate(_tickers):
        _ax.text(_j, _bottoms[_j] + 8, f"${_bottoms[_j]:.0f}B", ha="center", fontsize=FONTS["annotation"], fontweight="bold", color=COLORS["text_dark"])
    legend_below(_ax, ncol=len(_all_years))
    chart_title(fig_capex, "Cumulative capex by company, 2022–2025, plus 2026 guidance ($B)")
    plt.tight_layout(rect=[0.02, 0.08, 1, 1])
    add_rule(_ax)
    add_source(fig_capex, "Source: SEC 10-K filings via yfinance")
    add_brand_mark(fig_capex, logo_path=str(cfg.project_root / 'src/assets/tzdlabs_mark.png'))
    save_fig(fig_capex, cfg.img_dir / "dd001_capex_acceleration.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo, stats):
    _chart = mo.image(src=(cfg.img_dir / "dd001_capex_acceleration.png").read_bytes(), width=850)
    mo.md(f"""
    # Amazon leads the cumulative build-out since 2022, with 2026 guidance still pointing higher

    {_chart}

    *Spend rose from about \\${stats['capex_2023']:.0f}B (2023) to about \\${stats['capex_2025']:.0f}B (2025), and 2026 guidance still points higher at about \\${stats['guidance_2026_point']:.0f}B (range \\${stats['guidance_2026_low']:.0f}–\\${stats['guidance_2026_high']:.0f}B). Source: SEC filings and Q4 2025 guidance calls.*
    """)
    return


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    Microsoft signed over \\${stats['msft_neocloud_total_bn']}B in leases with third-party
    data center operators in three months (September–November 2025): Nebius
    \\${stats['msft_nebius_deal_bn']}B, Nscale \\${stats['msft_nscale_deal_bn']}B, Iren
    \\${stats['msft_iren_deal_bn']}B, Lambda multi-billion. None of it shows up in
    Microsoft's capital expenditure (NYT, Dec 2025). Meta financed
    \\${stats['meta_beignet_financing_bn']}B of Louisiana data center construction through
    a separate legal entity called Beignet Investor LLC, with Blue Owl Capital providing
    80% of the funding and Pimco selling the bonds to investors. Also classified as an
    operating lease, also absent from the capital expenditure figures above.

    These are special purpose vehicles: legal structures that hold assets separately from
    the parent company. Because the arrangements are classified as operating expenses rather
    than capital investment, they never appear in reported capex. The actual infrastructure
    commitment is higher than the charts show. How the financial risk distributes is traced
    in [03_risk_and_durability.py](./03_risk_and_durability.py).

    *(US rules that took effect in 2019 require operating leases over 12 months to appear
    on the balance sheet as assets and liabilities. But they still flow through operating
    expenses rather than capital investment lines, which is why they do not appear in the
    figures above. Source: NYT, "How Tech's Biggest Companies Are Offloading the Risks of
    the A.I. Boom," Dec 15, 2025, Weise & Tan.)*
    """)
    return


@app.cell
def _(COLORS, CONTEXT, FONTS, add_brand_mark, add_source, cfg, chart_title, plt, save_fig, stats):
    _companies = ["Microsoft", "Meta"]
    _reported = [stats["msft_2025"], stats["meta_2025"]]
    _offbs = [stats["msft_neocloud_total_bn"], stats["meta_beignet_financing_bn"]]

    fig_obs, _ax = plt.subplots(figsize=(6.5, 4.5))
    _x = [0, 1]
    _w = 0.5

    _ax.bar(_x, _reported, width=_w, color=CONTEXT, alpha=0.85)
    _ax.bar(_x, _offbs, bottom=_reported, width=_w,
            color=COLORS["accent"], hatch="///", alpha=0.75, edgecolor="white")

    for _i, (_r, _o) in enumerate(zip(_reported, _offbs)):
        _ax.text(_i, _r / 2, f"${_r:.0f}B\nreported",
                 ha="center", va="center",
                 fontsize=FONTS["annotation"], color="white", fontweight="bold")
        _ax.text(_i, _r + _o / 2, f"+${_o:.0f}B",
                 ha="center", va="center",
                 fontsize=FONTS["annotation"], color="white", fontweight="bold")
        _ax.text(_i, _r + _o + 2, f"${_r + _o:.0f}B total",
                 ha="center", va="bottom",
                 fontsize=FONTS["annotation"], color=COLORS["text_dark"], fontweight="bold")

    _ax.set_xticks(_x)
    _ax.set_xticklabels(_companies, fontsize=FONTS["tick_label"])
    _ax.set_ylabel("Capital commitment ($B)", fontsize=FONTS["axis_label"])
    _ax.tick_params(axis="y", labelsize=FONTS["tick_label"])
    _ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:.0f}B"))
    _msft_pct = round(stats["msft_neocloud_total_bn"] / stats["msft_2025"] * 100)
    chart_title(fig_obs, "Reported 2025 capex vs. identified off-balance-sheet commitments, Microsoft and Meta ($B)")
    plt.tight_layout(rect=[0.02, 0.08, 1, 1])
    add_source(fig_obs, "Source: Microsoft/Meta/Google announcements; SEC filings")
    add_brand_mark(fig_obs, logo_path=str(cfg.project_root / 'src/assets/tzdlabs_mark.png'))
    save_fig(fig_obs, cfg.img_dir / "dd001_off_balance_sheet.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo, stats):
    _chart = mo.image(src=(cfg.img_dir / "dd001_off_balance_sheet.png").read_bytes(), width=600)
    _msft_pct = round(stats["msft_neocloud_total_bn"] / stats["msft_2025"] * 100)
    mo.md(f"""
    # Off-balance-sheet leases added {_msft_pct}% to Microsoft's reported capex — in just three months

    {_chart}

    *Microsoft: Nebius \\${stats['msft_nebius_deal_bn']}B, Nscale \\${stats['msft_nscale_deal_bn']}B,
    Iren \\${stats['msft_iren_deal_bn']}B, plus Lambda (multi-billion) — all signed Sep–Nov 2025, none
    appearing in reported capex. Meta: Beignet Investor LLC, \\${stats['meta_beignet_financing_bn']}B
    Louisiana data center, 80% financed by Blue Owl Capital. Source: NYT, Dec 15, 2025 (Weise & Tan).*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ---

    ## 1. How much of the spending is backed by current revenue?

    Amazon, Alphabet, and Microsoft are the only three that report cloud as a separate
    revenue segment (AWS, Azure, Google Cloud), so a direct comparison between spending
    and revenue is possible.
    """)
    return


@app.cell
def _(
    CONTEXT,
    FONTS,
    capex_annual,
    cfg,
    chart_title,
    cloud_rev,
    company_color,
    company_label,
    plt,
    save_fig,
):
    from src.data.cloud_capex import capex_to_revenue_ratio

    _tickers = ["AMZN", "GOOGL", "MSFT"]
    _data = capex_to_revenue_ratio(capex_annual, cloud_rev, _tickers, [2023, 2024, 2025])

    fig_ratio_slope, _ax = plt.subplots(figsize=(6.5, 3.8))

    # Reference line at 1.0 — label on left to avoid collision with end-of-line labels
    _ax.axhline(1.0, color=CONTEXT, linewidth=1.2, linestyle="--", alpha=0.6, zorder=1)
    _ax.text(2026.65, 1.03, "Spending = Revenue", va="bottom",
             fontsize=FONTS["annotation"] - 1, color=CONTEXT)

    _missing = [t for t in _tickers if _data[_data["ticker"] == t].empty]
    if _missing:
        raise ValueError(f"Per-company ratio chart: missing data for {_missing}. Check DB coverage.")

    for _t in _tickers:
        _d = _data[_data["ticker"] == _t].sort_values("year")
        _c = company_color(_t)
        _ax.plot(_d["year"], _d["ratio"], color=_c, linewidth=2.2, zorder=3,
                 marker="o", markersize=6, markerfacecolor=_c,
                 markeredgecolor="white", markeredgewidth=1.5)
        _last = _d.iloc[-1]
        _ax.text(2025.2, _last["ratio"],
                 f"{company_label(_t)}\n{_last['ratio']:.1f}×",
                 va="center", fontsize=FONTS["annotation"], color=_c, linespacing=1.4)

    _ax.set_xticks([2023, 2024, 2025])
    _ax.set_xticklabels(["2023", "2024", "2025"], fontsize=FONTS["tick_label"])
    _ax.set_xlim(2022.6, 2027.2)
    _ax.set_ylim(0.1, 1.85)
    _ax.set_yticks([])
    _ax.spines["left"].set_visible(False)
    chart_title(fig_ratio_slope, "Annual capex as a share of cloud revenue (AWS, Azure, Google Cloud), 2023–2025")
    plt.tight_layout(rect=[0.02, 0.08, 1, 1])
    add_rule(_ax)
    add_source(fig_ratio_slope, "Source: SEC 10-K filings via yfinance (2015–2025)")
    add_brand_mark(fig_ratio_slope, logo_path=str(cfg.project_root / 'src/assets/tzdlabs_mark.png'))
    save_fig(fig_ratio_slope, cfg.img_dir / "dd001_capex_ratio_slope.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo, stats):
    _chart = mo.image(src=(cfg.img_dir / "dd001_capex_ratio_slope.png").read_bytes(), width=500)
    mo.md(f"""
    # Alphabet crossed first in 2024. Amazon followed in 2025. Microsoft hasn't yet.

    {_chart}

    *Annual capital spending as a share of annual cloud revenue (AWS, Azure, Google Cloud). 2023–2025 are reported figures from mandatory annual (10-K) and quarterly (10-Q) financial filings submitted to the US Securities and Exchange Commission (SEC). Framing follows Sequoia Capital's "AI's \\${stats['sequoia_rev_target_bn']}B Question" (Sep 2024) and Goldman Sachs "Gen AI: Too Much Spend, Too Little Return?" (Sep 2024).*

    Alphabet spends about 1.6 dollars on infrastructure for every dollar Google Cloud earns, and the ratio has been above 1.0 since 2024. Amazon crossed the same line in 2025. Microsoft, whose Azure revenue base is the largest of the three, still spends about 70 cents per dollar of cloud revenue, but its spending is rising fastest.

    "{stats['pichai_underinvest']}" Sundar Pichai told analysts on Alphabet's Q4 2024
    earnings call (February 2025). David Cahn at Sequoia Capital frames the question
    differently: his "AI's \\${stats['sequoia_rev_target_bn']}B Question" (September 2024)
    estimates the industry needs \\${stats['sequoia_rev_target_bn']}B in annual AI revenue
    to justify the current infrastructure pace. Actual AI-specific revenue is a fraction
    of that.
    """)
    return


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    ## 2. What are they building it for?

    Andy Jassy (Amazon CEO) said in September 2025 that about {stats['jassy_infra_split']}
    Mark Zuckerberg put it more bluntly in January 2025: "{stats['zuckerberg_capacity']}"

    A September 2025 survey of the industry (NYT, Metz & Weise) found at least six
    distinct visions being funded from the same pool of capital, from products with
    proven revenue to long-horizon bets with no commercial model:
    """)
    return


@app.cell(hide_code=True)
def _(
    COLORS,
    CONTEXT,
    FLOW_FONT_SIZE,
    add_brand_mark,
    add_source,
    cfg,
    flow_diagram,
    mpatches,
    save_fig,
    stats,
):
    fig_rt = flow_diagram(
        nodes={
            # root at same y as medium-term → straight horizontal arrow r→m
            "r":  ("Six AI \nRevenue Assumptions\n(2025 spending)", 1.2, 1.5, COLORS["accent"], COLORS["background"]),
            "n":  ("Near-term:\nproven revenue", 4.5, 4.9, COLORS["muted"], COLORS["background"]),
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
            mpatches.Patch(facecolor=COLORS["muted"], label="Near-term: proven revenue"),
            mpatches.Patch(facecolor=COLORS["neutral"], label="Medium-term: speculative"),
            mpatches.Patch(facecolor=CONTEXT, label="Long-term: no revenue model"),
        ],
    )
    add_source(fig_rt, "Source: SEC 10-Q/K filings via yfinance; company earnings calls")
    add_brand_mark(fig_rt, logo_path=str(cfg.project_root / 'src/assets/tzdlabs_mark.png'))
    save_fig(fig_rt, cfg.img_dir / "dd001_revenue_theses.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo):
    _chart = mo.image(src=(cfg.img_dir / "dd001_revenue_theses.png").read_bytes(), width=850)
    mo.md(f"""
    # One spending line, six incompatible demand assumptions

    {_chart}

    *Six revenue assumptions are being funded from the same pool of capital investment. Only
    the near-term products (better search, enterprise software) have demonstrated commercial
    scale so far. Source: NYT, "What Exactly Are A.I. Companies Trying to Build?" Sep 2025.*
    """)
    return


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    Capital investment figures add all six visions together. Revenue coming in right now
    reflects mainly the near-term products: better search and productivity software.

    Microsoft's Azure AI business reached a \\${stats['azure_ai_run_rate_bn']}B annual
    run rate by January 2026, growing 175% year-on-year (Microsoft Q2 FY2026 earnings
    call). Google Cloud's remaining performance obligations reached
    \\${stats['gcp_rpo_bn']}B, and cloud revenue is growing
    {stats['cloud_yoy_min']:.0f}–{stats['cloud_yoy_max']:.0f}% year-on-year. Those
    figures are real. But a significant portion of cloud demand comes from AI startups
    funded by venture capital (\\${stats['vc_ai_2024_bn']}B in venture investment
    globally in 2024, PitchBook). Those startups are large cloud customers whose
    spending depends on continued investor funding rather than their own revenue.
    McKinsey's 2025 survey found only about 25% of businesses testing generative AI
    saw meaningful impact on their bottom line.

    If the longer-horizon bets don't develop into products people pay for, the
    infrastructure built for them runs at a fraction of capacity. By 2028–2030, that
    means: revenue growth slows, operators carry the fixed costs of infrastructure
    built for demand that never arrived.

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
    add_brand_mark,
    add_rule,
    add_source,
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
                f"Capital expenditure overtakes revenue\n\\${_cap_vals[_i]:.0f}B vs \\${_rev_vals[_i]:.0f}B",
                xy=(_i, _cap_vals[_i]), xytext=(_i - 3, _cap_vals[_i] + 15),
                fontsize=FONTS["annotation"], color=COLORS["accent"], fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=COLORS["accent"], connectionstyle="arc3,rad=-0.2", linewidth=1.5),
            )
            break
    _last = len(_common) - 1
    _ax.text(_last, _rev_vals[_last] - 4, f"${_rev_vals[_last]:.0f}B", ha="center", va="top", fontsize=FONTS["annotation"], color=COLORS["text_light"])
    _ax.text(_last + 0.15, _cap_vals[_last] + 1.5, f"${_cap_vals[_last]:.0f}B", ha="left", va="bottom", fontsize=FONTS["annotation"], color=COLORS["accent"], fontweight="bold")
    _ax.set_xticks(_x)
    _ax.set_xticklabels(_common, fontsize=FONTS["tick_label"], rotation=45, ha="right")
    _ax.set_ylabel("Quarterly ($B)", fontsize=FONTS["axis_label"])
    _ax.tick_params(axis="y", labelsize=FONTS["tick_label"])
    _ax.set_ylim(0, max(max(_rev_vals), max(_cap_vals)) * 1.25)
    legend_below(_ax, ncol=2, bbox_to_anchor=(0.5, -0.22))
    chart_title(fig_rev, "Quarterly cloud revenue vs. capital expenditure, Amazon + Alphabet + Microsoft ($B)")
    plt.tight_layout(rect=[0.02, 0.08, 1, 1])
    add_rule(_ax)
    add_source(fig_rev, "Source: SEC 10-Q filings via yfinance; company earnings calls")
    add_brand_mark(fig_rev, logo_path=str(cfg.project_root / 'src/assets/tzdlabs_mark.png'))
    save_fig(fig_rev, cfg.img_dir / "dd001_revenue_gap.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo, stats):
    _chart = mo.image(src=(cfg.img_dir / "dd001_revenue_gap.png").read_bytes(), width=850)
    mo.md(f"""
    # Total capital expenditure overtook cloud revenue in late 2025

    {_chart}

    *By Q4 2025, capital expenditure for Amazon, Alphabet, and Microsoft exceeded combined cloud revenue; full-year 2025 was about \\${stats['capex_3co_2025']:.0f}B vs about \\${stats['cloud_rev_2025']:.0f}B. About {stats['ai_capex_share_pct']}% of hyperscaler capex is AI-attributed (CreditSights, "Hyperscaler AI Capex: How Big Is Too Big?", 2024). Source: SEC 10-Q filings.*
    """)
    return


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    ## 3. What happens if the demand doesn't arrive?

    The last infrastructure cycle that looked like this was fiber optic cable in the
    late 1990s. US telecom companies invested roughly \\${stats['telecom_capex_bn']}B
    between 1996 and 2002, financed largely by \\${stats['telecom_debt_tn']:.1f} trillion
    in issued debt. Their capex-to-revenue ratio peaked at {stats['telecom_capex_rev_pct']}%,
    roughly double the industry norm. By 2002, an estimated 3-5% of installed fiber was
    carrying traffic. The infrastructure survived; the companies that built it mostly
    did not.

    The structural difference: those companies borrowed to build. Today's AI builders
    spend from operating cash flow. A demand disappointment would reduce future
    investment, not trigger cascading defaults. The losses fall on equity holders
    through lower earnings, not on creditors.

    If efficiency gains reduce infrastructure demand, the ratio of spending to revenue
    should fall. If it does not, companies are building ahead of demand, and the risk of
    overbuilding is structural, not cyclical.

    DeepSeek R1 provided that test. When a major efficiency signal arrived in January
    2025, did spending slow?
    """)
    return


@app.cell
def _(
    COLORS,
    CONTEXT,
    FIGSIZE,
    FONTS,
    add_brand_mark,
    add_rule,
    add_source,
    capex_annual,
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
    _ax.set_ylabel("Quarterly capital expenditure ($B)", fontsize=FONTS["axis_label"])
    _ax.tick_params(axis="both", labelsize=FONTS["tick_label"])
    _ax.grid(True, axis="y", linestyle=":", alpha=0.4)
    _ymax = capex_raw[capex_raw["ticker"].isin(_tickers)]["capex_bn"].max()
    # Annual combined total annotations — extend ylim to create header band
    _annual_4co = capex_annual[capex_annual["ticker"].isin(_tickers)].groupby("year")["capex_bn"].sum()
    _ax.set_ylim(0, _ymax * 1.22)
    for _yr, _mid in [(2023, "2023-07-01"), (2024, "2024-07-01"), (2025, "2025-07-01")]:
        if _yr not in _annual_4co.index:
            continue
        _ax.text(
            pd.Timestamp(_mid), _ymax * 1.10,
            f"{_yr}: ${_annual_4co[_yr]:.0f}B combined",
            fontsize=FONTS["annotation"], color=COLORS["muted"],
            ha="center", va="center",
        )
    _ax.axvline(_deepseek_date, color=COLORS["accent"], linestyle="-", linewidth=2, alpha=0.7)
    _ax.text(_deepseek_date, _ymax * 0.98, "  DeepSeek R1", fontsize=FONTS["annotation"], color=COLORS["accent"], fontweight="bold", va="top")
    _ax.text(_deepseek_date + pd.Timedelta(days=200), _ymax * 0.18, "All four accelerated\nafter DeepSeek", fontsize=FONTS["annotation"], color=COLORS["accent"], fontweight="bold", ha="left", va="center", bbox={"boxstyle": "round,pad=0.4", "fc": "white", "ec": COLORS["accent"], "alpha": 0.8})
    legend_below(_ax, ncol=4)
    chart_title(fig_quarterly, "Quarterly capex by company, 2023–2025 ($B)")
    plt.tight_layout(rect=[0.02, 0.08, 1, 1])
    add_rule(_ax)
    add_source(fig_quarterly, "Source: SEC 10-Q filings via yfinance")
    add_brand_mark(fig_quarterly, logo_path=str(cfg.project_root / 'src/assets/tzdlabs_mark.png'))
    save_fig(fig_quarterly, cfg.img_dir / "dd001_quarterly_capex.png")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    # DeepSeek-V3 reportedly trained for $6M — a fraction of current infrastructure budgets

    DeepSeek's reported $6M figure for V3's final training run (arXiv:2412.19437, Dec 2024)
    is self-reported and partial (one run, not the full cost of development). But the
    directional claim matters: models matching or approaching the capability of today's
    most powerful systems may be achievable at costs far below what current infrastructure
    spending implies.
    """)
    return


@app.cell(hide_code=True)
def _(cfg, mo, stats):
    _chart = mo.image(src=(cfg.img_dir / "dd001_quarterly_capex.png").read_bytes(), width=850)
    mo.md(f"""
    # DeepSeek R1 changed nothing — all four AI builders accelerated capital expenditure

    {_chart}

    *Even after DeepSeek R1 (Jan 2025), all four major builders kept accelerating through Q4 2025, despite Nvidia losing about \\${stats['nvda_deepseek_loss_bn']}B in market value in a single day on the efficiency news. Source: yfinance (SEC filings).*
    """)
    return


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    Compute got much cheaper, but total infrastructure spending still increased. The spending
    data through Q4 2025 fits both explanations: companies are investing ahead of real demand,
    or cheaper compute is unlocking so much more usage that total spending rises anyway. The
    data alone cannot tell which.

    The second explanation has a name: the Jevons paradox. When something gets cheaper,
    people use more of it, and total consumption can rise even as the unit price falls.
    OpenAI's cost to process one million tokens — roughly 750,000 words of text, or about
    seven novels — fell about 97%, from roughly $60 in March 2023 to roughly $2.50 by
    May 2024, and usage volumes rose. But the paradox only
    holds when demand responds strongly enough to more than offset the price drop. Whether AI
    usage is that sensitive to price is not yet established.

    Three things would all need to be true for cheaper compute to fully explain the spending
    trajectory:
    1. **Costs keep falling** — verified; roughly 10x cheaper per 18 months (company pricing pages, 2023–2025)
    2. **Demand grows faster than costs fall** — plausible but not yet demonstrated at scale
    3. **New categories of use open up** — cheaper compute enables things that weren't possible before, not just cheaper versions of existing things

    Satya Nadella (Microsoft CEO, January 2025): "{stats['nadella_demand_supply']}" Jensen
    Huang (Nvidia CEO, GTC 2024): "{stats['huang_industrial_rev']}"

    Jim Covello, Goldman Sachs's head of global equity research, asked a different
    question in June 2024: "{stats['covello_trillion']}" MIT economist Daron Acemoglu
    estimated AI would add {stats['acemoglu_tfp_pct']}% to total factor productivity
    over a decade (NBER Working Paper 32487, May 2024). Goldman's own economist
    Joseph Briggs estimated {stats['gs_tfp_pct']}%. The gap between those two
    numbers — roughly 10× — is the gap between the bull case and the bear case
    for this infrastructure.

    The 2026 spending figures are also less certain than they appear. Company guidance on
    capital investment has historically shifted by as much as plus or minus
    {stats['guidance_max_revision_pct']}% within a single year. Meta cut its 2023 investment
    plans by {stats['meta_guidance_cut_pct']}%, from an original range of
    \\${stats['meta_2023_guidance_low']}–{stats['meta_2023_guidance_high']}B down to
    \\${stats['meta_2023']:.0f}B actual. Microsoft raised its fiscal year 2025 plans by
    {stats['msft_guidance_raise_pct']}% in a single quarter.
    """)
    return


@app.cell
def _(COLORS, CONTEXT, FONTS, add_brand_mark, add_source, cfg, chart_title, plt, save_fig, stats):
    _meta_pct = -stats["meta_guidance_cut_pct"]    # negative: guidance cut
    _msft_pct = stats["msft_guidance_raise_pct"]   # positive: guidance raised

    fig_guidance, _ax = plt.subplots(figsize=(8.0, 2.6))

    _ax.axvline(0, color=CONTEXT, linewidth=1.2, linestyle="--", alpha=0.5, zorder=1)
    _ax.text(0, 1.62, "Initial guidance", ha="center", va="bottom",
             fontsize=FONTS["annotation"] - 1, color=CONTEXT)

    # Microsoft row (positive: raise)
    _ax.plot([0, _msft_pct], [1, 1], color=COLORS["accent"], linewidth=2.5,
             solid_capstyle="round", zorder=2)
    _ax.scatter([0], [1], s=80, color=CONTEXT, zorder=3)
    _ax.scatter([_msft_pct], [1], s=120, color=COLORS["accent"], zorder=3)
    _ax.text(0, 1.12, f"${stats['msft_fy25_initial_g']:.0f}B", ha="center", va="bottom",
             fontsize=FONTS["annotation"] - 1, color=CONTEXT)
    _ax.text(_msft_pct + 1, 1, f"${stats['msft_fy25_revised_g']:.0f}B  +{_msft_pct:.0f}%",
             ha="left", va="center", fontsize=FONTS["annotation"],
             color=COLORS["accent"], fontweight="bold")
    _ax.text(-45, 1, "Microsoft FY2025", ha="right", va="center",
             fontsize=FONTS["tick_label"], color=COLORS["text_dark"])

    # Meta row (negative: cut)
    _ax.plot([0, _meta_pct], [0, 0], color=COLORS["accent"], linewidth=2.5,
             solid_capstyle="round", zorder=2)
    _ax.scatter([0], [0], s=80, color=CONTEXT, zorder=3)
    _ax.scatter([_meta_pct], [0], s=120, color=COLORS["accent"], zorder=3)
    _ax.text(0, 0.12, f"${stats['meta_2023_guidance_low']}–{stats['meta_2023_guidance_high']}B",
             ha="center", va="bottom", fontsize=FONTS["annotation"] - 1, color=CONTEXT)
    _ax.text(_meta_pct - 1, 0,
             f"${stats['meta_2023']:.0f}B  {_meta_pct:.0f}%",
             ha="right", va="center", fontsize=FONTS["annotation"],
             color=COLORS["accent"], fontweight="bold")
    _ax.text(-45, 0, "Meta 2023", ha="right", va="center",
             fontsize=FONTS["tick_label"], color=COLORS["text_dark"])

    _ax.set_xlim(-48, 48)
    _ax.set_ylim(-0.5, 1.8)
    _ax.set_yticks([])
    _ax.spines["left"].set_visible(False)
    _ax.set_xlabel("Change from initial guidance (%)", fontsize=FONTS["axis_label"])
    _ax.tick_params(axis="x", labelsize=FONTS["tick_label"])
    _ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:+.0f}%"))
    chart_title(fig_guidance, "Initial vs. actual capex guidance, selected cases 2023–2025 (% change from initial)")
    plt.tight_layout(rect=[0.02, 0.08, 1, 1])
    add_source(fig_guidance, "Source: Company earnings calls; SEC filings")
    add_brand_mark(fig_guidance, logo_path=str(cfg.project_root / 'src/assets/tzdlabs_mark.png'))
    save_fig(fig_guidance, cfg.img_dir / "dd001_guidance_reliability.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo, stats):
    _chart = mo.image(src=(cfg.img_dir / "dd001_guidance_reliability.png").read_bytes(), width=750)
    mo.md(f"""
    # Guidance has shifted by as much as {stats['guidance_max_revision_pct']}% in a single year

    {_chart}

    *Meta 2023: initial guidance \\${stats['meta_2023_guidance_low']}–{stats['meta_2023_guidance_high']}B,
    actual \\${stats['meta_2023']:.0f}B (cut {stats['meta_guidance_cut_pct']}%). Microsoft FY2025: initial
    guidance \\${stats['msft_fy25_initial_g']:.0f}B, revised to \\${stats['msft_fy25_revised_g']:.0f}B
    (+{stats['msft_guidance_raise_pct']}% in a single quarter). Sources: Meta Q1 2023 earnings call;
    Microsoft FY2025 Q1 and Q2 earnings calls.*
    """)
    return


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    The \\${stats['guidance_2026_point']:.0f}B combined 2026 figure is directionally correct but
    should not be read as a firm commitment at the company level. It would also require these
    companies to spend about {stats['capex_ocf_2026_pct']:.0f}% of the cash their operations
    generated over the past twelve months (about \\${stats['ocf_ttm']:.0f}B total), well above their
    historical average of about {stats['hist_capex_ocf_avg_pct']}% (Bernstein Research, 2024). Amazon
    alone is already at about {stats['amzn_ocf_pct']:.0f}% of its operating cash flow.

    For context: the 1990s telecom buildout reached similar capex-to-revenue ratios
    ({stats['telecom_capex_rev_pct']}% at peak, against a 15-20% norm), but was financed
    by \\${stats['telecom_debt_tn']:.1f} trillion in issued debt. When demand disappointed,
    the debt triggered cascading defaults. These companies finance from cash flow. A
    pullback would mean lower future earnings, not a credit crisis.
    """)
    return


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    ## The signal to watch

    Amazon, Alphabet, and Microsoft spent
    **{stats['capex_3co_2025'] / stats['cloud_rev_2025']:.2f} dollars** on infrastructure
    for every dollar of cloud revenue they earned in 2025, the first time the ratio has
    crossed above 1.0. Where this ratio goes next answers all three questions at once.
    """)
    return


@app.cell
def _(COLORS, CONTEXT, FONTS, add_brand_mark, add_source, capex_annual, cfg, chart_title, cloud_rev, plt, save_fig, stats):
    _tickers = ["AMZN", "GOOGL", "MSFT"]

    # Historical aggregate capex / cloud-revenue ratio
    _cloud_yr = (
        cloud_rev[cloud_rev["ticker"].isin(_tickers)]
        .assign(year=lambda d: d["quarter"].str[:4].astype(int))
        .groupby("year")["revenue_bn"].sum()
    )
    _capex_yr = (
        capex_annual[capex_annual["ticker"].isin(_tickers)]
        .groupby("year")["capex_bn"].sum()
    )
    _hist_years = [y for y in [2023, 2024, 2025] if y in _cloud_yr.index and y in _capex_yr.index]
    _missing_years = {2023, 2024, 2025} - set(_hist_years)
    if _missing_years:
        raise ValueError(
            f"Scenario chart: missing coverage for years {sorted(_missing_years)} in "
            "cloud_rev or capex_annual. Check DB pipeline coverage."
        )
    _hist_ratio = [float(_capex_yr[y] / _cloud_yr[y]) for y in _hist_years]
    _r2025 = _hist_ratio[-1]

    # Scenario endpoints for 2026 — illustrative, not forecasts
    _scenarios = [
        (_r2025 * 0.78, "Demand catches up",    COLORS["positive"]),
        (_r2025 * 1.03, "Status quo",            CONTEXT),
        (_r2025 * 1.35, "Overbuilding continues", COLORS["accent"]),
    ]

    fig_scenarios, _ax = plt.subplots(figsize=(8.5, 4.0))

    _ax.axhline(1.0, color=CONTEXT, linewidth=1, linestyle="--", alpha=0.4, zorder=1)
    _ax.text(2022.6, 1.02, "Spending = Revenue", va="bottom",
             fontsize=FONTS["annotation"] - 1, color=CONTEXT, alpha=0.65)

    # Historical line
    _ax.plot(_hist_years, _hist_ratio, color=COLORS["text_dark"], linewidth=2.5,
             marker="o", markersize=7, markerfacecolor="white",
             markeredgecolor=COLORS["text_dark"], markeredgewidth=2.2, zorder=4)
    for _y, _r in zip(_hist_years, _hist_ratio):
        _yoff = 0.05 if _r < 1.0 else -0.07
        _va = "bottom" if _r < 1.0 else "top"
        _ax.text(_y, _r + _yoff, f"{_r:.2f}×", ha="center", va=_va,
                 fontsize=FONTS["annotation"] - 1, color=COLORS["text_dark"])

    # Scenario fan from 2025
    for _r26, _label, _color in _scenarios:
        _ax.plot([2025, 2026], [_r2025, _r26], color=_color, linewidth=2.2,
                 linestyle="--", alpha=0.9, zorder=3)
        _ax.scatter([2026], [_r26], s=80, color=_color, zorder=5,
                    edgecolors="white", linewidths=1.2)
        _ax.text(2026.08, _r26, f"{_label}  {_r26:.2f}×", va="center",
                 fontsize=FONTS["annotation"], color=_color, fontweight="bold")

    _ax.set_xticks(_hist_years + [2026])
    _ax.set_xticklabels(["2023", "2024", "2025", "2026\n(scenarios)"],
                        fontsize=FONTS["tick_label"])
    _ax.set_xlim(2022.5, 2027.5)
    _ax.set_ylim(0.35, 1.75)
    _ax.set_yticks([])
    _ax.spines["left"].set_visible(False)
    chart_title(
        fig_scenarios,
        "Capex-to-cloud-revenue ratio, Amazon + Alphabet + Microsoft, 2023–2026 scenarios",
    )
    plt.tight_layout(rect=[0.02, 0.08, 1, 1])
    add_source(fig_scenarios, "Source: Company guidance; author projections")
    add_brand_mark(fig_scenarios, logo_path=str(cfg.project_root / 'src/assets/tzdlabs_mark.png'))
    save_fig(fig_scenarios, cfg.img_dir / "dd001_scenarios_2026.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo, stats):
    _chart = mo.image(src=(cfg.img_dir / "dd001_scenarios_2026.png").read_bytes(), width=800)
    mo.md(f"""
    # The {stats['capex_3co_2025'] / stats['cloud_rev_2025']:.2f}× ratio is the signal to watch — three paths from here

    {_chart}

    *Annual capex as a share of cloud revenue (Amazon AWS, Microsoft Azure, Google Cloud),
    2023–2025 reported. 2026 scenarios are illustrative, not forecasts.*
    """)
    return


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md("""
    **Ratio falls:** demand is catching up. Companies can justify continuing to build,
    provided revenue growth comes from durable enterprise contracts rather than
    venture-funded startups.

    **Ratio holds near 1.0:** the picture stays mixed. Wait for more data.

    **Ratio keeps rising:** overbuilding. If the ratio climbs while businesses using AI
    still can't show improved financial results, the spending has outrun the demand.

    The worst case by 2028–2030: enterprise revenue stalls, operators carry the fixed costs
    of infrastructure built for demand that never arrived, and ratepayers absorb utility
    grid upgrades they'll be paying off for decades.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ---

    Capital commitments are clear. Whether physical infrastructure actually gets built at
    the pace announced is a different question.

    **Next:** [02_conversion_reality.py](./02_conversion_reality.py) — construction timelines, grid interconnection queues, and the gap between announcement and operation.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    import altair as alt

    from src.altair_theme import register as _reg
    from src.data.db import query as _query

    _reg()

    _df = _query("""
        SELECT ticker, date, capex_bn
        FROM energy_data.hyperscaler_capex
        ORDER BY ticker, date
    """)

    _chart = (
        alt.Chart(_df)
        .mark_line(point=alt.OverlayMarkDef(size=30))
        .encode(
            x=alt.X("date:T", title=None, axis=alt.Axis(format="%Y")),
            y=alt.Y("capex_bn:Q", title="CapEx ($ billions)"),
            color=alt.Color("ticker:N", title="Company"),
            tooltip=[
                alt.Tooltip("date:T", title="Quarter", format="%b %Y"),
                alt.Tooltip("ticker:N", title="Company"),
                alt.Tooltip("capex_bn:Q", title="CapEx ($B)", format=".2f"),
            ],
        )
        .properties(width="container", height=300)
        .interactive()
    )

    from src.notebook import SITE_URL as _SITE_URL
    _lite = f"https://lite.datasette.io/?url={_SITE_URL}/data/research.sqlite#/research/hyperscaler_capex"

    mo.accordion({
        "Explore the data": mo.vstack([
            mo.md(
                "Quarterly CapEx by hyperscaler. Hover for exact values; "
                "click and drag to zoom; double-click to reset."
            ),
            _chart,
            mo.md(f"[Open `hyperscaler_capex` in Datasette →]({_lite})"),
        ], gap="0.75rem"),
    })
    return


if __name__ == "__main__":
    app.run()
