# Data Sources Catalog

A working catalog of data sources for the AI commodity research project. Each entry includes what the source provides, how to access it, and what it's useful for in the model.

---

## Government and Institutional Sources

### EIA (U.S. Energy Information Administration)
- **URL:** https://www.eia.gov/
- **What it provides:** U.S. electricity generation, consumption, capacity, and forecasts. Detailed breakdowns by fuel source, state, and sector.
- **Key datasets:**
  - Electricity Data Browser (monthly generation/consumption by state and source)
  - Annual Energy Outlook (long-term forecasts)
  - Short-Term Energy Outlook (near-term forecasts)
  - Form EIA-860 (generator-level data)
- **Access:** Free, downloadable as CSV/Excel. API available.
- **Use in model:** Baseline electricity demand, grid capacity constraints, generation mix projections

### IEA (International Energy Agency)
- **URL:** https://www.iea.org/
- **What it provides:** Global energy analysis, data center energy reports, technology outlooks
- **Key publications:**
  - "Electricity 2024" report
  - Data centre and AI energy consumption analysis
  - World Energy Outlook (annual)
- **Access:** Some reports free, some behind paywall. Key data center reports have been publicly available.
- **Use in model:** Global context, data center energy intensity benchmarks, international comparison

### USGS (U.S. Geological Survey)
- **URL:** https://www.usgs.gov/centers/national-minerals-information-center
- **What it provides:** Mineral commodity summaries, production data, reserve estimates, trade data
- **Key datasets:**
  - Mineral Commodity Summaries (annual, covers ~90 commodities)
  - Minerals Yearbook (detailed annual data by mineral)
  - Historical statistics for mineral commodities
- **Access:** Free, downloadable as PDF and some data tables.
- **Use in model:** Supply-side constraints for copper, lithium, rare earths, silicon. Reserve-to-production ratios. Import dependency.

### Federal Reserve FRED
- **URL:** https://fred.stlouisfed.org/
- **What it provides:** Economic time series -- commodity prices, industrial production, capital investment, interest rates
- **Key series:**
  - Producer Price Index for copper, aluminum, etc.
  - Private fixed investment in equipment and structures
  - Industrial production indices
  - Real estate indices
- **Access:** Free API with Python wrapper (`fredapi` package)
- **Use in model:** Commodity price dynamics, macroeconomic context, historical capital investment cycles

---

## Corporate and Financial Sources

### SEC Filings (EDGAR)
- **URL:** https://www.sec.gov/edgar/
- **What it provides:** Quarterly and annual filings from public companies, including CapEx disclosures
- **Key companies to track:**
  - **Microsoft** (MSFT) -- Azure cloud + OpenAI partnership
  - **Alphabet/Google** (GOOG) -- GCP + DeepMind
  - **Amazon** (AMZN) -- AWS
  - **Meta** (META) -- AI infrastructure buildout
  - **NVIDIA** (NVDA) -- GPU revenue as AI demand proxy
  - **Equinix** (EQIX), **Digital Realty** (DLR) -- Data center REITs
- **What to extract:** Total CapEx, capital lease obligations, segment-level infrastructure spending, management commentary on AI-specific investment
- **Access:** Free via EDGAR full-text search and XBRL structured data
- **Use in model:** AI CapEx estimates, growth trajectory calibration, regime switching signal inputs

### Bloomberg / S&P Global
- **What it provides:** Commodity price indices, sector analytics, supply chain data
- **Key datasets:**
  - Bloomberg Commodity Index (BCOM)
  - S&P GSCI commodity sub-indices
  - S&P Global Market Intelligence (power market data)
- **Access:** Paid subscription. Check if accessible through library or institutional access.
- **Use in model:** Commodity price dynamics, benchmark indices for validation

---

## Industry and Research Sources

### Uptime Institute
- **URL:** https://uptimeinstitute.com/
- **What it provides:** Data center industry surveys, PUE (Power Usage Effectiveness) data, infrastructure trend reports
- **Use in model:** Data center efficiency benchmarks, cooling technology adoption rates

### Data Center Map / Data Center Hawk
- **What it provides:** Geographic database of data center locations, capacity, and operators
- **Use in model:** Geographic concentration analysis, water stress mapping

### SEMI (Semiconductor Equipment and Materials International)
- **URL:** https://www.semi.org/
- **What it provides:** Semiconductor fab construction data, equipment spending forecasts
- **Use in model:** Semiconductor supply chain capacity, fab lead times

### Lawrence Berkeley National Laboratory
- **What it provides:** Research on U.S. data center energy use (Shehabi et al. studies)
- **Key publications:** "United States Data Center Energy Usage Report" series
- **Use in model:** Bottom-up energy consumption estimates, efficiency trend data

---

## Historical Analogies for Regime Calibration

These aren't data sources per se, but historical episodes useful for calibrating Markov regime transition probabilities:

| Episode | Relevance | Data Source |
|---|---|---|
| **Dot-com boom/bust (1997-2003)** | Technology CapEx cycle with overbuilding followed by consolidation. Fiber optic overcapacity persisted and became useful later. | FRED, SEC filings from era |
| **Shale oil boom (2010-2020)** | Commodity-linked capital cycle with boom, bust, and restructuring. Supply response dynamics. | EIA, FRED |
| **Crypto mining (2017-2023)** | Energy-intensive computing with volatile demand. Geographic shifts due to regulation and energy costs. | Cambridge Bitcoin Electricity Consumption Index |
| **Telecom buildout (1996-2002)** | Infrastructure overinvestment that eventually got used. Demand caught up to supply on ~10-year lag. | FCC reports, FRED |

---

## Data Access Priorities

For Phase 2 of the learning plan, prioritize these in order:
1. **EIA Electricity Data Browser** -- Foundational for energy demand modeling
2. **SEC CapEx filings** -- Core input for AI investment trajectory
3. **USGS Mineral Commodity Summaries** -- Supply constraint calibration
4. **FRED commodity prices** -- Historical price dynamics
5. **IEA data center reports** -- Global benchmarking

## Python Packages for Data Access
```
fredapi          # FRED API wrapper
sec-edgar-api    # SEC EDGAR data access
pandas-datareader # General financial data
yfinance         # Stock/commodity price data
requests         # General API access
```
