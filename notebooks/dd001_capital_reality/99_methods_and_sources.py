import marimo

__generated_with = "0.19.11"
app = marimo.App(width="medium", app_title="DD-001 Methods & Sources")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
    # DD-001 Methods & Reproducibility
    ## CapEx vs Physical Reality

    Companion notebook for:
    `notebooks/dd001_capital_reality/01_capex_vs_reality.py`
    """
    )
    return


@app.cell
def _():
    import hashlib
    import sys

    import marimo as mo
    import pandas as pd

    sys.path.insert(0, str(mo.notebook_dir().parent.parent))

    from src.data.db import query

    return hashlib, mo, pd, query


@app.cell
def _(hashlib, pd, query):
    sql_methods = {
        "capex_latest_date": "SELECT MAX(CAST(date AS DATE)) AS as_of FROM energy_data.hyperscaler_capex",
        "market_cap_latest_date": "SELECT MAX(CAST(date AS DATE)) AS as_of FROM energy_data.mag7_market_caps",
        "queue_summary_latest_year": "SELECT MAX(year) AS as_of FROM energy_data.lbnl_queue_summary",
        "eia_generators_latest_year": "SELECT MAX(operating_year) AS as_of FROM energy_data.eia860_generators",
        "fred_pnfi_latest_date": (
            "SELECT MAX(CAST(date AS DATE)) AS as_of FROM energy_data.fred_series "
            "WHERE series_id = 'PNFI'"
        ),
        "bea_nipa_latest_year": "SELECT MAX(year) AS as_of FROM energy_data.bea_nipa_investment",
        "edgar_ppe_latest_fiscal_year": "SELECT MAX(fiscal_year) AS as_of FROM energy_data.edgar_ppe_schedule",
        "cloud_revenue_latest_quarter": "SELECT MAX(quarter) AS as_of FROM energy_data.cloud_revenue",
        "hyperscaler_ocf_latest_period": "SELECT MAX(period) AS as_of FROM energy_data.hyperscaler_ocf",
    }

    def _sql_hash(sql: str) -> str:
        return hashlib.sha256(" ".join(sql.split()).encode("utf-8")).hexdigest()[:12]

    query_registry = pd.DataFrame(
        [
            {"metric": metric, "sql_hash": _sql_hash(sql), "sql": " ".join(sql.split())}
            for metric, sql in sql_methods.items()
        ]
    )

    freshness_rows = []
    for metric, sql in sql_methods.items():
        val = query(sql).iloc[0, 0]
        freshness_rows.append({"dataset_metric": metric, "as_of": str(val)})
    data_freshness = pd.DataFrame(freshness_rows)

    used_source_keys = [
        "queue_cohort_2000_2005_pct",
        "queue_cohort_2006_2010_pct",
        "queue_cohort_2011_2015_pct",
        "queue_cohort_2016_2020_pct",
        "meta_2026g_low",
        "meta_2026g_high",
        "meta_2023_guidance_low",
        "meta_2023_guidance_high",
        "msft_fy25_initial_g",
        "msft_fy25_revised_g",
        "meta_headcount_2022",
        "meta_headcount_2023",
        "sequoia_rev_target_bn",
        "gcp_backlog_bn",
        "gcp_backlog_growth_pct",
        "vc_ai_2024_bn",
        "ai_capex_share_pct",
        "hist_capex_ocf_avg_pct",
        "analyst_const_pct_low",
        "dc_construction_low_bn",
        "dc_construction_high_bn",
        "cloud_rev_2026_low",
        "cloud_rev_2026_high",
        "nvda_deepseek_loss_bn",
        "stargate_announced_bn",
        "stargate_initial_bn",
    ]
    _key_sql = ", ".join(f"'{k}'" for k in used_source_keys)
    source_dates = query(
        f"""
        SELECT key, source_name, source_date, source_detail, url
        FROM energy_data.source_citations
        WHERE key IN ({_key_sql})
        ORDER BY source_date DESC, key
        """
    )

    return data_freshness, query_registry, source_dates


@app.cell(hide_code=True)
def _(data_freshness, mo, query_registry, source_dates):
    mo.vstack(
        [
            mo.md("## Data Freshness"),
            mo.as_html(data_freshness),
            mo.md("## Sources (Exact Source Dates)"),
            mo.as_html(source_dates),
            mo.md("## SQL Registry (hashes)"),
            mo.as_html(query_registry[["metric", "sql_hash"]]),
        ]
    )
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
