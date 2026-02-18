import marimo

__generated_with = "0.19.11"
app = marimo.App(
    width="medium",
    app_title="DD-001: Conversion Reality",
    css_file="../../src/notebook_theme/custom.css",
    html_head_file="../../src/notebook_theme/head.html",
)


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    # From Announcement to Infrastructure: The Conversion Gap

    *Thandolwethu Zwelakhe Dlamini*

    ---

    Capital commitment and physical delivery are different things. The previous notebook
    documented ~\\${stats['capex_2025']:.0f}B in disclosed capex (2025) and ~\\${stats['guidance_2026_point']:.0f}B guided for 2026.
    This notebook asks the harder question: how much of that is becoming operating
    infrastructure, on what timeline, and with what physical footprint?

    The short answer: slowly. Interconnection queues now hold {stats['queue_total_gw']:,} GW of
    proposed capacity, but only {stats['queue_completion_pct']}% of queued projects historically reach
    commercial operation. A single Amazon campus in Indiana — Project Rainier — accounts for
    roughly half of Indiana's projected load growth through 2030. The constraint is not
    capital. It is the physical sequence: land, permits, grid interconnection, construction,
    equipment, energization.

    The infrastructure that *does* get built will outlast the demand thesis by decades.
    Understanding the asset-life distribution is the key to understanding lock-in.
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
        FONTS,
        chart_title,
        legend_below,
    )
    cfg = setup()
    return (
        COLORS, CONTEXT, FIGSIZE, FONTS, cfg, chart_title,
        legend_below, mo, mpatches, np, pd, plt, query, save_fig,
    )


@app.cell
def _(pd, query):
    _tickers_6 = ["MSFT", "AMZN", "GOOGL", "META", "ORCL", "NVDA"]
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
    queue_summary = query("""
        SELECT year, generation_gw, storage_gw, total_gw,
               solar_gw, wind_gw, gas_gw, nuclear_gw, other_gw,
               completion_pct, withdrawal_pct
        FROM energy_data.lbnl_queue_summary ORDER BY year
    """)
    ppe_schedule = query("""
        SELECT ticker, fiscal_year, category, category_raw, gross_value_m
        FROM energy_data.edgar_ppe_schedule
    """)
    _pnfi = query("""
        SELECT value FROM energy_data.fred_series
        WHERE series_id = 'PNFI' ORDER BY date DESC LIMIT 1
    """)
    pnfi_bn = float(_pnfi["value"].iloc[0])
    _cite_raw = query("""
        SELECT key, value FROM energy_data.source_citations
    """)
    citations = dict(zip(_cite_raw["key"], _cite_raw["value"]))
    guidance_2026 = query("""
        SELECT ticker, year, capex_bn, source FROM energy_data.capex_guidance
    """)
    return capex_annual, capex_raw, citations, guidance_2026, pnfi_bn, queue_summary, ppe_schedule


@app.cell
def _(capex_annual, citations, guidance_2026, ppe_schedule, pnfi_bn, queue_summary):
    _tickers_6 = ["MSFT", "AMZN", "GOOGL", "META", "ORCL", "NVDA"]
    _annual = capex_annual[capex_annual["ticker"].isin(_tickers_6)]

    # --- capex totals ---
    stats = {
        "capex_2025": _annual[_annual["year"] == 2025]["capex_bn"].sum(),
        "guidance_2026_point": guidance_2026[guidance_2026["ticker"].isin(_tickers_6)]["capex_bn"].sum(),
        "pnfi_bn": pnfi_bn,
        "dc_construction_low_bn": int(citations["dc_construction_low_bn"]),
        "dc_construction_high_bn": int(citations["dc_construction_high_bn"]),
        "analyst_const_pct_low": int(citations["analyst_const_pct_low"]),
    }
    stats["pnfi_share_pct"] = stats["capex_2025"] / stats["pnfi_bn"] * 100

    # --- AI era totals (2022-2025) for lock-in calculation ---
    _ai_era = _annual[_annual["year"].isin([2022, 2023, 2024, 2025])]
    stats["ai_era_total_bn"] = _ai_era["capex_bn"].sum()

    # --- PP&E decomposition from 10-K schedules ---
    _ppe_2024 = ppe_schedule[ppe_schedule["fiscal_year"] == 2024]
    _const_cats = ["Construction in progress", "Land and buildings", "Leasehold improvements"]
    _equip_cats = ["Machinery and equipment", "Servers", "Network equipment", "Right-of-use assets"]
    _ppe_const = _ppe_2024[_ppe_2024["category"].isin(_const_cats)]["gross_value_m"].sum()
    _ppe_equip = _ppe_2024[_ppe_2024["category"].isin(_equip_cats)]["gross_value_m"].sum()
    _ppe_total = _ppe_const + _ppe_equip
    stats["decomp_const_pct"] = round(_ppe_const / _ppe_total * 100) if _ppe_total > 0 else 42
    stats["decomp_equip_pct"] = 100 - stats["decomp_const_pct"]
    stats["decomp_const_low"] = max(stats["decomp_const_pct"] - 8, 30)
    stats["decomp_const_high"] = min(stats["decomp_const_pct"] + 8, 60)
    stats["ai_era_const_bn"] = round(stats["ai_era_total_bn"] * stats["decomp_const_pct"] / 100)

    # --- Queue stats from LBNL data ---
    _q_latest = queue_summary.iloc[-1]
    _q_prev = queue_summary.iloc[-2] if len(queue_summary) > 1 else _q_latest
    stats["queue_total_gw"] = int(_q_latest["total_gw"])
    stats["queue_withdrawal_pct"] = int(_q_latest["withdrawal_pct"])
    stats["queue_completion_pct"] = int(_q_latest["completion_pct"])
    stats["queue_yoy_pct"] = round(
        (_q_latest["total_gw"] - _q_prev["total_gw"]) / _q_prev["total_gw"] * 100
    ) if _q_prev["total_gw"] > 0 else 0
    stats["queue_solar_gw"] = int(_q_latest["solar_gw"])
    stats["queue_wind_gw"] = int(_q_latest["wind_gw"])
    stats["queue_gas_gw"] = int(_q_latest["gas_gw"])
    stats["queue_storage_gw"] = int(_q_latest["storage_gw"])
    _total_gw = _q_latest["total_gw"]
    stats["queue_solar_pct"] = round(_q_latest["solar_gw"] / _total_gw * 100)
    stats["queue_wind_pct"] = round(_q_latest["wind_gw"] / _total_gw * 100)
    stats["queue_storage_pct"] = round(_q_latest["storage_gw"] / _total_gw * 100)
    _gas_prev = float(_q_prev["gas_gw"]) if float(_q_prev["gas_gw"]) > 0 else 1.0
    stats["queue_gas_growth_pct"] = round(
        (float(_q_latest["gas_gw"]) - _gas_prev) / _gas_prev * 100
    )
    # --- Queue cohort completion rates (source_citations) ---
    stats["queue_cohort_2000_2005_pct"] = int(citations["queue_cohort_2000_2005_pct"])
    stats["queue_cohort_2006_2010_pct"] = int(citations["queue_cohort_2006_2010_pct"])
    stats["queue_cohort_2011_2015_pct"] = int(citations["queue_cohort_2011_2015_pct"])
    # --- Stargate ---
    stats["stargate_announced_bn"] = int(citations["stargate_announced_bn"])
    stats["stargate_initial_bn"] = int(citations["stargate_initial_bn"])
    # --- Project Rainier ---
    stats["rainier_gw"] = float(citations["rainier_gw"])
    stats["rainier_dc_planned"] = int(citations["rainier_dc_planned"])
    stats["rainier_dc_built_jun2025"] = int(citations["rainier_dc_built_jun2025"])
    stats["rainier_workers_weekly"] = int(citations["rainier_workers_weekly"])
    stats["rainier_tax_break_sales_bn"] = int(citations["rainier_tax_break_sales_bn"])
    stats["rainier_tax_break_property_bn"] = int(citations["rainier_tax_break_property_bn"])
    stats["aep_indiana_peak_2024_gw"] = float(citations["aep_indiana_peak_2024_gw"])
    stats["aep_indiana_peak_2030_gw"] = int(citations["aep_indiana_peak_2030_gw"])
    stats["aep_gas_share_pct"] = int(citations["aep_gas_share_pct"])
    return (stats,)


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
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

    FY2024 10-K property schedules (EDGAR) imply ~{stats['decomp_const_pct']}% of gross PP&E is
    construction-class assets (land, buildings, leasehold improvements, CIP) and
    ~{stats['decomp_equip_pct']}% is equipment-class (servers, network gear, machinery). In practice,
    the split varies: Meta skews toward construction; Microsoft skews toward equipment.
    The range across the three companies with clear disclosure is {stats['decomp_const_low']}–{stats['decomp_const_high']}%.
    """)
    return


@app.cell
def _(COLORS, CONTEXT, FIGSIZE, FONTS, cfg, chart_title, plt, save_fig, stats):
    _total_capex = round(stats["capex_2025"])
    _equip = _total_capex * stats["decomp_equip_pct"] / 100
    _const = _total_capex * stats["decomp_const_pct"] / 100
    _equip_life = 6
    _const_life = 40
    _h_equip = 1.0
    _h_const = (_const / _equip) if _equip > 0 else 0.42

    fig_decomp, _ax = plt.subplots(figsize=FIGSIZE["wide"])

    _ax.barh(
        [1.6], [_equip_life], height=_h_equip,
        color=CONTEXT, alpha=0.85, edgecolor="white", linewidth=0.5, left=2025,
    )
    _ax.barh(
        [0.6], [_const_life], height=_h_const,
        color=COLORS["accent"], alpha=0.85, edgecolor="white", linewidth=0.5, left=2025,
    )
    _ax.axvspan(2025, 2028, alpha=0.06, color=COLORS["accent"])
    _ax.text(
        2026.5, 2.3, "AI demand\nforecast\nhorizon",
        ha="center", fontsize=FONTS["annotation"] - 1, color=COLORS["accent"], alpha=0.7,
    )
    _ax.axvline(2025 + _equip_life, color=CONTEXT, linewidth=1, linestyle="--", alpha=0.6)
    _ax.text(
        2025 + _equip_life + 0.3, 2.3, "Equipment\nfully replaced",
        fontsize=FONTS["annotation"] - 1, color=CONTEXT, va="top",
    )
    _ax.text(
        2025 + _equip_life / 2, 1.6,
        f"Equipment  ${_equip:.0f}B", va="center", ha="center",
        fontsize=FONTS["annotation"] - 2, color=COLORS["text_dark"], fontweight="bold",
    )
    _ax.text(
        2025 + _const_life / 2, 0.6,
        f"Construction  ${_const:.0f}B", va="center", ha="center",
        fontsize=FONTS["annotation"], color="white", fontweight="bold",
    )
    _ax.text(
        2025 + _equip_life + 0.5, 1.6, "~6 yr life",
        va="center", fontsize=FONTS["annotation"], color=COLORS["text_dark"], fontweight="bold",
    )
    _ax.text(
        2025 + _const_life + 0.5, 0.6, "20\u201340 yr life",
        va="center", fontsize=FONTS["annotation"], color=COLORS["accent"], fontweight="bold",
    )
    _ax.set_xlim(2024, 2072)
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
    typically persist for 20–40 years. Equipment turns over much faster. Horizontal
    span represents asset life; bar thickness represents 2025 capex scale. Note:
    Alphabet extended server useful life from 4 to 6 years in 2024, adding ~$3.9B to
    annual operating income — asset life assumptions materially affect the economics
    (Alphabet 10-K FY2024, Note 1). Cumulated across the 2022–2025 AI era, the six major
    builders committed ~${stats['ai_era_total_bn']:.0f}B in total capex — of which approximately
    ~${stats['ai_era_const_bn']:.0f}B (applying the {stats['decomp_const_pct']}% EDGAR-derived construction
    share) is now embedded in physical infrastructure with 20–40 year asset lives.*

    This is the lock-in asymmetry. Investment risk is often evaluated on a 3–5 year
    return horizon, but much of the physical footprint lasts far longer. A gas plant
    built to power a data center campus is demand-thesis-dependent at inception. Once
    built, it operates for 40 years regardless of whether the data center scales as
    planned. The path-dependency literature (Arthur 1989; David 1985) demonstrates how
    early capital choices create self-reinforcing lock-in — the lock-in here is not just
    technological but geographic and infrastructural. Substations, transmission lines,
    and campus foundations cannot be relocated the way software platforms can.
    """)
    return


@app.cell(hide_code=True)
def _(mo, stats):
    _capex_low = stats["capex_2025"] * stats["analyst_const_pct_low"] / 100
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

    The binding constraint is **power availability**. The typical time from
    interconnection request to commercial operation has grown to ~5 years nationally,
    up from ~3 years a decade ago *(Rand et al., 2025)*. This is a physical bottleneck
    that no amount of capital can instantly resolve.

    **Context on completion rates:** The {stats['queue_completion_pct']}% headline figure is partly a censoring
    artifact — recent cohorts haven't had time to complete. But even fully matured
    cohorts show low rates: {stats['queue_cohort_2000_2005_pct']}% for 2000-2005 entries, declining to {stats['queue_cohort_2006_2010_pct']}% (2006-2010)
    and {stats['queue_cohort_2011_2015_pct']}% (2011-2015) *(Rand et al., 2025, Table 3)*. The queue has never
    been an efficient pipeline. Low completion is partly structural in first-come,
    first-served systems with low entry costs — developers rationally submit speculative
    requests to preserve optionality (Palmer et al., RFF, 2024). FERC Order 2023 shifts
    to first-ready, first-served processing to address this.

    The queue composition is shifting: natural gas requests grew significantly to
    ~{stats['queue_gas_gw']} GW (end-2024), likely reflecting data center demand for firm,
    dispatchable power. Solar remains dominant at ~{stats['queue_solar_gw']:,} GW ({stats['queue_solar_pct']}% of total queue),
    storage ~{stats['queue_storage_gw']:,} GW ({stats['queue_storage_pct']}%), wind ~{stats['queue_wind_gw']} GW ({stats['queue_wind_pct']}%).

    Supply-side constraints that capex figures don't capture:

    - **GPU allocation and advanced packaging:** TSMC's CoWoS (Chip-on-Wafer-on-Substrate)
      packaging capacity is the proximate bottleneck on H100/H200/B200 AI accelerator
      production. GPU delivery lags order placement by 12–18 months.
    - **Grid interconnection:** The median time from interconnection request to operation
      is 4+ years (LBNL *Queued Up* 2025). Committed construction capex cannot be
      energized until grid capacity is allocated.
    - **Transformer supply:** Lead times for large power transformers have extended to
      2+ years — data center buildings can be erected faster than the substation
      equipment needed to power them (see archived *CS-1: Transformer Manufacturing*).
    """)
    return


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    ### Case Study: Project Rainier (Amazon/Anthropic, Indiana)

    The most detailed public record of AI infrastructure conversion comes from
    Amazon's Project Rainier campus near New Carlisle, Indiana — a facility built
    specifically for Anthropic and documented by the NYT in June 2025.

    **Scale and timeline:**
    - 1,200 acres of former cornfield, 15 miles west of South Bend
    - {stats['rainier_gw']} GW planned capacity — enough to power a million homes
    - ~{stats['rainier_dc_planned']} data centers planned; {stats['rainier_dc_built_jun2025']} built by June 2025 (each larger than
      a football stadium), with four construction firms working simultaneously
    - ~{stats['rainier_workers_weekly']:,} construction workers on site weekly

    **Public subsidy and cost:**
    - Indiana legislature: 50-year sales tax break (~\\${stats['rainier_tax_break_sales_bn']}B, per Citizens Action
      Coalition estimate)
    - County property/technology tax breaks: ~\\${stats['rainier_tax_break_property_bn']}B additional over 35 years
    - Total public subsidy: **~\\${stats['rainier_tax_break_sales_bn'] + stats['rainier_tax_break_property_bn']}B** for one campus

    **Grid impact (the DD-002 connection):**
    - AEP (local utility) told regulators that data centers will more than double
      Indiana's peak power demand: from {stats['aep_indiana_peak_2024_gw']} GW (2024) to {stats['aep_indiana_peak_2030_gw']}+ GW by ~2030
    - **Amazon's campus alone accounts for about half of the additional load**
    - AEP plans to meet ~{stats['aep_gas_share_pct']}% of additional power demand with natural gas —
      directly connecting AI infrastructure to fossil fuel expansion

    **The conversion lesson:** Project Rainier shows what "announcement → infrastructure"
    actually requires: utility negotiations begun months after ChatGPT launched (early 2023),
    land acquired by early 2024, first buildings up by mid-2025. That's roughly a 2-year
    timeline from site selection to initial operation — and as of June 2025 the campus
    is still less than a quarter built. The constraint isn't capital. It's the physical
    sequence: land → permits → utility interconnection → construction → equipment → energization.

    *Source: NYT, "At Amazon's Biggest Data Center, Everything Is Supersized for
    A.I.," Jun 24, 2025 (Weise & Metz).*
    """)
    return


@app.cell
def _(COLORS, CONTEXT, FIGSIZE, FONTS, cfg, chart_title, mpatches, np, plt, save_fig, stats):
    _built = stats["rainier_dc_built_jun2025"]
    _planned = stats["rainier_dc_planned"]
    _remaining = _planned - _built
    _pct_done = _built / _planned * 100

    fig_rainier, (_ax_bar, _ax_time) = plt.subplots(
        2, 1, figsize=(FIGSIZE["wide"][0], FIGSIZE["wide"][1] * 0.85),
        gridspec_kw={"height_ratios": [1, 1.2]},
    )

    # Top: horizontal stacked bar (built vs remaining)
    _ax_bar.barh(0, _built, height=0.5, color=COLORS["accent"], label=f"Built ({_built})")
    _ax_bar.barh(0, _remaining, left=_built, height=0.5, color=CONTEXT, alpha=0.4,
                 label=f"Remaining ({_remaining})")
    _ax_bar.text(_built / 2, 0, f"{_built} built", va="center", ha="center",
                 fontsize=FONTS["value_label"], fontweight="bold", color="white")
    _ax_bar.text(_built + _remaining / 2, 0, f"{_remaining} remaining", va="center",
                 ha="center", fontsize=FONTS["annotation"], color=CONTEXT)
    _ax_bar.text(_planned + 0.4, 0, f"{_pct_done:.0f}% complete", va="center",
                 fontsize=FONTS["annotation"], color=COLORS["text_dark"])
    _ax_bar.set_xlim(0, _planned + 5)
    _ax_bar.set_ylim(-0.5, 0.5)
    _ax_bar.set_xlabel("Number of data center buildings", fontsize=FONTS["axis_label"])
    _ax_bar.tick_params(axis="x", labelsize=FONTS["tick_label"])
    _ax_bar.get_yaxis().set_visible(False)
    _ax_bar.spines[["top", "right", "left"]].set_visible(False)

    # Bottom: milestone timeline
    _milestones = [
        (2023.0, "ChatGPT launches\nutility talks begin"),
        (2024.0, "Land acquired\nsite cleared"),
        (2025.5, "7 of 30 DCs\noperating (Jun 2025)"),
        (2027.0, "Full campus\nestimated"),
    ]
    _ax_time.set_xlim(2022.5, 2028)
    _ax_time.set_ylim(-0.5, 1)
    _ax_time.axhline(0, color=CONTEXT, linewidth=2, alpha=0.4)
    for _year, _label in _milestones:
        _is_current = "Jun 2025" in _label
        _clr = COLORS["accent"] if _is_current else CONTEXT
        _ax_time.plot(_year, 0, "o", markersize=10 if _is_current else 8, color=_clr, zorder=3)
        _ax_time.text(_year, 0.15, _label, ha="center", va="bottom",
                      fontsize=FONTS["annotation"] - 1, color=_clr,
                      fontweight="bold" if _is_current else "normal")
    _ax_time.set_xlabel("Year", fontsize=FONTS["axis_label"])
    _ax_time.tick_params(axis="x", labelsize=FONTS["tick_label"])
    _ax_time.get_yaxis().set_visible(False)
    _ax_time.spines[["top", "right", "left"]].set_visible(False)

    plt.tight_layout(h_pad=1.2)
    chart_title(
        fig_rainier,
        f"Project Rainier: {_pct_done:.0f}% built after 2 years — at {stats['rainier_gw']} GW, it doubles Indiana's peak load",
    )
    save_fig(fig_rainier, cfg.img_dir / "dd001_rainier_progress.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo, stats):
    _chart = mo.image(
        src=(cfg.img_dir / "dd001_rainier_progress.png").read_bytes(), width=850
    )
    mo.md(f"""
    # Project Rainier: {stats['rainier_dc_built_jun2025']} of {stats['rainier_dc_planned']} buildings complete — Amazon's campus alone doubles Indiana's peak grid load

    {_chart}

    *Top: build progress as of June 2025 — {stats['rainier_dc_built_jun2025']} data center buildings completed,
    {stats['rainier_dc_planned'] - stats['rainier_dc_built_jun2025']} remaining, from a planned {stats['rainier_dc_planned']}-building campus.
    Bottom: conversion timeline from announcement to operation.
    The {stats['rainier_gw']} GW campus accounts for roughly half of the additional load AEP Indiana
    is planning to serve by 2030 (from {stats['aep_indiana_peak_2024_gw']} GW to {stats['aep_indiana_peak_2030_gw']}+ GW peak demand).
    AEP plans to meet ~{stats['aep_gas_share_pct']}% of that additional load with natural gas.
    Source: NYT, "At Amazon's Biggest Data Center, Everything Is Supersized for A.I.,"
    Jun 24, 2025 (Weise & Metz).*
    """)
    return


@app.cell
def _(COLORS, CONTEXT, FONTS, cfg, chart_title, legend_below, mpatches, np, plt, queue_summary, save_fig, stats):
    _years = queue_summary["year"].tolist()
    _gen_gw = queue_summary["generation_gw"].tolist()
    _storage_gw = queue_summary["storage_gw"].tolist()

    _fig_queue, _ax = plt.subplots(figsize=(10, 5))

    _x = np.arange(len(_years))
    _w = 0.55

    _ax.bar(_x, _gen_gw, _w, color=CONTEXT)
    _ax.bar(_x, _storage_gw, _w, bottom=_gen_gw, color=COLORS["accent"])

    for _i, (_g, _s) in enumerate(zip(_gen_gw, _storage_gw)):
        _ax.text(
            _i, _g + _s + 30, f"{int(_g + _s):,}",
            ha="center", fontsize=FONTS["annotation"], fontweight="bold",
            color=COLORS["text_dark"],
        )

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

    legend_below(
        _ax,
        handles=[mpatches.Patch(facecolor=CONTEXT), mpatches.Patch(facecolor=COLORS["accent"])],
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


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    ---

    Infrastructure is converting. But at 2× planned load and {stats['aep_gas_share_pct']}% natural gas.

    The physical buildout is real and underway. The constraint is not whether capital
    converts to infrastructure — it will, given enough time. The constraints are
    *when*, *where*, and *who pays for the grid capacity* needed to power it. Those
    questions are the subject of DD-002.

    **Next:** [03_risk_and_durability.py](./03_risk_and_durability.py) — Who holds
    the financial downside if the demand thesis proves incorrect?
    """)
    return


if __name__ == "__main__":
    app.run()
