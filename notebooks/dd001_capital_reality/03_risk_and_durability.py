import marimo

__generated_with = "0.19.11"
app = marimo.App(
    width="medium",
    app_title="DD-001: Risk and Durability",
    css_file="../../src/notebook_theme/custom.css",
    html_head_file="../../src/notebook_theme/head.html",
)


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    # Who Holds the Downside? Risk Distribution in the AI Buildout

    *Thandolwethu Zwelakhe Dlamini*

    ---

    The previous two notebooks documented what is being spent (~\\${stats['capex_2025']:.0f}B in 2025)
    and how slowly it converts to operating infrastructure. This notebook asks the
    distributional question: when long-lived infrastructure outlasts the demand thesis
    that justified it, *who holds the loss*?

    The answer has shifted materially through 2025. The entities best positioned to
    evaluate AI demand — the tech giants — have systematically moved financial exposure
    outward to entities with less visibility into demand trajectories. Special purpose
    vehicles, short-term leases, and concentrated neocloud dependencies have distributed
    risk to private credit, pension funds, and rural communities — on timescales that
    run decades beyond the companies' exit options.
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
        legend_below, mo, mpatches, np, plt, query, save_fig,
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
        "openai_coreweave_commitment_bn": float(citations["openai_coreweave_commitment_bn"]),
        "coreweave_interest_rate_pct": int(citations["coreweave_interest_rate_pct"]),
        "openai_msft_compute_promise_bn": int(citations["openai_msft_compute_promise_bn"]),
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
def _(COLORS, CONTEXT, FIGSIZE, FONTS, cfg, chart_title, legend_below, mpatches, np, plt, save_fig, stats):
    # Risk Exposure Timeline — horizontal Gantt
    # Each row: one risk bearer; bar spans their exposure window
    # Color encodes exit optionality: CONTEXT = can exit; COLORS["negative"] = locked in
    _entities = [
        ("Tech giants\n(Meta, MSFT)", 2025, 2030, "exit"),
        ("Neoclouds\n(CoreWeave, Nebius)", 2025, 2035, "locked"),
        ("Private credit\n(Pimco, Blue Owl)", 2025, stats["beignet_bond_maturity"], "locked"),
        ("Pension funds\n& endowments", 2025, 2055, "locked"),
        ("Rural communities\n(Indiana, Louisiana…)", 2025, 2070, "permanent"),
    ]
    _color_map = {
        "exit": CONTEXT,
        "locked": COLORS["negative"],
        "permanent": COLORS["negative"],
    }
    _alpha_map = {"exit": 0.6, "locked": 0.8, "permanent": 1.0}

    fig_risk, _ax = plt.subplots(figsize=(FIGSIZE["wide"][0], FIGSIZE["wide"][1] * 0.9))

    _y_positions = np.arange(len(_entities))
    _bar_height = 0.55

    for _i, (_label, _start, _end, _kind) in enumerate(_entities):
        _clr = _color_map[_kind]
        _alpha = _alpha_map[_kind]
        _ax.barh(
            _i, _end - _start, left=_start, height=_bar_height,
            color=_clr, alpha=_alpha, edgecolor="white", linewidth=0.5,
        )
        # End-year annotation inside or just past bar
        _ax.text(
            _end + 0.3, _i, str(_end) if _kind != "permanent" else "2070+",
            va="center", ha="left", fontsize=FONTS["annotation"] - 1,
            color=_clr if _kind != "exit" else COLORS["text_dark"],
            fontweight="bold",
        )
        # Duration annotation inside bar (if wide enough)
        _dur = _end - _start
        if _dur >= 8:
            _ax.text(
                _start + _dur / 2, _i, f"{_dur} yr",
                va="center", ha="center", fontsize=FONTS["annotation"] - 1,
                color="white" if _kind != "exit" else COLORS["text_dark"],
            )

    # "Today" marker
    _today = 2026
    _ax.axvline(_today, color=COLORS["accent"], linewidth=2, linestyle="-", alpha=0.8, zorder=5)
    _ax.text(_today + 0.2, len(_entities) - 0.1, "Today", fontsize=FONTS["annotation"],
             color=COLORS["accent"], fontweight="bold", va="top")

    # Meta exit window annotation
    _ax.annotate(
        f"Meta can\nexit ~{stats['meta_beignet_exit_year']}",
        xy=(stats["meta_beignet_exit_year"], 0),
        xytext=(stats["meta_beignet_exit_year"] + 2, 0.8),
        fontsize=FONTS["annotation"] - 1, color=CONTEXT,
        arrowprops=dict(arrowstyle="->", color=CONTEXT, linewidth=1),
        ha="left",
    )

    _ax.set_yticks(_y_positions)
    _ax.set_yticklabels(
        [e[0] for e in _entities],
        fontsize=FONTS["tick_label"],
    )
    _ax.set_xlabel("Year", fontsize=FONTS["axis_label"])
    _ax.tick_params(axis="x", labelsize=FONTS["tick_label"])
    _ax.set_xlim(2024, 2076)
    _ax.spines[["top", "right"]].set_visible(False)

    legend_below(
        _ax,
        handles=[
            mpatches.Patch(facecolor=CONTEXT, alpha=0.6, label="Can exit"),
            mpatches.Patch(facecolor=COLORS["negative"], alpha=0.9, label="Locked in"),
        ],
        labels=["Can exit (3-5 yr leases)", "Locked in (debt / bond maturity)"],
        ncol=2,
    )
    chart_title(
        fig_risk,
        "The further from the investment decision, the longer the exposure",
    )
    plt.tight_layout()
    save_fig(fig_risk, cfg.img_dir / "dd001_risk_exposure_timeline.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo):
    _chart = mo.image(
        src=(cfg.img_dir / "dd001_risk_exposure_timeline.png").read_bytes(), width=850
    )
    mo.md(f"""
    # The further from the investment decision, the longer the exposure

    {_chart}

    *Horizontal bars show the financial exposure window for each risk bearer.
    Tech giants (Meta, Microsoft) signed 3-5 year leases — they can exit the
    arrangements as early as 2028-2030. Neocloud operators borrowed at 10%+
    interest rates on 10-year debt to build the capacity. Pimco sold bonds
    maturing in 2049 to pension funds and endowments. Rural communities bear
    permanent grid, water, and community externalities. The "Today" marker is 2026.
    Sources: NYT (Dec 2025), CoreWeave S-1/A (2025), S&P Global Ratings.*
    """)
    return


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    ---

    ## The Risk Distribution Mechanisms

    The mechanisms fall into three categories:

    **1. Special Purpose Vehicles (SPVs)**

    Meta's Louisiana data center is the clearest case. Meta created Beignet Investor
    LLC and worked with Blue Owl Capital to borrow ~\\${stats['meta_beignet_financing_bn']}B for the project. Blue Owl
    provided 80% of the financing; Pimco sold bonds maturing in **{stats['beignet_bond_maturity']}** to its
    clients — insurers, pension funds, endowments, and financial advisers. Meta
    agreed to "rent" the facility through a series of {stats['meta_beignet_lease_years']}-year leases, classifying the
    arrangement as operating cost rather than debt.

    The risk asymmetry: Meta can walk away as early as {stats['meta_beignet_exit_year']}. The bondholders are
    committed through {stats['beignet_bond_maturity']}. If AI demand underwhelms, the data center's value
    depreciates — and that loss lands on pension fund portfolios and insurance
    company balance sheets, not Meta's.

    A Columbia Business School accounting professor drew explicit parallels to the
    off-balance-sheet vehicles that preceded the dot-com bust (NYT, Dec 2025). The
    comparison is directional, not exact — Meta has provided protections that future
    deals may not require — but the structural pattern is recognizable.

    **2. Neocloud Leases**

    Microsoft signed over \\${stats['msft_neocloud_total_bn']}B in 3-5 year data center leases in a single quarter
    (Sep–Nov 2025), spread across at least four neocloud providers. These shorter
    contracts give Microsoft flexibility: computing power that shows up as day-to-day
    operating expense rather than decades-long capital commitment.

    The counterparties — Nebius (ex-Yandex founder, \\${stats['msft_nebius_deal_bn']}B), Nscale (privately held, British,
    \\${stats['msft_nscale_deal_bn']}B), Iren (former bitcoin miner, \\${stats['msft_iren_deal_bn']}B), Lambda — are building the data centers
    with their own capital. If Microsoft's demand shifts after the lease terms end, these
    smaller companies and their lenders absorb the stranded-asset risk.

    The pattern mirrors how large retailers use franchise and lease structures to
    maintain optionality while franchisees bear the capital risk. The difference is
    scale: multi-billion-dollar infrastructure assets with 20-40 year physical lifetimes
    financed against 3-5 year demand commitments.

    **3. Downstream Concentration: The CoreWeave–OpenAI Chain**

    CoreWeave, the largest neocloud, has tied its future to a small number of
    customers — borrowing billions at {stats['coreweave_interest_rate_pct']}%+ interest rates to build capacity
    that OpenAI has committed to purchase (up to \\${stats['openai_coreweave_commitment_bn']}B). Microsoft is
    CoreWeave's dominant customer, representing ~62% of 2024 revenue (CoreWeave
    S-1/A, March 2025, EDGAR CIK 2051911). OpenAI has separately promised to route
    \\${stats['openai_msft_compute_promise_bn']}B in computing through Microsoft — creating a dependency chain that runs
    CoreWeave → OpenAI → Microsoft's continued AI investment.

    CoreWeave's viability depends on OpenAI's growth, which depends on consumer and
    enterprise adoption of AI products that — as the revenue section documented —
    haven't yet generated returns matching the infrastructure investment.

    ### What This Means for the Analysis

    The risk distribution pattern has a directional implication for the durability
    question: **the entities best positioned to evaluate AI demand (the tech giants)
    are systematically reducing their exposure, while entities with less visibility
    into demand trajectories (private credit, pension funds, neocloud startups)
    are absorbing it.**

    This doesn't mean the investments are wrong. It means the market structure is
    pricing risk asymmetrically — and if the demand thesis proves incorrect, the
    consequences will be distributed across the financial system in ways that the
    companies' own balance sheets won't fully reflect.

    | Risk bearer | Mechanism | Exposure window | Visibility into AI demand |
    | :--- | :--- | :--- | :--- |
    | Tech giants (Meta, MSFT) | SPVs, short-term leases | 3-5 years (can exit) | **High** (own the products) |
    | Neoclouds (CoreWeave, Nebius) | Debt-funded capacity build | 10-20 years (debt terms) | Medium (contracted, not owned) |
    | Private credit / bondholders | Bond purchases, loans | 20-25 years (bond maturity) | **Low** (financial instruments) |
    | Pension funds / endowments | Bond portfolios | Indefinite (asset allocation) | **None** (downstream investors) |
    | Rural communities | Tax incentives, grid load | **Permanent** (infrastructure) | **None** |

    **Regulatory context:** FERC's AD24-11 Policy Statement (May 2024) directly
    addresses the cost allocation question: the Commission affirmed that
    cost-causation principles apply to large loads like data centers and that upgrade
    costs "may be inappropriately socialized" across existing ratepayers if not
    allocated to the triggering customer. The Policy Statement is non-binding; no
    Final Rule has been issued. FERC Order 2023 (July 2023) is distinct — it governs
    *generator* (supply-side) interconnection reform and does not apply to large-load
    data center interconnection. The gap between the AD24-11 policy intent and any
    binding rule means cost allocation for Rainier-scale load additions remains
    an open regulatory question that will shape who ultimately pays for grid upgrades.

    *Sources: NYT, "How Tech's Biggest Companies Are Offloading the Risks of the
    A.I. Boom," Dec 15, 2025 (Weise & Tan); CoreWeave S-1/A, March 2025 (EDGAR CIK
    2051911); FERC AD24-11 Policy Statement, May 2024.*
    """)
    return


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    ---

    ## Where This Research Goes Next

    The three notebooks in this series establish the premise: AI capital is real and
    accelerating, conversion is slow and physical-constraint-bound, and the financial
    risk of disappointment has been moved to entities furthest from the decision.

    The remaining deep dives trace what happens when capital *does* convert:

    - **DD-002: Grid Modernization** (active) — What generation mix is getting built?
      Which fuel types? Where geographically? Who pays for the grid upgrades? The
      Project Rainier case provides an anchor: one campus in Indiana accounts for ~half
      of the state's projected load growth through 2030, with the utility planning
      {stats['aep_gas_share_pct']}% natural gas. Meta's Louisiana data center ({stats['meta_louisiana_dc_gw']} GW) and OpenAI's
      Texas facility ({stats['openai_texas_dc_gw']} GW) are comparable in scale. DD-002 traces whether
      these facility-level patterns aggregate into a grid-wide shift in generation mix
      and emissions trajectory.
    - **DD-003: Labor Markets** (scoping) — Who gets hired and displaced? What are the
      temporal dynamics of build-phase construction employment vs. long-term operations
      staffing vs. knowledge-work displacement?
    - **CS-4: Material Supply Chains** (not started) — GOES steel, copper, transformers.
      Where does concentration risk bind?

    ---

    *Sources: SEC EDGAR (10-K/10-Q filings via yfinance, through Q4 2025),
    Yahoo Finance (market caps, Feb 2026), FRED (BEA PNFI series, Q2 2025 SAAR),
    Sequoia Capital ("The \\$600B Question," Sep 2024), CreditSights (AI capex
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
    CoreWeave S-1/A, March 2025 (EDGAR CIK 2051911).
    FERC AD24-11 Policy Statement, May 2024.*
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


if __name__ == "__main__":
    app.run()
