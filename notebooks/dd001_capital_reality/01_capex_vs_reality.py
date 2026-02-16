import marimo

__generated_with = "0.19.11"
app = marimo.App(width="medium", app_title="AI Capital vs. Physical Reality")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # AI Valuations vs. Physical Infrastructure Reality
    ## Where Does the Capital Actually Land?

    *Thandolwethu Zwelakhe Dlamini*

    ---

    AI company valuations have added ~\$10 trillion in market cap since January 2023.
    Hyperscaler capital expenditure is approaching $300B+ per year. But how much of
    that capital is actually converting to physical infrastructure — and what does the
    grid get from the portion that does?

    This notebook traces the **three-layer disconnect** between AI financial narratives
    and physical outcomes:

    1. **Valuations vs. Capex** — \$10T in market cap gains vs. ~$300B in annual spending
    2. **Capex vs. Revenue** — The "$600B question" (Sequoia, 2024)
    3. **Announcements vs. Physical Reality** — 75-80% of queued projects never reach operation

    The key insight: physical construction is ~30-40% of capex but creates the most
    durable assets. Equipment is ~50-60% but depreciates in 3-6 years. **The grid gets
    lasting infrastructure even if the AI demand thesis falters.**
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
        BAR_DEFAULTS,
        CATEGORICAL,
        COLORS,
        COMPANY_COLORS,
        COMPANY_LABELS,
        FIGSIZE,
        FONTS,
        annotate_point,
        company_color,
        company_label,
        legend_below,
        reference_line,
    )

    cfg = setup()
    return (
        BAR_DEFAULTS,
        CATEGORICAL,
        COLORS,
        COMPANY_COLORS,
        COMPANY_LABELS,
        FIGSIZE,
        FONTS,
        annotate_point,
        cfg,
        company_color,
        company_label,
        legend_below,
        mo,
        np,
        pd,
        plt,
        query,
        reference_line,
        save_fig,
    )


@app.cell
def _(pd, query):
    # Live capex data from DuckDB (yfinance + historical CSV)
    capex_raw = query("""
        SELECT ticker, date, capex_bn
        FROM energy_data.hyperscaler_capex
        ORDER BY date, ticker
    """)
    capex_raw["date"] = pd.to_datetime(capex_raw["date"])
    capex_raw["year"] = capex_raw["date"].dt.year

    # Annual capex by company
    capex_annual = (
        capex_raw.groupby(["ticker", "year"])["capex_bn"]
        .sum()
        .reset_index()
        .sort_values(["ticker", "year"])
    )

    # 2025 guidance from DuckDB (loaded from data/external/ CSV)
    guidance_2025 = query("""
        SELECT ticker, year, capex_bn, source
        FROM energy_data.capex_guidance
    """)

    # Market cap reference data from DuckDB (loaded from data/external/ CSV)
    _mkt = query("""
        SELECT ticker, company, date, market_cap_t
        FROM energy_data.mag7_market_caps
        ORDER BY ticker, date
    """)
    # Pivot to wide format for the chart
    _early = _mkt[_mkt["date"] == "2023-01-03"].set_index("ticker")
    _late = _mkt[_mkt["date"] == "2025-01-02"].set_index("ticker")
    mkt_cap = _early[["company"]].copy()
    mkt_cap["mkt_cap_2023_t"] = _early["market_cap_t"]
    mkt_cap["mkt_cap_2025_t"] = _late["market_cap_t"]
    mkt_cap["gain_t"] = mkt_cap["mkt_cap_2025_t"] - mkt_cap["mkt_cap_2023_t"]
    mkt_cap = mkt_cap.reset_index()
    return capex_annual, capex_raw, guidance_2025, mkt_cap


@app.cell
def _(
    BAR_DEFAULTS,
    COLORS,
    COMPANY_COLORS,
    COMPANY_LABELS,
    FIGSIZE,
    FONTS,
    capex_annual,
    cfg,
    company_color,
    company_label,
    guidance_2025,
    legend_below,
    np,
    pd,
    plt,
    save_fig,
):
    # Combine actuals with 2025 guidance
    _tickers = ["MSFT", "AMZN", "GOOGL", "META", "ORCL", "NVDA"]

    # Aggregate actuals by year for 2021-2024
    _years = [2021, 2022, 2023, 2024]
    _data = capex_annual[
        (capex_annual["ticker"].isin(_tickers)) & (capex_annual["year"].isin(_years))
    ].copy()

    # Add 2025 guidance
    _guide = guidance_2025[guidance_2025["ticker"].isin(_tickers)].copy()
    _combined = pd.concat(
        [_data[["ticker", "year", "capex_bn"]], _guide[["ticker", "year", "capex_bn"]]],
        ignore_index=True,
    )

    fig_capex, _ax = plt.subplots(figsize=FIGSIZE["wide"])
    _all_years = sorted(_combined["year"].unique())
    _bar_width = 0.12
    _x = np.arange(len(_all_years))

    for _i, _ticker in enumerate(_tickers):
        _sub = _combined[_combined["ticker"] == _ticker]
        _vals = []
        for y in _all_years:
            _match = _sub[_sub["year"] == y]
            _vals.append(_match["capex_bn"].sum() if len(_match) else 0)

        _offset = (_i - len(_tickers) / 2 + 0.5) * _bar_width
        _bars = _ax.bar(
            _x + _offset,
            _vals,
            _bar_width,
            label=company_label(_ticker),
            color=company_color(_ticker),
            **BAR_DEFAULTS,
        )

        # Mark 2025 guidance bar with hatching
        if 2025 in _all_years:
            _idx_2025 = _all_years.index(2025)
            _bars[_idx_2025].set_hatch("//")
            _bars[_idx_2025].set_alpha(0.5)

    _ax.set_xticks(_x)
    _ax.set_xticklabels([str(y) for y in _all_years], fontsize=FONTS["tick_label"])
    _ax.set_ylabel("Capital expenditure ($B)", fontsize=FONTS["axis_label"])
    _ax.tick_params(axis="y", labelsize=FONTS["tick_label"])

    # Annotate total for each year
    for j, y in enumerate(_all_years):
        _total = _combined[_combined["year"] == y]["capex_bn"].sum()
        _suffix = "*" if y == 2025 else ""
        _ax.text(
            j,
            _total / len(_tickers) + max(_combined.groupby("year")["capex_bn"].max()) * 0.05,
            f"${_total:.0f}B{_suffix}",
            ha="center",
            fontsize=FONTS["small"],
            fontweight="bold",
            color=COLORS["text_dark"],
        )

    legend_below(_ax, ncol=6)
    plt.tight_layout()
    save_fig(fig_capex, cfg.img_dir / "dd001_capex_acceleration.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo):
    _chart = mo.image(
        src=(cfg.img_dir / "dd001_capex_acceleration.png").read_bytes(), width=850
    )
    mo.md(f"""
    # Hyperscaler capex has more than doubled in two years

    {_chart}

    *2025 figures are management guidance (hatched bars), not audited actuals.
    Total Big 5+Nvidia capex: ~$147B (2023) to ~$345B (2025 guidance). Sources:
    SEC 10-K/10-Q filings, earnings call transcripts.*
    """)
    return


@app.cell
def _(
    BAR_DEFAULTS,
    COLORS,
    FIGSIZE,
    FONTS,
    cfg,
    company_color,
    mkt_cap,
    np,
    plt,
    reference_line,
    save_fig,
):
    fig_mktcap, _ax = plt.subplots(figsize=FIGSIZE["wide"])

    _sorted = mkt_cap.sort_values("gain_t", ascending=True)
    _y = np.arange(len(_sorted))
    _colors_gain = [company_color(t) for t in _sorted["ticker"]]

    _ax.barh(
        _y,
        _sorted["gain_t"],
        height=0.55,
        color=_colors_gain,
        alpha=BAR_DEFAULTS["alpha"],
        edgecolor=BAR_DEFAULTS["edgecolor"],
    )

    for _i, (_, _row) in enumerate(_sorted.iterrows()):
        _ax.text(
            _row["gain_t"] + 0.08,
            _i,
            f"+${_row['gain_t']:.1f}T",
            va="center",
            fontsize=FONTS["value_label"],
            fontweight="bold",
        )

    _ax.set_yticks(_y)
    _ax.set_yticklabels(_sorted["company"], fontsize=FONTS["tick_label"])
    _ax.set_xlabel(
        "Market cap gain, Jan 2023 \u2192 Jan 2025 ($T)", fontsize=FONTS["axis_label"]
    )
    _ax.tick_params(axis="x", labelsize=FONTS["tick_label"])

    # Reference line: total 2024 capex
    reference_line(_ax, 0.30, orientation="v", label="Total 2024\ncapex: $230B")

    plt.tight_layout()
    save_fig(fig_mktcap, cfg.img_dir / "dd001_valuation_disconnect.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo):
    _chart = mo.image(
        src=(cfg.img_dir / "dd001_valuation_disconnect.png").read_bytes(), width=850
    )
    mo.md(rf"""
    # Markets added ~\$10T in value against ~$230B in annual spending

    {_chart}

    *The six largest AI-associated companies gained ~$9.5T in market capitalization
    in two years. Their combined annual capex is ~$230B (2024). Markets are pricing
    AI returns at roughly 30x the infrastructure investment. The red dashed line
    shows total 2024 capex for scale.*

    This is Layer 1 of the disconnect: the financial narrative runs far ahead
    of the physical capital being deployed.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## Layer 2: The "$600B Question"

    Sequoia Capital's David Cahn estimated (September 2024) that the AI industry
    needs ~\$600B in annual revenue to justify the infrastructure buildout. Actual
    AI revenue — excluding Nvidia hardware sales — was roughly \$100B, leaving a
    **$500B hole**.

    Other estimates are harsher:

    | Analyst | Capex-to-Revenue Ratio | Normal Infrastructure Ratio |
    | :--- | :--- | :--- |
    | Bernstein (Sacconaghi) | 7-10x | 1-2x |
    | Goldman Sachs (Covello) | "Too expensive" | — |
    | Elliott Management | "Overhyped" | — |

    **Counterargument:** AI revenue is growing fast. Microsoft's AI run rate
    exceeded $10B/quarter by late 2024. Google Cloud grew 35% YoY. But a meaningful
    portion is hyperscalers selling AI services to each other or to VC-funded
    startups — circular spending that inflates the top line without proving
    end-user demand.

    The revenue gap matters for this research because it determines **durability**.
    If AI revenue catches up, the infrastructure is justified. If it doesn't,
    the physical assets persist anyway — but the economics shift from
    "demand-thesis-dependent" to "stranded or repurposed."
    """)
    return


@app.cell
def _(BAR_DEFAULTS, COLORS, FIGSIZE, FONTS, cfg, np, plt, save_fig):
    _categories = [
        "Physical construction\n(buildings, power infra)",
        "Equipment\n(servers, GPUs, networking)",
        "Other\n(land, permits, services)",
    ]
    _shares = [35, 55, 10]  # Midpoint estimates from industry data
    _asset_life = ["20-40 years", "3-6 years", "Varies"]
    _colors = [COLORS["positive"], COLORS["negative"], COLORS["neutral"]]

    _ratios = {"width_ratios": [1.2, 1]}
    fig_decomp, (_ax1, _ax2) = plt.subplots(
        1, 2, figsize=FIGSIZE["double"], gridspec_kw=_ratios
    )

    # Left: Capex decomposition pie
    _wedges, _texts, _autotexts = _ax1.pie(
        _shares,
        labels=None,
        autopct="%1.0f%%",
        colors=_colors,
        startangle=90,
        pctdistance=0.6,
        textprops={"fontsize": FONTS["value_label"], "fontweight": "bold"},
    )
    for t in _autotexts:
        t.set_color("white")

    _ax1.legend(
        _wedges,
        _categories,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.15),
        ncol=1,
        fontsize=FONTS["small"],
        frameon=False,
    )

    # Right: Asset lifetime comparison
    _durations = [30, 4.5, 5]  # Midpoint lifetimes
    _y = np.arange(3)
    _ax2.barh(
        _y,
        _durations,
        height=0.5,
        color=_colors,
        alpha=BAR_DEFAULTS["alpha"],
        edgecolor=BAR_DEFAULTS["edgecolor"],
    )
    for _i, (_dur, _life_label) in enumerate(zip(_durations, _asset_life)):
        _ax2.text(
            _dur + 0.5,
            _i,
            _life_label,
            va="center",
            fontsize=FONTS["value_label"],
            fontweight="bold",
        )

    _ax2.set_yticks(_y)
    _ax2.set_yticklabels(
        ["Construction", "Equipment", "Other"],
        fontsize=FONTS["tick_label"],
    )
    _ax2.set_xlabel("Typical asset life (years)", fontsize=FONTS["axis_label"])
    _ax2.set_xlim(0, 45)

    plt.tight_layout()
    save_fig(fig_decomp, cfg.img_dir / "dd001_capex_decomposition.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo):
    _chart = mo.image(
        src=(cfg.img_dir / "dd001_capex_decomposition.png").read_bytes(), width=850
    )
    mo.md(rf"""
    # 35% of capex creates 20-40 year assets — the rest depreciates in under 6

    {_chart}

    *Of ~\$300B+ in annual hyperscaler capex, roughly \$100-120B goes to physical
    construction (buildings, substations, power interconnections). These are 20-40
    year assets that persist regardless of whether the AI demand thesis holds.
    The remaining ~\$170B in equipment depreciates in 3-6 years — it's a recurring
    cost, not a durable commitment.*

    This asymmetry is the crux of the infrastructure lock-in problem. The financial
    risk (will AI generate returns?) is a 3-5 year question. The infrastructure
    consequence (what did we build?) is a 30-50 year answer.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ---

    ## Layer 3: Announcements vs. Physical Reality

    The gap between what's announced and what gets built is enormous:

    - **Stargate Project:** $500B announced (Jan 2025). $100B initially committed.
      SoftBank's balance sheet had ~$30-40B deployable capital. Financial structure
      remains opaque.
    - **PJM Interconnection Queue:** ~90 GW of data center requests. Historical
      attrition rate: **75-80% of queued projects never reach commercial operation.**
    - **ERCOT Large Load Requests:** ~60 GW pending (includes data centers and crypto).
    - **Industry-wide:** Only 20-30% of announced data center projects proceed to
      construction within the initially announced timeline.

    The binding constraint is **power availability**. Average time from interconnection
    request to energized service has stretched to 3-5 years in some regions (up from
    1-2 years). This is a physical bottleneck that no amount of capital can instantly
    resolve — it requires substations, transmission lines, and generation capacity
    that take years to permit and build.

    As of early 2025: no major hyperscaler project cancellations reported. The pattern
    is delays and site relocation, not outright cancellation. The capital is real,
    but the conversion rate from announcement to operating infrastructure is far
    lower than headlines suggest.
    """)
    return


@app.cell
def _(
    BAR_DEFAULTS,
    CATEGORICAL,
    COLORS,
    FIGSIZE,
    FONTS,
    annotate_point,
    cfg,
    np,
    plt,
    save_fig,
):
    _categories = [
        "Intellectual\nproperty",
        "Equipment",
        "Structures",
        "Hyperscaler\ncapex",
    ]
    _values = [1400, 1400, 750, 300]  # $B, approximate 2024
    _colors = CATEGORICAL[:4]

    fig_share, _ax = plt.subplots(figsize=FIGSIZE["single"])
    _x = np.arange(len(_categories))

    _bars = _ax.bar(
        _x,
        _values,
        color=_colors,
        width=0.6,
        **BAR_DEFAULTS,
    )

    for bar, val in zip(_bars, _values):
        _ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 30,
            f"${val:,}B",
            ha="center",
            fontsize=FONTS["value_label"],
            fontweight="bold",
        )

    # Annotate the hyperscaler share
    _total = 3500  # Total US private nonresidential fixed investment
    _pct = 300 / _total * 100
    annotate_point(
        _ax,
        f"{_pct:.0f}% of total\nUS private\ninvestment",
        xy=(3, 300),
        xytext=(2.2, 1100),
        color=COLORS["accent"],
    )

    _ax.set_xticks(_x)
    _ax.set_xticklabels(_categories, fontsize=FONTS["tick_label"])
    _ax.set_ylabel("Annual investment ($B)", fontsize=FONTS["axis_label"])
    _ax.tick_params(axis="y", labelsize=FONTS["tick_label"])

    plt.tight_layout()
    save_fig(fig_share, cfg.img_dir / "dd001_capex_us_share.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo):
    _chart = mo.image(
        src=(cfg.img_dir / "dd001_capex_us_share.png").read_bytes(), width=850
    )
    mo.md(f"""
    # Hyperscaler capex is ~9% of all US private nonresidential investment

    {_chart}

    *Total US private nonresidential fixed investment is ~$3.5T annually (BEA, 2024).
    Hyperscaler capex (~$300B) represents a significant and rapidly growing share —
    concentrated in a handful of companies making infrastructure decisions that
    normally take decades of utility planning.*

    For context: total US data center construction spending is estimated at $30-50B
    annually (JLL, CBRE). The Census Bureau's C30 construction series does not
    separately report data centers — they are buried in "commercial/warehouse"
    categories. This is one of several critical data gaps.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ---

    ## The DeepSeek Test

    DeepSeek's R1 model (January 2025) demonstrated competitive AI performance at
    reportedly much lower training costs. Nvidia lost ~$600B in market cap in a
    single day. It was the first real test of whether efficiency gains would reduce
    infrastructure demand.

    **They didn't.** In subsequent earnings calls:

    | Company | Response |
    | :--- | :--- |
    | Microsoft | Maintained $80B+ guidance |
    | Meta | *Increased* guidance to $60-65B |
    | Alphabet | Announced $75B (above consensus) |
    | Amazon | Maintained $100B+ trajectory |

    Management teams invoked the **Jevons paradox**: cheaper AI inference increases
    adoption and ultimately increases total compute demand. Historical precedent
    (LED lighting, Moore's Law, cloud computing) supports this — but it is not
    guaranteed to apply.

    For infrastructure analysis, the DeepSeek episode reinforced a key finding:
    **hyperscaler capex is stickier than valuations.** Stock prices fluctuate on
    sentiment; capital expenditure programs, once committed, roll forward on
    multi-year procurement contracts, construction timelines, and competitive
    dynamics (the prisoner's dilemma — no one can be the first to stop spending).
    """)
    return


@app.cell
def _(
    COLORS,
    FIGSIZE,
    FONTS,
    capex_raw,
    cfg,
    company_color,
    company_label,
    legend_below,
    pd,
    plt,
    save_fig,
):
    _tickers = ["MSFT", "AMZN", "GOOGL", "META"]

    fig_quarterly, _ax = plt.subplots(figsize=FIGSIZE["wide"])

    for _ticker in _tickers:
        _sub = capex_raw[capex_raw["ticker"] == _ticker].sort_values("date")
        if len(_sub) < 2:
            continue
        _ax.plot(
            _sub["date"],
            _sub["capex_bn"],
            marker="o",
            markersize=5,
            label=company_label(_ticker),
            color=company_color(_ticker),
            linewidth=2.5,
        )

    _ax.set_ylabel("Quarterly capex ($B)", fontsize=FONTS["axis_label"])
    _ax.tick_params(axis="both", labelsize=FONTS["tick_label"])
    _ax.grid(True, axis="y", linestyle=":", alpha=0.4)

    # Annotate DeepSeek moment
    _deepseek_date = pd.Timestamp("2025-01-27")
    _ymax = capex_raw[capex_raw["ticker"].isin(_tickers)]["capex_bn"].max()
    _ax.axvline(
        _deepseek_date, color=COLORS["text_dark"], linestyle="--", linewidth=1.5, alpha=0.5
    )
    _ax.text(
        _deepseek_date,
        _ymax * 0.95,
        " DeepSeek R1",
        fontsize=FONTS["small"],
        color=COLORS["text_light"],
        fontweight="bold",
        va="top",
    )

    legend_below(_ax, ncol=4)
    plt.tight_layout()
    save_fig(fig_quarterly, cfg.img_dir / "dd001_quarterly_capex.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo):
    _chart = mo.image(
        src=(cfg.img_dir / "dd001_quarterly_capex.png").read_bytes(), width=850
    )
    mo.md(f"""
    # Quarterly capex ramps show no sign of slowing

    {_chart}

    *Quarterly capital expenditure for the four largest AI infrastructure spenders.
    The dashed line marks DeepSeek R1's release (January 2025). Despite the efficiency
    shock, no company reduced capex guidance. Data: yfinance (SEC filings).*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ---

    ## What Persists: The Durability Taxonomy

    Applying the project's analytical framework, AI infrastructure investments
    fall into three durability categories:

    | Category | What Gets Built | Life | Persists? |
    | :--- | :--- | :--- | :--- |
    | **Structural** | Grid upgrades, substations, DC shells | 20-50 yrs | Yes |
    | **Policy-dependent** | Nuclear restarts, SMR, rate structures | Varies | If regime holds |
    | **Demand-thesis-dependent** | GPU clusters, AI cooling, inference HW | 3-6 yrs | No |

    The interesting cases are investments that **start as demand-thesis-dependent
    but create structural demand through second-order effects.** A gas plant built
    to power a data center campus is demand-thesis-dependent at inception. Once
    built, it operates for 40 years regardless of whether the data center scales
    as planned. The capital decision was AI-driven; the infrastructure consequence
    is not.

    ### The historical parallel

    The dot-com fiber overbuild (1998-2001) was called a bubble — and it was. But
    the fiber stayed in the ground. Within a decade, traffic growth consumed the
    excess capacity and then some. The physical infrastructure outlasted the
    financial thesis that built it.

    The question for AI infrastructure is whether the same pattern holds: **does
    the grid modernization funded by AI capex retain value even if AI revenue
    never reaches $600B?** The durability taxonomy says yes for the physical
    construction layer (~35% of capex) and no for the equipment layer (~55%).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ---

    ## Where This Research Goes Next

    This notebook establishes the premise: AI capital is real and accelerating,
    but the conversion from financial commitment to physical infrastructure is
    lossy and slow. The three-layer disconnect — valuations, revenue, physical
    reality — means we cannot take announcements at face value.

    The remaining deep dives trace what happens when capital *does* convert:

    - **DD-002: Grid Modernization** — What generation mix is getting built?
      Which fuel types? Where geographically? What does EIA Form 860 show
      about the capacity pipeline?
    - **DD-003: Labor Markets** — Who gets hired and displaced? What are the
      temporal dynamics of build-phase construction employment vs. long-term
      operations staffing vs. knowledge-work displacement?
    - **CS-3: Grid Interconnection** — The interconnection queue as binding
      constraint. LBNL data on queue attrition, wait times, and regional
      bottlenecks.
    - **CS-4: Material Supply Chains** — GOES steel, copper, transformers.
      Where does concentration risk bind?

    ### Key data gaps to resolve

    1. No government statistical series tracks data center construction separately
    2. No clean separation of "AI capex" vs. "general cloud capex" in public filings
    3. Interconnection queue attrition rates are estimated, not precisely tracked
    4. Stargate and similar mega-projects have opaque financial structures
    5. AI-specific electricity consumption at facility level is not systematically reported

    ---

    *Sources: SEC EDGAR (10-K/10-Q filings), Sequoia Capital, BEA NIPA tables,
    EIA, EPRI, LBNL. See `research/ai_valuation_vs_infrastructure_reality.md`
    for full source list and methodology notes.*
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
