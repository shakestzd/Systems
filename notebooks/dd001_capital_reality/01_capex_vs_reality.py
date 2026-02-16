import marimo

__generated_with = "0.19.11"
app = marimo.App(width="medium", app_title="AI Capital vs. Physical Reality")


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    # AI Valuations vs. Physical Infrastructure Reality
    ## Where Does the Capital Actually Land?

    *Thandolwethu Zwelakhe Dlamini*

    ---

    AI company valuations have added ~\\${stats['mkt_gain_t']:.1f} trillion in
    market cap since January 2023. Hyperscaler capital expenditure reached
    ~\\${stats['capex_2025']:.0f}B in 2025 (up from ~\\${stats['capex_2024']:.0f}B in 2024),
    with ~\\${stats['guidance_2026']:.0f}B guided for 2026. But how much of that capital
    is actually converting to physical infrastructure — and what does the grid get
    from the portion that does?

    This notebook traces the **three-layer disconnect** between AI financial narratives
    and physical outcomes:

    1. **Valuations vs. Capex** — ~\\${stats['mkt_gain_t']:.1f}T in market cap gains (7 companies) vs. ~\\${stats['capex_2025']:.0f}B in annual spending (6 hyperscalers)
    2. **Capex vs. Revenue** — Cloud revenue growing fast (~\\${stats['cloud_rev_q4_annual']:.0f}B annualized) but capex-to-revenue ratios remain far above historical norms
    3. **Announcements vs. Physical Reality** — most queued projects never reach operation (LBNL, 2024)

    The key insight: ~40% of capex funds physical construction that creates the most
    durable assets (per FY2024 10-K data). Equipment (~50%) depreciates in 3-6 years.
    **The grid gets lasting infrastructure even if the AI demand thesis falters.**
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
        COLORS,
        CONTEXT,
        FIGSIZE,
        FONTS,
        chart_title,
        company_color,
        company_label,
        legend_below,
    )

    cfg = setup()
    return (
        COLORS,
        CONTEXT,
        FIGSIZE,
        FONTS,
        cfg,
        chart_title,
        company_color,
        company_label,
        legend_below,
        mo,
        np,
        pd,
        plt,
        query,
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

    # 2026 guidance from DuckDB (loaded from data/external/ CSV)
    guidance_2026 = query("""
        SELECT ticker, year, capex_bn, source
        FROM energy_data.capex_guidance
    """)

    # Market cap reference data (3 snapshots: Jan 2023, Jan 2025, Feb 2026)
    _mkt = query("""
        SELECT ticker, company, date, market_cap_t
        FROM energy_data.mag7_market_caps
        ORDER BY ticker, date
    """)
    _early = _mkt[_mkt["date"] == "2023-01-03"].set_index("ticker")
    _late = _mkt[_mkt["date"] == "2026-02-14"].set_index("ticker")
    mkt_cap = _early[["company"]].copy()
    mkt_cap["mkt_cap_2023_t"] = _early["market_cap_t"]
    mkt_cap["mkt_cap_2026_t"] = _late["market_cap_t"]
    mkt_cap["gain_t"] = mkt_cap["mkt_cap_2026_t"] - mkt_cap["mkt_cap_2023_t"]
    mkt_cap = mkt_cap.reset_index()

    # Cloud revenue (quarterly) for Layer 2 analysis
    cloud_rev = query("""
        SELECT ticker, segment, quarter, revenue_bn, yoy_growth_pct
        FROM energy_data.cloud_revenue
        ORDER BY quarter, ticker
    """)

    # BEA Private Nonresidential Fixed Investment (FRED, latest quarterly SAAR)
    _pnfi = query("""
        SELECT value FROM energy_data.fred_series
        WHERE series_id = 'PNFI'
        ORDER BY date DESC LIMIT 1
    """)
    pnfi_bn = float(_pnfi["value"].iloc[0])

    return capex_annual, capex_raw, cloud_rev, guidance_2026, mkt_cap, pnfi_bn


@app.cell
def _(capex_annual, cloud_rev, guidance_2026, mkt_cap, pnfi_bn):
    # Compute key summary stats — used by all markdown captions to avoid hardcoded numbers.
    _tickers_6 = ["MSFT", "AMZN", "GOOGL", "META", "ORCL", "NVDA"]
    _annual = capex_annual[capex_annual["ticker"].isin(_tickers_6)]
    _cloud_q4 = cloud_rev[cloud_rev["quarter"] == "2025-Q4"]
    _cloud_2024 = cloud_rev[cloud_rev["quarter"].str.startswith("2024")]
    _cloud_2025 = cloud_rev[cloud_rev["quarter"].str.startswith("2025")]
    stats = {
        "capex_2022": _annual[_annual["year"] == 2022]["capex_bn"].sum(),
        "capex_2023": _annual[_annual["year"] == 2023]["capex_bn"].sum(),
        "capex_2024": _annual[_annual["year"] == 2024]["capex_bn"].sum(),
        "capex_2025": _annual[_annual["year"] == 2025]["capex_bn"].sum(),
        "guidance_2026": guidance_2026[
            guidance_2026["ticker"].isin(_tickers_6)
        ]["capex_bn"].sum(),
        "mkt_gain_t": mkt_cap["gain_t"].sum(),
        # BEA PNFI from FRED (quarterly SAAR, $B)
        "pnfi_bn": pnfi_bn,
        # Cloud revenue (Layer 2)
        "cloud_rev_q4": _cloud_q4["revenue_bn"].sum(),
        "cloud_rev_q4_annual": _cloud_q4["revenue_bn"].sum() * 4,
        "cloud_rev_2024": _cloud_2024.groupby("ticker")["revenue_bn"].sum().sum(),
        "cloud_rev_2025": _cloud_2025.groupby("ticker")["revenue_bn"].sum().sum(),
    }
    stats["ratio_vs_2025"] = stats["mkt_gain_t"] / (stats["capex_2025"] / 1000)
    stats["pnfi_share_pct"] = stats["capex_2025"] / stats["pnfi_bn"] * 100
    # Per-company annual totals (for DeepSeek table and inline citations)
    for _t in ["AMZN", "GOOGL", "MSFT", "META"]:
        for _y in [2024, 2025]:
            stats[f"{_t.lower()}_{_y}"] = _annual[
                (_annual["ticker"] == _t) & (_annual["year"] == _y)
            ]["capex_bn"].sum()
    # Per-company guidance
    for _, _row in guidance_2026[
        guidance_2026["ticker"].isin(["AMZN", "GOOGL", "MSFT", "META"])
    ].iterrows():
        stats[f"{_row['ticker'].lower()}_2026g"] = _row["capex_bn"]
    # Backward compat aliases
    stats["meta_2022"] = _annual[
        (_annual["ticker"] == "META") & (_annual["year"] == 2022)
    ]["capex_bn"].sum()
    stats["meta_2023"] = _annual[
        (_annual["ticker"] == "META") & (_annual["year"] == 2023)
    ]["capex_bn"].sum()
    return (stats,)


@app.cell
def _(
    COLORS,
    CONTEXT,
    FIGSIZE,
    FONTS,
    capex_annual,
    cfg,
    chart_title,
    company_label,
    guidance_2026,
    legend_below,
    np,
    pd,
    plt,
    save_fig,
):
    # Combine actuals (2022-2025) with 2026 guidance
    _tickers = ["MSFT", "AMZN", "GOOGL", "META", "ORCL", "NVDA"]

    _years = [2022, 2023, 2024, 2025]
    _data = capex_annual[
        (capex_annual["ticker"].isin(_tickers)) & (capex_annual["year"].isin(_years))
    ].copy()

    # Add 2026 guidance
    _guide = guidance_2026[guidance_2026["ticker"].isin(_tickers)].copy()
    _combined = pd.concat(
        [_data[["ticker", "year", "capex_bn"]], _guide[["ticker", "year", "capex_bn"]]],
        ignore_index=True,
    )

    # SWD: companies on x-axis, years stacked — shows WHO is driving the acceleration.
    # Graduated grays for actuals, accent for 2026 guidance.
    fig_capex, _ax = plt.subplots(figsize=FIGSIZE["wide"])
    _all_years = sorted(_combined["year"].unique())
    _x = np.arange(len(_tickers))

    # Year colors: graduated grays for actuals, accent for guidance
    _year_colors = {
        2022: "#e0e0e0",
        2023: "#c0c0c0",
        2024: "#999999",
        2025: "#555555",
        2026: COLORS["accent"],
    }

    # Build stacked data: each year is a layer (bottom=oldest)
    _bottoms = np.zeros(len(_tickers))
    for _yr in _all_years:
        _vals = []
        for _ticker in _tickers:
            _match = _combined[
                (_combined["ticker"] == _ticker) & (_combined["year"] == _yr)
            ]
            _vals.append(_match["capex_bn"].sum() if len(_match) else 0)
        _vals = np.array(_vals)
        _bars = _ax.bar(
            _x, _vals, bottom=_bottoms, width=0.55,
            color=_year_colors[_yr], edgecolor="white", linewidth=0.5,
            label=str(_yr) + ("*" if _yr == 2026 else ""),
        )
        # Hatch the 2026 guidance bars
        if _yr == 2026:
            for _b in _bars:
                _b.set_hatch("//")
                _b.set_alpha(0.85)
        _bottoms += _vals

    _ax.set_xticks(_x)
    _ax.set_xticklabels(
        [company_label(t) for t in _tickers], fontsize=FONTS["tick_label"],
    )
    _ax.set_ylabel("Annual capital expenditure ($B)", fontsize=FONTS["axis_label"])
    _ax.tick_params(axis="y", labelsize=FONTS["tick_label"])

    # Total per company above each bar — the hero element
    for _j, _ticker in enumerate(_tickers):
        _ax.text(
            _j, _bottoms[_j] + 8, f"${_bottoms[_j]:.0f}B",
            ha="center", fontsize=FONTS["annotation"], fontweight="bold",
            color=COLORS["accent"],
        )

    legend_below(_ax, ncol=len(_all_years))
    chart_title(fig_capex, "Hyperscaler capex tripled in three years — and 2026 guidance doubles again")
    plt.tight_layout()
    save_fig(fig_capex, cfg.img_dir / "dd001_capex_acceleration.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo, stats):
    _chart = mo.image(
        src=(cfg.img_dir / "dd001_capex_acceleration.png").read_bytes(), width=850
    )
    mo.md(f"""
    # Hyperscaler capex tripled in three years — and 2026 guidance doubles again

    {_chart}

    *2026 figures are management guidance (hatched bars), not audited actuals.
    Combined capex for these six companies: ~\\${stats['capex_2023']:.0f}B (2023) →
    ~\\${stats['capex_2024']:.0f}B (2024) → ~\\${stats['capex_2025']:.0f}B (2025) →
    ~\\${stats['guidance_2026']:.0f}B (2026 guidance). Capex aggregated by calendar year;
    note that Microsoft (June FY) and Oracle (May FY) report on non-calendar fiscal
    years. Capex figures include all capital expenditure, not only AI-related spending
    (e.g., Amazon includes logistics infrastructure). ~75% of 2026 capex is expected to
    fund AI infrastructure directly (CreditSights, Feb 2026). Additionally, these figures
    exclude leased capacity — significant data center capacity is leased from colocation
    providers (Equinix, Digital Realty) and does not appear in the lessee's capex line.
    Total AI infrastructure investment is higher than what corporate capex alone shows.
    Sources: SEC 10-K/10-Q filings via yfinance, earnings call transcripts (Jan-Feb 2026).*
    """)
    return


@app.cell
def _(
    COLORS,
    FIGSIZE,
    FONTS,
    cfg,
    chart_title,
    company_color,
    company_label,
    legend_below,
    mkt_cap,
    plt,
    save_fig,
    stats,
):
    # Single stacked horizontal bar — the TOTAL length vs. the capex reference
    # line tells the scale-mismatch story far better than individual bars.
    _sorted = mkt_cap.sort_values("gain_t", ascending=False)
    _total = _sorted["gain_t"].sum()
    _capex_t = stats["capex_2025"] / 1000  # $B → $T

    fig_mktcap, _ax = plt.subplots(figsize=FIGSIZE["wide"])

    _left = 0.0
    for _, _row in _sorted.iterrows():
        _ticker = _row["ticker"]
        _gain = _row["gain_t"]
        _clr = company_color(_ticker)
        _ax.barh(
            0, _gain, left=_left, height=0.55,
            color=_clr, edgecolor="white", linewidth=1.5,
            label=company_label(_ticker),
        )
        # Direct label on segments wide enough to hold text
        if _gain >= 0.8:
            _ax.text(
                _left + _gain / 2, 0,
                f"{company_label(_ticker)}\n+${_gain:.1f}T",
                ha="center", va="center",
                fontsize=FONTS["annotation"] - 1, fontweight="bold",
                color="white",
            )
        _left += _gain

    # Reference line: the punchline — capex is a sliver of the total
    _ax.axvline(
        _capex_t, color=COLORS["accent"], linestyle="-", linewidth=2.5, alpha=0.9,
    )
    _ax.text(
        _capex_t, 0.38,
        f"  2025 capex: ${stats['capex_2025']:.0f}B",
        fontsize=FONTS["annotation"], fontweight="bold",
        color=COLORS["accent"], va="bottom",
    )

    # Total at right end
    _ax.text(
        _total + 0.12, 0,
        f"${_total:.1f}T",
        ha="left", va="center",
        fontsize=FONTS["value_label"], fontweight="bold",
        color=COLORS["text_dark"],
    )

    _ax.set_yticks([])
    _ax.set_xlabel(
        "Market cap gain, Jan 2023 \u2192 Feb 2026 ($T)", fontsize=FONTS["axis_label"]
    )
    _ax.tick_params(axis="x", labelsize=FONTS["tick_label"])

    legend_below(_ax, ncol=len(_sorted))
    chart_title(
        fig_mktcap,
        f"~{stats['ratio_vs_2025']:.0f}x gap between market cap gains and annual capex",
    )
    plt.tight_layout()
    save_fig(fig_mktcap, cfg.img_dir / "dd001_valuation_disconnect.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo, stats):
    _chart = mo.image(
        src=(cfg.img_dir / "dd001_valuation_disconnect.png").read_bytes(), width=850
    )
    mo.md(
        "# Markets added ~\\${mkt:.1f}T in value against ~\\${capex:.0f}B in annual spending"
        .format(mkt=stats['mkt_gain_t'], capex=stats['capex_2025'])
        + f"""

    {_chart}

    *The seven largest AI-associated companies gained ~\\${stats['mkt_gain_t']:.1f}T in
    market capitalization over three years (Jan 2023 - Feb 2026). Combined 2025 capex
    for the six hyperscalers was ~\\${stats['capex_2025']:.0f}B — markets priced in
    ~{stats['ratio_vs_2025']:.0f}x the annual infrastructure investment. The red line
    shows total 2025 capex for scale. Tesla is included in market cap but its capex
    (~\\$11B, primarily automotive) is excluded from the hyperscaler total; see callout
    below. Note: some companies (AMZN, MSFT) saw mkt cap dip or flatten in early 2026
    even as capex accelerated — the valuation gap is narrowing but remains extreme.
    Sources: Yahoo Finance (market cap, Feb 14 2026), SEC filings via yfinance (capex).*

    This is Layer 1 of the disconnect: the financial narrative runs far ahead
    of the physical capital being deployed.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    > **The Tesla/xAI question.** Tesla's \\$1.18T market cap gain (Jan 2023 - Feb 2026)
    > is overwhelmingly priced on AI, not cars: forward P/E is ~160x vs. the auto sector
    > median of 6.2x, and Musk claims 80% of Tesla's future value will come from the
    > Optimus robot. Tesla spent ~\\$5B on AI infrastructure in 2024 (44% of total capex),
    > scaling from 35K to 85K H100 GPUs, and guides \\$20B+ for 2026 with a hard pivot
    > toward robotaxi and Optimus production (discontinuing Model S/X to repurpose lines).
    >
    > Separately, Musk's xAI built the 200,000-GPU "Colossus" supercomputer in Memphis
    > for ~\\$7B, raised \\$22B+ in venture capital, and was acquired by SpaceX in February
    > 2026 at a \\$250B valuation. Tesla invested \\$2B in xAI's Series E — over shareholder
    > objections (the non-binding vote rejected the investment; Tesla's board proceeded
    > anyway). Shareholders have sued Musk for diverting \\$500M of Nvidia GPUs and 11+
    > engineers from Tesla to xAI.
    >
    > The Tesla-xAI-SpaceX nexus illustrates a distinct pattern: AI infrastructure capital
    > flowing through a web of related entities with overlapping leadership, shared resources,
    > and ambiguous corporate boundaries. Tesla's capex is excluded from the hyperscaler
    > total above because its core spend remains automotive, but the AI narrative drives
    > its valuation — making it arguably the most extreme example of the disconnect this
    > analysis tracks.
    >
    > *Sources: Tesla 10-K (2024), TechCrunch, CNBC, CompaniesMarketCap, AI Magazine,
    > court filings (Cleveland Bakers and Teamsters Pension Fund v. Musk, Delaware
    > Chancery Court, June 2024).*
    """)
    return


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    ---

    ## Layer 2: The Revenue Question

    Sequoia Capital's David Cahn estimated (September 2024) that the AI industry
    needs ~\\$600B in annual revenue to justify the infrastructure buildout. As of
    Q4 2025, the three major cloud providers generated ~\\${stats['cloud_rev_q4']:.0f}B
    in quarterly revenue (~\\${stats['cloud_rev_q4_annual']:.0f}B annualized). Full-year
    2025 combined cloud revenue was ~\\${stats['cloud_rev_2025']:.0f}B.

    The gap is narrowing — but capex is accelerating faster:

    | Metric | 2024 | 2025 | 2026 (guided) |
    | :--- | :--- | :--- | :--- |
    | Hyperscaler capex (6 co.) | ~\\${stats['capex_2024']:.0f}B | ~\\${stats['capex_2025']:.0f}B | ~\\${stats['guidance_2026']:.0f}B |
    | Cloud revenue (3 providers) | ~\\${stats['cloud_rev_2024']:.0f}B | ~\\${stats['cloud_rev_2025']:.0f}B | est. ~\\$400-450B |
    | Capex / Revenue ratio\\* | ~{stats['capex_2024'] / stats['cloud_rev_2024']:.1f}x | ~{stats['capex_2025'] / stats['cloud_rev_2025']:.1f}x | ~1.5-1.8x |

    \\*This ratio overstates the mismatch: the numerator covers 6 companies (including
    Meta, Oracle, Nvidia) while the denominator covers only 3 cloud providers' reported
    cloud segments (AWS, Microsoft Intelligent Cloud, Google Cloud). Meta and Nvidia
    do not report comparable cloud revenue. Still, even the directional trend is clear —
    capex is outpacing revenue growth.

    **The ratio is getting worse, not better.** In normal infrastructure businesses,
    capex-to-revenue ratios of 1-2x are sustainable. At the current trajectory, these
    companies are spending more on infrastructure than their cloud businesses generate
    in revenue. The bet is that AI-driven demand creates a step function in revenue
    growth.

    **Counterargument:** Cloud revenue is growing 20-48% YoY across providers,
    and Google Cloud's contracted backlog surged 55% to \\$240B (Q4 2025). But a
    meaningful portion is hyperscalers selling AI services to each other or to
    VC-funded startups — circular spending that inflates the top line without
    proving durable end-user demand. VC investment in AI/ML startups reached
    \\$131.5B globally in 2024 — over a third of all VC dollars (PitchBook) — and
    many of those startups are major cloud customers. If VC funding contracts,
    a portion of cloud revenue disappears with it. This is the same dynamic
    that inflated telecom revenue in 1999-2000.

    The revenue gap matters for this research because it determines **durability**.
    If AI revenue catches up, the infrastructure is justified. If it doesn't,
    the physical assets persist anyway — but the economics shift from
    "demand-thesis-dependent" to "stranded or repurposed."
    """)
    return


@app.cell
def _(
    COLORS,
    CONTEXT,
    FIGSIZE,
    FONTS,
    cfg,
    chart_title,
    cloud_rev,
    legend_below,
    pd,
    plt,
    save_fig,
):
    # Revenue gap chart: quarterly cloud revenue trajectory vs capex trajectory
    _cloud_quarterly = (
        cloud_rev.groupby("quarter")["revenue_bn"]
        .sum()
        .reset_index()
        .sort_values("quarter")
    )
    _cloud_quarterly["date"] = pd.to_datetime(
        _cloud_quarterly["quarter"].str.replace(r"(\d{4})-Q(\d)", r"\1", regex=True)
        + "-"
        + _cloud_quarterly["quarter"].str.replace(
            r"(\d{4})-Q(\d)", lambda m: str(int(m.group(2)) * 3), regex=True
        )
        + "-28",
        format="%Y-%m-%d",
    )

    fig_rev, _ax = plt.subplots(figsize=FIGSIZE["wide"])

    _ax.bar(
        _cloud_quarterly["date"],
        _cloud_quarterly["revenue_bn"],
        width=60,
        color=CONTEXT,
        alpha=0.7,
        label="Combined cloud revenue (AWS + MSFT Cloud + GCP)",
    )

    # Reference line: $150B/quarter = $600B annual target
    _ax.axhline(150, color=COLORS["accent"], linestyle="--", linewidth=2, alpha=0.8)
    _ax.text(
        _cloud_quarterly["date"].iloc[-1],
        153,
        '  $600B/yr target (Sequoia)',
        fontsize=FONTS["annotation"],
        color=COLORS["accent"],
        fontweight="bold",
        va="bottom",
    )

    # Annotate latest quarter
    _latest = _cloud_quarterly.iloc[-1]
    _ax.text(
        _latest["date"],
        _latest["revenue_bn"] + 3,
        f"${_latest['revenue_bn']:.0f}B",
        ha="center",
        fontsize=FONTS["annotation"],
        fontweight="bold",
        color=COLORS["text_dark"],
    )

    _ax.set_ylabel("Quarterly cloud revenue ($B)", fontsize=FONTS["axis_label"])
    _ax.tick_params(axis="both", labelsize=FONTS["tick_label"])

    legend_below(_ax, ncol=1)
    chart_title(fig_rev, "Cloud revenue growing but still well below the capex justification threshold")
    plt.tight_layout()
    save_fig(fig_rev, cfg.img_dir / "dd001_revenue_gap.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo, stats):
    _chart = mo.image(
        src=(cfg.img_dir / "dd001_revenue_gap.png").read_bytes(), width=850
    )
    mo.md(f"""
    # Cloud revenue is growing fast — but capex is growing faster

    {_chart}

    *Combined quarterly revenue for AWS, Microsoft Intelligent Cloud, and Google Cloud
    Platform. The dashed line shows the ~\\$150B/quarter (\\$600B/year) threshold Sequoia
    estimated would justify current infrastructure spending. Q4 2025 combined revenue
    was ~\\${stats['cloud_rev_q4']:.0f}B (~\\${stats['cloud_rev_q4_annual']:.0f}B annualized).
    Note: Microsoft Intelligent Cloud includes Azure plus other server products, making
    it a broader measure than pure cloud compute. Revenue segments were restated in
    Microsoft's FY2025 reporting. Sources: SEC filings, earnings releases (Q1 2023 –
    Q4 2025).*
    """)
    return


@app.cell
def _(
    COLORS,
    CONTEXT,
    FONTS,
    cfg,
    chart_title,
    legend_below,
    plt,
    save_fig,
    stats,
):
    from matplotlib.patches import Patch, Rectangle

    # Decomposition: shares from FY2024 10-K property schedules, base is 2025 actual
    # Meta: 42% servers/network, 47% buildings/land/CIP
    # Amazon: 56% equipment, 43% buildings/land/CIP
    # Alphabet: 56% tech infrastructure, 40% buildings/land/CIP
    # Cross-company midpoint: ~50% equipment, ~40% construction, ~10% other
    _total_capex = round(stats["capex_2025"])  # $B, data-driven
    _equip = _total_capex * 50 / 100
    _const = _total_capex * 40 / 100
    _equip_life = 6   # max asset life (years)
    _const_life = 40  # max asset life (years)

    fig_decomp, _ax = plt.subplots(figsize=(10, 5))

    # Construction: wide rectangle, short — the lock-in story (accent)
    _ax.add_patch(Rectangle(
        (0, 0), _const_life, _const,
        facecolor=COLORS["accent"], alpha=0.85,
        edgecolor="white", linewidth=1.5,
    ))
    # Equipment: narrow rectangle, tall — depreciates fast (context gray)
    _ax.add_patch(Rectangle(
        (0, 0), _equip_life, _equip,
        facecolor=CONTEXT, alpha=0.85,
        edgecolor="white", linewidth=1.5,
    ))

    # Asset life labels beside each bar
    _ax.text(
        _equip_life + 1, _equip * 0.55,
        "3\u20136 years",
        fontsize=FONTS["annotation"], color=COLORS["text_dark"], fontweight="bold",
    )
    _ax.text(
        _const_life + 1, _const * 0.5,
        "20\u201340 years",
        fontsize=FONTS["annotation"], color=COLORS["accent"], fontweight="bold",
    )

    # Axes: only show meaningful ticks
    _ax.set_xlim(0, 48)
    _ax.set_ylim(0, _equip * 1.15)
    _ax.set_xticks([_equip_life, _const_life])
    _ax.set_yticks([_const, _equip])
    _ax.set_yticklabels(
        [f"\\${_const:.0f}B", f"\\${_equip:.0f}B"],
        fontsize=FONTS["tick_label"],
    )
    _ax.tick_params(axis="x", labelsize=FONTS["tick_label"])
    _ax.set_xlabel("Asset Life (years)", fontsize=FONTS["axis_label"], style="italic")
    _ax.set_ylabel("Capex", fontsize=FONTS["axis_label"], style="italic")

    legend_below(
        _ax,
        handles=[
            Patch(facecolor=CONTEXT, edgecolor=CONTEXT, alpha=0.85),
            Patch(facecolor=COLORS["accent"], edgecolor=COLORS["accent"], alpha=0.85),
        ],
        labels=[
            "Equipment (servers, GPUs, networking)",
            "Construction (buildings, substations, power)",
        ],
    )

    chart_title(
        fig_decomp,
        "40% of capex creates 20\u201340 year assets \u2014 the rest depreciates in under 6",
    )
    plt.tight_layout()
    save_fig(fig_decomp, cfg.img_dir / "dd001_capex_decomposition.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo):
    _chart = mo.image(
        src=(cfg.img_dir / "dd001_capex_decomposition.png").read_bytes(), width=850
    )
    mo.md(rf"""
    # 40% of capex creates 20-40 year assets — the rest depreciates in under 6

    {_chart}

    *Split derived from FY2024 10-K property schedules: Meta reports 47% buildings/land/CIP
    vs. 42% servers/network; Amazon 43% buildings vs. 56% equipment; Alphabet 40% buildings
    vs. 56% technical infrastructure. Cross-company midpoint: ~50% equipment, ~40%
    construction, ~10% other (land, permitting, soft costs). Ratios reflect cumulative gross
    PP&E (the stock of assets), which may differ from marginal capex flows in any given year.
    Bar height reflects 2025 annual spend; width reflects asset life.*

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

    - **Stargate Project:** \\$500B announced (Jan 2025). \\$100B initially committed.
      SoftBank's balance sheet had ~\\$30-40B deployable capital. Financial structure
      remains opaque.
    - **U.S. Interconnection Queue:** ~2,300 GW of generation and storage capacity
      seeking grid connection as of end-2024 — roughly 1.8x total U.S. installed
      capacity. Of all capacity queued from 2000-2019, **77% was withdrawn** and only
      **13% reached commercial operation** (LBNL, *Queued Up* 2025 Edition).
    - **PJM (Data Center Alley):** Projects 30 GW of data center load growth through
      2030; ~140 GW of generation proposals queued to serve that demand.
    - **ERCOT Large Load Requests:** ~63 GW at end-2024, surging to ~226 GW by
      November 2025 — a ~300% increase in one year. Over 70% are data center
      requests, yet only ~5.3 GW of large loads have actually been energized.

    The binding constraint is **power availability**. Median time from interconnection
    request to commercial operation has grown to 4-5 years for recently completed
    projects (LBNL, *Queued Up* 2025 Edition), up from under 2 years in the
    2000s. This is a physical bottleneck that no amount of capital can instantly
    resolve — it requires substations, transmission lines, and generation capacity
    that take years to permit and build.

    The queue is also shifting composition: natural gas requests surged **72% in a
    single year** to 136 GW (end-2024), likely reflecting data center demand for
    firm, dispatchable power. Gas projects have a 31% completion rate — roughly 2-3x
    the rate of solar (13%) or storage (11%).

    As of early 2025: no major hyperscaler project cancellations reported. The pattern
    is delays and site relocation, not outright cancellation. The capital is real,
    but the conversion rate from announcement to operating infrastructure is far
    lower than headlines suggest.
    """)
    return


@app.cell
def _(COLORS, CONTEXT, FONTS, cfg, chart_title, np, plt, save_fig):
    # LBNL "Queued Up" 2025 Edition — queue growth and attrition
    _years = [2020, 2021, 2022, 2023, 2024]
    _gen_gw = [750, 1000, 1350, 1570, 1400]   # generation capacity (GW)
    _storage_gw = [200, 400, 680, 1030, 890]   # storage capacity (GW)

    _fig_queue, _ax = plt.subplots(figsize=(10, 5))

    _x = np.arange(len(_years))
    _w = 0.55

    _ax.bar(_x, _gen_gw, _w, label="Generation", color=CONTEXT, alpha=0.85)
    _ax.bar(
        _x, _storage_gw, _w, bottom=_gen_gw,
        label="Storage", color=COLORS["accent"], alpha=0.85,
    )

    # Annotate totals
    for _i, (_g, _s) in enumerate(zip(_gen_gw, _storage_gw)):
        _ax.text(
            _i, _g + _s + 30, f"{_g + _s:,}",
            ha="center", fontsize=FONTS["annotation"], fontweight="bold",
            color=COLORS["text_dark"],
        )

    # Completion rate annotation
    _ax.annotate(
        "Of all capacity queued\n2000\u20132019:\n77% withdrawn\n13% built",
        xy=(4, 2290), xytext=(3.1, 1800),
        fontsize=FONTS["annotation"], color=COLORS["negative"],
        fontweight="bold", ha="center",
        arrowprops={"arrowstyle": "->", "color": COLORS["negative"], "lw": 1.5},
    )

    _ax.set_xticks(_x)
    _ax.set_xticklabels(_years, fontsize=FONTS["tick_label"])
    _ax.set_ylabel("Active queue capacity (GW)", fontsize=FONTS["axis_label"])
    _ax.tick_params(axis="y", labelsize=FONTS["tick_label"])
    _ax.set_ylim(0, 2800)

    from matplotlib.patches import Patch as _Patch
    _ax.legend(
        handles=[
            _Patch(facecolor=CONTEXT, alpha=0.85),
            _Patch(facecolor=COLORS["accent"], alpha=0.85),
        ],
        labels=["Generation", "Storage"],
        loc="upper left", frameon=False, fontsize=FONTS["annotation"],
    )

    chart_title(
        _fig_queue,
        "U.S. interconnection queue tripled in four years \u2014 but most projects never get built",
    )
    plt.tight_layout()
    save_fig(_fig_queue, cfg.img_dir / "dd001_queue_funnel.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo):
    _chart = mo.image(
        src=(cfg.img_dir / "dd001_queue_funnel.png").read_bytes(), width=850
    )
    mo.md(f"""
    # The queue tripled — but 77% of projects are eventually withdrawn

    {_chart}

    *Total generation and storage capacity in U.S. interconnection queues, year-end.
    Of all capacity that requested interconnection from 2000-2019, only 13% reached
    commercial operation while 77% was withdrawn. Completion rates vary by technology:
    gas (31%), wind (20%), solar (13%), storage (11%). The queue peaked at ~2,600 GW
    in 2023 before declining 12% in 2024 as withdrawal rates exceeded new entries.
    Source: LBNL, "Queued Up" 2025 Edition (data through end-2024).*
    """)
    return


@app.cell
def _(COLORS, CONTEXT, FIGSIZE, FONTS, cfg, chart_title, plt, save_fig, stats):
    import matplotlib.patches as _mp
    import matplotlib.path as _mpath

    _capex = round(stats["capex_2025"])  # data-driven from yfinance
    _bea_total = round(stats["pnfi_bn"])  # FRED PNFI, latest quarterly SAAR
    _pct = stats["pnfi_share_pct"]

    # BEA categories ($B, approximate shares of PNFI) — bottom to top
    # Shares from BEA NIPA Table 5.3.5 (structures ~18%, equipment ~33%, IP ~49%)
    _cats = [
        ("Structures", round(_bea_total * 0.18)),
        ("Equipment", round(_bea_total * 0.33)),
        ("Intellectual property", round(_bea_total * 0.49)),
    ]
    _cat_sum = sum(v for _, v in _cats)

    fig_share, _ax = plt.subplots(figsize=FIGSIZE["wide"])

    # --- Layout constants ---
    _LX = 2.5    # left column right edge
    _RX = 7.5    # right column left edge
    _CW = 0.7    # column width
    _GAP = 50    # visual gap between right-side nodes ($B)

    # --- Compute vertical positions ---
    # Left: contiguous (no gaps)
    _left_pos = []
    _ly = 0.0
    for _, _val in _cats:
        _left_pos.append((_ly, _ly + _val))
        _ly += _val

    # Right: spaced with gaps
    _right_pos = []
    _ry = 0.0
    for _i, (_, _val) in enumerate(_cats):
        _right_pos.append((_ry, _ry + _val))
        _ry += _val + _GAP
    _max_y = max(_ly, _ry)

    # --- Left node ---
    _ax.add_patch(_mp.Rectangle(
        (_LX - _CW, 0), _CW, _cat_sum,
        facecolor=CONTEXT, alpha=0.5, edgecolor="white", linewidth=1,
    ))
    # Hyperscaler slice at bottom (accent)
    _ax.add_patch(_mp.Rectangle(
        (_LX - _CW, 0), _CW, _capex,
        facecolor=COLORS["accent"], alpha=0.75, edgecolor="white", linewidth=1,
    ))

    # --- Right nodes + flow bands ---
    _xm = (_LX + _RX) / 2
    for _i, (_name, _val) in enumerate(_cats):
        _ly0, _ly1 = _left_pos[_i]
        _ry0, _ry1 = _right_pos[_i]

        # Right rectangle
        _ax.add_patch(_mp.Rectangle(
            (_RX, _ry0), _CW, _val,
            facecolor=CONTEXT, alpha=0.5, edgecolor="white", linewidth=1,
        ))

        # S-curve flow band (cubic Bezier)
        verts = [
            (_LX, _ly0),
            (_xm, _ly0), (_xm, _ry0), (_RX, _ry0),
            (_RX, _ry1),
            (_xm, _ry1), (_xm, _ly1), (_LX, _ly1),
            (_LX, _ly0),
        ]
        codes = [
            _mpath.Path.MOVETO,
            _mpath.Path.CURVE4, _mpath.Path.CURVE4, _mpath.Path.CURVE4,
            _mpath.Path.LINETO,
            _mpath.Path.CURVE4, _mpath.Path.CURVE4, _mpath.Path.CURVE4,
            _mpath.Path.CLOSEPOLY,
        ]
        _ax.add_patch(_mp.PathPatch(
            _mpath.Path(verts, codes),
            facecolor=CONTEXT, alpha=0.3,
            edgecolor="none",
        ))

        # Right-side label
        _ax.text(
            _RX + _CW + 0.2, (_ry0 + _ry1) / 2,
            f"{_name}\n${_val:,}B",
            ha="left", va="center",
            fontsize=FONTS["annotation"],
            color=COLORS["text_dark"],
        )

    # --- Left-side labels ---
    _ax.text(
        _LX - _CW - 0.15, _cat_sum / 2,
        f"US nonresidential\nfixed investment\n${_bea_total / 1000:.1f}T/year",
        ha="right", va="center",
        fontsize=FONTS["annotation"], fontweight="bold",
        color=COLORS["text_dark"],
    )
    _ax.text(
        _LX - _CW - 0.15, _capex / 2,
        f"Hyperscaler capex\n${_capex}B ({_pct:.0f}%)",
        ha="right", va="center",
        fontsize=FONTS["annotation"], fontweight="bold",
        color=COLORS["accent"],
    )

    _ax.set_xlim(0, 10.5)
    _ax.set_ylim(-120, _max_y + 120)
    _ax.axis("off")

    chart_title(
        fig_share,
        f"Hyperscaler capex is ~{_pct:.0f}% of all US private nonresidential investment",
    )
    plt.tight_layout()
    save_fig(fig_share, cfg.img_dir / "dd001_capex_us_share.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo, stats):
    _chart = mo.image(
        src=(cfg.img_dir / "dd001_capex_us_share.png").read_bytes(), width=850
    )
    mo.md(f"""
    # Hyperscaler capex is ~{stats['pnfi_share_pct']:.0f}% of all US private nonresidential investment

    {_chart}

    *Total US private nonresidential fixed investment is ~\\${stats['pnfi_bn'] / 1000:.1f}T
    SAAR (BEA NIPA Table 5.3.5, Q2 2025 via FRED series PNFI). Hyperscaler capex
    (~\\${stats['capex_2025']:.0f}B in 2025) represents a significant and rapidly growing
    share — concentrated in a handful of companies making infrastructure decisions that
    normally take decades of utility planning. Category shares (structures ~18%,
    equipment ~33%, IP ~49%) are approximate from BEA Table 5.3.5.*

    **Caveat:** This comparison overstates the US-specific share. Hyperscaler capex
    is global (significant spending in Europe, Asia, and the Middle East), while the
    BEA denominator is US-only. The true US share is lower, but no public data
    cleanly separates domestic from international hyperscaler capex.

    For context: total US data center construction spending is estimated at \\$30-50B
    annually (JLL, CBRE). The Census Bureau's C30 construction series does not
    separately report data centers — they are buried in "commercial/warehouse"
    categories. This is one of several critical data gaps.
    """)
    return


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    ---

    ## The DeepSeek Test

    DeepSeek's R1 model (January 2025) demonstrated competitive AI performance at
    reportedly much lower training costs. Nvidia lost ~\\$600B in market cap in a
    single day. It was the first real test of whether efficiency gains would reduce
    infrastructure demand.

    **They didn't.** A year later, the 2025 actuals are in — every hyperscaler
    *accelerated*:

    | Company | 2024 actual | 2025 actual | 2026 guidance |
    | :--- | :--- | :--- | :--- |
    | Amazon | ~\\${stats['amzn_2024']:.0f}B | ~\\${stats['amzn_2025']:.0f}B | \\${stats['amzn_2026g']:.0f}B |
    | Alphabet | ~\\${stats['googl_2024']:.0f}B | ~\\${stats['googl_2025']:.0f}B | \\${stats['googl_2026g']:.0f}B |
    | Microsoft | ~\\${stats['msft_2024']:.0f}B | ~\\${stats['msft_2025']:.0f}B | ~\\${stats['msft_2026g']:.0f}B |
    | Meta | ~\\${stats['meta_2024']:.0f}B | ~\\${stats['meta_2025']:.0f}B | \\$115-135B |

    Management teams invoked the **Jevons paradox**: cheaper AI inference increases
    adoption and ultimately increases total compute demand. Historical precedent
    (LED lighting, Moore's Law, cloud computing) supports this — but it is not
    guaranteed to apply. The combined 2026 guidance of ~\\${stats['guidance_2026']:.0f}B
    would consume nearly 100% of these companies' operating cash flow (vs. a 10-year
    average of ~40%), prompting significant debt issuance.

    For infrastructure analysis, the DeepSeek episode reinforced a key finding:
    **hyperscaler capex is stickier than valuations.** Stock prices fluctuate on
    sentiment; capital expenditure programs, once committed, roll forward on
    multi-year procurement contracts, construction timelines, and competitive
    pressure. This is not absolute — Meta held capex flat at ~\\${stats['meta_2022']:.0f}B
    through its "year of efficiency" (2023) while cutting headcount by 21%, and
    the stock rallied — but the current competitive dynamic, where every hyperscaler
    fears falling behind on AI capacity, makes unilateral deceleration costly.
    """)
    return


@app.cell
def _(
    COLORS,
    CONTEXT,
    FIGSIZE,
    FONTS,
    capex_raw,
    cfg,
    chart_title,
    company_color,
    company_label,
    legend_below,
    pd,
    plt,
    save_fig,
):
    _tickers = ["MSFT", "AMZN", "GOOGL", "META"]
    _deepseek_date = pd.Timestamp("2025-01-27")

    fig_quarterly, _ax = plt.subplots(figsize=FIGSIZE["wide"])

    for _ticker in _tickers:
        _sub = capex_raw[capex_raw["ticker"] == _ticker].sort_values("date")
        if len(_sub) < 2:
            continue
        # SWD: pre-DeepSeek is CONTEXT gray, post-DeepSeek is the story
        _pre = _sub[_sub["date"] <= _deepseek_date]
        _post = _sub[_sub["date"] >= _deepseek_date]
        _clr = company_color(_ticker)

        # Context: pre-DeepSeek in gray (not muted brand color)
        _ax.plot(
            _pre["date"], _pre["capex_bn"],
            marker="o", markersize=3, color=CONTEXT,
            linewidth=1.2, alpha=0.5,
        )
        # Story: post-DeepSeek in bold brand color — no slowdown
        _ax.plot(
            _post["date"], _post["capex_bn"],
            marker="o", markersize=6, color=_clr,
            linewidth=3, alpha=1.0,
            label=company_label(_ticker),
        )

    _ax.set_ylabel("Quarterly capex ($B)", fontsize=FONTS["axis_label"])
    _ax.tick_params(axis="both", labelsize=FONTS["tick_label"])
    _ax.grid(True, axis="y", linestyle=":", alpha=0.4)

    # DeepSeek moment — accent it as the dividing line
    _ymax = capex_raw[capex_raw["ticker"].isin(_tickers)]["capex_bn"].max()
    _ax.axvline(
        _deepseek_date, color=COLORS["accent"], linestyle="-", linewidth=2, alpha=0.7,
    )
    _ax.text(
        _deepseek_date,
        _ymax * 0.98,
        "  DeepSeek R1",
        fontsize=FONTS["annotation"],
        color=COLORS["accent"],
        fontweight="bold",
        va="top",
    )
    # Callout: the punchline — position below the lines to avoid overlap
    _ax.text(
        _deepseek_date + pd.Timedelta(days=200),
        _ymax * 0.18,
        "All four accelerated\nafter DeepSeek",
        fontsize=FONTS["annotation"],
        color=COLORS["accent"],
        fontweight="bold",
        ha="left", va="center",
        bbox={"boxstyle": "round,pad=0.4", "fc": "white", "ec": COLORS["accent"], "alpha": 0.8},
    )

    legend_below(_ax, ncol=4)
    chart_title(fig_quarterly, "DeepSeek R1 changed nothing \u2014 all four hyperscalers accelerated capex")
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
    The red line marks DeepSeek R1's release (January 2025). Despite the efficiency
    shock, all four accelerated capex through 2025. Data: yfinance (SEC filings,
    through Q4 2025).*
    """)
    return


@app.cell(hide_code=True)
def _(mo, stats):
    _capex_low = stats["capex_2025"] * 0.35
    mo.md(f"""
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

    **The analogy has limits.** Dark fiber requires near-zero maintenance — it sits
    in conduit until someone lights it. Data centers are not passive assets. They
    require continuous power, cooling, and maintenance. A stranded data center is
    not a stranded fiber cable — it has ongoing operating costs even when idle.
    The better parallel is the *grid infrastructure* built to serve data centers
    (substations, transmission lines), which is closer to the fiber analogy:
    durable, low-maintenance, and useful regardless of what the connected load does.

    The question for AI infrastructure is whether the same pattern holds: **does
    the grid modernization funded by AI capex retain value even if AI revenue
    never reaches \\$600B?** The durability taxonomy says yes for the physical
    construction layer and no for the equipment layer — and this qualitative
    conclusion holds across plausible decomposition ranges. FY2024 10-K property
    schedules show construction at 40-47% of gross PP&E for Meta, Amazon, and
    Alphabet — higher than the 35% often cited in analyst estimates. Even at
    the low end, 35% of ~\\${stats['capex_2025']:.0f}B is ~\\${_capex_low:.0f}B in
    durable physical assets deployed in a single year.
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

    - **DD-002: Grid Modernization** (active) — What generation mix is getting
      built? Which fuel types? Where geographically? Who benefits from the
      cost allocation? What feedback loops shape the buildout trajectory?
    - **DD-003: Labor Markets** (scoping) — Who gets hired and displaced? What
      are the temporal dynamics of build-phase construction employment vs.
      long-term operations staffing vs. knowledge-work displacement?
    - **CS-4: Material Supply Chains** (not started) — GOES steel, copper,
      transformers. Where does concentration risk bind?

    ### Key data gaps to resolve

    1. No government statistical series tracks data center construction separately
    2. No clean separation of "AI capex" vs. "general cloud capex" in public filings
    3. Interconnection queue attrition rates are estimated, not precisely tracked
    4. Stargate and similar mega-projects have opaque financial structures
    5. AI-specific electricity consumption at facility level is not systematically reported

    ---

    *Sources: SEC EDGAR (10-K/10-Q filings via yfinance, through Q4 2025),
    Yahoo Finance (market caps, Feb 2026), FRED (BEA PNFI series, Q2 2025 SAAR),
    Sequoia Capital ("The \\$600B Question," Sep 2024), CreditSights (hyperscaler
    capex estimates, Jan-Feb 2026), earnings call transcripts (Jan-Feb 2026).
    See `research/ai_valuation_vs_infrastructure_reality.md` for full source list.*
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
