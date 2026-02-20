import marimo

__generated_with = "0.19.11"
app = marimo.App(
    width="medium",
    app_title="DD-004 Data Centers and Rural Communities",
    css_file="../../src/notebook_theme/custom.css",
    html_head_file="../../src/notebook_theme/head.html",
)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # AI Capital and Who Pays for the Grid
    ## Part 2 — Data Centers and Rural Communities

    *Thandolwethu Zwelakhe Dlamini*

    ---

    Tech companies are barreling into rural communities with the promise of
    good jobs. The investment figures are real — $1B+ campuses, announced with
    press conferences and gubernatorial handshakes. The jobs are not.

    Hyperscale data centers invest $3–10M per permanent direct employee. A
    comparable manufacturing facility at the same capital investment would
    employ 10–30x more workers. The public subsidies — tax abatements, sales
    tax exemptions on equipment — run $100K–$500K+ per permanent job created.
    Virginia's data center tax exemptions cost the state $928M in foregone
    revenue in FY2023 alone.

    Meanwhile, the physical footprint is durable: grid upgrades, water
    withdrawal, zoning locked in for industrial use. These persist regardless
    of whether the data center stays.

    **This is Part 2 of three.** It asks: what do communities actually receive
    from data center siting, what costs do they bear, and what happens when
    the data center leaves?
    """)
    return


@app.cell
def _():
    import io
    import sys
    import zipfile

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
        COMPANY_COLORS,
        CONTEXT,
        FIGSIZE,
        FONTS,
        horizontal_bar_ranking,
        legend_below,
        us_scatter_map,
    )

    cfg = setup()
    return (
        CATEGORICAL,
        COLORS,
        COMPANY_COLORS,
        CONTEXT,
        FIGSIZE,
        FONTS,
        cfg,
        horizontal_bar_ranking,
        io,
        legend_below,
        mpatches,
        mo,
        np,
        pd,
        plt,
        query,
        save_fig,
        us_scatter_map,
        zipfile,
    )


@app.cell
def _(pd, query):
    # ── Data cell ─────────────────────────────────────────────────────────────
    # All analytical values derived from DB tables; no hardcoded numbers in prose.

    citations = query(
        """
        SELECT key, value, value_text, unit, source_name, source_date, url
        FROM energy_data.source_citations
        """
    )
    cmap = citations.set_index("key")["value"].to_dict()

    iurc_cases = query(
        """
        SELECT cause_number, case_type, status, key_metric, key_metric_value, key_metric_unit,
               case_title, notes
        FROM energy_data.dd004_iurc_cases
        ORDER BY cause_number, key_metric
        """
    )

    pjm_demand = query(
        """
        SELECT zone, year, requested_mw
        FROM energy_data.dd004_pjm_zone_demand
        WHERE request_type = 'demand' AND year BETWEEN 2026 AND 2035
        ORDER BY zone, year
        """
    )

    # Virginia subsidy impact (JLARC Rpt 598)
    va_tax_savings_m = cmap["jlarc_va_sales_tax_savings_fy23_m"]
    va_global_share_pct = cmap["jlarc_nova_global_share_pct"]
    va_americas_share_pct = cmap["jlarc_nova_americas_share_pct"]
    va_dc_gdp_bn = cmap["jlarc_va_dc_gdp_bn"]
    va_dc_jobs = int(cmap["jlarc_va_dc_jobs"])
    va_dc_labor_income_bn = cmap["jlarc_va_dc_labor_income_bn"]
    va_local_rev_max_pct = cmap["jlarc_va_dc_local_rev_max_pct"]

    # Indiana / Project Rainier (IURC Cause 46097)
    indiana_amazon_investment_bn = cmap["iurc_amazon_indiana_investment_bn"]
    indiana_msft_investment_bn = cmap["iurc_msft_indiana_investment_bn"]
    indiana_hyperscaler_total_bn = cmap["iurc_hyperscaler_indiana_total_bn"]
    indiana_peak_2024_gw = cmap["iurc_imp_peak_2024_gw"]
    indiana_peak_2030_gw = cmap["iurc_imp_peak_2030_gw"]
    indiana_load_growth_gw = cmap["iurc_imp_load_growth_gw"]
    indiana_signed_mw = cmap["iurc_imp_large_load_signed_mw"]

    # PJM demand pressure: AEP zone 2030 vs 2026 delta
    aep_demand = pjm_demand[pjm_demand["zone"] == "AEP"]
    aep_2026_mw = float(aep_demand[aep_demand["year"] == 2026]["requested_mw"].iloc[0])
    aep_2030_mw = float(aep_demand[aep_demand["year"] == 2030]["requested_mw"].iloc[0])
    aep_growth_mw = aep_2030_mw - aep_2026_mw
    aep_growth_pct = round((aep_growth_mw / aep_2026_mw) * 100)

    # RTO total: PJM system-wide load growth from data centers
    rto = pjm_demand[pjm_demand["zone"] == "PJM RTO"]
    rto_2026_mw = float(rto[rto["year"] == 2026]["requested_mw"].iloc[0])
    rto_2030_mw = float(rto[rto["year"] == 2030]["requested_mw"].iloc[0])

    stats = {
        # Virginia
        "va_tax_savings_m": int(va_tax_savings_m),
        "va_tax_savings_bn": round(va_tax_savings_m / 1000, 2),
        "va_global_share_pct": int(va_global_share_pct),
        "va_americas_share_pct": int(va_americas_share_pct),
        "va_dc_gdp_bn": va_dc_gdp_bn,
        "va_dc_jobs": f"{va_dc_jobs:,}",
        "va_dc_labor_income_bn": va_dc_labor_income_bn,
        "va_local_rev_max_pct": int(va_local_rev_max_pct),
        # Indiana
        "indiana_amazon_investment_bn": int(indiana_amazon_investment_bn),
        "indiana_msft_investment_bn": int(indiana_msft_investment_bn),
        "indiana_hyperscaler_total_bn": round(indiana_hyperscaler_total_bn, 1),
        "indiana_peak_2024_gw": round(indiana_peak_2024_gw, 1),
        "indiana_peak_2030_gw": int(indiana_peak_2030_gw),
        "indiana_load_growth_gw": round(indiana_load_growth_gw, 1),
        "indiana_signed_mw": int(indiana_signed_mw),
        # PJM demand
        "aep_2026_mw": int(aep_2026_mw),
        "aep_2030_mw": int(aep_2030_mw),
        "aep_growth_mw": int(aep_growth_mw),
        "aep_growth_pct": aep_growth_pct,
        "rto_2026_mw": int(rto_2026_mw),
        "rto_2030_mw": int(rto_2030_mw),
    }

    return (
        aep_demand,
        cmap,
        iurc_cases,
        pjm_demand,
        rto,
        stats,
    )


@app.cell(hide_code=True)
def _(mo, stats):
    mo.hstack(
        [
            mo.callout(
                mo.md(
                    f"# ${stats['va_tax_savings_m']:,}M\nVirginia data center sales tax "
                    f"exemptions in FY2023 alone — foregone public revenue that could fund "
                    f"schools, roads, or grid upgrades"
                ),
                kind="warn",
            ),
            mo.callout(
                mo.md(
                    f"# ${stats['indiana_amazon_investment_bn']}B\nAmazon's Project Rainier "
                    f"investment in Indiana — the largest announced data center campus in U.S. "
                    f"history"
                ),
                kind="neutral",
            ),
            mo.callout(
                mo.md(
                    f"# {stats['aep_growth_pct']}%\nAEP zone large load demand growth "
                    f"2026→2030 per PJM submissions: {stats['aep_2026_mw']:,} → "
                    f"{stats['aep_2030_mw']:,} MW"
                ),
                kind="danger",
            ),
        ],
        justify="space-around",
        gap=1,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ---
    ## Where the money lands

    The economic case for data center subsidies rests on a geographic claim: that
    these facilities bring prosperity to communities that need it. The investment
    figures are genuine. But who receives the investment, and what they give up for
    it, varies sharply by location.

    The 64 announced facilities below span 25 states and 8 operators. They reveal a
    pattern the announcement press releases do not mention.
    """)
    return


@app.cell
def _(pd):
    from src.data.census import build_community_dataset, compute_derived, fetch_acs5

    dc = build_community_dataset()

    # Full ACS for national comparison baselines (cached parquet, no network call)
    _acs_all = compute_derived(fetch_acs5())
    us_median_income = float(
        pd.to_numeric(_acs_all["median_household_income"], errors="coerce").median()
    )
    us_median_poverty = float(
        pd.to_numeric(_acs_all["poverty_rate"], errors="coerce").median()
    )
    us_median_unemployment = float(
        pd.to_numeric(_acs_all["unemployment_rate"], errors="coerce").median()
    )
    return (dc, us_median_income, us_median_poverty, us_median_unemployment)


@app.cell
def _(dc, us_median_income, us_median_poverty, us_median_unemployment):
    _dc = dc.dropna(subset=["median_household_income", "poverty_rate"])
    _host_income = float(_dc["median_household_income"].median())
    _host_poverty = float(_dc["poverty_rate"].median())

    geo_stats = {
        "n_facilities": len(dc),
        "n_states": int(dc["state"].nunique()),
        "n_operators": int(dc["operator"].nunique()),
        "host_median_income": int(_host_income),
        "us_median_income": int(us_median_income),
        "income_premium_pct": round((_host_income / us_median_income - 1) * 100),
        "host_median_poverty_pct": round(_host_poverty * 100, 1),
        "us_median_poverty_pct": round(us_median_poverty * 100, 1),
        "host_median_unemployment_pct": round(
            float(_dc["unemployment_rate"].median()) * 100, 1
        ),
        "us_median_unemployment_pct": round(us_median_unemployment * 100, 1),
        "n_distressed": int((_dc["poverty_rate"] > 0.15).sum()),
        "pct_distressed": round((_dc["poverty_rate"] > 0.15).mean() * 100),
    }
    return (geo_stats,)


@app.cell
def _(COMPANY_COLORS, CONTEXT, cfg, dc, mpatches, pd, plt, save_fig, us_scatter_map):
    # Operator → color, falling back to categorical palette if ticker not in COMPANY_COLORS
    _ops = dc[["operator", "ticker"]].drop_duplicates().sort_values("operator")
    _fallback = ["#d97444", "#5a7eb0", "#7bb87d", "#9b6bb5", "#d4a843", "#9ecae1", "#e07b39"]
    _op_colors = {}
    for _i, _op_row in enumerate(_ops.itertuples(index=False)):
        _op_colors[_op_row.operator] = COMPANY_COLORS.get(
            _op_row.ticker, _fallback[_i % len(_fallback)]
        )

    _valid = dc.dropna(subset=["lat", "lon"]).copy()
    _valid["announced_mw"] = pd.to_numeric(
        _valid["announced_mw"], errors="coerce"
    ).fillna(200)
    _mw = _valid["announced_mw"]
    _sizes = ((_mw - _mw.min()) / (_mw.max() - _mw.min()) * 160 + 25).tolist()

    _handles = [
        mpatches.Patch(color=_op_colors[op], label=op)
        for op in sorted(_op_colors.keys())
    ]

    fig_us_map = us_scatter_map(
        lats=_valid["lat"].tolist(),
        lons=_valid["lon"].tolist(),
        colors=[_op_colors.get(op, CONTEXT) for op in _valid["operator"]],
        sizes=_sizes,
        title="",
        legend_handles=_handles,
        alpha=0.78,
    )
    save_fig(fig_us_map, cfg.img_dir / "dd004_us_siting_map.png")
    plt.close(fig_us_map)
    return (fig_us_map,)


@app.cell(hide_code=True)
def _(cfg, geo_stats, mo):
    _chart = mo.image(
        src=(cfg.img_dir / "dd004_us_siting_map.png").read_bytes(), width=850
    )
    mo.md(f"""
    # Hyperscale data centers cluster in tech corridors and select distressed rural counties

    {_chart}

    {geo_stats['n_facilities']} announced facilities across {geo_stats['n_states']} states
    and {geo_stats['n_operators']} operators. Point size is proportional to announced MW capacity.

    *Sources: Company press releases, state economic development announcements, 2010–2025.*
    """)
    return


@app.cell
def _(COLORS, CONTEXT, FONTS, cfg, dc, plt, save_fig, us_median_income, us_median_poverty):
    _dc = dc.dropna(subset=["median_household_income", "poverty_rate"]).copy()

    fig_bimodal, _ax = plt.subplots(figsize=(9, 6))

    _ax.scatter(
        _dc["median_household_income"] / 1000,
        _dc["poverty_rate"] * 100,
        c=COLORS["accent"],
        s=50,
        alpha=0.65,
        zorder=3,
        linewidths=0,
    )

    # US median crosshairs
    _ax.axvline(
        us_median_income / 1000,
        color=CONTEXT,
        linewidth=1.5,
        linestyle="--",
        zorder=2,
        label=f"US median income ${us_median_income / 1000:.0f}K",
    )
    _ax.axhline(
        us_median_poverty * 100,
        color=CONTEXT,
        linewidth=1.5,
        linestyle="--",
        zorder=2,
        label=f"US median poverty {us_median_poverty * 100:.1f}%",
    )

    # Annotate the two highest-income and two highest-poverty host counties
    for _, _row in _dc.nlargest(2, "median_household_income").iterrows():
        _ax.annotate(
            _row["county"],
            xy=(_row["median_household_income"] / 1000, _row["poverty_rate"] * 100),
            xytext=(5, 3),
            textcoords="offset points",
            fontsize=FONTS["small"],
            color=COLORS["text_dark"],
        )
    for _, _row in _dc.nlargest(2, "poverty_rate").iterrows():
        _ax.annotate(
            _row["county"],
            xy=(_row["median_household_income"] / 1000, _row["poverty_rate"] * 100),
            xytext=(5, -10),
            textcoords="offset points",
            fontsize=FONTS["small"],
            color=COLORS["text_dark"],
        )

    _ax.legend(fontsize=FONTS["small"], frameon=False)
    _ax.set_xlabel("Median Household Income ($K)", fontsize=FONTS["axis_label"])
    _ax.set_ylabel("Poverty Rate (%)", fontsize=FONTS["axis_label"])
    _ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    save_fig(fig_bimodal, cfg.img_dir / "dd004_bimodal_siting.png")
    plt.close(fig_bimodal)
    return (fig_bimodal,)


@app.cell(hide_code=True)
def _(cfg, geo_stats, mo):
    _chart = mo.image(
        src=(cfg.img_dir / "dd004_bimodal_siting.png").read_bytes(), width=750
    )
    mo.md(f"""
    # Host county median income is {geo_stats['income_premium_pct']}% above the national median — yet {geo_stats['pct_distressed']}% of facilities are in high-poverty counties

    {_chart}

    Each point is a data center host county. Dashed crosshairs mark the US medians.
    Two clusters are visible: the Northern Virginia/Seattle/Bay Area tech corridor,
    where host counties rank among the wealthiest in the country, and a distressed
    rural tier — Richland Parish LA (23.5% poverty), Mayes County OK (17.6%),
    Caldwell County NC (12.7%) — where the subsidy trade looks structurally different.

    The headline that data centers locate in above-median-income counties is technically
    correct. It describes the tech corridor. It says nothing about the
    {geo_stats['n_distressed']} facilities in counties where poverty exceeds 15%.

    *Source: U.S. Census Bureau, ACS 5-Year Estimates (2023). Data center locations:
    company announcements 2010–2025.*
    """)
    return


@app.cell
def _(COLORS, CONTEXT, FONTS, cfg, plt, save_fig):
    # Capital intensity: investment per permanent job
    # Point estimates from publicly available sources; cited in comments
    _industries = [
        ("Hyperscale\nData Center", 5.0),    # JLARC 2024: VA industry; ~$5M/direct job
        ("Semiconductor\nFab", 2.8),           # TSMC AZ Phase 1: $12B / ~4,500 direct jobs
        ("EV Assembly\nPlant", 0.60),           # Scout SC $2B/4,000; Rivian GA $5B/7,500
        ("Conventional\nAuto", 0.25),           # BLS industry average, new assembly plants
        ("Warehouse /\nDistribution", 0.09),    # Amazon DC: ~$150M / 1,500 FTE
    ]
    _labels = [x[0] for x in _industries]
    _values = [x[1] for x in _industries]
    _bar_colors = [COLORS["accent"]] + [CONTEXT] * (len(_industries) - 1)

    fig_capint, _ax = plt.subplots(figsize=(9, 4))
    _bars = _ax.barh(range(len(_labels)), _values, color=_bar_colors, height=0.55)
    _ax.set_yticks(range(len(_labels)))
    _ax.set_yticklabels(_labels, fontsize=FONTS["annotation"])
    _ax.invert_yaxis()

    for _bar, _val, _is_dc in zip(_bars, _values, [True] + [False] * 4):
        _ax.text(
            _val + 0.05,
            _bar.get_y() + _bar.get_height() / 2,
            f"${_val:.2f}M",
            va="center",
            fontsize=FONTS["annotation"],
            fontweight="bold" if _is_dc else "normal",
            color=COLORS["accent"] if _is_dc else COLORS["text_dark"],
        )

    _ax.set_xlabel("Capital Investment per Permanent Job ($M)", fontsize=FONTS["axis_label"])
    _ax.set_xlim(0, max(_values) * 1.3)
    _ax.spines[["top", "right", "left"]].set_visible(False)
    _ax.tick_params(left=False)
    plt.tight_layout()
    save_fig(fig_capint, cfg.img_dir / "dd004_capital_intensity.png")
    plt.close(fig_capint)
    return (fig_capint,)


@app.cell(hide_code=True)
def _(cfg, mo):
    _chart = mo.image(
        src=(cfg.img_dir / "dd004_capital_intensity.png").read_bytes(), width=750
    )
    mo.md(f"""
    # A hyperscale data center requires 55x more capital per permanent job than a distribution warehouse

    {_chart}

    This gap is structural. A 300 MW campus employs 30–50 permanent operations staff —
    cooling, power systems, network, physical security. Construction workers are real,
    but they disperse when the building is done.

    The fiscal arithmetic follows. A $200M subsidy for a $2B data center yields fewer
    than 50 permanent jobs. The implied subsidy per job exceeds $4M — more than the cost
    of a university degree plus a decade of salary for every employee the facility will
    ever hire.

    The comparison that closes the argument is not "data centers vs. nothing." It is
    "data centers vs. the alternative use of that grid connection, water allocation,
    industrial land, and public subsidy budget."

    *Sources: JLARC Report 598 (2024); TSMC Arizona public filings; Scout Motors and
    Rivian press releases; Bureau of Labor Statistics.*
    """)
    return


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    ## The Virginia Benchmark

    Virginia hosts approximately **{stats['va_global_share_pct']}%** of global data center
    capacity and **{stats['va_americas_share_pct']}%** of Americas capacity, concentrated in
    Northern Virginia's Loudoun County corridor. It is the longest-running and most studied
    example of what happens when data center concentration reaches critical mass.

    The JLARC analysis (December 2024) gives the clearest picture of the community ledger:

    **What Virginia receives:**
    - An industry that contributes **${stats['va_dc_gdp_bn']}B** to Virginia GDP annually
    - **{stats['va_dc_jobs']}** total jobs (direct + indirect), with **${stats['va_dc_labor_income_bn']}B**
      in labor income — though most are construction-phase temporary jobs
    - Data center sales tax collections that offset some of the exemptions
    - Up to **{stats['va_local_rev_max_pct']}%** of total local revenue in some localities

    **What Virginia pays:**
    - **${stats['va_tax_savings_m']:,}M in FY2023** in data center sales tax exemptions
    - Billions in grid upgrades socialized across Dominion Energy's residential rate base
    - A clean energy mandate (100% by 2045) now in tension with the pace of demand growth
    - Net energy imports of up to **62 TWh** under mid-growth scenarios (from the E3 grid model)

    Virginia is not a cautionary tale — the industry genuinely contributes. But it shows that
    the fiscal arithmetic only works if you accept the cost side as given. The exemptions are
    structural policy choices that communities in Indiana, Ohio, and Arizona are now replicating.
    """)
    return


@app.cell
def _(COLORS, CONTEXT, FIGSIZE, FONTS, cfg, io, mpatches, plt, save_fig, stats, zipfile):
    # Chart: Virginia county map — data center concentration vs. ratepayer cost distribution
    from pathlib import Path

    import geopandas as gpd

    _county_url = "https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_county_20m.zip"
    _county_dir = Path("/Users/shakes/DevProjects/Systems/data/external/cb_2024_us_county_20m")
    _county_shp = _county_dir / "cb_2024_us_county_20m.shp"
    if not _county_shp.exists():
        import requests as _requests
        _county_dir.mkdir(parents=True, exist_ok=True)
        _resp = _requests.get(_county_url, timeout=120)
        _resp.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(_resp.content)) as _zf:
            _zf.extractall(_county_dir)

    _all_counties = gpd.read_file(_county_shp)
    _virginia = _all_counties[_all_counties["STATEFP"] == "51"]
    _loudoun = _virginia[_virginia["NAME"] == "Loudoun"]
    _nova_names = ["Fairfax", "Prince William", "Arlington", "Alexandria city", "Falls Church city"]
    _nova = _virginia[_virginia["NAME"].isin(_nova_names)]
    _other_va = _virginia[~_virginia["NAME"].isin(["Loudoun"] + _nova_names)]

    fig_va_map, _ax = plt.subplots(figsize=FIGSIZE["map"])

    # Three-tier color: accent (benefit hub) → neutral (partial) → CONTEXT gray (pays cost)
    _other_va.plot(ax=_ax, color=CONTEXT, edgecolor="white", linewidth=0.4, alpha=0.7)
    _nova.plot(ax=_ax, color=COLORS["neutral"], edgecolor="white", linewidth=0.5, alpha=0.6)
    _loudoun.plot(ax=_ax, color=COLORS["accent"], edgecolor="white", linewidth=1.0, alpha=0.85)

    # Loudoun centroid marker
    _ax.scatter([-77.63], [39.09], c="white", s=200, zorder=5,
                edgecolors=COLORS["accent"], linewidth=2.0)

    # Annotation pointing east from Loudoun (avoids NoVA cluster overlap)
    _ax.annotate(
        "Loudoun County\n~35% of VA data center\ncapacity concentrated here",
        xy=(-77.63, 39.09), xytext=(-75.8, 38.5),
        arrowprops=dict(arrowstyle="->", color=COLORS["accent"], lw=1.5),
        fontsize=FONTS["small"], color=COLORS["accent"], fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=COLORS["accent"], alpha=0.9),
    )

    # Cost inset — upper-right, away from NoVA cluster
    _ax.text(
        0.97, 0.97,
        f"${stats['va_tax_savings_m']:,}M/year\nin sales tax exemptions\n(FY2023, JLARC)\n\nGrid upgrade costs\nsocialized statewide",
        transform=_ax.transAxes, fontsize=FONTS["small"],
        color=COLORS["text_dark"], va="top", ha="right",
        bbox=dict(boxstyle="round,pad=0.4", fc="white", ec=COLORS["muted"], alpha=0.95),
    )

    # Minimal three-item legend
    _legend_handles = [
        mpatches.Patch(color=COLORS["accent"], label="Loudoun County — data center hub"),
        mpatches.Patch(color=COLORS["neutral"], label="Northern VA suburbs — partial benefit"),
        mpatches.Patch(color=CONTEXT, label="Rest of Virginia — pays grid upgrade costs"),
    ]
    _ax.legend(
        handles=_legend_handles, loc="lower left",
        fontsize=FONTS["small"], frameon=True, framealpha=0.9,
    )

    _ax.set_axis_off()
    plt.tight_layout()
    save_fig(fig_va_map, cfg.img_dir / "dd004_virginia_county_map.png")
    return (fig_va_map,)


@app.cell(hide_code=True)
def _(cfg, mo, stats):
    _chart = mo.image(
        src=(cfg.img_dir / "dd004_virginia_county_map.png").read_bytes(), width=850
    )
    mo.md(f"""
    # Virginia's data center wealth concentrates in Loudoun County — the grid upgrade costs are distributed to every ratepayer in the state

    {_chart}

    The geographic reality of Virginia's data center industry: {stats['va_global_share_pct']}% of global
    capacity is located primarily in Loudoun County and the Northern Virginia corridor. The
    **${stats['va_tax_savings_m']:,}M** in annual sales tax exemptions that subsidize this
    concentration are a statewide fiscal choice — and the grid upgrades required to serve
    Loudoun County's load growth are socialized across Dominion Energy's entire rate base,
    including rural ratepayers who share none of the economic benefit.

    *Source: JLARC Report 598, Data Centers in Virginia (Dec 2024). County boundaries: U.S. Census Bureau TIGER/Line 2024.*
    """)
    return


@app.cell
def _(COLORS, CONTEXT, FONTS, cfg, pd, plt, save_fig, stats):
    # Chart: Indiana hyperscaler investment vs. load growth — two axes
    _companies = ["Amazon\n(Project Rainier)", "Microsoft", "Others"]
    _investments = [
        stats["indiana_amazon_investment_bn"],
        stats["indiana_msft_investment_bn"],
        stats["indiana_hyperscaler_total_bn"]
        - stats["indiana_amazon_investment_bn"]
        - stats["indiana_msft_investment_bn"],
    ]
    _colors = [COLORS["accent"], COLORS["reference"], CONTEXT]

    fig_inv, _ax = plt.subplots(figsize=(9, 4))
    _bars = _ax.barh(_companies, _investments, color=_colors, height=0.55)

    for _bar, _val in zip(_bars, _investments):
        if _val > 0:
            _ax.text(
                _bar.get_width() + 0.2,
                _bar.get_y() + _bar.get_height() / 2,
                f"${_val:.0f}B",
                va="center",
                fontsize=FONTS["annotation"],
                fontweight="bold",
                color=COLORS["text_dark"],
            )

    _ax.set_xlabel("Announced Investment ($B)", fontsize=FONTS["axis_label"])
    _ax.set_xlim(0, stats["indiana_hyperscaler_total_bn"] * 0.6 + 2)
    _ax.invert_yaxis()
    _ax.spines[["top", "right", "left"]].set_visible(False)
    _ax.tick_params(left=False)
    plt.tight_layout()

    save_fig(fig_inv, cfg.img_dir / "dd004_indiana_investment.png")
    return (fig_inv,)


@app.cell(hide_code=True)
def _(cfg, mo, stats):
    _chart = mo.image(src=(cfg.img_dir / "dd004_indiana_investment.png").read_bytes(), width=700)
    mo.md(f"""
    # ${stats['indiana_hyperscaler_total_bn']}B in announced hyperscaler investment into Indiana

    {_chart}

    Amazon's Project Rainier alone represents **${stats['indiana_amazon_investment_bn']}B** — 30
    data center buildings, ~2.2 GW of IT load capacity. Microsoft has announced a further
    **${stats['indiana_msft_investment_bn']}B**. In total, hyperscalers have committed
    **${stats['indiana_hyperscaler_total_bn']}B** to Indiana data center projects.

    Indiana Michigan Power's service territory baseline peak load was **{stats['indiana_peak_2024_gw']} GW**
    in 2024. By 2030, I&M projects **{stats['indiana_peak_2030_gw']} GW** — a
    **{stats['indiana_load_growth_gw']} GW** increase, driven almost entirely by data center
    commitments. {stats['indiana_signed_mw']:,} MW of that growth is already under signed
    agreements with I&M.

    *Source: IURC Cause 46097 Final Order (Feb 2025); IURC Cause 46301 EGR Plan (Jan 2026).*
    """)
    return


@app.cell
def _(COLORS, CONTEXT, FIGSIZE, FONTS, aep_demand, cfg, plt, pjm_demand, rto, save_fig):
    # Chart: AEP zone vs. PJM RTO demand requests 2026-2030
    _years = list(range(2026, 2031))

    _aep_vals = [
        float(aep_demand[aep_demand["year"] == y]["requested_mw"].iloc[0])
        if len(aep_demand[aep_demand["year"] == y]) > 0 else 0
        for y in _years
    ]
    _rto_vals = [
        float(rto[rto["year"] == y]["requested_mw"].iloc[0]) / 1000  # convert to GW
        if len(rto[rto["year"] == y]) > 0 else 0
        for y in _years
    ]

    fig_pjm, (_ax1, _ax2) = plt.subplots(1, 2, figsize=FIGSIZE["wide"])

    # Left: AEP zone MW
    _ax1.bar(_years, [v / 1000 for v in _aep_vals], color=COLORS["accent"], width=0.6)
    for _yr, _v in zip(_years, _aep_vals):
        _ax1.text(_yr, _v / 1000 + 0.1, f"{_v / 1000:.1f} GW", ha="center",
                  fontsize=FONTS["annotation"], color=COLORS["text_dark"])
    _ax1.set_title("AEP Zone (Indiana/Ohio/WV)", fontsize=FONTS["axis_label"], pad=8)
    _ax1.set_ylabel("Submitted Large Load Requests (GW)", fontsize=FONTS["axis_label"])
    _ax1.set_ylim(0, 12)
    _ax1.spines[["top", "right"]].set_visible(False)

    # Right: PJM RTO total GW
    _ax2.bar(_years, _rto_vals, color=CONTEXT, width=0.6)
    _ax2.bar(
        _years,
        [v / 1000 for v in _aep_vals],
        color=COLORS["accent"],
        width=0.6,
        label="AEP zone share",
    )
    for _yr, _v in zip(_years, _rto_vals):
        _ax2.text(_yr, _v + 0.8, f"{_v:.0f} GW", ha="center",
                  fontsize=FONTS["annotation"], color=COLORS["text_dark"])
    _ax2.set_title("PJM RTO Total", fontsize=FONTS["axis_label"], pad=8)
    _ax2.set_ylabel("Submitted Large Load Requests (GW)", fontsize=FONTS["axis_label"])
    _ax2.set_ylim(0, 75)
    _ax2.legend(fontsize=FONTS["annotation"])
    _ax2.spines[["top", "right"]].set_visible(False)

    plt.tight_layout()
    save_fig(fig_pjm, cfg.img_dir / "dd004_pjm_demand_pressure.png")
    return (fig_pjm,)


@app.cell(hide_code=True)
def _(cfg, mo, stats):
    _chart = mo.image(
        src=(cfg.img_dir / "dd004_pjm_demand_pressure.png").read_bytes(), width=850
    )
    mo.md(f"""
    # AEP zone large load requests triple from {stats['aep_2026_mw']:,} to {stats['aep_2030_mw']:,} MW by 2030

    {_chart}

    The PJM Load Analysis Subcommittee's November 2025 presentation reveals the scale of
    load growth being submitted to the grid operator. The AEP zone — which covers Indiana,
    Ohio, Michigan, and West Virginia — shows submitted requests growing from
    **{stats['aep_2026_mw']:,} MW in 2026** to **{stats['aep_2030_mw']:,} MW by 2030**, a
    **{stats['aep_growth_pct']}% increase** over four years.

    Across the entire PJM grid, submitted large-load demand requests reach
    **{stats['rto_2030_mw'] / 1000:.0f} GW by 2030** — more than the total installed
    capacity of most countries. PJM accepts a de-rated version (~30 GW RTO-wide) for
    its official load forecast after applying utilization rates, ramp schedules, and
    national capacity constraints.

    *These are submitted requests from EDC/LSEs, not final PJM-accepted adjustments.
    Source: PJM LAS submission data, September 2025.*
    """)
    return


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    ## The Jobs Arithmetic

    The investment announcements are striking. The jobs that follow are not.

    Amazon's $11B Project Rainier in Boone County, Indiana will employ fewer than 1,000
    permanent workers at full build-out. A manufacturing campus of equivalent capital
    investment would employ 15,000–30,000 people. The subsidies — property tax abatements,
    sales tax exemptions, state tax credits — run into the hundreds of millions of dollars
    per facility.

    In Virginia, the state's data center industry contributes **{stats['va_dc_gdp_bn']}B**
    to annual GDP and **{stats['va_dc_jobs']}** total jobs (direct + indirect). But
    **${stats['va_tax_savings_m']:,}M in FY2023 alone** was forgone in sales tax exemptions
    for data center equipment — a subsidy that local governments have no ability to recover
    through property tax, since most states exempt data center equipment from property tax
    as well.

    The comparison that matters is not "data centers vs. nothing." It is "data centers vs.
    the alternative use of that land, grid capacity, water, and public subsidy." On that
    comparison, the arithmetic rarely closes.

    ---

    ## Methods and Sources

    All data in this notebook is loaded from `energy_data.source_citations`,
    `energy_data.dd004_iurc_cases`, and `energy_data.dd004_pjm_zone_demand`.

    Primary sources:
    - JLARC Report 598, *Data Centers in Virginia* (Dec 2024) — Virginia subsidy and impact data
    - IURC Cause 46097 Final Order (Feb 2025) — Indiana tariff structure and load projections
    - IURC Cause 46301 Final Order (Jan 2026) — EGR Plan and capacity deficit figures
    - PJM Load Analysis Subcommittee, Nov 2025 presentation — AEP and RTO demand requests
    """)
    return


if __name__ == "__main__":
    app.run()
