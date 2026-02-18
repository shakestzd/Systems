import marimo

__generated_with = "0.19.11"
app = marimo.App(width="medium", app_title="DD-002 Methods & Sources")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
    # DD-002 Methods & Reproducibility
    ## Grid Modernization: Who Benefits?

    Companion notebook for:
    `notebooks/dd002_grid_modernization/02_who_benefits.py`
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
        "lbnl_queue_summary_latest_year": "SELECT MAX(year) AS as_of FROM energy_data.lbnl_queue_summary",
        "dd002_queue_region_backlog_latest_year": "SELECT MAX(year) AS as_of FROM energy_data.dd002_queue_region_backlog",
        "dd002_cost_allocation_latest_year": "SELECT MAX(year) AS as_of FROM energy_data.dd002_cost_allocation",
        "dd002_policy_events_latest_date": "SELECT MAX(CAST(event_date AS DATE)) AS as_of FROM energy_data.dd002_policy_events",
        "dd002_projection_priors_latest_source_date": (
            "SELECT MAX(COALESCE(TRY_CAST(source_date AS DATE), TRY_CAST(source_date || '-01' AS DATE))) "
            "AS as_of FROM energy_data.dd002_projection_priors"
        ),
        "eia860_generators_latest_operating_year": "SELECT MAX(operating_year) AS as_of FROM energy_data.eia860_generators",
        "hyperscaler_capex_latest_date": "SELECT MAX(CAST(date AS DATE)) AS as_of FROM energy_data.hyperscaler_capex",
        "fred_retail_price_latest_date": (
            "SELECT MAX(CAST(date AS DATE)) AS as_of FROM energy_data.fred_series "
            "WHERE series_id = 'APU000072610'"
        ),
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
    methods_freshness = pd.DataFrame(freshness_rows)

    source_keys = [
        "queue_median_years",
        "va_bill_annual_2040",
        "va_capacity_share_americas_pct",
    ]
    _source_key_sql = ", ".join(f"'{k}'" for k in source_keys)
    source_citations = query(
        f"""
        SELECT key, source_name, source_date, source_detail, url
        FROM energy_data.source_citations
        WHERE key IN ({_source_key_sql})
        ORDER BY source_date DESC, key
        """
    )

    queue_region_sources = query(
        """
        SELECT DISTINCT
            'dd002_queue_region_backlog' AS table_name,
            source AS source_name,
            NULL AS source_date,
            source_detail,
            NULL AS url
        FROM energy_data.dd002_queue_region_backlog
        WHERE source IS NOT NULL
        """
    )
    cost_alloc_sources = query(
        """
        SELECT DISTINCT
            'dd002_cost_allocation' AS table_name,
            source AS source_name,
            NULL AS source_date,
            source_detail,
            NULL AS url
        FROM energy_data.dd002_cost_allocation
        WHERE source IS NOT NULL
        """
    )
    prior_sources = query(
        """
        SELECT DISTINCT
            'dd002_projection_priors' AS table_name,
            source AS source_name,
            COALESCE(TRY_CAST(source_date AS DATE), TRY_CAST(source_date || '-01' AS DATE)) AS source_date,
            source_detail,
            NULL AS url
        FROM energy_data.dd002_projection_priors
        WHERE source IS NOT NULL
        """
    )
    policy_sources = query(
        """
        SELECT DISTINCT
            'dd002_policy_events' AS table_name,
            source_name,
            CAST(event_date AS DATE) AS source_date,
            description AS source_detail,
            source_url AS url
        FROM energy_data.dd002_policy_events
        WHERE source_name IS NOT NULL
        """
    )
    table_sources = (
        pd.concat(
            [queue_region_sources, cost_alloc_sources, prior_sources, policy_sources],
            ignore_index=True,
        )
        .sort_values(["table_name", "source_name", "source_date"], ascending=[True, True, False])
        .reset_index(drop=True)
    )

    return methods_freshness, query_registry, source_citations, table_sources


@app.cell(hide_code=True)
def _(methods_freshness, mo, query_registry, source_citations, table_sources):
    mo.vstack(
        [
            mo.md("## Data Freshness"),
            mo.as_html(methods_freshness),
            mo.md("## DD-002 Pipeline Table Sources"),
            mo.as_html(table_sources),
            mo.md("## Source Citations Used in Narrative Claims"),
            mo.as_html(source_citations),
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
