"""Census Bureau data access — ACS 5-year estimates and geographic data.

Two primary access modes:
- fetch_acs5(): ACS 5-year estimates at county level via Census API
- load_counties(): TIGER/Line county shapefiles (cached locally)
- load_locations(): Data center locations CSV with correct FIPS string dtype

API key is optional but recommended — without one, the Census API allows
only 500 requests/day per IP. Get a free key at:
    https://api.census.gov/data/key_signup.html

Store as CENSUS_API_KEY in a .env file at the project root. Never hardcode.

Usage:
    from src.data.census import fetch_acs5, compute_derived, load_counties, load_locations

    # Fetch 2023 ACS for all US counties
    df = fetch_acs5(2023)
    df = compute_derived(df)

    # Load county shapefiles for mapping
    counties = load_counties()          # requires geopandas

    # Load the data center locations with FIPS preserved as string
    locs = load_locations()
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

import pandas as pd
import requests

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
EXTERNAL_DIR = PROJECT_ROOT / "data" / "external"
RAW_DIR = PROJECT_ROOT / "data" / "raw"

_HEADERS = {"User-Agent": "Systems Research Project systems-research@proton.me"}

# ---------------------------------------------------------------------------
# ACS Variable Definitions
# ---------------------------------------------------------------------------

ACS_VARIABLES: dict[str, str] = {
    # Poverty
    "B17001_001E": "pop_poverty_universe",
    "B17001_002E": "pop_below_poverty",
    # Median household income
    "B19013_001E": "median_household_income",
    # Employment / unemployment (civilian noninstitutionalized pop 16+)
    "B23025_001E": "pop_16_plus",
    "B23025_002E": "labor_force",
    "B23025_003E": "civilian_labor_force",
    "B23025_004E": "employed",
    "B23025_005E": "unemployed",
    "B23025_006E": "armed_forces",
    "B23025_007E": "not_in_labor_force",
    # Educational attainment (25+)
    "B15003_001E": "pop_25_plus",
    "B15003_022E": "bach_degree",
    "B15003_023E": "masters_degree",
    "B15003_024E": "professional_degree",
    "B15003_025E": "doctorate_degree",
    # Total population
    "B01003_001E": "total_population",
    # Race and Hispanic origin (B03002 = non-Hispanic breakdowns)
    "B03002_001E": "race_universe",
    "B03002_003E": "white_non_hispanic",
    "B03002_004E": "black_non_hispanic",
    "B03002_006E": "asian_non_hispanic",
    "B03002_012E": "hispanic_or_latino",
}

# Latest ACS 5-year vintage confirmed available as of Feb 2026
ACS_DEFAULT_YEAR = 2023

_ACS_BASE_URL = "https://api.census.gov/data/{year}/acs/acs5"

# Threshold below which Census uses large negative placeholder values
_CENSUS_SUPPRESSION_THRESHOLD = -999999


# ---------------------------------------------------------------------------
# ACS fetch
# ---------------------------------------------------------------------------


def fetch_acs5(
    year: int = ACS_DEFAULT_YEAR,
    variables: dict[str, str] | None = None,
    api_key: str | None = None,
    use_cache: bool = True,
) -> pd.DataFrame:
    """Fetch ACS 5-year estimates for all US counties.

    Returns a DataFrame with:
    - county_fips (str, 5-digit, zero-padded)
    - state_fips (str, 2-digit)
    - county_code (str, 3-digit)
    - county_name (str)
    - One column per ACS variable, using the short name from `variables`

    Census uses large negative placeholder values for suppressed/missing data.
    These are NOT cleaned here — call compute_derived() which handles them.

    Downloads are cached to data/external/acs5_{year}_county.parquet.
    Set use_cache=False to force a fresh download.

    Parameters
    ----------
    year : int
        ACS 5-year vintage (2009–2023 available; avoid 2020 due to COVID-19
        data collection disruptions).
    variables : dict mapping Census variable code → column name.
        Defaults to ACS_VARIABLES (the full set for community impact analysis).
    api_key : str, optional
        Census API key. If None, reads CENSUS_API_KEY from environment.
        Without a key, the API allows 500 requests/day per IP.
    use_cache : bool
        If True (default), return cached parquet if available.
    """
    vars_map = variables or ACS_VARIABLES
    cache_path = EXTERNAL_DIR / f"acs5_{year}_county.parquet"

    if use_cache and cache_path.exists():
        logger.info("ACS5 %d: loading from cache %s", year, cache_path)
        return pd.read_parquet(cache_path)

    key = api_key or os.environ.get("CENSUS_API_KEY", "")
    if not key:
        logger.warning(
            "CENSUS_API_KEY not set. Requests will be rate-limited to 500/day per IP. "
            "Get a free key at https://api.census.gov/data/key_signup.html"
        )

    # The Census API handles up to ~50 variables per request; batch if needed
    var_codes = list(vars_map.keys())
    all_frames: list[pd.DataFrame] = []

    # Always include NAME for human-readable county labels
    for batch_start in range(0, len(var_codes), 45):
        batch = var_codes[batch_start : batch_start + 45]
        get_param = "NAME," + ",".join(batch)

        params: dict[str, str] = {
            "get": get_param,
            "for": "county:*",
            "in": "state:*",
        }
        if key:
            params["key"] = key

        url = _ACS_BASE_URL.format(year=year)
        logger.info("ACS5 %d: fetching %d variables from %s", year, len(batch), url)

        try:
            resp = requests.get(url, params=params, timeout=120, headers=_HEADERS)
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            logger.error("ACS5 %d: request failed", year, exc_info=True)
            raise

        if not data or len(data) < 2:
            logger.warning("ACS5 %d: empty response", year)
            continue

        headers = data[0]
        rows = data[1:]
        batch_df = pd.DataFrame(rows, columns=headers)

        # Reconstruct 5-digit FIPS from separate state/county columns
        if "state" in batch_df.columns and "county" in batch_df.columns:
            state_z = batch_df["state"].str.zfill(2)
            county_z = batch_df["county"].str.zfill(3)
            batch_df["county_fips"] = state_z + county_z
            batch_df["state_fips"] = state_z
            batch_df["county_code"] = batch_df["county"].str.zfill(3)
            batch_df = batch_df.drop(columns=["state", "county"])

        all_frames.append(batch_df)

    if not all_frames:
        return pd.DataFrame()

    # Merge all batches on county_fips (they share the same rows in same order)
    result = all_frames[0]
    for extra in all_frames[1:]:
        merge_cols = ["county_fips"]
        extra = extra.drop(
            columns=[c for c in ["NAME", "state_fips", "county_code"] if c in extra.columns],
            errors="ignore",
        )
        result = result.merge(extra, on=merge_cols, how="left")

    # Rename ACS variable codes to short names
    result = result.rename(columns={k: v for k, v in vars_map.items() if k in result.columns})

    # Rename NAME column
    if "NAME" in result.columns:
        result = result.rename(columns={"NAME": "county_name"})

    # Coerce numeric ACS value columns (they come back as strings)
    acs_cols = list(vars_map.values())
    for col in acs_cols:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors="coerce")

    result["acs_year"] = year

    # Cache
    EXTERNAL_DIR.mkdir(parents=True, exist_ok=True)
    result.to_parquet(cache_path, index=False)
    logger.info("ACS5 %d: cached %d rows → %s", year, len(result), cache_path)

    return result


# ---------------------------------------------------------------------------
# Derived metrics
# ---------------------------------------------------------------------------


def compute_derived(df: pd.DataFrame) -> pd.DataFrame:
    """Compute rate and percentage metrics from raw ACS counts.

    Suppresses Census placeholder values (large negatives) to NaN
    before computing any ratio. Safe to call on any ACS DataFrame
    that has been through fetch_acs5().

    Adds columns:
    - poverty_rate
    - unemployment_rate
    - labor_force_participation
    - pct_bachelors_plus
    - pct_white, pct_black, pct_hispanic
    """
    df = df.copy()

    # Suppress Census negative placeholder codes before any arithmetic
    numeric_cols = df.select_dtypes(include="number").columns
    df[numeric_cols] = df[numeric_cols].where(
        df[numeric_cols] > _CENSUS_SUPPRESSION_THRESHOLD,
        other=float("nan"),
    )

    def _rate(num: str, denom: str) -> pd.Series:
        """Safe ratio — returns NaN when denominator is 0 or missing."""
        if num not in df.columns or denom not in df.columns:
            return pd.Series(float("nan"), index=df.index)
        return df[num].div(df[denom].replace(0, float("nan")))

    df["poverty_rate"] = _rate("pop_below_poverty", "pop_poverty_universe")
    df["unemployment_rate"] = _rate("unemployed", "civilian_labor_force")
    df["labor_force_participation"] = _rate("labor_force", "pop_16_plus")

    # bachelors+ = sum of all post-secondary degree levels
    for col in ["bach_degree", "masters_degree", "professional_degree", "doctorate_degree"]:
        if col not in df.columns:
            df[col] = float("nan")
    if "pop_25_plus" in df.columns:
        df["pct_bachelors_plus"] = (
            df[["bach_degree", "masters_degree", "professional_degree", "doctorate_degree"]]
            .sum(axis=1, min_count=1)
            .div(df["pop_25_plus"].replace(0, float("nan")))
        )

    df["pct_white"] = _rate("white_non_hispanic", "race_universe")
    df["pct_black"] = _rate("black_non_hispanic", "race_universe")
    df["pct_hispanic"] = _rate("hispanic_or_latino", "race_universe")

    return df


# ---------------------------------------------------------------------------
# TIGER/Line county shapefiles
# ---------------------------------------------------------------------------

_TIGER_URL = "https://www2.census.gov/geo/tiger/TIGER2023/COUNTY/tl_2023_us_county.zip"
_TIGER_CACHE = RAW_DIR / "tl_2023_us_county.zip"


def load_counties(force_download: bool = False) -> pd.DataFrame:
    """Load 2023 TIGER/Line US county boundaries as a GeoDataFrame.

    Downloads once and caches to data/raw/tl_2023_us_county.zip.
    Projection: WGS84 / EPSG:4326 (latitude/longitude).

    For national choropleth maps, reproject to Albers Equal Area:
        counties = load_counties().to_crs("EPSG:5070")

    Returns a GeoDataFrame with columns:
        county_fips (str, 5-digit), county_name (str), namelsad (str),
        aland (int, land area in sq meters), geometry (Polygon)

    Requires geopandas. Install via: uv pip install geopandas
    """
    try:
        import geopandas as gpd
    except ImportError as e:
        msg = "geopandas is required for load_counties(). Install via: uv pip install geopandas"
        raise ImportError(msg) from e

    if not _TIGER_CACHE.exists() or force_download:
        logger.info("TIGER/Line: downloading county shapefile from %s", _TIGER_URL)
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        resp = requests.get(_TIGER_URL, stream=True, timeout=180, headers=_HEADERS)
        resp.raise_for_status()
        _TIGER_CACHE.write_bytes(resp.content)
        logger.info("TIGER/Line: cached to %s", _TIGER_CACHE)

    gdf = gpd.read_file(f"zip://{_TIGER_CACHE}")
    gdf = gdf[["GEOID", "NAME", "NAMELSAD", "ALAND", "geometry"]].rename(
        columns={
            "GEOID": "county_fips",
            "NAME": "county_name",
            "NAMELSAD": "namelsad",
            "ALAND": "aland",
        }
    )
    return gdf


# ---------------------------------------------------------------------------
# Data center locations CSV
# ---------------------------------------------------------------------------


def load_locations(path: Path | None = None) -> pd.DataFrame:
    """Load the data center locations CSV with county_fips preserved as string.

    IMPORTANT: county_fips must be read as a string to preserve leading zeros
    in FIPS codes for states like Arizona (04xxx) and Alabama (01xxx). Pandas
    will silently strip leading zeros if read as integer.

    Returns a DataFrame ready for merging with ACS and TIGER/Line data
    on the county_fips column.
    """
    csv_path = path or (EXTERNAL_DIR / "data_center_locations.csv")
    return pd.read_csv(csv_path, dtype={"county_fips": str})


# ---------------------------------------------------------------------------
# Convenience: joined dataset for the community impact analysis
# ---------------------------------------------------------------------------


def build_community_dataset(
    acs_year: int = ACS_DEFAULT_YEAR,
    api_key: str | None = None,
) -> pd.DataFrame:
    """Return a DataFrame merging data center locations with ACS county data.

    Each row is a data center facility, enriched with county-level
    socioeconomic indicators from the ACS.

    Columns: all location CSV columns + all ACS_VARIABLES (renamed) +
    all compute_derived() outputs.

    Parameters
    ----------
    acs_year : ACS 5-year vintage to use for socioeconomic context.
    api_key : Census API key (reads CENSUS_API_KEY env var if None).
    """
    locs = load_locations()
    acs = fetch_acs5(year=acs_year, api_key=api_key)
    acs = compute_derived(acs)

    merged = locs.merge(
        acs,
        on="county_fips",
        how="left",
        suffixes=("", "_acs"),
    )

    n_matched = merged["total_population"].notna().sum()
    logger.info(
        "community_dataset: %d locations, %d matched to ACS (%d unmatched)",
        len(locs),
        n_matched,
        len(locs) - n_matched,
    )
    return merged
