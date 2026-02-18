import marimo

__generated_with = "0.19.11"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # AI Capital and Grid Modernization
    ## Part 2 — Who Benefits?

    *Thandolwethu Zwelakhe Dlamini*

    ---

    Part 1 showed what generation is getting built. Solar dominates new
    capacity, gas remains significant, and battery storage is the fastest-
    growing category. But new generation is useless if it cannot connect
    to the grid.

    This part asks: **does AI-driven grid investment modernize infrastructure
    for everyone, or just create faster pipes for hyperscalers?**

    The answer hinges on two things: the interconnection queue (can new
    generation actually reach the grid?) and cost allocation (who pays for
    the upgrades?).
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
        CATEGORICAL,
        COLORS,
        CONTEXT,
        FONTS,
        FUEL_COLORS,
        horizontal_bar_ranking,
        legend_below,
        stacked_bar,
        waterfall_chart,
    )

    cfg = setup()
    return (
        CATEGORICAL,
        COLORS,
        CONTEXT,
        FONTS,
        FUEL_COLORS,
        cfg,
        horizontal_bar_ranking,
        legend_below,
        mo,
        np,
        pd,
        plt,
        query,
        save_fig,
        stacked_bar,
        waterfall_chart,
    )


@app.cell
def _(pd, query):
    # Database-backed inputs for the narrative notebook.
    queue_summary = query(
        """
        SELECT year, generation_gw, storage_gw, total_gw, completion_pct, withdrawal_pct,
               solar_gw, wind_gw, gas_gw, other_gw
        FROM energy_data.lbnl_queue_summary
        ORDER BY year
        """
    )
    queue_region = query(
        """
        SELECT year, region, queue_gw, is_major_dc_region, source, source_detail
        FROM energy_data.dd002_queue_region_backlog
        WHERE year = (SELECT MAX(year) FROM energy_data.dd002_queue_region_backlog)
        ORDER BY queue_gw DESC
        """
    )
    cost_alloc = query(
        """
        SELECT year, region, cost_category, cost_bn, sort_order, is_total, project_count,
               socialized_pct, is_estimate, source, source_detail
        FROM energy_data.dd002_cost_allocation
        ORDER BY year, sort_order
        """
    )
    policy_events = query(
        """
        SELECT event_date, jurisdiction, docket, event_name, event_type, status,
               effective_or_due_date, description, source_name, source_url
        FROM energy_data.dd002_policy_events
        ORDER BY event_date
        """
    )
    projection_priors = query(
        """
        SELECT parameter, base_value, low_value, high_value, units, source, source_date, source_detail
        FROM energy_data.dd002_projection_priors
        ORDER BY parameter
        """
    )
    region_weights = query(
        """
        SELECT ticker, region, allocation_weight, source, source_detail
        FROM energy_data.dd002_hyperscaler_region_weights
        """
    )
    capex_annual = query(
        """
        SELECT ticker, YEAR(CAST(date AS DATE)) AS year, SUM(capex_bn) AS capex_bn
        FROM energy_data.hyperscaler_capex
        GROUP BY ticker, YEAR(CAST(date AS DATE))
        """
    )
    in_service_state_year = query(
        """
        SELECT operating_year AS year, state,
               SUM(nameplate_capacity_mw) / 1000.0 AS in_service_gw
        FROM energy_data.eia860_generators
        WHERE status = 'OP'
          AND operating_year >= 2020
          AND state IS NOT NULL
        GROUP BY operating_year, state
        """
    )
    _installed = float(
        query(
            """
            SELECT SUM(nameplate_capacity_mw) / 1000.0 AS installed_gw
            FROM energy_data.eia860_generators
            WHERE status = 'OP'
            """
        ).iloc[0, 0]
    )
    _elec_price = float(
        query(
            """
            SELECT value AS retail_price_cents_kwh
            FROM energy_data.fred_series
            WHERE series_id = 'APU000072610'
            ORDER BY date DESC
            LIMIT 1
            """
        ).iloc[0, 0]
    )
    citations = query(
        """
        SELECT key, value, unit, source_name, source_date, source_detail, url
        FROM energy_data.source_citations
        """
    )
    citation_map = citations.set_index("key")["value"].to_dict()

    queue_comp = queue_summary[
        ["year", "solar_gw", "storage_gw", "wind_gw", "gas_gw", "other_gw"]
    ].rename(columns={"storage_gw": "battery"})
    queue_comp[["solar_gw", "battery", "wind_gw", "gas_gw", "other_gw"]] = queue_comp[
        ["solar_gw", "battery", "wind_gw", "gas_gw", "other_gw"]
    ].fillna(0)

    region_state_map = {
        "PJM": {"DC", "DE", "IL", "IN", "KY", "MD", "MI", "NC", "NJ", "OH", "PA", "TN", "VA", "WV"},
        "MISO": {"AR", "IA", "LA", "MN", "MS", "MO", "MT", "ND", "SD", "WI"},
        "CAISO": {"CA"},
        "SPP": {"KS", "NE", "NM", "OK", "WY"},
        "ERCOT": {"TX"},
        "NYISO": {"NY"},
        "ISO-NE": {"CT", "MA", "ME", "NH", "RI", "VT"},
        "Non-ISO West": {"AK", "AZ", "CO", "HI", "ID", "NV", "OR", "UT", "WA"},
        "Non-ISO Southeast": {"AL", "FL", "GA", "SC"},
    }
    state_to_region = {state: region for region, states in region_state_map.items() for state in states}
    in_service_state_year["region"] = in_service_state_year["state"].map(state_to_region).fillna("Non-ISO West")
    in_service_region_2024 = (
        in_service_state_year[in_service_state_year["year"] == 2024]
        .groupby("region", as_index=False)["in_service_gw"]
        .sum()
    )

    capex_latest_year = int(capex_annual["year"].max())
    capex_latest = capex_annual[capex_annual["year"] == capex_latest_year].copy()
    capex_region = capex_latest.merge(region_weights, on="ticker", how="inner")
    capex_region["allocated_capex_bn"] = capex_region["capex_bn"] * capex_region["allocation_weight"]
    lag_by_company_region = (
        capex_region.merge(queue_region[["region", "queue_gw"]], on="region", how="left")
        .merge(in_service_region_2024, on="region", how="left")
        .assign(
            implied_lag_years=lambda d: d["queue_gw"] / d["in_service_gw"],
            throughput_mw_per_bn=lambda d: (d["in_service_gw"] * 1000.0) / d["allocated_capex_bn"],
        )
        .sort_values(["implied_lag_years", "allocated_capex_bn"], ascending=[False, False])
    )

    _q_latest = queue_summary.iloc[-1]
    _q_prev = queue_summary.iloc[-2]
    _queue_yoy_pct = (_q_latest["total_gw"] / _q_prev["total_gw"] - 1) * 100
    _cost_total = cost_alloc[cost_alloc["is_total"]].iloc[-1]
    _avg_monthly_bill = round(_elec_price * 886)
    _avg_annual_bill = _avg_monthly_bill * 12

    stats = {
        "queue_total_gw": int(_q_latest["total_gw"]),
        "queue_gen_gw": int(_q_latest["generation_gw"]),
        "queue_storage_gw": int(_q_latest["storage_gw"]),
        "median_years": int(citation_map["queue_median_years"]),
        "completion_pct": int(_q_latest["completion_pct"]),
        "queue_yoy_pct": round(_queue_yoy_pct),
        "queue_yoy_abs_pct": abs(round(_queue_yoy_pct)),
        "queue_yoy_direction": "decrease" if _queue_yoy_pct < 0 else "increase",
        "ucs_cost_bn": float(_cost_total["cost_bn"]),
        "ucs_projects": int(_cost_total["project_count"]),
        "ucs_socialized_pct": int(_cost_total["socialized_pct"]),
        "va_bill_annual": int(citation_map["va_bill_annual_2040"]),
        "va_bill_monthly": round(float(citation_map["va_bill_annual_2040"]) / 12),
        "va_capacity_pct": int(citation_map["va_capacity_share_americas_pct"]),
        "installed_gw": round(_installed),
        "queue_ratio": round(_q_latest["total_gw"] / _installed, 1),
        "avg_monthly_bill": _avg_monthly_bill,
        "avg_annual_bill": _avg_annual_bill,
        "avg_bill_10pct": round(_avg_annual_bill * 0.1),
        "capex_lag_year": capex_latest_year,
        "lag_top_region": lag_by_company_region.iloc[0]["region"],
        "lag_top_years": lag_by_company_region.iloc[0]["implied_lag_years"],
    }

    return (
        cost_alloc,
        lag_by_company_region,
        policy_events,
        projection_priors,
        queue_comp,
        queue_region,
        stats,
    )


@app.cell(hide_code=True)
def _(mo, stats):
    mo.hstack(
        [
            mo.callout(
                mo.md(f"# {stats['queue_total_gw']:,} GW\nProposed projects in the "
                       f"interconnection queue — {stats['queue_ratio']}x U.S. installed "
                       f"generation capacity"),
                kind="warn",
            ),
            mo.callout(
                mo.md(f"# {stats['median_years']}+ years\nMedian time from interconnection "
                       f"request to commercial operation for projects built since 2018"),
                kind="danger",
            ),
            mo.callout(
                mo.md(f"# {stats['completion_pct']}%\nOf projects that enter the queue "
                       f"are ever built. The rest withdraw due to cost, delays, or "
                       f"changing economics"),
                kind="neutral",
            ),
        ],
        justify="space-around",
        gap=1,
    )
    return


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    ## The Interconnection Queue: {stats['queue_total_gw']:,} GW Waiting

    Every new power plant — solar farm, gas turbine, battery installation —
    must apply to connect to the grid through the interconnection queue.
    The queue is managed by regional grid operators (ISOs/RTOs) and requires
    engineering studies, cost estimates, and utility agreements before a
    project can proceed.

    As of 2024, the U.S. interconnection queue contains approximately
    **{stats['queue_total_gw']:,} GW** of proposed projects (roughly
    {stats['queue_gen_gw']:,} GW of generation and {stats['queue_storage_gw']:,} GW
    of storage) — {stats['queue_ratio']}x the country's installed generation
    capacity ({stats['installed_gw']:,} GW). The median time from interconnection
    request to commercial operation exceeds **{stats['median_years']} years** for
    projects built since 2018. Only about **{stats['completion_pct']}%** of projects
    that enter the queue are ever built.

    There are early signs of improvement. FERC Order 2023 reforms and high
    withdrawal rates have begun reducing queue backlog — the LBNL annual data
    shows a {stats['queue_yoy_abs_pct']}% {stats['queue_yoy_direction']} in active
    queue volume from the prior year. But the structural bottleneck remains severe.

    This is the binding constraint on AI infrastructure. It does not matter
    how many renewable PPAs a hyperscaler signs if the generation cannot
    connect to the grid for half a decade.
    """)
    return


@app.cell(hide_code=True)
def _(cfg, mo, stats):
    _funnel = mo.image(
        src=(cfg.img_dir / "dd002_queue_funnel.png").read_bytes(), width=500
    )
    mo.md(
        f"""
    {_funnel}

    *The interconnection queue is a funnel, not a pipeline. Of the
    {stats['queue_total_gw']:,} GW waiting to connect, only about
    {stats['completion_pct']}% will ever be built. The rest withdraw due to cost
    escalation, engineering obstacles, or changing project economics.*
    """
    )
    return


@app.cell
def _(CATEGORICAL, COLORS, cfg, horizontal_bar_ranking, legend_below, plt, queue_region, save_fig):
    _regions = queue_region["region"].tolist()
    _backlog_gw = queue_region["queue_gw"].tolist()
    _highlight = [i for i, flag in enumerate(queue_region["is_major_dc_region"].tolist()) if flag]

    fig_queue = horizontal_bar_ranking(
        _regions,
        _backlog_gw,
        "PJM and MISO carry the largest interconnection backlogs",
        xlabel="Queue Backlog (GW)",
        highlight_indices=_highlight,
        highlight_color=COLORS["accent"],
    )
    _ax_q = fig_queue.axes[0]
    _legend_handles = [
        plt.Line2D([0], [0], marker="s", color="w", markerfacecolor=COLORS["accent"],
                   markersize=14, label="Major data center region"),
        plt.Line2D([0], [0], marker="s", color="w", markerfacecolor=CATEGORICAL[0],
                   markersize=14, label="Other region"),
    ]
    legend_below(_ax_q, handles=_legend_handles, ncol=2)
    save_fig(fig_queue, cfg.img_dir / "dd002_queue_by_region.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo):
    _queue_chart = mo.image(
        src=(cfg.img_dir / "dd002_queue_by_region.png").read_bytes(), width=800
    )
    mo.md(
        f"""
    # PJM and MISO carry the largest interconnection backlogs

    {_queue_chart}

    PJM — the grid operator covering the mid-Atlantic from Virginia to
    Illinois — carries the largest backlog at ~520 GW. This is not
    coincidental: PJM is home to Northern Virginia's data center corridor,
    the densest concentration of data center capacity on Earth. MISO
    (Midwest), CAISO (California), and ERCOT (Texas) follow.

    The queue is dominated by clean energy — solar, battery storage, hybrid,
    and wind projects together account for the vast majority of proposed
    capacity. Gas projects represent roughly 6% of the queue and the share
    is declining. The bottleneck is not the business case for renewables;
    it is the administrative and engineering process of connecting them
    to the grid.

    *Regional backlog values are loaded from `energy_data.dd002_queue_region_backlog`
    and reconciled to the national queue total in `energy_data.lbnl_queue_summary`.*
    """
    )
    return


@app.cell
def _(CATEGORICAL, COLORS, CONTEXT, FUEL_COLORS, cfg, queue_comp, save_fig, stacked_bar):
    _colors = {
        "solar_gw": {"color": FUEL_COLORS["solar"], "label": "Solar"},
        "battery": {"color": FUEL_COLORS["battery"], "label": "Battery Storage"},
        "wind_gw": {"color": FUEL_COLORS["wind"], "label": "Wind"},
        "gas_gw": {"color": CONTEXT, "label": "Gas"},
        "other_gw": {"color": COLORS["reference"], "label": "Other"},
    }

    fig_comp = stacked_bar(
        queue_comp,
        "year",
        {k: v.copy() for k, v in _colors.items()},
        "The queue is overwhelmingly clean energy — gas is a shrinking share",
        ylabel="Queue Capacity (GW)",
    )
    save_fig(fig_comp, cfg.img_dir / "dd002_queue_composition.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo):
    _comp_chart = mo.image(
        src=(cfg.img_dir / "dd002_queue_composition.png").read_bytes(), width=800
    )
    mo.md(
        f"""
    # The queue is overwhelmingly clean energy — gas is a shrinking share

    {_comp_chart}

    The composition of the queue reveals an important structural fact:
    **the pipeline of proposed generation is overwhelmingly clean energy.**
    Solar and storage projects account for the majority of queued capacity.
    Wind remains material. Gas is a smaller share and has not kept pace with
    clean-energy queue growth.

    This means that even under the most aggressive AI demand scenarios,
    the generation that eventually connects to the grid will be predominantly
    renewable. The constraint is not technology choice — it is queue throughput.
    Anything that speeds up interconnection (FERC reform, utility process
    improvements, standardized studies) disproportionately benefits clean energy.

    *Queue composition is sourced from `energy_data.lbnl_queue_summary`
    (LBNL annual queue editions), with storage mapped to battery for charting.*
    """
    )
    return


@app.cell
def _(cfg, cost_alloc, save_fig, stats, waterfall_chart):
    _alloc = cost_alloc[~cost_alloc["is_total"]].sort_values("sort_order")
    _items = [
        (row["cost_category"].replace(" ", "\n"), float(row["cost_bn"]))
        for _, row in _alloc.iterrows()
    ]

    fig_cost = waterfall_chart(
        _items,
        f"\\${stats['ucs_cost_bn']:.2f}B in PJM data center grid costs shifted to ratepayers in 2024",
        total_label="Total\nsocialized",
    )
    save_fig(fig_cost, cfg.img_dir / "dd002_cost_allocation.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo, stats):
    _cost_chart = mo.image(
        src=(cfg.img_dir / "dd002_cost_allocation.png").read_bytes(), width=800
    )
    mo.md(
        f"""
    ## The \\${stats['ucs_cost_bn']:.2f} Billion Question

    # \\${stats['ucs_cost_bn']:.2f}B in PJM data center grid costs shifted to ratepayers in 2024

    {_cost_chart}

    When a data center connects to the grid, it triggers upgrades: new
    substations, transmission reinforcement, distribution capacity. The
    question is who pays.

    The Union of Concerned Scientists identified more than {stats['ucs_projects']}
    local transmission projects from 2022 to 2024, with
    **\\${stats['ucs_cost_bn']:.2f} billion** in data center transmission connection
    costs approved in **2024 alone** and passed to PJM ratepayers. Over
    {stats['ucs_socialized_pct']}% of projects socialized their costs to all
    utility customers — meaning residential customers in Virginia, Ohio, and
    Pennsylvania are subsidizing grid upgrades that primarily serve hyperscaler
    data centers.

    The category rows are loaded from
    `energy_data.dd002_cost_allocation`. The \\$4.36B total is the
    source-reported UCS figure; category-level rows remain analyst
    allocations and are explicitly flagged in the source table.

    "Socialized costs" means that grid upgrades triggered by data center
    demand are paid for through higher electricity bills for everyone in
    the utility's service territory. A household in rural Virginia pays
    slightly more on their electric bill so that AWS can connect a new
    data center campus in Loudoun County.

    The picture is not entirely one-sided. E3 — the same firm that
    conducted the Virginia JLARC study — found in a separate
    Amazon-commissioned study (December 2025) that data centers "generate
    sufficient revenue to cover their costs and, in many instances,
    generated surplus revenue, providing a potential net benefit to other
    ratepayers." Whether data centers are net cost-shifters
    or net contributors depends on rate design, load profile, and the
    specific utility territory. The UCS finding captures a real cost
    allocation problem; it does not mean every data center is a net
    negative for ratepayers.
    """
    )
    return


@app.cell(hide_code=True)
def _(mo, policy_events):
    _events = policy_events.sort_values("event_date")
    _lines = "\n".join(
        [
            (
                f"- **{row['event_date']} — {row['event_name']}** "
                f"({row['jurisdiction']} {row['docket']}): {row['description']}"
            )
            for _, row in _events.iterrows()
        ]
    )
    mo.md(
        f"""
    ## Regulatory Timeline (Database-Sourced)

    The policy timeline below is loaded from `energy_data.dd002_policy_events`:

    {_lines}
    """
    )
    return


@app.cell(hide_code=True)
def _(mo, stats):
    mo.hstack(
        [
            mo.callout(
                mo.md(
                    "**What this changes:** Co-located loads (the xAI model — "
                    "data center at a power plant site) can no longer free-ride "
                    "on grid services they use but do not pay for."
                ),
                kind="success",
            ),
            mo.callout(
                mo.md(
                    f"**What this does NOT change:** Standard grid interconnection "
                    f"cost allocation. The \\${stats['ucs_cost_bn']:.2f}B UCS finding "
                    f"covers projects that connect through the normal process, not "
                    f"co-location. The broader cost allocation question remains unresolved."
                ),
                kind="warn",
            ),
        ],
        gap=1,
    )
    return


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    ## The Virginia Case Study

    Virginia is the most advanced example of the "who benefits" tension.

    The Virginia Joint Legislative Audit and Review Commission (JLARC)
    commissioned Energy + Environmental Economics (E3) to study the
    impact of data center growth on the state's grid. The December 2024
    report found:

    - **Northern Virginia hosts the densest concentration of data center
      capacity in the world** — approximately {stats['va_capacity_pct']}% of
      capacity in the Americas.
    - Data center load growth is driving **billions in grid upgrades** that
      will be socialized across Dominion Energy's residential rate base.
    - Under high-growth scenarios, residential electricity bills could
      increase by approximately **\\${stats['va_bill_annual']} per year
      (\\${stats['va_bill_monthly']} per month) by 2040**.
    - The Virginia Clean Economy Act's 100% clean energy mandate by 2045
      is in tension with the pace of data center demand — it may not be
      possible to build clean generation fast enough.

    Virginia is the canary in the coal mine. What is happening there
    represents an early version of the tension every state with significant
    data center growth will face: Texas, Georgia, Ohio, Arizona. The policy
    response in Virginia will set precedent.
    """)
    return


@app.cell
def _(FONTS, cfg, np, plt, save_fig, stats):
    # Virginia residential bill impact projection (E3/JLARC high-growth scenario)
    _years = np.arange(2024, 2041)
    _endpoint = stats["va_bill_annual"]
    # Illustrative trajectory: E3 endpoint of $444/year by 2040.
    # Uses t^1.5 curve (faster-than-linear) to reflect compounding data center
    # load growth. The actual path depends on rate case outcomes.
    _bill_increase = _endpoint * ((_years - 2024) / (2040 - 2024)) ** 1.5

    fig_virginia, _ax = plt.subplots(figsize=(10, 4))
    _ax.fill_between(_years, _bill_increase, alpha=0.2, color=COLORS["accent"])
    _ax.plot(_years, _bill_increase, color=COLORS["accent"], linewidth=2.5)

    # Annotate endpoint (escape $ for matplotlib)
    _ax.annotate(
        f"\\${_endpoint}/yr (\\${stats['va_bill_monthly']}/mo)",
        xy=(2040, _endpoint), xytext=(2034, _endpoint + 30),
        fontsize=FONTS["annotation"], fontweight="bold", color=COLORS["accent"],
        arrowprops=dict(arrowstyle="->", color=COLORS["accent"], lw=1.5),
    )

    # Reference: 10% of average U.S. residential bill (DB-derived)
    _ten_pct = stats["avg_bill_10pct"]
    _ax.axhline(y=_ten_pct, color=COLORS["reference"], linestyle="--", linewidth=1, alpha=0.6)
    _ax.annotate(
        f"~10% of avg U.S. residential bill (~\\${stats['avg_monthly_bill']}/mo)",
        xy=(2025, _ten_pct + 5), fontsize=FONTS["annotation"],
        color=COLORS["reference"], va="bottom",
    )

    _ax.set_xlabel("Year", fontsize=FONTS["axis_label"])
    _ax.set_ylabel("Annual Bill Increase ($)", fontsize=FONTS["axis_label"])
    _ax.set_xlim(2024, 2040)
    _ax.set_ylim(0, 520)
    _ax.grid(True, linestyle=":", alpha=0.4)
    plt.tight_layout()

    save_fig(fig_virginia, cfg.img_dir / "dd002_virginia_bills.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo, stats):
    _va_chart = mo.image(
        src=(cfg.img_dir / "dd002_virginia_bills.png").read_bytes(), width=800
    )
    mo.md(
        f"""
    # Virginia residential bills could rise \\${stats['va_bill_annual']}/year by 2040 under high data center growth

    {_va_chart}

    *Illustrative trajectory based on the E3/JLARC high-growth scenario endpoint
    of \\${stats['va_bill_annual']}/year by 2040. The curve shape (t^1.5) assumes
    faster-than-linear growth as data center load compounds; the actual path
    depends on Dominion Energy rate cases and regulatory decisions. The 10%
    reference line uses the current national average residential bill
    (~\\${stats['avg_monthly_bill']}/month from FRED series APU000072610). Virginia bills differ
    from the national average.*
    """
    )
    return


@app.cell
def _(mo, projection_priors):
    _priors = projection_priors.set_index("parameter")

    growth_mu_slider = mo.ui.slider(
        start=float(_priors.loc["annual_growth_mean", "low_value"]),
        stop=float(_priors.loc["annual_growth_mean", "high_value"]),
        step=0.01,
        value=float(_priors.loc["annual_growth_mean", "base_value"]),
        label="Annual growth mean",
        show_value=True,
    )
    growth_sigma_slider = mo.ui.slider(
        start=float(_priors.loc["annual_growth_sigma", "low_value"]),
        stop=float(_priors.loc["annual_growth_sigma", "high_value"]),
        step=0.005,
        value=float(_priors.loc["annual_growth_sigma", "base_value"]),
        label="Growth uncertainty (sigma)",
        show_value=True,
    )
    shock_prob_slider = mo.ui.slider(
        start=float(_priors.loc["regulatory_shock_probability", "low_value"]),
        stop=float(_priors.loc["regulatory_shock_probability", "high_value"]),
        step=0.01,
        value=float(_priors.loc["regulatory_shock_probability", "base_value"]),
        label="Regulatory shock probability",
        show_value=True,
    )
    shock_impact_slider = mo.ui.slider(
        start=float(_priors.loc["regulatory_shock_impact", "low_value"]),
        stop=float(_priors.loc["regulatory_shock_impact", "high_value"]),
        step=0.01,
        value=float(_priors.loc["regulatory_shock_impact", "base_value"]),
        label="Shock impact on growth",
        show_value=True,
    )
    throughput_gain_slider = mo.ui.slider(
        start=float(_priors.loc["throughput_improvement_per_year", "low_value"]),
        stop=float(_priors.loc["throughput_improvement_per_year", "high_value"]),
        step=0.005,
        value=float(_priors.loc["throughput_improvement_per_year", "base_value"]),
        label="Queue throughput improvement per year",
        show_value=True,
    )
    years_slider = mo.ui.slider(
        start=5,
        stop=20,
        step=1,
        value=10,
        label="Projection years",
        show_value=True,
    )
    sims_slider = mo.ui.slider(
        start=1000,
        stop=20000,
        step=1000,
        value=8000,
        label="Monte Carlo draws",
        show_value=True,
    )

    mo.vstack(
        [
            mo.md("## Probabilistic Forecast (ESIG-style uncertainty framing)"),
            mo.hstack([growth_mu_slider, growth_sigma_slider, years_slider], justify="space-around"),
            mo.hstack([shock_prob_slider, shock_impact_slider, throughput_gain_slider], justify="space-around"),
            mo.hstack([sims_slider], justify="start"),
        ],
        gap=1,
    )
    return (
        growth_mu_slider,
        growth_sigma_slider,
        shock_impact_slider,
        shock_prob_slider,
        sims_slider,
        throughput_gain_slider,
        years_slider,
    )


@app.cell
def _(
    COLORS,
    FONTS,
    growth_mu_slider,
    growth_sigma_slider,
    mo,
    np,
    plt,
    shock_impact_slider,
    shock_prob_slider,
    sims_slider,
    stats,
    throughput_gain_slider,
    years_slider,
):
    # Monte Carlo fan chart using uncertain growth + policy shock dynamics.
    _annual_base = stats["ucs_cost_bn"]  # 2024 PJM approvals
    _mu = growth_mu_slider.value
    _sigma = growth_sigma_slider.value
    _shock_prob = shock_prob_slider.value
    _shock_impact = shock_impact_slider.value
    _throughput_gain = throughput_gain_slider.value
    _years = int(years_slider.value)
    _draws = int(sims_slider.value)

    _rng = np.random.default_rng(42)
    _growth = _rng.normal(_mu, _sigma, size=(_draws, _years))
    _growth = np.clip(_growth, -0.25, 0.60)
    _shock = (_rng.random((_draws, _years)) < _shock_prob).astype(float)

    _trend_penalty = _throughput_gain * np.arange(_years)
    _eff_growth = _growth - (_shock * _shock_impact) - _trend_penalty
    _eff_growth = np.clip(_eff_growth, -0.30, 0.60)

    _annual = np.zeros((_draws, _years))
    _annual[:, 0] = _annual_base * (1 + _eff_growth[:, 0])
    for _t in range(1, _years):
        _annual[:, _t] = _annual[:, _t - 1] * (1 + _eff_growth[:, _t])
    _annual = np.clip(_annual, 0, None)
    _cumulative = np.cumsum(_annual, axis=1)

    _x_labels = 2025 + np.arange(_years)
    _annual_p10, _annual_p50, _annual_p90 = np.percentile(_annual, [10, 50, 90], axis=0)
    _cum_p10, _cum_p50, _cum_p90 = np.percentile(_cumulative, [10, 50, 90], axis=0)

    _deterministic = _annual_base * np.cumprod(np.full(_years, 1 + _mu))

    _fig, _ax = plt.subplots(figsize=(10, 5))
    _ax.fill_between(
        _x_labels,
        _annual_p10,
        _annual_p90,
        alpha=0.25,
        color=COLORS["accent"],
        label="P10-P90 annual range",
    )
    _ax.plot(
        _x_labels,
        _annual_p50,
        color=COLORS["accent"],
        linewidth=2.5,
        label="P50 annual cost",
    )
    _ax.plot(
        _x_labels,
        _deterministic,
        color=COLORS["reference"],
        linestyle="--",
        linewidth=1.3,
        label="Deterministic line (for comparison)",
    )
    _ax.axhline(y=_annual_base, color=COLORS["text_light"], linestyle=":", linewidth=1, alpha=0.7)
    _ax.annotate(
        f"2024 baseline: \\${_annual_base:.1f}B",
        xy=(2025, _annual_base), xytext=(2025 + _years * 0.2, _annual_base * 0.82),
        fontsize=FONTS["annotation"], color=COLORS["reference"],
        arrowprops=dict(arrowstyle="->", color=COLORS["reference"], lw=0.8),
    )

    _final_p50 = _annual_p50[-1]
    _final_p10 = _annual_p10[-1]
    _final_p90 = _annual_p90[-1]
    _ax.annotate(
        f"P50: \\${_final_p50:,.1f}B/yr\nP10-P90: \\${_final_p10:,.1f}B-\\${_final_p90:,.1f}B",
        xy=(_x_labels[-1], _final_p50),
        xytext=(_x_labels[-1] - _years * 0.28, _final_p90 * 1.06),
        fontsize=FONTS["annotation"], fontweight="bold", color=COLORS["accent"],
        arrowprops=dict(arrowstyle="->", color=COLORS["accent"], lw=1.2),
    )

    _ax.set_xlabel("Year", fontsize=FONTS["axis_label"])
    _ax.set_ylabel("Annual socialized cost ($B)", fontsize=FONTS["axis_label"])
    _ax.set_xlim(_x_labels[0] - 0.5, _x_labels[-1] + 0.5)
    _ax.set_ylim(0, _annual_p90.max() * 1.25)
    _ax.legend(loc="upper left", fontsize=FONTS["annotation"] - 1)
    plt.tight_layout()

    _cum_final_p10 = _cum_p10[-1]
    _cum_final_p50 = _cum_p50[-1]
    _cum_final_p90 = _cum_p90[-1]

    mo.vstack([
        mo.md(
            f"# Probabilistic projection to {int(_x_labels[-1])}: "
            f"P50 annual \\${_final_p50:,.1f}B (P10-P90: \\${_final_p10:,.1f}B-\\${_final_p90:,.1f}B)"
        ),
        mo.as_html(_fig),
        mo.md(
            f"**Cumulative socialized cost over {_years} years** "
            f"(P10/P50/P90): \\${_cum_final_p10:,.1f}B / \\${_cum_final_p50:,.1f}B / "
            f"\\${_cum_final_p90:,.1f}B.\n\n"
            f"Model setup: {_draws:,} draws, annual growth ~ N({_mu:.1%}, {_sigma:.1%}), "
            f"shock probability {_shock_prob:.0%}, shock impact {_shock_impact:.1%}, "
            f"queue-throughput improvement {_throughput_gain:.1%}/yr. This follows an "
            f"ESIG-style uncertainty framing: probabilistic bands instead of a single line."
        ),
    ])
    plt.close(_fig)
    return


@app.cell
def _(COLORS, cfg, horizontal_bar_ranking, lag_by_company_region, save_fig):
    _lag = (
        lag_by_company_region.dropna(subset=["implied_lag_years"])
        .sort_values("implied_lag_years", ascending=False)
        .head(10)
    )
    _labels = [
        f"{row['ticker']} - {row['region']}"
        for _, row in _lag.iterrows()
    ]
    _values = _lag["implied_lag_years"].tolist()

    fig_lag = horizontal_bar_ranking(
        _labels,
        _values,
        "Implied queue-to-service lag proxy by company-region exposure",
        xlabel="Queue GW / 2024 in-service GW (years, proxy)",
        highlight_indices=[0, 1, 2],
        highlight_color=COLORS["accent"],
    )
    save_fig(fig_lag, cfg.img_dir / "dd002_capex_lag_proxy.png")
    return


@app.cell(hide_code=True)
def _(cfg, lag_by_company_region, mo, stats):
    _lag_chart = mo.image(
        src=(cfg.img_dir / "dd002_capex_lag_proxy.png").read_bytes(), width=800
    )
    _table = lag_by_company_region[
        [
            "ticker",
            "region",
            "allocated_capex_bn",
            "queue_gw",
            "in_service_gw",
            "implied_lag_years",
        ]
    ].copy()
    _table = _table.rename(
        columns={
            "allocated_capex_bn": f"allocated_capex_{stats['capex_lag_year']}_bn",
            "queue_gw": "queue_gw_latest",
            "in_service_gw": "in_service_2024_gw",
            "implied_lag_years": "lag_proxy_years",
        }
    )
    mo.vstack(
        [
            mo.md(
                f"""
    ## Signature Metric: CapEx -> Interconnection -> In-Service Lag

    {_lag_chart}

    This metric links company capex exposure to regional queue congestion and
    realized 2024 in-service additions. It is a **throughput lag proxy**:
    `queue_gw_latest / in_service_2024_gw`.
    """
            ),
            mo.as_html(_table.head(20)),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.callout(
        mo.md(
            """
    ## Methods and Reproducibility

    Detailed methods, source-date tables, and SQL hash registry are published in:
    `notebooks/dd002_grid_modernization/99_methods_and_sources.py`.
    """
        ),
        kind="info",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Three Spillover Scenarios
    """)
    return


@app.cell(hide_code=True)
def _(cfg, mo):
    _scenarios = mo.image(
        src=(cfg.img_dir / "dd002_three_scenarios.png").read_bytes(), width=800
    )
    mo.md(
        f"""
    {_scenarios}

    The question "does anyone else benefit?" has three possible answers,
    depending on regulatory choices being made now:

    ### Scenario 1: Pure Spillover
    Grid upgrades driven by data center demand improve reliability and
    capacity for all users. New substations serve not just the data center
    but the surrounding community. Transmission upgrades reduce congestion
    for existing generators. The data center is a catalyst for grid
    modernization that was needed anyway.

    *This happens when:* Interconnection upgrades are designed for shared
    benefit, cost allocation reflects the broader value, and utilities
    invest ahead of demand.

    ### Scenario 2: Captured Benefit
    Data centers go behind-the-meter, building their own generation and
    bypassing the grid entirely. The grid gets nothing — no investment,
    no modernization, no shared benefit. Meanwhile, existing ratepayers
    face higher costs as the utility's fixed costs are spread over a
    smaller base.

    *This happens when:* Queue wait times are too long, cost allocation
    rules are hostile to large loads, and permitting favors on-site
    generation over grid connection.

    ### Scenario 3: Cost Shifting
    Data centers connect to the grid but shift upgrade costs to other
    ratepayers. The grid modernizes, but residential customers bear
    the cost. Public backlash grows as electricity bills rise, leading
    to political pressure against data center expansion.

    *This happens when:* Cost allocation rules allow socialization,
    utility regulators do not require cost-causation, and the political
    environment does not yet constrain data center growth.

    **The current reality is a mix of all three**, and the ratio is
    determined by regulatory choices being made right now — FERC cost
    allocation rules, state PUC proceedings, and utility planning
    processes. Part 3 formalizes this as a feedback model.

    ---

    ## What Comes Next

    Part 1 asked **what** is getting built. Part 2 asked **who pays**
    and **who benefits**. Part 3 formalizes the feedback architecture
    that determines whether the system tips toward grid modernization
    for everyone or private infrastructure for a few.

    ---

    ### Sources

    - LBNL "Queued Up: 2025 Edition" — U.S. interconnection queue data through 2024
    - Union of Concerned Scientists (September 2025), "Connection Costs Loophole
      Costs Customers Over \\$4 Billion" — PJM data center cost socialization study
    - JLARC / E3 (December 2024), "Data Centers in Virginia" — grid infrastructure
      and customer rate impact analysis
    - FERC Docket EL25-49-000 (December 18, 2025) — cost allocation order for
      co-located loads in PJM
    - PJM interconnection queue data — via interconnection.fyi and PJM Data Miner
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
