import marimo

__generated_with = "0.19.11"
app = marimo.App(
    width="compact",
    app_title="DD-001: Risk and Durability",
    css_file="../../src/notebook_theme/custom.css",
    html_head_file="../../src/notebook_theme/head.html",
)


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    # Who Holds the Downside? Risk Distribution in AI Infrastructure

    *Thandolwethu Zwelakhe Dlamini*

    ---

    The previous two notebooks documented what is being spent (about \\${stats["capex_2025"]:.0f}B of capital expenditure in 2025)
    and how slowly it converts to operating infrastructure. This notebook asks the
    distributional question: when long-lived infrastructure outlasts the demand outlook
    that justified it, *who holds the loss*?

    The answer has shifted materially through 2025. The entities best positioned to
    evaluate AI demand — the tech giants — have systematically moved financial exposure
    outward to entities with less visibility into demand trajectories. Special purpose
    vehicles, short-term leases, and concentrated new-cloud-provider dependencies have distributed
    risk to private credit, pension funds, and rural communities — on timescales that
    run decades beyond the companies' exit options.

    """)
    return


@app.cell
def _(mo):
    mo.callout(
        mo.md("""
    **Plain-language glossary**

    - **SPV (special purpose vehicle):** a ring-fenced project entity used to finance one deal.
    - **Neocloud:** a newer cloud provider leasing or borrowing heavily for AI compute capacity.
    - **FERC AD24-11:** a federal inquiry on whether large loads should pay the grid upgrade costs they cause.
    """),
        kind="info",
    )
    return


@app.cell
def _(add_brand_mark, add_source):
    import io
    import sys
    import zipfile

    import marimo as mo

    sys.path.insert(0, str(mo.notebook_dir().parent.parent))
    from pathlib import Path

    import geopandas as gpd
    import matplotlib.lines as mlines
    import matplotlib.patches as mpatches
    import matplotlib.pyplot as plt
    import numpy as np
    import requests

    from src.data.db import query
    from src.notebook import save_fig, setup
    from src.plotting import (
        COLORS,
        CONTEXT,
        FIGSIZE,
        FLOW_FONT_SIZE,
        FONTS,
        add_brand_mark,
        add_rule,
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
        add_rule,
        add_source,
        cfg,
        chart_title,
        flow_diagram,
        gpd,
        io,
        legend_below,
        mlines,
        mo,
        mpatches,
        np,
        plt,
        query,
        requests,
        save_fig,
        us_scatter_map,
        zipfile,
    )


@app.cell
def _(query):
    _cite_raw = query("""
        SELECT key, value FROM energy_data.source_citations
    """)
    citations = dict(zip(_cite_raw["key"], _cite_raw["value"]))
    return (citations,)


@app.cell
def _(citations):
    stats = {
        "capex_2025": 400,  # placeholder — overridden below if data available
        "meta_beignet_financing_bn": int(citations["meta_beignet_financing_bn"]),
        "meta_beignet_exit_year": int(citations["meta_beignet_exit_year"]),
        "beignet_bond_maturity": int(citations["beignet_bond_maturity"]),
        "msft_neocloud_total_bn": int(citations["msft_neocloud_total_bn"]),
        "msft_nebius_deal_bn": int(citations["msft_nebius_deal_bn"]),
        "msft_nscale_deal_bn": int(citations["msft_nscale_deal_bn"]),
        "msft_iren_deal_bn": int(citations["msft_iren_deal_bn"]),
        "meta_beignet_lease_years": int(citations["meta_beignet_lease_years"]),
        "openai_coreweave_commitment_bn": float(
            citations["openai_coreweave_commitment_bn"]
        ),
        "coreweave_interest_rate_pct": int(
            citations["coreweave_interest_rate_pct"]
        ),
        "openai_msft_compute_promise_bn": int(
            citations["openai_msft_compute_promise_bn"]
        ),
        "meta_louisiana_dc_gw": int(citations["meta_louisiana_dc_gw"]),
        "openai_texas_dc_gw": float(citations["openai_texas_dc_gw"]),
        "aep_gas_share_pct": int(citations["aep_gas_share_pct"]),
        "rainier_gw": float(citations["rainier_gw"]),
    }
    # Override capex_2025 from live data if available
    from src.data.db import query as _q

    _capex = _q("""
        SELECT SUM(capex_bn) AS total
        FROM energy_data.hyperscaler_capex
        WHERE date LIKE '2025%'
          AND ticker IN ('MSFT','AMZN','GOOGL','META','ORCL','NVDA')
    """)
    if len(_capex) > 0 and _capex["total"].iloc[0] is not None:
        stats["capex_2025"] = float(_capex["total"].iloc[0])
    return (stats,)


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
    mpatches,
    plt,
    save_fig,
):
    # 2x2 thesis matrix: asset lifetime (x) × demand thesis durability (y)
    # Shows why AI infrastructure sits in the structural risk zone
    _fig_matrix, _ax_m = plt.subplots(figsize=FIGSIZE["square"])

    _quads = [
        # (x, y, fill_color, alpha, label)
        (
            0,
            0,
            CONTEXT,
            0.15,
            "Aligned — Agile\nGPU server leases\nCloud compute contracts",
        ),
        (
            1,
            0,
            COLORS["negative"],
            0.45,  # focus quadrant — more saturated than context quadrants
            "Risk Zone\nAI-dedicated substations\nData center shells\nTransmission upgrades",
        ),
        (0, 1, CONTEXT, 0.1, "Mismatch — Oversized\n(unusual in practice)"),
        (
            1,
            1,
            COLORS["positive"],
            0.18,
            "Aligned — Durable\nBaseload power plants\nTelecom fiber backbone",
        ),
    ]

    for _xi, _yi, _qcolor, _alpha, _label in _quads:
        _ax_m.add_patch(
            mpatches.Rectangle(
                (_xi, _yi), 1, 1, color=_qcolor, alpha=_alpha, zorder=1
            )
        )
        _tc = COLORS["text_dark"]
        _ax_m.text(
            _xi + 0.5,
            _yi + 0.5,
            _label,
            ha="center",
            va="center",
            fontsize=FONTS["annotation"],
            color=_tc,
            zorder=2,
            multialignment="center",
        )

    _ax_m.set_xlim(0, 2)
    _ax_m.set_ylim(0, 2)
    _ax_m.axvline(1, color=CONTEXT, linewidth=0.8, alpha=0.6)
    _ax_m.axhline(1, color=CONTEXT, linewidth=0.8, alpha=0.6)
    _ax_m.set_xticks([0.5, 1.5])
    _ax_m.set_xticklabels(
        ["Short\n(3–5 yr)", "Long\n(25–50 yr)"], fontsize=FONTS["tick_label"]
    )
    _ax_m.set_yticks([0.5, 1.5])
    _ax_m.set_yticklabels(
        ["Short\n(3–5 yr)", "Long\n(20+ yr)"], fontsize=FONTS["tick_label"]
    )
    _ax_m.set_xlabel("Asset Lifetime", fontsize=FONTS["axis_label"])
    _ax_m.set_ylabel("Demand Thesis Durability", fontsize=FONTS["axis_label"])
    _ax_m.spines[["top", "right", "left", "bottom"]].set_visible(False)
    _ax_m.tick_params(left=False, bottom=False)

    chart_title(
        _fig_matrix,
        "AI infrastructure occupies the structural risk zone",
    )
    plt.tight_layout(rect=[0.02, 0.08, 1, 1])
    add_source(_fig_matrix, "Source: Author's risk framework; SEC filings; industry research")
    add_brand_mark(_fig_matrix, logo_path=str(cfg.project_root / 'src/assets/tzdlabs_mark.png'))
    save_fig(_fig_matrix, cfg.img_dir / "dd001_thesis_matrix.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo):
    _chart_matrix = mo.image(
        src=(cfg.img_dir / "dd001_thesis_matrix.png").read_bytes(), width=700
    )
    mo.md(f"""
    # AI infrastructure occupies the structural risk zone — long-lived assets, short demand visibility

    {_chart_matrix}

    *Takeaway: long-lived physical assets are being funded against short demand visibility, which is the core mismatch this notebook tracks.*
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
    cfg,
    chart_title,
    legend_below,
    mpatches,
    np,
    plt,
    save_fig,
    stats,
):
    # Risk Exposure Timeline — horizontal Gantt
    # Each row: one risk bearer; bar spans their exposure window
    # Color encodes exit optionality: CONTEXT = can exit; COLORS["negative"] = locked in
    _entities = [
        ("Tech giants\n(Meta, MSFT)", 2025, 2030, "exit"),
        ("Neoclouds\n(CoreWeave, Nebius)", 2025, 2035, "locked"),
        (
            "Private credit\n(Pimco, Blue Owl)",
            2025,
            stats["beignet_bond_maturity"],
            "locked",
        ),
        ("Pension funds\n& endowments", 2025, 2055, "locked"),
        ("Rural communities\n(Indiana, Louisiana…)", 2025, 2070, "permanent"),
    ]
    _color_map = {
        "exit": CONTEXT,
        "locked": COLORS["negative"],
        "permanent": COLORS["negative"],
    }
    _alpha_map = {"exit": 0.6, "locked": 0.8, "permanent": 1.0}

    fig_risk, _ax = plt.subplots(
        figsize=(FIGSIZE["wide"][0], FIGSIZE["wide"][1] * 0.9)
    )

    _y_positions = np.arange(len(_entities))
    _bar_height = 0.55

    for _i, (_label, _start, _end, _kind) in enumerate(_entities):
        _clr = _color_map[_kind]
        _alpha = _alpha_map[_kind]
        _ax.barh(
            _i,
            _end - _start,
            left=_start,
            height=_bar_height,
            color=_clr,
            alpha=_alpha,
            edgecolor="white",
            linewidth=0.5,
        )
        # End-year annotation inside or just past bar
        _ax.text(
            _end + 0.3,
            _i,
            str(_end) if _kind != "permanent" else "2070+",
            va="center",
            ha="left",
            fontsize=FONTS["annotation"] - 1,
            color=_clr if _kind != "exit" else COLORS["text_dark"],
            fontweight="bold",
        )
        # Duration annotation inside bar (if wide enough)
        _dur = _end - _start
        if _dur >= 8:
            _ax.text(
                _start + _dur / 2,
                _i,
                f"{_dur} yr",
                va="center",
                ha="center",
                fontsize=FONTS["annotation"] - 1,
                color="white" if _kind != "exit" else COLORS["text_dark"],
            )

    # "Today" marker
    _today = 2026
    _ax.axvline(
        _today,
        color=COLORS["accent"],
        linewidth=2,
        linestyle="-",
        alpha=0.8,
        zorder=5,
    )
    _ax.text(
        _today + 0.2,
        len(_entities) - 0.1,
        "Today",
        fontsize=FONTS["annotation"],
        color=COLORS["accent"],
        fontweight="bold",
        va="top",
    )

    # Meta exit window annotation — in the gap between Tech giants (y=0) and
    # Neoclouds (y=1). Bar height=0.55 → bars span ±0.275 from their centre;
    # safe text zone is y ∈ [0.3, 0.72]. Arrow tip at top edge of Tech giants bar.
    _ax.annotate(
        f"Meta can\nexit ~{stats['meta_beignet_exit_year']}",
        xy=(stats["meta_beignet_exit_year"], 0.28),
        xytext=(stats["meta_beignet_exit_year"] + 1.5, 0.52),
        fontsize=FONTS["annotation"] - 1,
        color=CONTEXT,
        arrowprops=dict(arrowstyle="->", color=CONTEXT, linewidth=1),
        ha="left",
        va="center",
    )

    _ax.set_yticks(_y_positions)
    _ax.set_yticklabels(
        [e[0] for e in _entities],
        fontsize=FONTS["tick_label"],
    )
    _ax.set_xlabel("Year", fontsize=FONTS["axis_label"])
    _ax.tick_params(axis="x", labelsize=FONTS["tick_label"])
    _ax.set_xlim(2024, 2076)
    _ax.set_ylim(-0.4, len(_entities) - 0.2)
    _ax.spines[["top", "right"]].set_visible(False)

    legend_below(
        _ax,
        handles=[
            mpatches.Patch(facecolor=CONTEXT, alpha=0.6, label="Can exit"),
            mpatches.Patch(
                facecolor=COLORS["negative"], alpha=0.9, label="Locked in"
            ),
        ],
        labels=["Can exit (3-5 yr leases)", "Locked in (debt / bond maturity)"],
        ncol=2,
    )
    chart_title(
        fig_risk,
        "The further from the investment decision, the longer the exposure",
    )
    plt.tight_layout(rect=[0.02, 0.08, 1, 1])
    add_rule(_ax)
    add_source(fig_risk, "Source: SEC filings; CRS reports; author's analysis")
    add_brand_mark(fig_risk, logo_path=str(cfg.project_root / 'src/assets/tzdlabs_mark.png'))
    save_fig(fig_risk, cfg.img_dir / "dd001_risk_exposure_timeline.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo):
    _chart = mo.image(
        src=(cfg.img_dir / "dd001_risk_exposure_timeline.png").read_bytes(),
        width=850,
    )
    mo.md(f"""
    # The further from the investment decision, the longer the exposure

    {_chart}

    *Takeaway: exposure duration extends as risk moves downstream: tech giants can exit in years, while creditors and communities remain exposed for decades. Sources: NYT; CoreWeave S-1/A; S&P Global Ratings.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ---

    ## Decision Application: Who Should Hold Long-Duration Liability

    Three structural mechanisms are moving financial exposure from tech giants, who
    have the most visibility into AI demand, to counterparties who have the least.
    The policy and contracting question is whether that transfer should be permitted
    by default.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ### 1. Special Purpose Vehicles (SPVs): The Beignet Pattern
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
    fig_spv = flow_diagram(
        nodes={
            "meta":  ("Meta\n(Tech Giant)",                                1.5,  1.0, CONTEXT,              COLORS["text_dark"]),
            "spv":   ("Beignet \nInvestor \nLLC (SPV)",                       6.0,  1.0, COLORS["neutral"],    "#ffffff"),
            "bo":    ("Blue Owl \nCapital\n80% of financing",               9.5,  1.0, COLORS["neutral"],    "#ffffff"),
            "pimco": ("Pimco \nBlackRock\nbond underwriters",             15.0,  1.0, COLORS["neutral"],    "#ffffff"),
            "inst":  ("Pension Funds\nEndowments · Insurers",             15.0, -0.6, COLORS["negative"],   "#ffffff"),
            "dc":    (f"Louisiana Data Center\n2 GW — ${stats['meta_beignet_financing_bn']}B project",
                       1.5, -0.6, COLORS["background"], COLORS["text_dark"]),
        },
        edges=[
            {"src": "meta",  "dst": "spv",   "label": f"${stats['meta_beignet_financing_bn']}B \narrangement"},
            {"src": "spv",   "dst": "bo"},
            {"src": "bo",    "dst": "pimco", "label": "bonds sold to"},
            {"src": "pimco", "dst": "inst"},
            {"src": "spv",   "dst": "dc",   "label": "builds & owns",  "dashed": True, "exit": "bottom",    "entry": "right"},
            {"src": "meta",  "dst": "dc",
             "label": f"{stats['meta_beignet_lease_years']}-yr leases  ·  exit ~{stats['meta_beignet_exit_year']}",
             "dashed": True},
            {"src": "inst",  "dst": "spv",
             "label": f"bonds locked to {stats['beignet_bond_maturity']}",
             "dashed": True,  "color": COLORS["negative"], "exit": "left",    "entry": "bottom"},
        ],
        figsize=(16, 5),
        xlim=(-2, 19),
        ylim=(-1.4, 1.8),
        font_size=FLOW_FONT_SIZE,
        legend_handles=[
            mpatches.Patch(fc=CONTEXT,              label="Can exit (tech giant)"),
            mpatches.Patch(fc=COLORS["neutral"],    label="Mechanism (SPV / credit)"),
            mpatches.Patch(fc=COLORS["negative"],   label="Locked in (bondholders)"),
            mpatches.Patch(fc=COLORS["background"], ec=CONTEXT, lw=1.2, label="Physical asset"),
        ],
    )
    add_source(fig_spv, "Source: SEC filings; CoreWeave S-1; project finance documents")
    add_brand_mark(fig_spv, logo_path=str(cfg.project_root / 'src/assets/tzdlabs_mark.png'))
    save_fig(fig_spv, cfg.img_dir / "dd001_spv_chain.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo):
    _chart = mo.image(src=(cfg.img_dir / "dd001_spv_chain.png").read_bytes(), width=850)
    mo.md(f"{_chart}")
    return


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    **Applied implication:** this structure keeps short-duration optionality with the
    decision-maker and pushes long-duration downside to outside capital.

    Meta created Beignet Investor LLC and worked with Blue Owl Capital to borrow
    about \\${stats["meta_beignet_financing_bn"]}B for the project. Blue Owl provided 80% of the financing; Pimco
    sold bonds maturing in **{stats["beignet_bond_maturity"]}** to its clients — insurers, pension funds,
    endowments, and financial advisers. Meta agreed to "rent" the facility through
    a series of {stats["meta_beignet_lease_years"]}-year leases, classifying the arrangement as operating cost
    rather than debt.

    **The risk asymmetry:** Meta can walk away as early as {stats["meta_beignet_exit_year"]}. Bondholders
    are committed through {stats["beignet_bond_maturity"]}. A Columbia Business School accounting
    professor drew explicit parallels to the off-balance-sheet vehicles that preceded
    the dot-com bust *(NYT, Dec 2025)*.

    The pattern is not unique to Meta. The same dynamic plays out geographically across
    every major AI campus: the entity that decided to build retains exit options measured
    in years; the community where it was built cannot exit at all.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # AI data centers land in specific communities — and those communities hold the risk longest
    """)
    return


@app.cell(hide_code=True)
def _(
    COLORS,
    CONTEXT,
    FONTS,
    add_brand_mark,
    add_source,
    cfg,
    mlines,
    save_fig,
    us_scatter_map,
):
    # US overview: major AI data center sites, color-coded by risk bearer.
    # Color = who holds the long-term exposure.
    # Size = approximate GW capacity.
    _sites = [
        # (name, lat, lon, gw, risk_category)
        # Meta Richland Parish, LA — community/ratepayer bears grid cost; SPV locks in
        ("Meta\nRichland Parish, LA", 32.48, -91.75, 2.0, "community"),
        # Amazon Project Rainier, New Carlisle, IN — grid cost socialized via AEP
        ("Amazon Rainier\nNew Carlisle, IN", 41.69, -86.48, 2.2, "community"),
        # OpenAI Stargate, Abilene, TX — Texas ERCOT, behind-the-meter solar mix
        ("OpenAI Stargate\nAbilene, TX", 32.44, -99.74, 1.2, "ambiguous"),
        # xAI Colossus, Memphis, TN — behind-the-meter generators; grid impact disputed
        ("xAI Colossus\nMemphis, TN", 35.06, -90.15, 1.0, "btm"),
    ]
    _color_map = {
        "community": COLORS["negative"],   # community/ratepayers hold long-term exposure
        "btm": COLORS["neutral"],          # behind-the-meter; minimal direct grid cost
        "ambiguous": CONTEXT,              # unclear or split liability allocation
    }
    _lats    = [s[1] for s in _sites]
    _lons    = [s[2] for s in _sites]
    _sizes   = [s[3] * 120 for s in _sites]   # scale: 1 GW → size 120
    _colors  = [_color_map[s[4]] for s in _sites]

    _legend_handles = [
        mlines.Line2D(
            [0], [0], marker="o", color="w",
            markerfacecolor=COLORS["negative"], markersize=10,
            label="Community / ratepayers hold long-term exposure",
        ),
        mlines.Line2D(
            [0], [0], marker="o", color="w",
            markerfacecolor=CONTEXT, markersize=10,
            label="Liability allocation unclear or contested",
        ),
        mlines.Line2D(
            [0], [0], marker="o", color="w",
            markerfacecolor=COLORS["neutral"], markersize=10,
            label="Behind-the-meter (minimal direct grid cost to community)",
        ),
    ]

    fig_us_map = us_scatter_map(
        lats=_lats,
        lons=_lons,
        colors=_colors,
        sizes=_sizes,
        title="AI data centers land in specific communities — and those communities hold the risk longest",
        legend_handles=_legend_handles,
    )

    # Add site labels directly on the map
    _ax_us = fig_us_map.axes[0]
    _label_offsets = {
        "Meta\nRichland Parish, LA":        (-4.0,  1.5),   # west-northwest of the point
        "Amazon Rainier\nNew Carlisle, IN": ( 1.2,  0.8),   # east-northeast
        "OpenAI Stargate\nAbilene, TX":     (-5.0, -1.8),   # southwest
        "xAI Colossus\nMemphis, TN":        ( 2.5,  2.0),   # northeast, clear of Meta label
    }
    for _name, _lat, _lon, _gw, _cat in _sites:
        _dx, _dy = _label_offsets[_name]
        _ax_us.annotate(
            _name,
            xy=(_lon, _lat),
            xytext=(_lon + _dx, _lat + _dy),
            fontsize=FONTS["small"] - 1,
            color=_color_map[_cat],
            ha="center",
            va="center",
            arrowprops=dict(arrowstyle="-", color=_color_map[_cat], linewidth=0.8),
        )

    add_source(fig_us_map, "Source: AWS, Meta, Google public infrastructure announcements")
    add_brand_mark(fig_us_map, logo_path=str(cfg.project_root / 'src/assets/tzdlabs_mark.png'))
    save_fig(fig_us_map, cfg.img_dir / "dd001_louisiana_us_overview.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo):
    _chart = mo.image(
        src=(cfg.img_dir / "dd001_louisiana_us_overview.png").read_bytes(),
        width=850,
    )
    mo.md(f"""
    # AI data centers land in specific communities — and those communities hold the risk longest

    {_chart}

    *Takeaway: most mapped sites place long-run exposure on communities or ratepayers rather than the original demand decision-makers. Sources: NYT; CoreWeave S-1/A; datacentermap.com.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Richland Parish, Louisiana, financed the facility Meta can leave — and cannot leave itself
    """)
    return


@app.cell(hide_code=True)
def _(
    COLORS,
    FONTS,
    Path,
    add_brand_mark,
    add_source,
    cfg,
    gpd,
    io,
    plt,
    requests,
    save_fig,
    zipfile,
):
    # Louisiana parish zoom: highlight Richland Parish where Meta's DC sits.
    # Downloads Census county shapefile on first run; cached to data/external/.
    _county_url = "https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_county_20m.zip"
    _county_dir = Path("/Users/shakes/DevProjects/Systems/data/external/cb_2024_us_county_20m")
    _county_shp = _county_dir / "cb_2024_us_county_20m.shp"
    if not _county_shp.exists():
        _county_dir.mkdir(parents=True, exist_ok=True)
        _resp = requests.get(_county_url, timeout=120)
        _resp.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(_resp.content)) as _zf:
            _zf.extractall(_county_dir)

    _all_counties = gpd.read_file(_county_shp)
    _louisiana    = _all_counties[_all_counties["STATEFP"] == "22"]
    _richland     = _louisiana[_louisiana["NAME"] == "Richland"]

    fig_la, _ax_la = plt.subplots(figsize=(10, 8))

    # All parishes — muted background
    _louisiana.plot(
        ax=_ax_la,
        color=COLORS["background"],
        edgecolor=COLORS["muted"],
        linewidth=0.7,
    )
    # Richland Parish highlighted
    _richland.plot(
        ax=_ax_la,
        color=COLORS["negative"],
        edgecolor=COLORS["text_dark"],
        linewidth=1.8,
        alpha=0.75,
    )

    # Facility scatter point
    _dc_lon, _dc_lat = -91.75, 32.48
    _ax_la.scatter(
        [_dc_lon], [_dc_lat],
        s=200,
        color=COLORS["accent"],
        edgecolors="white",
        linewidth=1.2,
        zorder=5,
    )

    # Annotation: point from the east side to avoid overlap with the highlighted parish
    _ax_la.annotate(
        "Meta Richland Parish DC\n2 GW  ·  $10B project\nFinanced via Beignet SPV\n→ Blue Owl → Pimco",
        xy=(_dc_lon, _dc_lat),
        xytext=(-88.8, 31.6),
        fontsize=FONTS["annotation"] - 1,
        color=COLORS["text_dark"],
        ha="left",
        va="top",
        arrowprops=dict(
            arrowstyle="->",
            color=COLORS["text_dark"],
            linewidth=1.0,
            connectionstyle="arc3,rad=-0.2",
        ),
    )

    # SPV chain inset (lower-left corner)
    _ax_la.text(
        0.02, 0.02,
        "Richland Parish SPV chain:\nMeta → Beignet LLC → Blue Owl → Pimco → pension funds",
        transform=_ax_la.transAxes,
        fontsize=FONTS["small"],
        color=COLORS["text_light"],
        va="bottom",
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="none", alpha=0.8),
    )

    _ax_la.set_axis_off()
    plt.tight_layout(rect=[0.02, 0.08, 1, 1])
    add_source(fig_la, "Source: Louisiana Economic Development; company announcements")
    add_brand_mark(fig_la, logo_path=str(cfg.project_root / 'src/assets/tzdlabs_mark.png'))
    save_fig(fig_la, cfg.img_dir / "dd001_louisiana_parish_zoom.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo):
    _chart = mo.image(
        src=(cfg.img_dir / "dd001_louisiana_parish_zoom.png").read_bytes(),
        width=700,
    )
    mo.md(f"""
    # Richland Parish, Louisiana, financed the facility Meta can leave — and cannot leave itself

    {_chart}

    *Takeaway: Richland Parish illustrates the asymmetry: Meta has earlier exit optionality, while local grid and tax commitments persist. Sources: Louisiana Economic Development; NYT.*
    """)
    return


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    ### 2. Neocloud Leases

    **Applied implication:** short-term Big Tech leases transfer long-tail risk to
    the communities where infrastructure is physically built — not primarily to the
    neoclouds, which are informed participants who priced the tenant-concentration
    risk before signing.

    Microsoft signed over \\${stats["msft_neocloud_total_bn"]}B in 3-5 year data center leases in a single
    quarter (Sep–Nov 2025): Nebius (\\${stats["msft_nebius_deal_bn"]}B) near Mäntsälä, Finland; Nscale
    (\\${stats["msft_nscale_deal_bn"]}B) in Rennesøy, Norway; Iren (\\${stats["msft_iren_deal_bn"]}B) in Childress, Texas
    and Prince George, British Columbia; Lambda via third-party colocation (no
    owned-facility exposure). Each neocloud accepted the 3-to-5-year lease structure
    knowingly — it is the market standard, and the alternative is no revenue at all.

    The communities where these facilities sit made no equivalent calculation.
    Childress County, Texas added significant grid load from IREN's campus; Rennesøy
    built energy infrastructure for Nscale's Norwegian campus; the local grid near
    Mäntsälä was upgraded to support Nebius's Finnish campus. Their exposure runs the
    full life of the physical infrastructure — twenty to fifty years — while
    Microsoft's contractual obligation ends in three to five.

    *Note on sourcing: individual company locations are confirmed from primary filings
    (see Research Evidence section below). The specific Sep–Nov 2025 Microsoft deal
    set as a group, and the reported total of \\${stats["msft_neocloud_total_bn"]}B, comes from NYT
    reporting (Weise & Tan, Dec 15, 2025) and has not been independently confirmed
    from SEC or company filings. Use with appropriate caveat.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ### 3. Downstream Concentration: The CoreWeave Chain

    SPVs and neocloud leases both let Big Tech companies *offload* balance sheet exposure —
    they are downstream risk layering mechanisms. CoreWeave represents the opposite:
    an independent intermediary that has *absorbed* the exposure directly, building
    capacity on its own balance sheet with concentrated customer and supply risk.
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
    fig_cw = flow_diagram(
        nodes={
            "msft":   ("Microsoft\n~62% of CoreWeave\n2024 revenue",  2.0,  1.5, CONTEXT,            COLORS["text_dark"]),
            "openai": ("OpenAI",                                       2.0, -1.5, CONTEXT,            COLORS["text_dark"]),
            "cw":     ("CoreWeave\n(largest neocloud)",                8.0,  0.0, COLORS["negative"], "#ffffff"),
            "gpu":    ("Nvidia GPU Clusters\nH100 / H200 / B200",     14.0,  0.0, COLORS["neutral"],  "#ffffff"),
        },
        edges=[
            {"src": "msft",   "dst": "cw",     "label": "dominant customer", "exit": "right",    "entry": "top"},
            {"src": "openai", "dst": "cw",
             "label": f"up to ${stats['openai_coreweave_commitment_bn']:.0f}B \ncommitted", "exit": "top",    "entry": "left"},
            {"src": "openai", "dst": "msft",
             "label": f"${stats['openai_msft_compute_promise_bn']}B \ncompute \npromise",
             "curve":-0.5,"exit": "left",    "entry": "bottom"},
            {"src": "cw",     "dst": "gpu",
             "label": f"{stats['coreweave_interest_rate_pct']}%+ \nborrowing \nrate"},
            {"src": "cw",     "dst": "openai",
             "label": "viability depends on\nOpenAI growth",
             "dashed": True, "color": COLORS["negative"], "exit": "bottom",    "entry": "right"},
        ],
        figsize=(12, 6),
        xlim=(-1, 17),
        ylim=(-3.0, 3.0),
        font_size=FLOW_FONT_SIZE,
        legend_handles=[
            mpatches.Patch(fc=CONTEXT,            label="Can exit / dominant (Big Tech cloud company)"),
            mpatches.Patch(fc=COLORS["negative"], label="Exposed (neocloud)"),
            mpatches.Patch(fc=COLORS["neutral"],  label="Collateral (GPU assets)"),
        ],
    )
    add_source(fig_cw, "Source: CoreWeave S-1 (March 2025); SEC filings")
    add_brand_mark(fig_cw, logo_path=str(cfg.project_root / 'src/assets/tzdlabs_mark.png'))
    save_fig(fig_cw, cfg.img_dir / "dd001_coreweave_chain.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo):
    _chart = mo.image(src=(cfg.img_dir / "dd001_coreweave_chain.png").read_bytes(), width=850)
    mo.md(f"{_chart}")
    return


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    **Decision recommendation:** align liability with control. When the load decision
    is private and optional, upgrade cost responsibility should not be permanently socialized.

    CoreWeave borrowed billions at {stats["coreweave_interest_rate_pct"]}%+ interest rates to build capacity
    that OpenAI committed to purchase (up to \\${stats["openai_coreweave_commitment_bn"]}B). Microsoft is
    CoreWeave's dominant customer — about 62% of 2024 revenue *(CoreWeave S-1/A, March 2025,
    SEC EDGAR CIK 0001956029, Table of Remaining Performance Obligations)*. OpenAI
    separately committed to route \\${stats["openai_msft_compute_promise_bn"]}B in computing through
    Microsoft, creating a chain: **CoreWeave → OpenAI → Microsoft**.

    CoreWeave's viability depends on OpenAI's growth, which depends on consumer and
    enterprise adoption of AI products that haven't yet generated returns matching
    the infrastructure investment.

    ---

    ### The Directional Implication

    **The entities best positioned to evaluate AI demand are systematically reducing
    their exposure, while entities with less visibility are absorbing it.**

    | Risk bearer | Mechanism | Exposure window | Visibility into AI demand |
    | :--- | :--- | :--- | :--- |
    | Tech giants (Meta, MSFT) | SPVs, short-term leases | 3-5 years (can exit) | **High** |
    | Neoclouds (CoreWeave, Nebius) | Debt-funded capacity | 10-20 years | Medium |
    | Private credit / bondholders | Bond purchases | 20-25 years | **Low** |
    | Pension funds / endowments | Bond portfolios | Indefinite | **None** |
    | Rural communities | Tax incentives, grid load | **Permanent** | **None** |

    **Applied rule:** where visibility is lowest and exposure is longest, require
    stronger collateral, direct assignment, and exit-cost recovery up front.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ---

    ### The Regulatory Lever: FERC AD24-11

    In plain terms: regulators are deciding whether data centers pay their own
    upgrade bill, or whether everyone shares it through rates.

    The question of who holds the loss is not only a private market question — it is
    being actively decided by regulators. FERC docket AD24-11 (Notice of Inquiry,
    opened May 2024) asks whether large-load customers like AI data centers should
    pay for the transmission upgrades they trigger, or whether those costs are
    socialized across all ratepayers. The two outcome paths lead to fundamentally
    different loss distributions.
    """)
    return


@app.cell(hide_code=True)
def _(COLORS, CONTEXT, FLOW_FONT_SIZE, add_brand_mark, add_source, cfg, flow_diagram, mpatches, save_fig):
    fig_ferc = flow_diagram(
        nodes={
            "ferc": ("FERC AD24-11\nNotice of Inquiry\nMay 2024 · pending",             8.0,  3.5, CONTEXT,              COLORS["text_dark"]),
            "pub":  ("Public-benefit\nclassification",                                   3.0,  2.0, COLORS["neutral"],    "#ffffff"),
            "ben":  ("Beneficiary-pays\nclassification",                                13.0,  2.0, COLORS["neutral"],    "#ffffff"),
            "d":    ("Ratepayers absorb\nstranded costs\nvia tariff",                    1.0,  0.5, COLORS["negative"],   "#ffffff"),
            "e":    ("Hyperscalers\nprotected from\ndirect cost",                        5.0,  0.5, CONTEXT,              COLORS["text_dark"]),
            "f":    ("Hyperscalers pay\ntransmission\nupgrade costs",                   11.0,  0.5, COLORS["positive"],   "#ffffff"),
            "g":    ("Existing ratepayers\nprotected",                                  15.0,  0.5, CONTEXT,              COLORS["text_dark"]),
            "h":    ("Risk stays with\ncommunities\n& utilities",                        1.0, -1.0, COLORS["negative"],   "#ffffff"),
            "i":    ("Risk stays with\nthe decision-makers",                            11.0, -1.0, COLORS["positive"],   "#ffffff"),
        },
        edges=[
            {"src": "ferc", "dst": "pub", "exit": "left",    "entry": "top"},
            {"src": "ferc", "dst": "ben", "exit": "right",    "entry": "top"},
            {"src": "pub",  "dst": "d"},
            {"src": "pub",  "dst": "e"},
            {"src": "ben",  "dst": "f"},
            {"src": "ben",  "dst": "g"},
            {"src": "d",    "dst": "h"},
            {"src": "f",    "dst": "i"},
        ],
        figsize=(16, 7),
        xlim=(-1.5, 18.5),
        ylim=(-2.5, 5.0),
        font_size=FLOW_FONT_SIZE,
        legend_handles=[
            mpatches.Patch(fc=CONTEXT,              label="Open / pending (no final rule)"),
            mpatches.Patch(fc=COLORS["neutral"],    label="Classification path"),
            mpatches.Patch(fc=COLORS["negative"],   label="Risk to communities / ratepayers"),
            mpatches.Patch(fc=COLORS["positive"],   label="Risk to decision-makers"),
        ],
    )
    add_source(fig_ferc, "Source: FERC Order 2023; EIA data; author's analysis")
    add_brand_mark(fig_ferc, logo_path=str(cfg.project_root / 'src/assets/tzdlabs_mark.png'))
    save_fig(fig_ferc, cfg.img_dir / "dd001_ferc_fork.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo):
    _chart = mo.image(src=(cfg.img_dir / "dd001_ferc_fork.png").read_bytes(), width=850)
    mo.md(f"{_chart}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    FERC AD24-11 is a Notice of Inquiry — it opens a comment period, not a rulemaking.
    No Final Rule has been issued. FERC Order 2023 (July 2023) governs *generator*
    interconnection reform and does not apply to large-load data center interconnection.
    Cost allocation for Rainier-scale load additions remains an open regulatory question.

    *Sources: NYT, "How Tech's Biggest Companies Are Offloading the Risks of the
    A.I. Boom," Dec 15, 2025 (Weise & Tan); CoreWeave S-1/A, March 2025 (SEC EDGAR
    CIK 0001956029); FERC AD24-11 Notice of Inquiry, May 2024 (ferc.gov eLibrary).*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ---

    ## Research Evidence: Observable Article Sources

    This section is the research companion for
    [`observable/src/dd001-risk.md`](../../observable/src/dd001-risk.md).
    Every claim in the published article should trace to a row here.
    Verification status: ✅ confirmed from primary filing · ⚠️ estimated or
    from secondary reporting · ❌ not independently confirmed.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ### Neocloud Community Locations

    The Observable article names specific communities where each neocloud's
    infrastructure is built. Source documentation:

    | Company | Location | Verification | Primary Source |
    | :--- | :--- | :--- | :--- |
    | **IREN** (formerly Iris Energy) | Childress, TX | ✅ | IREN FY2025 Annual Report (ASX: IDA); Nasdaq: IREN 20-F. Childress campus confirmed in "Operations" section. |
    | **IREN** | Prince George, BC | ✅ | IREN FY2025 Annual Report (ASX: IDA). Prince George campus confirmed, ~40 MW operational. |
    | **Nebius Group** | Mäntsälä, Finland | ✅ | Nebius Group 6-K filings (Nasdaq: NBIS). EU-North1 data center campus in Mäntsälä (60 km east of Helsinki) confirmed. |
    | **Nscale** | Rennesøy, Norway | ✅ | Nscale press releases and company disclosures. Norwegian campus at Rennesøy, Rogaland county, near Stavanger. |
    | **Lambda Labs** | Colocation (no owned facilities) | ✅ | Lambda infrastructure documentation. Lambda operates through third-party colocation; does not own data center shells. |

    **Verification priority:** Before publishing the Observable article, pull IREN's
    most recent 20-F from SEC EDGAR (CIK search: "Iris Energy") and verify Childress
    campus MW capacity. Pull Nebius Group's most recent 6-K and confirm Mäntsälä
    operational status.
    """)
    return


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    ### Microsoft Neocloud Deal Amounts

    | Claim | Amount | Verification | Source |
    | :--- | :--- | :--- | :--- |
    | Microsoft–Nebius lease | ${stats["msft_nebius_deal_bn"]}B | ⚠️ | NYT Dec 15 2025 (Weise & Tan); Nebius press release Oct 2025 |
    | Microsoft–Nscale lease | ${stats["msft_nscale_deal_bn"]}B | ⚠️ | NYT Dec 15 2025 (Weise & Tan); Nscale announcement |
    | Microsoft–IREN lease | ${stats["msft_iren_deal_bn"]}B | ⚠️ | NYT Dec 15 2025 (Weise & Tan); IREN ASX announcement |
    | Microsoft–Lambda lease | (amount not disclosed) | ⚠️ | NYT Dec 15 2025 (Weise & Tan) |
    | Total (Sep–Nov 2025) | ${stats["msft_neocloud_total_bn"]}B | ⚠️ | NYT Dec 15 2025; not confirmed from SEC filings |

    **Caveat:** The specific Sep–Nov 2025 deal set as a group, and the
    ${stats["msft_neocloud_total_bn"]}B total, have not been independently confirmed from Microsoft
    SEC filings or MSFT 10-Q. Individual deal announcements (Nebius, Nscale, IREN)
    are confirmed from company press releases. Aggregation and timing are from
    NYT reporting.

    **What to verify:** Check Microsoft's most recent 10-K/10-Q (SEC EDGAR CIK 789019)
    for operating lease commitments by counterparty. Check IREN's ASX announcements
    for the Microsoft deal announcement date and amount.

    ---

    ### Community Grid Exposure Claims

    | Claim | Verification | Source |
    | :--- | :--- | :--- |
    | Childress County added "significant grid load" from IREN | ⚠️ | Check AEP Texas interconnection queue for Childress County load additions. ERCOT queue data at ercot.com. IREN FY2025 Annual Report states MW capacity at Childress campus. |
    | Rennesøy "built energy infrastructure" for Nscale | ⚠️ | Nscale press releases; Statnett (Norwegian TSO) interconnection data at statnett.no. |
    | Mäntsälä municipalities: local grid upgraded for Nebius | ⚠️ | Fingrid (Finnish TSO) grid data; Nebius 6-K for MW capacity. Finnish data center association (FICDC) for any municipal commitments. |
    | Lambda colocation: no community-specific grid exposure | ✅ | Lambda Labs infrastructure documentation confirms colocation model. |

    **Research note:** The Mäntsälä claim is the weakest — municipality involvement
    in Fingrid interconnection is standard infrastructure process, not a special
    commitment. The Observable prose uses "local grid was upgraded to support
    Nebius's Finnish campus," which is the safe formulation.
    """)
    return


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    ### Beignet SPV Structure

    | Claim | Verification | Source |
    | :--- | :--- | :--- |
    | Meta created Beignet Investor LLC | ✅ | Delaware corporate registry; NYT Dec 15 2025 |
    | Blue Owl Capital provided 80% of financing | ✅ | NYT Dec 15 2025 (Weise & Tan); Blue Owl Capital disclosures |
    | Pimco and BlackRock sold bonds | ✅ | NYT Dec 15 2025 |
    | Bond maturity: {stats["beignet_bond_maturity"]} | ⚠️ | NYT Dec 15 2025; not independently confirmed from SEC bond filing |
    | Meta exit option: ~{stats["meta_beignet_exit_year"]} | ⚠️ | NYT Dec 15 2025; derived from {stats["meta_beignet_lease_years"]}-year lease start date |
    | Columbia professor drew dot-com parallels | ✅ | NYT Dec 15 2025 (Weise & Tan) |
    | Richland Parish, Louisiana: {stats["meta_louisiana_dc_gw"]} GW facility | ✅ | Meta press release; Louisiana Economic Development |

    **Verify before publishing:** Pull the Beignet Investor LLC bond prospectus from SEC
    EDGAR (search: "Beignet Investor") to confirm maturity date and Meta lease terms.

    ---

    ### FERC AD24-11

    | Claim | Verification | Source |
    | :--- | :--- | :--- |
    | FERC docket AD24-11 opened May 2024 | ✅ | ferc.gov eLibrary, Docket AD24-11 |
    | No Final Rule issued | ✅ | FERC eLibrary as of Feb 2026 — verify current status |
    | FERC Order 2023 does not apply to large-load interconnection | ✅ | FERC Order 2023 (July 2023) — generator interconnection only |

    ---

    ### CoreWeave Chain

    | Claim | Verification | Source |
    | :--- | :--- | :--- |
    | Microsoft = ~62% of CoreWeave 2024 revenue | ✅ | CoreWeave S-1/A March 2025 (SEC EDGAR CIK 0001956029), Table of Remaining Performance Obligations |
    | OpenAI committed up to ${stats["openai_coreweave_commitment_bn"]:.0f}B | ✅ | CoreWeave S-1/A; OpenAI press release |
    | CoreWeave borrowing rate: {stats["coreweave_interest_rate_pct"]}%+ | ✅ | S&P credit analysis; CoreWeave S-1/A |
    | OpenAI committed ${stats["openai_msft_compute_promise_bn"]}B through Microsoft | ✅ | OpenAI–Microsoft partnership announcement |
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


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    ---

    ## Immediate Decisions Before DD-002

    The three notebooks in this series establish a decision sequence:
    capital is real and accelerating, conversion is physically constrained, and downside
    is drifting toward entities furthest from the original investment decision.

    Before expanding infrastructure investment, the next deep dives should test three decision gates:

    - **Gate 1 (DD-002):** does incremental generation create shared grid benefit or
      private bypass? Rainier-scale growth (utility planning at {stats["aep_gas_share_pct"]}% gas) is the live test.
    - **Gate 2 (DD-003):** is labor supply keeping pace, or do electrician and regional
      hiring bottlenecks convert approved projects into idle capital?
    - **Gate 3 (CS-4):** are transformer and materials constraints widening conversion lag
      and shifting cost burden into long-duration public liabilities?

    If these gates fail, the recommendation is to stage long-lived commitments and
    tighten beneficiary-pays rules rather than continue socialized expansion by default.

    ---

    *Sources: SEC EDGAR (10-K/10-Q filings via yfinance, through Q4 2025),
    Yahoo Finance (market caps, Feb 2026), FRED (BEA PNFI series, Q2 2025 SAAR),
    Sequoia Capital ("The \\$600B Question," Sep 2024), CreditSights (AI capital expenditure
    estimates, Jan-Feb 2026), earnings call transcripts (Jan-Feb 2026),
    Rand et al., "Queued Up: Characteristics of Power Plants Seeking Transmission
    Interconnection — As of the End of 2024," LBNL, April 2025 (emp.lbl.gov/queues),
    Palmer et al., "Reforming Electricity Interconnection," Resources for the Future, 2024.
    NYT, "At Amazon's Biggest Data Center, Everything Is Supersized for A.I.,"
    Jun 24, 2025 (Karen Weise & Cade Metz).
    NYT, "What Exactly Are A.I. Companies Trying to Build? Here's a Guide,"
    Sep 16, 2025 (Cade Metz & Karen Weise).
    NYT, "How Tech's Biggest Companies Are Offloading the Risks of the A.I. Boom,"
    Dec 15, 2025 (Karen Weise & Eli Tan).
    CoreWeave S-1/A, March 2025 (SEC EDGAR CIK 0001956029).
    FERC AD24-11 Notice of Inquiry, May 2024 (ferc.gov eLibrary).*
    """)
    return


if __name__ == "__main__":
    app.run()
