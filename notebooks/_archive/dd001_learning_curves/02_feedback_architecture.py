import marimo

__generated_with = "0.19.11"
app = marimo.App()


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # The Learning Curve of Power Infrastructure
    ## Part 2 — Feedback Architecture
    *Thandolwethu Zwelakhe Dlamini*
    """)
    return


@app.cell
def _():
    import sys

    import marimo as mo

    # Ensure project root is first in sys.path so src is importable
    sys.path.insert(0, str(mo.notebook_dir().parent.parent))

    import matplotlib.patches as mpatches
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd

    from src.notebook import save_fig, setup
    from src.plotting import FONTS, legend_below, multi_panel

    cfg = setup()
    return FONTS, cfg, legend_below, mo, mpatches, multi_panel, np, pd, plt, save_fig


# ── Section 1: Context ─────────────────────────────────────────────────


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## What Part 1 Established

    Part 1 decomposed transformer prices into commodity and manufacturing components
    and found a signal: material-adjusted costs have been declining for years. The
    post-2021 price surge is almost entirely a raw material and lead-time tax, not a
    manufacturing efficiency failure.

    The resulting hypothesis: **AI demand may be unlocking Wright's Law learning curves
    in the standardizable segment of transformer manufacturing.** Evaluated against
    Brian Potter's five structural conditions for learning curves, distribution
    transformers scored credibly on most.

    But Part 1's arguments were linear. The real system has feedback. This notebook
    formalizes those arguments into **causal loops** — the feedback architecture that
    determines whether the learning curve hypothesis holds under dynamic conditions.
    The outcome depends on which loops dominate, and that is a function of
    parameters that can be tested.
    """)
    return


# ── Section 2: The Causal Loop Diagram ─────────────────────────────────


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## The Feedback Architecture

    I identified ten feedback loops that govern transformer market dynamics. Three
    are **reinforcing** (self-amplifying) and seven are **balancing** (self-correcting).
    Which set dominates determines whether the learning curve hypothesis holds.

    ### Reinforcing Loops (R) — Virtuous Cycles

    **R1: Volume–Learning (Wright's Law)**
    The core hypothesis. More production → more experience → lower manufacturing costs
    → more demand → more production. This is the same mechanism that drove solar module
    costs down 99% between 1976 and 2019 (IRENA 2023). It requires standardization
    high enough for experience to accumulate — Potter's Condition #1.

    **R2: Standardization Incentive**
    Hyperscaler demand creates economic pressure to converge on fewer designs. Fewer
    designs enable automation investment. Automation increases throughput. Higher
    throughput lowers costs. Lower costs attract more demand. The Compass/Siemens
    deal (1,500 identical modular units) and Compass/Schneider ($3B, 400+ power
    centers/year) are this loop in action.

    **R3: Vertical Integration (Cleveland-Cliffs)**
    GOES demand → Cliffs revenue → investment in integrated transformer plant →
    more GOES consumption internally → reduced supply chain friction. A steel company
    building transformers is a structural change, not just a volume effect.

    ### Balancing Loops (B) — Counterforces

    **B1: Lead Time Constraint** — Orders pile up → lead times stretch to 128-144
    weeks → some projects get deferred or cancelled → demand suppressed.

    **B2: Regulatory Ratchet (DOE)** — Production visibility → regulatory scrutiny →
    efficiency standards → higher GOES grade requirements → material cost increase.
    Research finding: this is a one-time step-change (April 2029), NOT a French
    nuclear-style continuous ratchet.

    **B3: Commodity Price Feedback** — Transformer demand → copper/GOES demand →
    prices rise → unit cost rises → dampened demand.

    **B4: Capacity Expansion Delay (Sterman Boom-Bust)** — Demand signal → investment
    decision → 2-4 year construction delay → new capacity → potential overcapacity →
    investment pullback. This is the classic oscillatory dynamic from Sterman's
    *Business Dynamics*.

    **B5: SST Substitution** — High traditional costs → solid-state transformer R&D →
    SST deployment → traditional demand erosion. Research finding: 10x cost premium
    today, 2030+ for grid-scale impact. A long-fuse balancing loop.

    **B6: Labor Market Constraint** — Capacity expansion → increased demand for skilled
    technicians (winding, core assembly, testing) → wage pressure and recruitment
    delays → higher unit cost and slower capacity ramp. The U.S. transformer
    workforce is aging, and new entrants require 2-3 years of on-the-job training.
    Partially offset by R2: standardization enables automation, reducing labor
    intensity per unit.

    **B7: Trade Policy Feedback** — Domestic supply deficit → increased transformer
    imports (South Korea, Mexico, Canada) → domestic producer lobbying → tariffs and
    trade barriers → reduced imports → supply deficit persists. Factory location
    determines exposure to tariff regimes, GOES sourcing constraints, and regulatory
    jurisdiction. Cleveland-Cliffs' Weirton plant is an explicit bet on this
    dynamic — vertical integration within U.S. trade boundaries.
    """)
    return


@app.cell
def _(FONTS, cfg, legend_below, mpatches, np, plt, save_fig):
    def draw_cld():
        """Draw the causal loop diagram using matplotlib."""
        fig, ax = plt.subplots(figsize=(20, 14))
        ax.set_xlim(-1.25, 1.25)
        ax.set_ylim(-1.2, 1.2)
        ax.set_aspect("equal")
        ax.axis("off")

        # Node positions (x, y) — arranged to show loop structure
        nodes = {
            "AI Demand": (0, 0.95),
            "Transformer\nOrders": (0.7, 0.65),
            "Order\nBacklog": (0.95, 0.2),
            "Lead\nTimes": (0.95, -0.25),
            "Production\nRate": (0.5, -0.55),
            "Cumulative\nProduction": (0, -0.85),
            "Manufacturing\nExperience": (-0.5, -0.55),
            "Unit\nCost": (-0.95, -0.15),
            "Standardization": (-0.7, 0.65),
            "Manufacturing\nCapacity": (0.5, -0.1),
            "Regulatory\nStringency": (-0.95, 0.35),
            "Material\nCosts": (-0.55, 0.15),
            "Labor\nPool": (-0.25, -0.35),
            "Trade\nPolicy": (0.3, 0.85),
        }

        # Draw nodes
        for label, (x, y) in nodes.items():
            bbox = dict(
                boxstyle="round,pad=0.4",
                facecolor="white",
                edgecolor="#323034",
                linewidth=1.5,
            )
            ax.text(
                x, y, label,
                ha="center", va="center",
                fontsize=FONTS["annotation"], fontweight="bold",
                bbox=bbox, zorder=5,
            )

        # Draw edges: (from, to, polarity, color, curve_direction)
        edges = [
            # R1: Volume-Learning
            ("AI Demand", "Transformer\nOrders", "+", "#2ca02c", 0.1),
            ("Transformer\nOrders", "Order\nBacklog", "+", "#2ca02c", 0.1),
            ("Order\nBacklog", "Production\nRate", "+", "#2ca02c", 0.15),
            ("Production\nRate", "Cumulative\nProduction", "+", "#2ca02c", 0.1),
            ("Cumulative\nProduction", "Manufacturing\nExperience", "+", "#2ca02c", 0.1),
            ("Manufacturing\nExperience", "Unit\nCost", "\u2212", "#2ca02c", 0.1),
            ("Unit\nCost", "AI Demand", "\u2212", "#2ca02c", 0.15),
            # B1: Lead time
            ("Order\nBacklog", "Lead\nTimes", "+", "#d62728", 0.1),
            ("Lead\nTimes", "AI Demand", "\u2212", "#d62728", -0.3),
            # B3: Commodity
            ("Transformer\nOrders", "Material\nCosts", "+", "#ff7f0e", -0.15),
            ("Material\nCosts", "Unit\nCost", "+", "#ff7f0e", 0.1),
            # R2: Standardization
            ("AI Demand", "Standardization", "+", "#1f77b4", 0.15),
            ("Standardization", "Manufacturing\nExperience", "+", "#1f77b4", -0.2),
            # B2: Regulatory
            ("Regulatory\nStringency", "Material\nCosts", "+", "#9467bd", 0.1),
            # B4: Capacity delay
            ("Order\nBacklog", "Manufacturing\nCapacity", "+", "#8c564b", -0.2),
            ("Manufacturing\nCapacity", "Production\nRate", "+", "#8c564b", 0.1),
            # B6: Labor Market Constraint
            ("Manufacturing\nCapacity", "Labor\nPool", "+", "#17becf", 0.15),
            ("Labor\nPool", "Production\nRate", "+", "#17becf", -0.15),
            ("Labor\nPool", "Unit\nCost", "+", "#17becf", -0.15),
            # B7: Trade Policy
            ("AI Demand", "Trade\nPolicy", "+", "#e377c2", -0.1),
            ("Trade\nPolicy", "Material\nCosts", "+", "#e377c2", 0.15),
        ]

        for from_node, to_node, polarity, color, curve in edges:
            x1, y1 = nodes[from_node]
            x2, y2 = nodes[to_node]
            # Shorten arrows to not overlap with node boxes
            dx, dy = x2 - x1, y2 - y1
            dist = np.sqrt(dx**2 + dy**2)
            shrink = 0.12
            x1s = x1 + shrink * dx / dist
            y1s = y1 + shrink * dy / dist
            x2s = x2 - shrink * dx / dist
            y2s = y2 - shrink * dy / dist

            ax.annotate(
                "",
                xy=(x2s, y2s),
                xytext=(x1s, y1s),
                arrowprops=dict(
                    arrowstyle="-|>",
                    color=color,
                    linewidth=1.8,
                    connectionstyle=f"arc3,rad={curve}",
                    shrinkA=0, shrinkB=0,
                ),
                zorder=3,
            )
            # Polarity label at midpoint
            mx = (x1s + x2s) / 2 + curve * 0.3 * (-(y2s - y1s) / dist)
            my = (y1s + y2s) / 2 + curve * 0.3 * ((x2s - x1s) / dist)
            ax.text(
                mx, my, polarity,
                ha="center", va="center",
                fontsize=FONTS["annotation"], fontweight="bold",
                color=color,
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85),
                zorder=6,
            )

        # Loop labels
        loop_labels = [
            (0.25, -0.15, "R1\nVolume\u2013\nLearning", "#2ca02c"),
            (-0.35, 0.82, "R2\nStandardization", "#1f77b4"),
            (0.85, -0.05, "B1\nLead Time", "#d62728"),
            (-0.15, 0.35, "B3\nCommodity", "#ff7f0e"),
            (-0.85, 0.65, "B2\nRegulatory", "#9467bd"),
            (0.75, -0.35, "B4\nCapacity\nDelay", "#8c564b"),
            (-0.05, -0.55, "B6\nLabor", "#17becf"),
            (0.55, 0.85, "B7\nTrade\nPolicy", "#e377c2"),
        ]
        for x, y, label, color in loop_labels:
            ax.text(
                x, y, label,
                ha="center", va="center",
                fontsize=FONTS["annotation"], fontweight="bold",
                color=color,
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=color, alpha=0.7),
            )

        # Legend
        legend_elements = [
            mpatches.Patch(facecolor="#2ca02c", label="R1: Volume\u2013Learning"),
            mpatches.Patch(facecolor="#1f77b4", label="R2: Standardization"),
            mpatches.Patch(facecolor="#d62728", label="B1: Lead Time"),
            mpatches.Patch(facecolor="#ff7f0e", label="B3: Commodity"),
            mpatches.Patch(facecolor="#9467bd", label="B2: Regulatory"),
            mpatches.Patch(facecolor="#8c564b", label="B4: Capacity Delay"),
            mpatches.Patch(facecolor="#17becf", label="B6: Labor"),
            mpatches.Patch(facecolor="#e377c2", label="B7: Trade Policy"),
        ]
        legend_below(ax, handles=legend_elements, ncol=4)
        plt.tight_layout()
        return fig

    _cld_fig = draw_cld()
    save_fig(_cld_fig, cfg.img_dir / "dd001_cld.png")
    return (draw_cld,)


@app.cell(hide_code=True)
def _(cfg, mo):
    _cld_img = mo.image(
        src=(cfg.img_dir / "dd001_cld.png").read_bytes(), width=900
    )
    mo.md(f"""
    # Causal Loop Diagram: Transformer Market Dynamics

    {_cld_img}

    The green arrows trace **R1 (Volume\u2013Learning)** — the reinforcing loop at the
    center of the hypothesis. AI demand drives orders \u2192 orders become production \u2192
    production accumulates experience \u2192 experience lowers cost \u2192 lower cost invites
    more demand. The red arrows show **B1 (Lead Time)** — the balancing force that
    currently dominates. Orders accumulate in the backlog, lead times stretch to
    128\u2013144 weeks (Wood Mackenzie 2025), and demand gets deferred.

    **The model's central question:** *Under what conditions does R1 overpower B1?*
    If capacity expansion (B4) and standardization (R2) strengthen the reinforcing
    loops faster than lead times and commodity prices (B1, B3) strengthen the
    balancing loops, the system transitions to a learning-curve regime. Otherwise,
    it remains in the current scarcity equilibrium.

    The teal arrows introduce **B6 (Labor)** — a constraint that becomes binding as
    capacity scales. The pink arrows show **B7 (Trade Policy)** — the geopolitical
    feedback that determines whether the supply response is domestic, imported, or
    blocked.
    """)
    return


# ── Section 3: From Loops to Stocks and Flows ──────────────────────────


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## From Loops to Stocks and Flows

    A causal loop diagram captures feedback structure but cannot be simulated
    directly. Simulation requires translating it into **stocks** (accumulations),
    **flows** (rates of change), and **auxiliaries** (computed variables).

    The model has five stocks:

    | Stock | Units | What It Represents |
    | :--- | :--- | :--- |
    | **Cumulative Production** | Units | Total transformers produced (Wright's Law x-axis) |
    | **Order Backlog** | Units | Unfilled orders in the pipeline |
    | **Manufacturing Capacity** | Units/Year | Annual production ceiling |
    | **Standardization Fraction** | 0–1 | Share of production using standardized designs |
    | **Regulatory Stringency** | 0–1 | DOE efficiency standard tightness |

    The cost equation is the key auxiliary — it combines Wright's Law manufacturing
    cost with commodity material costs and a regulatory premium:

    ```
    Unit Cost = Manufacturing Cost + Material Cost + Regulatory Premium
    ```

    Where manufacturing cost follows Wright's Law *conditional on standardization*:

    ```
    Manufacturing Cost = Base × (Cumulative Production / Reference)^(-b × standardization_effect)
    ```

    This is the critical modeling choice: **learning is not automatic.** It scales
    with standardization. Below a threshold (~40%), manufacturing stays fragmented
    and experience doesn't compound. Above it, Wright's Law activates. This
    operationalizes Potter's Condition #1 (repetition of identical units).
    """)
    return


# ── Section 4: The PySD Model ──────────────────────────────────────────


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Loading the Model

    The stock-and-flow model is defined in a Vensim `.mdl` file at
    `src/dynamics/transformer_market.mdl`. This format is human-readable, diffs
    cleanly in git, and can also be opened in Vensim PLE (free) for visual
    inspection. PySD translates it into executable Python.
    """)
    return


@app.cell
def _(cfg):
    import pysd

    model_path = cfg.models_dir / "transformer_market.mdl"
    model = pysd.read_vensim(str(model_path))
    return model, model_path, pysd


@app.cell
def _(model):
    baseline = model.run()
    baseline.head()
    return (baseline,)


@app.cell
def _(baseline, cfg, multi_panel, save_fig):
    _panels = [
        {
            "columns": {"Cumulative Production": {"color": "#2ca02c"}},
            "title": "Cumulative Production",
            "ylabel": "Units",
        },
        {
            "columns": {"unit cost": {"color": "#d62728"}},
            "title": "Unit Cost",
            "ylabel": "$/Unit (indexed)",
        },
        {
            "columns": {
                "Order Backlog": {"color": "#ff7f0e", "label": "Order Backlog"},
                "Manufacturing Capacity": {
                    "color": "#1f77b4",
                    "linestyle": "--",
                    "label": "Mfg Capacity",
                },
            },
            "title": "Backlog vs. Capacity",
            "ylabel": "Units or Units/Year",
        },
        {
            "columns": {"Standardization Fraction": {"color": "#9467bd"}},
            "title": "Standardization Fraction",
            "ylabel": "Fraction (0\u20131)",
            "ylim": (0, 1),
        },
    ]

    _baseline_fig = multi_panel(baseline, _panels, "Baseline Simulation (2020\u20132040)")
    save_fig(_baseline_fig, cfg.img_dir / "dd001_baseline_simulation.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo):
    _baseline_img = mo.image(
        src=(cfg.img_dir / "dd001_baseline_simulation.png").read_bytes(), width=900
    )
    mo.md(f"""
    # Baseline Simulation (2020\u20132040)

    {_baseline_img}

    Under baseline parameters, cumulative production grows steadily as AI demand
    compounds. Unit cost declines — but only *after* standardization crosses the
    threshold. The order backlog initially spikes (reflecting the current lead-time
    crisis) then is gradually absorbed as capacity expansion comes online with a
    3-year delay.

    The 2029 DOE regulatory step-change appears as a one-time bump in unit cost,
    not a compounding ratchet. The system absorbs it and resumes its downward
    trajectory.

    These are baseline parameters. The next section tests how sensitive the outcome
    is to the values of the key unknowns.
    """)
    return


# ── Section 5: Interactive Scenario Exploration ────────────────────────


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Scenario Exploration

    The three parameters that matter most for the hypothesis:

    - **Learning exponent** — How steep is the cost curve? (0 = no learning, 0.32 = solar-like)
    - **Standardization threshold** — How much convergence is needed before learning kicks in?
    - **AI demand growth rate** — How fast is the demand engine spinning?

    The sliders below control these three parameters. Marimo reruns the simulation reactively on each change.
    """)
    return


@app.cell
def _(mo):
    learning_slider = mo.ui.slider(
        start=0.0, stop=0.35, step=0.01, value=0.18,
        label="Learning Exponent (b)",
        show_value=True,
    )
    threshold_slider = mo.ui.slider(
        start=0.1, stop=0.8, step=0.05, value=0.4,
        label="Standardization Threshold",
        show_value=True,
    )
    demand_slider = mo.ui.slider(
        start=0.0, stop=0.25, step=0.01, value=0.12,
        label="AI Demand Growth Rate",
        show_value=True,
    )
    regulatory_slider = mo.ui.slider(
        start=0.0, stop=0.5, step=0.05, value=0.25,
        label="Regulatory Step Size (2029)",
        show_value=True,
    )

    mo.hstack(
        [learning_slider, threshold_slider, demand_slider, regulatory_slider],
        justify="space-around",
    )
    return demand_slider, learning_slider, regulatory_slider, threshold_slider


@app.cell
def _(
    FONTS,
    baseline,
    demand_slider,
    learning_slider,
    legend_below,
    model_path,
    plt,
    pysd,
    regulatory_slider,
    threshold_slider,
):
    # Reload model fresh for each parameter set (PySD models are stateful)
    _model = pysd.read_vensim(str(model_path))
    scenario = _model.run(
        params={
            "learning exponent": learning_slider.value,
            "standardization threshold": threshold_slider.value,
            "AI demand growth rate": demand_slider.value,
            "regulatory step size": regulatory_slider.value,
        }
    )

    fig_scenario, axes_s = plt.subplots(1, 3, figsize=(14, 4))

    # Unit Cost comparison
    ax = axes_s[0]
    ax.plot(baseline.index, baseline["unit cost"], color="#aaaaaa", linestyle="--", label="Baseline")
    ax.plot(scenario.index, scenario["unit cost"], color="#d62728", label="Scenario")
    ax.set_ylabel("$/Unit (indexed)", fontsize=FONTS["axis_label"])
    legend_below(ax)

    # Cumulative Production
    ax = axes_s[1]
    ax.plot(
        baseline.index, baseline["Cumulative Production"],
        color="#aaaaaa", linestyle="--", label="Baseline",
    )
    ax.plot(
        scenario.index, scenario["Cumulative Production"],
        color="#2ca02c", label="Scenario",
    )
    ax.set_ylabel("Cumulative Production", fontsize=FONTS["axis_label"])
    legend_below(ax)

    # Standardization
    ax = axes_s[2]
    ax.plot(
        baseline.index, baseline["Standardization Fraction"],
        color="#aaaaaa", linestyle="--", label="Baseline",
    )
    ax.plot(
        scenario.index, scenario["Standardization Fraction"],
        color="#9467bd", label="Scenario",
    )
    ax.axhline(
        y=threshold_slider.value, color="#9467bd",
        linestyle=":", alpha=0.5, label="Threshold",
    )
    ax.set_ylabel("Standardization (0\u20131)", fontsize=FONTS["axis_label"])
    ax.set_ylim(0, 1)
    legend_below(ax)

    plt.tight_layout()
    fig_scenario
    return (scenario,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ### What the Scenarios Reveal

    Adjusting the sliders exposes four structural dynamics:

    **1. The standardization threshold is a tipping point.** Below it, unit cost
    barely moves regardless of volume. Above it, costs decline measurably. This
    formalizes Potter's insight: learning accrues from *repetition of identical
    units*, not from raw volume.

    **2. Demand growth rate matters more than learning exponent.** A moderate learning
    rate (b=0.12) with fast demand growth (15%+) produces steeper cost declines than
    a steep learning rate (b=0.25) with slow demand growth (5%). Volume is the input
    that feeds the curve.

    **3. The 2029 regulatory step is absorbable.** Even at the maximum step size, the
    cost bump is temporary. This is qualitatively different from the French nuclear
    pattern where each regulatory cycle compounded on the previous one (Grubler 2010).
    The DOE standard is a one-time level shift, not a recurring ratchet.

    **4. Capacity delay creates oscillation.** The backlog overshoots then undershoots
    as delayed capacity comes online in waves. This is the boom-bust archetype from
    Sterman (2000, Ch. 20) — the same structure that produces commodity cycles in
    mining and real estate.
    """)
    return


# ── Section 6: Sensitivity Analysis ───────────────────────────────────


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Sensitivity Analysis: Where Does the System Tip?

    Rather than single-scenario exploration, the heatmap below sweeps two
    parameters simultaneously, showing the **unit cost in 2035** across
    combinations of learning exponent and standardization threshold. The contour
    where cost drops below 90 (10% decline from baseline) marks the "learning
    curve zone."
    """)
    return


@app.cell
def _(FONTS, cfg, legend_below, model_path, np, plt, pysd, save_fig):
    learning_range = np.arange(0.0, 0.36, 0.03)
    threshold_range = np.arange(0.15, 0.85, 0.05)
    cost_grid = np.zeros((len(threshold_range), len(learning_range)))

    for i, thresh in enumerate(threshold_range):
        for j, learn in enumerate(learning_range):
            _m = pysd.read_vensim(str(model_path))
            _run = _m.run(
                params={
                    "learning exponent": learn,
                    "standardization threshold": thresh,
                },
                return_columns=["unit cost"],
            )
            # Get cost at 2035 (index 60 = year 15 at quarterly steps)
            idx_2035 = min(60, len(_run) - 1)
            cost_grid[i, j] = _run.iloc[idx_2035]["unit cost"]

    fig_heat, ax_heat = plt.subplots(figsize=(10, 6))
    im = ax_heat.contourf(
        learning_range, threshold_range, cost_grid,
        levels=20, cmap="RdYlGn_r",
    )
    ax_heat.contour(
        learning_range, threshold_range, cost_grid,
        levels=[90], colors=["black"], linewidths=[2], linestyles=["--"],
    )
    plt.colorbar(im, ax=ax_heat, label="Unit Cost at 2035 (indexed)")
    ax_heat.set_xlabel("Learning Exponent (b)", fontsize=FONTS["axis_label"])
    ax_heat.set_ylabel("Standardization Threshold", fontsize=FONTS["axis_label"])

    # Mark current best estimates
    ax_heat.plot(0.18, 0.4, "ko", markersize=10, label="DD-001 estimate (b\u22480.18)")
    legend_below(ax_heat)

    plt.tight_layout()
    save_fig(fig_heat, cfg.img_dir / "dd001_sensitivity_heatmap.png")
    return


# ── Section 7: Loop Dominance Analysis ─────────────────────────────────


@app.cell(hide_code=True)
def _(cfg, mo):
    _heatmap_img = mo.image(
        src=(cfg.img_dir / "dd001_sensitivity_heatmap.png").read_bytes(), width=800
    )
    mo.md(f"""
    ## Loop Dominance: Which Forces Win?

    # Unit Cost at 2035 by Learning Rate \u00d7 Standardization Threshold

    {_heatmap_img}

    The heatmap reveals the system's topology. The black dashed contour is the
    **learning curve threshold** — the boundary between "costs stagnate" (warm colors)
    and "costs decline" (cool colors).

    Three observations:

    **1. The Part 1 estimate sits near the boundary.** At b\u22480.18 and a threshold
    of 0.4, the system is in the learning zone — but not deep in it. Small changes
    in either parameter swing the outcome. This underscores why Bayesian estimation
    of these parameters (Part 3) matters — the uncertainty is decision-relevant.

    **2. Standardization matters more than raw learning rate.** The contour is
    nearly vertical on the left (below b\u22480.10, no amount of standardization helps)
    but horizontal on the right (above b\u22480.25, even moderate standardization
    produces cost declines). The leverage point is standardization, and that is
    precisely what the hyperscaler contracts (Compass/Siemens, Compass/Schneider)
    are providing.

    **3. The system is path-dependent.** If early demand drives standardization
    past the threshold, the reinforcing loops (R1, R2) take over and the outcome
    is self-sustaining. If demand falters before that point, the balancing loops
    (B1, B3) keep the system in the current scarcity equilibrium. This path
    dependence is what makes the Markov regime-switching framework (Part 4)
    a natural fit.
    """)
    return


# ── Section 8: Limitations and Next Steps ──────────────────────────────


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## What This Model Captures vs. What It Omits

    **Captures:**
    - Volume–learning feedback (Wright's Law conditional on standardization)
    - Supply constraint dynamics (backlog, lead times, capacity delay)
    - Commodity cost pass-through
    - Regulatory step-change (DOE 2029)
    - Standardization as an endogenous variable driven by hyperscaler demand
    - Labor market constraints on capacity scaling
    - Trade policy feedback on material costs

    **Omits (for now):**
    - **Solid-state transformer substitution** (B5) — relevant at longer time
      horizons (2030+). Adding this requires a competing technology stock with
      its own learning curve (SiC/GaN semiconductors).
    - **Cost socialization dynamics** — the FERC/ratepayer feedback loop. Research
      found $4.3B/year in socialized grid costs, with FERC reforming cost allocation
      in 2025-2026. This affects *who benefits*, not whether learning occurs.
    - **Calibration to real data** — all parameters are estimates. Part 3 (Bayesian
      estimation) will replace these with data-driven posteriors.

    ## What Comes Next

    This analysis identifies the feedback architecture and the parameters that
    determine which regime the system enters. The next steps are:

    - **Data validation** — Several claims rest on industry reports rather than
      primary data. The learning exponent, standardization fraction, and labor
      intensity assumptions need grounding in public datasets (BLS, Census Bureau
      of Manufacturing, NEMA shipment data).
    - **Reference review** — The sources listed below need to be read and evaluated
      firsthand, not cited secondhand from summary coverage.
    - **Publication** — Tightening this analysis into a self-contained piece that
      answers: "Are AI data centers accidentally industrializing transformer
      manufacturing?"
    """)
    return


# ── Section 9: Sources ─────────────────────────────────────────────────


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ---

    ### Sources and Further Reading

    **Systems Dynamics:**
    - **Sterman, J. (2000):** *Business Dynamics: Systems Thinking and Modeling for
      a Complex World.* McGraw-Hill. The canonical SD textbook.
    - **Meadows, D. (2008):** *Thinking in Systems.* Chelsea Green. Conceptual primer.
    - **PySD Documentation:** [pysd.readthedocs.io](https://pysd.readthedocs.io/)

    **Transformer Market Data:**
    - **Wood Mackenzie (2025):** 30% power transformer supply deficit, 128-144 week
      lead times.
    - **NREL (2024-2025):** Distribution transformer demand segmentation, 160-260%
      capacity growth by 2050.
    - **DOE (2024):** Final efficiency standards — 75% GOES, 25% amorphous, 5-year
      compliance (April 2029).

    **Industry Developments:**
    - **Compass/Siemens (2025):** 1,500 identical modular MV skid units, 5-year
      contract.
    - **Compass/Schneider ($3B, 2023-2028):** 240-400+ power centers/year, West
      Chester OH.
    - **Cleveland-Cliffs ($150M, 2024):** Vertically integrated GOES-to-transformer
      plant, Weirton WV. Three-phase distribution transformers. On track H1 2026.

    **Learning Curves and Skepticism:**
    - **Brian Potter:** *Construction Physics* — conditions for learning curves.
    - **Grubler (2010):** French nuclear negative learning (counterexample).
    - **BCG (1968):** Original experience curve observations, 10-25% across industries.

    **Cost Socialization:**
    - **Union of Concerned Scientists (2025):** $4.3B in PJM data center grid costs
      socialized to ratepayers.
    - **FERC (December 2025):** Ordered PJM to allocate 100% of co-location upgrade
      costs to large load customers.

    ---

    *Part 2 of 4*
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
