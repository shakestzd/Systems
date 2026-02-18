"""dlt data pipelines for the Systems research project.

Loads data from EIA, LBNL, FRED, BLS, SEC EDGAR, BEA, and reference CSVs
into a centralized DuckDB database at data/research.duckdb. Run with:

    uv run python -m src.data.pipelines          # all sources
    uv run python -m src.data.pipelines --eia     # EIA Form 860 only
    uv run python -m src.data.pipelines --lbnl    # LBNL queue only
    uv run python -m src.data.pipelines --fred    # FRED series only
    uv run python -m src.data.pipelines --bls     # BLS QCEW only
    uv run python -m src.data.pipelines --oews    # BLS OEWS wage data only
    uv run python -m src.data.pipelines --edgar   # SEC EDGAR only
    uv run python -m src.data.pipelines --ref     # Reference + citations

BLS data access functions (for direct notebook use) are in src/data/bls.py.
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
        # CA/CS = combined cycle steam/combustion parts.
        # CT = simple-cycle combustion turbine (intentionally classified as gas_ct,
        # not gas_cc — corrected from earlier misclassification per EIA definitions).
        if prime_mover in ("CA", "CS"):
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

        # Parse plant data for state/location info (including lat/lon)
        plant_info: dict[int, dict] = {}
        if plant_files:
            with zf.open(plant_files[0]) as f:
                plant_df = pd.read_excel(f, skiprows=1)
            for _, prow in plant_df.iterrows():
                pc = prow.get("Plant Code")
                if pd.notna(pc):
                    lat = prow.get("Latitude")
                    lon = prow.get("Longitude")
                    try:
                        lat_f = float(lat) if pd.notna(lat) else None
                    except (TypeError, ValueError):
                        lat_f = None
                    try:
                        lon_f = float(lon) if pd.notna(lon) else None
                    except (TypeError, ValueError):
                        lon_f = None
                    plant_info[int(pc)] = {
                        "state": str(prow.get("State", "")),
                        "latitude": lat_f,
                        "longitude": lon_f,
                    }

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

        info = plant_info.get(plant_id, {})
        yield {
            "plant_id": plant_id,
            "generator_id": str(row.get("Generator ID", "")),
            "state": info.get("state", str(row.get("State", ""))),
            "latitude": info.get("latitude"),
            "longitude": info.get("longitude"),
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
    # Energy prices (DD-002)
    "WPU0543": "Electric power PPI",
    "DHHNGSP": "Henry Hub natural gas spot price",
    "PCU335311335311": "Transformer PPI",
    "CPIENGSL": "Energy CPI",
    "APU000072610": "Average electricity price (cents/kWh)",
    # Macro (DD-001)
    "PNFI": "Private Nonresidential Fixed Investment",
    # Employment (DD-003)
    "USCONS": "All Employees, Construction",
    "CES4422000001": "All Employees, Utilities",
    "CES6054150001": "All Employees, Computer Systems Design",
    "USINFO": "All Employees, Information Sector",
    "CES6054000001": "All Employees, Professional/Scientific/Tech",
    "MANEMP": "All Employees, Manufacturing",
    "UNRATE": "Unemployment Rate",
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
# BLS QCEW — County-level employment by industry
# ---------------------------------------------------------------------------

QCEW_API_URL = "https://data.bls.gov/cew/data/api/{year}/a/industry/{naics}.csv"

# NAICS codes for DD-003 labor analysis
QCEW_NAICS = {
    "518210": "Data Processing, Hosting, Related Services",
    "236220": "Commercial/Institutional Building Construction",
    "2211": "Electric Power Generation/Transmission/Distribution",
    "5415": "Computer Systems Design and Related Services",
    "334": "Computer and Electronic Product Manufacturing",
}


@dlt.resource(write_disposition="replace")
def bls_qcew(
    years: list[int] | None = None,
    naics_codes: dict[str, str] | None = None,
) -> dlt.sources.DltResource:
    """Download BLS QCEW annual averages for selected NAICS codes.

    Uses the BLS QCEW API (per-industry endpoint) to fetch county-level
    employment data. No API key required.
    """
    years = years or list(range(2016, 2025))
    codes = naics_codes or QCEW_NAICS

    for naics, description in codes.items():
        for year in years:
            url = QCEW_API_URL.format(year=year, naics=naics)
            logger.info("Fetching QCEW %s (%s) for %d", naics, description, year)

            try:
                resp = requests.get(url, timeout=60)
                resp.raise_for_status()
                df = pd.read_csv(io.StringIO(resp.text))
            except Exception:
                logger.warning(
                    "Failed to fetch QCEW %s for %d", naics, year, exc_info=True
                )
                continue

            # Filter to private ownership (own_code=5) and county level
            if "own_code" in df.columns:
                df = df[df["own_code"] == 5]

            for _, row in df.iterrows():
                area_fips = str(row.get("area_fips", "")).strip()
                # Skip state-level and national aggregates
                if area_fips.endswith("000") or len(area_fips) != 5:
                    continue

                avg_empl = row.get("annual_avg_emplvl")
                avg_wage = row.get("annual_avg_wkly_wage")
                establishments = row.get("annual_avg_estabs")

                try:
                    avg_empl = int(avg_empl) if pd.notna(avg_empl) else None
                except (TypeError, ValueError):
                    avg_empl = None
                try:
                    avg_wage = int(avg_wage) if pd.notna(avg_wage) else None
                except (TypeError, ValueError):
                    avg_wage = None
                try:
                    establishments = int(establishments) if pd.notna(establishments) else None
                except (TypeError, ValueError):
                    establishments = None

                yield {
                    "year": year,
                    "area_fips": area_fips,
                    "state_fips": area_fips[:2],
                    "county_fips": area_fips[2:],
                    "industry_code": naics,
                    "industry_description": description,
                    "annual_avg_employment": avg_empl,
                    "annual_avg_weekly_wage": avg_wage,
                    "annual_avg_establishments": establishments,
                    "disclosure_code": str(row.get("disclosure_code", "")),
                }


# ---------------------------------------------------------------------------
# BLS OEWS — Occupational Employment and Wage Statistics
# ---------------------------------------------------------------------------


@dlt.resource(write_disposition="replace")
def oews_wages(
    soc_codes: dict[str, str] | None = None,
    years: list[int] | None = None,
) -> dlt.sources.DltResource:
    """Load BLS OEWS wage data for key occupations (DD-003 labor analysis).

    Downloads and caches annual OEWS national flat files via src.data.bls.
    No API key required. Files are cached to data/raw/bls/ after first download.

    Covers both the AI/technical stack (software developers, data scientists,
    electrical engineers) and the construction trades (electricians, line
    installers) that the public discourse systematically undercounts.
    """
    from src.data.bls import SOC_CODES_DD003, fetch_oews_soc

    codes = soc_codes or SOC_CODES_DD003
    years_list = years or list(range(2019, 2025))

    logger.info("OEWS: fetching %d SOC codes for %d years", len(codes), len(years_list))
    df = fetch_oews_soc(codes, years_list)

    if df.empty:
        logger.warning("OEWS: no data returned")
        return

    for _, row in df.iterrows():
        record: dict = {
            "year": int(row["year"]),
            "occ_code": str(row.get("occ_code", "")),
            "occ_title": str(row.get("occ_title", "")),
            "label": str(row.get("label", "")),
            "o_group": str(row.get("o_group", "")),
        }
        for col in ["tot_emp", "h_mean", "a_mean", "h_median", "a_median", "a_pct25", "a_pct75"]:
            val = row.get(col)
            record[col] = float(val) if pd.notna(val) else None
        yield record


# ---------------------------------------------------------------------------
# Census County Business Patterns
# ---------------------------------------------------------------------------

CENSUS_CBP_URL = "https://api.census.gov/data/{year}/cbp"

CBP_NAICS = {
    "518210": "Data Processing, Hosting",
    "236220": "Commercial Building Construction",
    "2211": "Electric Power",
    "5415": "Computer Systems Design",
}


@dlt.resource(write_disposition="replace")
def census_cbp(
    years: list[int] | None = None,
    naics_codes: dict[str, str] | None = None,
) -> dlt.sources.DltResource:
    """Fetch Census County Business Patterns for selected NAICS codes.

    Uses the Census Bureau API (no key required for basic access).
    Returns county-level establishment, employment, and payroll data.
    """
    years = years or list(range(2016, 2023))
    codes = naics_codes or CBP_NAICS

    for naics, description in codes.items():
        for year in years:
            url = CENSUS_CBP_URL.format(year=year)
            params = {
                "get": "NAICS2017,ESTAB,EMP,PAYANN",
                "for": "county:*",
                "NAICS2017": naics,
            }
            logger.info("Fetching Census CBP %s (%s) for %d", naics, description, year)

            try:
                resp = requests.get(url, params=params, timeout=60)
                resp.raise_for_status()
                data = resp.json()
            except Exception:
                logger.warning(
                    "Failed to fetch Census CBP %s for %d", naics, year, exc_info=True
                )
                continue

            if not data or len(data) < 2:
                continue

            headers = data[0]
            for row in data[1:]:
                record = dict(zip(headers, row))

                estab = record.get("ESTAB")
                emp = record.get("EMP")
                payann = record.get("PAYANN")

                try:
                    estab = int(estab) if estab else None
                except (TypeError, ValueError):
                    estab = None
                try:
                    emp = int(emp) if emp else None
                except (TypeError, ValueError):
                    emp = None
                try:
                    payann = int(payann) if payann else None
                except (TypeError, ValueError):
                    payann = None

                yield {
                    "year": year,
                    "state_fips": record.get("state", ""),
                    "county_fips": record.get("county", ""),
                    "naics_code": naics,
                    "naics_description": description,
                    "establishments": estab,
                    "employment": emp,
                    "annual_payroll_1000": payann,
                }


# ---------------------------------------------------------------------------
# Hyperscaler CapEx (via yfinance + historical CSV)
# ---------------------------------------------------------------------------

HYPERSCALER_TICKERS = ["MSFT", "GOOGL", "AMZN", "META", "NVDA", "ORCL"]


@dlt.resource(write_disposition="replace")
def hyperscaler_capex(
    tickers: list[str] | None = None,
) -> dlt.sources.DltResource:
    """Pull quarterly capital expenditure from yfinance + historical CSV.

    Merges live yfinance data (~5 trailing quarters) with a manually
    maintained historical CSV for earlier quarters.
    Values are positive (absolute spend in $B).
    """
    import yfinance as yf

    tickers = tickers or HYPERSCALER_TICKERS

    # Load historical reference CSV if available
    hist_path = PROJECT_ROOT / "data" / "external" / "hyperscaler_capex_historical.csv"
    hist_rows: dict[tuple[str, str], dict] = {}
    if hist_path.exists():
        hist_df = pd.read_csv(hist_path, parse_dates=["date"])
        for _, row in hist_df.iterrows():
            key = (str(row["ticker"]), pd.Timestamp(row["date"]).isoformat()[:10])
            hist_rows[key] = {
                "ticker": str(row["ticker"]),
                "date": pd.Timestamp(row["date"]).isoformat()[:10],
                "capex_bn": float(row["capex_bn"]),
            }
        logger.info("Loaded %d historical capex rows", len(hist_rows))

    # Fetch live data from yfinance
    for ticker in tickers:
        try:
            t = yf.Ticker(ticker)
            cf = t.quarterly_cashflow
            if cf is None or cf.empty:
                logger.warning("No cash flow data for %s", ticker)
                continue
            if "Capital Expenditure" not in cf.index:
                logger.warning("No CapEx line for %s", ticker)
                continue

            capex_series = cf.loc["Capital Expenditure"]
            for date, value in capex_series.items():
                if pd.notna(value):
                    key = (ticker, pd.Timestamp(date).isoformat()[:10])
                    hist_rows[key] = {
                        "ticker": ticker,
                        "date": pd.Timestamp(date).isoformat()[:10],
                        "capex_bn": round(abs(float(value)) / 1e9, 3),
                    }
        except Exception:
            logger.warning("Failed to fetch CapEx for %s", ticker, exc_info=True)

    yield from sorted(hist_rows.values(), key=lambda r: (r["date"], r["ticker"]))


# ---------------------------------------------------------------------------
# Capex Guidance (forward-looking management estimates)
# ---------------------------------------------------------------------------


@dlt.resource(write_disposition="replace")
def capex_guidance() -> dlt.sources.DltResource:
    """Load forward-looking capex guidance from CSV.

    These are management estimates from earnings calls, not audited actuals.
    Kept separate from hyperscaler_capex (which is historical/actual).
    Source: data/external/hyperscaler_capex_guidance.csv
    """
    path = PROJECT_ROOT / "data" / "external" / "hyperscaler_capex_guidance.csv"
    if not path.exists():
        logger.warning("Capex guidance CSV not found at %s", path)
        return

    df = pd.read_csv(path)
    for _, row in df.iterrows():
        yield {
            "ticker": str(row["ticker"]),
            "year": int(row["year"]),
            "capex_bn": float(row["capex_bn"]),
            "source": str(row.get("source", "")),
        }


# ---------------------------------------------------------------------------
# Market Capitalizations (reference snapshots)
# ---------------------------------------------------------------------------


@dlt.resource(write_disposition="replace")
def mag7_market_caps() -> dlt.sources.DltResource:
    """Load market cap reference snapshots from CSV.

    Point-in-time market capitalizations for valuation-vs-capex analysis.
    Source: data/external/mag7_market_caps.csv
    """
    path = PROJECT_ROOT / "data" / "external" / "mag7_market_caps.csv"
    if not path.exists():
        logger.warning("Market cap CSV not found at %s", path)
        return

    df = pd.read_csv(path)
    for _, row in df.iterrows():
        yield {
            "ticker": str(row["ticker"]),
            "company": str(row["company"]),
            "date": str(row["date"]),
            "market_cap_t": float(row["market_cap_t"]),
            "source": str(row.get("source", "")),
        }


# ---------------------------------------------------------------------------
# Cloud Revenue (quarterly, from CSV)
# ---------------------------------------------------------------------------


@dlt.resource(write_disposition="replace")
def cloud_revenue() -> dlt.sources.DltResource:
    """Load quarterly cloud revenue from CSV.

    Tracks AWS, Microsoft Intelligent Cloud, and Google Cloud Platform
    revenue for the capex-vs-revenue analysis (DD-001 Layer 2).
    Source: data/external/cloud_revenue_quarterly.csv
    """
    path = PROJECT_ROOT / "data" / "external" / "cloud_revenue_quarterly.csv"
    if not path.exists():
        logger.warning("Cloud revenue CSV not found at %s", path)
        return

    df = pd.read_csv(path)
    for _, row in df.iterrows():
        yield {
            "ticker": str(row["ticker"]),
            "segment": str(row["segment"]),
            "quarter": str(row["quarter"]),
            "revenue_bn": float(row["revenue_bn"]),
            "yoy_growth_pct": float(row.get("yoy_growth_pct", 0)),
            "source": str(row.get("source", "")),
        }


@dlt.resource(write_disposition="replace")
def hyperscaler_ocf() -> dlt.sources.DltResource:
    """Load hyperscaler trailing twelve-month operating cash flow from CSV.

    Used to compute capex/OCF ratios for the guidance reliability analysis.
    Source: data/external/hyperscaler_ocf.csv (from SEC 10-Q filings).
    """
    path = PROJECT_ROOT / "data" / "external" / "hyperscaler_ocf.csv"
    if not path.exists():
        logger.warning("Hyperscaler OCF CSV not found at %s", path)
        return

    df = pd.read_csv(path)
    for _, row in df.iterrows():
        yield {
            "ticker": str(row["ticker"]),
            "period": str(row["period"]),
            "ocf_bn": float(row["ocf_bn"]),
            "source": str(row.get("source", "")),
        }


@dlt.resource(write_disposition="replace")
def lbnl_queue_summary() -> dlt.sources.DltResource:
    """Load LBNL interconnection queue summary data from CSV.

    Year-end queue capacity by fuel type, plus completion/withdrawal rates.
    Source: data/external/lbnl_queue_summary.csv
    Data: Rand et al., LBNL "Queued Up" editions (emp.lbl.gov/queues).
    """
    path = PROJECT_ROOT / "data" / "external" / "lbnl_queue_summary.csv"
    if not path.exists():
        logger.warning("LBNL queue summary CSV not found at %s", path)
        return

    df = pd.read_csv(path)
    for _, row in df.iterrows():
        rec: dict = {
            "year": int(row["year"]),
            "generation_gw": float(row["generation_gw"]),
            "storage_gw": float(row["storage_gw"]),
            "total_gw": float(row["total_gw"]),
            "source": str(row.get("source", "")),
        }
        # Optional fuel-type breakdown columns
        for col in ("solar_gw", "wind_gw", "gas_gw", "nuclear_gw", "other_gw",
                     "completion_pct", "withdrawal_pct"):
            val = row.get(col)
            if pd.notna(val):
                rec[col] = float(val)
        yield rec


@dlt.resource(write_disposition="replace")
def dd002_queue_region_backlog() -> dlt.sources.DltResource:
    """Load DD-002 queue backlog splits by region.

    Source: data/external/dd002_queue_region_backlog.csv
    """
    path = PROJECT_ROOT / "data" / "external" / "dd002_queue_region_backlog.csv"
    if not path.exists():
        logger.warning("DD-002 queue region CSV not found at %s", path)
        return

    df = pd.read_csv(path)
    for _, row in df.iterrows():
        yield {
            "year": int(row["year"]),
            "region": str(row["region"]),
            "queue_gw": float(row["queue_gw"]),
            "is_major_dc_region": str(row.get("is_major_dc_region", "false")).lower() == "true",
            "source": str(row.get("source", "")),
            "source_detail": str(row.get("source_detail", "")),
        }


@dlt.resource(write_disposition="replace")
def dd002_cost_allocation() -> dlt.sources.DltResource:
    """Load DD-002 cost-allocation records.

    Source: data/external/dd002_cost_allocation.csv
    """
    path = PROJECT_ROOT / "data" / "external" / "dd002_cost_allocation.csv"
    if not path.exists():
        logger.warning("DD-002 cost allocation CSV not found at %s", path)
        return

    df = pd.read_csv(path)
    for _, row in df.iterrows():
        yield {
            "year": int(row["year"]),
            "region": str(row["region"]),
            "cost_category": str(row["cost_category"]),
            "cost_bn": float(row["cost_bn"]),
            "sort_order": int(row.get("sort_order", 0)),
            "is_total": str(row.get("is_total", "false")).lower() == "true",
            "project_count": int(row.get("project_count", 0)),
            "socialized_pct": float(row.get("socialized_pct", 0)),
            "is_estimate": str(row.get("is_estimate", "false")).lower() == "true",
            "source": str(row.get("source", "")),
            "source_detail": str(row.get("source_detail", "")),
        }


@dlt.resource(write_disposition="replace")
def dd002_policy_events() -> dlt.sources.DltResource:
    """Load DD-002 policy and regulatory event timeline.

    Source: data/external/dd002_policy_events.csv
    """
    path = PROJECT_ROOT / "data" / "external" / "dd002_policy_events.csv"
    if not path.exists():
        logger.warning("DD-002 policy events CSV not found at %s", path)
        return

    df = pd.read_csv(path)
    for _, row in df.iterrows():
        yield {
            "event_date": str(row["event_date"]),
            "jurisdiction": str(row.get("jurisdiction", "")),
            "docket": str(row.get("docket", "")),
            "event_name": str(row.get("event_name", "")),
            "event_type": str(row.get("event_type", "")),
            "status": str(row.get("status", "")),
            "effective_or_due_date": str(row.get("effective_or_due_date", "")),
            "description": str(row.get("description", "")),
            "source_name": str(row.get("source_name", "")),
            "source_url": str(row.get("source_url", "")),
        }


@dlt.resource(write_disposition="replace")
def dd002_hyperscaler_region_weights() -> dlt.sources.DltResource:
    """Load DD-002 hyperscaler capex allocation weights by grid region.

    Source: data/external/dd002_hyperscaler_region_weights.csv
    """
    path = PROJECT_ROOT / "data" / "external" / "dd002_hyperscaler_region_weights.csv"
    if not path.exists():
        logger.warning("DD-002 hyperscaler region weights CSV not found at %s", path)
        return

    df = pd.read_csv(path)
    for _, row in df.iterrows():
        yield {
            "ticker": str(row["ticker"]),
            "region": str(row["region"]),
            "allocation_weight": float(row["allocation_weight"]),
            "source": str(row.get("source", "")),
            "source_detail": str(row.get("source_detail", "")),
        }


@dlt.resource(write_disposition="replace")
def dd002_projection_priors() -> dlt.sources.DltResource:
    """Load DD-002 probabilistic projection priors.

    Source: data/external/dd002_projection_priors.csv
    """
    path = PROJECT_ROOT / "data" / "external" / "dd002_projection_priors.csv"
    if not path.exists():
        logger.warning("DD-002 projection priors CSV not found at %s", path)
        return

    df = pd.read_csv(path)
    for _, row in df.iterrows():
        yield {
            "parameter": str(row["parameter"]),
            "base_value": float(row["base_value"]),
            "low_value": float(row["low_value"]),
            "high_value": float(row["high_value"]),
            "units": str(row.get("units", "")),
            "source": str(row.get("source", "")),
            "source_date": str(row.get("source_date", "")),
            "source_detail": str(row.get("source_detail", "")),
        }


# ---------------------------------------------------------------------------
# SEC EDGAR XBRL & PP&E Extraction
# ---------------------------------------------------------------------------


@dlt.resource(write_disposition="replace")
def edgar_xbrl_facts(
    tickers: list[str] | None = None,
) -> dlt.sources.DltResource:
    """Extract structured XBRL financial facts from SEC EDGAR.

    Fetches PP&E totals, capex, and depreciation from the Company Concept API.
    No API key required. Rate-limited to 10 req/sec per SEC policy.
    """
    from src.data.edgar import (
        COMPANIES,
        XBRL_CONCEPTS,
        extract_annual_facts,
        get_company_concept,
    )

    tickers = tickers or ["META", "AMZN", "GOOGL"]

    for ticker in tickers:
        if ticker not in COMPANIES:
            logger.warning("Unknown ticker %s — skipping", ticker)
            continue
        cik, company_name = COMPANIES[ticker]
        for tag, taxonomy in XBRL_CONCEPTS.items():
            try:
                data = get_company_concept(cik, taxonomy, tag)
            except Exception:
                logger.warning("Failed to fetch %s/%s for %s", taxonomy, tag, ticker)
                continue
            for fact in extract_annual_facts(data, ticker):
                yield {
                    "ticker": ticker,
                    "company": company_name,
                    "concept": fact["concept"],
                    "fiscal_year": fact["fiscal_year"],
                    "value": fact["value"],
                    "unit": fact["unit"],
                    "filed": fact["filed"],
                    "form": fact["form"],
                }


@dlt.resource(write_disposition="replace")
def edgar_ppe_schedule(
    tickers: list[str] | None = None,
    fiscal_years: list[int] | None = None,
) -> dlt.sources.DltResource:
    """Extract PP&E decomposition from 10-K property schedule notes.

    Downloads raw 10-K HTML filings, caches in data/raw/edgar/,
    and parses the property schedule table using BeautifulSoup.
    """
    from src.data.edgar import (
        COMPANIES,
        download_10k_html,
        extract_ppe_schedule,
    )

    tickers = tickers or ["META", "AMZN", "GOOGL"]
    fiscal_years = fiscal_years or [2024]
    save_dir = RAW_DIR / "edgar"

    for ticker in tickers:
        if ticker not in COMPANIES:
            logger.warning("Unknown ticker %s — skipping", ticker)
            continue
        cik, _name = COMPANIES[ticker]
        for fy in fiscal_years:
            html_path = download_10k_html(ticker, cik, fy, save_dir)
            if html_path is None:
                continue
            yield from extract_ppe_schedule(html_path, ticker, fy)


# ---------------------------------------------------------------------------
# Source Citations Registry
# ---------------------------------------------------------------------------


@dlt.resource(write_disposition="replace")
def source_citations() -> dlt.sources.DltResource:
    """Load cited constants from the structured source document registry.

    Every numerical constant used in notebooks that isn't computed from
    database data gets a row here with full provenance: source name, date,
    URL, and paywall status.

    Source: data/external/source_citations.csv
    """
    path = PROJECT_ROOT / "data" / "external" / "source_citations.csv"
    if not path.exists():
        logger.warning("Source citations CSV not found at %s", path)
        return

    df = pd.read_csv(path)
    for _, row in df.iterrows():
        yield {
            "key": str(row["key"]),
            "value": float(row["value"]),
            "unit": str(row.get("unit", "")),
            "source_type": str(row.get("source_type", "")),
            "source_name": str(row.get("source_name", "")),
            "source_date": str(row.get("source_date", "")),
            "source_detail": str(row.get("source_detail", "")),
            "url": str(row.get("url", "")),
            "paywalled": str(row.get("paywalled", "false")).lower() == "true",
        }


# ---------------------------------------------------------------------------
# BEA NIPA Investment Data
# ---------------------------------------------------------------------------


@dlt.resource(write_disposition="replace")
def bea_nipa_investment() -> dlt.sources.DltResource:
    """Load BEA NIPA private fixed investment by type.

    Falls back to data/external/bea_nipa_reference.csv if BEA_API_KEY
    is not set. The CSV approach is the default for zero-budget operation.

    Source: BEA NIPA Table 5.3.5 "Private Fixed Investment by Type"
    """
    path = PROJECT_ROOT / "data" / "external" / "bea_nipa_reference.csv"
    if not path.exists():
        logger.warning("BEA NIPA reference CSV not found at %s", path)
        return

    df = pd.read_csv(path)
    for _, row in df.iterrows():
        yield {
            "year": int(row["year"]),
            "line_number": int(row.get("line_number", 0)),
            "line_description": str(row["line_description"]),
            "value_bn": float(row["value_bn"]),
            "table_name": str(row.get("table_name", "T50305")),
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


def run_bls() -> None:
    """Run BLS QCEW pipeline."""
    pipeline = _make_pipeline()
    info = pipeline.run(bls_qcew())
    logger.info("BLS QCEW: %s", info)


def run_oews() -> None:
    """Run BLS OEWS occupational wage pipeline."""
    pipeline = _make_pipeline()
    info = pipeline.run(oews_wages())
    logger.info("BLS OEWS: %s", info)


def run_census() -> None:
    """Run Census CBP pipeline."""
    pipeline = _make_pipeline()
    info = pipeline.run(census_cbp())
    logger.info("Census CBP: %s", info)


def run_capex() -> None:
    """Run hyperscaler CapEx pipeline."""
    pipeline = _make_pipeline()
    info = pipeline.run(hyperscaler_capex())
    logger.info("Hyperscaler CapEx: %s", info)


def run_reference() -> None:
    """Run reference data pipelines (guidance, market caps, cloud revenue, LBNL queue)."""
    pipeline = _make_pipeline()
    info = pipeline.run(capex_guidance())
    logger.info("Capex guidance: %s", info)
    info = pipeline.run(mag7_market_caps())
    logger.info("Market caps: %s", info)
    info = pipeline.run(cloud_revenue())
    logger.info("Cloud revenue: %s", info)
    info = pipeline.run(lbnl_queue_summary())
    logger.info("LBNL queue summary: %s", info)
    info = pipeline.run(dd002_queue_region_backlog())
    logger.info("DD-002 queue region backlog: %s", info)
    info = pipeline.run(dd002_cost_allocation())
    logger.info("DD-002 cost allocation: %s", info)
    info = pipeline.run(dd002_policy_events())
    logger.info("DD-002 policy events: %s", info)
    info = pipeline.run(dd002_hyperscaler_region_weights())
    logger.info("DD-002 hyperscaler region weights: %s", info)
    info = pipeline.run(dd002_projection_priors())
    logger.info("DD-002 projection priors: %s", info)
    info = pipeline.run(hyperscaler_ocf())
    logger.info("Hyperscaler OCF: %s", info)
    info = pipeline.run(source_citations())
    logger.info("Source citations: %s", info)
    info = pipeline.run(bea_nipa_investment())
    logger.info("BEA NIPA: %s", info)


def run_edgar() -> None:
    """Run SEC EDGAR pipeline (XBRL facts + PP&E schedule extraction)."""
    pipeline = _make_pipeline()
    info = pipeline.run(edgar_xbrl_facts())
    logger.info("EDGAR XBRL facts: %s", info)
    info = pipeline.run(edgar_ppe_schedule())
    logger.info("EDGAR PP&E schedule: %s", info)


def run_all() -> None:
    """Run all pipelines."""
    run_fred()
    run_eia()
    run_lbnl()
    run_bls()
    run_oews()
    run_census()
    run_capex()
    run_reference()
    run_edgar()


if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    parser = argparse.ArgumentParser(description="Run data pipelines")
    parser.add_argument("--eia", action="store_true", help="EIA Form 860 only")
    parser.add_argument("--lbnl", action="store_true", help="LBNL queue only")
    parser.add_argument("--fred", action="store_true", help="FRED series only")
    parser.add_argument("--bls", action="store_true", help="BLS QCEW only")
    parser.add_argument("--oews", action="store_true", help="BLS OEWS wage data only")
    parser.add_argument("--census", action="store_true", help="Census CBP only")
    parser.add_argument("--capex", action="store_true", help="Hyperscaler CapEx only")
    parser.add_argument("--ref", action="store_true", help="Reference data only")
    parser.add_argument("--edgar", action="store_true", help="SEC EDGAR only")
    args = parser.parse_args()

    flags = [
        args.eia, args.lbnl, args.fred, args.bls, args.oews,
        args.census, args.capex, args.ref, args.edgar,
    ]
    if not any(flags):
        run_all()
    else:
        if args.fred:
            run_fred()
        if args.eia:
            run_eia()
        if args.lbnl:
            run_lbnl()
        if args.bls:
            run_bls()
        if args.oews:
            run_oews()
        if args.census:
            run_census()
        if args.capex:
            run_capex()
        if args.ref:
            run_reference()
        if args.edgar:
            run_edgar()
