# Research Framework

## 1. Systems Dynamics Model

### Purpose
Map the causal feedback loops between AI capital expenditure and downstream commodity/infrastructure demand. Systems dynamics captures the non-linear, delayed, and reinforcing/balancing feedback effects that simple linear models miss.

### Core Causal Loop Structure
```
AI Commercial Success
    ├──> AI CapEx (hyperscaler spending)
    │       ├──> Data Center Construction
    │       │       ├──> Electricity Demand
    │       │       ├──> Water Demand (cooling)
    │       │       ├──> Real Estate / Land Use
    │       │       └──> Construction Materials
    │       ├──> Semiconductor Demand
    │       │       ├──> Critical Minerals (silicon, rare earths, copper)
    │       │       └──> Fab Capacity Investment
    │       └──> Network Infrastructure
    │               ├──> Fiber Optic Demand
    │               └──> Edge Computing Buildout
    │
    ├──> Grid Capacity Constraints (balancing loop)
    │       ├──> Utility CapEx Response
    │       ├──> Renewable Energy Buildout
    │       └──> Permitting / Regulatory Delays
    │
    └──> Supply Chain Bottlenecks (balancing loop)
            ├──> Mining Capacity Expansion (long lead times)
            ├──> Price Signals → Substitution Effects
            └──> Recycling / Secondary Supply
```

### Key Feedback Loops to Model
1. **Reinforcing: AI success → more CapEx → more infrastructure → enables more AI adoption**
2. **Balancing: Grid constraints → higher energy costs → reduced data center margins → slower buildout**
3. **Balancing: Mineral scarcity → higher input costs → slower semiconductor production → CapEx delays**
4. **Reinforcing: Data center cluster effects → utility investment → improved grid → attracts more data centers**
5. **Balancing: Water scarcity → regulatory pressure → cooling technology shifts → design cost increases**

### Tools
- **Primary:** Python with [PySD](https://pysd.readthedocs.io/) library (integrates with data science stack)
- **Alternative:** Vensim PLE (free for learning, industry standard GUI)
- **Learning resource:** MIT OpenCourseWare -- System Dynamics (15.871/15.872)

---

## 2. Bayesian Inference Layer

### Purpose
Many parameters in the systems dynamics model are uncertain and contested. Bayesian methods let us formally represent this uncertainty, update estimates as new data arrives, and propagate uncertainty through to conclusions.

### Key Uncertain Parameters
| Parameter | Why It's Uncertain |
|---|---|
| AI-specific share of data center growth | Hyperscalers report total CapEx but don't break out AI vs. cloud vs. enterprise |
| Energy intensity per AI workload | Varies by model size, inference vs. training, hardware generation |
| Grid expansion timeline | Depends on permitting, utility investment cycles, political environment |
| Mineral supply elasticity | New mines take 7-15 years; recycling capacity is nascent |
| Water consumption per MW of cooling | Varies by climate, cooling technology, and local water availability |

### Approach
1. Define prior distributions for each uncertain parameter based on published estimates and expert ranges
2. Use available data (EIA reports, SEC filings, industry surveys) as likelihood functions
3. Compute posterior distributions via MCMC sampling
4. Feed posterior parameter distributions into the systems dynamics model to produce probabilistic output ranges

### Tools
- **PyMC** or **Stan** (via PyStan/CmdStanPy) for Bayesian modeling
- **ArviZ** for posterior diagnostics and visualization
- **Learning resource:** "Statistical Rethinking" by Richard McElreath (book + lectures)

---

## 3. Markov Regime Switching

### Purpose
Rather than picking a single scenario, model the economy as existing in one of several "regimes" with probabilistic transitions between them. This captures the reality that AI's trajectory is uncertain and can shift.

### Proposed Regimes
| Regime | Description | Commodity Demand Implications |
|---|---|---|
| **AI Boom** | Continued exponential CapEx growth, strong commercial returns | Maximum demand pressure across all sectors |
| **AI Plateau** | CapEx stabilizes, AI becomes utility-like infrastructure | Sustained but flattening demand; grid and minerals remain constrained |
| **AI Bust** | Commercial disappointment, CapEx cuts | Demand drops for AI-specific inputs; but grid/data center infrastructure persists for general cloud |

### Key Analytical Questions
- Which commodities show **durable demand across all three regimes**? (These are the "regime-robust" bets)
- Which commodities are **regime-sensitive**? (High demand in boom, collapse in bust)
- What are the **transition probabilities** between regimes, and how do they shift based on observable signals?

### Approach
1. Define state-dependent demand equations for each commodity sector under each regime
2. Estimate transition probabilities using historical analogies (dot-com, shale boom, crypto) and current market signals
3. Run Monte Carlo simulations across regime paths to generate demand probability distributions
4. Identify regime-robust vs. regime-sensitive commodity exposures

### Tools
- **statsmodels** `MarkovRegression` / `MarkovAutoregression` for regime switching models
- **hmmlearn** for hidden Markov model implementation
- Custom simulation code for Monte Carlo regime path generation

---

## 4. Sector Analysis Approach

For each of the five key sectors, the analysis will address:

### Electricity Generation and Grid Capacity
- Current data center share of US/global electricity consumption
- Projected growth under each regime
- Grid expansion bottlenecks (permitting, transformer lead times, interconnection queues)
- Implications for natural gas, renewables, nuclear
- Key question: Does grid investment become self-sustaining once started, regardless of AI trajectory?

### Water Consumption and Cooling Infrastructure
- Water intensity of different cooling technologies (evaporative, liquid, air)
- Geographic concentration of data centers vs. water stress
- Regulatory risk (water rights, drought restrictions)
- Key question: Does water scarcity become a binding constraint that redirects data center geography?

### Critical Minerals
- Copper: grid expansion + data center construction + EV overlap
- Lithium: battery storage for grid reliability
- Rare earths: permanent magnets in generators, hard drives
- Silicon: semiconductor feedstock
- Key question: Which minerals face supply constraints that take 10+ years to resolve?

### Fiber Optic and Network Backbone
- Bandwidth demand from AI inference (serving models to users)
- Edge computing buildout requirements
- Subsea cable investment
- Key question: Is network infrastructure demand a durable tailwind regardless of which AI applications succeed?

### Real Estate and Construction (Data Centers)
- Data center construction pipeline and vacancy rates
- Geographic clustering patterns and constraints
- Construction material demand (concrete, steel, specialized electrical equipment)
- Key question: Are data centers becoming general-purpose cloud infrastructure that persists post-AI-hype?

---

## 5. Phased Learning Plan

### Phase 1: Foundation (Weeks 1-4)
**Goal:** Literature review + basic systems dynamics competency
- [ ] Complete MIT OCW systems dynamics introductory materials
- [ ] Read IEA data center energy reports (2023, 2024 editions)
- [ ] Read key papers on AI infrastructure energy demand
- [ ] Build a simple causal loop diagram (CLD) of AI → energy → commodities
- [ ] Get PySD running with a toy model
- [ ] Collect and organize bookmarks for all data sources

**Deliverable:** Causal loop diagram + annotated bibliography

### Phase 2: Data and Bayesian Foundations (Weeks 5-8)
**Goal:** Data collection + Bayesian methods competency
- [ ] Pull EIA electricity generation and consumption data
- [ ] Pull USGS mineral commodity summaries
- [ ] Pull SEC CapEx data for MSFT, GOOG, AMZN, META
- [ ] Build exploratory visualizations of key trends
- [ ] Work through "Statistical Rethinking" chapters 1-8
- [ ] Build first Bayesian parameter estimation model (e.g., estimate AI share of data center energy)

**Deliverable:** Cleaned datasets + exploratory analysis notebook + first Bayesian model

### Phase 3: Model Integration (Weeks 9-12)
**Goal:** Build the integrated systems dynamics + Bayesian + regime switching model
- [ ] Convert CLD to stock-and-flow model in PySD
- [ ] Integrate Bayesian posterior distributions as parameter inputs
- [ ] Build Markov regime switching model with historical calibration
- [ ] Connect regime states to demand equations in the systems dynamics model
- [ ] Run initial simulations and debug

**Deliverable:** Working integrated model with preliminary results

### Phase 4: Analysis and Write-up (Weeks 13-16)
**Goal:** Run scenarios, extract insights, produce final output
- [ ] Run Monte Carlo simulations across regime paths
- [ ] Identify regime-robust vs. regime-sensitive commodities
- [ ] Sensitivity analysis on key uncertain parameters
- [ ] Write up findings as a research report
- [ ] Create presentation-ready visualizations
- [ ] Prepare portfolio-ready summary

**Deliverable:** Research report + model code + presentation materials
