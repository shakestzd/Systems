import marimo

__generated_with = "0.19.11"
app = marimo.App()


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #The Learning Curve of Power Infrastructure
    ## Part 1 — The Investigation
    *Thandolwethu Zwelakhe Dlamini*
    """)
    return


@app.cell
def _():
    import sys
    import marimo as mo

    # Ensure project root is first in sys.path so src is importable
    sys.path.insert(0, str(mo.notebook_dir().parent.parent))

    import pandas as pd
    import numpy as np

    from src.notebook import setup, save_fig
    from src.data.fred import fetch_csv
    from src.plotting import FONTS, annotated_series, legend_below

    cfg = setup()
    return FONTS, annotated_series, cfg, fetch_csv, legend_below, mo, np, pd, save_fig


@app.cell
def _(cfg, mo):
    grid_hierarchy = mo.image(
        src=(cfg.img_dir / "grid_hierarchy.png").read_bytes(), width=800
    )
    return (grid_hierarchy,)


@app.cell
def _(cfg, mo):
    bespoke_vs_modular = mo.image(
        src=(cfg.img_dir / "bespoke_vs_modular.png").read_bytes(), width=800
    )
    return (bespoke_vs_modular,)


@app.cell
def _(cfg, mo):
    bespoke_vs_commodity = mo.image(
        src=(cfg.img_dir / "bespoke_vs_commodity.png").read_bytes(), width=800
    )
    return (bespoke_vs_commodity,)


@app.cell
def _(cfg, mo):
    transmission_titan = mo.image(
        src=(cfg.img_dir / "transmission_titan.png").read_bytes(), width=400
    )
    distribution_hub = mo.image(
        src=(cfg.img_dir / "distribution_hub.png").read_bytes(), width=400
    )
    return distribution_hub, transmission_titan


@app.cell(hide_code=True)
def _(mo):
    mo.md(f"""
    ## Where This Started

    Three numbers frame the problem. Bloomberg NEF projects U.S. data center power
    demand reaching 106 GW by 2035. Wood Mackenzie forecasts a 30% supply deficit for
    power transformers through 2025. And lead times for Large Power Transformers have
    stretched to **38 months** (Wood Mackenzie, 2025).

    The framing in most coverage — Canary Media, Volts, utility filings to FERC — is
    **scarcity**: AI is consuming the grid faster than it can be built. That framing
    treats the grid as a fixed resource being depleted. But a demand shock of this
    magnitude also reshapes the industrial economics of the supply chain itself. The
    question I wanted to investigate: is AI demand changing *how* grid hardware gets
    manufactured, not just how much of it gets consumed?
    """)
    return


@app.cell(hide_code=True)
def _(grid_hierarchy, mo):
    mo.md(f"""
    ## Why Transformers

    Why focus on transformers? Because they are the only technology class that appears
    at every layer of the grid — generation, transmission, distribution. Every megawatt
    of new capacity requires them at every stage. If AI demand is reshaping grid
    economics, transformer markets are where the pressure shows up first.
    {grid_hierarchy}

    - **Generation:** Step-up transformers raise voltage from generators to transmission levels
    - **Transmission:** Large Power Transformers move electricity across the high-voltage backbone
    - **Distribution:** Step-down transformers deliver power to homes, businesses, and data centers

    ### Two Commodities, One Bottleneck

    Transformers also sit at the intersection of two critical commodity markets:

    - **Copper** — for the windings that carry current
    - **Grain-Oriented Electrical Steel (GOES)** — for the magnetic cores that transfer energy between windings

    This means transformer costs are a *composite signal*: part manufacturing efficiency,
    part commodity market, part supply chain structure. Disentangling these is the
    analytical challenge at the heart of this notebook.

    There's a related technology I want to flag for future investigation: **switchgear**.
    Like transformers, switchgear is required at every level of the grid (generation,
    transmission, distribution). Like transformers, it depends on copper and specialized
    steel. And like transformers, it's been historically bespoke. If AI demand is
    industrializing transformer manufacturing, the same forces likely apply to switchgear —
    but that's a separate analysis.
    """)
    return


@app.cell
def _(fetch_csv, mo):
    transformer_ppi = fetch_csv("PCU335311335311")
    copper_ppi = fetch_csv("WPU102501")
    steel_ppi = fetch_csv("WPU1017")

    mo.md(
        """
    ## The Data: Starting Simple

    I started with the simplest thing I could measure: **prices over time.** The St. Louis
    Fed (FRED) publishes Producer Price Indices for transformers and their key input
    materials. Three series — one for the finished product, two for the raw materials that
    dominate its cost structure:

    - **Transformer PPI** (`PCU335311335311`) — average selling price for power transformers
    - **Copper PPI** (`WPU102501`) — primary winding material
    - **Steel PPI** (`WPU1017`) — proxy for Grain-Oriented Electrical Steel (GOES), the core
    """
    )
    return copper_ppi, steel_ppi, transformer_ppi


@app.cell
def _(copper_ppi, pd, steel_ppi, transformer_ppi):
    df = transformer_ppi.rename(columns={"PCU335311335311": "Transformer_PPI"})
    df = df.join(
        copper_ppi.rename(columns={"WPU102501": "Copper_PPI"}), how="inner"
    )
    df = df.join(steel_ppi.rename(columns={"WPU1017": "Steel_PPI"}), how="inner")
    df = df.dropna()

    base_date = "2015-01-01"
    if pd.Timestamp(base_date) not in df.index:
        base_date = df.index[0]

    df_norm = df / df.loc[base_date]

    # Cost breakdown: 30% Copper, 30% Steel, 40% Labor/Fixed (NREL, 2024)
    df_norm["Raw_Material_Index"] = (
        (df_norm["Copper_PPI"] * 0.3) + (df_norm["Steel_PPI"] * 0.3) + 0.4
    )
    df_norm["Adjusted_Transformer_Price"] = (
        df_norm["Transformer_PPI"] / df_norm["Raw_Material_Index"]
    )
    return (df_norm,)


@app.cell
def _(annotated_series, cfg, df_norm, save_fig):
    _columns = {
        "Transformer_PPI": {
            "color": "#d62728",
            "linewidth": 2,
            "label": "Actual Transformer PPI",
        },
        "Adjusted_Transformer_Price": {
            "color": "#2ca02c",
            "linewidth": 2,
            "linestyle": "--",
            "label": "Material-Adjusted (Hidden Learning)",
        },
    }

    fig_nominal = annotated_series(
        df_norm,
        _columns,
        "Transformer Prices: Nominal vs. Material-Adjusted",
        ylabel="Normalized Index (Base = 1.0)",
        fill_between=("Transformer_PPI", "Adjusted_Transformer_Price"),
    )
    save_fig(fig_nominal, cfg.img_dir / "dd001_nominal_vs_adjusted.png")
    return


@app.cell
def _(annotated_series, cfg, df_norm, pd, save_fig):
    _columns_pre = {
        "Transformer_PPI": {
            "color": "#d62728",
            "linewidth": 2,
            "label": "Actual Transformer PPI",
        },
        "Adjusted_Transformer_Price": {
            "color": "#2ca02c",
            "linewidth": 2,
            "linestyle": "--",
            "label": "Material-Adjusted (Hidden Learning)",
        },
    }
    _annotations = [
        (
            "Underlying Efficiency Trend",
            pd.Timestamp("2019-01-01"),
            0.9,
            (pd.Timestamp("2016-01-01"), 0.5),
        )
    ]

    fig_pre2020 = annotated_series(
        df_norm,
        _columns_pre,
        "Pre-2020: The Signal Under the Noise",
        annotations=_annotations,
        ylabel="Normalized Index (Base = 1.0)",
        fill_between=("Transformer_PPI", "Adjusted_Transformer_Price"),
    )
    save_fig(fig_pre2020, cfg.img_dir / "dd001_pre2020_signal.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo):
    _nominal_chart = mo.image(
        src=(cfg.img_dir / "dd001_nominal_vs_adjusted.png").read_bytes(), width=800
    )
    mo.md(f"""
    ## Decomposing the Price Signal

    Transformer prices are rising. But is that because manufacturing is getting less
    efficient, or because the raw materials are getting more expensive? To separate the
    two, I built a rough cost decomposition: ~30% copper, ~30% steel, ~40% labor and
    fixed costs (NREL, 2024). Dividing the transformer PPI by a weighted material index
    isolates a proxy for the manufacturing efficiency trend.

    # Transformer Prices: Nominal vs. Material-Adjusted

    {_nominal_chart}

    The red line is the nominal PPI — the headline number in industry reports. The
    green dashed line strips out commodity volatility. It shows a different dynamic:
    **the manufacturing process itself has been getting steadily more efficient.** The
    post-2021 price surge is almost entirely a raw material and lead-time tax, not a
    manufacturing failure.

    This distinction matters. If the price increase were driven by worsening
    manufacturing economics, the scarcity framing would be the whole story. Instead,
    there appears to be a **learning curve** hiding under commodity noise.
    """)
    return


@app.cell(hide_code=True)
def _(bespoke_vs_modular, mo):
    mo.md(f"""
    ## The Hypothesis: Wright's Law in Grid Hardware?

    **Wright's Law** is the empirical observation that for every doubling of cumulative
    production, unit cost falls by a roughly constant percentage. Solar PV exhibits a
    learning rate of ~20% (IRENA, 2023). Lithium-ion batteries ~18% (BloombergNEF,
    2024). These rates reflect the compounding effects of manufacturing experience,
    process optimization, and design-for-manufacturing.

    Grid hardware has historically shown **near-zero** learning rates. The standard
    explanation is that the grid is old and slow-moving. But the data suggests a more
    specific structural reason. The grid is a **spectrum**:

    {bespoke_vs_modular}

    At one end: **Large Power Transformers (LPTs)** — 500kV+, custom impedance matching,
    site-specific thermal designs. Each one is engineered from scratch. At the other end:
    **distribution transformers** — pad-mounted units, modular switchgear. These *could* be
    standardized, but historically there was never enough volume of any single design to
    justify manufacturing innovation. Over 80,000 unique transformer configurations exist
    globally (Uptime Institute).

    The question: **is AI demand concentrated enough in the standardizable segment
    to trigger learning effects that historical demand patterns never could?**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    | Domain | Role | Key Hardware | Standardizable? |
    | :--- | :--- | :--- | :--- |
    | **Generation** | Creating electrons | Generators, step-up transformers | Partially (site-dependent) |
    | **Transmission** | High-voltage superhighway (66kV-765kV) | **Large Power Transformers** | No (custom engineering) |
    | **Distribution** | Last-mile delivery (11kV-33kV) | **Distribution transformers** | **Yes** (factory-built, repeatable) |
    """)
    return


@app.cell
def _(distribution_hub, mo, transmission_titan):
    mo.md(f"""
    {mo.hstack([
        mo.vstack([
            mo.md("**The Transmission Titan (LPT)**"),
            transmission_titan,
            mo.md("100MVA+ units ($1.4M-$2.5M). Custom-engineered. Lead times: ~38 months."),
        ]),
        mo.vstack([
            mo.md("**The Distribution Hub**"),
            distribution_hub,
            mo.md("Pad-mounted units. Factory-built. **This is where standardization could bite.**"),
        ]),
    ], justify="space-around")}
    """)
    return


@app.cell(hide_code=True)
def _(bespoke_vs_commodity, mo):
    mo.md(f"""
    ## A Precedent: What Tesla Did for Batteries

    The closest precedent for a demand shock unlocking a dormant learning curve is
    EV batteries.

    - **Phase 1 — Premium funds capability.** Tesla's Roadster and Model S/X were
      low-volume, high-margin. They funded battery R&D but didn't bend the cost curve
      themselves.
    - **Phase 2 — Volume unlocks manufacturing innovation.** The Model 3/Y justified
      gigacasting, structural battery packs, simplified wiring. Fundamentally different
      manufacturing designed for scale. *That* is where the learning rate kicked in.
    - **Phase 3 — Both segments coexist.** Model S/X are still produced. The premium didn't
      disappear — volume unlocked a parallel commodity track alongside it.

    Government incentives (EV tax credits, ZEV mandates) created the demand certainty that
    justified the capex. The IRA and grid modernization mandates may be playing the same
    role for transformers today.

    {bespoke_vs_commodity}
    *A Bugatti is still hand-built. A Volkswagen rolls off a robotic line. Both exist — but
    only one segment has a learning curve. The question is which segment of the grid AI
    demand is growing.*

    There is a direct supply chain parallel unfolding now. **Cleveland-Cliffs** — the
    sole U.S. producer of Grain-Oriented Electrical Steel — announced a $150M vertically
    integrated transformer plant in Weirton, WV (online H1 2026). A steel company
    building transformers is a structural bet on sustained, standardized volume.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## The Skeptical Case: When Learning Curves Don't Show Up

    Brian Potter's *Construction Physics* work (and his book *The Origins of Efficiency*,
    Stripe Press, 2024) provides the strongest framework for **why learning curves fail**
    in construction-adjacent industries. His core argument: Wright's Law is not a law of
    nature. It is an empirical regularity that holds when specific structural conditions
    are met. When those conditions are absent, costs stagnate — or even *increase* with
    volume.

    Potter identifies five conditions that must hold for learning curves to emerge:

    **1. Repetition of identical units.** Every variation resets the learning clock. In
    construction, every project means new workers, new site, new design. With 80,000+
    transformer configurations, is AI demand actually compressing this variation — or just
    adding volume across the same fragmented landscape?

    **2. Stable production environment.** Factory beats field. LPTs are partially
    site-assembled (too large to ship fully built). Distribution transformers are
    factory-built — a point *in favor* of the hypothesis for that segment.

    **3. Continuous production runs.** Learning degrades with stop-start ordering.
    Historically, transformer orders came in irregular batches from different utilities
    with different specs. Hyperscalers are now placing multi-year, multi-site contracts —
    Compass Datacenters partnered with Eaton in 2025 to deploy standardized modular power
    blocks. This is new.

    **4. No regulatory ratcheting.** This is the nuclear lesson. Arnulf Grubler's 2010
    study of France's nuclear program is the canonical counterexample: France had
    centralized decision-making, standardized reactor designs, regulatory stability —
    everything going for it. Yet reactor costs *tripled in real terms* over the program's
    lifetime. Each generation triggered new safety requirements that reset the learning
    curve. Grubler called this **"negative learning by doing."** The transformer parallel:
    DOE's 2023 efficiency standards mandate higher-grade GOES steel, increasing material
    costs. If regulations ratchet faster than manufacturing can optimize, you get the
    nuclear outcome.

    **5. The product doesn't increase in complexity.** Solar panels get simpler as they
    scale (thinner cells, fewer materials, streamlined processes). Nuclear reactors got more
    complex (safety systems, fuel cycle management). Are data center transformers getting
    simpler through standardization, or more complex through smart grid integration and
    monitoring requirements? This remains an open question.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Testing the Hypothesis: A Scorecard

    Applying Potter's five conditions to the two segments of the transformer market
    produces a diagnostic rather than a conclusion:

    | Condition | LPTs (Transmission) | Distribution Transformers |
    | :--- | :--- | :--- |
    | Identical units | **Fail** — custom-engineered | **Partial pass** — standardizing via hyperscaler specs |
    | Stable environment | **Fail** — partial site assembly | **Pass** — factory-built |
    | Continuous production | **Fail** — irregular, one-off orders | **Passing** — multi-year hyperscaler contracts |
    | No regulatory ratcheting | **Risk** — DOE efficiency mandates | **Risk** — same DOE mandates |
    | Decreasing complexity | **Fail** — smart grid adds complexity | **Uncertain** — standardization simplifies, monitoring adds |

    LPTs fail on almost every condition. They are the Grubler nuclear analogy —
    large, lumpy, bespoke, and subject to regulatory ratcheting. Asserting learning
    curves for LPTs is not supported by the structural evidence.

    Distribution transformers are a credible candidate. They pass on factory environment
    and are increasingly passing on continuous production. The open risks are regulatory
    ratcheting (DOE standards) and whether complexity is trending up or down.

    The scorecard identifies *where to look next*, not what the answer is.
    """)
    return


@app.cell(hide_code=True)
def _(cfg, mo):
    _pre2020_chart = mo.image(
        src=(cfg.img_dir / "dd001_pre2020_signal.png").read_bytes(), width=800
    )
    mo.md(f"""
    ## Back to the Data: Fitting a Learning Rate

    With Potter's framework as a filter, the pre-2020 FRED data warrants a closer look.
    Before the commodity shock, the material-adjusted price shows a visible downward
    trend. The next step is to fit a Wright's Law model to it.

    # Pre-2020: The Signal Under the Noise

    {_pre2020_chart}

    A proper Wright's Law fit requires cumulative *units produced* on the x-axis.
    Segment-level production volume data for U.S. transformers does not appear to be
    publicly available. As a proxy, I use the cumulative sum of the PPI index as a
    stand-in for production activity. **This is a meaningful limitation** — the proxy
    is directionally informative but not equivalent to actual production volume. The
    NREL 2024 distribution transformer assessment may contain better data for a future
    iteration.
    """)
    return


@app.cell
def _(df_norm, mo, np):
    df_norm["Cumulative_Proxy"] = df_norm["Transformer_PPI"].expanding().sum()
    log_vol = np.log(df_norm["Cumulative_Proxy"])
    log_price = np.log(df_norm["Adjusted_Transformer_Price"])
    slope, intercept = np.polyfit(log_vol, log_price, 1)
    learning_rate = 1 - (2**slope)

    result_stat = mo.stat(
        label="Estimated Learning Rate (with caveats)",
        value=f"{learning_rate * 100:.2f}%",
        caption="Cost reduction per doubling of cumulative production proxy (material-adjusted)",
    )
    result_stat
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    This estimate is *consistent with* a ~12% learning rate, which falls within the
    range BCG observed across heavy industrial products in the 1960s-70s (10-25%).
    Three caveats constrain how far this result can be pushed:

    - This is a **proxy**, not a measurement. A real Wright's Law fit needs cumulative
      production volume, not a cumulative price index.
    - The PPI aggregates *all* transformers — LPTs, distribution, specialty. It doesn't
      isolate the standardizable segment where learning curves would most plausibly emerge.
    - The signal is pre-2020. Whether AI demand *accelerates* or *disrupts* this trend is
      the open question.

    **The data is consistent with the hypothesis but does not prove it.** Confirmation
    would require segment-level production volume and cost data, which may exist in
    proprietary industry databases (IHS Markit, Wood Mackenzie) but is not publicly
    available.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Open Questions

    Six questions need to be resolved to move from hypothesis to conviction:

    **1. Segment-level data.** The PPI bundles all transformers together. Can I isolate
    distribution transformer pricing from LPTs? NREL's 2024 assessment and DOE's supply
    chain reports may have this.

    **2. The DOE regulatory ratchet.** The 2023 efficiency standards mandate amorphous
    steel cores for many distribution transformers, which are more expensive than
    conventional GOES. Is this a one-time step-change that manufacturers absorb, or the
    start of a French nuclear-style escalation?

    **3. Hyperscaler spec convergence.** Are Microsoft, Google, and Amazon actually ordering
    the same transformer designs? Or are they each specifying custom configurations? The
    Compass/Eaton partnership suggests convergence, but I need more evidence.

    **4. Cleveland-Cliffs as a leading indicator.** A steel company vertically integrating
    into transformer manufacturing is a strong signal that *someone* believes standardized
    volume is coming. But is this a bet on AI demand specifically, or on broader grid
    modernization and the IRA?

    **5. The solid-state wildcard.** Solid-state transformers (SSTs) use power electronics
    instead of iron cores. If they scale like semiconductors, they leapfrog the entire
    traditional manufacturing question. Canary Media flagged them as "advancing faster than
    expected" in their 2026 outlook. This could render the whole
    learning-curve-for-traditional-transformers question moot.

    **6. Who captures the benefit?** Even if learning curves emerge in the standardizable
    segment, the financing question matters. If hyperscalers capture the cost decline through
    private procurement while ratepayers bear the infrastructure costs, the "AI modernizes
    the grid" narrative becomes more complicated. In 2024, $4.3B in systemic grid connection
    costs were assigned to general ratepayers in the mid-Atlantic (Union of Concerned
    Scientists).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Where This Goes Next

    This investigation established a hypothesis and a first-pass data signal. The
    remaining parts formalize and stress-test it:

    - **Part 2 — Feedback Architecture** (`02_feedback_architecture.py`): Causal loop
      diagram and PySD stock-and-flow simulation identifying which feedback loops
      dominate under different parameter regimes.
    - **Part 3 — Bayesian Estimation** (`03_bayesian_estimation.py`): PyMC model
      quantifying uncertainty around the learning rate with proper production volume
      priors.
    - **Part 4 — Regime Switching** (`04_regime_switching.py`): Markov switching model
      testing whether AI demand constitutes a structural break or another commodity cycle.

    The goal is a model that makes assumptions explicit and uncertainties measurable.
    If the learning curve thesis is wrong, the model should identify *where* it breaks.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ---
    ### Sources and Further Reading

    **Data:**
    - **FRED:** PPI Series `PCU335311335311` (Transformers), `WPU102501` (Copper), `WPU1017` (Steel)
    - **NREL (2024):** *Distribution Transformer Supply and Demand Assessment.* [Link](https://www.nrel.gov/docs/fy24osti/88441.pdf)

    **Industry Analysis:**
    - **Wood Mackenzie (2024):** *The Era of Flat Power Demand is Over.* [Link](https://www.woodmac.com/news/opinion/the-era-of-flat-power-demand-is-over/)
    - **Wood Mackenzie (2025):** *Power transformers and distribution transformers will face supply deficits of 30% and 10% in 2025.* [Link](https://www.woodmac.com/press-releases/power-transformers-and-distribution-transformers-will-face-supply-deficits-of-30-and-10-in-2025/)
    - **Bloomberg NEF (2025):** *AI and the Power Grid: Where the Rubber Meets the Road.* [Link](https://about.bnef.com/insights/clean-energy/ai-and-the-power-grid-where-the-rubber-meets-the-road/)
    - **DOE (2022):** *Electric Grid Supply Chain Review.* [Link](https://www.energy.gov/sites/default/files/2022-02/Electric%20Grid%20Supply%20Chain%20Report%20-%20Final.pdf)

    **Learning Curves and Skepticism:**
    - **Brian Potter:** *How Accurate Are Learning Curves?* and *Where Are My Damn Learning Curves?* — [Construction Physics](https://www.construction-physics.com/)
    - **Brian Potter:** *The Origins of Efficiency* (Stripe Press, 2024)
    - **Arnulf Grubler (2010):** *The costs of the French nuclear scale-up: A case of negative learning by doing.* [Energy Policy](https://www.sciencedirect.com/science/article/abs/pii/S0301421510003526)
    - **Ramez Naam (2020):** *Solar's Future is Insanely Cheap.* [Link](https://rameznaam.com/2020/05/14/solars-future-is-insanely-cheap-2020/)
    - **Casey Handmer:** *Grid Storage: Batteries Will Win* and *Direct Current Data Centers.* [Blog](https://caseyhandmer.wordpress.com/)

    **Manufacturing:**
    - **Cleveland-Cliffs (2024):** Weirton transformer plant announcement. [Press release](https://www.clevelandcliffs.com/news/news-releases/detail/644/)
    - **Northfield Transformers (2025):** *Data Center Expansion is Reshaping Transformer Demand.* [Link](https://northfieldtransformers.com/blog/data-center-expansion-reshaping-transformer-demand/)

    *DD-001 · Part 1 of 4*
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
