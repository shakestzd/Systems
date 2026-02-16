import marimo

__generated_with = "0.19.11"
app = marimo.App()


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # AI Capital and Grid Modernization
    ## Part 1 — What's Getting Built

    *Thandolwethu Zwelakhe Dlamini*

    ---

    The largest grid buildout in decades is underway — driven by clean energy
    economics, the IRA, and now accelerated by AI demand. AI companies are
    concentrating capital in specific corridors and compressing timelines, but
    they didn't start the buildout. They are, however, making 40-year energy
    decisions on 3-year demand forecasts. The question is what fuel mix their
    money locks in — and whether anyone else benefits from the infrastructure
    it creates.

    This is Part 1 of three. It asks: **what new generation capacity is being
    driven by AI demand, and is it clean or dirty?**
    """)
    return


@app.cell
def _(BAR_DEFAULTS, COLORS, FIGSIZE, FONTS, FUEL_COLORS, cfg, np, plt, save_fig):
    # Asset lifetime vs AI forecast horizon — the fundamental mismatch
    _techs = [
        "AI demand forecast",
        "Gas peaker (BTM)",
        "Battery storage",
        "Solar PPA",
        "Wind farm",
        "Gas CC (grid)",
        "Nuclear restart",
        "Transmission line",
    ]
    _lifetimes = [3, 25, 25, 30, 30, 35, 50, 50]
    _colors = [
        COLORS["text_dark"],
        FUEL_COLORS["gas_cc"],
        FUEL_COLORS["battery"],
        FUEL_COLORS["solar"],
        FUEL_COLORS["wind"],
        FUEL_COLORS["gas_ct"],
        FUEL_COLORS["nuclear"],
        FUEL_COLORS["hydro"],
    ]

    fig_timeline, _ax = plt.subplots(figsize=FIGSIZE["wide"])
    _y = np.arange(len(_techs))

    for i, (life, c) in enumerate(zip(_lifetimes, _colors)):
        _ax.barh(
            i, life, left=2024, height=0.55, color=c,
            alpha=BAR_DEFAULTS["alpha"], edgecolor=BAR_DEFAULTS["edgecolor"],
        )
        _ax.text(
            2024 + life + 0.5,
            i,
            f"{life} yrs",
            va="center",
            fontsize=FONTS["value_label"],
            fontweight="bold",
        )

    # AI forecast horizon band
    _ax.axvspan(2024, 2027, alpha=0.12, color=COLORS["text_dark"], zorder=0)
    _ax.axvline(2027, color=COLORS["text_dark"], linestyle="--", linewidth=1.5, alpha=0.7)
    _ax.text(
        2025.5,
        -0.8,
        "AI forecast\nhorizon",
        fontsize=FONTS["annotation"],
        color=COLORS["text_light"],
        ha="center",
        fontweight="bold",
    )

    _ax.set_yticks(_y)
    _ax.set_yticklabels(_techs, fontsize=FONTS["tick_label"])
    _ax.set_xlabel("Year", fontsize=FONTS["axis_label"])
    _ax.set_xlim(2022, 2080)
    _ax.invert_yaxis()
    _ax.grid(True, axis="x", linestyle=":", alpha=0.4)
    plt.tight_layout()

    save_fig(fig_timeline, cfg.img_dir / "dd002_asset_timeline.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo):
    _chart = mo.image(
        src=(cfg.img_dir / "dd002_asset_timeline.png").read_bytes(), width=850
    )
    mo.md(
        f"""
    # AI demand forecasts span 3 years — the infrastructure lasts 25-60

    {_chart}

    *Every bar represents a capital decision being made today. The dark band shows
    the AI demand forecast window (~3 years). Everything to the right will still be
    operating long after the demand thesis that funded it is confirmed or refuted.*
    """
    )
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
        BAR_DEFAULTS,
        CATEGORICAL,
        COLORS,
        COMPANY_COLORS,
        FIGSIZE,
        FONTS,
        FUEL_COLORS,
        SCATTER_DEFAULTS,
        company_color,
        fuel_color,
        horizontal_bar_ranking,
        legend_below,
        stacked_bar,
        us_scatter_map,
    )

    cfg = setup()
    return (
        BAR_DEFAULTS,
        CATEGORICAL,
        COLORS,
        COMPANY_COLORS,
        FIGSIZE,
        FONTS,
        FUEL_COLORS,
        SCATTER_DEFAULTS,
        cfg,
        company_color,
        fuel_color,
        horizontal_bar_ranking,
        legend_below,
        mo,
        np,
        pd,
        plt,
        query,
        save_fig,
        stacked_bar,
        us_scatter_map,
    )


@app.cell
def _(pd, query):
    # Load EIA Form 860 generator data from DuckDB
    eia = query(
        """
        SELECT fuel_category, operating_year, state, nameplate_capacity_mw, status,
               latitude, longitude
        FROM energy_data.eia860_generators
        WHERE operating_year IS NOT NULL
          AND nameplate_capacity_mw > 0
        """
    )

    # Load FRED energy price series
    natgas = query(
        """
        SELECT date, value as price
        FROM energy_data.fred_series
        WHERE series_id = 'DHHNGSP'
        ORDER BY date
        """
    )
    natgas["date"] = pd.to_datetime(natgas["date"])
    natgas = natgas.set_index("date")

    elec_ppi = query(
        """
        SELECT date, value as price
        FROM energy_data.fred_series
        WHERE series_id = 'WPU0543'
        ORDER BY date
        """
    )
    elec_ppi["date"] = pd.to_datetime(elec_ppi["date"])
    elec_ppi = elec_ppi.set_index("date")
    return eia, elec_ppi, natgas


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## The Generation Mix Since 2020

    The AI buildout is happening inside a broader energy transition. Since 2020,
    the United States has added more new generation capacity than in any
    comparable period since the post-WWII electrification. The fuel mix of
    that capacity tells us what the grid will look like for the next 30-40 years.
    """)
    return


@app.cell
def _(eia):
    # Filter to additions since 2018 and aggregate by year + fuel category
    _recent = eia[eia["operating_year"] >= 2018].copy()

    # Group and pivot for stacked bar
    _agg = (
        _recent.groupby(["operating_year", "fuel_category"])[
            "nameplate_capacity_mw"
        ]
        .sum()
        .reset_index()
    )
    gen_pivot = _agg.pivot_table(
        index="operating_year",
        columns="fuel_category",
        values="nameplate_capacity_mw",
        aggfunc="sum",
        fill_value=0,
    ).reset_index()

    # Keep major categories, order by total
    major_fuels = [
        "solar",
        "wind",
        "battery",
        "gas_cc",
        "gas_ct",
        "nuclear",
        "hydro",
        "coal",
    ]
    gen_pivot["year"] = gen_pivot["operating_year"].astype(int)
    for col in major_fuels:
        if col not in gen_pivot.columns:
            gen_pivot[col] = 0.0

    # Convert to GW
    for col in major_fuels:
        gen_pivot[col] = gen_pivot[col] / 1000
    return gen_pivot, major_fuels


@app.cell
def _(COLORS, FONTS, FUEL_COLORS, cfg, gen_pivot, major_fuels, save_fig, stacked_bar):
    # Fuel labels for stacked bar (colors from design system)
    _fuel_labels = {
        "solar": "Solar", "wind": "Wind", "battery": "Battery Storage",
        "gas_cc": "Gas (Combined Cycle)", "gas_ct": "Gas (Combustion Turbine)",
        "nuclear": "Nuclear", "hydro": "Hydro", "coal": "Coal",
    }
    _colors = {
        k: {"color": FUEL_COLORS[k], "label": _fuel_labels[k]}
        for k in _fuel_labels
    }

    fig_mix = stacked_bar(
        gen_pivot,
        "year",
        {k: v.copy() for k, v in _colors.items() if k in major_fuels},
        "Solar and battery storage dominate new U.S. generation since 2020",
        ylabel="New Capacity (GW)",
    )

    _ax = fig_mix.axes[0]
    _years_list = gen_pivot["year"].tolist()
    if 2022 in _years_list:
        _ira_idx = _years_list.index(2022)
        _ax.axvline(
            x=_ira_idx + 0.4,
            color=COLORS["text_dark"],
            linestyle="--",
            linewidth=1,
            alpha=0.6,
        )
        _ax.annotate(
            "IRA signed\nAug 2022",
            xy=(_ira_idx + 0.4, _ax.get_ylim()[1] * 0.9),
            fontsize=FONTS["annotation"],
            ha="center",
            bbox=dict(
                boxstyle="round,pad=0.3", fc="white", ec=COLORS["text_dark"], alpha=0.8
            ),
        )

    save_fig(fig_mix, cfg.img_dir / "dd002_generation_mix.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo):
    _mix_chart = mo.image(
        src=(cfg.img_dir / "dd002_generation_mix.png").read_bytes(), width=800
    )
    mo.md(
        f"""
    # Solar and battery storage dominate new U.S. generation since 2020

    {_mix_chart}

    The chart tells a story that contradicts the dominant narrative. Solar is the
    largest single source of new generation capacity since 2020 — not natural gas.
    Battery storage is growing faster than any thermal source. Gas combined cycle
    plants remain significant, but they are a shrinking share of the total.

    A caveat: nameplate capacity overstates solar's energy contribution. A gas
    combined cycle plant typically runs at 55-65% capacity factor versus solar
    at 25-30%, producing roughly twice the energy per installed GW. The chart
    shows what is being built, not how much energy it generates.

    It is also worth noting that most generation additions since 2020 are driven
    by IRA tax credits, state clean energy mandates, and cost competitiveness —
    not AI demand specifically. AI-attributable demand is a growing but still
    minority share of total additions. What AI does is accelerate the timeline
    and concentrate investment geographically.

    This matters for the AI infrastructure thesis because it means the generation
    mix being built to serve data centers is cleaner than the existing grid. The
    question is whether that holds as AI demand accelerates.
    """
    )
    return


@app.cell
def _(FONTS, cfg, eia, legend_below, np, plt, save_fig):
    # Compare nameplate vs energy-equivalent capacity by fuel type since 2020
    _recent = eia[eia["operating_year"] >= 2020].copy()
    _by_fuel = (
        _recent.groupby("fuel_category")["nameplate_capacity_mw"].sum() / 1000
    )

    # Reference capacity factors (EIA national averages)
    _cap_factors = {
        "solar": 0.25,
        "wind": 0.35,
        "gas_cc": 0.57,
        "gas_ct": 0.12,
        "nuclear": 0.93,
    }

    _fuels = ["solar", "wind", "gas_cc", "gas_ct", "nuclear"]
    _labels = ["Solar", "Wind", "Gas CC", "Gas CT", "Nuclear"]
    _nameplate = [_by_fuel.get(f, 0) for f in _fuels]
    _effective = [_by_fuel.get(f, 0) * _cap_factors.get(f, 0.3) for f in _fuels]

    fig_capfactor, _ax = plt.subplots(figsize=(10, 5))
    _x = np.arange(len(_fuels))
    _w = 0.35
    _bars1 = _ax.bar(
        _x - _w / 2, _nameplate, _w, color=FUEL_COLORS["wind"], label="Nameplate Capacity"
    )
    _bars2 = _ax.bar(
        _x + _w / 2,
        _effective,
        _w,
        color=COLORS["accent"],
        label="Energy-Equivalent Capacity",
    )

    for _bar in _bars1:
        _h = _bar.get_height()
        if _h > 0.5:
            _ax.text(
                _bar.get_x() + _bar.get_width() / 2,
                _h + 0.3,
                f"{_h:.1f}",
                ha="center",
                va="bottom",
                fontsize=FONTS["value_label"],
                color=COLORS["text_dark"],
            )
    for _bar in _bars2:
        _h = _bar.get_height()
        if _h > 0.5:
            _ax.text(
                _bar.get_x() + _bar.get_width() / 2,
                _h + 0.3,
                f"{_h:.1f}",
                ha="center",
                va="bottom",
                fontsize=FONTS["value_label"],
                color=COLORS["text_dark"],
            )

    _ax.set_xticks(_x)
    _ax.set_xticklabels(_labels)
    _ax.set_ylabel("GW Added Since 2020", fontsize=FONTS["axis_label"])
    legend_below(_ax)
    plt.tight_layout()

    save_fig(fig_capfactor, cfg.img_dir / "dd002_capacity_factor.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo):
    _cf_chart = mo.image(
        src=(cfg.img_dir / "dd002_capacity_factor.png").read_bytes(), width=800
    )
    mo.md(
        f"""
    # Solar leads in nameplate, but gas CC closes the gap when adjusted for capacity factor

    {_cf_chart}

    The comparison makes the caveat concrete. Solar dominates nameplate additions,
    but when adjusted for capacity factor — the fraction of time a plant actually
    generates at full output — gas combined cycle narrows the gap substantially.
    A single GW of gas CC delivers roughly twice the annual energy of a GW of solar.
    Battery storage is excluded here; its value is in shifting supply timing, not
    raw energy output.
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## The Generation Spectrum

    Not all AI-driven generation is equal. The range runs from dirty shortcuts
    to potentially transformative investments.

    | Strategy | Example | Asset Life | Benefits Grid? | Stranded Asset Risk |
    | :--- | :--- | :--- | :--- | :--- |
    | **Gas peakers (behind-the-meter)** | xAI Colossus, Memphis | 20-30 years | No — bypasses grid entirely | High if emissions rules return |
    | **Grid-connected gas CC** | Utility plants for DC load | 30-40 years | Yes — grid infrastructure built | Moderate — long asset life |
    | **Utility-scale solar + storage** | Standard utility procurement | 25-35 years | Yes — shared grid resource | Low — cost-competitive already |
    | **Corporate renewable PPAs** | Microsoft/Brookfield 10.5GW, Amazon ~30GW | 15-25 years | Depends on structure | Low |
    | **Nuclear restart / SMR** | Microsoft/Constellation, Amazon SMR | 40-60 years | Potentially transformative | Low if technology matures |
    | **Behind-the-meter renewables** | On-site solar + Tesla Megapacks | 25-30 years | No — private infrastructure | Low |

    The xAI case is instructive. When a company builds natural gas turbines on-site
    to power a data center, bypassing the grid entirely, the grid gets nothing — no
    modernization, no spillover, no shared benefit. The regulatory environment
    determines how many companies take this path versus connecting to the grid.

    **Durability analysis:** Gas plants are demand-thesis-dependent at the decision
    point (built because of AI demand forecasts), but structural once built — a
    40-year generating asset operates regardless of whether the data center scales
    as planned. Solar PPAs are structural from day one — they are cost-competitive
    without AI demand. Nuclear restarts are policy-dependent — they require
    favorable NRC treatment and sustained political support.
    """)
    return


@app.cell
def _(FONTS, cfg, plt, save_fig):
    # Generation spectrum: 2D positioning by asset life and grid benefit
    _strategies = [
        {
            "name": "Gas peaker\n(BTM)",
            "life": 25,
            "grid": 0.03,
            "size": 300,
            "color": COLORS["accent"],
        },
        {
            "name": "BTM\nrenewables",
            "life": 27,
            "grid": 0.15,
            "size": 250,
            "color": FUEL_COLORS["battery"],
        },
        {
            "name": "Corporate\nrenewable PPA",
            "life": 20,
            "grid": 0.5,
            "size": 500,
            "color": COLORS["positive"],
        },
        {
            "name": "Grid\ngas CC",
            "life": 35,
            "grid": 0.7,
            "size": 400,
            "color": FUEL_COLORS["gas_ct"],
        },
        {
            "name": "Solar+storage\nPPA",
            "life": 30,
            "grid": 0.8,
            "size": 550,
            "color": FUEL_COLORS["solar"],
        },
        {
            "name": "Nuclear\nrestart / SMR",
            "life": 50,
            "grid": 0.85,
            "size": 200,
            "color": FUEL_COLORS["nuclear"],
        },
    ]

    fig_spectrum, _ax = plt.subplots(figsize=(10, 6))

    for s in _strategies:
        _ax.scatter(
            s["life"],
            s["grid"],
            s=s["size"],
            c=s["color"],
            alpha=0.7,
            edgecolors="white",
            linewidth=1.5,
            zorder=3,
        )
        _offset = (12, 0) if s["life"] < 45 else (-12, 0)
        _ha = "left" if s["life"] < 45 else "right"
        _ax.annotate(
            s["name"],
            (s["life"], s["grid"]),
            textcoords="offset points",
            xytext=_offset,
            fontsize=FONTS["annotation"],
            va="center",
            ha=_ha,
        )

    # Quadrant shading — upper right is the policy target
    _ax.axhspan(
        0.5, 1.05, xmin=0.4, xmax=1.0, alpha=0.06, color=COLORS["positive"], zorder=0
    )
    _ax.axhline(0.5, color=COLORS["muted"], linestyle="--", linewidth=1, alpha=0.6)
    _ax.axvline(30, color=COLORS["muted"], linestyle="--", linewidth=1, alpha=0.6)

    # Quadrant labels
    _ax.text(
        17,
        0.97,
        "Short-lived\nhigh grid benefit",
        fontsize=FONTS["annotation"],
        color=COLORS["reference"],
        ha="left",
        va="top",
    )
    _ax.text(
        56,
        0.97,
        "Long-lived\nhigh grid benefit",
        fontsize=FONTS["annotation"],
        color=COLORS["positive"],
        ha="right",
        va="top",
        fontweight="bold",
    )
    _ax.text(
        17,
        0.03,
        "Short-lived\nno grid benefit",
        fontsize=FONTS["annotation"],
        color=COLORS["reference"],
        ha="left",
        va="bottom",
    )
    _ax.text(
        56,
        0.03,
        "Long-lived\nno grid benefit",
        fontsize=FONTS["annotation"],
        color=COLORS["accent"],
        ha="right",
        va="bottom",
    )

    _ax.set_xlabel("Asset Lifetime (years)", fontsize=FONTS["axis_label"])
    _ax.set_ylabel(
        "Grid Benefit (shared infrastructure value)", fontsize=FONTS["axis_label"]
    )
    _ax.set_xlim(15, 58)
    _ax.set_ylim(-0.05, 1.05)
    _ax.grid(True, linestyle=":", alpha=0.3)
    plt.tight_layout()

    save_fig(fig_spectrum, cfg.img_dir / "dd002_generation_spectrum.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo):
    _chart = mo.image(
        src=(cfg.img_dir / "dd002_generation_spectrum.png").read_bytes(), width=800
    )
    mo.md(
        f"""
    # Not all AI-driven generation is equal — long-lived grid assets create the most spillover

    {_chart}

    *Bubble size reflects approximate relative new capacity. The green-shaded
    upper-right quadrant — long-lived assets with high grid benefit — is where
    policy should steer AI capital. The lower-left is where it lands without
    intervention. The regulatory environment determines which quadrant dominates.*
    """
    )
    return


@app.cell
def _(cfg, eia, horizontal_bar_ranking, legend_below, plt, save_fig):
    # Top states by new capacity since 2020
    _state_agg = (
        eia[eia["operating_year"] >= 2020]
        .groupby("state")["nameplate_capacity_mw"]
        .sum()
        .sort_values(ascending=False)
        .head(15)
    )

    _labels = _state_agg.index.tolist()
    _values = (_state_agg.values / 1000).tolist()  # Convert to GW

    # Highlight data center corridor states
    _dc_states = {"TX", "VA", "GA", "OH", "CA"}
    _highlight = [i for i, s in enumerate(_labels) if s in _dc_states]

    fig_states = horizontal_bar_ranking(
        _labels,
        _values,
        "Texas, California, and Virginia lead new generation — all major data center corridors",
        xlabel="New Capacity Since 2020 (GW)",
        highlight_indices=_highlight,
    )
    # Add legend for highlight colors
    _ax_st = fig_states.axes[0]
    _legend_handles = [
        plt.Line2D([0], [0], marker="s", color="w", markerfacecolor=COLORS["negative"],
                   markersize=14, label="Data center corridor state"),
        plt.Line2D([0], [0], marker="s", color="w", markerfacecolor=CATEGORICAL[0],
                   markersize=14, label="Other state"),
    ]
    legend_below(_ax_st, handles=_legend_handles, ncol=2)
    save_fig(fig_states, cfg.img_dir / "dd002_state_generation.png")
    return


@app.cell
def _(cfg, eia, np, plt, save_fig, us_scatter_map):
    # Map: new power plants since 2020, colored by fuel type
    _recent_geo = eia[
        (eia["operating_year"] >= 2020)
        & eia["latitude"].notna()
        & eia["longitude"].notna()
        # Filter to continental US bounds
        & (eia["longitude"] > -130)
        & (eia["longitude"] < -60)
        & (eia["latitude"] > 23)
        & (eia["latitude"] < 51)
    ].copy()

    _colors = [
        FUEL_COLORS.get(f, COLORS["reference"]) for f in _recent_geo["fuel_category"]
    ]
    _sizes = np.clip(_recent_geo["nameplate_capacity_mw"].values / 5, 3, 120)

    # Build legend
    _legend_handles = [
        plt.Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            markerfacecolor=c,
            markersize=18,
            label=label.replace("_", " ").title(),
        )
        for label, c in FUEL_COLORS.items()
        if label in _recent_geo["fuel_category"].values
    ]

    fig_plant_map = us_scatter_map(
        _recent_geo["latitude"].values,
        _recent_geo["longitude"].values,
        _colors,
        _sizes,
        "New power plants since 2020 cluster in data center corridors and renewable-rich regions",
        legend_handles=_legend_handles,
        figsize=FIGSIZE["large"],
        alpha=0.5,
    )

    # Override legend with larger font and markers for readability
    _map_ax = fig_plant_map.axes[0]
    _map_ax.get_legend().remove()
    _map_ax.legend(
        handles=_legend_handles,
        labels=[h.get_label() for h in _legend_handles],
        loc="upper center",
        bbox_to_anchor=(0.5, -0.02),
        ncol=4,
        fontsize=16,
        frameon=False,
        markerscale=1.5,
        columnspacing=1.5,
    )

    save_fig(fig_plant_map, cfg.img_dir / "dd002_plant_map.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo):
    _plant_map = mo.image(
        src=(cfg.img_dir / "dd002_plant_map.png").read_bytes(), width=850
    )
    mo.md(
        f"""
    ## Geographic Concentration

    # New power plants since 2020 cluster in data center corridors and renewable-rich regions

    {_plant_map}

    The map reveals clear spatial patterns. Solar concentrates in the
    Sun Belt — Texas, California, the Southeast. Wind clusters in the
    Great Plains corridor. Gas combined cycle plants dot the eastern
    seaboard and Texas Gulf Coast. The geographic distribution is not
    random: it follows resource availability (sun, wind), existing
    grid infrastructure, and permitting environments.
    """
    )
    return


@app.cell
def _(FONTS, cfg, np, plt, save_fig, us_scatter_map):
    # Frontier AI data center locations (Epoch AI, February 2025)
    # Filtered to US-based facilities with confirmed power capacity
    _datacenters = [
        {
            "name": "Amazon Canton MS",
            "lat": 32.59,
            "lon": -90.09,
            "mw": 341,
            "owner": "Amazon",
        },
        {
            "name": "Anthropic-Amazon New Carlisle IN",
            "lat": 41.69,
            "lon": -86.46,
            "mw": 751,
            "owner": "Amazon",
        },
        {
            "name": "Google Pryor OK",
            "lat": 36.24,
            "lon": -95.33,
            "mw": 195,
            "owner": "Google",
        },
        {
            "name": "Google New Albany OH",
            "lat": 40.06,
            "lon": -82.76,
            "mw": 543,
            "owner": "Google",
        },
        {
            "name": "Google Omaha NE",
            "lat": 41.34,
            "lon": -96.09,
            "mw": 189,
            "owner": "Google",
        },
        {
            "name": "Google Council Bluffs IA",
            "lat": 41.17,
            "lon": -95.79,
            "mw": 190,
            "owner": "Google",
        },
        {
            "name": "Meta Prometheus OH",
            "lat": 40.07,
            "lon": -82.75,
            "mw": 814,
            "owner": "Meta",
        },
        {
            "name": "Meta Temple TX",
            "lat": 31.13,
            "lon": -97.37,
            "mw": 198,
            "owner": "Meta",
        },
        {
            "name": "OpenAI-Oracle Stargate TX",
            "lat": 32.50,
            "lon": -99.78,
            "mw": 295,
            "owner": "Oracle",
        },
        {
            "name": "Microsoft Goodyear AZ",
            "lat": 33.41,
            "lon": -112.37,
            "mw": 316,
            "owner": "Microsoft",
        },
        {
            "name": "xAI Colossus 1 TN",
            "lat": 35.06,
            "lon": -90.16,
            "mw": 498,
            "owner": "xAI",
        },
        {
            "name": "xAI Colossus 2 TN",
            "lat": 35.00,
            "lon": -90.03,
            "mw": 302,
            "owner": "xAI",
        },
    ]

    _owner_colors = {
        "Amazon": COMPANY_COLORS["AMZN"],
        "Google": COMPANY_COLORS["GOOGL"],
        "Meta": COMPANY_COLORS["META"],
        "Microsoft": COMPANY_COLORS["MSFT"],
        "xAI": COLORS["text_dark"],
        "Oracle": COMPANY_COLORS["ORCL"],
    }

    _lats = [d["lat"] for d in _datacenters]
    _lons = [d["lon"] for d in _datacenters]
    _colors = [_owner_colors.get(d["owner"], COLORS["reference"]) for d in _datacenters]
    _sizes = np.array([d["mw"] for d in _datacenters]) / 2

    _legend_handles = [
        plt.Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            markerfacecolor=c,
            markersize=14,
            label=owner,
        )
        for owner, c in _owner_colors.items()
        if owner in {d["owner"] for d in _datacenters}
    ]

    fig_dc_map = us_scatter_map(
        _lats,
        _lons,
        _colors,
        _sizes,
        "Frontier AI data centers concentrate in a few states — the same ones building generation",
        legend_handles=_legend_handles,
        figsize=(14, 8),
        alpha=0.8,
        edgecolors=COLORS["text_dark"],
        linewidth=1.0,
    )

    # Enlarge legend markers and font for readability
    _dc_ax = fig_dc_map.axes[0]
    _dc_legend = _dc_ax.get_legend()
    if _dc_legend:
        _dc_legend.remove()
    _dc_ax.legend(
        handles=_legend_handles,
        labels=[h.get_label() for h in _legend_handles],
        loc="upper center",
        bbox_to_anchor=(0.5, -0.03),
        ncol=min(len(_legend_handles), 6),
        fontsize=16,
        frameon=False,
        markerscale=1.5,
        columnspacing=1.5,
    )

    # Add labels for largest facilities — placed at specific map coordinates
    # to guarantee no overlap (using data coords for xytext)
    _ax = _dc_ax
    _label_positions = {
        "Meta Prometheus OH": ("Meta Prometheus\n814 MW", (-72, 46)),
        "Anthropic-Amazon New Carlisle IN": (
            "Anthropic-Amazon\n751 MW",
            (-96, 46),
        ),
        "Google New Albany OH": ("Google New Albany\n543 MW", (-72, 35)),
        "xAI Colossus 1 TN": ("xAI Colossus\n498 MW", (-82, 31)),
    }
    for d in _datacenters:
        if d["name"] in _label_positions:
            _text, (_lx, _ly) = _label_positions[d["name"]]
            _ax.annotate(
                _text,
                (d["lon"], d["lat"]),
                xytext=(_lx, _ly),
                fontsize=FONTS["annotation"],
                color=COLORS["text_dark"],
                arrowprops=dict(arrowstyle="->", color=COLORS["text_light"], lw=1.2,
                                connectionstyle="arc3,rad=0.1"),
                bbox=dict(
                    boxstyle="round,pad=0.3", fc="white", ec=COLORS["muted"], alpha=0.95
                ),
            )

    save_fig(fig_dc_map, cfg.img_dir / "dd002_datacenter_map.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo):
    _dc_map = mo.image(
        src=(cfg.img_dir / "dd002_datacenter_map.png").read_bytes(), width=850
    )
    _state_chart = mo.image(
        src=(cfg.img_dir / "dd002_state_generation.png").read_bytes(), width=800
    )
    mo.md(
        f"""
    # Frontier AI data centers concentrate in a few states — the same ones building generation

    {_dc_map}

    *Source: Epoch AI Frontier Data Centers dataset (February 2025). Only facilities
    with confirmed power capacity shown. Bubble size proportional to MW.*

    The overlap between these two maps is the core geographic story: AI data
    centers are landing in the same states that are adding the most generation
    capacity. Ohio, Texas, and the Southeast corridor dominate both.

    # Texas, California, and Virginia lead new generation — all major data center corridors

    {_state_chart}

    Data centers locate where power is available (or can be built). The
    infrastructure they require — substations, transmission upgrades,
    generation capacity — shapes the grid topology for decades. Where AI
    capital lands today determines the grid geography of 2060.
    """
    )
    return


@app.cell
def _(FONTS, cfg, elec_ppi, legend_below, natgas, pd, plt, save_fig):
    # Natural gas price + electricity PPI with AI milestone annotations
    _gas = natgas["2015":].copy()
    _elec = elec_ppi["2015":].copy()

    fig_gas, _ax1 = plt.subplots(figsize=(14, 6.5))

    # Primary axis: natural gas price
    _ax1.plot(
        _gas.index,
        _gas["price"],
        color=COLORS["accent"],
        linewidth=2,
        label="Henry Hub Spot Price",
    )
    _ax1.set_ylabel(
        "Natural Gas ($/MMBtu)", color=COLORS["accent"], fontsize=FONTS["axis_label"]
    )
    _ax1.tick_params(axis="y", labelcolor=COLORS["accent"])
    _ax1.set_ylim(0, 10)

    # Secondary axis: electricity PPI (indexed)
    _ax2 = _ax1.twinx()
    _ax2.plot(
        _elec.index,
        _elec["price"],
        color=CATEGORICAL[0],
        linewidth=1.5,
        alpha=0.7,
        label="Electricity PPI",
    )
    _ax2.set_ylabel(
        "Electricity PPI (Index)", color=CATEGORICAL[0], fontsize=FONTS["axis_label"]
    )
    _ax2.tick_params(axis="y", labelcolor=CATEGORICAL[0])

    # AI milestone annotations — compact placement to avoid obstructing data
    _ax1.annotate(
        "ChatGPT launch",
        xy=(pd.Timestamp("2022-11-30"), 7.0),
        xytext=(pd.Timestamp("2021-09-01"), 9.0),
        arrowprops=dict(arrowstyle="->", color="black", lw=1.2),
        fontsize=FONTS["annotation"] - 1,
        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=COLORS["text_light"], alpha=0.85),
    )
    _ax1.annotate(
        "GPT-4",
        xy=(pd.Timestamp("2023-03-14"), 2.5),
        xytext=(pd.Timestamp("2021-06-01"), 1.0),
        arrowprops=dict(arrowstyle="->", color="black", lw=1.2),
        fontsize=FONTS["annotation"] - 1,
        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=COLORS["text_light"], alpha=0.85),
    )
    _ax1.grid(True, linestyle=":", alpha=0.4)

    # Combined legend
    _lines1, _labels1 = _ax1.get_legend_handles_labels()
    _lines2, _labels2 = _ax2.get_legend_handles_labels()
    legend_below(_ax1, handles=_lines1 + _lines2, labels=_labels1 + _labels2)

    plt.tight_layout()
    save_fig(fig_gas, cfg.img_dir / "dd002_energy_prices.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo):
    _price_chart = mo.image(
        src=(cfg.img_dir / "dd002_energy_prices.png").read_bytes(), width=800
    )
    mo.md(
        f"""
    ## Price Signals

    # Gas prices spiked with the energy crisis — electricity prices followed and stayed elevated

    {_price_chart}

    Natural gas prices tell a more nuanced story than the "AI is raising
    electricity costs" narrative suggests. The 2022 price spike was driven
    by the Ukraine war and the European energy crisis, not by data center
    demand. Since then, gas prices have collapsed to near-historic lows —
    but the electricity PPI (blue) tells a different story: electricity
    prices rose with gas and have not fully come back down. The divergence
    reflects grid congestion, capacity costs, and growing demand.

    For data center operators, cheap gas is a double-edged sword. It makes
    gas-fired generation economically attractive in the near term, but it
    also makes the stranded asset question more urgent: if you build a gas
    plant today because gas is cheap, what happens when carbon regulation
    returns and gas prices normalize?

    The underlying cost trend favors renewables regardless. Solar-plus-storage
    is cost-competitive with new gas in many U.S. markets, and unsubsidized
    solar alone is cheaper than new gas in most. The question is whether
    permitting timelines — not economics — push operators toward gas as a
    faster path to power.
    """
    )
    return


@app.cell
def _(cfg, horizontal_bar_ranking, save_fig):
    # Hyperscaler renewable portfolio sizes (approximate, from sustainability reports)
    _companies = ["Microsoft", "Amazon", "Meta", "Google"]
    _gw = [34, 32.5, 12, 10]

    fig_ppa = horizontal_bar_ranking(
        _companies,
        _gw,
        "Microsoft and Amazon have contracted more renewable energy than most countries generate",
        xlabel="Contracted Renewable Capacity (GW)",
        highlight_indices=[0, 1],
        highlight_color=COLORS["positive"],
        color=FUEL_COLORS["wind"],
    )
    save_fig(fig_ppa, cfg.img_dir / "dd002_hyperscaler_ppa.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo):
    _ppa_chart = mo.image(
        src=(cfg.img_dir / "dd002_hyperscaler_ppa.png").read_bytes(), width=800
    )
    mo.md(
        f"""
    ## The Hyperscaler PPA Landscape

    # Microsoft and Amazon have contracted more renewable energy than most countries generate

    {_ppa_chart}

    The major AI companies are signing the largest corporate power purchase
    agreements in history:

    - **Amazon:** The world's largest corporate buyer of renewable energy,
      with 600+ projects and approximately 30-35 GW of contracted nameplate
      capacity. Invested in SMR development through multiple partnerships.
    - **Microsoft:** 34 GW total renewable portfolio across 24 countries,
      including a 10.5 GW deal with Brookfield Renewable Partners and a
      landmark agreement with Constellation to restart the Three Mile Island
      Unit 1 nuclear reactor. Major Iberdrola partnership (500MW+ in Spain).
    - **Google:** Pioneering geothermal energy through Fervo partnership.
      First major tech company to achieve 100% matched renewable energy.
    - **Meta:** 100% renewable energy for operations. Significant solar
      and wind PPAs across the U.S.
    - **Anthropic:** Pledged to cover electricity price increases caused
      by its data centers for affected communities.

    The scale is unprecedented. These PPAs represent a permanent shift in
    corporate energy procurement — the contracts lock in clean generation
    for 15-25 years regardless of what happens to AI demand.

    But there is a tension. The same companies signing renewable PPAs are
    also building or contracting gas-fired generation for reliability and
    speed. xAI's Colossus facility in Memphis runs on natural gas turbines.
    Microsoft's data centers in Virginia draw from a grid that is
    predominantly fossil-fueled. The public commitments and the operational
    reality do not always align.

    **"Greenhushing"** compounds this tension. In the current political
    environment, companies are continuing their clean energy strategies
    but muting public messaging. The underlying economics still favor
    renewables, but the visible narrative has shifted.
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## What This Means for Durability

    Applying the durability taxonomy from the research framework:

    **Structural investments** (persist regardless of AI's commercial outcome):
    - Solar PPAs at current prices — cost-competitive without any AI demand premium
    - Grid infrastructure upgrades triggered by interconnection — substations,
      transmission lines, distribution upgrades
    - Battery storage paired with renewables — serves grid stability independent
      of data center load

    **Policy-dependent investments** (durable only under a specific regulatory regime):
    - Nuclear restarts — require NRC approval, sustained political support, and
      favorable rate treatment
    - SMR development — depends on DOE loan guarantees, NRC licensing timeline,
      and continued IRA tax credits
    - Gas plants in states with emissions standards — at risk if clean energy
      mandates return

    **Demand-thesis-dependent investments** (durable only if AI growth continues):
    - Behind-the-meter gas generation (xAI model) — built specifically for
      data center load, limited alternative use
    - AI-optimized grid topology — transmission upgrades to specific corridors
      that only make sense at projected data center scale

    The key insight: even demand-thesis-dependent investments create structural
    infrastructure once built. A gas plant commissioned to serve a data center
    becomes a 40-year generating asset that operates regardless of whether the
    data center scales as planned. The capital decision was AI-driven; the
    infrastructure consequence is not.

    ---

    ## What Comes Next

    Part 1 asked **what** is getting built. Part 2 asks **who benefits**:
    does AI-driven grid investment modernize infrastructure for everyone,
    or just create faster pipes for hyperscalers? The answer depends on
    interconnection queues, cost allocation rules, and regulatory choices
    being made right now.

    ---

    ### Sources

    - EIA Form 860 (2024 release) — generator-level data for all U.S. power plants
    - FRED — Henry Hub Natural Gas Spot Price (DHHNGSP), Electric Power PPI (WPU0543)
    - Amazon sustainability report (2024): ~30-35 GW contracted renewable capacity, 600+ projects
    - Microsoft environmental sustainability report (2025): 34 GW total renewable portfolio; 10.5 GW Brookfield deal
    - Google environmental report (2025): 100% matched renewable energy
    - xAI Colossus facility: EPA non-road engine loophole closure (January 2026)
    - HBR on "greenhushing" — companies continuing climate strategies while muting messaging
    - Axios (February 2026): "Greenhouse gas emissions will keep falling despite Trump's climate rollback"
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
