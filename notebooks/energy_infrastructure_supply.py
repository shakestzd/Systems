import marimo

__generated_with = "0.19.11"
app = marimo.App(
    width="medium",
    app_title="Energy Infrastructure Supply Chain: Transformer Dynamics",
)


@app.cell
def _():
    from pathlib import Path

    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    from scipy.integrate import solve_ivp

    plt.style.use(Path(__file__).parent / "shakes.mplstyle")

    return Path, mo, np, pd, plt, solve_ivp


@app.cell
def _(mo):
    mo.md(r"""
    # Energy Infrastructure Supply Chain: Transformer Dynamics

    This notebook models the **transformer supply chain crisis** driven by converging
    demand from AI data centers, grid modernization, renewables integration, and aging
    infrastructure replacement. It explores:

    | Analysis | Method | Question |
    |----------|--------|----------|
    | **Supply-demand dynamics** | Systems dynamics (ODE) | How do manufacturing delays create boom-bust cycles? |
    | **Bubble burst scenarios** | Monte Carlo simulation | What happens to transformer supply if AI CapEx contracts? |
    | **Crowding-out** | Comparative analysis | How does LPT demand affect distribution transformer availability for minigrids? |
    | **Historical precedent** | Fiber optic comparison | Does the dot-com fiber glut predict a transformer surplus? |

    **Core thesis:** The transformer supply chain exhibits classic bullwhip dynamics —
    long manufacturing delays (2-4 years), concentrated suppliers, and inelastic demand
    create conditions where capacity expansion announced today arrives *after* the demand
    signal that triggered it may have shifted. The structural question is whether non-AI
    demand (grid aging, electrification, renewables) provides a durable floor that
    prevents a fiber-optic-style glut.

    **Data sources:** Wood Mackenzie T&D supply surveys, IEA grid infrastructure reports,
    manufacturer press releases (Hitachi Energy, Siemens Energy, GE Vernova, Eaton),
    NIAC/CISA transformer shortage report (June 2024), NREL distribution transformer
    demand projections.

    ---
    """)
    return


@app.cell
def _(Path, mo, np, pd):
    """Load reference data from CSVs."""
    import duckdb

    _data_dir = Path(__file__).resolve().parent.parent / "data"
    _external = _data_dir / "external"
    _processed = _data_dir / "processed"

    # Lead times
    lead_times = pd.read_csv(_external / "transformer_lead_times.csv")

    # Manufacturing capacity expansions
    mfg_capacity = pd.read_csv(_external / "transformer_mfg_capacity.csv")

    # Market metrics
    _market_raw = pd.read_csv(_external / "transformer_market.csv")
    market = dict(zip(_market_raw["metric"], _market_raw["value"]))

    # Commodity prices (if available from pipeline)
    _commodity_path = _processed / "commodity_prices.parquet"
    copper_prices = None
    if _commodity_path.exists():
        _con = duckdb.connect()
        copper_prices = _con.sql(f"""
            SELECT date, close AS price
            FROM '{_commodity_path}'
            WHERE ticker = 'HG=F'
            ORDER BY date
        """).df()
        _con.close()

    # Hyperscaler CapEx (for demand context)
    _capex_path = _processed / "hyperscaler_capex.parquet"
    capex_quarterly = None
    if _capex_path.exists():
        _con = duckdb.connect()
        capex_quarterly = _con.sql(f"""
            SELECT date, ROUND(SUM(capex_bn), 2) AS total_capex_bn
            FROM '{_capex_path}'
            GROUP BY date ORDER BY date
        """).df()
        _con.close()

    mo.md(f"""
    **Data loaded:**
    - Lead time history: {len(lead_times)} observations \
({lead_times['year'].min()}-{lead_times['year'].max()})
    - Manufacturer expansions: {len(mfg_capacity)} projects
    - Market metrics: {len(market)} indicators
    - Copper prices: {'available' if copper_prices is not None else 'run pipeline first'}
    - Hyperscaler CapEx: {'available' if capex_quarterly is not None else 'run pipeline first'}
    """)
    return capex_quarterly, copper_prices, lead_times, market, mfg_capacity


@app.cell
def _(mo):
    mo.md("""
    ## 1. The Supply Crisis in Numbers

    Power transformer lead times have quadrupled since 2019, from ~30 weeks to ~128 weeks.
    Generator step-up units (critical for renewables) are even worse at 144 weeks.
    Circuit breakers approach 3 years. Meanwhile, manufacturing capacity grows at 3-4%
    annually against 7-9% demand growth — a structural deficit that won't close until
    the late 2020s even under optimistic scenarios.
    """)
    return


@app.cell
def _(lead_times, np, pd, plt):
    """Visualize lead time explosion by equipment type."""
    _fig, _axes = plt.subplots(1, 2, figsize=(12, 5))

    # Panel 1: Lead times over time
    _ax1 = _axes[0]
    _equipment_labels = {
        "power_transformer": "Power Transformer",
        "distribution_transformer": "Distribution Transformer",
        "generator_stepup": "Generator Step-Up",
        "circuit_breaker": "Circuit Breaker",
        "mv_switchgear": "MV Switchgear",
    }
    for _etype, _label in _equipment_labels.items():
        _subset = lead_times[lead_times["equipment_type"] == _etype]
        _ax1.plot(_subset["year"], _subset["lead_weeks"], marker="o", label=_label, linewidth=2)

    _ax1.set_xlabel("Year")
    _ax1.set_ylabel("Lead Time (weeks)")
    _ax1.set_title("Equipment Lead Times")
    _ax1.legend(fontsize=7, loc="upper left")
    _ax1.axhline(y=52, color="grey", linestyle="--", alpha=0.5, linewidth=0.8)
    _ax1.annotate("1 year", xy=(2019.1, 54), fontsize=7, color="grey")
    _ax1.axhline(y=104, color="grey", linestyle="--", alpha=0.5, linewidth=0.8)
    _ax1.annotate("2 years", xy=(2019.1, 106), fontsize=7, color="grey")

    # Panel 2: Supply deficit and demand growth
    _ax2 = _axes[1]
    _categories = ["Power\nTransformer", "Distribution\nTransformer", "Generator\nStep-Up"]
    _demand_growth = [116, 41, 274]
    _price_increase = [77, 95, 45]

    _x = np.arange(len(_categories))
    _width = 0.35
    _bars1 = _ax2.bar(_x - _width / 2, _demand_growth, _width, label="Demand Growth (% since 2019)")
    _bars2 = _ax2.bar(
        _x + _width / 2, _price_increase, _width,
        label="Price Increase (% since 2019)",
    )
    _ax2.set_ylabel("Percent (%)")
    _ax2.set_title("Demand Growth vs Price Impact")
    _ax2.set_xticks(_x)
    _ax2.set_xticklabels(_categories, fontsize=8)
    _ax2.legend(fontsize=7)

    for _bar in _bars1:
        _ax2.annotate(
            f"{int(_bar.get_height())}%",
            xy=(_bar.get_x() + _bar.get_width() / 2, _bar.get_height()),
            ha="center", va="bottom", fontsize=7,
        )
    for _bar in _bars2:
        _ax2.annotate(
            f"{int(_bar.get_height())}%",
            xy=(_bar.get_x() + _bar.get_width() / 2, _bar.get_height()),
            ha="center", va="bottom", fontsize=7,
        )

    _fig.suptitle(
        "Transformer Supply Crisis (2019-2025)",
        fontsize=13, fontweight="bold", y=1.02,
    )
    plt.tight_layout()
    _fig
    return


@app.cell
def _(mo):
    mo.md("""
    ## 2. Model Configuration
    """)
    return


@app.cell
def _(mo):
    demand_growth = mo.ui.slider(
        0.04, 0.12, value=0.08, step=0.01,
        label="Transformer demand growth (annual)",
    )
    supply_growth = mo.ui.slider(
        0.02, 0.08, value=0.035, step=0.005,
        label="Mfg capacity growth (annual)",
    )
    factory_delay = mo.ui.slider(
        1.0, 5.0, value=3.0, step=0.5,
        label="Factory construction delay (years)",
    )
    goes_elasticity = mo.ui.slider(
        0.1, 1.0, value=0.4, step=0.1,
        label="GOES supply elasticity",
    )
    sim_years = mo.ui.slider(
        5, 20, value=12, step=1, label="Simulation horizon (years)",
    )

    mo.vstack([
        mo.md("**Adjust key parameters** — the SD model updates reactively:"),
        mo.hstack([demand_growth, supply_growth], justify="start", gap=2),
        mo.hstack([factory_delay, goes_elasticity], justify="start", gap=2),
        sim_years,
    ])
    return demand_growth, factory_delay, goes_elasticity, sim_years, supply_growth


@app.cell
def _(mo):
    mo.md(r"""
    ## 3. Systems Dynamics Model: Transformer Supply-Demand

    The model tracks four coupled stocks:

    | Stock | Initial Value | Unit | Source |
    |-------|--------------|------|--------|
    | **Order Backlog** $B$ | 2.5 | years of production | Wood Mackenzie (128 wk lead time) |
    | **Manufacturing Capacity** $M$ | 1.0 | normalized (2025 = 1.0) | Baseline |
    | **GOES Inventory** $G$ | 0.8 | normalized (adequate = 1.0) | Cleveland-Cliffs constraints |
    | **Installed Fleet Age** $A$ | 0.55 | fraction past service life | NREL (40M of ~70M units) |

    **Key feedback loops:**

    - **R1 (Investment Signal):** High backlog → price signal → manufacturer investment → capacity expansion (delayed 2-4 years)
    - **R2 (Demand Amplification):** AI CapEx growth → data center demand → transformer orders → backlog increase
    - **B1 (Capacity Catch-Up):** New factories online → production increases → backlog drains → lead times shorten
    - **B2 (Demand Destruction):** High prices → marginal project cancellation → demand reduction
    - **B3 (GOES Constraint):** Low GOES inventory → production slowdown → capacity underutilized despite demand

    $$\frac{dB}{dt} = D(t) - P(M, G)$$
    $$\frac{dM}{dt} = I(B, t-\tau) \cdot s_M$$
    $$\frac{dG}{dt} = S_G(p) - U_G(M)$$
    $$\frac{dA}{dt} = \text{aging rate} - \text{replacement rate}(P)$$
    """)
    return


@app.cell
def _(demand_growth, factory_delay, goes_elasticity, market, np, plt, sim_years, solve_ivp, supply_growth):
    """Systems dynamics model: transformer supply-demand with delays."""

    # Parameters from sliders
    _d_growth = demand_growth.value       # annual demand growth rate
    _s_growth = supply_growth.value       # annual capacity growth rate
    _tau = factory_delay.value            # factory construction delay (years)
    _goes_e = goes_elasticity.value       # GOES supply elasticity
    _T = sim_years.value                  # simulation horizon

    # Demand decomposition (shares of total transformer demand)
    _ai_dc_share = 0.30        # AI / data center share
    _renewables_share = 0.25   # renewables integration (GSUs etc.)
    _replacement_share = 0.25  # aging fleet replacement
    _grid_mod_share = 0.20     # grid modernization / electrification

    def _transformer_odes(t, y):
        B, M, G, A = y  # backlog, mfg capacity, GOES inventory, fleet age fraction

        # Demand: AI-driven + structural
        ai_demand = _ai_dc_share * (1 + _d_growth) ** t
        structural_demand = (1 - _ai_dc_share) * (1 + 0.04) ** t  # 4% structural growth
        total_demand = ai_demand + structural_demand

        # Production: constrained by capacity AND GOES availability
        goes_factor = min(1.0, G / 0.6)  # production drops if GOES < 0.6
        production = M * goes_factor

        # Backlog dynamics
        dB = total_demand - production

        # Capacity investment: responds to backlog with delay
        # Investment signal based on backlog level (high backlog → more investment)
        if t > _tau:
            investment_signal = max(0, (B - 1.0) * 0.3)  # invest when backlog > 1 year
        else:
            investment_signal = max(0, (B - 1.0) * 0.15)  # early phase: less response
        dM = _s_growth * M + investment_signal * 0.1

        # GOES dynamics: supply responds to price (proxy: backlog level)
        goes_supply = 0.15 * (1 + _goes_e * max(0, B - 1.5))  # supply responds to scarcity
        goes_usage = 0.12 * M * goes_factor
        dG = goes_supply - goes_usage

        # Fleet aging: fraction past service life
        replacement_rate = production * 0.3 * (1 / (1 + B))  # replacement harder when backlog high
        aging_rate = 0.02  # ~2% of fleet ages past service life annually
        dA = aging_rate - replacement_rate * 0.05

        return [dB, dM, dG, dA]

    _y0 = [2.5, 1.0, 0.8, 0.55]  # initial conditions (2025)
    _t_span = (0, _T)
    _t_eval = np.linspace(0, _T, _T * 12)  # monthly resolution

    _sol = solve_ivp(
        _transformer_odes, _t_span, _y0, t_eval=_t_eval,
        method="RK45", max_step=0.1,
    )

    _years = 2025 + _sol.t
    _B, _M, _G, _A = _sol.y

    # Convert backlog to lead time in weeks
    _lead_time_weeks = _B * 52

    # Plot
    _fig, _axes = plt.subplots(2, 2, figsize=(12, 8))

    # Backlog → lead time
    _ax = _axes[0, 0]
    _ax.plot(_years, _lead_time_weeks, linewidth=2)
    _ax.axhline(y=128, color="red", linestyle="--", alpha=0.6, linewidth=0.8)
    _ax.annotate("Current (128 wk)", xy=(2025.5, 132), fontsize=7, color="red")
    _ax.axhline(y=35, color="green", linestyle="--", alpha=0.6, linewidth=0.8)
    _ax.annotate("Pre-2020 baseline", xy=(2025.5, 38), fontsize=7, color="green")
    _ax.set_ylabel("Lead Time (weeks)")
    _ax.set_title("Power Transformer Lead Time")

    # Manufacturing capacity
    _ax = _axes[0, 1]
    _ax.plot(_years, _M, linewidth=2, color="C1")
    _ax.set_ylabel("Normalized Capacity (2025 = 1.0)")
    _ax.set_title("Manufacturing Capacity")
    _ax.annotate(
        f"Final: {_M[-1]:.2f}x",
        xy=(_years[-1], _M[-1]), fontsize=8,
        xytext=(-60, 10), textcoords="offset points",
        arrowprops=dict(arrowstyle="->", color="C1"),
    )

    # GOES inventory
    _ax = _axes[1, 0]
    _ax.plot(_years, _G, linewidth=2, color="C2")
    _ax.axhline(y=0.6, color="red", linestyle="--", alpha=0.6, linewidth=0.8)
    _ax.annotate("Production constraint threshold", xy=(2025.5, 0.62), fontsize=7, color="red")
    _ax.set_ylabel("Normalized Inventory")
    _ax.set_title("GOES (Electrical Steel) Inventory")
    _ax.set_xlabel("Year")

    # Fleet aging
    _ax = _axes[1, 1]
    _ax.plot(_years, _A * 100, linewidth=2, color="C3")
    _ax.set_ylabel("% Past Service Life")
    _ax.set_title("Distribution Transformer Fleet Age")
    _ax.set_xlabel("Year")

    _fig.suptitle(
        "Transformer Supply Chain Dynamics"
        f" (demand +{_d_growth:.0%}/yr, capacity +{_s_growth:.1%}/yr)",
        fontsize=13, fontweight="bold", y=1.02,
    )
    plt.tight_layout()
    _fig
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 4. Manufacturer Capacity Expansion Timeline

    OEMs have committed **>$1.8 billion** in North American transformer capacity since
    2023. But new factories take 2-4 years from announcement to production. The critical
    question: does the capacity arrive before or after the demand peak?

    Key investments:
    - **Hitachi Energy:** $457M South Boston VA (2028), $195M CAD Varennes QC (2027)
    - **Siemens Energy:** $400M Charlotte NC — first US LPT plant (2026)
    - **GE Vernova:** $5.3B Prolec GE acquisition + $600M in expansions
    - **Eaton:** $340M Jonesville SC (2027), doubled TX output (2025)
    """)
    return


@app.cell
def _(mfg_capacity, np, pd, plt):
    """Visualize manufacturer capacity expansion timeline."""
    # Filter to real projects (exclude halted Weirton, and zero-investment rows)
    _active = mfg_capacity[
        (mfg_capacity["completion_year"] > 0)
        & (mfg_capacity["investment_usd_m"] > 0)
    ].copy()
    _active = _active.sort_values("completion_year")

    # Group by completion year
    _by_year = _active.groupby("completion_year")["investment_usd_m"].sum()

    # Cumulative investment timeline
    _fig, _axes = plt.subplots(1, 2, figsize=(12, 5))

    # Panel 1: Investment by manufacturer
    _ax1 = _axes[0]
    _by_mfg = (
        _active.groupby("manufacturer")["investment_usd_m"]
        .sum()
        .sort_values(ascending=True)
    )
    _colors = plt.cm.Set2(np.linspace(0, 1, len(_by_mfg)))
    _ax1.barh(_by_mfg.index, _by_mfg.values, color=_colors)
    _ax1.set_xlabel("Investment ($M USD)")
    _ax1.set_title("Capacity Investment by Manufacturer")
    for _i, (_mfg, _val) in enumerate(_by_mfg.items()):
        if _val > 50:
            _ax1.annotate(f"${_val:.0f}M", xy=(_val + 10, _i), va="center", fontsize=7)

    # Panel 2: Capacity coming online by year
    _ax2 = _axes[1]
    _cumulative = _by_year.cumsum()
    _ax2.bar(_by_year.index, _by_year.values, alpha=0.6, label="Annual investment")
    _ax2.plot(
        _cumulative.index, _cumulative.values,
        "o-", color="C3", linewidth=2, label="Cumulative",
    )
    _ax2.set_xlabel("Completion Year")
    _ax2.set_ylabel("Investment ($M USD)")
    _ax2.set_title("Capacity Expansion Timeline")
    _ax2.legend(fontsize=8)
    _ax2.axvline(x=2025, color="grey", linestyle=":", alpha=0.5)
    _ax2.annotate("Today", xy=(2025, _ax2.get_ylim()[1] * 0.9), fontsize=8, color="grey")

    _fig.suptitle(
        "Transformer Manufacturing Capacity Investments",
        fontsize=13, fontweight="bold", y=1.02,
    )
    plt.tight_layout()
    _fig
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 5. Bubble Burst Scenario Analysis

    What happens to the transformer supply chain under different AI CapEx trajectories?

    Three scenarios are modeled via Monte Carlo simulation:

    | Scenario | AI CapEx Growth | Probability Weight | Rationale |
    |----------|-----------------|--------------------|-----------|
    | **Sustained Boom** | +15-25%/yr through 2030 | 40% | Sovereign funds + structural cloud migration |
    | **Moderate Plateau** | +5-10%/yr, flattening 2027 | 35% | ROI pressure, efficiency gains |
    | **Severe Contraction** | -30-50% from peak by 2028 | 25% | Dot-com-style correction, debt unwinding |

    **Key insight from demand decomposition:** AI/data centers represent ~25-35% of
    transformer demand. Even in a severe bust, the remaining 65-75% (grid aging,
    renewables, electrification) provides a structural floor. The most likely outcome
    is **lead time normalization**, not a true surplus.
    """)
    return


@app.cell
def _(mo):
    bust_severity = mo.ui.slider(
        0.20, 0.70, value=0.50, step=0.05,
        label="AI CapEx contraction in bust scenario (%)",
    )
    n_sims = mo.ui.slider(
        100, 2000, value=500, step=100,
        label="Monte Carlo simulations",
    )
    mo.hstack([bust_severity, n_sims], justify="start", gap=2)
    return bust_severity, n_sims


@app.cell
def _(bust_severity, n_sims, np, plt):
    """Monte Carlo: transformer demand under AI boom/plateau/bust."""
    _rng = np.random.default_rng(42)
    _n = int(n_sims.value)
    _years_fwd = 10
    _t = np.arange(_years_fwd + 1)
    _year_labels = 2025 + _t

    # Demand decomposition (2025 baseline = 1.0)
    _ai_share = 0.30
    _structural_share = 0.70  # renewables + replacement + grid mod

    # Scenario weights
    _weights = np.array([0.40, 0.35, 0.25])

    _all_paths = np.zeros((_n, _years_fwd + 1))
    _all_paths[:, 0] = 1.0  # normalized to 2025

    _scenario_labels = []
    _bust_frac = bust_severity.value

    for _i in range(_n):
        # Assign scenario
        _scenario = _rng.choice(3, p=_weights)
        _scenario_labels.append(_scenario)

        for _yr in range(1, _years_fwd + 1):
            # Structural demand always grows (aging fleet, electrification, renewables)
            _structural = _structural_share * (1 + _rng.normal(0.04, 0.01)) ** _yr

            if _scenario == 0:  # Sustained boom
                _ai = _ai_share * (1 + _rng.normal(0.20, 0.05)) ** _yr
            elif _scenario == 1:  # Moderate plateau
                if _yr <= 3:
                    _ai = _ai_share * (1 + _rng.normal(0.10, 0.03)) ** _yr
                else:
                    _ai = _ai_share * (1 + 0.10) ** 3 * (1 + _rng.normal(0.02, 0.02)) ** (_yr - 3)
            else:  # Severe contraction
                if _yr <= 2:
                    _ai = _ai_share * (1 + _rng.normal(0.15, 0.05)) ** _yr
                elif _yr <= 4:
                    _peak = _ai_share * (1.15) ** 2
                    _ai = _peak * (1 - _bust_frac * (_yr - 2) / 2)
                else:
                    _ai = _ai_share * (1 - _bust_frac * 0.6)  # partial recovery

            _all_paths[_i, _yr] = _structural + max(_ai, 0.05)

    _scenario_labels = np.array(_scenario_labels)

    # Plot
    _fig, _axes = plt.subplots(1, 2, figsize=(12, 5))

    # Panel 1: Fan chart
    _ax1 = _axes[0]
    _p5 = np.percentile(_all_paths, 5, axis=0)
    _p25 = np.percentile(_all_paths, 25, axis=0)
    _p50 = np.percentile(_all_paths, 50, axis=0)
    _p75 = np.percentile(_all_paths, 75, axis=0)
    _p95 = np.percentile(_all_paths, 95, axis=0)

    _ax1.fill_between(_year_labels, _p5, _p95, alpha=0.15, color="C0", label="5th-95th percentile")
    _ax1.fill_between(_year_labels, _p25, _p75, alpha=0.3, color="C0", label="25th-75th percentile")
    _ax1.plot(_year_labels, _p50, linewidth=2, color="C0", label="Median")
    _ax1.axhline(y=1.0, color="grey", linestyle="--", alpha=0.5)
    _ax1.set_xlabel("Year")
    _ax1.set_ylabel("Transformer Demand (2025 = 1.0)")
    _ax1.set_title("Total Transformer Demand: Fan Chart")
    _ax1.legend(fontsize=7)

    # Panel 2: By scenario
    _ax2 = _axes[1]
    _colors_s = ["C2", "C1", "C3"]
    _names = ["Sustained Boom", "Moderate Plateau", "Severe Contraction"]
    for _s in range(3):
        _mask = _scenario_labels == _s
        _scenario_paths = _all_paths[_mask]
        _med = np.median(_scenario_paths, axis=0)
        _lo = np.percentile(_scenario_paths, 10, axis=0)
        _hi = np.percentile(_scenario_paths, 90, axis=0)
        _ax2.fill_between(_year_labels, _lo, _hi, alpha=0.15, color=_colors_s[_s])
        _ax2.plot(_year_labels, _med, linewidth=2, color=_colors_s[_s], label=_names[_s])

    _ax2.axhline(y=1.0, color="grey", linestyle="--", alpha=0.5)
    _ax2.set_xlabel("Year")
    _ax2.set_ylabel("Transformer Demand (2025 = 1.0)")
    _ax2.set_title("Demand by Scenario")
    _ax2.legend(fontsize=8)

    _fig.suptitle(
        "Bubble Burst Analysis: Transformer Demand"
        f" ({_n} sims, bust = -{_bust_frac:.0%} AI CapEx)",
        fontsize=12, fontweight="bold", y=1.02,
    )
    plt.tight_layout()
    _fig
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 6. The Crowding-Out: Large Power Transformers vs Distribution Transformers

    The transformer supply chain exhibits a **resource competition feedback loop** between
    large power transformers (ordered by data centers and utilities) and distribution
    transformers (needed by rural cooperatives, minigrids, and developing-country utilities).

    **Shared resources under competition:**
    - **GOES** — grain-oriented electrical steel used in both LPT and DT cores
    - **Copper winding wire** — prices rose from ~$6,000 to >$10,000/ton (2020-2025)
    - **Skilled labor** — winding, core assembly, and testing technicians overlap
    - **Factory scheduling** — some facilities produce both types on shared lines

    **The asymmetry is stark:** A single hyperscale data center ($500M-$2B investment)
    orders more transformer capacity than an entire country's minigrid program. Minigrid
    developers ordering 10-50 small transformers worth $50-250K total are invisible to
    manufacturers compared to a data center operator ordering $5-50M in equipment.

    **Supply deficits (2025, Wood Mackenzie):**
    - Power transformers: **30%** shortfall
    - Distribution transformers: **10%** shortfall

    Despite the smaller percentage deficit, the distribution transformer shortage has
    outsized impact on energy access: **40+ million US units** are past service life,
    and Africa's Mission 300 program ($48B) depends on distribution-class equipment.
    """)
    return


@app.cell
def _(np, plt):
    """Visualize the crowding-out mechanism."""
    _fig, _axes = plt.subplots(1, 2, figsize=(12, 5))

    # Panel 1: Supply deficit comparison
    _ax1 = _axes[0]
    _categories = ["Power\nTransformers", "Distribution\nTransformers"]
    _deficit = [30, 10]
    _demand_growth = [116, 41]
    _x = np.arange(len(_categories))
    _w = 0.35
    _ax1.bar(_x - _w / 2, _deficit, _w, label="Supply Deficit (%)", color="C3")
    _ax1.bar(_x + _w / 2, _demand_growth, _w, label="Demand Growth (% since 2019)", color="C0")
    _ax1.set_ylabel("Percent (%)")
    _ax1.set_xticks(_x)
    _ax1.set_xticklabels(_categories)
    _ax1.legend(fontsize=8)
    _ax1.set_title("Supply Deficit vs Demand Growth")

    # Panel 2: Price comparison — who can afford the wait?
    _ax2 = _axes[1]
    _buyers = [
        "Hyperscale\nData Center",
        "US Utility\n(IOU)",
        "Rural\nCo-op",
        "Africa\nMinigrid",
    ]
    _order_size = [25000, 5000, 200, 50]  # $K typical transformer order
    _wait_tolerance = [3, 2.5, 1.5, 0.5]  # years they can afford to wait

    _colors = ["C3", "C1", "C0", "C2"]
    _scatter = _ax2.scatter(
        _order_size, _wait_tolerance,
        s=[max(200, v * 2) for v in _order_size],
        c=_colors, alpha=0.7, edgecolors="black", linewidths=0.5,
    )
    for _i, _buyer in enumerate(_buyers):
        _ax2.annotate(
            _buyer, xy=(_order_size[_i], _wait_tolerance[_i]),
            fontsize=8, ha="center",
            xytext=(0, 20 if _i != 3 else -25),
            textcoords="offset points",
        )
    _ax2.set_xscale("log")
    _ax2.set_xlabel("Typical Order Size ($K)")
    _ax2.set_ylabel("Wait Tolerance (years)")
    _ax2.set_title("Buyer Power vs Queue Position")
    _ax2.set_xlim(20, 50000)

    _fig.suptitle(
        "The Crowding-Out: Who Gets Transformers First?",
        fontsize=13, fontweight="bold", y=1.02,
    )
    plt.tight_layout()
    _fig
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 7. Historical Precedent: The Fiber Optic Glut (2000-2005)

    The closest historical analogy to the current AI infrastructure buildout is the
    **dot-com era fiber optic cable investment**:

    | Metric | Fiber Optic (1995-2005) | Transformers (2020-2030?) |
    |--------|------------------------|--------------------------|
    | Total investment | ~$2 trillion | ~$1.8B in manufacturing capacity |
    | Utilization at bust | **5%** (95% dark fiber) | Unlikely — multiple demand drivers |
    | Time to build | Weeks-months (cable) | **2-4 years** (factory + transformer) |
    | Number of producers | Hundreds | **<20** globally (LPT) |
    | Product standardization | High (commodity) | Low (highly customized) |
    | Post-bust outcome | 90% price collapse, fire-sale acquisition | Lead time normalization, 20-30% price correction |

    **Why a fiber-optic-style glut is unlikely for transformers:**

    1. **Multiple demand drivers:** AI is ~30% of demand. Grid aging, renewables, and
       electrification provide a structural floor that fiber optic had no equivalent for.
    2. **Long production cycles:** Transformer factories take 2-4 years to build, and
       each large unit takes months to manufacture. This naturally limits overcapacity.
    3. **Few producers:** Unlike fiber optic cable (hundreds of manufacturers), LPT
       production is concentrated in <20 firms globally. Oligopolistic coordination
       limits overbuilding.
    4. **Customization:** Each large transformer is essentially bespoke — matched to
       site-specific voltage, frequency, and climate. Surplus units aren't fungible.

    **What IS likely under a severe AI bust (2028-2030):**
    - Lead times normalize from 2-4 years → 6-12 months
    - Prices correct 20-30% from peak levels
    - Geographic rebalancing: developing countries gain access as they move up the queue
    - The NIAC's proposed "virtual strategic reserve" would buffer manufacturers against
      demand volatility
    """)
    return


@app.cell
def _(np, plt):
    """Compare fiber optic and transformer investment cycles."""
    _fig, _axes = plt.subplots(1, 2, figsize=(12, 5))

    # Panel 1: Fiber optic investment cycle (stylized)
    _ax1 = _axes[0]
    _fiber_years = np.arange(1995, 2008)
    _fiber_investment = np.array([20, 40, 80, 150, 300, 400, 100, 30, 15, 10, 12, 15, 20])
    _fiber_utilization = np.array([60, 55, 45, 30, 15, 5, 5, 6, 8, 10, 12, 14, 15])

    _ax1.bar(_fiber_years, _fiber_investment, alpha=0.6, color="C0", label="Investment ($B)")
    _ax1_twin = _ax1.twinx()
    _ax1_twin.plot(
        _fiber_years, _fiber_utilization,
        "o-", color="C3", linewidth=2, label="Utilization (%)",
    )
    _ax1.set_xlabel("Year")
    _ax1.set_ylabel("Investment ($B)", color="C0")
    _ax1_twin.set_ylabel("Fiber Utilization (%)", color="C3")
    _ax1.set_title("Fiber Optic: Classic Boom-Bust")
    _lines1, labels1 = _ax1.get_legend_handles_labels()
    _lines2, labels2 = _ax1_twin.get_legend_handles_labels()
    _ax1.legend(_lines1 + _lines2, labels1 + labels2, fontsize=7, loc="upper left")

    # Panel 2: Transformer investment cycle (projected)
    _ax2 = _axes[1]
    _tx_years = np.arange(2019, 2033)
    # Demand index (2019=1.0): AI + structural
    _tx_demand = np.array([
        1.0, 1.05, 1.15, 1.35, 1.55, 1.80, 2.00,  # 2019-2025 (observed)
        2.15, 2.25, 2.30, 2.25, 2.20, 2.25, 2.30,  # 2026-2032 (projected, moderate plateau)
    ])
    # Capacity index (2019=1.0): lagged expansion
    _tx_capacity = np.array([
        1.0, 1.02, 1.03, 1.05, 1.08, 1.12, 1.16,   # 2019-2025
        1.25, 1.40, 1.55, 1.70, 1.80, 1.85, 1.88,   # 2026-2032 (factories coming online)
    ])

    _ax2.plot(_tx_years, _tx_demand, "o-", color="C3", linewidth=2, label="Demand (indexed)")
    _ax2.plot(_tx_years, _tx_capacity, "s-", color="C2", linewidth=2, label="Capacity (indexed)")
    _ax2.fill_between(
        _tx_years, _tx_capacity, _tx_demand,
        where=_tx_demand > _tx_capacity, alpha=0.2, color="C3", label="Deficit",
    )
    _ax2.fill_between(
        _tx_years, _tx_capacity, _tx_demand,
        where=_tx_capacity > _tx_demand, alpha=0.2, color="C2", label="Surplus",
    )
    _ax2.axvline(x=2025, color="grey", linestyle=":", alpha=0.5)
    _ax2.annotate("Today", xy=(2025, 0.95), fontsize=8, color="grey")
    _ax2.set_xlabel("Year")
    _ax2.set_ylabel("Index (2019 = 1.0)")
    _ax2.set_title("Transformers: Delayed Catch-Up (Moderate Scenario)")
    _ax2.legend(fontsize=7)

    _fig.suptitle(
        "Historical Comparison: Fiber Optic Glut vs Transformer Supply",
        fontsize=13, fontweight="bold", y=1.02,
    )
    plt.tight_layout()
    _fig
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 8. Implications for Developing Countries

    The transformer supply chain crisis creates a **two-tier access problem:**

    | Tier | Buyers | Queue Position | Impact |
    |------|--------|----------------|--------|
    | **Tier 1** | Hyperscalers, large utilities, sovereign funds | Front of queue (premium pricing, multi-year contracts) | Secured supply |
    | **Tier 2** | Rural cooperatives, minigrids, developing-country utilities | Back of queue (price-sensitive, short procurement horizons) | 2-4 year delays, 100-200% cost increase |

    **Mission 300 tension:** The World Bank ($30B) and AfDB ($18B) committed to connect
    300 million people in Sub-Saharan Africa by 2030 — half via minigrids. But there is
    **no mechanism** to secure the 10-500 kVA distribution transformers these minigrids
    need in a market where data center operators are outbidding everyone.

    **Policy gap:** US Defense Production Act, Buy American requirements, and IRA incentives
    are all domestically focused. They may actually **worsen** developing-country access by
    redirecting manufacturing capacity toward US domestic orders.

    **The silver lining of a bust:** A moderate AI CapEx contraction (the "plateau" scenario)
    would normalize lead times and prices, creating a window for developing-country procurement.
    The fiber optic precedent shows that post-bust surplus can dramatically benefit previously
    excluded buyers — universities acquired dark fiber at fire-sale prices after 2001.

    ---

    ## Key Findings

    1. **The transformer shortage is real but multi-causal.** AI data centers are ~30% of demand;
       grid aging, renewables, and electrification provide a structural floor of ~70%.

    2. **Manufacturing capacity is responding, but slowly.** ~$1.8B+ in North American
       investments announced since 2023, but factories take 2-4 years to build. The
       capacity-demand gap won't close before 2028-2029.

    3. **A fiber-optic-style glut is unlikely.** Too few producers, too much customization,
       too many non-AI demand drivers. But a **price correction of 20-30%** and **lead time
       normalization** are plausible under a moderate AI plateau scenario.

    4. **Distribution transformers for minigrids are the most vulnerable.** Shared resources
       (GOES, copper, labor) and radically asymmetric buyer power mean that minigrid
       developers are structurally disadvantaged in the current market.

    5. **Policy is misaligned.** Mission 300's $48B commitment has no corresponding
       supply chain strategy for minigrid-scale transformers. This is a modeling opportunity
       for the SD framework — what policy interventions (strategic reserves, targeted
       procurement, GOES allocation) could protect developing-country access?
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ---
    *Notebook: Energy Infrastructure Supply Chain — Transformer Dynamics*
    *Part of the Systems Dynamics Research Project*
    *Data: Wood Mackenzie, IEA, NIAC/CISA, manufacturer filings*
    """)
    return


if __name__ == "__main__":
    app.run()
