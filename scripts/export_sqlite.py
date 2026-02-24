#!/usr/bin/env python3
"""Export curated DuckDB tables to SQLite for Datasette Lite.

Produces ``_site/data/research.sqlite`` — a self-contained SQLite database
hosted on GitHub Pages and browsable via Datasette Lite without a server.

Only analytically useful tables are exported. Large county-level BLS/Census
tables (bls_qcew, bls_laus, census_cbp) are omitted to keep the file size
reasonable for browser-based loading (~30–60 MB expected).

Usage::

    uv run python scripts/export_sqlite.py           # writes to _site/data/
    uv run python scripts/export_sqlite.py --dry-run # list tables only
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "research.duckdb"
SITE_DATA_DIR = PROJECT_ROOT / "_site" / "data"

# ---------------------------------------------------------------------------
# Curated table list with human-readable descriptions
# ---------------------------------------------------------------------------

TABLES: list[dict] = [
    # Hyperscaler financials
    {
        "name": "hyperscaler_capex",
        "label": "Hyperscaler Capital Expenditure",
        "description": (
            "Quarterly capital expenditure (billions USD) for Microsoft, Google, "
            "Amazon, Meta, Nvidia, and Oracle. Source: SEC 10-Q/10-K via yfinance "
            "and manual historical CSV."
        ),
        "case_study": "DD-001",
    },
    {
        "name": "capex_guidance",
        "label": "CapEx Guidance (Forward-Looking)",
        "description": (
            "Management guidance for 2025–2027 capital expenditure by company. "
            "Source: Earnings calls and investor presentations."
        ),
        "case_study": "DD-001",
    },
    {
        "name": "cloud_revenue",
        "label": "Cloud Revenue (Quarterly)",
        "description": (
            "Quarterly cloud segment revenue (billions USD) with year-over-year "
            "growth for AWS, Google Cloud, and Azure. Source: SEC filings."
        ),
        "case_study": "DD-001",
    },
    {
        "name": "hyperscaler_ocf",
        "label": "Operating Cash Flow",
        "description": (
            "Annual operating cash flow (billions USD) for hyperscalers. "
            "Source: SEC 10-K filings."
        ),
        "case_study": "DD-001",
    },
    {
        "name": "mag7_market_caps",
        "label": "Market Capitalizations",
        "description": (
            "Point-in-time market capitalization snapshots (trillions USD) "
            "for the Magnificent Seven. Source: public market data."
        ),
        "case_study": "DD-001",
    },
    {
        "name": "edgar_xbrl_facts",
        "label": "SEC EDGAR XBRL Facts",
        "description": (
            "XBRL-tagged financial concepts (PP&E, CapEx, depreciation) from "
            "10-K/10-Q filings for Meta, Amazon, and Google. Source: SEC EDGAR API."
        ),
        "case_study": "DD-001",
    },
    {
        "name": "edgar_ppe_schedule",
        "label": "PP&E Schedule",
        "description": (
            "Property, plant & equipment by category (equipment, buildings, land, "
            "construction in progress) from annual 10-K filings."
        ),
        "case_study": "DD-001",
    },
    # Grid / interconnection
    {
        "name": "lbnl_queue",
        "label": "LBNL Interconnection Queue",
        "description": (
            "Project-level US electricity interconnection queue data. Each row is "
            "a generation or storage project seeking grid connection. "
            "Source: LBNL Queued Up dataset."
        ),
        "case_study": "DD-002",
    },
    {
        "name": "lbnl_queue_summary",
        "label": "LBNL Queue Summary (Annual)",
        "description": (
            "Annual aggregate interconnection queue capacity (GW) by fuel type "
            "and completion/withdrawal rates. Source: LBNL Queued Up reports."
        ),
        "case_study": "DD-002",
    },
    {
        "name": "dd002_queue_region_backlog",
        "label": "Queue Backlog by ISO/RTO Region",
        "description": (
            "Annual interconnection queue backlog (GW) by grid region (PJM, ERCOT, "
            "WECC, MISO, etc.), with major data center region flag. "
            "Source: LBNL Queued Up, manual compilation."
        ),
        "case_study": "DD-002",
    },
    {
        "name": "dd002_cost_allocation",
        "label": "Network Upgrade Cost Allocation",
        "description": (
            "Interconnection network upgrade costs (billions USD) by region and "
            "cost category, including the share socialized to ratepayers. "
            "Source: FERC Order 2023 filings, RTO annual reports."
        ),
        "case_study": "DD-002",
    },
    {
        "name": "dd002_hyperscaler_region_weights",
        "label": "Hyperscaler Regional CapEx Weights",
        "description": (
            "Estimated allocation of each hyperscaler's data center CapEx "
            "across ISO/RTO regions. Source: data center location databases, "
            "company real estate filings."
        ),
        "case_study": "DD-002",
    },
    {
        "name": "dd002_projection_priors",
        "label": "Grid Projection Priors",
        "description": (
            "Parameter priors for the DD-002 grid feedback model: base, low, and "
            "high scenario values for key assumptions (load growth, IRA effect, etc.)."
        ),
        "case_study": "DD-002",
    },
    {
        "name": "dd002_policy_events",
        "label": "Regulatory Policy Events",
        "description": (
            "Key regulatory events affecting AI grid integration: FERC orders, "
            "state PUC filings, tariff proceedings. Source: FERC docket system, "
            "state PUC websites."
        ),
        "case_study": "DD-002",
    },
    # Generation fleet
    {
        "name": "eia860_generators",
        "label": "EIA Form 860 Generators",
        "description": (
            "US utility-scale generator fleet: plant, state, capacity (MW), fuel "
            "type, prime mover, operating year. Source: EIA Form 860 Annual Survey."
        ),
        "case_study": "DD-002",
    },
    # FRED economic series
    {
        "name": "fred_series",
        "label": "FRED Economic Time Series",
        "description": (
            "16 Federal Reserve economic data series relevant to AI infrastructure: "
            "electricity PPI, transformer PPI, Henry Hub gas price, construction "
            "employment, private fixed investment, and more. Source: FRED API."
        ),
        "case_study": "DD-001, DD-002",
    },
    # Labor
    {
        "name": "oews_wages",
        "label": "BLS OEWS Occupational Wages",
        "description": (
            "Annual occupational employment and wage statistics (2019–2024) for 15 "
            "occupations relevant to AI infrastructure: software developers, "
            "electricians, data scientists, line installers, and others. "
            "Source: BLS Occupational Employment and Wage Statistics."
        ),
        "case_study": "DD-003",
    },
    # Utility regulation
    {
        "name": "dd004_pjm_zone_demand",
        "label": "PJM Zone Demand Requests",
        "description": (
            "PJM Load Analysis Subcommittee demand request data by zone (2025–2046). "
            "Source: PJM Load Analysis Subcommittee reports."
        ),
        "case_study": "DD-004",
    },
    {
        "name": "dd004_iurc_cases",
        "label": "Indiana Utility Regulatory Cases (IURC)",
        "description": (
            "Indiana Utility Regulatory Commission case records related to data "
            "center load additions and grid upgrade cost allocation. "
            "Source: IURC final orders (OCR-extracted)."
        ),
        "case_study": "DD-004",
    },
    # Cross-cutting
    {
        "name": "bea_nipa_investment",
        "label": "BEA NIPA Private Fixed Investment",
        "description": (
            "BEA Table 5.3.5: Private Fixed Investment by Type (billions USD). "
            "Structures, equipment, and intellectual property by industry category. "
            "Source: Bureau of Economic Analysis."
        ),
        "case_study": "DD-001",
    },
    {
        "name": "source_citations",
        "label": "Source Citations Registry",
        "description": (
            "Every numeric constant cited in the analysis: value, unit, source name, "
            "date, detail, and URL. This table is the single source of truth for "
            "all manually cited figures."
        ),
        "case_study": "All",
    },
]

TABLE_NAMES = [t["name"] for t in TABLES]

# ---------------------------------------------------------------------------
# Export logic
# ---------------------------------------------------------------------------


def export(
    duckdb_path: Path = DB_PATH,
    output_dir: Path = SITE_DATA_DIR,
) -> dict[str, int]:
    """Export curated tables from DuckDB to SQLite.

    Parameters
    ----------
    duckdb_path:
        Path to the source DuckDB database.
    output_dir:
        Directory where ``research.sqlite`` and ``metadata.json`` are written.

    Returns
    -------
    dict[str, int]
        Mapping of table name → row count for each exported table.
    """
    try:
        import duckdb
    except ImportError as e:
        raise ImportError("duckdb is required: uv pip install duckdb") from e

    output_dir.mkdir(parents=True, exist_ok=True)
    sqlite_path = output_dir / "research.sqlite"
    sqlite_path.unlink(missing_ok=True)

    row_counts: dict[str, int] = {}

    with duckdb.connect(str(duckdb_path), read_only=True) as con:
        with sqlite3.connect(str(sqlite_path)) as lite:
            lite.execute("PRAGMA journal_mode=WAL")
            lite.execute("PRAGMA synchronous=NORMAL")

            for table in TABLES:
                name = table["name"]
                try:
                    df = con.execute(
                        f"SELECT * FROM energy_data.{name}"
                    ).fetchdf()
                    df.to_sql(name, lite, if_exists="replace", index=False)
                    row_counts[name] = len(df)
                    print(f"  OK    {name} ({len(df):,} rows)")
                except Exception as exc:
                    print(f"  SKIP  {name}: {exc}")

            # Compact the file
            lite.execute("VACUUM")

    size_mb = sqlite_path.stat().st_size / 1e6
    print(f"  Total: research.sqlite ({size_mb:.1f} MB)")

    _write_metadata(output_dir, row_counts)
    return row_counts


def _write_metadata(output_dir: Path, row_counts: dict[str, int]) -> None:
    """Write a Datasette metadata.json describing the database and tables."""
    tables_meta = {}
    for table in TABLES:
        name = table["name"]
        tables_meta[name] = {
            "title": table["label"],
            "description": table["description"],
            "label_column": _guess_label_column(name),
        }

    metadata = {
        "title": "The Physical Economy of AI — Research Data",
        "description": (
            "Every dataset used in the 'Where AI Capital Lands' research project. "
            "Browse, query, and download the underlying data behind each case study."
        ),
        "source": "Shakes-tzd/Systems on GitHub",
        "source_url": "https://github.com/Shakes-tzd/Systems",
        "license": "ODbL",
        "license_url": "https://opendatacommons.org/licenses/odbl/",
        "databases": {
            "research": {
                "tables": tables_meta,
            }
        },
    }

    meta_path = output_dir / "metadata.json"
    meta_path.write_text(json.dumps(metadata, indent=2))
    print("  OK    metadata.json")


def _guess_label_column(table_name: str) -> str | None:
    """Return a reasonable label column for Datasette row pages."""
    candidates = {
        "hyperscaler_capex": "ticker",
        "cloud_revenue": "segment",
        "oews_wages": "occ_title",
        "lbnl_queue": "project_name",
        "eia860_generators": "entity_name",
        "fred_series": "series_id",
        "source_citations": "key",
        "dd002_policy_events": "event_name",
        "dd004_iurc_cases": "case_title",
    }
    return candidates.get(table_name)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> int:
    dry_run = "--dry-run" in sys.argv

    if dry_run:
        print("Tables to export:")
        for t in TABLES:
            print(f"  {t['name']:<45} {t['label']}")
        return 0

    if not DB_PATH.exists():
        print(f"Database not found: {DB_PATH}")
        print("Run the data pipelines first: uv run python -m src.data.pipelines")
        return 1

    print(f"Exporting to {SITE_DATA_DIR / 'research.sqlite'} ...")
    export()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
