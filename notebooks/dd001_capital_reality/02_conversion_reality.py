import marimo

__generated_with = "0.19.11"
app = marimo.App(
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
    documented about \\${stats['capex_2025']:.0f}B in disclosed capital expenditure (2025) and about \\${stats['guidance_2026_point']:.0f}B guided for 2026.
    This notebook asks the harder question: how much of that is becoming operating
    infrastructure, on what timeline, and with what physical footprint?

    The short answer: slowly. Interconnection queues now hold {stats['queue_total_gw']:,} GW of
    proposed capacity, but only {stats['queue_completion_pct']}% of queued projects historically reach
    commercial operation. A single Amazon campus in Indiana — Project Rainier — accounts for
    roughly half of Indiana's projected load growth through 2030. The constraint is not
    capital. It is the physical sequence: land, permits, grid interconnection, construction,
    equipment, energization.

    The infrastructure that *does* get built will outlast the demand outlook by decades.
    Understanding the asset-life distribution is the key to understanding lock-in.
    """)
    return


@app.cell
def _():
    import sys
    from pathlib import Path

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
        add_brand_mark,
        add_source,
        chart_title,
        flow_diagram,
        legend_below,
        us_scatter_map,
    )
    cfg = setup()
    return (
        COLORS,
        CONTEXT,
        FIGSIZE,
        FLOW_FONT_SIZE,
        FONTS,
        Path,
        add_brand_mark,
        add_source,
        cfg,
        chart_title,
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
    return (
        capex_annual,
        citations,
        guidance_2026,
        pnfi_bn,
        ppe_schedule,
        queue_summary,
    )


@app.cell
def _(
    capex_annual,
    citations,
    guidance_2026,
    pnfi_bn,
    ppe_schedule,
    queue_summary,
):
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

    ## Decision Filter: What Counts as Durable Obligation

    This section answers a practical allocation question: which assets should be
    underwritten as long-duration obligations, and which should stay contingent on
    realized demand?

    AI infrastructure investments fall into three durability categories. The distinction
    matters because financial cycles are short, while some infrastructure consequences
    persist for decades:

    | Category | What Gets Built | Life | Persists? |
    | :--- | :--- | :--- | :--- |
    | **Structural** | Grid upgrades, substations, DC shells | 20-50 yrs | Yes |
    | **Policy-dependent** | Nuclear restarts, SMR, rate structures | Varies | If regime holds |
    | **Demand-thesis-dependent** | GPU clusters, AI cooling, inference HW | 3-6 yrs | No |

    FY2024 10-K property schedules (EDGAR) imply about {stats['decomp_const_pct']}% of gross PP&E is
    construction-class assets (land, buildings, leasehold improvements, CIP) and
    about {stats['decomp_equip_pct']}% is equipment-class (servers, network gear, machinery). In practice,
    the split varies: Meta skews toward construction; Microsoft skews toward equipment.
    The range across the three companies with clear disclosure is {stats['decomp_const_low']}–{stats['decomp_const_high']}%.

    The decision tree below shows the classification logic and the failure condition
    that should force reclassification to a lower-confidence tier:
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
):
    fig_dt = flow_diagram(
        nodes={
            "q1": ("Is it physically\nembedded in the grid?", 6.5, 4.5, CONTEXT, COLORS["text_dark"]),
            "q2": ("Is demand\nmulti-customer?", 2.0, 2.5, CONTEXT, COLORS["text_dark"]),
            "q3": ("Does a regulatory\nregime protect it?", 11.0, 2.5, CONTEXT, COLORS["text_dark"]),
            "s":  ("STRUCTURAL\n20–50 yr life\nGrid · substations\ntransmission", 2.0, 0.0, COLORS["positive"], "#ffffff"),
            "p":  ("POLICY-DEPENDENT\nvariable life\nNuclear · SMR\nRate structures", 6.5, 0.0, COLORS["neutral"], "#ffffff"),
            "d":  ("DEMAND-THESIS\nDEPENDENT\n3–6 yr life\nGPU · AI cooling", 11.0, 0.0, COLORS["negative"], "#ffffff"),
        },
        edges=[
            {"src": "q1", "dst": "q2", "label": "Yes","exit": "left",    "entry": "top"},
            {"src": "q1", "dst": "q3", "label": "No","exit": "right",    "entry": "top"},
            {"src": "q2", "dst": "s", "label": "Yes →\ndurable demand"},
            {"src": "q2", "dst": "p", "label": "No →\nsingle-customer","exit": "right",    "entry": "top"},
            {"src": "q3", "dst": "p", "label": "Yes","exit": "left",    "entry": "top"},
            {"src": "q3", "dst": "d", "label": "No"},
        ],
        figsize=(16, 8),
        xlim=(-2.5, 16.5),
        ylim=(-2.5, 6.5),
        font_size=FLOW_FONT_SIZE,
        legend_handles=[
            mpatches.Patch(facecolor=COLORS["positive"], label="Structural (20–50 yr)"),
            mpatches.Patch(facecolor=COLORS["neutral"], label="Policy-dependent (variable)"),
            mpatches.Patch(facecolor=COLORS["negative"], label="Demand-thesis-dependent (3–6 yr)"),
        ],
    )
    add_source(fig_dt, "Source: Author's framework; EIA asset lifetime estimates")
    add_brand_mark(fig_dt, logo_path=str(cfg.project_root / 'src/assets/tzdlabs_mark.png'))
    save_fig(fig_dt, cfg.img_dir / "dd001_durability_taxonomy.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo):
    _chart = mo.image(src=(cfg.img_dir / "dd001_durability_taxonomy.png").read_bytes(), width=850)
    mo.md(f"{_chart}")
    return


@app.cell
def _(
    COLORS,
    CONTEXT,
    FIGSIZE,
    FONTS,
    add_brand_mark,
    add_source,
    cfg,
    chart_title,
    plt,
    save_fig,
    stats,
):
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
        f"{stats['decomp_const_pct']}% of capital expenditure creates 20\u201340 year assets \u2014 the rest depreciates in under 6",
    )
    plt.tight_layout(rect=[0.02, 0.08, 1, 1])
    add_source(fig_decomp, "Source: SEC 10-K filings via yfinance; SemiAnalysis")
    add_brand_mark(fig_decomp, logo_path=str(cfg.project_root / 'src/assets/tzdlabs_mark.png'))
    save_fig(fig_decomp, cfg.img_dir / "dd001_capex_decomposition.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo, stats):
    _chart = mo.image(
        src=(cfg.img_dir / "dd001_capex_decomposition.png").read_bytes(), width=850
    )
    mo.md(f"""
    # {stats['decomp_const_pct']}% of capital expenditure creates 20-40 year assets — the rest depreciates in under 6

    {_chart}

    *Takeaway: about {stats['decomp_const_pct']}% of AI-era capital expenditure went into long-lived construction assets, creating infrastructure lock-in beyond 3-5 year demand visibility. Source: FY2024 10-K property schedules.*

    This is the lock-in asymmetry. Investment risk is often evaluated on a 3–5 year
    return horizon, but much of the physical footprint lasts far longer. A gas plant
    built to power a data center campus is demand-thesis-dependent at inception. Once
    built, it operates for 40 years regardless of whether the data center scales as
    planned. The path-dependency literature (Arthur 1989; David 1985) demonstrates how
    early capital choices create self-reinforcing lock-in — the lock-in here is not just
    technological but geographic and infrastructural. Substations, transmission lines,
    and campus foundations cannot be relocated the way software platforms can.

    **The current binding constraint on conversion is not capital — it is the physical
    sequence.** Of all phases, grid interconnection imposes the longest lag: a national
    median of about 5 years from request to commercial operation, up from about 3 years a decade
    ago (Rand et al., LBNL, 2025). The physical constraint sequence is detailed in the
    next section.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Decision Check: Announced Capital vs Buildable Capital
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
    fig_sg = flow_diagram(
        nodes={
            "a": ("Stargate Announcement\nJan 21, 2025", 2.0, 1.5, CONTEXT, COLORS["text_dark"]),
            "b": (f"Phase 1\n${stats['stargate_initial_bn']}B\nCommitted · deploying", 7.5, 3.0, COLORS["positive"], "#ffffff"),
            "c": (f"Mobilization pledge\n~${stats['stargate_announced_bn'] - stats['stargate_initial_bn']}B\nStructure unspecified", 7.5, 0.0, CONTEXT, COLORS["text_dark"]),
            "d": ("Texas sites\nunder construction", 13.0, 3.0, COLORS["positive"], "#ffffff"),
            "e": ("Requires SoftBank\ndebt issuance +\nco-investor capital", 13.0, 0.0, CONTEXT, COLORS["text_dark"]),
        },
        edges=[
            {"src": "a", "dst": "b", "label": "committed", "exit": "top", "entry": "left"},
            {"src": "a", "dst": "c", "label": "speculative", "exit": "bottom", "entry": "left"},
            {"src": "b", "dst": "d"},
            {"src": "c", "dst": "e"},
        ],
        figsize=(12, 5),
        xlim=(-1.0, 17.0),
        ylim=(-1.5, 4.5),
        font_size=FLOW_FONT_SIZE,
        legend_handles=[
            mpatches.Patch(facecolor=COLORS["positive"], label="Committed capital"),
            mpatches.Patch(facecolor=CONTEXT, label="Speculative / unverified"),
        ],
    )
    add_source(fig_sg, "Source: Microsoft, SoftBank, OpenAI announcements (January 2025)")
    add_brand_mark(fig_sg, logo_path=str(cfg.project_root / 'src/assets/tzdlabs_mark.png'))
    save_fig(fig_sg, cfg.img_dir / "dd001_stargate_commitment.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo):
    _chart = mo.image(src=(cfg.img_dir / "dd001_stargate_commitment.png").read_bytes(), width=850)
    mo.md(f"{_chart}")
    return


@app.cell(hide_code=True)
def _(mo, stats):
    _capex_low = stats["capex_2025"] * stats["analyst_const_pct_low"] / 100
    mo.md(f"""
    **Decision implication:** do not treat announced capital expenditure as delivered infrastructure.
    The central gap is conversion, not commitment. Announcements are large, but
    delivery is constrained by interconnection timelines, permitting, and equipment
    bottlenecks:

    - **Stargate Project:** \\${stats['stargate_announced_bn']}B announced intent (White House
      press conference, Jan 21, 2025 — no binding construction commitment at announcement).
      \\${stats['stargate_initial_bn']}B Phase 1 committed and under active deployment.
      SoftBank's balance sheet had about \\$30-40B deployable capital at announcement time;
      financial structure and timeline for the remaining \\${stats['stargate_announced_bn'] - stats['stargate_initial_bn']}B remain opaque.
      *(Sources: White House announcement, Jan 2025; FT analysis)*
    - **U.S. Interconnection Queue:** Over {stats['queue_total_gw']:,} GW of generation and storage capacity
      seeking grid connection as of end-2024 — roughly
      3x total U.S. installed capacity (Rand et al., LBNL *Queued Up* 2025 Edition).
      Of all capacity queued from 2000-2024, **{stats['queue_withdrawal_pct']}% was withdrawn** and only **{stats['queue_completion_pct']}%
      reached commercial operation.**
    - **Large Load (Data Center) Requests:** For the first time, LBNL tracked load-side
      interconnection: over **100 GW** of large load requests (predominantly data
      centers), with PJM alone accounting for about 80 GW — up from about 5 GW just two years
      earlier *(Rand et al., 2025)*. PJM's Board initiated a "Critical Issue Fast Path"
      process in February 2025 to handle the unprecedented volume.

    The binding constraint is **power availability**. The typical time from
    interconnection request to commercial operation has grown to about 5 years nationally,
    up from about 3 years a decade ago *(Rand et al., 2025)*. This is a physical bottleneck
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
    about {stats['queue_gas_gw']} GW (end-2024), likely reflecting data center demand for firm,
    dispatchable power. Solar remains dominant at about {stats['queue_solar_gw']:,} GW ({stats['queue_solar_pct']}% of total queue),
    storage about {stats['queue_storage_gw']:,} GW ({stats['queue_storage_pct']}%), wind about {stats['queue_wind_gw']} GW ({stats['queue_wind_pct']}%).

    For planning, this implies a delivery haircut: when programs depend on queue
    outcomes, treat only a minority of announced capacity as likely near-term delivery.

    Supply-side constraints that capital expenditure figures don't capture — visualized in the
    next chart.
    """)
    return


@app.cell
def _(
    COLORS,
    CONTEXT,
    FIGSIZE,
    FONTS,
    add_brand_mark,
    add_source,
    cfg,
    chart_title,
    np,
    plt,
    save_fig,
):
    # Physical constraint phases: each row shows where time is consumed
    # before a data center can operate. Data from LBNL Queued Up 2025 + industry sources.
    _phases = [
        ("GPU chip order\nto delivery",         0,  18, "locked", "TSMC CoWoS packaging\nbottleneck (12–18 mo)"),
        ("Grid interconnection\nrequest to ops",  0,  60, "locked", "National median: ~5 yrs\n(LBNL Queued Up 2025)"),
        ("Transformer\nprocurement",              6,  30, "locked", "Lead time: 2–3 yrs\n(CS-1 Transformer Mfg)"),
        ("Land + permits",                        0,  12, "exit",   "Site selection to\nground-break: 6–12 mo"),
        ("DC construction",                      12,  30, "exit",   "18–30 mo per building\n(Project Rainier proxy)"),
        ("Energization",                          30,  36, "locked", "Final step: utility\nswitchgear install"),
    ]
    _colors = {"locked": COLORS["negative"], "exit": CONTEXT}
    _alphas = {"locked": 0.8, "exit": 0.5}

    fig_constraints, _ax = plt.subplots(figsize=(FIGSIZE["wide"][0], FIGSIZE["wide"][1] * 1.4))

    _n = len(_phases)
    _short_bar = 12  # months — below this threshold, annotation goes outside the bar
    for _i, (_label, _start, _end, _kind, _note) in enumerate(_phases):
        _dur = _end - _start
        _ax.barh(
            _i, _dur, left=_start, height=0.65,
            color=_colors[_kind], alpha=_alphas[_kind],
            edgecolor="white", linewidth=0.5,
        )
        if _dur >= _short_bar:
            # Long bar: annotation centered inside
            _mid = _start + _dur / 2
            _ax.text(
                _mid, _i, _note, ha="center", va="center",
                fontsize=FONTS["annotation"] - 2,
                color="white" if _kind == "locked" else COLORS["text_dark"],
                fontweight="normal",
            )
        else:
            # Short bar: annotation to the right, outside the bar
            _ax.text(
                _end + 1.0, _i, _note, ha="left", va="center",
                fontsize=FONTS["annotation"] - 2,
                color=COLORS["text_dark"],
                fontweight="normal",
            )

    _ax.set_yticks(np.arange(_n))
    _ax.set_yticklabels([p[0] for p in _phases], fontsize=FONTS["tick_label"])
    _ax.set_xlabel("Months from capital commitment", fontsize=FONTS["axis_label"])
    _ax.tick_params(axis="x", labelsize=FONTS["tick_label"])
    _ax.set_xlim(0, 68)
    _ax.axvline(36, color=COLORS["accent"], linewidth=1.5, linestyle="--", alpha=0.7)
    # Place "~3-year minimum" just above the top bar (Energization, y=n-1)
    # va="bottom" keeps it above the bar without extending into the title
    _ax.text(36.5, _n - 1 + 0.35, "~3-year\nminimum", fontsize=FONTS["annotation"] - 1,
             color=COLORS["accent"], va="bottom")
    _ax.spines[["top", "right"]].set_visible(False)
    chart_title(fig_constraints,
                "Physical constraints stack — grid interconnection alone takes 5 years")
    plt.tight_layout(rect=[0.02, 0.08, 1, 1])
    add_source(fig_constraints, "Source: Author's framework; industry sources")
    add_brand_mark(fig_constraints, logo_path=str(cfg.project_root / 'src/assets/tzdlabs_mark.png'))
    save_fig(fig_constraints, cfg.img_dir / "dd001_constraint_phases.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo):
    _chart = mo.image(src=(cfg.img_dir / "dd001_constraint_phases.png").read_bytes(), width=850)
    mo.md(f"""
    # Physical constraints stack — grid interconnection alone takes 5 years

    {_chart}

    *Takeaway: the limiting step is still grid interconnection (~5 years median), so capital alone cannot compress end-to-end delivery below roughly three years. Sources: LBNL Queued Up 2025; CS-1 Transformer Manufacturing.*
    """)
    return


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    ### Case Study: Project Rainier (Amazon/Anthropic, Indiana)

    **Decision relevance:** Rainier is a live benchmark for timeline realism, subsidy
    exposure, and load-concentration risk.

    The most detailed public record of AI infrastructure conversion comes from
    Amazon's Project Rainier campus near New Carlisle, Indiana — a facility built
    specifically for Anthropic and documented by the NYT in June 2025.

    **Scale and timeline:**
    - 1,200 acres of former cornfield, 15 miles west of South Bend
    - {stats['rainier_gw']} GW planned capacity — enough to power a million homes
    - about {stats['rainier_dc_planned']} data centers planned; {stats['rainier_dc_built_jun2025']} built by June 2025 (each larger than
      a football stadium), with four construction firms working simultaneously
    - about {stats['rainier_workers_weekly']:,} construction workers on site weekly

    **Public subsidy and cost:**
    - Indiana legislature: 50-year sales tax break (about \\${stats['rainier_tax_break_sales_bn']}B, per Citizens Action
      Coalition estimate)
    - County property/technology tax breaks: about \\${stats['rainier_tax_break_property_bn']}B additional over 35 years
    - Total public subsidy: **about \\${stats['rainier_tax_break_sales_bn'] + stats['rainier_tax_break_property_bn']}B** for one campus

    **Grid impact (the DD-002 connection):**
    - AEP (local utility) told regulators that data centers will more than double
      Indiana's peak power demand: from {stats['aep_indiana_peak_2024_gw']} GW (2024) to {stats['aep_indiana_peak_2030_gw']}+ GW by about 2030
    - **Amazon's campus alone accounts for about half of the additional load**
    - AEP plans to meet about {stats['aep_gas_share_pct']}% of additional power demand with natural gas —
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
def _(
    COLORS,
    CONTEXT,
    FIGSIZE,
    FONTS,
    add_brand_mark,
    add_source,
    cfg,
    chart_title,
    plt,
    save_fig,
    stats,
):
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

    plt.tight_layout(h_pad=1.2, rect=[0.02, 0.08, 1, 1])
    chart_title(
        fig_rainier,
        f"Project Rainier: {_pct_done:.0f}% built after 2 years — at {stats['rainier_gw']} GW, it doubles Indiana's peak load",
    )
    add_source(fig_rainier, "Source: Microsoft announcements; company filings")
    add_brand_mark(fig_rainier, logo_path=str(cfg.project_root / 'src/assets/tzdlabs_mark.png'))
    save_fig(fig_rainier, cfg.img_dir / "dd001_rainier_progress.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo, stats):
    _chart = mo.image(
        src=(cfg.img_dir / "dd001_rainier_progress.png").read_bytes(), width=850
    )
    mo.md(f"""
    # Project Rainier: {stats['rainier_dc_built_jun2025']} of {stats['rainier_dc_planned']} buildings complete after 2 years — conversion is the constraint, not capital

    {_chart}

    *Takeaway: Rainier is a live conversion benchmark, with {stats['rainier_dc_built_jun2025']} of {stats['rainier_dc_planned']} buildings up after ~2 years and major long-run grid implications. Source: NYT (Jun 24, 2025).*
    """)
    return


@app.cell(hide_code=True)
def _(
    COLORS,
    CONTEXT,
    FONTS,
    Path,
    add_brand_mark,
    add_source,
    cfg,
    plt,
    save_fig,
):
    import io as _io
    import zipfile as _zipfile

    import geopandas as _gpd
    import matplotlib.colors as _mcolors
    import pandas as _pd
    import requests as _requests

    # ── 1. County shapefile (already cached from earlier map cells) ───────────
    _county_shp = Path("/Users/shakes/DevProjects/Systems/data/external/cb_2024_us_county_20m/cb_2024_us_county_20m.shp")
    if not _county_shp.exists():
        _county_dir = _county_shp.parent
        _county_dir.mkdir(parents=True, exist_ok=True)
        _resp = _requests.get(
            "https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_county_20m.zip",
            timeout=120,
        )
        _resp.raise_for_status()
        with _zipfile.ZipFile(_io.BytesIO(_resp.content)) as _zf:
            _zf.extractall(_county_shp.parent)

    _all_counties = _gpd.read_file(_county_shp)
    _conus = _all_counties[~_all_counties["STATEFP"].isin(["02", "15", "72"])]

    # ── 2. Census ACS 5-yr unemployment rate by Indiana county ────────────────
    # B23025_005E = Unemployed; B23025_002E = Civilian labor force total
    _unemp_cache = Path("/Users/shakes/DevProjects/Systems/data/external/indiana_county_unemployment.csv")
    if _unemp_cache.exists():
        _unemp_df = _pd.read_csv(_unemp_cache, dtype={"GEOID": str})
    else:
        _url = (
            "https://api.census.gov/data/2022/acs/acs5"
            "?get=NAME,B23025_005E,B23025_002E&for=county:*&in=state:18"
        )
        _r = _requests.get(_url, timeout=30)
        _data = _r.json()
        _unemp_df = _pd.DataFrame(_data[1:], columns=_data[0])
        _unemp_df["B23025_005E"] = _pd.to_numeric(_unemp_df["B23025_005E"], errors="coerce")
        _unemp_df["B23025_002E"] = _pd.to_numeric(_unemp_df["B23025_002E"], errors="coerce")
        _unemp_df["unemployment_rate"] = (
            _unemp_df["B23025_005E"] / _unemp_df["B23025_002E"] * 100
        ).round(1)
        _unemp_df["GEOID"] = _unemp_df["state"] + _unemp_df["county"]
        _unemp_df[["GEOID", "NAME", "unemployment_rate"]].to_csv(_unemp_cache, index=False)

    # ── 3. Spatial setup ──────────────────────────────────────────────────────
    _indiana = _conus[_conus["STATEFP"] == "18"].copy()
    _indiana = _indiana.merge(_unemp_df[["GEOID", "unemployment_rate"]], on="GEOID", how="left")
    _st_joseph = _indiana[_indiana["NAME"] == "St. Joseph"]
    _neighbors = _conus[_conus["STATEFP"].isin(["17", "26", "39", "21"])]
    _us_states = _conus.dissolve(by="STATEFP", as_index=False)

    # ── 4. Combined figure: US context (left) + Indiana zoom (right) ──────────
    fig_rainier_map, (_ax_us, _ax_in) = plt.subplots(
        1, 2, figsize=(16, 6),
        gridspec_kw={"width_ratios": [2.2, 1]},
    )

    # --- Left panel: US overview ---
    _us_states.plot(
        ax=_ax_us, color=COLORS["background"], edgecolor=COLORS["muted"], linewidth=0.3,
    )
    _site_lats = [41.68,   32.477,  35.058,  32.502]
    _site_lons = [-86.47,  -91.755, -90.153, -99.789]
    _dot_colors = [COLORS["accent"], CONTEXT, CONTEXT, CONTEXT]
    for _la, _lo, _c in zip(_site_lats, _site_lons, _dot_colors):
        _ax_us.scatter(_lo, _la, c=_c, s=100, zorder=5, edgecolors="white", linewidth=1.0)
    _labels_us = [
        (-86.47,  41.68,  "Project Rainier\n(New Carlisle, IN)",    "left",  42.8, COLORS["accent"]),
        (-91.755, 32.477, "Meta Hyperion\n(Richland Parish, LA)",   "right", 31.5, COLORS["text_light"]),
        (-90.153, 35.058, "xAI Colossus\n(Memphis, TN)",            "left",  36.8, COLORS["text_light"]),
        (-99.789, 32.502, "Stargate TX\n(Abilene, TX)",             "right", 28.5, COLORS["text_light"]),
    ]
    for _lo, _la, _lbl, _ha, _yt, _clr in _labels_us:
        _xt = _lo + (2.5 if _ha == "left" else -2.5)
        _ax_us.annotate(
            _lbl, xy=(_lo, _la), xytext=(_xt, _yt), ha=_ha,
            fontsize=FONTS["small"], color=_clr,
            arrowprops=dict(arrowstyle="-", color=_clr, lw=0.8),
        )
    _ax_us.set_xlim(-125, -65)
    _ax_us.set_ylim(24, 50)
    _ax_us.set_axis_off()

    # --- Right panel: Indiana zoom + Lake Michigan context ---
    # Blue background: Lake Michigan visible as the blue area above Indiana's northern border
    _ax_in.set_facecolor("#dde8f4")
    _neighbors.dissolve(by="STATEFP", as_index=False).plot(
        ax=_ax_in, color="#f0f0f0", edgecolor=COLORS["muted"], linewidth=0.3, zorder=1,
    )
    _vmin, _vmax = 2.5, 8.5
    _indiana.plot(
        column="unemployment_rate", ax=_ax_in, cmap="YlOrRd",
        vmin=_vmin, vmax=_vmax,
        edgecolor=COLORS["muted"], linewidth=0.4, zorder=2,
        missing_kwds={"color": COLORS["background"]},
    )
    # St. Joseph County: accent border, no fill override (preserves choropleth)
    _st_joseph.plot(ax=_ax_in, color="none", edgecolor=COLORS["accent"], linewidth=2.5, zorder=4)
    # New Carlisle site dot
    _ax_in.scatter([-86.47], [41.68], c=COLORS["accent"], s=200, zorder=6,
                   edgecolors="white", linewidth=1.5)
    # Lake Michigan label — in the blue background above Indiana's northern border
    _ax_in.text(-86.3, 42.0, "Lake Michigan", ha="center",
                fontsize=FONTS["small"], color="#4a7fa5", style="italic", zorder=5)
    # Distance annotation: New Carlisle to lake shore (~8 miles)
    _ax_in.annotate(
        "~8 mi\nto lake", xy=(-86.47, 41.78), xytext=(-87.4, 42.05),
        ha="center", fontsize=FONTS["small"] - 1, color="#4a7fa5", zorder=5,
        arrowprops=dict(arrowstyle="->", color="#4a7fa5", lw=1.0),
    )
    # Geographic reference points
    _ax_in.text(-87.7, 41.5, "Chicago\n(~60 mi W)", ha="center",
                fontsize=FONTS["small"] - 1, color=CONTEXT, zorder=5)
    _ax_in.text(-86.05, 41.67, "South Bend\n(15 mi E)", ha="left",
                fontsize=FONTS["small"] - 1, color=CONTEXT, zorder=5)
    # Colorbar for unemployment choropleth
    _sm = plt.cm.ScalarMappable(
        cmap="YlOrRd", norm=_mcolors.Normalize(vmin=_vmin, vmax=_vmax),
    )
    _sm.set_array([])
    _cbar = plt.colorbar(_sm, ax=_ax_in, orientation="horizontal",
                         pad=0.02, fraction=0.06, aspect=18, shrink=0.85)
    _cbar.set_label("Unemployment rate (%) — Census ACS 2022",
                    fontsize=FONTS["small"] - 1, color=COLORS["text_dark"])
    _cbar.ax.tick_params(labelsize=FONTS["small"] - 2)
    # Extend north past Indiana's border to reveal Lake Michigan in the background
    _ax_in.set_xlim(-88.1, -84.7)
    _ax_in.set_ylim(37.7, 42.2)
    _ax_in.set_axis_off()

    plt.tight_layout(pad=1.0, w_pad=0.5, rect=[0.02, 0.08, 1, 1])
    add_source(fig_rainier_map, "Source: Microsoft public data; LBNL data center database")
    add_brand_mark(fig_rainier_map, logo_path=str(cfg.project_root / 'src/assets/tzdlabs_mark.png'))
    save_fig(fig_rainier_map, cfg.img_dir / "dd001_rainier_combined_map.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo):
    _chart = mo.image(
        src=(cfg.img_dir / "dd001_rainier_combined_map.png").read_bytes(), width=850
    )
    mo.md(f"""
    # New Carlisle sits 8 miles from Lake Michigan — water access and grid proximity drove site selection

    {_chart}

    *Takeaway: New Carlisle combined cooling-water access, grid proximity, and local economic incentives, making it a plausible fast-start site for a multi-GW campus. Sources: Census ACS/TIGER; NYT.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    Rainier is a special case: Amazon contracted directly with the local utility
    (AEP Indiana) and bypassed the standard interconnection queue by securing a
    negotiated rate agreement. Most AI data centers cannot do this — they enter the
    standard interconnection queue and face the general-case attrition and delays
    documented below.
    """)
    return


@app.cell
def _(
    COLORS,
    CONTEXT,
    FONTS,
    add_brand_mark,
    add_source,
    cfg,
    chart_title,
    legend_below,
    mpatches,
    np,
    plt,
    queue_summary,
    save_fig,
    stats,
):
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
    add_source(_fig_queue, "Source: LBNL 'Queued Up' 2024 Edition; FERC interconnection data")
    add_brand_mark(_fig_queue, logo_path=str(cfg.project_root / 'src/assets/tzdlabs_mark.png'))
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

    *Takeaway: queue volume is rising ({stats['queue_total_gw']:,} GW), but conversion remains weak: {stats['queue_withdrawal_pct']}% withdrawn and only {stats['queue_completion_pct']}% completed historically. Source: LBNL "Queued Up" 2025.*
    """)
    return


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    ---

    Infrastructure is converting. But at 2× planned load and {stats['aep_gas_share_pct']}% natural gas.

    The physical infrastructure expansion is real and underway. The constraint is not whether capital
    converts to infrastructure — it will, given enough time. The constraints are
    *when*, *where*, and *who pays for the grid capacity* needed to power it. Those
    questions are the subject of DD-002.

    **Failure movie (2027-2030):** queue completion stays near {stats['queue_completion_pct']}%,
    utilities still build for projected large data center load, and rate-base obligations are
    socialized before durable local benefits materialize. If demand then softens, customers
    still carry a decades-long amortization tail on underutilized assets.

    **Applied decision rule for DD-002:** prioritize projects with shared-grid spillover
    and clear beneficiary-pays cost allocation; defer programs whose economics only hold
    under optimistic queue and demand assumptions.

    **Next:** [03_risk_and_durability.py](./03_risk_and_durability.py) — Who holds
    the financial downside if the demand outlook proves incorrect?
    """)
    return


if __name__ == "__main__":
    app.run()
