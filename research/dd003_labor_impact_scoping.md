# DD-003: AI Capital Flows and Labor Impact — Scoping Document

*Compiled: 2026-02-15*
*Source: Researcher agent scoping output*

---

## Core Question

How do AI capital flows reshape labor demand — who gets hired, displaced, what
skills become critical, and where do jobs land?

---

## Five Capital-to-Labor Transmission Channels

### 1. Direct Infrastructure Construction Labor
- Data center construction requires electricians, welders, heavy equipment operators,
  concrete/steel workers
- Build phase is temporary and front-loaded (18-36 months per site)
- Once built, operations staffing drops to ~50-100 people per large campus
- Geographic concentration: Northern Virginia, Central Ohio, Dallas-Fort Worth,
  Phoenix, Atlanta metro

### 2. Supply Chain Manufacturing Labor
- Transformer manufacturing (NAICS 335311), switchgear, backup generators
- Semiconductor fabrication (TSMC Arizona, Intel Ohio, Samsung Texas)
- These are longer-duration jobs but dependent on sustained demand

### 3. Utility and Grid Workforce
- Lineworkers, substation technicians, power plant operators
- Aging workforce (average age ~50+) with 4-year apprenticeship pipeline
- AI-driven grid expansion competes with baseline replacement demand

### 4. Knowledge Work Displacement
- Software engineering, data analysis, content creation, administration
- Layoffs visible and ongoing (Challenger Gray & Christmas data)
- Different population, geography, and skill set than infrastructure hires
- Displacement is persistent; infrastructure hiring is cyclical

### 5. Operations and Maintenance Phase
- Data center technicians, facility managers, network engineers
- Much lower headcount than build phase
- Skills partially overlap with displaced tech workers but geography differs

---

## Free Data Sources

| Source | What It Covers | Access |
|:---|:---|:---|
| **BLS QCEW** | County-level employment by NAICS, quarterly | API, no key |
| **FRED** | National employment series by sector | CSV, no key |
| **Census CBP** | County-level establishments, employment, payroll | API, no key |
| **BLS JOLTS** | Job openings and separations by industry | FRED download |
| **BLS OES** | Occupational employment and wages | Bulk download |
| **WARN Act filings** | Advance layoff notices by state | State websites |
| **Challenger Gray** | Tech layoff announcements | Press releases |
| **DOE USEER** | Energy employment by sector and state | PDF/download |

### NAICS Codes for Analysis

| Code | Industry | Relevance |
|:---|:---|:---|
| 518210 | Data Processing, Hosting | Direct data center employment |
| 236220 | Commercial Building Construction | Data center construction |
| 2211 | Electric Power Gen/Trans/Dist | Utility workforce |
| 5415 | Computer Systems Design | Knowledge work displacement |
| 334 | Computer/Electronic Manufacturing | Supply chain manufacturing |
| 335311 | Power Transformer Manufacturing | Grid equipment supply chain |

---

## Quantitative Anchors (from research)

- **Build-phase labor intensity:** ~3,000-5,000 construction jobs per large data
  center campus (1-2 GW), lasting 18-36 months
- **Operations staffing:** ~50-100 permanent jobs per campus
- **Ratio:** ~30-50x more build-phase than operations-phase labor per site
- **Electrician shortage:** IBEW reports ~80,000 unfilled electrician positions
  nationally, with 4-year apprenticeship pipeline
- **Tech layoffs 2023-2024:** ~400,000+ announced (Challenger data), concentrated
  in software, content, and operations roles
- **Aging utility workforce:** ~25% of utility workers eligible for retirement
  within 5 years (DOE USEER)

---

## Contradictory Evidence

1. **Net job creation may be positive** in the near term — McKinsey estimates AI
   infrastructure could create 1-3M construction-adjacent jobs through 2030
2. **Retraining pathways exist** — some coding bootcamps pivoting to trades;
   community colleges expanding electrical programs
3. **Geographic overlap is partial** — some data center corridors are in tech
   metros (Northern Virginia) where displaced workers could theoretically shift
4. **AI augmentation vs replacement** — many knowledge work roles may be augmented
   rather than eliminated, reducing the displacement count

---

## Proposed Notebook Structure

### NB01: The Labor Footprint of AI Capital
- Map the five transmission channels with data
- FRED employment trends by sector (construction, utilities, info, manufacturing)
- BLS QCEW county-level employment in data center corridors
- Key chart: employment trajectories diverging post-2020

### NB02: Build Phase vs. Operations Phase
- Temporal dynamics: what happens when construction ends?
- Census CBP establishment counts in data center counties over time
- Geographic concentration analysis
- Key chart: build-phase employment spike and post-completion decline

### NB03: Displacement and Skills Mismatch
- Knowledge work layoffs (Challenger, WARN Act data)
- Skills gap analysis: displaced skills vs demanded skills
- Retraining pipeline capacity and lead times
- Key chart: "the skills canyon" — displacement categories vs infrastructure demand

### NB04 (optional): Political Economy
- Public perception and policy feedback
- How labor outcomes affect regulatory environment for AI infrastructure
- The temporal mismatch: visible layoffs now, infrastructure jobs temporary

---

## Key Academic References

- Autor, D. (2024). "Applying AI to Rebuild Middle Class Jobs." NBER Working Paper.
- Acemoglu, D. & Restrepo, P. (2019). "Automation and New Tasks." AER.
- Frey, C.B. & Osborne, M. (2017). "The Future of Employment." Technological
  Forecasting and Social Change.
- DOE (2024). U.S. Energy and Employment Report (USEER).
- Grid Strategies (2023). The Era of Flat Power Demand is Over.

---

## Data Already Loaded (DuckDB)

As of 2026-02-15, the following DD-003 data is in `data/research.duckdb`:

| Table | Records | Source |
|:---|---:|:---|
| `energy_data.fred_series` | ~15,900 | 12 FRED series (5 energy + 7 employment) |
| `energy_data.bls_qcew` | ~118,000 | BLS QCEW 2016-2024, 5 NAICS codes |
| `energy_data.census_cbp` | ~29,700 | Census CBP 2016-2022, 4 NAICS codes |

Pipeline commands:
- `uv run python -m src.data.pipelines --fred`
- `uv run python -m src.data.pipelines --bls`
- `uv run python -m src.data.pipelines --census`
