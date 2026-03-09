# Plan: DD-004 Part 2 — Data Centers and Community Impact
## Geographic Analysis of AI Infrastructure Siting

**Status:** Data collection in progress (research agent running Feb 2026)
**Notebook:** `notebooks/dd004_utility_regulation/02_data_center_community_impact.py`

---

## Research Question

Where do hyperscale data centers actually land in the physical economy, and who
bears the costs? The geographic analysis maps facility siting against community
economic conditions to test two claims:

1. **The targeting hypothesis** — Developers select economically distressed communities
   for siting because deprivation correlates with weaker opposition, easier zoning, and
   more aggressive tax incentive competition between jurisdictions.

2. **The cost distribution problem** — Grid upgrade costs are socialized across entire
   utility service territories. The communities paying for the infrastructure are not
   necessarily the communities hosting or benefiting from it.

---

## Analytical Framework

### Section 1: Where they land
- US county choropleth map: Area Deprivation Index (ADI) as base layer
- Data center point overlay: location, operator, announced MW, investment
- Color-code by hyperscaler (use `COMPANY_COLORS` from `src/plotting.py`)
- Statistical test: ADI score distribution for host counties vs. all US counties
- Secondary map: employment rate (BLS LAUS) at time of announcement

### Section 2: The tax incentive geography
- Which states/counties have active data center tax exemption programs?
- Map: counties with known exemption programs
- Chart: public subsidy per permanent job by state
  - Virginia: $437M foregone tax revenue FY2023 (source needed)
  - Compare to manufacturing, warehousing at equivalent capital investment
- Key insight: capital intensity ($3–10M/permanent employee) means subsidy/job
  is structurally higher than any other large-footprint industrial use

### Section 3: Employment before and after
- Event study: for counties with known facility openings (with operational date),
  plot NAICS 518210 employment T-3 to T+4 years using BLS QCEW
- Overlay total county employment (all sectors) over same window
- Null hypothesis: a $1B+ data center does not meaningfully move county-level
  employment because the permanent headcount is too small
- This is the key empirical test of the "job creation" justification for subsidies

### Section 4: Who pays for the grid
- Data centers bypass the grid via direct utility contracts (behind-the-meter or
  direct interconnection agreements)
- Grid upgrade costs — transmission and distribution reinforcement — get added to
  the utility rate base and recovered from all ratepayers in the service territory
- Map: utility service territory boundaries + host counties
- Chart: income profile of the service territory vs. income of host county
- If host counties are wealthier (tech corridor), other ratepayers cross-subsidize
- If host counties are poorer (rural/distressed), community bears costs AND
  receives few permanent jobs

### Section 5: Durability mismatch
- Timeline chart showing three overlapping windows:
  - Tax exemption window: typically 10–20 years (state-negotiated)
  - Data center asset life: 20–30 years (but equipment cycles faster)
  - PE fund lifecycle: 7–10 years (relevant when utility is PE-owned — DD-004 Part 1)
- Key question: what is the community's net fiscal position over each window?
- When the tax exemption expires, does the facility stay?

---

## Data Requirements

### Already available (pipeline exists)

| Data | Source | Table in DB | Notes |
|------|---------|-------------|-------|
| County employment by NAICS 518210 | BLS QCEW | `bls_qcew` | 2016–2024, county level |
| County establishment count by NAICS | Census CBP | `census_cbp` | 2016–2022 |
| County employment by NAICS | Census CBP | `census_cbp` | 2016–2022 |
| Power plant locations + lat/lon | EIA Form 860 | `eia860_generators` | For energy infrastructure context |

### Needs to be built/collected

| Data | Source | File/Table | Status |
|------|---------|------------|--------|
| Data center locations (geocoded) | Manual + press releases | `data/external/data_center_locations.csv` | **Research agent building** |
| Area Deprivation Index | Neighborhood Atlas (UW) | `data/raw/adi_county_2023.csv` | Manual download, registration required |
| County poverty rate, income, demographics | Census ACS 5-year | needs `src/data/census.py` | Research agent documenting variables |
| County unemployment rate (monthly) | BLS LAUS | needs pipeline resource | Research agent documenting |
| US county boundaries (shapefile) | Census TIGER/Line | `data/raw/tl_2023_us_county/` | Research agent finding URL |
| State tax exemption programs | State leg. records | `data/external/dc_tax_exemptions.csv` | Manual research needed |
| Utility service territory boundaries | EIA Form 861 | `data/raw/utility_territories/` | Manual download from EIA |

---

## Implementation Steps (in order)

**Step 1 — Review research agent output**
- Read `data/external/data_center_locations.csv` — validate rows, fill gaps
- Read `data/external/README_geo_data_sources.md` — get Census ACS variable codes
- Download ADI data from Neighborhood Atlas (manual — requires registration)
- Download TIGER/Line county shapefile using URL from README

**Step 2 — Add `src/data/census.py`**
```python
# Pattern: mirrors fred.py
# Fetches ACS 5-year estimates by county
# Key variables: poverty rate, median HH income, unemployment, educational attainment
# Requires CENSUS_API_KEY env variable (free at api.census.gov/sign_up.html)
```

**Step 3 — Add BLS LAUS resource to `src/data/pipelines.py`**
```python
@dlt.resource(write_disposition="merge", primary_key=["area_fips", "year", "month"])
def bls_laus(years: list[int] | None = None) -> ...:
    # Monthly county unemployment rates
    # URL: https://www.bls.gov/lau/data.htm (CSV bulk files)
```

**Step 4 — Add `--laus` flag to pipeline runner**
- Add `run_laus()` and `--laus` argument to `pipelines.py` `__main__`

**Step 5 — Run pipelines to populate DB**
```bash
uv run python -m src.data.pipelines --laus
uv run python -m src.data.pipelines --census
```

**Important: FIPS as string**
Always read `data_center_locations.csv` with `dtype={"county_fips": str}` — pandas will
strip leading zeros from FIPS codes starting with 0 (Arizona=04xxx, Alabama=01xxx) if
read as integers. Same applies to the ACS API response: reconstruct with string ops.

**Step 6 — Build the notebook**
- Follow section structure above
- Stats cell pattern: all data-derived values computed from DB, interpolated into prose
- Charts: use `COMPANY_COLORS` for operator colors, `focus_colors()` for emphasis
- Maps: geopandas + matplotlib (static, publication-ready)
- Run `bash scripts/test_notebooks.sh` after each major section

---

## Key Chart Designs

### Map 1: The siting pattern
```
Projection: AlbersEqualArea (standard for US thematic maps)
Base layer: county polygons colored by ADI decile (light gray = least deprived,
            dark rust = most deprived) — using diverging palette from src/plotting.py
Points: data center locations, sized by announced MW, colored by operator
Legend: operator color legend below map
Title (H1 above chart): "Hyperscale data centers concentrate in [finding]"
```

### Chart 2: Capital intensity comparison
```
Horizontal bar chart, sorted descending
Categories: Data Center, Semiconductor Fab, Auto Manufacturing,
            Warehouse/Logistics, Food Processing
X-axis: $ million per permanent employee
Color: focus_colors() — data center highlighted in accent, others in CONTEXT gray
Direct labels on bars
Title: "$X million per permanent job — [n]x more capital-intensive than [comparable]"
```

### Event study: Employment before/after
```
Line chart, x-axis = years relative to facility announcement (T=0)
Two lines: NAICS 518210 employment (accent color), total county employment (gray)
Shaded region: pre-announcement period
Vertical dashed line: T=0 (announcement), T=operational (dotted)
Multiple counties as thin gray lines, median as thick accent line
Title: "Data center employment barely registers in county-level job counts"
```

---

## Open Questions to Resolve

1. **What is "distressed"?** ADI decile cutoff for "high deprivation" — use top quartile (ADI > 75)?
   Or use established federal designations (Opportunity Zones, Promise Zones, EDA distressed criteria)?

2. **Tax exemption data source** — No clean centralized dataset exists. Options:
   - National Conference of State Legislatures (NCSL) tracks data center tax bills
   - Good Jobs First "Subsidy Tracker" database — free, covers major corporate subsidies
   - Manual research for top 10 states by data center investment

3. **Causality vs. correlation for employment** — Event study shows correlation.
   To test causality would need a difference-in-differences design with control counties.
   For this publication, be clear it's descriptive, not causal.

4. **Grid cost data** — EIA Form 861 has utility territory shapefiles and load data.
   Actual cost allocation records are in rate cases filed with state utility commissions —
   much harder to aggregate. May need to rely on case studies (Virginia SCC, PJM filings).

---

## Connections to Other Case Studies

- **DD-004 Part 1** (`01_pe_utility_acquisitions.py`): When PE owns the utility, the
  rate-base cost socialization mechanism is the same but the return structure changes.
  The community impact analysis should cross-reference the PE acquisition map.

- **DD-001** (`01_markets_and_money.py`): The off-balance-sheet SPV financing (Beignet/Meta)
  means reported capex understates actual capital commitment. The locations CSV
  investment figures are from press releases, not audited financials — note this caveat.

- **DD-003** (`01_who_gets_hired.py`): Labor market analysis. The event study here
  (Section 3) is the geographic complement to DD-003's occupational wage analysis.

---

## Resume Instructions

When returning to this work:
1. Check if research agent output exists: `data/external/data_center_locations.csv`
   and `data/external/README_geo_data_sources.md`
2. Read both files to understand data quality and gaps
3. Follow implementation steps above in order
4. The notebook stub is at `notebooks/dd004_utility_regulation/02_data_center_community_impact.py`
   — it has the intro markdown but no data cells yet
