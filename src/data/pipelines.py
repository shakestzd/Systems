"""dlt data pipelines for the Systems research project.

Loads data from EIA, LBNL, and FRED into a centralized DuckDB database
at data/research.duckdb. Run with:

    uv run python -m src.data.pipelines          # all sources
    uv run python -m src.data.pipelines --eia     # EIA Form 860 only
    uv run python -m src.data.pipelines --lbnl    # LBNL queue only
    uv run python -m src.data.pipelines --fred    # FRED series only
"""

from __future__ import annotations

import io
import logging
import zipfile
from pathlib import Path

import dlt
import pandas as pd
import requests

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "research.duckdb"
RAW_DIR = PROJECT_ROOT / "data" / "raw"

# ---------------------------------------------------------------------------
# Fuel category mapping for EIA energy source codes
# ---------------------------------------------------------------------------

_FUEL_MAP: dict[str, str] = {
    "SUN": "solar",
    "WND": "wind",
    "NUC": "nuclear",
    "WAT": "hydro",
    "MWH": "battery",
    "BIT": "coal",
    "SUB": "coal",
    "LIG": "coal",
    "RC": "coal",
    "WC": "coal",
    "PC": "petroleum",
    "DFO": "petroleum",
    "RFO": "petroleum",
    "KER": "petroleum",
    "JF": "petroleum",
    "WO": "petroleum",
    "AB": "biomass",
    "MSW": "biomass",
    "OBS": "biomass",
    "WDS": "biomass",
    "OBL": "biomass",
    "SLW": "biomass",
    "BLQ": "biomass",
    "LFG": "biomass",
    "OBG": "biomass",
    "GEO": "geothermal",
    "PUR": "purchased_steam",
}


def _fuel_category(energy_source: str, prime_mover: str) -> str:
    """Map EIA energy source code + prime mover to analysis category."""
    if energy_source == "NG":
        # Distinguish combined cycle from combustion turbine
        if prime_mover in ("CA", "CS", "CT"):
            return "gas_cc"
        return "gas_ct"
    return _FUEL_MAP.get(energy_source, "other")


# ---------------------------------------------------------------------------
# EIA Form 860 — Generator-level data
# ---------------------------------------------------------------------------

EIA860_URL = "https://www.eia.gov/electricity/data/eia860/xls/eia8602024.zip"


@dlt.resource(write_disposition="replace")
def eia860_generators(url: str = EIA860_URL) -> dlt.sources.DltResource:
    """Download and parse EIA Form 860 generator data.

    Yields one record per generator with plant location, capacity,
    fuel type, and operating year.
    """
    logger.info("Downloading EIA Form 860 from %s", url)
    resp = requests.get(
        url,
        timeout=120,
        headers={"User-Agent": "Mozilla/5.0 (Systems Research Project)"},
    )
    resp.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        # Find the generator schedule file
        gen_files = [n for n in zf.namelist() if "3_1_Generator" in n and n.endswith(".xlsx")]
        plant_files = [n for n in zf.namelist() if "2___Plant" in n and n.endswith(".xlsx")]

        if not gen_files:
            msg = f"No generator file found in ZIP. Contents: {zf.namelist()}"
            raise FileNotFoundError(msg)

        # Parse generator data (skip header rows)
        with zf.open(gen_files[0]) as f:
            gen_df = pd.read_excel(f, skiprows=1)

        # Parse plant data for state/location info
        plant_state: dict[int, str] = {}
        if plant_files:
            with zf.open(plant_files[0]) as f:
                plant_df = pd.read_excel(f, skiprows=1)
            if "Plant Code" in plant_df.columns and "State" in plant_df.columns:
                plant_state = dict(
                    zip(plant_df["Plant Code"], plant_df["State"], strict=False)
                )

    # Yield clean records
    for _, row in gen_df.iterrows():
        raw_plant_id = row.get("Plant Code")
        if pd.isna(raw_plant_id):
            continue
        plant_id = int(raw_plant_id)

        energy_source = str(row.get("Energy Source 1", "")).strip()
        prime_mover = str(row.get("Prime Mover", "")).strip()

        capacity = row.get("Nameplate Capacity (MW)")
        try:
            capacity = float(capacity) if pd.notna(capacity) else 0.0
        except (TypeError, ValueError):
            capacity = 0.0

        raw_year = row.get("Operating Year")
        try:
            operating_year = int(float(raw_year)) if pd.notna(raw_year) else None
        except (TypeError, ValueError):
            operating_year = None

        yield {
            "plant_id": plant_id,
            "generator_id": str(row.get("Generator ID", "")),
            "state": plant_state.get(plant_id, str(row.get("State", ""))),
            "nameplate_capacity_mw": capacity,
            "energy_source_code": energy_source,
            "prime_mover": prime_mover,
            "fuel_category": _fuel_category(energy_source, prime_mover),
            "operating_year": operating_year,
            "status": str(row.get("Status", "")),
            "entity_name": str(row.get("Entity Name", "")),
            "sector_name": str(row.get("Sector Name", "")),
        }


# ---------------------------------------------------------------------------
# LBNL Interconnection Queue
# ---------------------------------------------------------------------------

# The LBNL download URL changes per edition; fall back to local file
LBNL_FALLBACK = RAW_DIR / "lbnl_queues.xlsx"


@dlt.resource(write_disposition="replace")
def lbnl_queue(file_path: str | Path | None = None) -> dlt.sources.DltResource:
    """Parse LBNL interconnection queue data from Excel workbook.

    If no file_path is provided, looks for the file at data/raw/lbnl_queues.xlsx.
    Download the latest from https://emp.lbl.gov/queues manually.
    """
    path = Path(file_path) if file_path else LBNL_FALLBACK

    if not path.exists():
        logger.warning(
            "LBNL queue file not found at %s. "
            "Download from https://emp.lbl.gov/queues and save to data/raw/lbnl_queues.xlsx",
            path,
        )
        return

    logger.info("Parsing LBNL queue data from %s", path)

    # The workbook has multiple sheets; the main data is typically in
    # a sheet containing project-level records
    xl = pd.ExcelFile(path)
    # Try common sheet names for the project-level data
    data_sheet = None
    for name in xl.sheet_names:
        lower = name.lower()
        if "data" in lower or "project" in lower or "active" in lower:
            data_sheet = name
            break
    if data_sheet is None:
        # Fall back to first sheet
        data_sheet = xl.sheet_names[0]

    df = pd.read_excel(xl, sheet_name=data_sheet)

    # Normalize column names (LBNL format varies between editions)
    col_map = {}
    for c in df.columns:
        cl = str(c).lower().strip()
        if "capacity" in cl and "mw" in cl:
            col_map[c] = "capacity_mw"
        elif "queue" in cl and "date" in cl:
            col_map[c] = "queue_date"
        elif cl in ("state", "s"):
            col_map[c] = "state"
        elif "type" in cl and ("clean" in cl or "fuel" in cl or "resource" in cl):
            col_map[c] = "fuel_type"
        elif "status" in cl:
            col_map[c] = "status"
        elif "region" in cl or "entity" in cl or "iso" in cl or "rto" in cl:
            col_map[c] = "region"
        elif "project" in cl and "name" in cl:
            col_map[c] = "project_name"
        elif cl in ("ia status", "interconnection agreement status"):
            col_map[c] = "ia_status"

    df = df.rename(columns=col_map)

    for _, row in df.iterrows():
        capacity = row.get("capacity_mw")
        try:
            capacity = float(capacity)
        except (TypeError, ValueError):
            capacity = None

        queue_date = row.get("queue_date")
        if pd.notna(queue_date):
            queue_date = pd.Timestamp(queue_date).isoformat()
        else:
            queue_date = None

        yield {
            "project_name": str(row.get("project_name", "")),
            "state": str(row.get("state", "")),
            "queue_date": queue_date,
            "capacity_mw": capacity,
            "fuel_type": str(row.get("fuel_type", "")),
            "status": str(row.get("status", "")),
            "region": str(row.get("region", "")),
        }


# ---------------------------------------------------------------------------
# FRED Economic Time Series
# ---------------------------------------------------------------------------

FRED_CSV_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"

# Series relevant to the research
FRED_SERIES = {
    "WPU0543": "Electric power PPI",
    "DHHNGSP": "Henry Hub natural gas spot price",
    "PCU335311335311": "Transformer PPI",
    "CPIENGSL": "Energy CPI",
    "APU000072610": "Average electricity price (cents/kWh)",
}


@dlt.resource(write_disposition="merge", primary_key=["series_id", "date"])
def fred_series(
    series_ids: dict[str, str] | None = None,
) -> dlt.sources.DltResource:
    """Fetch FRED time series via CSV download (no API key needed).

    Uses merge write_disposition so subsequent runs only add new dates.
    Uses urllib (same approach as src/data/fred.py) to avoid SSL issues.
    """
    import urllib.request

    ids = series_ids or FRED_SERIES

    for series_id, description in ids.items():
        url = FRED_CSV_URL.format(series_id=series_id)
        logger.info("Fetching FRED series %s (%s)", series_id, description)

        try:
            resp = urllib.request.urlopen(url)  # noqa: S310
            df = pd.read_csv(
                io.BytesIO(resp.read()),
                parse_dates=["observation_date"],
            )
        except Exception:
            logger.warning("Failed to fetch FRED series %s", series_id, exc_info=True)
            continue

        df = df.rename(columns={"observation_date": "date"})
        value_col = [c for c in df.columns if c != "date"][0]
        df = df.rename(columns={value_col: "value"})
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df = df.dropna(subset=["value"])

        for _, row in df.iterrows():
            yield {
                "series_id": series_id,
                "description": description,
                "date": row["date"].isoformat(),
                "value": float(row["value"]),
            }


# ---------------------------------------------------------------------------
# Pipeline Runner
# ---------------------------------------------------------------------------


def _make_pipeline() -> dlt.Pipeline:
    """Create the dlt pipeline targeting data/research.duckdb."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return dlt.pipeline(
        pipeline_name="systems_research",
        destination=dlt.destinations.duckdb(str(DB_PATH)),
        dataset_name="energy_data",
    )


def run_eia() -> None:
    """Run EIA Form 860 pipeline."""
    pipeline = _make_pipeline()
    info = pipeline.run(eia860_generators())
    logger.info("EIA 860: %s", info)


def run_lbnl() -> None:
    """Run LBNL interconnection queue pipeline."""
    pipeline = _make_pipeline()
    info = pipeline.run(lbnl_queue())
    logger.info("LBNL queue: %s", info)


def run_fred() -> None:
    """Run FRED time series pipeline."""
    pipeline = _make_pipeline()
    info = pipeline.run(fred_series())
    logger.info("FRED series: %s", info)


def run_all() -> None:
    """Run all pipelines."""
    run_fred()
    run_eia()
    run_lbnl()


if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    parser = argparse.ArgumentParser(description="Run data pipelines")
    parser.add_argument("--eia", action="store_true", help="EIA Form 860 only")
    parser.add_argument("--lbnl", action="store_true", help="LBNL queue only")
    parser.add_argument("--fred", action="store_true", help="FRED series only")
    args = parser.parse_args()

    if not any([args.eia, args.lbnl, args.fred]):
        run_all()
    else:
        if args.fred:
            run_fred()
        if args.eia:
            run_eia()
        if args.lbnl:
            run_lbnl()
