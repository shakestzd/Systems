import marimo

__generated_with = "0.19.11"
app = marimo.App(
    width="medium",
    app_title="DD-004 The Cost-Liability Map",
    css_file="../../src/notebook_theme/custom.css",
    html_head_file="../../src/notebook_theme/head.html",
)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # AI Capital and Who Pays for the Grid
    ## Part 3 — The Cost-Liability Map

    *Thandolwethu Zwelakhe Dlamini*

    ---

    AI infrastructure creates durable physical obligations, but the capital
    structure that builds it is designed to exit. This notebook maps the
    asymmetry: who owns assets, who bears maintenance, and what determines
    who is left holding the cost when the capital moves.

    The durability taxonomy from DD-001 classifies investments by asset
    lifespan. Here it is extended to classify by *liability holder*:

    - **Equipment** (6-year life): sits on hyperscaler balance sheet — they
      bear the depreciation risk. Portable: can be redeployed to other facilities.
    - **Data center construction** (40-year life): on hyperscaler balance sheet,
      but land and building are geographically fixed. Harder to repurpose.
    - **Grid upgrades** (30–40-year life): in utility rate base — on *ratepayer*
      tabs. Not owned by the hyperscaler at all. Even if the data center exits,
      the amortization continues.
    - **Tax abatements** (foregone public revenue): sunk cost to the state
      regardless of data center tenure.

    The key regulatory lever is FERC AD24-11: an active FERC proceeding on
    whether large loads (data centers) should pay their own interconnection
    upgrade costs, or have those costs socialized across all ratepayers — the
    same cost-causation question resolved for generators in Order 2023.

    **This is Part 3 of three.** It asks: what is the full cost-liability map
    across the AI infrastructure buildout, and which regulatory decisions
    determine who pays?
    """)
    return


@app.cell
def _():
    import sys

    import marimo as mo

    sys.path.insert(0, str(mo.notebook_dir().parent.parent))

    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np
    import pandas as pd

    from src.data.db import query
    from src.notebook import save_fig, setup
    from src.plotting import (
        COLORS,
        CONTEXT,
        FIGSIZE,
        FONTS,
        waterfall_chart,
    )

    cfg = setup()
    return (
        COLORS,
        CONTEXT,
        FIGSIZE,
        FONTS,
        cfg,
        mo,
        mpatches,
        np,
        pd,
        plt,
        query,
        save_fig,
        waterfall_chart,
    )


@app.cell
def _(pd, query):
    # ── Data cell ──────────────────────────────────────────────────────────────

    citations = query(
        """
        SELECT key, value, value_text, unit, source_name, source_date
        FROM energy_data.source_citations
        """
    )
    cmap = citations.set_index("key")["value"].to_dict()

    iurc_cases = query(
        """
        SELECT cause_number, case_type, status, key_metric, key_metric_value,
               key_metric_unit, case_title
        FROM energy_data.dd004_iurc_cases
        ORDER BY cause_number, key_metric
        """
    )

    ferc_events = query(
        """
        SELECT event_date, event_name, docket, jurisdiction, description, status
        FROM energy_data.dd002_policy_events
        WHERE docket LIKE 'AD24%' OR docket LIKE 'EL25%' OR event_name LIKE '%cost%'
           OR event_name LIKE '%FERC%' OR event_name LIKE '%AD24%'
        ORDER BY event_date
        """
    )

    # Pull key metrics from IURC cases table
    egr = iurc_cases[iurc_cases["cause_number"] == "46301"].set_index("key_metric")
    tariff = iurc_cases[iurc_cases["cause_number"] == "46097"].set_index("key_metric")

    total_icap_mw = float(egr.loc["total_icap_need_mw", "key_metric_value"])
    gas_ct_mw = float(egr.loc["new_gas_ct_mw", "key_metric_value"])
    clean_energy_mw = float(egr.loc["clean_energy_ceiling_mw", "key_metric_value"])
    tier1_mw = float(tariff.loc["tier1_threshold_mw", "key_metric_value"])
    tier2_mw = float(tariff.loc["tier2_threshold_mw", "key_metric_value"])

    # From source_citations
    stranded_cost_1gw_bn = cmap["iurc_imp_ll_stranded_cost_1gw_bn"]
    collateral_m = cmap["iurc_imp_ll_collateral_m"]
    demand_charge_kw = cmap["iurc_imp_ll_demand_charge_kw"]
    capacity_deficit_mw = cmap["iurc_egr_capacity_deficit_2030_mw"]
    dispatchable_icap_mw = cmap["iurc_egr_dispatchable_icap_mw"]
    signed_mw = cmap["iurc_imp_large_load_signed_mw"]
    oregon_mw = cmap["iurc_oregon_ccgt_mw"]
    oregon_eol = int(cmap["iurc_oregon_eol_year"])
    amazon_bn = cmap["iurc_amazon_indiana_investment_bn"]
    peak_2024_gw = cmap["iurc_imp_peak_2024_gw"]
    peak_2030_gw = cmap["iurc_imp_peak_2030_gw"]
    transmission_cost_m = cmap["iurc_imp_ll_transmission_cost_annual_m"]

    stats = {
        "total_icap_mw": int(total_icap_mw),
        "gas_ct_mw": int(gas_ct_mw),
        "clean_energy_mw": int(clean_energy_mw),
        "tier1_mw": int(tier1_mw),
        "tier2_mw": int(tier2_mw),
        "stranded_cost_1gw_bn": stranded_cost_1gw_bn,
        "collateral_m": int(collateral_m),
        "demand_charge_kw": demand_charge_kw,
        "capacity_deficit_mw": int(capacity_deficit_mw),
        "dispatchable_icap_mw": int(dispatchable_icap_mw),
        "signed_mw": int(signed_mw),
        "oregon_mw": int(oregon_mw),
        "oregon_eol": oregon_eol,
        "amazon_bn": int(amazon_bn),
        "peak_2024_gw": peak_2024_gw,
        "peak_2030_gw": int(peak_2030_gw),
        "transmission_cost_m": int(transmission_cost_m),
        # Derived
        "gas_ct_pct_of_icap": round(gas_ct_mw / total_icap_mw * 100),
        "peak_growth_gw": round(peak_2030_gw - peak_2024_gw, 1),
        "peak_growth_pct": round((peak_2030_gw - peak_2024_gw) / peak_2024_gw * 100),
    }

    return (
        cmap,
        capacity_deficit_mw,
        citations,
        clean_energy_mw,
        collateral_m,
        demand_charge_kw,
        dispatchable_icap_mw,
        egr,
        ferc_events,
        gas_ct_mw,
        iurc_cases,
        stats,
        tariff,
        tier1_mw,
        tier2_mw,
        total_icap_mw,
    )


@app.cell(hide_code=True)
def _(mo, stats):
    mo.hstack(
        [
            mo.callout(
                mo.md(
                    f"# {stats['total_icap_mw']:,} MW\nTotal capacity need in I&M's "
                    f"Indiana service territory 2025–2030 — driven by "
                    f"{stats['peak_growth_pct']:.0f}% peak load growth from data centers"
                ),
                kind="danger",
            ),
            mo.callout(
                mo.md(
                    f"# {stats['gas_ct_mw']:,} MW\nNew gas combustion turbines approved "
                    f"by IURC in January 2026 EGR Plan — {stats['gas_ct_pct_of_icap']}% "
                    f"of total capacity need, all costs to all ratepayers"
                ),
                kind="warn",
            ),
            mo.callout(
                mo.md(
                    f"# ${stats['stranded_cost_1gw_bn']:.0f}B\nStranded cost exposure per "
                    f"1 GW customer exiting I&M's service territory more than 5 years "
                    f"early — the asymmetry that defines the liability map"
                ),
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
    ## The Indiana Case Study: Four Decisions That Set Precedent

    Indiana has become the most active regulatory laboratory for the cost-liability
    question. Four proceedings between 2024 and 2026 — all before the Indiana Utility
    Regulatory Commission — establish the framework that other states will copy or contest.

    ### Decision 1: Who bears customer-specific infrastructure costs?
    IURC Cause 46097 (Final Order, February 2025) created a tiered tariff for large
    load data center customers. The structure:

    - **Tier 1** (≥{stats['tier1_mw']} MW per site): customer-specific equipment and
      customer-specific grid facilities paid directly by the customer
    - **Tier 2** (≥{stats['tier2_mw']} MW aggregate): higher minimum demand charge
    - Both tiers: minimum demand charge of **${stats['demand_charge_kw']}/kW/month**,
      ensuring I&M recovers fixed costs even if load factors are lower than projected
    - **Collateral requirement**: ${stats['collateral_m']:,}M — security against
      early exit stranding costs
    - **Stranded cost exposure**: approximately **${stats['stranded_cost_1gw_bn']:.0f}B**
      per 1 GW customer exiting more than 5 years early

    The critical asymmetry: customer-specific transmission and distribution upgrades
    go directly to the customer. **Generation capacity costs — the 1,650 MW of new gas
    turbines, the Oregon NGCC acquisition — are socialized across all ratepayers.**

    ### Decision 2: Oregon Clean Energy Center acquisition
    IURC Cause 46217 (Final Order, November 2025) approved I&M's acquisition of the
    Oregon Clean Energy Center — **{stats['oregon_mw']} MW** of natural gas combined
    cycle capacity, operational since 2017, with approximately 32 years of remaining
    life (to ~{stats['oregon_eol']}). Cost basis: all into rate base, all ratepayers.

    This is {stats['oregon_mw']} MW of gas capacity with a 32-year cost amortization
    tail whose primary justification is data center load that may or may not persist.

    ### Decision 3: EGR Plan — capacity for whom?
    IURC Cause 46301 (Final Order, January 2026) approved I&M's Expedited Generation
    Resource Plan under Indiana Code. The plan:

    - **{stats['total_icap_mw']:,} MW** total ICAP need identified for 2025–2030
    - **{stats['capacity_deficit_mw']:,} MW** projected deficit without the plan
    - Approved: **{stats['gas_ct_mw']:,} MW** new gas combustion turbines
    - Approved: up to **{stats['clean_energy_mw']:,} MW** clean energy
    - {stats['signed_mw']:,} MW of load growth is under signed agreements with I&M

    All of this capacity enters I&M's rate base. All ratepayers pay for generation
    capacity whose primary driver is data center load commitments. The EGR framework
    under Indiana Code was designed for emergency capacity situations — it is now being
    used for planned hyperscale buildout.

    ### Decision 4: Pending ARPs
    IURC Causes 46276 and 46305 (both pending) are Alternative Regulatory Plans filed
    by I&M for customer-specific clean energy arrangements. If approved, these allow
    individual large load customers to contract for dedicated clean capacity. Whether
    that capacity is direct-assigned or socialized is the open question — and why
    municipalities (Marion, Fort Wayne, South Bend) are intervening.
    """)
    return


@app.cell
def _(COLORS, CONTEXT, FIGSIZE, FONTS, cfg, plt, save_fig, stats):
    # Chart: Asset lifetime vs. liability holder — visual taxonomy
    _assets = [
        ("Server hardware\n(IT equipment)", 6, "Hyperscaler", COLORS["accent"]),
        ("Network equipment", 8, "Hyperscaler", COLORS["accent"]),
        ("Data center building", 40, "Hyperscaler", COLORS["reference"]),
        (f"Oregon NGCC\n({stats['oregon_mw']} MW)", 32, "All ratepayers", CONTEXT),
        (f"Gas CTs\n({stats['gas_ct_mw']:,} MW EGR Plan)", 28, "All ratepayers", CONTEXT),
        ("Substation upgrades", 35, "All ratepayers", CONTEXT),
        ("Transmission lines", 40, "All ratepayers", CONTEXT),
        ("Tax abatements\n(foregone revenue)", 15, "Public (sunk)", "#e8c97e"),
    ]

    fig_liab, _ax = plt.subplots(figsize=FIGSIZE["wide"])
    _y_pos = list(range(len(_assets)))

    for _i, (label, life, holder, color) in enumerate(_assets):
        _ax.barh(_i, life, color=color, height=0.6, alpha=0.9)
        _ax.text(
            life + 0.5, _i, f"{life} yr — {holder}",
            va="center", fontsize=FONTS["annotation"],
            color=COLORS["text_dark"],
        )

    _ax.set_yticks(_y_pos)
    _ax.set_yticklabels([a[0] for a in _assets], fontsize=FONTS["annotation"])
    _ax.set_xlabel("Asset Lifetime (years)", fontsize=FONTS["axis_label"])
    _ax.set_xlim(0, 55)
    _ax.axvline(x=3, color=COLORS["negative"], linestyle="--", linewidth=1.2, alpha=0.8)
    _ax.text(3.2, len(_assets) - 0.3, "Typical AI\nforecast\nhorizon (3 yr)",
             fontsize=FONTS["annotation"] - 1, color=COLORS["negative"], va="top")
    _ax.spines[["top", "right"]].set_visible(False)
    _ax.invert_yaxis()

    # Labels on each bar already identify the liability holder; no legend needed.
    plt.tight_layout()

    save_fig(fig_liab, cfg.img_dir / "dd004_liability_taxonomy.png")
    return (fig_liab,)


@app.cell(hide_code=True)
def _(cfg, mo, stats):
    _chart = mo.image(
        src=(cfg.img_dir / "dd004_liability_taxonomy.png").read_bytes(), width=850
    )
    mo.md(f"""
    # Grid assets lock in ratepayer liability for 30-40 years; AI forecast horizon is 3 years

    {_chart}

    The mismatch is structural. Hyperscalers depreciate server hardware over 6 years and
    can redeploy it elsewhere. Data center buildings have 40-year useful lives but at least
    sit on the hyperscaler's own balance sheet — they bear that amortization risk directly.

    Grid assets are different. The {stats['oregon_mw']}-MW Oregon NGCC (32-year remaining
    life) and the {stats['gas_ct_mw']:,}-MW of new gas turbines approved in the EGR Plan
    (~28-year life) enter I&M's rate base. The utility recovers those costs through rates —
    from all ratepayers — over three decades. The hyperscaler that justified the capacity
    need faces no obligation to remain a customer for that period.

    Indiana's tariff attempts to partially address this with the ${stats['collateral_m']:,}M
    collateral requirement and the ${stats['stranded_cost_1gw_bn']:.0f}B stranded cost
    exposure formula for early exit. But those provisions cover customer-specific
    infrastructure only — not the generation capacity additions that are socialized.

    A hyperscaler that exits I&M's service territory in 2035 leaves behind a 25-year
    amortization tail on gas turbines whose primary justification was their load commitment.
    """)
    return


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    ## The FERC Lever: AD24-11 and Cost Causation

    The Indiana IURC proceedings establish state-level cost allocation rules. The federal
    analogue — and the more consequential one for hyperscalers operating across multiple
    utility territories — is FERC Docket AD24-11.

    FERC AD24-11 (Policy Statement, May 2024) is a non-binding statement on how large
    loads should be treated under the Federal Power Act's cost-causation principle.
    Key language:

    - Para 15: cost-causation applies to large loads; those that cause grid upgrades
      should bear them
    - Para 22: upgrade costs "may be inappropriately socialized" across ratepayers
      under current rules
    - Para 45: AI data centers present "novel challenges" for interconnection planning

    This Policy Statement has no regulatory force. It has not advanced to a Notice of
    Proposed Rulemaking (NOPR) or Final Rule. The practical effect is that the existing
    rules — under which costs can be socialized — remain in effect.

    If FERC issues a Final Rule requiring cost-causation for large loads (as it did for
    generators in Order 2023), the cost-liability map changes substantially. The
    ${stats['transmission_cost_m']:,}M in annual transmission costs currently being
    recovered from all I&M ratepayers would instead be direct-assigned to the data
    center customers that triggered them.

    Whether that happens — and when — is the highest-leverage regulatory variable in
    the entire AI infrastructure cost story.
    """)
    return


@app.cell(hide_code=True)
def _(ferc_events, mo):
    _lines = "\n".join(
        f"- **{row['event_date']} — {row['event_name']}** "
        f"({row['jurisdiction']} {row['docket']}): {row['description']}"
        for _, row in ferc_events.sort_values("event_date").iterrows()
        if row["event_name"] and str(row["event_name"]).strip()
    ) or "_No FERC cost allocation events found in dd002_policy_events. Add entries for AD24-11 milestones._"

    mo.callout(
        mo.md(f"""
    **FERC Cost Allocation Timeline** (from `energy_data.dd002_policy_events`):

    {_lines}
    """),
        kind="info",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ---

    ## Methods and Sources

    All numerical values in this notebook are loaded from:
    - `energy_data.source_citations` — cited constants with full provenance
    - `energy_data.dd004_iurc_cases` — structured IURC regulatory case data
    - `energy_data.dd002_policy_events` — FERC and regulatory timeline

    Primary sources:
    - IURC Cause 46097, Final Order (Feb 2025) — tariff structure, thresholds, collateral
    - IURC Cause 46217, Final Order (Nov 2025) — Oregon NGCC acquisition into rate base
    - IURC Cause 46301, Final Order (Jan 2026) — EGR Plan, 1,650 MW gas CT approval
    - FERC Docket AD24-11, Policy Statement (May 2024) — cost causation for large loads
    - PJM LAS presentation, Nov 2025 — AEP zone demand requests
    """)
    return


if __name__ == "__main__":
    app.run()
