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

    AI company valuations have added nearly ${stats['mkt_gain_t']:.1f} trillion in
    market cap since January 2023. Hyperscaler capital expenditure reached
    ~${stats['capex_2024']:.0f}B in 2024, with ~${stats['guidance_2025']:.0f}B guided
    for 2025. But how much of that capital is actually converting to physical
    infrastructure — and what does the grid get from the portion that does?

    This notebook traces the **three-layer disconnect** between AI financial narratives
    and physical outcomes:

    1. **Valuations vs. Capex** — ~${stats['mkt_gain_t']:.1f}T in market cap gains vs. ~${stats['capex_2024']:.0f}B in annual spending
    2. **Capex vs. Revenue** — The "$600B question" (Sequoia, 2024)
    3. **Announcements vs. Physical Reality** — most queued projects never reach operation (LBNL, 2024)

    The key insight: an estimated ~30-40% of capex funds physical construction that
    creates the most durable assets. Equipment (~50-60%) depreciates in 3-6 years.
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
        BAR_DEFAULTS,
        CATEGORICAL,
        COLORS,
        COMPANY_COLORS,
        COMPANY_LABELS,
        CONTEXT,
        FIGSIZE,
        FONTS,
        annotate_point,
        chart_title,
        company_color,
        company_label,
        focus_colors,
        legend_below,
        reference_line,
    )

    cfg = setup()
    return (
        BAR_DEFAULTS,
        COLORS,
        CONTEXT,
        FIGSIZE,
        FONTS,
        annotate_point,
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
def _(capex_annual, guidance_2025, mkt_cap):
    # Compute key summary stats — used by all markdown captions to avoid hardcoded numbers.
    _tickers_6 = ["MSFT", "AMZN", "GOOGL", "META", "ORCL", "NVDA"]
    _annual = capex_annual[capex_annual["ticker"].isin(_tickers_6)]
    stats = {
        "capex_2022": _annual[_annual["year"] == 2022]["capex_bn"].sum(),
        "capex_2023": _annual[_annual["year"] == 2023]["capex_bn"].sum(),
        "capex_2024": _annual[_annual["year"] == 2024]["capex_bn"].sum(),
        "guidance_2025": guidance_2025[
            guidance_2025["ticker"].isin(_tickers_6)
        ]["capex_bn"].sum(),
        "mkt_gain_t": mkt_cap["gain_t"].sum(),
    }
    stats["ratio_vs_2024"] = stats["mkt_gain_t"] / (stats["capex_2024"] / 1000)
    # Per-company annual totals (for inline citations)
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
    FIGSIZE,
    FONTS,
    capex_annual,
    cfg,
    chart_title,
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

    # Aggregate actuals by year for 2022-2024
    _years = [2022, 2023, 2024]
    _data = capex_annual[
        (capex_annual["ticker"].isin(_tickers)) & (capex_annual["year"].isin(_years))
    ].copy()

    # Add 2025 guidance
    _guide = guidance_2025[guidance_2025["ticker"].isin(_tickers)].copy()
    _combined = pd.concat(
        [_data[["ticker", "year", "capex_bn"]], _guide[["ticker", "year", "capex_bn"]]],
        ignore_index=True,
    )

    # SWD: companies on x-axis, years stacked — shows WHO is driving the acceleration.
    # Graduated grays (light→dark) for actuals, accent for 2025 guidance.
    fig_capex, _ax = plt.subplots(figsize=FIGSIZE["wide"])
    _all_years = sorted(_combined["year"].unique())
    _x = np.arange(len(_tickers))

    # Year colors: graduated grays for actuals, accent for guidance
    _year_colors = {
        2022: "#d4d4d4",
        2023: "#aaaaaa",
        2024: "#777777",
        2025: COLORS["accent"],
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
            label=str(_yr) + ("*" if _yr == 2025 else ""),
        )
        # Hatch the 2025 guidance bars
        if _yr == 2025:
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
        _total = _combined[_combined["ticker"] == _ticker]["capex_bn"].sum()
        _ax.text(
            _j, _bottoms[_j] + 4, f"${_bottoms[_j]:.0f}B",
            ha="center", fontsize=FONTS["annotation"], fontweight="bold",
            color=COLORS["accent"],
        )

    legend_below(_ax, ncol=len(_all_years))
    chart_title(fig_capex, "Hyperscaler capex has more than doubled in two years")
    plt.tight_layout()
    save_fig(fig_capex, cfg.img_dir / "dd001_capex_acceleration.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo, stats):
    _chart = mo.image(
        src=(cfg.img_dir / "dd001_capex_acceleration.png").read_bytes(), width=850
    )
    mo.md(f"""
    # Hyperscaler capex has more than doubled in two years

    {_chart}

    *2025 figures are management guidance (hatched bars), not audited actuals.
    Combined capex for these six companies: ~${stats['capex_2023']:.0f}B (2023) →
    ~${stats['capex_2024']:.0f}B (2024) → ~${stats['guidance_2025']:.0f}B (2025
    guidance). Capex aggregated by calendar year; note that Microsoft (June FY) and
    Oracle (May FY) report on non-calendar fiscal years. Capex figures include all
    capital expenditure, not only AI-related spending (e.g., Amazon includes logistics
    infrastructure). Sources: SEC 10-K/10-Q filings, earnings call transcripts.*
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
    _capex_t = stats["capex_2024"] / 1000  # $B → $T

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
        f"  2024 capex: ${stats['capex_2024']:.0f}B",
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
        "Market cap gain, Jan 2023 \u2192 Jan 2025 ($T)", fontsize=FONTS["axis_label"]
    )
    _ax.tick_params(axis="x", labelsize=FONTS["tick_label"])

    legend_below(_ax, ncol=len(_sorted))
    chart_title(
        fig_mktcap,
        f"~{stats['ratio_vs_2024']:.0f}x gap between market cap gains and annual capex",
    )
    plt.tight_layout()
    save_fig(fig_mktcap, cfg.img_dir / "dd001_valuation_disconnect.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo, stats):
    _chart = mo.image(
        src=(cfg.img_dir / "dd001_valuation_disconnect.png").read_bytes(), width=850
    )
    mo.md(f"""
    # Markets added ~\${stats['mkt_gain_t']:.1f}T in value against ~\${stats['capex_2024']:.0f}B in annual spending

    {_chart}

    *The six largest AI-associated companies gained ~\${stats['mkt_gain_t']:.1f}T in
    market capitalization in two years (Jan 2023 – Jan 2025). Their combined 2024
    capex was ~\${stats['capex_2024']:.0f}B — markets priced in
    ~{stats['ratio_vs_2024']:.0f}x the annual infrastructure investment. The red line
    shows total 2024 capex for scale. Sources: Yahoo Finance (market cap), SEC filings
    (capex).*

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

    # Estimated decomposition: shares are industry estimates, base is 2024 actual
    _total_capex = round(stats["capex_2024"])  # $B, data-driven
    _equip = _total_capex * 55 / 100
    _const = _total_capex * 35 / 100
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
        "35% of capex creates 20\u201340 year assets \u2014 the rest depreciates in under 6",
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
    # 35% of capex creates 20-40 year assets — the rest depreciates in under 6

    {_chart}

    *These are industry-level estimates, not audited figures. The ~55% equipment /
    ~35% construction split is an approximation derived from analyst reports and
    partial 10-K disclosures; Microsoft's property schedule suggests a roughly
    50/50 split for their own capex, and ratios vary by company and year. The key
    qualitative point — that a substantial share of capex funds long-lived physical
    assets — holds across plausible ranges. Bar height reflects annual spend; width reflects
    asset life.*

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
      withdrawal rates exceed 70% of queued capacity (LBNL, *Queued Up* 2024 edition;
      exact rates vary by year and interconnection type).
    - **ERCOT Large Load Requests:** ~60 GW pending (includes data centers and crypto).

    The binding constraint is **power availability**. Median time from interconnection
    request to commercial operation has grown to 5 years nationally (LBNL, *Queued Up*
    2024), up from ~2 years a decade ago. This is a physical bottleneck that no
    amount of capital can instantly resolve — it requires substations, transmission
    lines, and generation capacity that take years to permit and build.

    As of early 2025: no major hyperscaler project cancellations reported. The pattern
    is delays and site relocation, not outright cancellation. The capital is real,
    but the conversion rate from announcement to operating infrastructure is far
    lower than headlines suggest.
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
    plt,
    save_fig,
    stats,
):
    import matplotlib.patches as _mp
    import matplotlib.path as _mpath

    _capex = round(stats["capex_2024"])  # data-driven, not hardcoded
    _bea_total = 3500  # Total US private nonresidential fixed investment (BEA)
    _pct = _capex / _bea_total * 100

    # BEA categories ($B, approximate 2024) — bottom to top
    _cats = [
        ("Structures", 750),
        ("Equipment", 1400),
        ("Intellectual property", 1400),
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
    _bea_total = 3500  # BEA NIPA Table 5.3.5, 2024 ($B)
    _pct = stats["capex_2024"] / _bea_total * 100
    mo.md(f"""
    # Hyperscaler capex is ~{_pct:.0f}% of all US private nonresidential investment

    {_chart}

    *Total US private nonresidential fixed investment is ~${_bea_total / 1000:.1f}T
    annually (BEA NIPA Table 5.3.5, 2024). Hyperscaler capex (~${stats['capex_2024']:.0f}B
    in 2024) represents a significant and rapidly growing share — concentrated in a
    handful of companies making infrastructure decisions that normally take decades of
    utility planning.*

    **Caveat:** This comparison overstates the US-specific share. Hyperscaler capex
    is global (significant spending in Europe, Asia, and the Middle East), while the
    BEA denominator is US-only. The true US share is lower, but no public data
    cleanly separates domestic from international hyperscaler capex.

    For context: total US data center construction spending is estimated at $30-50B
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
    pressure. This is not absolute — Meta cut capex from ~${stats['meta_2022']:.0f}B
    (2022) to ~${stats['meta_2023']:.0f}B (2023) during its "year of efficiency" and
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
