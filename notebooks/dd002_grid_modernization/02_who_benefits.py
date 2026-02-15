import marimo

__generated_with = "0.19.11"
app = marimo.App()


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

    import pandas as pd
    import numpy as np

    from src.notebook import setup, save_fig
    from src.data.db import query
    from src.plotting import (
        stacked_bar,
        waterfall_chart,
        horizontal_bar_ranking,
    )

    cfg = setup()
    return (
        cfg,
        horizontal_bar_ranking,
        mo,
        pd,
        save_fig,
        stacked_bar,
        waterfall_chart,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## The Interconnection Queue: 2,300 GW Waiting

    Every new power plant — solar farm, gas turbine, battery installation —
    must apply to connect to the grid through the interconnection queue.
    The queue is managed by regional grid operators (ISOs/RTOs) and requires
    engineering studies, cost estimates, and utility agreements before a
    project can proceed.

    As of 2024, the U.S. interconnection queue contains approximately
    **2,300 GW** of proposed projects (roughly 1,400 GW of generation and
    890 GW of storage) — roughly double the country's installed generation
    capacity. The median time from interconnection request to commercial
    operation exceeds **4 years** for projects built since 2018. Only about
    **13%** of projects that enter the queue are ever built.

    There are early signs of improvement. FERC Order 2023 reforms and high
    withdrawal rates have begun reducing queue backlog — the LBNL 2025
    edition shows a 12% decrease in active queue volume from the prior year.
    But the structural bottleneck remains severe.

    This is the binding constraint on AI infrastructure. It does not matter
    how many renewable PPAs a hyperscaler signs if the generation cannot
    connect to the grid for half a decade.
    """)
    return


@app.cell
def _(cfg, horizontal_bar_ranking, save_fig):
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
    _backlog_gw = [
        580, 470, 350, 310, 290,
        120, 80, 200, 180,
    ]

    fig_queue = horizontal_bar_ranking(
        _regions,
        _backlog_gw,
        "PJM and MISO carry the largest interconnection backlogs",
        xlabel="Queue Backlog (GW)",
        highlight_indices=[0, 4],  # PJM and ERCOT — major data center regions
        highlight_color="#e74c3c",
    )
    save_fig(fig_queue, cfg.img_dir / "dd002_queue_by_region.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo):
    _queue_chart = mo.image(
        src=(cfg.img_dir / "dd002_queue_by_region.png").read_bytes(), width=800
    )
    mo.md(
        f"""
    {_queue_chart}

    PJM — the grid operator covering the mid-Atlantic from Virginia to
    Illinois — carries the largest backlog at ~580 GW. This is not
    coincidental: PJM is home to Northern Virginia's data center corridor,
    the densest concentration of data center capacity on Earth. MISO
    (Midwest), CAISO (California), and ERCOT (Texas) follow.

    The queue is dominated by solar (over 60% of proposed capacity),
    battery storage (~30%), and wind. Gas projects are a small fraction
    — the economics have shifted so decisively that most proposed
    generation is clean. The bottleneck is not the business case for
    renewables; it is the administrative and engineering process of
    connecting them to the grid.
    """
    )
    return


@app.cell
def _(cfg, pd, save_fig, stacked_bar):
    # Queue composition by fuel type — LBNL Queued Up 2025 data
    # Source: https://emp.lbl.gov/queues

    _comp = pd.DataFrame({
        "year": [2019, 2020, 2021, 2022, 2023, 2024],
        "solar": [180, 250, 350, 480, 550, 620],
        "battery": [30, 70, 160, 300, 400, 520],
        "wind": [250, 230, 200, 180, 170, 160],
        "gas": [40, 35, 30, 25, 25, 20],
        "hybrid": [10, 30, 80, 150, 200, 280],
        "other": [50, 45, 40, 35, 30, 25],
    })

    _colors = {
        "solar": {"color": "#f0b429", "label": "Solar"},
        "battery": {"color": "#7b68ee", "label": "Battery Storage"},
        "wind": {"color": "#4ecdc4", "label": "Wind"},
        "gas": {"color": "#e74c3c", "label": "Gas"},
        "hybrid": {"color": "#2ecc71", "label": "Hybrid (Solar+Storage)"},
        "other": {"color": "#999999", "label": "Other"},
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
    {_comp_chart}

    The composition of the queue reveals an important structural fact:
    **the pipeline of proposed generation is overwhelmingly clean energy.**
    Solar, battery storage, and hybrid projects (solar paired with batteries)
    account for over 85% of queued capacity. Gas is roughly 6%.

    This means that even under the most aggressive AI demand scenarios,
    the generation that eventually connects to the grid will be predominantly
    renewable. The constraint is not technology choice — it is queue throughput.
    Anything that speeds up interconnection (FERC reform, utility process
    improvements, standardized studies) disproportionately benefits clean energy.
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
        "$4.36B in PJM data center grid costs shifted to ratepayers in 2024 (estimated breakdown)",
        total_label="Total\nsocialized",
    )
    save_fig(fig_cost, cfg.img_dir / "dd002_cost_allocation.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo):
    _cost_chart = mo.image(
        src=(cfg.img_dir / "dd002_cost_allocation.png").read_bytes(), width=800
    )
    mo.md(
        f"""
    ## The $4.36 Billion Question

    {_cost_chart}

    When a data center connects to the grid, it triggers upgrades: new
    substations, transmission reinforcement, distribution capacity. The
    question is who pays.

    The Union of Concerned Scientists identified more than 150 local
    transmission projects from 2022 to 2024, with **$4.36 billion** in
    data center transmission connection costs approved in **2024 alone**
    and passed to PJM ratepayers across seven states. Over 95% of projects
    socialized their costs to all utility customers — meaning residential
    customers in Virginia, Ohio, and Pennsylvania are subsidizing grid
    upgrades that primarily serve hyperscaler data centers.

    The chart above breaks this total into estimated categories based on
    typical transmission project cost structures. The $4.36B total is
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
    - PJM must submit tariff amendments by February 16, 2026.
    - Three new transmission service options established for large loads.

    **What this changes:** Co-located loads (the xAI model — data center
    at a power plant site) can no longer free-ride on grid services they
    use but do not pay for.

    **What this does not change:** Standard grid interconnection cost
    allocation. The $4.36 billion UCS finding covers projects that connect
    through the normal process, not co-location. The broader cost
    allocation question — who pays when data center demand requires
    grid upgrades — remains unresolved.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## The Virginia Case Study

    Virginia is the most advanced example of the "who benefits" tension.

    The Virginia Joint Legislative Audit and Review Commission (JLARC)
    commissioned Energy + Environmental Economics (E3) to study the
    impact of data center growth on the state's grid. The December 2024
    report found:

    - **Northern Virginia hosts the densest concentration of data center
      capacity in the world** — approximately 25% of capacity in the
      Americas.
    - Data center load growth is driving **billions in grid upgrades** that
      will be socialized across Dominion Energy's residential rate base.
    - Under high-growth scenarios, residential electricity bills could
      increase by approximately **$444 per year ($37 per month) by 2040**.
    - The Virginia Clean Economy Act's 100% clean energy mandate by 2045
      is in tension with the pace of data center demand — it may not be
      possible to build clean generation fast enough.

    Virginia is the canary in the coal mine. What is happening there will
    happen in every state with significant data center growth: Texas,
    Georgia, Ohio, Arizona. The policy response in Virginia will set
    precedent for the country.
    """)
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
def _(growth_slider, mo, years_slider):
    # Simple projection: $4.36B approved in 2024 → compound growth
    _annual_base = 4.36  # $4.36B/year baseline (2024 approvals)
    _rate = growth_slider.value
    _years = int(years_slider.value)

    _projected = sum(
        _annual_base * (1 + _rate) ** y for y in range(_years)
    )

    mo.md(
        f"""
    ### Projected Socialized Grid Costs

    At **{_rate:.0%}** annual data center load growth over **{_years} years**:

    - **Projected total socialized cost: ${_projected:,.1f} billion**
    - Annual cost in final year: **${_annual_base * (1 + _rate) ** _years:,.2f} billion/year**

    This is a rough projection based on the UCS baseline of $4.36B
    approved in 2024. Actual costs depend on FERC reform, utility
    practices, and state regulatory responses.
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Three Spillover Scenarios

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
      Costs Customers Over $4 Billion" — PJM data center cost socialization study
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
