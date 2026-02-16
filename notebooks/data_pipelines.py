import marimo

__generated_with = "0.19.11"
app = marimo.App(width="medium", app_title="Data Pipeline Dashboard")


@app.cell
def _():
    import sys

    import marimo as mo

    sys.path.insert(0, str(mo.notebook_dir().parent))

    import pandas as pd

    from src.data.db import query, tables
    return mo, pd, query, tables


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
    # Data Pipeline Dashboard

    Interactive management of all research data pipelines. Each pipeline
    loads data into `data/research.duckdb` via dlt. Use the run buttons
    below to refresh individual sources, or check the status table for
    current freshness.

    **CLI equivalent:** `uv run python -m src.data.pipelines`
    """
    )
    return


@app.cell(hide_code=True)
def _(mo, pd, query, tables):
    # Database status overview
    try:
        _tbl = tables()
        _status_rows = []
        for _, row in _tbl.iterrows():
            schema = row["table_schema"]
            name = row["table_name"]
            try:
                count_df = query(f'SELECT count(*) as n FROM "{schema}"."{name}"')
                n = int(count_df["n"].iloc[0])
            except Exception:
                n = "?"
            _status_rows.append({"Schema": schema, "Table": name, "Rows": n})
        _status_df = pd.DataFrame(_status_rows)
        _status_display = mo.ui.table(_status_df, label="Database Tables")
    except Exception as e:
        _status_display = mo.callout(
            mo.md(f"**Database not found or empty.** Run a pipeline first.\n\n`{e}`"),
            kind="warn",
        )
    mo.md(
        f"""
    ## Database Status

    {_status_display}
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("---\n## Pipeline Controls")
    return


# ---------------------------------------------------------------------------
# FRED Pipeline
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    fred_btn = mo.ui.run_button(label="Run FRED Pipeline")
    mo.md(
        f"""
    ### FRED Economic Time Series

    Downloads employment and energy price series from FRED (no API key).

    | Series | Description |
    | :--- | :--- |
    | `USCONS` | Construction employment |
    | `CES6054150001` | Computer Systems Design employment |
    | `CES4422000001` | Utilities employment |
    | `USINFO` | Information sector employment |
    | `MANEMP` | Manufacturing employment |
    | `UNRATE` | Unemployment rate |
    | `WPU0543`, `DHHNGSP` | Energy prices |

    {fred_btn}
    """
    )
    return (fred_btn,)


@app.cell
def _(fred_btn, mo, query):
    mo.stop(not fred_btn.value, mo.md("*Click Run to fetch FRED series.*"))

    from src.data.pipelines import run_fred

    run_fred()

    _df = query(
        "SELECT series_id, description, count(*) as observations, "
        "min(date) as earliest, max(date) as latest "
        "FROM energy_data.fred_series GROUP BY series_id, description "
        "ORDER BY series_id"
    )
    mo.md(
        f"""
    **FRED loaded successfully.**

    {mo.ui.table(_df, label="FRED Series")}
    """
    )
    return


# ---------------------------------------------------------------------------
# EIA Pipeline
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    eia_btn = mo.ui.run_button(label="Run EIA Pipeline")
    mo.md(
        f"""
    ### EIA Form 860 — Generator Data

    Downloads all U.S. power plant generator data including capacity,
    fuel type, location, and operating year.

    Source: [EIA Form 860](https://www.eia.gov/electricity/data/eia860/)

    {eia_btn}
    """
    )
    return (eia_btn,)


@app.cell
def _(eia_btn, mo, query):
    mo.stop(not eia_btn.value, mo.md("*Click Run to fetch EIA data.*"))

    from src.data.pipelines import run_eia

    run_eia()

    _df = query(
        "SELECT fuel_category, count(*) as generators, "
        "round(sum(nameplate_capacity_mw), 0) as total_mw "
        "FROM energy_data.eia860_generators "
        "GROUP BY fuel_category ORDER BY total_mw DESC"
    )
    mo.md(
        f"""
    **EIA loaded successfully.**

    {mo.ui.table(_df, label="Generators by Fuel Category")}
    """
    )
    return


# ---------------------------------------------------------------------------
# BLS QCEW Pipeline
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    bls_btn = mo.ui.run_button(label="Run BLS QCEW Pipeline")
    mo.md(
        f"""
    ### BLS QCEW — County-Level Employment

    Downloads county-level employment data from the Quarterly Census
    of Employment and Wages for key NAICS codes:

    - `518210` — Data Processing, Hosting
    - `236220` — Commercial Building Construction
    - `2211` — Electric Power
    - `5415` — Computer Systems Design
    - `334` — Computer/Electronic Manufacturing

    Years: 2016–2024 | Source: [BLS QCEW](https://data.bls.gov/cew/)

    {bls_btn}
    """
    )
    return (bls_btn,)


@app.cell
def _(bls_btn, mo, query):
    mo.stop(not bls_btn.value, mo.md("*Click Run to fetch BLS QCEW data.*"))

    from src.data.pipelines import run_bls

    run_bls()

    _df = query(
        "SELECT industry_code, industry_description, "
        "count(DISTINCT area_fips) as counties, "
        "count(DISTINCT year) as years, "
        "sum(annual_avg_employment) as total_employment "
        "FROM energy_data.bls_qcew "
        "GROUP BY industry_code, industry_description "
        "ORDER BY total_employment DESC"
    )
    mo.md(
        f"""
    **BLS QCEW loaded successfully.**

    {mo.ui.table(_df, label="QCEW by Industry")}
    """
    )
    return


# ---------------------------------------------------------------------------
# Census CBP Pipeline
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    census_btn = mo.ui.run_button(label="Run Census CBP Pipeline")
    mo.md(
        f"""
    ### Census County Business Patterns

    County-level establishment counts, employment, and payroll
    from the Census Bureau API (no key required).

    Same NAICS codes as BLS QCEW for cross-validation.

    Years: 2016–2022 | Source: [Census CBP](https://www.census.gov/programs-surveys/cbp.html)

    {census_btn}
    """
    )
    return (census_btn,)


@app.cell
def _(census_btn, mo, query):
    mo.stop(not census_btn.value, mo.md("*Click Run to fetch Census CBP data.*"))

    from src.data.pipelines import run_census

    run_census()

    _df = query(
        "SELECT naics_code, naics_description, "
        "count(DISTINCT (state_fips || county_fips)) as counties, "
        "count(DISTINCT year) as years, "
        "sum(employment) as total_employment "
        "FROM energy_data.census_cbp "
        "GROUP BY naics_code, naics_description "
        "ORDER BY total_employment DESC"
    )
    mo.md(
        f"""
    **Census CBP loaded successfully.**

    {mo.ui.table(_df, label="CBP by NAICS Code")}
    """
    )
    return


# ---------------------------------------------------------------------------
# Hyperscaler CapEx Pipeline
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    capex_btn = mo.ui.run_button(label="Run CapEx Pipeline")
    mo.md(
        f"""
    ### Hyperscaler Capital Expenditure

    Quarterly capex from yfinance (trailing ~5 quarters) merged with
    historical reference CSV. Covers: MSFT, GOOGL, AMZN, META, NVDA, ORCL.

    {capex_btn}
    """
    )
    return (capex_btn,)


@app.cell
def _(capex_btn, mo, query):
    mo.stop(not capex_btn.value, mo.md("*Click Run to fetch CapEx data.*"))

    from src.data.pipelines import run_capex

    run_capex()

    _df = query(
        "SELECT ticker, count(*) as quarters, "
        "round(sum(capex_bn), 1) as total_capex_bn, "
        "min(date) as earliest, max(date) as latest "
        "FROM energy_data.hyperscaler_capex "
        "GROUP BY ticker ORDER BY total_capex_bn DESC"
    )
    mo.md(
        f"""
    **CapEx loaded successfully.**

    {mo.ui.table(_df, label="CapEx by Company")}
    """
    )
    return


# ---------------------------------------------------------------------------
# LBNL Queue Pipeline
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    lbnl_btn = mo.ui.run_button(label="Run LBNL Pipeline")
    mo.md(
        f"""
    ### LBNL Interconnection Queue

    Parsed from manually downloaded Excel workbook.
    Source: [LBNL Queues](https://emp.lbl.gov/queues)

    Requires `data/raw/lbnl_queues.xlsx` to be present.

    {lbnl_btn}
    """
    )
    return (lbnl_btn,)


@app.cell
def _(lbnl_btn, mo, query):
    mo.stop(not lbnl_btn.value, mo.md("*Click Run to parse LBNL queue data.*"))

    from src.data.pipelines import run_lbnl

    run_lbnl()

    try:
        _df = query(
            "SELECT fuel_type, count(*) as projects, "
            "round(sum(capacity_mw), 0) as total_mw "
            "FROM energy_data.lbnl_queue "
            "WHERE fuel_type != '' "
            "GROUP BY fuel_type ORDER BY total_mw DESC "
            "LIMIT 10"
        )
        _display = mo.ui.table(_df, label="Queue by Fuel Type (Top 10)")
    except Exception:
        _display = mo.callout(mo.md("LBNL table not found — is the Excel file present?"), kind="warn")

    mo.md(f"**LBNL pipeline complete.**\n\n{_display}")
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
