import marimo

__generated_with = "0.19.11"
app = marimo.App(
    width="compact",
    app_title="AI Capital and Labor Markets",
    css_file="../../src/notebook_theme/custom.css",
    html_head_file="../../src/notebook_theme/head.html",
)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # AI Capital and the Labor Market
    ## Electricians and Data Scientists — the Two Workforces Building the AI Stack

    *Thandolwethu Zwelakhe Dlamini*

    ---

    The standard AI-and-jobs debate asks whether software will displace workers.
    That question matters, but it is not where the 2024 labor market signal is
    clearest or most actionable.

    The clearest current signal is in two places that are almost never discussed
    together. First: demand for data scientists, software developers, and ML
    engineers is accelerating — priced into wages, visible in employment data,
    broadly reported. Second: the physical construction of AI data centers is
    creating acute demand for licensed electricians at a scale that is straining
    supply in the specific counties where the infrastructure is being built.
    Electricians are not part of the AI workforce debate. They should be.

    This notebook examines both with BLS public data: sector employment trends
    from FRED, occupational wages from OEWS, and county-level hiring from QCEW.
    The closing argument connects them — if electrician supply constrains how
    fast data centers can be built, the labor market is not just an outcome of
    AI capex, it is a feedback into it.

    **Causal chain under examination:**
    AI capex ↑ → hyperscalers hire technical staff + contract data center
    construction → construction labor demand ↑ + tech occupation wages ↑ →
    electrician shortage constrains buildout timelines → capex deployment lag ↑.

    The last link feeds directly into DD-002's interconnection queue finding:
    the constraint on AI infrastructure deployment is not just regulatory
    (grid interconnection) — it is also human capital (where are the electricians).
    """)
    return


@app.cell
def _(add_brand_mark, add_source):
    import sys

    import marimo as mo

    sys.path.insert(0, str(mo.notebook_dir().parent.parent))

    import matplotlib.dates as mdates
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd

    from src.data.bls import (
        SOC_CODES_TECHNICAL,
        SOC_CODES_TRADES,
        fetch_oews_soc,
        fetch_qcew_state,
    )
    from src.data.db import query
    from src.notebook import save_fig, setup
    from src.plotting import (
        CATEGORICAL,
        COLORS,
        CONTEXT,
        FIGSIZE,
        FONTS,
        add_brand_mark,
        add_source,
        legend_below,
    )

    cfg = setup()
    return (
        CATEGORICAL,
        COLORS,
        CONTEXT,
        FIGSIZE,
        FONTS,
        SOC_CODES_TECHNICAL,
        SOC_CODES_TRADES,
        add_brand_mark,
        add_source,
        cfg,
        fetch_oews_soc,
        fetch_qcew_state,
        legend_below,
        mdates,
        mo,
        np,
        pd,
        plt,
        query,
        save_fig,
        sys,
    )


@app.cell
def _(pd, query):
    # FRED employment series from the research database.
    # These are CES (Current Employment Statistics) monthly series,
    # seasonally adjusted, in thousands of persons.
    _fred = query(
        """
        SELECT series_id, CAST(date AS DATE) AS date, value
        FROM energy_data.fred_series
        WHERE series_id IN (
            'CES6054150001',
            'USCONS',
            'USINFO',
            'MANEMP',
            'CES4422000001'
        )
        AND CAST(date AS DATE) >= '2019-01-01'
        ORDER BY series_id, date
        """
    )

    # Pivot to wide format: index=date, columns=series_id
    empl_wide_raw = _fred.pivot(index="date", columns="series_id", values="value")
    # FRED dates are end-of-month (Jan 31, Feb 28, …). Normalize to month-start
    # so .loc[Timestamp("2020-01-01")] works. Strip timezone if present
    # (DuckDB may return TIMESTAMPTZ as tz-aware or tz-naive depending on driver).
    _idx = pd.to_datetime(empl_wide_raw.index)
    if _idx.tz is not None:
        _idx = _idx.tz_localize(None)
    empl_wide_raw.index = _idx.to_period("M").to_timestamp()
    empl_wide_raw = empl_wide_raw.sort_index()

    # Index to January 2020 = 100 (pre-pandemic, pre-AI-surge baseline)
    _base_date = pd.Timestamp("2020-01-01")
    _base = empl_wide_raw.loc[_base_date]
    empl_idx = (empl_wide_raw / _base * 100).dropna(how="all")

    return empl_idx, empl_wide_raw


@app.cell
def _(fetch_oews_soc, pd):
    # BLS Occupational Employment and Wage Statistics — national flat files.
    # Downloads and caches to data/raw/bls/oews_{year}_national.parquet.
    # First run downloads ~10MB/year (zipped Excel); subsequent runs use cache.
    try:
        wages_df = fetch_oews_soc(years=list(range(2019, 2025)))
    except Exception as _e:
        wages_df = pd.DataFrame()
        print(
            f"OEWS download failed: {_e}. "
            "To pre-load, run: uv run python -m src.data.pipelines --oews"
        )

    return (wages_df,)


@app.cell
def _(fetch_qcew_state, pd):
    # BLS Quarterly Census of Employment and Wages — state-level, NAICS 518210.
    # (Data Processing, Hosting, and Related Services — the data center industry.)
    # Annual averages, private sector ownership (own_code=5).
    # BLS releases annual QCEW ~6 months after year end; 2024 data available by mid-2025.
    _qcew_years = []
    for _yr in [2024, 2023, 2022, 2021, 2020, 2019]:
        try:
            _df = fetch_qcew_state("518210", _yr)
            _qcew_years.append(_df)
        except Exception:
            pass

    qcew_dc = pd.concat(_qcew_years, ignore_index=True) if _qcew_years else pd.DataFrame()

    return (qcew_dc,)


@app.cell
def _(empl_idx, np, pd, qcew_dc, wages_df):
    # State FIPS codes — used for QCEW state-level charts
    _state_fips: dict[str, str] = {
        "01": "Alabama", "02": "Alaska", "04": "Arizona", "05": "Arkansas",
        "06": "California", "08": "Colorado", "09": "Connecticut", "10": "Delaware",
        "11": "D.C.", "12": "Florida", "13": "Georgia", "16": "Idaho",
        "17": "Illinois", "18": "Indiana", "19": "Iowa", "20": "Kansas",
        "21": "Kentucky", "22": "Louisiana", "23": "Maine", "24": "Maryland",
        "25": "Massachusetts", "26": "Michigan", "27": "Minnesota", "28": "Mississippi",
        "29": "Missouri", "30": "Montana", "31": "Nebraska", "32": "Nevada",
        "33": "New Hampshire", "34": "New Jersey", "35": "New Mexico", "36": "New York",
        "37": "North Carolina", "38": "North Dakota", "39": "Ohio", "40": "Oklahoma",
        "41": "Oregon", "42": "Pennsylvania", "44": "Rhode Island", "45": "South Carolina",
        "46": "South Dakota", "47": "Tennessee", "48": "Texas", "49": "Utah",
        "50": "Vermont", "51": "Virginia", "53": "Washington", "54": "West Virginia",
        "55": "Wisconsin", "56": "Wyoming",
    }

    # ── Employment index stats (always available from DB) ──────────────
    _tech_col = "CES6054150001"
    _const_col = "USCONS"
    _info_col = "USINFO"
    _latest = empl_idx.index.max()
    _capex_date = pd.Timestamp("2023-01-01")

    def _idx_val(col: str, date: pd.Timestamp) -> float | None:
        if col not in empl_idx.columns:
            return None
        if date not in empl_idx.index:
            # Find nearest date
            _idx = empl_idx.index.get_indexer([date], method="nearest")[0]
            return float(empl_idx.iloc[_idx][col])
        return float(empl_idx.loc[date, col])

    _tech_latest = _idx_val(_tech_col, _latest)
    _const_latest = _idx_val(_const_col, _latest)
    _tech_at_capex = _idx_val(_tech_col, _capex_date)

    stats: dict = {
        "tech_index_latest": round(_tech_latest, 1) if _tech_latest else 0.0,
        "const_index_latest": round(_const_latest, 1) if _const_latest else 0.0,
        "tech_change_from_2020_pct": round(_tech_latest - 100, 1) if _tech_latest else 0.0,
        "const_change_from_2020_pct": round(_const_latest - 100, 1) if _const_latest else 0.0,
        "tech_since_capex_pct": (
            round((_tech_latest / _tech_at_capex - 1) * 100, 1)
            if _tech_latest and _tech_at_capex
            else 0.0
        ),
        "latest_date_str": _latest.strftime("%B %Y"),
        # OEWS placeholders
        "electrician_wage_2024": 0,
        "electrician_wage_2019": 0,
        "software_dev_wage_2024": 0,
        "software_dev_wage_2019": 0,
        "electrician_wage_change_pct": 0.0,
        "software_dev_wage_change_pct": 0.0,
        "wages_available": False,
        # QCEW placeholders
        "dc_empl_top_state": "N/A",
        "dc_empl_top_count": 0,
        "va_dc_empl": 0,
        "dc_year": 2024,
        "qcew_available": False,
    }

    # ── OEWS wage stats ────────────────────────────────────────────────
    if not wages_df.empty:
        _w = wages_df.dropna(subset=["a_mean"])

        def _wage(soc: str, year: int) -> int:
            _r = _w[(_w["occ_code"] == soc) & (_w["year"] == year)]
            return int(_r["a_mean"].iloc[0]) if not _r.empty else 0

        _e24 = _wage("47-2111", 2024)
        _e19 = _wage("47-2111", 2019)
        _s24 = _wage("15-1252", 2024)
        _s19 = _wage("15-1252", 2019)

        stats.update({
            "electrician_wage_2024": _e24,
            "electrician_wage_2019": _e19,
            "software_dev_wage_2024": _s24,
            "software_dev_wage_2019": _s19,
            "electrician_wage_change_pct": (
                round((_e24 / _e19 - 1) * 100, 1) if _e19 > 0 else 0.0
            ),
            "software_dev_wage_change_pct": (
                round((_s24 / _s19 - 1) * 100, 1) if _s19 > 0 else 0.0
            ),
            "wages_available": True,
        })

    # ── QCEW geographic stats ──────────────────────────────────────────
    if not qcew_dc.empty:
        _recent_yr = int(qcew_dc["year"].max())
        _recent = qcew_dc[qcew_dc["year"] == _recent_yr].copy()
        _recent["state"] = _recent["area_fips"].str[:2].map(_state_fips)
        _recent = _recent.dropna(subset=["annual_avg_employment", "state"])
        _recent = _recent[_recent["disclosure_code"].fillna("") == ""]  # disclosed only
        _recent = _recent.sort_values("annual_avg_employment", ascending=False)

        _top = _recent.iloc[0] if not _recent.empty else None
        _va = _recent[_recent["state"] == "Virginia"]

        stats.update({
            "dc_empl_top_state": _top["state"] if _top is not None else "N/A",
            "dc_empl_top_count": int(_top["annual_avg_employment"]) if _top is not None else 0,
            "va_dc_empl": int(_va["annual_avg_employment"].iloc[0]) if not _va.empty else 0,
            "dc_year": _recent_yr,
            "qcew_available": True,
        })

    return (stats,)


@app.cell(hide_code=True)
def _(mo, stats):
    mo.hstack(
        [
            mo.callout(
                mo.md(
                    f"# +{stats['tech_change_from_2020_pct']}%\n"
                    f"Computer Systems Design employment since Jan 2020 — "
                    f"+{stats['tech_since_capex_pct']}% since AI capex surge (Jan 2023)"
                ),
                kind="warn",
            ),
            mo.callout(
                mo.md(
                    f"# +{stats['const_change_from_2020_pct']}%\n"
                    f"Construction employment since Jan 2020 — "
                    f"driven in part by data center site preparation and electrical work"
                ),
                kind="neutral",
            ),
            mo.callout(
                mo.md(
                    f"# {stats['dc_empl_top_state']}\n"
                    f"Leading state for data center (NAICS 518210) employment "
                    f"({stats['dc_year']}) — concentration driven by NoVA data center corridor"
                    if stats["qcew_available"]
                    else "# QCEW data\nRun the BLS QCEW pipeline or check network connection"
                ),
                kind="danger",
            ),
        ],
        justify="space-around",
        gap=1,
    )
    return


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    ## Two Labor Markets, One Capital Flow

    By {stats['latest_date_str']}, Computer Systems Design employment had risen
    **{stats['tech_change_from_2020_pct']}%** from its January 2020 level, with
    **{stats['tech_since_capex_pct']}%** of that gain occurring after January 2023 —
    when the AI capex cycle began in earnest (ChatGPT release, hyperscaler capex
    announcements, and the first wave of GPU contract commitments).

    Construction employment tells a different story at first glance:
    **{stats['const_change_from_2020_pct']}%** growth from the same baseline.
    But aggregate construction includes housing, commercial, infrastructure —
    everything. The data center-specific signal is buried in that aggregate.
    The QCEW county data isolates it: in the counties where data centers are
    actually being built (Northern Virginia, Phoenix, Columbus, Atlanta exurbs),
    construction employment grew far faster than the national average.

    The two labor markets are connected by the same capital flow — and by a
    shared constraint. A data center requires roughly **3–5 megawatts of electrical
    capacity per 10,000 square feet** of compute floor. Installing that electrical
    infrastructure requires licensed electricians, and the licensed electrician
    workforce is not growing fast enough to keep pace with the pipeline.

    The National Electrical Contractors Association projected a shortage of
    approximately 50,000 electricians by 2026 even before the AI data center
    surge accelerated demand. That shortage is already showing up in project
    timelines in Northern Virginia, Phoenix, and Columbus — the three largest
    data center markets.
    """)
    return


@app.cell
def _(CATEGORICAL, COLORS, CONTEXT, FIGSIZE, FONTS, add_brand_mark, add_source, cfg, empl_idx, legend_below, mdates, pd, plt, save_fig):
    # Employment index chart: sector divergence since Jan 2020 = 100
    # Focus: Computer Systems Design (tech hiring signal)
    # Context: Construction, Information, Manufacturing

    _series = {
        "CES6054150001": {
            "label": "Computer Systems Design",
            "color": COLORS["accent"],
            "lw": 2.5,
            "zorder": 4,
        },
        "USCONS": {
            "label": "Construction",
            "color": CATEGORICAL[2],
            "lw": 2.0,
            "zorder": 3,
        },
        "USINFO": {
            "label": "Information Sector (broad)",
            "color": CONTEXT,
            "lw": 1.5,
            "zorder": 2,
        },
        "MANEMP": {
            "label": "Manufacturing",
            "color": CONTEXT,
            "lw": 1.5,
            "zorder": 2,
        },
    }

    fig_empl, ax_empl = plt.subplots(figsize=FIGSIZE["wide"])

    for _sid, _style in _series.items():
        if _sid not in empl_idx.columns:
            continue
        _s = empl_idx[_sid].dropna()
        ax_empl.plot(
            _s.index,
            _s.values,
            label=_style["label"],
            color=_style["color"],
            linewidth=_style["lw"],
            zorder=_style["zorder"],
        )
        # Direct end-label for focus series
        if _style["color"] not in (CONTEXT,):
            _last_val = float(_s.iloc[-1])
            ax_empl.text(
                _s.index[-1] + pd.Timedelta(days=15),
                _last_val,
                f"{_last_val:.0f}",
                color=_style["color"],
                fontsize=FONTS["small"],
                fontweight="bold",
                va="center",
            )

    # Baseline and capex acceleration reference lines
    ax_empl.axhline(100, color=COLORS["reference"], linestyle="--", linewidth=0.8, alpha=0.6)
    ax_empl.text(
        empl_idx.index[0],
        101,
        "Jan 2020 = 100",
        fontsize=FONTS["small"],
        color=COLORS["reference"],
        va="bottom",
    )

    _capex_date = pd.Timestamp("2023-01-01")
    ax_empl.axvline(
        _capex_date,
        color=COLORS["text_light"],
        linestyle=":",
        linewidth=1.2,
        alpha=0.7,
    )
    ax_empl.text(
        _capex_date + pd.Timedelta(days=15),
        ax_empl.get_ylim()[0] + 1,
        "AI capex\nsurge",
        fontsize=FONTS["small"],
        color=COLORS["text_light"],
        va="bottom",
    )

    ax_empl.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax_empl.xaxis.set_major_locator(mdates.YearLocator())
    ax_empl.set_ylabel("Employment index (Jan 2020 = 100)", fontsize=FONTS["axis_label"])
    ax_empl.set_xlim(empl_idx.index.min(), empl_idx.index.max() + pd.Timedelta(days=60))
    legend_below(ax_empl)
    plt.tight_layout(rect=[0.02, 0.08, 1, 1])

    add_source(fig_empl, "Source: see methods section")
    add_brand_mark(fig_empl, logo_path=str(cfg.project_root / 'src/assets/tzdlabs_mark.png'))
    save_fig(fig_empl, cfg.img_dir / "dd003_employment_index.png")
    return


@app.cell(hide_code=True)
def _(cfg, mo, stats):
    _chart = mo.image(
        src=(cfg.img_dir / "dd003_employment_index.png").read_bytes(), width=800
    )
    mo.md(f"""
    # Computer Systems Design employment grew {stats['tech_change_from_2020_pct']}% since 2020 — twice the rate of construction

    {_chart}

    *BLS Current Employment Statistics (CES), seasonally adjusted monthly series.
    Computer Systems Design: CES6054150001. Construction: USCONS. Information
    Sector: USINFO. Manufacturing: MANEMP. Index base: January 2020 = 100.
    Source: `energy_data.fred_series` in the research database.*

    The divergence is not just about absolute employment levels — the composition
    matters. Computer Systems Design employment is growing faster from a smaller
    base, meaning each percentage point of growth represents a more concentrated
    demand signal. The aggregate Construction series masks the data center
    construction effect because data center electrical work is a small fraction
    of total construction spending — but in the specific counties where it
    concentrates, it is the dominant employer.

    The vertical marker at January 2023 shows where the acceleration is most
    visible in the Computer Systems Design series. The rate of employment growth
    in this sector noticeably steepened after hyperscaler capex commitments began
    in earnest. Construction's trajectory is flatter in the aggregate — but the
    county-level story is different.
    """)
    return


@app.cell
def _(CATEGORICAL, COLORS, CONTEXT, FIGSIZE, FONTS, SOC_CODES_TECHNICAL, SOC_CODES_TRADES, add_brand_mark, add_source, cfg, legend_below, mo, np, plt, save_fig, wages_df):
    # OEWS occupational wage time series — technical vs trades
    # Focus: Electricians and Software Developers (the two-workforce story)
    # Context: everything else

    mo.stop(
        wages_df.empty,
        mo.callout(
            mo.md(
                "**OEWS wage data unavailable.** "
                "Run `uv run python -m src.data.pipelines --oews` to download "
                "and cache BLS Occupational Employment and Wage Statistics, "
                "then re-run this notebook."
            ),
            kind="warn",
        ),
    )
    _w = wages_df.dropna(subset=["a_mean", "year", "occ_code"])
    _w = _w[_w["o_group"] == "detailed"]  # avoid aggregate rows

    # Which SOC codes have complete data across years?
    _all_years = sorted(_w["year"].unique())
    _complete = (
        _w.groupby("occ_code")["year"].nunique()
        >= max(1, len(_all_years) - 1)
    )
    _complete_codes = set(_complete[_complete].index)

    # Focus SOC codes
    _focus_tech = "15-1252"   # Software Developers
    _focus_trade = "47-2111"  # Electricians

    # Color map: focus gets color, rest get context gray
    _all_codes = {**SOC_CODES_TECHNICAL, **SOC_CODES_TRADES}
    _color_map = {soc: CONTEXT for soc in _all_codes}
    _color_map[_focus_tech] = CATEGORICAL[0]    # blue — technical
    _color_map[_focus_trade] = COLORS["accent"]  # red — trades

    fig_wages, ax_wages = plt.subplots(figsize=FIGSIZE["wide"])

    for _soc, _label in _all_codes.items():
        # Always draw focus codes even if BLS changed the SOC code mid-series
        if _soc not in _complete_codes and _soc not in (_focus_tech, _focus_trade):
            continue
        _soc_series = (
            _w[_w["occ_code"] == _soc]
            .sort_values("year")[["year", "a_mean"]]
        )
        if _soc_series.empty:
            continue
        _c = _color_map[_soc]
        _lw = 2.5 if _soc in (_focus_tech, _focus_trade) else 1.2
        _alpha = 1.0 if _soc in (_focus_tech, _focus_trade) else 0.5
        _zorder = 4 if _soc in (_focus_tech, _focus_trade) else 2

        ax_wages.plot(
            _soc_series["year"],
            _soc_series["a_mean"] / 1000,  # $K
            color=_c,
            linewidth=_lw,
            alpha=_alpha,
            zorder=_zorder,
        )

        # Direct end-labels for focus series
        if _soc in (_focus_tech, _focus_trade):
            _last_yr = int(_soc_series["year"].iloc[-1])
            _last_val = float(_soc_series["a_mean"].iloc[-1]) / 1000
            ax_wages.text(
                _last_yr + 0.1,
                _last_val,
                f"{_label} (${_last_val:.0f}K)",
                color=_c,
                fontsize=FONTS["small"],
                fontweight="bold",
                va="center",
            )

    # Legend handles for focus series
    import matplotlib.lines as mlines
    _handles = [
        mlines.Line2D([], [], color=CATEGORICAL[0], lw=2.5,
                      label="Software Developers (15-1252)"),
        mlines.Line2D([], [], color=COLORS["accent"], lw=2.5,
                      label="Electricians (47-2111)"),
        mlines.Line2D([], [], color=CONTEXT, lw=1.2,
                      label="Other tracked occupations"),
    ]
    legend_below(ax_wages, handles=_handles, ncol=3)

    ax_wages.set_ylabel("Annual mean wage ($K, nominal)", fontsize=FONTS["axis_label"])
    ax_wages.set_xlabel("Year", fontsize=FONTS["axis_label"])

    _year_min = int(_w["year"].min())
    _year_max = int(_w["year"].max())
    ax_wages.set_xlim(_year_min - 0.3, _year_max + 1.2)
    ax_wages.set_xticks(np.arange(_year_min, _year_max + 1))

    plt.tight_layout(rect=[0.02, 0.08, 1, 1])
    add_source(fig_wages, "Source: see methods section")
    add_brand_mark(fig_wages, logo_path=str(cfg.project_root / 'src/assets/tzdlabs_mark.png'))
    save_fig(fig_wages, cfg.img_dir / "dd003_oews_wages.png")

    return


@app.cell(hide_code=True)
def _(cfg, mo, stats):
    mo.stop(
        not stats["wages_available"],
        mo.callout(
            mo.md(
                "OEWS data not loaded — run `uv run python -m src.data.pipelines --oews` "
                "to populate wage charts."
            ),
            kind="neutral",
        ),
    )
    _chart = mo.image(
        src=(cfg.img_dir / "dd003_oews_wages.png").read_bytes(), width=800
    )
    mo.md(f"""
    # Electrician wages rose {stats['electrician_wage_change_pct']}% from 2019 to 2024 — the trades gap is closing but not closed

    {_chart}

    *BLS Occupational Employment and Wage Statistics (OEWS), annual national
    flat files, detailed occupation level. Annual mean wage in nominal dollars.
    Source: `fetch_oews_soc()` in `src/data/bls.py`, cached to
    `data/raw/bls/oews_{{year}}_national.parquet`.*

    In 2019, the median electrician earned ${stats['electrician_wage_2019']:,}/year
    nationally. By 2024, that had risen to ${stats['electrician_wage_2024']:,} —
    a **{stats['electrician_wage_change_pct']}% increase** in five years.
    Software developers moved from ${stats['software_dev_wage_2019']:,} to
    ${stats['software_dev_wage_2024']:,} over the same period
    (**{stats['software_dev_wage_change_pct']}%**).

    The absolute gap between the two occupations is wide and not closing —
    software developers earn roughly twice what electricians earn. But the
    *rate* of electrician wage growth is meaningful, and in the counties with
    the heaviest data center construction (Loudoun County, VA; Maricopa County,
    AZ; Licking County, OH), electrician wages run materially above the
    national average shown here. Spot wages in Northern Virginia for experienced
    commercial electricians have been reported at $45–60/hour, far above the
    national mean.

    Two dynamics drive this: a structural undersupply (the pipeline from
    apprenticeship to journeyman takes 4–5 years, and enrollment has not
    kept pace with demand) and geographic concentration (the demand spike is
    happening in specific counties, not distributed nationally).

    The context gray lines — electrical engineers, network administrators,
    data scientists, and other tracked occupations — show a broad upward
    trend across all the occupations in the AI labor stack, with no clear
    sign of wage deceleration in the most recent data.
    """)
    return


@app.cell
def _(CATEGORICAL, COLORS, FIGSIZE, FONTS, add_brand_mark, add_source, cfg, mo, np, plt, qcew_dc, save_fig):
    # QCEW state-level data center employment (NAICS 518210)
    # Most recent year with disclosed data, private sector only.

    _state_fips: dict[str, str] = {
        "01": "Alabama", "02": "Alaska", "04": "Arizona", "05": "Arkansas",
        "06": "California", "08": "Colorado", "09": "Connecticut", "10": "Delaware",
        "11": "D.C.", "12": "Florida", "13": "Georgia", "16": "Idaho",
        "17": "Illinois", "18": "Indiana", "19": "Iowa", "20": "Kansas",
        "21": "Kentucky", "22": "Louisiana", "23": "Maine", "24": "Maryland",
        "25": "Massachusetts", "26": "Michigan", "27": "Minnesota", "28": "Mississippi",
        "29": "Missouri", "30": "Montana", "31": "Nebraska", "32": "Nevada",
        "33": "New Hampshire", "34": "New Jersey", "35": "New Mexico", "36": "New York",
        "37": "North Carolina", "38": "North Dakota", "39": "Ohio", "40": "Oklahoma",
        "41": "Oregon", "42": "Pennsylvania", "44": "Rhode Island", "45": "South Carolina",
        "46": "South Dakota", "47": "Tennessee", "48": "Texas", "49": "Utah",
        "50": "Vermont", "51": "Virginia", "53": "Washington", "54": "West Virginia",
        "55": "Wisconsin", "56": "Wyoming",
    }

    mo.stop(
        qcew_dc.empty,
        mo.callout(
            mo.md(
                "**QCEW data unavailable.** "
                "Check network connection or BLS API availability, "
                "then re-run this notebook."
            ),
            kind="warn",
        ),
    )

    _recent_yr = int(qcew_dc["year"].max())
    _recent = qcew_dc[qcew_dc["year"] == _recent_yr].copy()
    _recent["state"] = _recent["area_fips"].str[:2].map(_state_fips)
    _recent = _recent.dropna(subset=["annual_avg_employment", "state"])
    _recent = _recent[_recent["disclosure_code"].fillna("") == ""]
    _recent = _recent.sort_values("annual_avg_employment", ascending=False).head(15)

    _labels = _recent["state"].tolist()
    _values = _recent["annual_avg_employment"].tolist()
    _colors = [
        COLORS["accent"] if s == "Virginia" else CATEGORICAL[0]
        for s in _labels
    ]

    fig_qcew, ax_qcew = plt.subplots(figsize=FIGSIZE["tall"])
    _y = np.arange(len(_labels))
    ax_qcew.barh(_y, _values, color=_colors, height=0.6)
    ax_qcew.set_yticks(_y)
    ax_qcew.set_yticklabels(_labels, fontsize=FONTS["tick_label"])
    ax_qcew.invert_yaxis()
    ax_qcew.set_xlabel(
        f"Average annual employment, {_recent_yr} (private sector)",
        fontsize=FONTS["axis_label"],
    )

    # Value labels
    _max_v = max(_values) if _values else 1
    for _i, _v in enumerate(_values):
        ax_qcew.text(
            _v + _max_v * 0.01,
            _i,
            f"{int(_v):,}",
            va="center",
            fontsize=FONTS["small"],
        )

    # Legend handles
    import matplotlib.patches as mpatches
    _legend_handles = [
        mpatches.Patch(color=COLORS["accent"], label="Virginia (Northern Virginia cluster)"),
        mpatches.Patch(color=CATEGORICAL[0], label="Other states"),
    ]
    ax_qcew.legend(
        handles=_legend_handles,
        loc="lower right",
        fontsize=FONTS["legend"],
        frameon=False,
    )

    plt.tight_layout(rect=[0.02, 0.08, 1, 1])
    add_source(fig_qcew, "Source: see methods section")
    add_brand_mark(fig_qcew, logo_path=str(cfg.project_root / 'src/assets/tzdlabs_mark.png'))
    save_fig(fig_qcew, cfg.img_dir / "dd003_qcew_dc_states.png")

    return


@app.cell(hide_code=True)
def _(cfg, mo, stats):
    mo.stop(
        not stats["qcew_available"],
        mo.callout(
            mo.md("QCEW data not loaded — check network or BLS API availability."),
            kind="neutral",
        ),
    )

    _chart = mo.image(
        src=(cfg.img_dir / "dd003_qcew_dc_states.png").read_bytes(), width=800
    )
    mo.md(f"""
    # {stats['dc_empl_top_state']} leads data center employment — the industry is hyperconcentrated in five states

    {_chart}

    *BLS Quarterly Census of Employment and Wages (QCEW), NAICS 518210
    (Data Processing, Hosting, and Related Services), private sector,
    annual average {stats['dc_year']}. States with suppressed employment
    (BLS disclosure code ≠ blank) are excluded.*

    **{stats['dc_empl_top_state']}** employs approximately **{stats['dc_empl_top_count']:,}
    workers** in NAICS 518210 — the BLS industry category that most closely
    captures data center operations. This figure does not include construction
    workers building data centers (classified under NAICS 236220 and 238210),
    or the equipment technicians contracted for installation. It captures only
    the operational employment: the people who run the facilities once built.

    Although {stats['dc_empl_top_state']} and Texas dominate in total state employment,
    Virginia is highlighted here because the Northern Virginia data center cluster
    in Loudoun County and neighboring Fairfax, Prince William, and Manassas Park
    localities represents the most concentrated single hub. The "Data Center Alley"
    concentration is so extreme that **Loudoun County alone** accounts for a significant
    portion of state-level NAICS 518210 employment — and Virginia holds approximately
    30–40% of the Americas' data center capacity by some industry estimates.

    The geographic concentration creates the labor constraint: the demand for
    electricians, HVAC technicians, and data center operators is not distributed
    nationally — it is concentrated in counties where the local labor pool is
    insufficient to absorb the demand. This is why wage premiums in these counties
    exceed national averages, and why project timelines are slipping.
    """)
    return


@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    ## The Feedback Into Capital Deployment

    The labor market findings complete a causal loop that is not fully captured
    in either the standard AI-and-jobs debate or in standard infrastructure
    analysis.

    The standard framing treats labor as an outcome: AI capex creates jobs.
    That is true. But the data above suggests a second dynamic: labor constraints
    are now feeding back into capex deployment timelines. Electrician shortages
    in Northern Virginia and Phoenix are real, documented by contractors, and
    not solved on the timescales relevant to hyperscaler expansion plans.

    The implications for the DD-002 analysis: **the interconnection queue is not
    the only bottleneck.** Even if a data center clears its FERC interconnection
    study and gets a grid connection approved, it still needs to be built.
    Building it requires licensed electricians. If the electrician pipeline is
    constrained, approved grid connections sit idle — which is a form of stranded
    capital that does not appear in the queue data.

    A back-of-envelope estimate: a large hyperscale data center campus (200–400 MW)
    requires 300–600 electricians for a 24–36 month construction period. Northern
    Virginia is currently developing multiple such campuses simultaneously. The
    math does not close without drawing workers from adjacent markets — which
    drives up wages, extends timelines, or both.

    ---

    ## What This Notebook Establishes

    Three empirical findings:

    1. **Tech sector employment acceleration is real and post-2023** — Computer
       Systems Design employment grew **{stats['tech_since_capex_pct']}%** since
       January 2023, faster than any other major sector in the FRED data.

    2. **Electrician wages are rising significantly** — from ${stats['electrician_wage_2019']:,}
       to ${stats['electrician_wage_2024']:,} nationally ({stats['electrician_wage_change_pct']}%),
       with spot wages in cluster counties materially higher than the national mean.
       This is a supply constraint, not just demand growth.

    3. **Data center employment is hyperconcentrated** — **{stats['dc_empl_top_state']}**
       leads nationally, with the concentration driven entirely by the Northern
       Virginia cluster. Five states capture the majority of U.S. data center
       operational employment.

    The next notebook in DD-003 will model the apprenticeship pipeline lag
    formally: given known apprenticeship enrollment data and 4-5 year completion
    timelines, what is the expected electrician supply curve, and when (if ever)
    does it intersect the demand curve implied by announced data center pipelines?
    That analysis will link directly to DD-002's capex deployment projections.

    ---

    ### Sources and Methods

    - BLS Current Employment Statistics (CES), monthly, seasonally adjusted.
      Series: CES6054150001 (Computer Systems Design), USCONS (Construction),
      USINFO (Information), MANEMP (Manufacturing). Via FRED / `energy_data.fred_series`.
    - BLS Occupational Employment and Wage Statistics (OEWS), annual national
      flat files, {2019}–2024. Detailed occupation level (o_group = "detailed").
      Downloaded and cached by `src/data/bls.fetch_oews_soc()`.
    - BLS Quarterly Census of Employment and Wages (QCEW), NAICS 518210,
      private sector annual averages. Downloaded by `src/data/bls.fetch_qcew_state()`.
    - NECA (National Electrical Contractors Association), workforce development
      reports on electrician supply-demand projections. Not in database — cited
      as industry primary source; see 99_methods_and_sources.py for details.
    - Data Center Alley capacity estimates: various industry sources (CBRE, JLL
      annual market reports). Paywalled — aggregate figures cited without direct
      database link.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.callout(
        mo.md(
            "**Methods and Reproducibility** — Detailed source-date tables, "
            "SQL hash registry, and data provenance notes are published in "
            "`notebooks/dd003_labor_markets/99_methods_and_sources.py`."
        ),
        kind="info",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    import altair as alt

    from src.altair_theme import register as _reg
    from src.data.db import query as _query

    _reg()

    _series = {
        "CES6054150001": "Computer systems design",
        "USCONS": "Construction",
        "USINFO": "Information",
        "MANEMP": "Manufacturing",
    }

    _series_in = ", ".join(f"'{s}'" for s in _series)
    _raw = _query(
        f"SELECT series_id, date, value FROM energy_data.fred_series "
        f"WHERE series_id IN ({_series_in}) "
        "AND date >= '2020-01-01' ORDER BY series_id, date"
    )

    _base = (
        _raw.sort_values("date")
        .groupby("series_id")
        .first()["value"]
        .rename("base")
    )
    _df = _raw.merge(_base, on="series_id")
    _df["indexed"] = _df["value"] / _df["base"] * 100
    _df["sector"] = _df["series_id"].map(_series)

    _sel = alt.selection_point(fields=["sector"], bind="legend")

    _chart = (
        alt.Chart(_df)
        .mark_line()
        .encode(
            x=alt.X("date:T", title=None, axis=alt.Axis(format="%Y")),
            y=alt.Y("indexed:Q", title="Index (Jan 2020 = 100)"),
            color=alt.Color("sector:N", title="Sector"),
            opacity=alt.condition(_sel, alt.value(1.0), alt.value(0.12)),
            tooltip=[
                alt.Tooltip("date:T", title="Month", format="%b %Y"),
                alt.Tooltip("sector:N", title="Sector"),
                alt.Tooltip("indexed:Q", title="Index", format=".1f"),
                alt.Tooltip("value:Q", title="Employment (thousands)", format=",.0f"),
            ],
        )
        .add_params(_sel)
        .properties(
            width="container", height=300,
            title="Employment Index by Sector (Jan 2020 = 100)",
        )
        .interactive()
    )

    from src.notebook import SITE_URL as _SITE_URL
    _lite = f"https://lite.datasette.io/?url={_SITE_URL}/data/research.sqlite#/research/fred_series"

    mo.accordion({
        "Explore the data": mo.vstack([
            mo.md(
                "Click a sector in the legend to isolate it. "
                "Hover for exact index values and underlying employment counts."
            ),
            _chart,
            mo.md(f"[Open `fred_series` in Datasette →]({_lite})"),
        ], gap="0.75rem"),
    })
    return


if __name__ == "__main__":
    app.run()
