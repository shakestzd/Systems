# Research Framework

## Core Question

The AI infrastructure buildout and the energy transition are not separate stories.
When an AI company signs a 20-year power purchase agreement, it locks in generation
capacity. When a utility cites data center load growth in a rate proceeding, it may
be used to justify new fossil generation. When a semiconductor fab receives federal
investment, it reshapes regional labor markets for a generation. These decisions are
made in separate rooms by separate actors using separate analytical frameworks. But
they are building the same physical world, and their interactions create feedback
loops that no single discipline tracks.

**This project investigates where technology capital lands in the physical economy,
what it locks in, and who bears the consequences.**

This is not a commodity demand forecast. It is an analysis of how capital flows
create infrastructure path dependencies — commitments that persist regardless of
whether the investment thesis that justified them holds — and how those commitments
distribute costs and benefits unevenly across workers, communities, and ratepayers.

---

## Analytical Framework

### 1. Capital Flow Mapping

Trace technology capital through the physical supply chain. Identify where
the capital converts from financial commitment to physical asset.

```
Technology CapEx ($200B+/year in AI alone)
    │
    ├── Power Infrastructure (~40-50% of data center site cost)
    │     ├── Generation capacity (gas plants, solar, nuclear PPAs)
    │     ├── Transmission (high-voltage lines, substations, LPTs)
    │     ├── Distribution (transformers, switchgear, interconnection)
    │     └── On-site power (backup generation, UPS, battery storage)
    │
    ├── Physical Plant (~25-30%)
    │     ├── Real estate and land
    │     ├── Building construction (concrete, steel, HVAC)
    │     └── Cooling systems (water, liquid, air)
    │
    ├── Compute Hardware (~15-20%)
    │     ├── GPUs/accelerators (NVIDIA, AMD, custom ASICs)
    │     ├── Semiconductor fabs (TSMC, Intel, Samsung)
    │     └── Critical minerals (silicon, copper, rare earths)
    │
    └── Network (~5-10%)
          ├── Fiber optic (intra-campus, metro, long-haul)
          ├── Subsea cables
          └── Edge infrastructure
```

The percentages are approximate and vary by deployment type (hyperscale greenfield
vs. colo expansion vs. edge). Power infrastructure dominates — and power
infrastructure has the longest asset life and the most complex regulatory
entanglement.

### 2. Durability Taxonomy

For each investment node, classify the durability of the capital commitment:

| Category | Definition | Examples | Asset Life |
| :--- | :--- | :--- | :--- |
| **Structural** | Justified by demand that persists regardless of AI's commercial outcome | Grid modernization, utility transformer replacement, transmission upgrades | 30-50 years |
| **Policy-dependent** | Durable only under a specific regulatory regime | Tariff-protected domestic manufacturing, subsidized generation capacity | Varies with political cycles |
| **Demand-thesis-dependent** | Durable only if AI demand growth continues | GPU fabs at current scale, AI-optimized cooling, AI-specific data center designs | 3-10 years (hardware); 20-30 years (buildings) |

The interesting cases are investments that start as demand-thesis-dependent but
create structural demand through second-order effects. Example: a gas plant built
to power a data center campus is demand-thesis-dependent at inception. But once
built, it becomes a 40-year generating asset that operates regardless of whether
the data center scales as planned. The capital decision was AI-driven; the
infrastructure consequence is not.

### 3. Regulatory Interaction Analysis

Regulatory decisions shape where and how capital converts to infrastructure.
Five dimensions:

**Trade policy and tariffs.**
Tariffs on transformers, steel (Section 232), and other equipment create a time
horizon mismatch: tariffs are administrative actions reversible within a single
administration, but manufacturing capacity requires 15-20 year investment horizons.
The result is not reshoring — it is a price transfer from buyers to existing
producers, followed by permanent price floor establishment through revealed
willingness-to-pay. When tariffs are removed, prices do not fully revert. The
delta is pure capital loss.

The exception is vertical integration that doesn't depend on tariff protection
(e.g., Cleveland-Cliffs' Weirton plant, which is hedged on structural demand and
GOES supply control, not trade policy).

**Energy and environmental policy.**
Federal clean energy incentives — now significantly modified by the One Big
Beautiful Act (H.R.1, signed July 4, 2025) — shape which generation technologies
get built. The act preserved manufacturing credits (§45X), carbon capture (§45Q),
hydrogen (§45V), and clean fuels (§45Z) while setting a 12/31/2031 sunset for
utility-scale wind/solar (§45Y/§48E). The US formally withdrew from the Paris
Agreement in January 2026. Simultaneously, AI data center operators are signing the
largest corporate renewable PPAs in history. What generation mix gets built depends
critically on the current regulatory moment, and that mix outlives multiple
administrations.

*Policy references should be verified against Congress.gov and EIA.gov before citing.*

**FERC and utility regulation.**
FERC interconnection reform (Order 2023, in effect as of 2024) requires ISOs and
RTOs to process applications in interconnection clusters. The 2,400 GW queue backlog
(LBNL data) remains a binding constraint — average queue wait times of 4-5 years
can set binding limits on when new generation can reach the grid. Cost allocation
rules in rate proceedings determine who pays for grid upgrades driven by data center
demand. FERC Order 1920 (transmission planning) is under 8th Circuit legal challenge
as of February 2026 and its durability is uncertain.

**Industrial policy.**
The CHIPS Act and Defense Production Act authorizations for grid equipment create
subsidy flows that interact with private AI capital. These policies have different
durability profiles — statutory provisions are harder to repeal than executive
authorizations. After the One Big Beautiful Act, the landscape of clean energy
incentives shifted significantly; any analysis citing pre-2025 IRA provisions needs
to be updated to reflect current law.

**International and climate policy.**
The US withdrawal from the Paris Agreement in January 2026 shifts the international
context for domestic clean energy investment. Other major economies remain committed,
which affects where international capital flows and which technology supply chains
get built where. The divergence between US policy direction and international
commitments creates both regulatory arbitrage opportunities and competitive exposure
for US-based manufacturers depending on export markets.

### 4. People and Distribution

Capital flows create and destroy jobs, shift costs onto ratepayers, transform
communities, and make some stakeholders powerful while marginalizing others.
Tracking capital without tracking people produces an incomplete — and often
misleading — picture.

**Workers: build vs. operate.**
Infrastructure construction creates high demand for electrical trades, welders, heavy
equipment operators. This demand is temporary and front-loaded — once a data center
or substation is built, the construction workforce moves on. Operations require far
fewer workers with different skills. Meanwhile, AI deployment displaces knowledge
work on a different timeline: the layoffs are ongoing and affect a different
population than the people hired for construction. A laid-off software engineer
cannot wire a substation.

**Communities: benefits vs. burdens.**
Data centers draw power and water from communities that may receive few permanent
jobs in return. Semiconductor fabs reshape regional labor markets for a generation.
Transmission lines cross land without transferring value to the communities they
traverse. The geographic mismatch between where capital lands and who benefits
from it is a first-order question — not an afterthought.

**Ratepayers and cost socialization.**
Grid upgrades required to serve large industrial loads may be socialized across
all ratepayers. Who bears those costs — whether large load customers pay directly
or the cost is spread across residential and commercial customers — is determined
by utility commission proceedings that most affected people never know are happening.

**Decision-makers and accountability.**
The actors making consequential decisions — utility commissioners, FERC
administrative law judges, state legislators setting renewable portfolio standards,
data center site selection teams — operate with different incentives, different
information, and different accountability structures. Understanding why decisions
are made the way they are requires understanding who makes them and what they're
optimizing for.

### 5. Systems Dynamics Modeling

Systems dynamics remains a core analytical tool, but its role is to map feedback
architecture and identify leverage points — not to predict commodity demand. The
CLD and stock-and-flow approach is used to:

- Identify reinforcing and balancing loops in each supply chain node
- Test which parameters the outcome is most sensitive to
- Find tipping points where the system shifts between regimes
- Understand delay structures (capacity expansion, permitting, workforce training)

The Vensim/PySD models are tools for structural insight, not numerical prediction.
Parameter calibration matters only to the extent that it changes which loops
dominate.

---

## Case Studies

Each case study is a deep dive into one node where technology capital creates
structural transformation. The case studies share the analytical framework (capital
flow → durability → regulatory interaction → people and distribution → feedback
architecture) but are designed to stand alone as publishable pieces.

### DD-001: AI Valuations vs Physical Infrastructure Reality

*Status: Active — notebooks 01, 02, 03 in progress*

**Focus:** How AI company market valuations compare to physical infrastructure
commitments, and what the gap between financial expectations and physical reality
implies for durability.

**Key questions:**
- How much of AI company market cap is justified by physical infrastructure that
  already exists vs. demand that must materialize?
- What fraction of capex converts to structural assets vs. demand-thesis-dependent
  assets?
- How do earnings guidance patterns compare to physical buildout commitments?
- What scenarios do current valuations imply, and how plausible are they?

**Data sources:** SEC EDGAR (10-K/10-Q filings), yfinance (market data), company
earnings guidance, EIA generation data.

### DD-002: AI Capital and Grid Modernization

*Status: Active — notebooks 01, 02, 03 in progress*

**Focus:** What grid infrastructure is being built to support AI demand, who pays
for it, and what it locks in for 30-50 years.

**Key questions:**
- What generation assets are being built to serve data center demand, and what
  are their long-term implications?
- How does the interconnection queue backlog constrain where capital can actually land?
- How do corporate renewable PPAs interact with utility-scale generation planning?
- What does FERC interconnection and transmission policy actually change, and on what timeline?
- What happens to gas plants built for data centers if AI demand plateaus?

**Data sources:** EIA Forms 860/923, FERC Form 1, LBNL interconnection queue reports,
ISO/RTO queue data (PJM, ERCOT, CAISO, MISO), utility IRP filings, hyperscaler
sustainability reports.

### DD-003: AI Capital Flows and Labor Impact

*Status: Active — notebook 01 in progress*

**Focus:** The full labor picture — workforce constraints on the supply side,
knowledge-work displacement on the demand side, and the temporal mismatch between
build-phase job creation and long-term operations staffing.

**Key questions:**

*Supply constraint (infrastructure workforce):*
- What is the current workforce gap in electrical trades and power engineering?
- What are training pipeline lead times (apprenticeship → journeyman)?
- How does the aging workforce demographic interact with demand growth?

*Temporal dynamics (build vs. operate):*
- What is the ratio of build-phase to operations-phase labor for a typical data
  center campus? For a substation? For a transmission line?
- How does concentration of build activity in specific geographies (Northern
  Virginia, Central Ohio, Dallas-Fort Worth) create and then withdraw local
  economic stimulus?

*Displacement and reallocation:*
- What is the net labor effect of AI investment (infrastructure jobs created vs.
  knowledge jobs displaced)?
- What skills gap exists between displaced knowledge workers and infrastructure
  demand? What retraining pathways exist, at what lead times?
- How does labor displacement affect public and political support for AI-favorable
  infrastructure policy?

**Data sources:** BLS OEWS, BLS QCEW, BLS JOLTS, IBEW apprenticeship data, DOE
U.S. Energy and Employment Report, WARN Act filings, Census Bureau County Business
Patterns, Challenger Gray & Christmas layoff data.

### DD-004: AI Capital and Who Pays for the Grid

*Status: Scoping*

**Focus:** How utility rate proceedings, cost allocation rules, and state regulation
determine who bears the cost of grid upgrades driven by large load customers — and
what the implications are for residential and commercial ratepayers.

**Key questions:**
- How are utilities characterizing data center load growth in IRP filings, and what
  generation decisions does it justify?
- How is the cost of grid upgrades allocated between large industrial customers and
  the general ratepayer base?
- What role do state utility commissions play, and how do their decisions interact
  with FERC authority?
- Who are the communities bearing the costs of infrastructure that serves distant
  shareholders?

**Data sources:** State PUC dockets, utility IRP filings (Dominion Virginia, Georgia
Power, AEP, Duke), FERC cost allocation proceedings, EIA retail electricity price
data, community impact assessments.

### CS-4: Material Supply Chains (Future)

*Status: Not started*

**Focus:** Concentration risk, trade dynamics, and vertical integration in the
materials that underpin power infrastructure — GOES, copper, critical minerals.

**Key questions:**
- How concentrated is GOES production, and what does Cleveland-Cliffs' entry mean
  for market structure?
- Where does copper supply elasticity bind for grid buildout vs. data center
  construction?
- Which material constraints take 10+ years to resolve (mine development timelines)?

**Data sources:** USGS Mineral Commodity Summaries, ITC trade data, company filings
(Cleveland-Cliffs, Nippon Steel), NEMA shipments data.

---

## Reference Foundation

The analysis rests on sources read firsthand, not cited secondhand.
Priority reading, organized by function:

### Systems dynamics and modeling methodology
- Sterman, J. (2000). *Business Dynamics.* McGraw-Hill.
- Meadows, D. (2008). *Thinking in Systems.* Chelsea Green.
- MIT OCW 15.871 / 15.872 — Systems Dynamics I and II.

### Learning curves and technology cost dynamics
- Wright, T.P. (1936). "Factors Affecting the Cost of Airplanes." *Journal of
  the Aeronautical Sciences* 3(4).
- Rubin, E. et al. (2015). "A review of learning rates for electricity supply
  technologies." *Energy Policy* 86.
- Kavlak, G. et al. (2018). "Evaluating the causes of cost reduction in
  photovoltaic modules." *Energy Policy* 123.
- Grubler, A. (2010). "The costs of the French nuclear scale-up." *Energy Policy*
  38(9).
- Potter, B. — *Construction Physics* newsletter, esp. "How Accurate Are Learning
  Curves?" and "Where Are My Damn Learning Curves?"

### AI infrastructure and data center demand
- Grid Strategies (2023). *The Era of Flat Power Demand is Over.*
- LBNL — U.S. Data Center Energy Usage Report series (Shehabi et al.)
- IEA (2024). World Energy Outlook, electricity grids chapter.
- IEA (2023). *Electricity Grids and Secure Energy Transitions.*
- EPRI (2024). "Powering Intelligence: Analyzing AI and Data Center Energy
  Consumption."

### Grid equipment and manufacturing
- DOE (2022). *Electric Grid Supply Chain Review.*
- NREL (2024). Distribution transformer assessment.
- NEMA Electroindustry shipments statistics.
- Census Bureau Annual Survey of Manufactures, NAICS 335311.
- ABB, Siemens Energy, Hitachi Energy annual reports.

### Trade, regulatory, and policy
- FERC Order 2023 (interconnection reform, 2023).
- FERC Order 1920 (transmission planning, 2024) — under 8th Circuit challenge as
  of February 2026; verify current status before citing.
- One Big Beautiful Act (H.R.1, signed July 4, 2025) — modified IRA clean energy
  tax credits; cite by section number (§45Y, §45X, §45Q, etc.), not program name.
- Section 232 steel and aluminum tariff history and modifications.
- LBNL interconnection queue reports (annual).
- Union of Concerned Scientists (2025). PJM data center grid cost socialization.
- State utility IRP filings (Dominion Virginia, Georgia Power) — data center load
  growth characterization in generation planning.

### Energy markets and utility data
- EIA Electricity Data Browser + Forms 860, 861, 923.
- FERC Form 1 (major electric utility annual reports).
- FRED — PPI series for transformers, copper, steel.
- NERC Long-Term Reliability Assessments (annual).

### Labor markets and workforce dynamics
- BLS Occupational Employment and Wage Statistics (OEWS).
- BLS JOLTS — job openings and separations in construction vs. information sectors.
- IBEW apprenticeship completion data.
- DOE (2024). U.S. Energy and Employment Report (USEER).
- Challenger, Gray & Christmas — tech layoff tracking data.
- WARN Act filings — advance layoff notification data by state and industry.
- Autor, D. (2024). "Applying AI to Rebuild Middle Class Jobs." NBER Working Paper.

### Historical analogies
- Dot-com/telecom overbuilding (1996-2003): fiber overcapacity, eventual absorption.
- Shale boom-bust (2010-2020): commodity capital cycle dynamics.
- French nuclear scale-up (1970-2000): negative learning from regulatory ratcheting.

---

## Current Status and Phased Plan

### Active work (as of February 2026)

- **DD-001** (AI Valuations vs Physical Infrastructure Reality): Three notebooks
  in progress — markets/money, conversion reality, risk and durability. Framework
  and data pipelines established.
- **DD-002** (AI Capital and Grid Modernization): Three notebooks in progress —
  what's getting built, who benefits, feedback architecture. Grid data pipelines
  established.
- **DD-003** (AI Capital Flows and Labor Impact): First notebook in progress.
- **DD-004** (Who Pays for the Grid): Scoping phase — data sources identified,
  notebook structure planned.

### Phase 1: Publish DD-001 and DD-002 (Current)

- Tighten numerical claims in DD-001 and DD-002 against primary data
- Data-ground all prose values (replace hardcoded numbers with stats cells)
- Strengthen references with specific sources, dates, and section numbers
- Verify all policy references for post-One Big Beautiful Act accuracy
- Publish both as self-contained pieces

**Deliverable:** Two publishable analyses on AI capital vs. physical reality
and grid modernization.

### Phase 2: Complete DD-003 and scope DD-004

- DD-003: Full labor picture — supply constraints, displacement, temporal mismatch
- DD-004: Rate proceeding analysis — who pays, which communities, which regulators
- Build out data pipelines for BLS, state PUC, FERC cost allocation data

**Deliverable:** Labor impact analysis; utility regulation deep dive.

### Phase 3: Synthesis and CS-4 (Materials)

- CS-4: Materials supply chain — GOES, copper, critical minerals
- Cross-case synthesis: which infrastructure commitments are durable?
- Integrated regulatory interaction analysis across all case studies

**Deliverable:** Complete case study set; integrated synthesis.

### Phase 4: Publication

- Final integrated analysis with people-first narrative thread
- Systems dynamics synthesis: feedback architecture across all supply chain nodes
- Publication-ready output

---

## Tools

| Tool | Purpose |
| :--- | :--- |
| **PySD / Vensim PLE** | Systems dynamics modeling (feedback architecture, not prediction) |
| **Marimo** | Reactive notebooks for analysis and publication drafts |
| **DuckDB / dlt** | Data pipelines and local analytical database |
| **FRED / fredapi** | Economic time series (PPI, production indices) |
| **yfinance** | Financial data (company filings, commodity prices) |
| **pandas / matplotlib / flowmpl** | Data analysis and visualization |
| **ruff / mypy** | Code quality |

Bayesian (PyMC) and regime switching (statsmodels) remain available for specific
case studies that need them, but are not prerequisites for the core analysis.

---

## Constraints

- Zero budget — all tools and data sources must be freely accessible
- Learning project — building analytical capability alongside the analysis
- Aligned with Sprint 1 goals (Feb 9 - May 3, 2026)
- Publication-oriented — every case study should be writable as a standalone piece
- Policy claims must be verified, dated, and cited by statutory section number
