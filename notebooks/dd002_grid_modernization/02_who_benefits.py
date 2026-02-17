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
def _(query):
    # --- External source constants ---
    # LBNL "Queued Up: 2025 Edition" — https://emp.lbl.gov/queues
    _queue_total = 2_300  # GW, active queue as of end-2024
    _queue_gen = 1_400  # GW, generation projects
    _queue_storage = 890  # GW, standalone storage
    _median_years = 4  # years, median interconnection time (projects built since 2018)
    _completion_pct = 13  # %, projects that enter queue and are eventually built
    _yoy_decrease_pct = 12  # %, decrease in active queue volume (2025 vs 2024 edition)

    # UCS "Connection Costs Loophole Costs Customers Over $4 Billion" (Sep 2025)
    _ucs_cost_bn = 4.36  # $B, PJM data center grid costs socialized in 2024
    _ucs_projects = 150  # count, local transmission projects 2022-2024
    _ucs_socialized_pct = 95  # %, projects that socialized costs

    # JLARC / E3 "Data Centers in Virginia" (December 2024)
    _va_bill_annual = 444  # $/year, high-growth scenario increase by 2040
    _va_bill_monthly = _va_bill_annual / 12  # $/month
    _va_capacity_pct = 25  # %, NoVA share of Americas data center capacity

    # DB-derived: installed capacity and avg residential bill
    _installed = query(
        "SELECT SUM(nameplate_capacity_mw)/1000 as gw "
        "FROM energy_data.eia860_generators WHERE status='OP'"
    ).iloc[0, 0]
    _elec_price = query(
        "SELECT value FROM energy_data.fred_series "
        "WHERE series_id='APU000072610' ORDER BY date DESC LIMIT 1"
    ).iloc[0, 0]
    _avg_monthly_bill = round(_elec_price * 886)  # 886 kWh = EIA avg household consumption
    _avg_annual_bill = _avg_monthly_bill * 12

    stats = {
        "queue_total_gw": _queue_total,
        "queue_gen_gw": _queue_gen,
        "queue_storage_gw": _queue_storage,
        "median_years": _median_years,
        "completion_pct": _completion_pct,
        "yoy_decrease_pct": _yoy_decrease_pct,
        "ucs_cost_bn": _ucs_cost_bn,
        "ucs_projects": _ucs_projects,
        "ucs_socialized_pct": _ucs_socialized_pct,
        "va_bill_annual": _va_bill_annual,
        "va_bill_monthly": round(_va_bill_monthly),
        "va_capacity_pct": _va_capacity_pct,
        "installed_gw": round(_installed),
        "queue_ratio": round(_queue_total / _installed, 1),
        "avg_monthly_bill": _avg_monthly_bill,
        "avg_annual_bill": _avg_annual_bill,
        "avg_bill_10pct": round(_avg_annual_bill * 0.1),
    }
    return (stats,)


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
    withdrawal rates have begun reducing queue backlog — the LBNL 2025
    edition shows a {stats['yoy_decrease_pct']}% decrease in active queue volume
    from the prior year. But the structural bottleneck remains severe.

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
def _(cfg, horizontal_bar_ranking, legend_below, plt, save_fig):
    # LBNL queue data — if not loaded, use representative summary data
    # from the LBNL Queued Up 2025 Edition report
    #
    # Source: LBNL "Queued Up: 2025 Edition" — https://emp.lbl.gov/queues
    # NOTE: These figures are illustrative estimates of active queue capacity (GW)
    # by ISO/RTO as of end-2024. Regional totals are approximate and may not sum
    # to the LBNL national total of ~2,300 GW due to rounding and methodology.

    _regions = [
        "PJM", "MISO", "CAISO", "SPP", "ERCOT",
        "NYISO", "ISO-NE", "Non-ISO West", "Non-ISO Southeast",
    ]
    # Approximate active queue by ISO/RTO (GW), scaled to sum to ~2,300 GW
    # Source: LBNL "Queued Up: 2025 Edition" — regional totals are estimates
    _backlog_gw = [
        520, 420, 310, 275, 260,
        105, 70, 180, 160,
    ]

    fig_queue = horizontal_bar_ranking(
        _regions,
        _backlog_gw,
        "PJM and MISO carry the largest interconnection backlogs",
        xlabel="Queue Backlog (GW)",
        highlight_indices=[0, 4],  # PJM and ERCOT — major data center regions
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

    *Regional backlogs are approximate estimates from LBNL data. Individual
    ISO/RTO figures may not sum precisely to the national total due to
    methodology differences.*
    """
    )
    return


@app.cell
def _(cfg, pd, save_fig, stacked_bar):
    # Queue composition by fuel type — LBNL Queued Up 2025 data
    # Source: https://emp.lbl.gov/queues

    # Queue composition by fuel type — illustrative estimates based on
    # LBNL "Queued Up" annual editions (2019-2025). 2024 column sums to
    # ~2,300 GW matching the LBNL 2025 Edition national total.
    _comp = pd.DataFrame({
        "year": [2019, 2020, 2021, 2022, 2023, 2024],
        "solar": [150, 230, 380, 580, 820, 1060],
        "hybrid": [10, 30, 80, 170, 260, 350],
        "battery": [40, 80, 170, 310, 400, 470],
        "wind": [220, 210, 200, 190, 186, 184],
        "gas": [100, 90, 85, 130, 130, 140],
        "other": [40, 30, 25, 30, 54, 96],
    })

    _colors = {
        "solar": {"color": FUEL_COLORS["solar"], "label": "Solar"},
        "hybrid": {"color": CATEGORICAL[3], "label": "Hybrid (Solar+Storage)"},
        "battery": {"color": FUEL_COLORS["battery"], "label": "Battery Storage"},
        "wind": {"color": FUEL_COLORS["wind"], "label": "Wind"},
        "gas": {"color": CONTEXT, "label": "Gas"},
        "other": {"color": COLORS["reference"], "label": "Other"},
    }

    fig_comp = stacked_bar(
        _comp,
        "year",
        {k: v.copy() for k, v in _colors.items()},
        "The queue is overwhelmingly clean energy — gas is a shrinking sliver",
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
    Solar and hybrid (solar+storage) projects account for over 60% of queued
    capacity, with standalone battery storage at roughly 20% and wind at about
    8%. Gas is approximately 6% — and its share has been declining even as
    absolute volumes grow.

    This means that even under the most aggressive AI demand scenarios,
    the generation that eventually connects to the grid will be predominantly
    renewable. The constraint is not technology choice — it is queue throughput.
    Anything that speeds up interconnection (FERC reform, utility process
    improvements, standardized studies) disproportionately benefits clean energy.

    *Queue composition is illustrative, based on LBNL "Queued Up" annual
    editions. LBNL categorization changed between editions; hybrid
    (solar+storage) projects may be partially counted under both solar and
    storage in some years.*
    """
    )
    return


@app.cell
def _(cfg, save_fig, waterfall_chart):
    # Cost allocation breakdown — UCS PJM study data
    # Source: Union of Concerned Scientists, "Connection Costs Loophole
    # Costs Customers Over $4 Billion" (September 2025)

    _items = [
        ("Data center\ninterconnection", 2.1),
        ("Transmission\nreinforcement", 1.2),
        ("Distribution\nupgrades", 0.6),
        ("Shared network\nimprovements", 0.46),
    ]

    # NOTE: The category breakdown ($2.1B interconnection, $1.2B transmission,
    # $0.6B distribution, $0.46B shared network) is illustrative, estimated
    # based on typical transmission project cost structures. The UCS total of
    # $4.36B is sourced; the breakdown by category is not from the UCS report.
    fig_cost = waterfall_chart(
        _items,
        "\\$4.36B in PJM data center grid costs shifted to ratepayers in 2024 (estimated breakdown)",
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

    # \\${stats['ucs_cost_bn']:.2f}B in PJM data center grid costs shifted to ratepayers in 2024 (estimated breakdown)

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

    The chart above breaks this total into estimated categories based on
    typical transmission project cost structures. The \\$4.36B total is
    sourced from UCS; the category-level breakdown is illustrative.

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
def _(mo):
    mo.md("""
    ## FERC Responds: The December 2025 Order

    The Federal Energy Regulatory Commission addressed this directly in
    **Docket EL25-49-000** (December 18, 2025). The order directed PJM
    to create new rules for co-located loads — data centers that share a
    connection point with a power plant.

    Key provisions:

    - **Cost causation principle:** "Costs must be allocated to those who
      cause them and benefit from them."
    - Co-located data centers must pay their fair share of transmission,
      regulation, and black start services.
    - PJM was directed to submit tariff amendments by February 16, 2026.
    - Three new transmission service options established for large loads.
    """)
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
    (~\\${stats['avg_monthly_bill']}/month from BLS data). Virginia bills differ
    from the national average.*
    """
    )
    return


@app.cell
def _(mo):
    # Interactive: projected socialized cost under different growth rates
    growth_slider = mo.ui.slider(
        start=0.05,
        stop=0.25,
        step=0.01,
        value=0.15,
        label="Data center load growth rate (annual)",
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

    mo.hstack([growth_slider, years_slider], justify="space-around")
    return growth_slider, years_slider


@app.cell
def _(FONTS, growth_slider, mo, np, plt, stats, years_slider):
    # Simple projection: UCS baseline → compound growth
    _annual_base = stats["ucs_cost_bn"]  # 2024 PJM approvals
    _rate = growth_slider.value
    _years = int(years_slider.value)

    _year_range = np.arange(0, _years)
    _annual_costs = np.array([_annual_base * (1 + _rate) ** y for y in _year_range])
    _cumulative = np.cumsum(_annual_costs)
    _x_labels = 2024 + _year_range

    _fig, _ax = plt.subplots(figsize=(10, 5))
    _ax.fill_between(_x_labels, _annual_costs, alpha=0.3, color=COLORS["accent"])
    _ax.plot(_x_labels, _annual_costs, color=COLORS["accent"], linewidth=2.5)
    _ax.axhline(y=_annual_base, color=COLORS["reference"], linestyle="--", linewidth=1, alpha=0.7)
    _ax.annotate(
        f"2024 baseline: \\${_annual_base:.1f}B",
        xy=(2024, _annual_base), xytext=(2024 + _years * 0.3, _annual_base * 0.85),
        fontsize=FONTS["annotation"], color=COLORS["reference"],
        arrowprops=dict(arrowstyle="->", color=COLORS["reference"], lw=0.8),
    )

    # Annotate final year
    _final = _annual_costs[-1]
    _ax.annotate(
        f"\\${_final:,.1f}B/yr",
        xy=(_x_labels[-1], _final),
        xytext=(_x_labels[-1] - _years * 0.2, _final * 1.1),
        fontsize=FONTS["annotation"], fontweight="bold", color=COLORS["accent"],
        arrowprops=dict(arrowstyle="->", color=COLORS["accent"], lw=1.2),
    )

    _ax.set_xlabel("Year", fontsize=FONTS["axis_label"])
    _ax.set_ylabel("Annual Socialized Cost ($B)", fontsize=FONTS["axis_label"])
    _ax.set_xlim(_x_labels[0] - 0.5, _x_labels[-1] + 0.5)
    _ax.set_ylim(0, _final * 1.25)
    plt.tight_layout()

    _projected = float(_cumulative[-1])

    mo.vstack([
        mo.md(
            f"# At {_rate:.0%} annual growth, socialized grid costs reach "
            f"\\${_final:,.1f}B/year by {int(_x_labels[-1])}"
        ),
        mo.as_html(_fig),
        mo.md(
            f"**Cumulative socialized cost over {_years} years: "
            f"\\${_projected:,.1f} billion.** "
            f"This is a rough compound projection from a single year's PJM data. "
            f"It assumes costs grow at the data center load rate, which ignores "
            f"regulatory responses (like the FERC order above), cost non-linearity, "
            f"and the fact that the \\${stats['ucs_cost_bn']:.2f}B baseline is "
            f"PJM-specific, not national. Treat as directional, not predictive."
        ),
    ])
    plt.close(_fig)
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
