"""BLS public data access — OEWS and QCEW.

Two access modes:
- Direct download functions (no API key) for use in notebooks
- Constants imported by pipelines.py for dlt pipeline defaults

Key data sources:
- OEWS: https://www.bls.gov/oes/tables.htm (annual flat files, ZIP → Excel/CSV)
- QCEW API: https://data.bls.gov/cew/data/api/ (county/state employment by industry)

OEWS flat files are large (~20–30 MB/year). They are cached to
data/raw/bls/oews_{year}_national.parquet after first download.
"""

from __future__ import annotations

import io
import logging
import zipfile
from pathlib import Path

import pandas as pd
import requests

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "bls"

_HEADERS = {"User-Agent": "Systems Research Project systems-research@proton.me"}

# ---------------------------------------------------------------------------
# SOC codes — DD-003 labor analysis
# ---------------------------------------------------------------------------

# Canonical reference for DD-003. Key: SOC code, value: short label.
# Split into two groups: AI/technical stack and construction trades.
# The trades group is systematically underweighted in public discourse.

SOC_CODES_TECHNICAL: dict[str, str] = {
    "15-2051": "Data Scientists",
    "15-1211": "Computer and Information Research Scientists",
    "15-1252": "Software Developers",
    "15-1243": "Database Architects",
    "15-1244": "Network and Computer Systems Administrators",
    "15-1231": "Computer Network Support Specialists",
    "17-2071": "Electrical Engineers",
    "17-2072": "Electronics Engineers",
    "17-3023": "Electrical and Electronic Engineering Technologists",
}

SOC_CODES_TRADES: dict[str, str] = {
    "47-2111": "Electricians",
    "47-1011": "First-Line Supervisors of Construction Trades Workers",
    "49-9051": "Electrical Power-Line Installers and Repairers",
    "47-2152": "Plumbers, Pipefitters, and Steamfitters",
    "47-2061": "Construction Laborers",
    "49-9071": "Maintenance and Repair Workers, General",
}

# Combined dict — used as default for fetch_oews_soc()
SOC_CODES_DD003: dict[str, str] = {**SOC_CODES_TECHNICAL, **SOC_CODES_TRADES}

# ---------------------------------------------------------------------------
# NAICS codes — DD-003 labor analysis
# ---------------------------------------------------------------------------

NAICS_DD003: dict[str, str] = {
    "518210": "Data Processing, Hosting, and Related Services",
    "236220": "Commercial and Institutional Building Construction",
    "238210": "Electrical Contractors and Other Wiring Installation",
    "541511": "Custom Computer Programming Services",
    "541512": "Computer Systems Design Services",
    "221100": "Electric Power Generation, Transmission and Distribution",
}

# ---------------------------------------------------------------------------
# County FIPS codes — known data center clusters
# Used to filter QCEW county data to geographies of interest.
# ---------------------------------------------------------------------------

DC_CLUSTER_COUNTIES: dict[str, str] = {
    "51107": "Loudoun County, VA (NoVA)",
    "51059": "Fairfax County, VA (NoVA)",
    "04013": "Maricopa County, AZ (Phoenix)",
    "48113": "Dallas County, TX",
    "48085": "Collin County, TX (DFW)",
    "48121": "Denton County, TX (DFW)",
    "13045": "Carroll County, GA (Atlanta)",
    "13285": "Troup County, GA (Atlanta)",
    "39089": "Licking County, OH (Columbus)",
    "17043": "DuPage County, IL (Chicago)",
    "32003": "Clark County, NV (Las Vegas)",
    "37183": "Wake County, NC (Research Triangle)",
    "06085": "Santa Clara County, CA (Bay Area)",
    "53033": "King County, WA (Seattle)",
}

# ---------------------------------------------------------------------------
# OEWS — Occupational Employment and Wage Statistics
# ---------------------------------------------------------------------------

# URL pattern: year_2d is "23" for 2023, "24" for 2024, etc.
_OEWS_URL = "https://www.bls.gov/oes/special.requests/oesm{year_2d}nat.zip"


def _oews_cache_path(year: int) -> Path:
    return RAW_DIR / f"oews_{year}_national.parquet"


def fetch_oews_national(
    year: int,
    force_download: bool = False,
) -> pd.DataFrame:
    """Download (and cache) the BLS OEWS national flat file for a given year.

    Returns a DataFrame with columns:
        year, occ_code, occ_title, o_group, tot_emp, h_mean, a_mean,
        h_median, a_median, a_pct25, a_pct75

    Wage values are in nominal USD. Employment is estimated headcount.
    BLS uses "*" for suppressed values and "#" for wages above $100/hr —
    these are coerced to NaN.

    The flat file is cached to data/raw/bls/oews_{year}_national.parquet
    after first download. Subsequent calls use the cache unless
    force_download=True.

    Parameters
    ----------
    year : int
        Reference year (2015–2024 available).
    force_download : bool
        If True, re-download even if cached.
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    cache = _oews_cache_path(year)

    if cache.exists() and not force_download:
        logger.info("OEWS %d: loading from cache %s", year, cache)
        return pd.read_parquet(cache)

    url = _OEWS_URL.format(year_2d=str(year)[2:])
    logger.info("OEWS %d: downloading from %s", year, url)

    resp = requests.get(url, timeout=180, headers=_HEADERS)
    resp.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        # Internal file naming varies by year. Recent: "national_M{year}_dl.xlsx"
        # Prefer the _dl (detailed level) file; fall back to first national match.
        candidates = [
            name for name in zf.namelist()
            if ("national" in name.lower() or "nat3d" in name.lower())
            and name.endswith((".xlsx", ".csv"))
            and "__MACOSX" not in name
        ]
        if not candidates:
            msg = f"No national OEWS file found in ZIP. Contents: {zf.namelist()}"
            raise FileNotFoundError(msg)

        dl_files = [f for f in candidates if "_dl" in f.lower()]
        target = dl_files[0] if dl_files else candidates[0]
        logger.info("OEWS %d: parsing %s", year, target)

        with zf.open(target) as f:
            if target.endswith(".xlsx"):
                df = pd.read_excel(f, dtype=str)
            else:
                df = pd.read_csv(f, dtype=str)

    df = _clean_oews(df, year)
    df.to_parquet(cache, index=False)
    logger.info("OEWS %d: cached %d rows → %s", year, len(df), cache)
    return df


def _clean_oews(df: pd.DataFrame, year: int) -> pd.DataFrame:
    """Normalize column names and coerce numeric fields."""
    df.columns = [str(c).strip().lower() for c in df.columns]

    # Keep and rename the columns we use
    _keep = {
        "occ_code": "occ_code",
        "occ_title": "occ_title",
        "o_group": "o_group",
        "tot_emp": "tot_emp",
        "h_mean": "h_mean",
        "a_mean": "a_mean",
        "h_median": "h_median",
        "a_median": "a_median",
        "a_pct25": "a_pct25",
        "a_pct75": "a_pct75",
    }
    df = df.rename(columns={k: v for k, v in _keep.items() if k in df.columns})
    df = df[[c for c in _keep.values() if c in df.columns]].copy()

    # Coerce numeric columns — BLS uses "*" (suppressed) and "#" (>$100/hr)
    for col in ["tot_emp", "h_mean", "a_mean", "h_median", "a_median", "a_pct25", "a_pct75"]:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col].str.replace(",", "", regex=False), errors="coerce"
            )

    df["year"] = year
    return df


def fetch_oews_soc(
    soc_codes: dict[str, str] | None = None,
    years: list[int] | None = None,
) -> pd.DataFrame:
    """Fetch OEWS wage data for specific SOC codes across multiple years.

    Returns a long-format DataFrame for time-series analysis:
        year, occ_code, occ_title, label, tot_emp, h_mean, a_mean,
        h_median, a_median, a_pct25, a_pct75

    Parameters
    ----------
    soc_codes : dict mapping SOC code → short label. Defaults to SOC_CODES_DD003.
    years : list of years to fetch. Defaults to 2019–2024.
    """
    codes = soc_codes or SOC_CODES_DD003
    years = years or list(range(2019, 2025))

    frames = []
    for year in years:
        try:
            df = fetch_oews_national(year)
        except Exception:
            logger.warning("OEWS %d: failed", year, exc_info=True)
            continue

        subset = df[df["occ_code"].isin(codes.keys())].copy()
        subset["label"] = subset["occ_code"].map(codes)
        frames.append(subset)

    if not frames:
        return pd.DataFrame()

    return (
        pd.concat(frames, ignore_index=True)
        .sort_values(["occ_code", "year"])
        .reset_index(drop=True)
    )


# ---------------------------------------------------------------------------
# QCEW — Quarterly Census of Employment and Wages
# ---------------------------------------------------------------------------

_QCEW_API_URL = "https://data.bls.gov/cew/data/api/{year}/a/industry/{naics}.csv"

# Ownership codes: 0=all, 1=federal, 2=state, 3=local, 5=private
_PRIVATE_OWN_CODE = 5


def fetch_qcew_county(
    naics: str,
    year: int,
    own_code: int = _PRIVATE_OWN_CODE,
) -> pd.DataFrame:
    """Fetch BLS QCEW annual averages for a NAICS code at county level.

    Returns a DataFrame with columns:
        year, naics, area_fips, state_fips, county_fips,
        annual_avg_employment, annual_avg_weekly_wage,
        annual_avg_establishments, disclosure_code

    Suppressed counties have a non-blank disclosure_code ('N' = not disclosed).
    These are included in the output — filter on disclosure_code == '' for
    fully-disclosed records only.

    Parameters
    ----------
    naics : NAICS industry code (e.g. "518210"). 2-, 3-, 4-, or 6-digit.
    year : reference year (2010–2024 available).
    own_code : ownership type filter (default 5 = private sector only).
    """
    url = _QCEW_API_URL.format(year=year, naics=naics)
    logger.info("QCEW county %s (%d): %s", naics, year, url)

    resp = requests.get(url, timeout=90, headers=_HEADERS)
    resp.raise_for_status()
    df = pd.read_csv(io.StringIO(resp.text))

    if "own_code" in df.columns:
        df = df[df["own_code"] == own_code]

    # County level: 5-char FIPS not ending in "000" (those are state/national)
    if "area_fips" in df.columns:
        df["area_fips"] = df["area_fips"].astype(str).str.zfill(5)
        df = df[
            (df["area_fips"].str.len() == 5)
            & (~df["area_fips"].str.endswith("000"))
        ]

    df = df.rename(columns={
        "annual_avg_emplvl": "annual_avg_employment",
        "annual_avg_wkly_wage": "annual_avg_weekly_wage",
        "annual_avg_estabs": "annual_avg_establishments",
    })

    df["state_fips"] = df["area_fips"].str[:2]
    df["county_fips"] = df["area_fips"].str[2:]
    df["year"] = year
    df["naics"] = naics

    _keep = [
        "year", "naics", "area_fips", "state_fips", "county_fips",
        "annual_avg_employment", "annual_avg_weekly_wage",
        "annual_avg_establishments", "disclosure_code",
    ]
    return df[[c for c in _keep if c in df.columns]].copy()


def fetch_qcew_state(
    naics: str,
    year: int,
    own_code: int = _PRIVATE_OWN_CODE,
) -> pd.DataFrame:
    """Fetch BLS QCEW annual averages for a NAICS code at state level.

    Returns same columns as fetch_qcew_county but with 2-digit state area_fips
    (e.g. "01000" for Alabama). Useful for national picture before drilling
    into county clusters.
    """
    url = _QCEW_API_URL.format(year=year, naics=naics)
    logger.info("QCEW state %s (%d)", naics, year)

    resp = requests.get(url, timeout=90, headers=_HEADERS)
    resp.raise_for_status()
    df = pd.read_csv(io.StringIO(resp.text))

    if "own_code" in df.columns:
        df = df[df["own_code"] == own_code]

    # State-level: 5-char FIPS ending in "000", excluding US total ("US000")
    if "area_fips" in df.columns:
        df["area_fips"] = df["area_fips"].astype(str).str.zfill(5)
        df = df[
            (df["area_fips"].str.len() == 5)
            & (df["area_fips"].str.endswith("000"))
            & (df["area_fips"] != "US000")
        ]

    df = df.rename(columns={
        "annual_avg_emplvl": "annual_avg_employment",
        "annual_avg_wkly_wage": "annual_avg_weekly_wage",
        "annual_avg_estabs": "annual_avg_establishments",
    })

    df["year"] = year
    df["naics"] = naics

    _keep = [
        "year", "naics", "area_fips",
        "annual_avg_employment", "annual_avg_weekly_wage",
        "annual_avg_establishments", "disclosure_code",
    ]
    return df[[c for c in _keep if c in df.columns]].copy()


def fetch_qcew_series(
    naics_codes: dict[str, str] | None = None,
    years: list[int] | None = None,
    level: str = "county",
) -> pd.DataFrame:
    """Fetch QCEW for multiple NAICS codes and years.

    Returns a long-format DataFrame with a naics_description column added.
    Failed year/NAICS combinations are skipped with a warning.

    Parameters
    ----------
    naics_codes : dict mapping NAICS code → description. Defaults to NAICS_DD003.
    years : list of years. Defaults to 2019–2024.
    level : "county" or "state".
    """
    codes = naics_codes or NAICS_DD003
    years = years or list(range(2019, 2025))
    fetch_fn = fetch_qcew_county if level == "county" else fetch_qcew_state

    frames = []
    for naics, description in codes.items():
        for year in years:
            try:
                df = fetch_fn(naics, year)
                df["naics_description"] = description
                frames.append(df)
            except Exception:
                logger.warning("QCEW %s %d: failed", naics, year, exc_info=True)

    if not frames:
        return pd.DataFrame()

    return (
        pd.concat(frames, ignore_index=True)
        .sort_values(["naics", "year"])
        .reset_index(drop=True)
    )
