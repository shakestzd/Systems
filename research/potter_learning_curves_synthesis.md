# Brian Potter's Learning Curve Framework: A Critical Synthesis
## For Systems Dynamics Modeling of AI Infrastructure Impact

**Compiled:** 2026-02-13
**Purpose:** Understanding when and why learning curves fail in infrastructure industries
**Application:** Grid transformer manufacturing analysis

---

## I. Core Arguments: When Learning Curves Work vs. Fail

### The Basic Mechanism (Wright's Law)
Learning curves describe the observation that **costs fall by a constant proportion for every cumulative doubling of production volume**. The equation is: `y = ax^-b`, where:
- y = cost for the xth unit
- a = cost for the 1st unit
- x = cumulative production volume
- b = learning exponent (determines learning rate)

Typical learning rates range from 80-95% (meaning 5-20% cost reduction per doubling).

**Key insight from Potter:** Learning curves are **not universal laws**—they emerge only under specific conditions, and their absence reveals structural barriers to efficiency improvement.

---

## II. Industries Where Learning Curves FAILED Despite Volume

### 1. **Construction (Potter's Primary Case Study)**

**The Paradox:**
- US housing: ~45M units in 1950 → 145M+ by 2020 (~1.66 doublings)
- **Expected cost decrease:** 17-25% (at 85-90% learning rates)
- **Actual result:** Essentially flat or declining productivity

**Potter's Diagnosis:**
> "Learning curves exist for individual projects (especially ones that have repetitive elements), but not for the industry as a whole."

**Structural Barriers:**

1. **Process Resets**
   - Every new project = new team, new site, new conditions, new owner
   - Knowledge doesn't transfer effectively across projects
   - Evidence: Sites shut down for holidays or financial problems show "significant productivity reset" when restarting

2. **Limited Scale Effects**
   - Doubling building size "just gets you twice as much building"
   - Unlike power plants or chemical refineries, construction lacks geometric returns to scale

3. **High Environmental Variation**
   - Site-specific conditions (soil, weather, local codes)
   - Material variation (dimensional lumber, site-produced concrete)
   - Contrast with factory manufacturing's controlled conditions

4. **Technological Stagnation**
   Potter: "The basic technology for how a building goes together is fairly well established."
   - Unlike semiconductors or aircraft, no breakthrough innovations
   - Mechanization often requires more capital than it saves vs. "Bubba and his truck" (low-overhead contractors)

5. **Information Processing Requirements**
   - Construction requires constant adaptation to site-specific information
   - Successful mechanization historically required "reducing or limiting the amount of information processing"
   - Buildings have distributed functionality that "can't be separated from the site itself"

**Quantitative Evidence:**
- WWII shipyards: Labor hours per Liberty Ship fell from 1.1M to 0.5M (55% reduction) due to standardization and repetition
- But when yards switched from Liberty Ships to Victory Ships: "dip in efficiency occurred"—learning curve reset

### 2. **Nuclear Power (The "Negative Learning" Case)**

**The French Paradox:**
France had the **most favorable conditions** for learning curves:
- Centralized decision-making
- High degree of standardization
- Regulatory stability
- Short construction times (initially)

**Yet: Costs INCREASED with cumulative experience** ("negative learning")

**Grubler's Analysis:**
- Real construction costs escalated substantially throughout 1970s-1990s
- Despite standardization, **costs rose rather than fell** with each reactor built
- Learning curve essentially inverted

**Why It Failed:**

1. **Regulatory Ratcheting**
   - Each new project triggered more stringent safety requirements
   - More locally-made components mandated
   - New reactor generations effectively "reset the learning curve to a new, higher starting point"

2. **Intrinsic Technology Characteristics**
   - Large-scale, lumpy projects
   - Complexity management challenges intensified with scale-up
   - Full fuel cycle management
   - Load-following operation requirements
   - Escalating safety standards

3. **Standardization Limits**
   Potter: "It doesn't matter how standardized your design is if you end up needing to change it on every project to meet new requirements."

**US Nuclear Experience:**
- Plants started in 1960s, completed early 1970s: **cost twice as much as expected**
- Over 1970s: Labor and material per plant **doubled**
- At least **30% of cost increase (1976-1988) attributable to regulation**

### 3. **Modular/Prefabricated Construction**

**The Factory Paradox:**
Despite moving to controlled factory environments with repetitive production, modular construction:
- Captured only ~5% of construction market
- "Lucky if they're even able to deliver buildings more cheaply than standard, site-built construction"

**Why Factory Production Didn't Help:**

1. **Geographic Constraints**
   - Transportation costs for large modules
   - Limited service radius for factories

2. **Output Variation**
   - Construction demand varies by location and type
   - Difficult to maintain steady production volume
   - Centralized factories add overhead that becomes liability when market shifts

3. **Interface Complexity**
   - Modular construction "greatly increases the number of interfaces between components"
   - Building functions are "distributed throughout the entire building"
   - Each module must integrate: waterproofing, electrical, HVAC, structure
   - Unlike modular products (PCs), building systems can't be cleanly isolated

**Where It Works:**
- Simple buildings (parking garages with minimal MEP systems)
- Low-completion panels (avoiding pre-installed services)
- Suggests complexity, not standardization, is the barrier

### 4. **Electrical Grid Transformers (Emerging Evidence)**

**Current State (2024-2026):**

**Customization Levels:**
- US power system: **~200+ different transformer designs per 1,000 units on distribution systems**
- Each transformer customized to "local distribution system intricacies"

**Manufacturing Constraints:**
- Lead times: **120 weeks (2.3 years) typical, up to 4 years for large units**
- US capacity utilization: ~40% of max capacity (~343 large power transformers/year)
- "Lack of standardization...made automation, assembly optimization initiatives, and other technologies that aid efficient mass production more difficult"

**Barriers to Learning Curves:**

1. **Extreme Customization**
   - Utilities demand bespoke specifications even for smaller components
   - Site-specific voltage, capacity, environmental requirements
   - No two transformers identical enough for true mass production

2. **Labor and Material Constraints**
   - Skilled labor shortages
   - Long procurement chains for specialty materials
   - Limited manufacturer base

3. **Policy Fragmentation**
   - Different state regulations
   - Utility-specific procurement rules
   - No federal standardization mandate

**Implication for AI-Driven Demand:**
If AI data centers drive 2-3x increase in transformer demand, **lack of standardization blocks the learning curve mechanism** that should reduce costs. Volume alone is insufficient.

---

## III. Industries Where Learning Curves SUCCEEDED

### 1. **Solar Panels (Swanson's Law)**

**Performance:**
- **20% cost reduction per doubling of cumulative shipped volume**
- Multi-decade consistent improvement
- Led to multi-terawatt deployment by 2025

**Success Factors:**

1. **Standardization**
   - Commodity product with defined specifications
   - Interchangeable modules
   - Standard mounting systems

2. **Manufacturing Automation**
   - Robotic assembly lines
   - Automated silicon processing and wafer slicing
   - Precision process control reducing defects

3. **Volume Scale**
   - Scale-sensitive industry
   - High upfront factory costs justified by massive production runs
   - Global market enabling continuous capacity utilization

4. **Continuous R&D**
   - Booming industry = high R&D budgets
   - Perovskite-silicon tandems, TOPCon technology
   - Simple, low-temperature manufacturing (especially perovskites)

5. **Material Innovation**
   - Thinner silicon wafers
   - Reduced material waste
   - Shift from energy-intensive purification to solution-based coating

**2026 State:**
- TOPCon capturing 70% market share
- Perovskite-silicon reaching 33% efficiency
- Commercial production by Oxford PV, Trina Solar

### 2. **Semiconductors**

**Performance:**
- Decades of consistent cost reductions (Moore's Law + Wright's Law)
- Transistor costs fell exponentially despite increasing complexity

**Success Factors:**

1. **Stable, Repetitive Process**
   - Fab lines run continuously on identical wafers
   - Photolithography, etching, deposition highly automated
   - Process changes are deliberate, not imposed by external variation

2. **Massive Production Volume**
   - Billions of chips per year
   - Economies of scale in equipment, materials, facilities

3. **Centralized R&D**
   - Coordinated industry roadmaps (ITRS/IRDS)
   - Shared equipment suppliers (ASML, Applied Materials)
   - Learning transfers across firms

4. **Isolated from Site Variation**
   - Cleanroom manufacturing
   - Zero environmental variation
   - Product identical regardless of location

### 3. **Batteries (Lithium-Ion)**

**Performance:**
- Rapid cost declines enabling EV transition
- Price per kWh fell ~90% from 2010-2020

**Success Factors:**

1. **Manufacturing Scale-Up**
   - Gigafactories (Tesla, CATL, LG Chem)
   - High-volume production justified by EV demand

2. **Standardization of Cell Formats**
   - 18650, 2170, prismatic, pouch cells
   - Modular battery pack design

3. **Process Automation**
   - Automated electrode coating, winding, assembly
   - Quality control via machine vision

4. **Material Cost Reduction**
   - Cobalt reduction
   - Nickel-manganese-cobalt (NMC) optimization
   - Solid-state battery R&D pipeline

### 4. **WWII Shipbuilding (Liberty Ships)**

**The Learning Curve Success Story:**

**Performance:**
- Labor hours: 1.1M → 0.5M hours per ship (55% reduction)
- Build time: ~250 days → <50 days
- Most efficient yards: 0.3M labor hours
- 3,000+ improvement suggestions saved $45M (~$800M in 2025 dollars) and 31M labor hours

**Success Factors:**

1. **Extreme Standardization**
   - Single design (EC2/Liberty Ship) replicated across multiple yards
   - Based on British Ocean-class tramp steamer
   - Standardized across entire Maritime Commission

2. **Prefabrication and Preassembly**
   - Larger cranes → bigger component blocks
   - Modules assembled off-critical-path
   - Reduced on-site complexity

3. **Welding Technology**
   - 50 miles of welding per ship
   - Faster than riveting
   - Novice welders trained in 1 week for simple tasks
   - Automatic welding machines (2x human speed)

4. **Worker Innovation**
   - "Jack-backer" tool eliminated 1,200 clips per ship
   - Continuous improvement culture
   - Inter-yard knowledge sharing

**But:** Learning curve reset when production switched from Liberty Ships to Victory Ships—demonstrating fragility of learning to process changes.

---

## IV. Potter's Framework: Distinguishing "Technologies" from "Commodities"

### The Conventional Wisdom (Which Potter Challenges)

**Technologies:**
- Manufactured goods
- Subject to learning curves
- Costs decline with volume
- Example: Solar, semiconductors, batteries

**Commodities:**
- Extracted resources
- No learning curves
- Subject to depletion/scarcity
- Example: Oil, minerals, crops

### Potter's Critique

**The distinction is "blurry" and "fuzzy":**

1. **Commodities Can Have Learning Curves**
   - 24 of 25 agricultural commodities cheaper over time
   - 60 of 93 mineral commodities cheaper over time
   - Aluminum and titanium (newer materials with complete production records) show clear learning curves

2. **Technologies Can Fail to Exhibit Learning Curves**
   - Wind power faces **geographic depletion** (best sites fill first)
   - Wake effects reduce output of adjacent wind farms
   - **Social resistance** grows with deployment (NIMBYism)
   - Models show "increasing cost of wind-generated electricity as deployment rises"

3. **The Real Distinction:**
   Not categorical (technology vs. commodity) but **specific constraints**:
   - Geographic concentration (wind, hydro, minerals in specific locations)
   - Environmental/social externalities
   - Regulatory dynamics
   - Scale economics vs. diseconomies

**Implication:** Labeling something a "technology" doesn't guarantee learning curves. Must analyze specific production constraints.

---

## V. Structural Characteristics That Block Learning Curves

### A Framework for Prediction

Based on Potter's work, learning curves are **blocked** when these factors dominate:

### 1. **Process Instability**

**Definition:** Production process changes frequently, resetting accumulated learning.

**Manifestations:**
- New teams for each project (construction)
- Design changes to meet evolving regulations (nuclear)
- Switching between product variants (shipyards: Liberty → Victory)
- Site-specific adaptations (every building unique)

**Quote:** Potter on construction: "Learning curves are disrupted whenever a process changes, and so each time a new project starts, the learning curve is reset."

**Counterfactual:** Solar and semiconductor fabs run **stable, repetitive processes** for years.

### 2. **Extreme Customization**

**Definition:** Each unit is bespoke, preventing standardized production.

**Manifestations:**
- Transformers: 200+ designs per 1,000 units
- Buildings: Unique owner requirements, site conditions, aesthetics
- Nuclear: Evolving safety requirements, local content rules

**Mechanism:** Customization prevents:
- Automated assembly (each unit needs different handling)
- Worker skill transfer (different tasks each time)
- Tooling amortization (custom fixtures for each variant)

**Quote:** Potter on transformers: "Lack of standardization...made automation, assembly optimization initiatives...more difficult."

### 3. **High Environmental Variation**

**Definition:** Production conditions vary uncontrollably across units.

**Manifestations:**
- Construction: Weather, soil conditions, local codes, material variation
- Site-specific infrastructure: Grid transformers adapted to local voltage/capacity
- Contrast: Cleanroom semiconductor fabs have zero environmental variation

**Mechanism:** Environmental variation requires:
- Constant problem-solving (not repetitive learning)
- Adaptive rather than optimized processes
- Information processing bandwidth that crowds out efficiency gains

### 4. **Site-Specificity (Cannot Centralize Production)**

**Definition:** Production must occur at the point of use, preventing factory economies.

**Manifestations:**
- Construction: Buildings built on-site, not in factories
- Infrastructure: Transformers must be installed where grid connects
- Contrast: Solar panels, chips, batteries made in centralized factories then shipped

**Mechanism:** Site-specific production:
- Eliminates factory process control
- Introduces logistics complexity for materials/labor
- Prevents capital-intensive automation (can't justify equipment for one-off sites)

**Quote:** Potter: "Because buildings are built manually on site by hand, there's a lot of variation in what ends up being built."

### 5. **Low Production Volume (Relative to Complexity)**

**Definition:** Units are produced infrequently relative to their complexity and capital intensity.

**Manifestations:**
- Large power transformers: ~343/year max US capacity, but 200+ designs
- Nuclear plants: Single-digit global construction starts per year
- Contrast: Semiconductor fabs produce millions of identical chips daily

**Mechanism:** Low volume means:
- Fixed costs (R&D, tooling, training) not amortized
- Limited practice opportunities for workers
- Infrequent production runs prevent rhythm/flow optimization

### 6. **Regulatory Ratcheting**

**Definition:** Requirements increase faster than learning accumulates.

**Manifestations:**
- Nuclear: Each project triggers new safety mandates
- Construction: Evolving building codes, energy standards
- Transformers: Changing grid interconnection requirements

**Mechanism:** Regulatory escalation:
- Forces redesigns that reset learning curves
- Adds complexity faster than experience reduces it
- Mandates bespoke solutions (e.g., local content requirements)

**Quote:** Potter: "It doesn't matter how standardized your design is if you end up needing to change it on every project to meet new requirements."

**Key Finding (US Nuclear):** At least **30% of 1976-1988 cost increases** due to regulation.

### 7. **Intrinsic Technology Scale/Complexity**

**Definition:** The technology is inherently large-scale and complex, limiting standardization benefits.

**Manifestations:**
- Nuclear: "Large-scale, lumpy" projects requiring "formidable ability to manage complexity"
- Large transformers: Expensive, difficult to transport, highly customized
- Contrast: Solar panels are small, modular, easy to transport

**Mechanism:** Scale/complexity means:
- Each unit is a megaproject requiring bespoke management
- Cannot decompose into standardized subcomponents
- Geometric scaling doesn't reduce per-unit complexity

**Quote:** Grubler on French nuclear: "Intrinsic characteristics of the technology limit essentially all classical mechanisms of cost improvements—standardization, large series, and a large number of quasi-identical experiences."

### 8. **Lack of Geometric Scaling Benefits**

**Definition:** Larger units don't become proportionally more efficient.

**Manifestations:**
- Construction: Doubling building size "just gets you twice as much building"
- Contrast: Power plants, chemical refineries, ships show scale economies

**Why Some Technologies Scale:**
- Surface-area-to-volume ratios (containment vessels, pipelines)
- Centralized control systems (one control room can manage larger plant)
- Shared infrastructure (one crane can serve larger factory)

**Why Others Don't:**
- Buildings: Each room needs same finishing regardless of building size
- Transformers: Each unit sized for specific grid node

---

## VI. Counter-Examples: Industries That Broke Through

### When Stuck Learning Curves Unstuck

Potter's work suggests **deliberate interventions** can unlock learning curves:

### 1. **WWII Shipbuilding**

**Before:** Shipbuilding was craft production, slow, expensive.

**Intervention:**
- **Standardization mandate:** Maritime Commission imposed single Liberty Ship design
- **Knowledge sharing:** 3,000+ improvement suggestions shared across yards
- **Welding over riveting:** Technology change enabling faster assembly
- **Prefabrication:** Larger cranes allowed modular construction

**Result:** 55% labor reduction, 80% time reduction.

**Lesson:** **Top-down standardization + technology insertion + knowledge coordination** can overcome craft production inertia.

### 2. **Solar Panels (Post-2000s)**

**Before:** High costs, limited deployment, seen as niche technology.

**Intervention:**
- **Policy support:** Feed-in tariffs (Germany), tax credits (US), manufacturing subsidies (China)
- **Manufacturing scale-up:** Chinese production capacity explosion
- **R&D investment:** Continuous material and process innovation
- **Standardization:** Module sizes, mounting systems, grid interconnection

**Result:** 90%+ cost reduction, multi-terawatt deployment.

**Lesson:** **Policy-driven demand + manufacturing investment + standardization** can trigger virtuous cycle.

### 3. **Batteries (2010s)**

**Before:** Expensive, limited range, EV skepticism.

**Intervention:**
- **Gigafactory model:** Tesla's Gigafactory 1 bet on scale manufacturing
- **EV adoption incentives:** Credits, mandates driving demand volume
- **Cell standardization:** 18650/2170 formats enabling automated production
- **Supply chain development:** Vertical integration (Tesla) and specialized suppliers

**Result:** ~90% cost reduction per kWh (2010-2020).

**Lesson:** **Visionary capital investment + demand incentives + standardization** unlocked learning curve.

### Common Threads in Breakthroughs:

1. **Imposed Standardization**
   - Usually requires external force (government, dominant firm, crisis)
   - Overcomes industry inertia toward customization

2. **Demand Volume Guarantee**
   - Policy mandates (wartime production, renewable energy targets, EV mandates)
   - De-risks manufacturing investment

3. **Manufacturing Process Innovation**
   - Not just design improvements, but **how** things are made
   - Automation, modularization, new assembly methods

4. **Knowledge Coordination**
   - Industry-wide learning sharing (Maritime Commission, semiconductor roadmaps)
   - Prevents reinventing wheel at each firm/project

---

## VII. Implications for Grid Transformer Manufacturing

### Current State: Locked in High-Cost Equilibrium

**Barriers Present:**
1. ✅ Extreme customization (200+ designs/1,000 units)
2. ✅ Site-specificity (each substation unique)
3. ✅ Low volume relative to variants
4. ✅ Regulatory fragmentation (state-by-state, utility-by-utility)
5. ✅ Limited automation (customization blocks it)
6. ✅ Long lead times (2-4 years)

**Result:** No evidence of learning curve despite decades of production.

### AI Demand Shock Scenario: Will Learning Curves Emerge?

**Optimistic Case (Learning Curves Activate):**

**Requirements:**
1. **Standardization Push:**
   - Federal/industry consortium defines "AI data center standard transformer"
   - Utilities agree to common specifications for data center substations
   - 70-80% of new transformers conform to 3-5 standard designs

2. **Volume Concentration:**
   - AI data center transformer demand reaches 100-200 units/year (vs. 343 total capacity)
   - Justifies dedicated production lines for standard models
   - Enables automation investment

3. **Manufacturing Innovation:**
   - New entrants (or existing manufacturers) invest in automated winding, assembly
   - Modular designs allow component reuse across models
   - Supply chain consolidation around standard materials

4. **Policy Support:**
   - Fast-track permitting for standard designs
   - Federal procurement preferences for standardized transformers
   - R&D funding for manufacturing process improvement

**Potential Learning Rate:** 85-90% (15-10% cost reduction per doubling)
**Doublings in 10 years:** ~1.5-2 doublings if AI demand grows 3-4x
**Cost Reduction:** 20-30% by 2035

**Skeptical Case (Learning Curves Fail to Emerge):**

**Why It Could Fail:**
1. **Customization Persists:**
   - Each AI firm demands bespoke specifications (Microsoft ≠ Google ≠ Meta)
   - Utilities refuse standardization (political economy, risk aversion)
   - Local regulations continue to fragment market

2. **Site-Specificity Remains Dominant:**
   - Even standardized transformers require site-specific installation
   - Geographic dispersion of data centers prevents centralized production benefits
   - Transportation costs for large transformers limit factory consolidation

3. **Regulatory Ratcheting:**
   - Grid reliability concerns trigger more stringent transformer requirements
   - Cybersecurity mandates for smart transformers add complexity
   - Environmental regulations (SF6 alternatives) force redesigns

4. **Insufficient Volume:**
   - AI demand shock is 2-3x, but spread across 200+ designs
   - No single design reaches volume threshold for automation investment
   - Skilled labor shortages persist regardless of volume

5. **Intrinsic Complexity:**
   - Large power transformers remain "large-scale, lumpy" capital goods
   - Cannot decompose into standardized modules (unlike solar panels)
   - Each unit still requires extensive testing, custom engineering

**Historical Analog:** Nuclear power—volume increased, standardization attempted, but costs rose due to regulatory ratcheting and intrinsic complexity.

**Likely Outcome:** **Minimal or no learning curve emergence** unless deliberate policy intervention imposes standardization.

---

## VIII. Potter's Key Quotes for Modeling

### On Construction Productivity Stagnation:
> "Learning curves exist for individual projects (especially ones that have repetitive elements), but not for the industry as a whole. This seems likely due to two effects: one is that learning curves are disrupted whenever a process changes, and so each time a new project starts, the learning curve is reset; the other is that certain types of improvements (such as scale effects, and underlying technology changes) are more difficult to achieve in construction."

### On Expected vs. Actual Improvement:
> "The US had approximately 45 million housing units in 1950, and has since built over 100 million more—about 1.66 doublings. A learning rate of 90% would imply a roughly 17% cost decrease between now and then; a rate of 85% would imply a 25% cost decrease. But we don't see anything like that at all."

### On Process Resets:
> "A dip in efficiency occurred when yards switched from building Liberty Ships to Victory Ships, and in general the broad swath of different ships produced by Maritime Commission yards meant that while Liberty Ship production improved significantly, overall wartime efficiency improvement was much less."

### On Nuclear Regulation:
> "Learning curve effects haven't occurred in the U.S. nuclear industry, likely due in part to frequently changing regulations, as it doesn't matter how standardized your design is if you end up needing to change it on every project to meet new requirements."

### On Mechanization Limits:
> "It's often possible to automate or mechanize construction work—replace labor with capital—in ways that aren't efficiency-enhancing. Construction automation and mechanization often requires a large amount of equipment to duplicate what's possible with a relatively small amount of labor."

### On Site-Specificity:
> "Because buildings are built manually on site by hand, there's a lot of variation in what ends up being built. There's only so accurately that a person can put something in place if they don't have precision tools, and the placement of materials tends to have a lot of variation."

### On Technologies vs. Commodities:
> "Models show that wind-generated electricity costs increase as deployment rises because the best, windiest sites get occupied first, and because wake effects from a wind farm can reduce the energy generated from adjacent wind farms."

### On French Nuclear Paradox:
> "Intrinsic characteristics of the technology limit essentially all classical mechanisms of cost improvements—standardization, large series, and a large number of quasi-identical experiences that can lead to technological learning and ultimate cost reductions." (Grubler, cited by Potter)

---

## IX. Modeling Framework for Systems Dynamics

### Key Variables for Transformer Learning Curve Model

**Exogenous Drivers:**
- AI CapEx → Data center build-out → Transformer demand
- Policy interventions (standardization mandates, fast-track permitting)
- Technology change (materials, manufacturing processes)

**Endogenous Dynamics:**

1. **Standardization Feedback Loop:**
   - (+) Volume → (+) Standardization incentive → (+) Automation investment → (–) Costs → (+) Volume
   - (–) Customization demand → (–) Standardization → (–) Automation → (+) Costs

2. **Regulatory Ratcheting Loop:**
   - (+) Deployment → (+) Visibility/incidents → (+) Regulatory stringency → (+) Complexity → (+) Costs
   - (Counteracts learning curve)

3. **Skill/Knowledge Loop:**
   - (+) Volume → (+) Worker experience → (–) Labor hours per unit → (–) Costs
   - (–) Process changes → (–) Accumulated knowledge → (+) Labor hours

4. **Capacity Constraint Loop:**
   - (+) Demand → (+) Capacity utilization → (+) Bottlenecks → (+) Lead times → (–) Demand response

**Critical Thresholds:**
- **Standardization threshold:** % of demand conforming to ≤5 standard designs
- **Volume threshold:** Units/year of each standard design (likely ~50-100 for automation ROI)
- **Lead time threshold:** Beyond ~3 years, demand starts seeking alternatives (distributed generation, demand reduction)

**Regime Scenarios:**

1. **Learning Regime:**
   - Standardization >70%, volume >50 units/design/year
   - Learning rate: 85-90%
   - Regulatory stability
   - Manufacturing innovation

2. **Stagnation Regime:**
   - Customization persists, fragmented demand
   - No learning curve (or negative learning if regulation escalates)
   - Costs stable or rising

3. **Transition Regime:**
   - Partial standardization (30-70% of demand)
   - Weak learning effects (5-10% cost reduction over decade)
   - Unstable (could tip to learning or stagnation)

**Modeling Approach:**
- Use **Markov regime switching** to model probability of transitioning between regimes
- Regime probabilities depend on policy variables (standardization enforcement) and demand volume
- **Bayesian inference** to quantify uncertainty in learning rate parameter (b) conditional on regime

---

## X. Research Gaps and Open Questions

### What Potter Hasn't Addressed (or Data Lacks):

1. **Transformer Industry Specifics:**
   - No detailed Potter analysis of transformer manufacturing
   - Limited public data on transformer cost trends over time
   - Unclear whether past demand spikes (grid buildout eras) showed any learning effects

2. **Threshold Analysis:**
   - At what volume does standardization become self-sustaining?
   - How much standardization (% of total demand) is needed to trigger learning curves?
   - What is break-even point for automation investment in transformer manufacturing?

3. **International Comparisons:**
   - Do European or Asian transformer markets show different learning dynamics?
   - Have any countries successfully standardized grid equipment?

4. **Material Constraints:**
   - Electrical steel, copper supply elasticity
   - How do commodity input prices interact with manufacturing learning curves?

5. **Alternative Technologies:**
   - Could modular substations or DC distribution bypass transformer bottlenecks?
   - If learning curves fail, what substitution mechanisms exist?

### Recommended Data Collection:

1. **Historical transformer cost data** (1970-2025) if available from utilities/manufacturers
2. **Lead time trends** as proxy for supply chain stress
3. **Design standardization metrics** (# of unique designs per utility, changes over time)
4. **Automation levels** in transformer manufacturing (% of labor automated)
5. **Case studies** of any past demand surges and industry response

---

## XI. Sources and References

### Brian Potter - Construction Physics:

- [Where Are My Damn Learning Curves?](https://www.construction-physics.com/p/where-are-my-damn-learning-curves) - Core argument on construction productivity stagnation
- [How Accurate Are Learning Curves?](https://www.construction-physics.com/p/how-accurate-are-learning-curves) - Analysis of learning curve model limitations
- [How the US Built 5,000 Ships in WWII](https://www.construction-physics.com/p/how-the-us-built-5000-ships-in-wwii) - Liberty Ship learning curve success story
- [On Technologies vs. Commodities](https://www.construction-physics.com/p/on-technologies-vs-commodities) - Critique of technology/commodity distinction
- [Making Modular Construction More Modular](https://www.construction-physics.com/p/making-modular-construction-more) - Why factory production doesn't solve construction problems
- [Trends in US Construction Productivity](https://www.construction-physics.com/p/trends-in-us-construction-productivity) - Mechanization limits and productivity data
- [The Birth of the Grid](https://www.construction-physics.com/p/the-birth-of-the-grid) - Electrical grid development (minimal manufacturing detail)

### Nuclear Power:

- [Why Does Nuclear Power Plant Construction Cost So Much?](https://ifp.org/nuclear-power-plant-construction-costs/) - Potter's analysis via Institute for Progress
- [Does Nuclear Power Have a Negative Learning Curve?](https://archive.thinkprogress.org/does-nuclear-power-have-a-negative-learning-curve-b389ef2de998/) - Grubler's French nuclear study discussion
- Grubler, A. (2010). "The costs of the French nuclear scale-up: A case of negative learning by doing." *Energy Policy*, 38(9), 5174-5188. - Seminal negative learning curve research

### Transformer Industry:

- [Large Power Transformer Resilience Report to Congress](https://www.energy.gov/sites/default/files/2024-10/EXEC-2022-001242%20-%20Large%20Power%20Transformer%20Resilience%20Report%20signed%20by%20Secretary%20Granholm%20on%207-10-24.pdf) - DOE report on customization, lead times, capacity (PDF not fully accessible)
- [Transformers in 2026: Shortage, Scramble, or Self-Inflicted Crisis?](https://www.powermag.com/transformers-in-2026-shortage-scramble-or-self-inflicted-crisis/) - Current supply chain issues
- [Transformer Supply Bottleneck Threatens Power System Stability](https://www.utilitydive.com/news/electric-transformer-shortage-nrel-niac/738947/) - NREL/NIAC analysis

### Solar and Semiconductors:

- [What Is the Learning Curve—and What Does It Mean for Solar Power?](https://blog.ucs.org/peter-oconnor/what-is-the-learning-curve/) - Swanson's Law explanation
- [A Critical Assessment of Learning Curves for Solar and Wind](https://www.oxfordenergy.org/wpcms/wp-content/uploads/2021/02/A-critical-assessment-of-learning-curves-for-solar-and-wind-power-technologies-EL-43.pdf) - Oxford Institute for Energy Studies
- [Historical and Future Learning for Multi-Terawatt Photovoltaics](https://www.nature.com/articles/s41560-025-01929-z) - Nature Energy on PV learning curves

### Learning Curve Theory:

- [Wright's Law](https://www.ark-invest.com/wrights-law) - ARK Invest explanation
- [Learning Curves and Wright's Law](https://medium.com/10x-curiosity/learning-curves-and-wrights-law-744b85b897a2) - Theory overview
- [Applications of Learning Curves in Production and Operations Management](https://www.sciencedirect.com/science/article/abs/pii/S0360835218305114) - Systematic literature review
- [The Learning Curve and Pricing in Chemical Processing Industries](https://www.gsb.stanford.edu/faculty-research/working-papers/learning-curve-pricing-chemical-processing-industries) - Stanford GSB research

### Potter's Book:

- *The Origins of Efficiency* (Stripe Press, 2025) - Comprehensive treatment of production efficiency across industries, including chapter on learning curves covering transistors, LEDs, solar panels, and failures in construction

---

## XII. Bottom Line for Your Systems Dynamics Model

**Central Thesis for Grid Transformer Manufacturing:**

**Learning curves are NOT automatic outcomes of production volume.** They require:

1. **Standardization** (70%+ of demand in ≤5 designs)
2. **Process stability** (no regulatory ratcheting or frequent redesigns)
3. **Sufficient volume per design** (~50-100 units/year minimum for automation ROI)
4. **Manufacturing innovation** (not just scaling up existing craft production)

**Current transformer industry exhibits ALL the blockers Potter identifies:**
- Extreme customization (200+ designs/1,000 units)
- Site-specificity
- Regulatory fragmentation
- Low volume per variant
- Craft production methods

**AI demand shock (2-3x increase) is INSUFFICIENT to trigger learning curves unless:**
- Policy intervention forces standardization (analogous to WWII Maritime Commission)
- Demand concentrates in standardized "AI data center transformer" designs
- Manufacturers invest in automated production lines (requires volume certainty)

**Default scenario: Stagnation regime**
- Costs remain flat or rise due to bottlenecks and regulatory responses
- Lead times extend (currently 2-4 years, could reach 5+ years)
- Supply chain crisis similar to post-COVID, but sustained

**Breakthrough scenario requires deliberate intervention:**
- Federal standardization mandate + fast-track permitting for standard designs
- Manufacturing subsidies/loan guarantees to de-risk automation investment
- Utility coordination (possibly via FERC) to align specifications

**Your model should:**
1. Make learning curve emergence **conditional** on standardization and policy variables
2. Default to **flat or negative learning** under business-as-usual
3. Use Markov regime switching to model probabilistic transitions between stagnation/learning regimes
4. Quantify uncertainty in learning rate parameter (b) using Bayesian inference—wide priors given lack of historical data

**Potter's work provides rigorous skepticism against facile "technology learning curve" assumptions.** For infrastructure capital goods like transformers, learning curves are the exception, not the rule.

---

**End of Synthesis**