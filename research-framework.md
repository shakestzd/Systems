# Research Framework

## Core Question

AI companies are deploying over $200 billion per year in capital expenditure. That
capital converts into physical infrastructure — power plants, transmission lines,
transformer factories, data centers, semiconductor fabs. Unlike the capital itself,
which can be written down in a quarterly earnings report, the infrastructure is
durable. It reshapes supply chains, labor markets, trade patterns, and grid topology
for decades.

**Where does AI capex land in the physical economy, what does it lock in, and how
do current regulatory decisions amplify or distort those outcomes?**

This is not a commodity demand forecast. It is an analysis of how capital flows
create infrastructure path dependencies — commitments that persist regardless of
whether the investment thesis that justified them holds.

---

## Analytical Framework

### 1. Capital Flow Mapping

Trace $1 of hyperscaler capex through the physical supply chain. Identify where
the capital converts from financial commitment to physical asset.

```
AI CapEx ($200B+/year)
    │
    ├── Power Infrastructure (~40-50% of site cost)
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
vs. colo expansion vs. edge). The key insight is that **power infrastructure
dominates** — and power infrastructure has the longest asset life and the most
complex regulatory entanglement.

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

Current regulatory decisions shape where and how AI capital converts to
infrastructure. Four dimensions:

**Trade policy and tariffs.**
Tariffs on transformers, steel (Section 232), and other equipment create a time
horizon mismatch: tariffs are administrative actions reversible within a single
administration, but manufacturing capacity requires 15-20 year investment horizons.
The result is not reshoring — it is a price transfer from buyers to existing
producers, followed by permanent price floor establishment through revealed
willingness-to-pay. When tariffs are removed, prices do not fully revert. The
delta is pure capital loss — the buyer paid more without gaining supply chain
resilience or domestic capacity.

The exception is vertical integration that doesn't depend on tariff protection
(e.g., Cleveland-Cliffs' Weirton plant, which is hedged on structural demand and
GOES supply control, not trade policy).

**Energy and environmental policy.**
Accelerated permitting for gas generation to meet data center demand locks in
30-40 year fossil assets. Simultaneously, data center operators are signing the
largest corporate renewable PPAs in history. The policy environment determines
which generation mix gets built, and that choice outlives multiple administrations.
Rolling back clean energy mandates while AI accelerates the largest grid buildout in
decades creates a tension: the capital flows regardless of policy, but *what kind*
of infrastructure it builds depends on the regulatory moment.

**FERC and utility regulation.**
Cost allocation rules determine who pays for grid upgrades driven by data center
demand. FERC's December 2025 order requiring 100% cost allocation to large load
customers for co-location upgrades is a structural shift. Interconnection queue
reform (or failure to reform) determines whether new generation can reach the grid
at all — currently, the average queue wait is 4-5 years, which is itself a binding
constraint on AI buildout.

**Industrial policy.**
The IRA, CHIPS Act, and Defense Production Act authorizations for grid equipment
create subsidy flows that interact with private AI capital. These policies have
different durability profiles — the IRA's tax credits are statutory (harder to
repeal), while DPA authorizations are executive (easier to reverse).

**Labor displacement and political economy.**
AI capital flows simultaneously create and destroy jobs, but on different
timelines, in different skill categories, and in different geographies:

- **Build phase** — High demand for construction trades, electricians, welders,
  heavy equipment operators. This demand is temporary and front-loaded. Once a
  data center or substation is built, the construction workforce moves on or
  disperses.
- **Operations phase** — Much lower headcount with different skills (facility
  managers, maintenance technicians, network engineers). The transition from
  build to operations is a structural drop in labor demand at each site.
- **Displacement** — AI deployment automates knowledge work (software engineering,
  data analysis, content, administration). These layoffs are ongoing, visible, and
  affect a different population than the people hired for construction.
- **Skills mismatch** — A laid-off software engineer cannot wire a substation.
  Retraining pathways exist (apprenticeship programs, community college trades
  programs) but have 2-4 year lead times, and there is no guarantee of uptake.

The net labor effect has a time structure: during the build phase (roughly
2024-2032), infrastructure job creation may partially offset knowledge-work
displacement. After the build phase, the infrastructure requires only maintenance-
level labor while AI continues displacing knowledge work. The long-term net effect
could be strongly negative.

This matters for the regulatory environment because public tolerance for
AI-favorable policy (fast permitting, tax incentives, relaxed environmental
review) depends on whether people perceive AI as creating or destroying jobs
*for them.* If the visible effect is tech layoffs while infrastructure jobs are
temporary, geographically concentrated, and inaccessible to the displaced
population, the political environment shifts toward restriction — which feeds
back into every other regulatory dimension.

### 4. Systems Dynamics Modeling

Systems dynamics remains a core analytical tool, but its role shifts from
"predict commodity demand" to "map feedback architecture and identify leverage
points." The CLD and stock-and-flow approach is used to:

- Identify reinforcing and balancing loops in each supply chain node
- Test which parameters the outcome is most sensitive to
- Find tipping points where the system shifts between regimes
- Understand delay structures (capacity expansion, permitting, workforce training)

The Vensim/PySD models are tools for structural insight, not numerical prediction.
Parameter calibration matters only to the extent that it changes which loops
dominate.

---

## Case Studies

Each case study is a deep dive into one supply chain node where AI capital creates
structural transformation. The case studies are independent but share the analytical
framework (capital flow → durability → regulatory interaction → feedback architecture).

### CS-1: Transformer Manufacturing and Grid Equipment

*Status: Draft complete (notebooks 01 and 02)*

**Focus:** How AI-driven demand is reshaping the transformer supply chain through
vertical integration, standardization pressure, trade dynamics, and labor constraints.

**Key findings so far:**
- Distribution transformers are a credible candidate for learning curves; LPTs are not
- Cleveland-Cliffs' vertical integration is a structural bet independent of tariffs
- The system sits near a tipping point between scarcity equilibrium and learning-curve regime
- Labor and trade policy are binding constraints not captured by the initial model

**Needs:**
- Validate which transformer segment AI demand actually concentrates in (LPT vs. distribution)
- Replace PPI proxy with actual production volume data (NEMA shipments, Census NAICS 335311)
- Ground the regulatory analysis in DOE rulemaking history
- Strengthen references with primary sources

### CS-2: Power Generation Mix and Asset Lock-in

*Status: Not started*

**Focus:** What generation assets are being built to serve data center demand, and
what are their 30-40 year implications?

**Key questions:**
- What fraction of new gas capacity is driven by data center demand vs. general load growth?
- How do corporate renewable PPAs interact with utility-scale generation planning?
- What happens to gas plants built for data centers if AI demand plateaus in 2032?
- How does the permitting environment determine the generation mix?

**Data sources:** EIA Form 860 (generator-level), EIA-923 (generation), FERC Form 1
(utility capex), hyperscaler sustainability reports, state PUC filings.

### CS-3: Grid Interconnection and Transmission

*Status: Not started*

**Focus:** The interconnection queue as a binding constraint on AI infrastructure,
and how queue reform (or its absence) shapes where capital physically lands.

**Key questions:**
- What is the current interconnection queue backlog by region and project type?
- How does queue wait time interact with data center site selection?
- What does FERC interconnection reform actually change, and on what timeline?
- How do transmission buildout decisions create 50-year grid topology lock-in?

**Data sources:** LBNL interconnection queue reports, FERC dockets, ISO/RTO queue
data (PJM, ERCOT, CAISO, MISO), Grid Strategies reports.

### CS-4: Material Supply Chains (GOES, Copper, Critical Minerals)

*Status: Not started*

**Focus:** Concentration risk, trade dynamics, and vertical integration in the
materials that underpin power infrastructure.

**Key questions:**
- How concentrated is GOES production, and what does Cleveland-Cliffs' entry mean
  for the market structure?
- How do Section 232 steel tariffs interact with transformer manufacturing costs?
- Where does copper supply elasticity bind — and is it the same constraint for
  grid buildout as for data center construction?
- Which material constraints take 10+ years to resolve (mine development timelines)?

**Data sources:** USGS Mineral Commodity Summaries, ITC trade data, Cleveland-Cliffs
and Nippon Steel filings, NEMA shipments data, copper industry reports.

### CS-5: Labor Market Dynamics

*Status: Not started*

**Focus:** The full labor picture — infrastructure workforce constraints on the
supply side, knowledge-work displacement on the demand side, and the temporal
mismatch between build-phase job creation and long-term operations staffing.

**Key questions:**

*Supply constraint (infrastructure workforce):*
- What is the current workforce gap in electrical trades and power engineering?
- What are the training pipeline lead times (apprenticeship → journeyman)?
- How does the aging workforce demographic interact with demand growth?
- Where does automation substitute for labor, and where doesn't it?

*Temporal dynamics (build vs. operate):*
- What is the ratio of build-phase to operations-phase labor for a typical data
  center campus? For a substation? For a transmission line?
- What happens to construction workforces when the build phase ends in a region?
- How does the concentration of build activity in specific geographies (Northern
  Virginia, Central Ohio, Dallas-Fort Worth) create and then withdraw local
  economic stimulus?

*Displacement and reallocation:*
- What is the net labor effect of AI investment (infrastructure jobs created vs.
  knowledge jobs displaced)?
- What is the skills gap between displaced knowledge workers and infrastructure
  demand? What retraining pathways exist, and what are their lead times and
  completion rates?
- How does labor displacement affect public and political support for AI-favorable
  infrastructure policy?

*Cross-cutting:*
- How do immigration policies affect the supply of both construction trades and
  tech workers?
- What is the geographic mismatch between where jobs are created (data center
  corridors) and where jobs are lost (tech hubs)?

**Data sources:** BLS Occupational Outlook Handbook, BLS QCEW (Quarterly Census of
Employment and Wages), BLS JOLTS (Job Openings and Labor Turnover Survey), NEMA
workforce surveys, IBEW apprenticeship data, DOE workforce reports, Challenger
Gray & Christmas layoff tracker, WARN Act filings, Census Bureau County Business
Patterns.

---

## Reference Foundation

The analysis rests on sources that need to be read firsthand, not cited secondhand.
Priority reading list, organized by function:

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
- Henderson, B. (1968). *Perspectives on Experience.* BCG.

### AI infrastructure and data center demand
- Grid Strategies (2023). *The Era of Flat Power Demand is Over.*
- LBNL — U.S. Data Center Energy Usage Report series (Shehabi et al.)
- IEA (2024). World Energy Outlook, electricity grids chapter.
- IEA (2023). *Electricity Grids and Secure Energy Transitions.*
- Goldman Sachs (2024). "AI, data centers, and the coming US power demand surge."
- EPRI (2024). "Powering Intelligence: Analyzing AI and Data Center Energy
  Consumption."

### Transformer and grid equipment markets
- DOE (2022). *Electric Grid Supply Chain Review.*
- DOE Transformer Rulemaking Docket (EERE-2019-BT-STD-0018).
- NREL (2024). Distribution transformer assessment.
- Wood Mackenzie (2025). Power transformer supply deficit analysis.
- Cleveland-Cliffs investor presentations and earnings calls (2024-2025).
- ABB, Siemens Energy, Hitachi Energy, Schneider Electric annual reports.
- NEMA Electroindustry shipments statistics.
- Census Bureau Annual Survey of Manufactures, NAICS 335311.

### Trade, regulatory, and policy
- FERC Order on large-load cost allocation (December 2025).
- DOE efficiency standards final rule (2024) for distribution transformers.
- Section 232 steel and aluminum tariff history and modifications.
- LBNL interconnection queue reports (annual).
- Union of Concerned Scientists (2025). PJM data center grid cost socialization.

### Energy markets and utility data
- EIA Electricity Data Browser + Forms 860, 861, 923.
- FERC Form 1 (major electric utility annual reports).
- FRED — PPI series for transformers, copper, steel.
- S&P Global / IHS Markit power market data.

### Labor markets and workforce dynamics
- BLS Occupational Employment and Wage Statistics (OEWS) — electrical trades,
  construction, power engineering occupations.
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

## Phased Plan

### Phase 1: Tighten CS-1 and establish the framework (Current)

- Strengthen the transformer case study with primary data sources
- Replace the PPI proxy with NEMA or Census production data
- Validate which transformer segment AI demand concentrates in
- Finalize the durability taxonomy and regulatory interaction framework
- Publish CS-1 as a self-contained piece

**Deliverable:** One publishable analysis: "Where does AI capex land in the grid?"

### Phase 2: Capital flow mapping and CS-2

- Trace hyperscaler capex through to physical infrastructure commitments
- Begin CS-2 (power generation mix) with EIA and FERC data
- Map the generation asset lock-in problem
- Develop the tariff / trade policy analysis with specific data

**Deliverable:** Capital flow map + generation mix analysis

### Phase 3: CS-3 through CS-5

- Grid interconnection queue analysis (LBNL data)
- Material supply chain deep dive (USGS, trade data, company filings)
- Labor market constraints (BLS, NEMA workforce)

**Deliverable:** Complete case study set

### Phase 4: Synthesis and publication

- Cross-case synthesis: which infrastructure commitments are durable?
- Regulatory interaction analysis across all case studies
- Final publication as an integrated analysis

**Deliverable:** Integrated research output suitable for publication

---

## Tools

| Tool | Purpose |
| :--- | :--- |
| **PySD / Vensim PLE** | Systems dynamics modeling (feedback architecture, not prediction) |
| **Marimo** | Reactive notebooks for analysis and publication drafts |
| **FRED / fredapi** | Economic time series (PPI, production indices) |
| **yfinance** | Financial data (company filings, commodity prices) |
| **pandas / matplotlib** | Data analysis and visualization |
| **ruff / mypy** | Code quality |

Bayesian (PyMC) and regime switching (statsmodels) remain available as tools if a
specific case study needs them, but they are not prerequisites for the core analysis.

---

## Constraints

- Zero budget — all tools and data sources must be freely accessible
- Learning project — building analytical capability alongside the analysis
- Aligned with Sprint 1 goals (Feb 9 - May 3, 2026)
- Publication-oriented — every case study should be writable as a standalone piece
