import marimo

__generated_with = "0.19.11"
app = marimo.App()


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # AI Capital and Grid Modernization
    ## Part 3 — Feedback Architecture

    *Thandolwethu Zwelakhe Dlamini*

    ---

    Part 1 showed that new generation capacity is predominantly clean — solar
    and battery storage dominate additions since 2020. Part 2 showed that the
    interconnection queue is the binding constraint, and that $4.36 billion in
    grid upgrade costs were approved for socialization to ratepayers in 2024
    alone.

    This part formalizes the feedback loops that determine whether AI capital
    catalyzes grid modernization for everyone or builds private infrastructure
    for a few. The central question: **does the system tip toward shared grid
    investment (spillover) or behind-the-meter bypass (capture)?**
    """)
    return


@app.cell
def _():
    import sys

    import marimo as mo
    import matplotlib.patches as mpatches
    import matplotlib.pyplot as plt

    sys.path.insert(0, str(mo.notebook_dir().parent.parent))

    import numpy as np
    import pysd

    from src.notebook import save_fig, setup
    from src.plotting import CATEGORICAL, COLORS, FONTS, legend_below, multi_panel

    cfg = setup()
    return (
        CATEGORICAL,
        COLORS,
        FONTS,
        cfg,
        legend_below,
        mo,
        mpatches,
        multi_panel,
        np,
        plt,
        pysd,
        save_fig,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Five Feedback Loops

    The grid modernization system contains two reinforcing loops (which
    amplify change) and three balancing loops (which resist it). Which set
    dominates determines whether AI capital drives broad grid modernization
    or private infrastructure buildout.

    | | Loop | Mechanism | Favors |
    | :--- | :--- | :--- | :--- |
    | **R1** | Grid Investment Cycle | Grid investment → lower costs → more connection | Grid modernization |
    | **R2** | Renewable Learning | More renewables → cheaper renewables → more renewables | Everyone (structural) |
    | **B1** | Regulatory Uncertainty | Policy ambiguity → investment pause → longer queues | Stagnation |
    | **B2** | BTM Bypass | Long queues → bypass grid → no spillover → backlash | Private infrastructure |
    | **B3** | Stranded Asset Risk | Carbon uncertainty → hesitation on all investments | Paralysis |

    ### Reinforcing Loops (Amplify)

    **R1: Grid Investment Virtuous Cycle**
    AI demand → grid investment → modernized infrastructure → lower grid
    costs → grid connection more attractive → more AI demand connects to
    grid → more grid investment.

    This is the "everyone benefits" loop. When AI capital flows through
    the grid, the infrastructure improvements serve all users. The key
    enabler is a regulatory environment that makes grid connection faster
    and cheaper than going behind-the-meter.

    **R2: Renewable Learning Curve**
    AI demand → renewable PPAs → increased renewable production → learning
    curve cost reductions → cheaper renewables → more PPAs.

    This loop fires regardless of whether AI demand connects to the grid
    or goes behind-the-meter. Every GW of solar or wind built drives
    down costs for the next GW. The learning curve is the one unambiguous
    positive — it proceeds in all scenarios.

    ### Balancing Loops (Resist)

    **B1: Regulatory Uncertainty**
    Policy ambiguity → investment pause → delayed grid modernization →
    longer queue times → more behind-the-meter bypass.

    The current regulatory environment (February 2026) creates a holding
    pattern. Companies will not publicly champion renewables against the
    current administration, but will not commit to fossil infrastructure
    because of stranded asset risk. The result is strategic ambiguity
    that slows grid investment.

    **B2: Behind-the-Meter Bypass**
    Long queue times → behind-the-meter attractive → no grid investment
    → no spillover benefit → ratepayer burden increases → political
    backlash → hostile regulatory environment → longer queue times.

    This is the "capture" loop. When companies bypass the grid, the grid
    gets nothing. Worse, existing ratepayers absorb a larger share of
    fixed costs, raising bills and generating political opposition to
    data center expansion.

    **B3: Stranded Asset Risk**
    Carbon regulation uncertainty → fossil investment hesitation → but
    also renewable hesitation (uncertainty about IRA credit durability)
    → overall investment slowdown.

    This loop creates paralysis. Neither fossil nor clean investments
    proceed at the pace needed because both face policy risk. The
    constraint is not economics — it is regulatory uncertainty.
    """)
    return


@app.cell
def _(FONTS, cfg, legend_below, mpatches, np, plt, save_fig):
    # Draw the Causal Loop Diagram
    fig_cld, ax = plt.subplots(figsize=(18, 14))
    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-1.3, 1.3)
    ax.set_aspect("equal")
    ax.axis("off")

    # Node positions (circular layout with adjustments)
    _nodes = {
        "AI\nDemand": (0, 1.0),
        "Grid\nInvestment": (-0.7, 0.5),
        "Grid\nCapacity": (-1.0, -0.1),
        "Energy\nCosts": (-0.7, -0.6),
        "Renewable\nPPAs": (0.7, 0.5),
        "Renewable\nCost": (1.0, -0.1),
        "BTM\nCapacity": (0.35, -0.3),
        "Queue\nBacklog": (-0.2, 0.2),
        "Regulatory\nEnvironment": (0, -0.85),
        "Ratepayer\nBurden": (-0.5, -1.1),
        "Political\nSupport": (0.5, -1.1),
    }

    # Draw nodes — larger radius and font for readability
    for label, (x, y) in _nodes.items():
        ax.add_patch(plt.Circle((x, y), 0.16, color="white", ec="black", lw=2, zorder=3))
        ax.text(x, y, label, ha="center", va="center", fontsize=FONTS["annotation"], fontweight="bold", zorder=4)

    # Edge drawing helper
    def _draw_edge(start, end, color, polarity, offset=0.15, curve=0.0, lw=1.8):
        x1, y1 = _nodes[start]
        x2, y2 = _nodes[end]
        dx, dy = x2 - x1, y2 - y1
        dist = np.sqrt(dx**2 + dy**2)
        x1 += offset * dx / dist
        y1 += offset * dy / dist
        x2 -= offset * dx / dist
        y2 -= offset * dy / dist

        ax.annotate(
            "",
            xy=(x2, y2),
            xytext=(x1, y1),
            arrowprops=dict(
                arrowstyle="-|>",
                color=color,
                lw=lw,
                connectionstyle=f"arc3,rad={curve}",
                mutation_scale=15,
            ),
            zorder=2,
        )
        mx = (x1 + x2) / 2 + curve * 0.3
        my = (y1 + y2) / 2 + curve * 0.3
        ax.text(mx, my, polarity, fontsize=FONTS["annotation"], color=color, fontweight="bold",
                ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec=color, alpha=0.9))

    # R1: Grid Investment Virtuous Cycle (blue) — thicker for reinforcing
    _r1 = CATEGORICAL[0]
    _draw_edge("AI\nDemand", "Grid\nInvestment", _r1, "+", curve=0.15, lw=2.5)
    _draw_edge("Grid\nInvestment", "Grid\nCapacity", _r1, "+", curve=0.1, lw=2.5)
    _draw_edge("Grid\nCapacity", "Energy\nCosts", _r1, "-", curve=0.1, lw=2.5)
    _draw_edge("Energy\nCosts", "AI\nDemand", _r1, "-", curve=-0.3, lw=2.5)

    # R2: Renewable Learning (green) — thicker for reinforcing
    _r2 = COLORS["positive"]
    _draw_edge("AI\nDemand", "Renewable\nPPAs", _r2, "+", curve=-0.15, lw=2.5)
    _draw_edge("Renewable\nPPAs", "Renewable\nCost", _r2, "-", curve=0.1, lw=2.5)
    _draw_edge("Renewable\nCost", "Renewable\nPPAs", _r2, "-", curve=0.3, lw=2.5)

    # B1: Regulatory Uncertainty (orange)
    _b1 = CATEGORICAL[7]
    _draw_edge("Regulatory\nEnvironment", "Grid\nInvestment", _b1, "+", curve=-0.2)
    _draw_edge("Regulatory\nEnvironment", "BTM\nCapacity", _b1, "-", curve=0.2)

    # B2: BTM Bypass (red)
    _b2 = COLORS["negative"]
    _draw_edge("Queue\nBacklog", "BTM\nCapacity", _b2, "+", curve=0.15)
    _draw_edge("BTM\nCapacity", "Ratepayer\nBurden", _b2, "+", curve=0.2)
    _draw_edge("Ratepayer\nBurden", "Political\nSupport", _b2, "-", curve=0.1)
    _draw_edge("Political\nSupport", "Regulatory\nEnvironment", _b2, "+", curve=0.2)

    # B3: Stranded Asset Risk (purple)
    _b3 = CATEGORICAL[5]
    _draw_edge("Regulatory\nEnvironment", "Queue\nBacklog", _b3, "-", curve=-0.15)

    # Loop labels placed near center of each loop's path
    ax.text(-0.45, 0.2, "R1", fontsize=FONTS["annotation"], fontweight="bold", color=_r1,
            ha="center", va="center", alpha=0.7,
            bbox=dict(boxstyle="circle,pad=0.3", fc="white", ec=_r1, alpha=0.7))
    ax.text(0.9, 0.25, "R2", fontsize=FONTS["annotation"], fontweight="bold", color=_r2,
            ha="center", va="center", alpha=0.7,
            bbox=dict(boxstyle="circle,pad=0.3", fc="white", ec=_r2, alpha=0.7))
    ax.text(-0.35, -0.4, "B1", fontsize=FONTS["annotation"], fontweight="bold", color=_b1,
            ha="center", va="center", alpha=0.7,
            bbox=dict(boxstyle="circle,pad=0.3", fc="white", ec=_b1, alpha=0.7))
    ax.text(0.15, -0.65, "B2", fontsize=FONTS["annotation"], fontweight="bold", color=_b2,
            ha="center", va="center", alpha=0.7,
            bbox=dict(boxstyle="circle,pad=0.3", fc="white", ec=_b2, alpha=0.7))
    ax.text(-0.15, -0.3, "B3", fontsize=FONTS["annotation"], fontweight="bold", color=_b3,
            ha="center", va="center", alpha=0.7,
            bbox=dict(boxstyle="circle,pad=0.3", fc="white", ec=_b3, alpha=0.7))

    # Legend
    _legend_items = [
        mpatches.Patch(color=_r1, label="R1: Grid Investment Virtuous Cycle"),
        mpatches.Patch(color=_r2, label="R2: Renewable Learning Curve"),
        mpatches.Patch(color=_b1, label="B1: Regulatory Uncertainty"),
        mpatches.Patch(color=_b2, label="B2: Behind-the-Meter Bypass"),
        mpatches.Patch(color=_b3, label="B3: Stranded Asset / Queue Dynamics"),
    ]
    legend_below(ax, handles=_legend_items, ncol=3)
    save_fig(fig_cld, cfg.img_dir / "dd002_cld.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo):
    _cld = mo.image(
        src=(cfg.img_dir / "dd002_cld.png").read_bytes(), width=850
    )
    mo.md(
        f"""
    # Five feedback loops determine whether AI capital modernizes the grid or bypasses it

    {_cld}

    The CLD captures the central tension. The reinforcing loops (R1 and R2)
    drive grid modernization and renewable cost reduction. The balancing loops
    (B1, B2, B3) resist it through regulatory uncertainty, behind-the-meter
    bypass, and political backlash from cost shifting.

    The critical variable is **Regulatory Environment**. It influences both
    the attractiveness of grid connection (R1) and the attractiveness of
    bypass (B2). A favorable regulatory environment — fast permitting,
    fair cost allocation, queue reform — strengthens R1 and weakens B2.
    A hostile environment does the opposite.
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## From Loops to Stocks and Flows

    The CLD shows the structure. To test which loops dominate, we need a
    simulation model. The stock-and-flow model has five stocks:

    | Stock | Units | Initial Value | What It Represents |
    | :--- | :--- | :--- | :--- |
    | Grid Capacity | GW | 50 | Grid-connected generation serving data center corridors |
    | Behind-the-Meter Capacity | GW | 5 | On-site generation bypassing the grid |
    | Queue Backlog | GW | 200 | Projects waiting for interconnection |
    | Renewable Cost Index | $/MWh | 40 | LCOE of utility-scale solar + storage |
    | Regulatory Favorability | 0-1 | 0.6 | Index of regulatory support for grid connection |

    The key output metric is the **grid spillover index**: the fraction of
    total capacity that is grid-connected. Higher means more spillover benefit
    to non-data-center users. Lower means more private infrastructure.
    """)
    return


@app.cell
def _(cfg, pysd):
    # Load the Vensim model
    model_path = cfg.models_dir / "grid_modernization.mdl"
    model = pysd.read_vensim(str(model_path))

    # Run baseline
    baseline = model.run()
    return baseline, model


@app.cell
def _(FONTS, baseline, cfg, multi_panel, save_fig):
    _panels = [
        {
            "columns": {
                "Grid Capacity": {"color": CATEGORICAL[0], "linewidth": 2, "label": "Grid Capacity"},
                "Behind the Meter Capacity": {"color": COLORS["negative"], "linewidth": 2, "linestyle": "--", "label": "Behind-the-Meter"},
            },
            "title": "Capacity Growth (GW)",
            "ylabel": "GW",
            "ylim": (0, None),
        },
        {
            "columns": {
                "Queue Backlog": {"color": CATEGORICAL[7], "linewidth": 2, "label": "Queue Backlog"},
            },
            "title": "Interconnection Queue (GW)",
            "ylabel": "GW",
        },
        {
            "columns": {
                "Renewable Cost Index": {"color": COLORS["positive"], "linewidth": 2, "label": "Solar+Storage LCOE"},
            },
            "title": "Renewable Cost ($/MWh)",
            "ylabel": "$/MWh",
        },
        {
            "columns": {
                "grid spillover index": {"color": CATEGORICAL[5], "linewidth": 2, "label": "Spillover Index"},
            },
            "title": "Grid Spillover Index",
            "ylabel": "Fraction (0-1)",
            "ylim": (0, 1),
        },
    ]

    fig_baseline = multi_panel(baseline, _panels, "Baseline: Grid vs. Behind-the-Meter Dynamics", ncols=2)

    # Annotate start/end values on each panel for self-sufficiency
    _axes = fig_baseline.get_axes()
    _t0, _tf = baseline.index[0], baseline.index[-1]

    # Panel 0: Capacity — annotate Grid and BTM end values
    _grid_end = baseline["Grid Capacity"].iloc[-1]
    _btm_end = baseline["Behind the Meter Capacity"].iloc[-1]
    _axes[0].annotate(f"{_grid_end:.0f}", xy=(_tf, _grid_end), fontsize=FONTS["value_label"], color=CATEGORICAL[0],
                      fontweight="bold", va="bottom", ha="right")
    _axes[0].annotate(f"{_btm_end:.0f}", xy=(_tf, _btm_end), fontsize=FONTS["value_label"], color=COLORS["negative"],
                      fontweight="bold", va="bottom", ha="right")

    # Panel 3: Spillover — annotate start and end
    _spill_start = baseline["grid spillover index"].iloc[0]
    _spill_end = baseline["grid spillover index"].iloc[-1]
    _axes[3].annotate(f"{_spill_start:.2f}", xy=(_t0, _spill_start), fontsize=FONTS["value_label"], color=CATEGORICAL[5],
                      fontweight="bold", va="bottom", ha="left")
    _axes[3].annotate(f"{_spill_end:.2f}", xy=(_tf, _spill_end), fontsize=FONTS["value_label"], color=CATEGORICAL[5],
                      fontweight="bold", va="top", ha="right")

    # Panel 2: Renewable cost — annotate start and end (well clear of line)
    _cost_start = baseline["Renewable Cost Index"].iloc[0]
    _cost_end = baseline["Renewable Cost Index"].iloc[-1]
    _axes[2].annotate(f"${_cost_start:.0f}", xy=(_t0, _cost_start),
                      xytext=(8, 18), textcoords="offset points",
                      fontsize=FONTS["value_label"], color=COLORS["positive"],
                      fontweight="bold", ha="left",
                      arrowprops=dict(arrowstyle="->", color=COLORS["positive"], lw=0.8))
    _axes[2].annotate(f"${_cost_end:.0f}", xy=(_tf, _cost_end),
                      xytext=(-8, -20), textcoords="offset points",
                      fontsize=FONTS["value_label"], color=COLORS["positive"],
                      fontweight="bold", ha="right",
                      arrowprops=dict(arrowstyle="->", color=COLORS["positive"], lw=0.8))

    save_fig(fig_baseline, cfg.img_dir / "dd002_baseline_simulation.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo):
    _baseline_chart = mo.image(
        src=(cfg.img_dir / "dd002_baseline_simulation.png").read_bytes(), width=850
    )
    mo.md(
        f"""
    # Baseline: Grid vs. Behind-the-Meter Dynamics

    {_baseline_chart}

    Under baseline parameters, three dynamics emerge:

    1. **Grid capacity grows, but behind-the-meter grows faster.** Both
       increase substantially, but BTM capacity gains share over time.
       The grid spillover index declines from 0.91 to 0.69 — meaning
       the share of AI-driven infrastructure that benefits the broader
       grid shrinks from 91% to 69%.

    2. **The queue clears.** The initial backlog of 200 GW processes
       through over the simulation period. This is optimistic — it
       assumes current queue processing rates hold as demand grows.

    3. **Renewable costs keep falling.** The learning curve drives
       solar+storage LCOE from $40/MWh to ~$31/MWh by 2040. This
       proceeds regardless of regulatory choices.

    The baseline tells a cautious story: the grid modernizes, but
    behind-the-meter capacity captures an increasing share of AI
    infrastructure investment. The regulatory environment is the
    swing variable.
    """
    )
    return


@app.cell
def _(mo):
    # Interactive scenario sliders
    grid_inv_slider = mo.ui.slider(
        start=0.1, stop=0.6, step=0.05, value=0.3,
        label="Expansion Aggressiveness",
        show_value=True,
    )
    btm_cost_slider = mo.ui.slider(
        start=0.5, stop=2.0, step=0.1, value=1.2,
        label="BTM Cost Advantage",
        show_value=True,
    )
    reg_slider = mo.ui.slider(
        start=0.1, stop=0.9, step=0.05, value=0.5,
        label="Target Regulatory Favorability",
        show_value=True,
    )

    mo.md("### Scenario Parameters")
    mo.hstack([grid_inv_slider, btm_cost_slider, reg_slider], justify="space-around")
    return btm_cost_slider, grid_inv_slider, reg_slider


@app.cell
def _(FONTS, baseline, btm_cost_slider, grid_inv_slider, legend_below, mo, model, plt, reg_slider):
    # Run scenario with slider values
    _scenario = model.run(params={
        "expansion aggressiveness": grid_inv_slider.value,
        "btm cost advantage": btm_cost_slider.value,
        "target regulatory favorability": reg_slider.value,
    })

    # Compare baseline vs scenario
    _fig, _axes = plt.subplots(1, 3, figsize=(15, 4.5))

    # Panel 1: Grid vs BTM capacity
    _axes[0].plot(baseline.index, baseline["Grid Capacity"], CATEGORICAL[0], alpha=0.4, label="Grid (baseline)")
    _axes[0].plot(baseline.index, baseline["Behind the Meter Capacity"], COLORS["negative"], linestyle="--", alpha=0.4, label="BTM (baseline)")
    _axes[0].plot(_scenario.index, _scenario["Grid Capacity"], CATEGORICAL[0], linewidth=2.5, label="Grid (scenario)")
    _axes[0].plot(_scenario.index, _scenario["Behind the Meter Capacity"], COLORS["negative"], linestyle="--", linewidth=2.5, label="BTM (scenario)")
    _axes[0].set_title("Capacity (GW)", fontsize=FONTS["panel_title"], fontweight="bold")
    _axes[0].set_ylabel("GW", fontsize=FONTS["axis_label"])
    legend_below(_axes[0], ncol=2)
    _axes[0].grid(True, linestyle=":", alpha=0.4)

    # Panel 2: Spillover index
    _axes[1].plot(baseline.index, baseline["grid spillover index"], "k--", label="Baseline", alpha=0.4)
    _axes[1].plot(_scenario.index, _scenario["grid spillover index"], CATEGORICAL[5], linewidth=2.5, label="Scenario")
    _axes[1].set_title("Grid Spillover Index", fontsize=FONTS["panel_title"], fontweight="bold")
    _axes[1].set_ylabel("Fraction (0-1)", fontsize=FONTS["axis_label"])
    _axes[1].set_ylim(0, 1)
    _axes[1].axhline(0.5, color=COLORS["accent"], linestyle="--", linewidth=1.2, alpha=0.6, label="50% threshold")
    legend_below(_axes[1])
    _axes[1].grid(True, linestyle=":", alpha=0.4)

    # Panel 3: Socialized cost
    _axes[2].plot(baseline.index, baseline["cost allocation to ratepayers"], "k--", label="Baseline", alpha=0.4)
    _axes[2].plot(_scenario.index, _scenario["cost allocation to ratepayers"], COLORS["accent"], linewidth=2.5, label="Scenario")
    _axes[2].set_title("Socialized Cost ($B/year)", fontsize=FONTS["panel_title"], fontweight="bold")
    _axes[2].set_ylabel("$B/year", fontsize=FONTS["axis_label"])
    legend_below(_axes[2])
    _axes[2].grid(True, linestyle=":", alpha=0.4)

    # Extract scenario 2035 spillover for reactive interpretation
    _idx_2035 = _scenario.index.get_indexer([2035], method="nearest")[0]
    scenario_spillover_2035 = float(_scenario["grid spillover index"].iloc[_idx_2035])
    _b_idx_2035 = baseline.index.get_indexer([2035], method="nearest")[0]
    baseline_spillover_2035 = float(baseline["grid spillover index"].iloc[_b_idx_2035])

    plt.tight_layout()

    mo.vstack([
        mo.as_html(_fig),
        mo.md(
            f"**2035 spillover index: {scenario_spillover_2035:.2f}** "
            f"(baseline: {baseline_spillover_2035:.2f}). "
            f"{'The grid captures more investment than baseline.' if scenario_spillover_2035 > baseline_spillover_2035 else 'Behind-the-meter captures more investment than baseline.' if scenario_spillover_2035 < baseline_spillover_2035 else 'No change from baseline.'}"
        ),
    ])
    plt.close(_fig)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    The sliders above control three parameters that together determine
    whether AI capital drives shared grid modernization or private
    infrastructure. Adjusting them exposes three structural insights:

    1. **The BTM tipping point.** When the BTM cost advantage exceeds
       ~1.5, behind-the-meter capacity grows explosively and the grid
       spillover index collapses. This is the "capture" regime where
       hyperscalers build private infrastructure and the grid gets nothing.

    2. **Regulatory favorability is the swing variable.** Moving target
       regulatory favorability from 0.3 (hostile) to 0.7 (favorable)
       shifts the spillover index by 15-20 percentage points. No other
       single parameter has as large an effect.

    3. **Expansion aggressiveness matters less than you think.** Even
       aggressive grid investment cannot overcome a hostile regulatory
       environment. The constraint is not willingness to invest — it is
       the structural incentive to bypass the grid when queue times are
       long and cost allocation is unfavorable.
    """)
    return


@app.cell
def _(FONTS, cfg, model, np, plt, save_fig):
    # Sensitivity analysis: BTM cost advantage × Regulatory favorability → spillover index
    _btm_range = np.arange(0.5, 2.1, 0.1)
    _reg_range = np.arange(0.1, 1.0, 0.05)
    _spillover = np.zeros((len(_reg_range), len(_btm_range)))

    for i, reg in enumerate(_reg_range):
        for j, btm in enumerate(_btm_range):
            _result = model.run(params={
                "btm cost advantage": btm,
                "target regulatory favorability": reg,
            })
            # Get spillover index at 2035
            _idx_2035 = _result.index.get_indexer([2035], method="nearest")[0]
            _spillover[i, j] = _result["grid spillover index"].iloc[_idx_2035]

    fig_sensitivity, _ax = plt.subplots(figsize=(10, 7))
    _contour = _ax.contourf(
        _btm_range, _reg_range, _spillover,
        levels=np.arange(0.3, 1.01, 0.05),
        cmap="RdYlGn",
    )
    _cbar = plt.colorbar(_contour, ax=_ax, label="Grid Spillover Index (2035)")

    # Mark the 0.5 threshold
    _ax.contour(
        _btm_range, _reg_range, _spillover,
        levels=[0.5],
        colors=["black"],
        linewidths=[2],
        linestyles=["--"],
    )

    # Mark current best estimate
    _ax.plot(1.2, 0.5, "k*", markersize=15, zorder=5)
    _ax.annotate(
        "Current\nestimate",
        xy=(1.2, 0.5),
        xytext=(1.5, 0.35),
        fontsize=FONTS["annotation"],
        arrowprops=dict(arrowstyle="->", color="black"),
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="black"),
    )

    # Regime labels
    _ax.text(0.7, 0.85, "GRID\nMODERNIZATION", fontsize=FONTS["annotation"], fontweight="bold",
             color="white", ha="center", va="center", alpha=0.8)
    _ax.text(1.7, 0.2, "PRIVATE\nINFRASTRUCTURE", fontsize=FONTS["annotation"], fontweight="bold",
             color="white", ha="center", va="center", alpha=0.8)

    _ax.set_xlabel("BTM Cost Advantage", fontsize=FONTS["axis_label"])
    _ax.set_ylabel("Regulatory Favorability", fontsize=FONTS["axis_label"])
    save_fig(fig_sensitivity, cfg.img_dir / "dd002_sensitivity.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo):
    _heatmap = mo.image(
        src=(cfg.img_dir / "dd002_sensitivity.png").read_bytes(), width=800
    )
    mo.md(
        f"""
    # Regulatory environment determines whether AI capital modernizes the grid or bypasses it

    {_heatmap}

    The heatmap sweeps two parameters — BTM cost advantage (how much
    cheaper it is to bypass the grid) and regulatory favorability (how
    supportive the policy environment is for grid connection). Green
    regions indicate high grid spillover (everyone benefits). Red regions
    indicate low spillover (private infrastructure dominates).

    The black dashed line marks the 50% spillover boundary. Below it,
    more than half of AI infrastructure investment bypasses the grid.

    The current best estimate (starred) sits near the boundary. This
    means the system is in a regime where small regulatory changes —
    FERC cost allocation reform, state permitting acceleration, queue
    processing improvements — can shift the outcome significantly.

    **The policy implication is clear:** the marginal dollar of regulatory
    effort toward grid connection has high leverage right now. Once the
    system tips into the "capture" regime (bottom-right), it is much
    harder to reverse — behind-the-meter infrastructure is built and
    sunk, and the political constituency for grid investment shrinks.
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Limitations

    This model captures structural dynamics, not numerical prediction.
    Several important features are omitted:

    - **Geographic resolution.** The model is national-level. In reality,
      grid dynamics vary enormously by ISO/RTO — PJM, ERCOT, and CAISO
      have different queue processes, cost allocation rules, and generation
      mixes.
    - **Temporal dynamics of FERC rulemaking.** Regulatory change is modeled
      as a smooth convergence toward a target. In practice, it happens through
      discrete orders, court challenges, and compliance timelines.
    - **Technology disruption.** SMRs, enhanced geothermal, and long-duration
      storage could change the cost structure fundamentally. These are not
      modeled.
    - **Financing constraints.** Access to capital, interest rates, and tax
      equity markets affect investment pace but are not captured.
    - **Political economy feedback.** The model does not fully capture how
      job losses in one sector (tech layoffs) interact with job creation
      in another (infrastructure construction) to shape political support
      for AI-favorable policy.

    These omissions define the boundary of what the model can and cannot
    say. It can identify which feedback loops dominate under different
    parameter regimes. It cannot predict the 2035 grid spillover index
    to two decimal places.

    ---

    ## Connection to CS-1

    The transformer case study (CS-1) asked whether AI demand could unlock
    learning curves in grid hardware manufacturing. This case study asks
    whether the infrastructure that hardware goes into benefits everyone
    or just the companies paying for it.

    The answer depends on the same regulatory variables: trade policy
    shapes transformer supply (CS-1), while energy and utility policy
    shape grid infrastructure (CS-2/3). Both are being decided now, and
    both create 30-50 year infrastructure consequences from near-term
    political choices.

    The grid spillover question is the infrastructure analogue of the
    learning curve question. In both cases, the system sits near a
    tipping point where small changes in policy create large changes
    in long-term outcome. The infrastructure will outlast the regulatory
    moment that shapes it.

    ---

    ### Sources

    - Sterman, J. (2000). *Business Dynamics.* McGraw-Hill.
    - Meadows, D. (2008). *Thinking in Systems.* Chelsea Green.
    - LBNL Queued Up (2025 Edition) — interconnection queue data
    - FERC Docket EL25-49-000 — co-location cost allocation order
    - UCS (September 2025) — PJM data center cost socialization ($4.36B approved in 2024)
    - JLARC / E3 (December 2024) — Virginia data center grid impact
    - Grid Strategies (2023) — *The Era of Flat Power Demand is Over*
    - IRENA (2024) — renewable energy cost trends and learning rates
    - Wright, T.P. (1936). Factors Affecting the Cost of Airplanes.
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
