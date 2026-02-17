# DD-001 Open Questions: Research Findings

**Date:** 2026-02-13
**Researcher:** Claude (for Thandolwethu Zwelakhe Dlamini)
**Context:** Filling knowledge gaps identified in DD-001 (The Hidden Descent: Investigating Learning Curves in Power Infrastructure)

---

## Question 1: Segment-Level Data

**Can we isolate distribution transformer pricing from LPTs?**

### Key Findings

**NREL Reports (2024-2025):**
NREL has published two critical reports that partially address this gap:

1. **"Major Drivers of Long-Term Distribution Transformer Demand"** (NREL/TP-6A40-87653, FY24) -- Identifies demand drivers by transformer segment.
2. **"Distribution Transformer Demand: Understanding Demand Segmentation, Drivers, and Management Through 2050"** (NREL/FS-6A40-92076, FY25) -- The most granular public segmentation available.

Key data points from these reports:
- **60-80 million** distribution transformers currently installed in the U.S., with 2.5-3.5 TVA of capacity.
- **Single-phase pole-mounted:** ~73% of installed units, ~30% of capacity (residential/commercial service transformers).
- **Single-phase pad-mounted:** ~20% of installed units, ~15% of capacity.
- **Three-phase pad-mounted step-up:** Could see close to 2 TW of additional demand by 2050 (solar, wind, battery arrays).
- Distribution transformer capacity may need to increase **160%-260% by 2050** compared to 2021 levels.

**Census Bureau (NAICS 335311):**
The Census Bureau classifies all transformer manufacturing under NAICS 335311 ("Power, Distribution, and Specialty Transformer Manufacturing"). The Economic Census includes product-level shipment data, but does *not* publicly break out distribution vs. power transformer pricing in a way useful for Wright's Law analysis. The data exists in the Census Industry Statistics Portal (data.census.gov) but requires direct access to product-class detail.

**Newton-Evans Research Company:**
Published a "Mid-2024 Assessment of the U.S. Distribution Transformer Industry" -- this is a proprietary report but may contain the segment-level pricing data needed.

**Pricing indicators found:**
- Pad-mounted distribution transformers: $4,000-$40,000 depending on kVA rating and quantity.
- Prices rose 5-6x in the past 2 years with lead times stretching to 2 years.

### Relevant Data Sources
- [NREL FY25 Demand Segmentation Report (PDF)](https://docs.nrel.gov/docs/fy25osti/92076.pdf)
- [NREL FY24 Demand Drivers Report (PDF)](https://docs.nrel.gov/docs/fy24osti/87653.pdf)
- [Census Bureau NAICS 335311 Portal](https://data.census.gov/profile/335311_-_Power,_distribution,_and_specialty_transformer_manufacturing?n=335311)
- [Newton-Evans Mid-2024 Assessment](https://www.newton-evans.com/a-mid-2024-assessment-of-the-u-s-distribution-transformer-industry/)
- [DOE Office of Electricity - Distribution Transformers](https://www.energy.gov/oe/articles/energy-department-researches-distribution-transformer-types-and-demand-drivers)

### Effect on Learning Curve Hypothesis
The NREL segmentation confirms that three-phase pad-mounted transformers (the segment most relevant to data centers) are a distinct and trackable category. The 160-260% capacity growth projection through 2050 provides the volume trajectory needed for Wright's Law analysis. However, public pricing data remains aggregated. The FRED PPI (PCU335311335311) bundles all transformer types, which means the ~12% learning rate estimated in DD-001 is a blended signal. The true learning rate for the standardizable distribution segment could be higher (if distribution is driving the efficiency gains) or lower (if it's being masked by LPT pricing noise).

### Suggested Next Steps
1. Download and analyze the full NREL FY25 report (92076) for detailed segmentation tables.
2. Access Census Bureau product-class detail for NAICS 335311 to attempt a distribution/LPT price split.
3. Evaluate whether the Newton-Evans proprietary report is worth the cost for segment-level pricing.
4. Check if DOE's Electric Grid Supply Chain Review (2022) has product-level cost breakdowns.
5. Contact NREL authors directly -- the reports invite stakeholder engagement.

---

## Question 2: DOE Regulatory Ratchet

**Are the 2023 DOE efficiency standards a one-time step-change or ongoing escalation?**

### Key Findings

**The Regulatory Timeline:**
1. **January 2023:** DOE proposed aggressive new efficiency standards for distribution transformers. The initial proposal would have required ~95% of the market to shift to amorphous steel cores, effectively mandating a near-complete replacement of Grain-Oriented Electrical Steel (GOES).
2. **April 4, 2024:** DOE finalized significantly revised standards after massive industry pushback. Key changes:
   - **75% of the market can comply using GOES** (vs. ~5% under the original proposal).
   - Only ~25% of the market needs to shift to amorphous alloy (vs. ~95% originally).
   - Compliance timeline extended from **3 years to 5 years** (deadline: April 23, 2029).
3. **Projected benefits:** $14 billion in energy savings and 85 million metric tons of CO2 reduction over 30 years.

**Critical Finding -- This is NOT Like France's Nuclear Ratchet:**

The French nuclear comparison from Grubler's 2010 study involved *continuous regulatory escalation* -- each reactor generation triggered new safety requirements that reset the learning curve. The DOE transformer rule is structurally different:

- **One-time step-change, not continuous escalation.** The rule sets a fixed efficiency floor effective 2029. There is no built-in mechanism for automatic escalation.
- **Industry pushback worked.** The final rule was dramatically weakened from the proposal, suggesting the regulatory process is responsive to supply chain constraints rather than ratcheting unilaterally.
- **GOES survives.** The dominant core material (GOES) remains viable for 75% of the market. This preserves existing manufacturing processes and supply chains, particularly Cleveland-Cliffs' domestic GOES production.
- **Amorphous steel is a known technology.** Unlike nuclear safety systems that added novel complexity, amorphous steel cores are a well-understood manufacturing process. The cost premium is material-driven, not complexity-driven.

**However, there are ratchet risks to monitor:**
- DOE conducts periodic reviews of efficiency standards. A future administration could propose tighter standards.
- State-level efficiency mandates (e.g., California) could create a patchwork of requirements.
- The 2029 compliance deadline creates a near-term cost step-change that could temporarily mask underlying learning curves.

### Relevant Data Sources
- [DOE Final Rule Announcement](https://www.energy.gov/articles/doe-finalizes-energy-efficiency-standards-distribution-transformers-protect-domestic)
- [DOE Final Rule - Federal Register](https://www.federalregister.gov/documents/2024/04/22/2024-07480/energy-conservation-program-energy-conservation-standards-for-distribution-transformers)
- [POWER Magazine Analysis of Eased Requirements](https://www.powermag.com/doe-eases-requirements-in-final-transformer-efficiency-standards-amid-supply-chain-strain/)
- [Utility Dive - Final Rule Analysis](https://www.utilitydive.com/news/doe-finalizes-distribution-transformer-rule/712229/)
- [American Electric Cooperatives - "Much Improved" Standard](https://www.electric.coop/doe-finalizes-much-improved-standard-for-distribution-transformers)
- [Grubler (2010) - French Nuclear Negative Learning](https://www.sciencedirect.com/science/article/abs/pii/S0301421510003526)

### Effect on Learning Curve Hypothesis
**Net positive for the hypothesis.** The DOE rule is a one-time step-change, not a ratchet. The final rule's GOES accommodation means the dominant manufacturing process is preserved. The 2029 compliance deadline will create a visible cost bump in 2028-2029 as manufacturers retool, but this is a discrete event that can be controlled for in the Wright's Law analysis (similar to how you'd control for a commodity price shock). The risk of continuous regulatory escalation -- the mechanism that destroyed French nuclear learning curves -- appears low in the current political environment.

### Suggested Next Steps
1. Model the 2029 efficiency step-change as a discrete cost shock in the systems dynamics model.
2. Track whether amorphous steel manufacturers (e.g., Metglas/Hitachi) are scaling capacity -- this determines whether the 25% amorphous requirement creates a supply bottleneck.
3. Monitor DOE's next scheduled review of transformer efficiency standards for signs of further tightening.
4. Compare the DOE rule's cost impact to the Grubler framework quantitatively -- is the magnitude of the step-change comparable to a single nuclear regulatory cycle?

---

## Question 3: Hyperscaler Spec Convergence

**Are hyperscalers ordering standardized transformer designs?**

### Key Findings

**Strong evidence of convergence, driven by three major partnerships:**

1. **Compass Datacenters + Siemens (2025):**
   - Multi-year capacity agreement for **1,500 modular medium-voltage skid units** over five years.
   - Each unit consolidates medium-voltage switchgear and transformers into a single integrated, prefabricated unit.
   - Uses standardized Siemens 8DJH 36 gas-insulated arc-resistant medium-voltage switchgear.
   - First installation: former Sears HQ site in Chicago, breaking ground H2 2025.

2. **Compass Datacenters + Schneider Electric ($3B, 2023-2028):**
   - 5-year, $3 billion vendor-supplier agreement for modular data center solutions.
   - Manufacturing facility in West Chester, OH producing **240 power centers in 2025**, with capacity for **400+ per year**.
   - ~150 modular solutions already delivered since partnership inception.
   - Explicitly designed for "standardized design, efficient manufacturing, and rapid deployment."
   - September 2025: Launched EcoStruxure Pod -- prefabricated modular white space solution.

3. **Eaton + Siemens Energy (2025):**
   - Joint forces to accelerate delivery of new data center capacity.
   - Combined power and technology platform for standardized deployment.

**NEMA Standardization (2023):**
NEMA published **US 80017-2023: "Design Considerations for Transformers in Data Center Applications"** -- a formal industry standard providing guidance on transformer specifications for data centers. This covers in-rush current handling, harmonic design (K4/K9/K13 ratings), and transient voltage protection. The existence of a NEMA standard is itself evidence of spec convergence -- it creates a common language for procurement.

**McKinsey Analysis (2025-2026):**
Industry experts recommend data center designs be **60-80% standardized and 20-40% customized** for site-specific elements. Every major hyperscaler now embraces modularity. Hyperscalers are "treating data center construction like a factory line, standardizing designs into repeatable, plug-and-play units."

**ON.energy (2025):**
Signed the "largest dedicated transformer deal in the U.S." -- a **5 GW transformer supply agreement** for data center and renewable infrastructure, supporting deployment starting 2026.

**The Fragmentation Problem Persists but is Shrinking:**
The Uptime Institute reports 80,000+ unique transformer configurations globally. However, the hyperscaler procurement model is actively compressing this variation. The shift is from "each utility orders custom specs" to "Compass orders 1,500 identical units from Siemens."

### Relevant Data Sources
- [Siemens/Compass Multi-Year Agreement](https://press.siemens.com/global/en/pressrelease/siemens-and-compass-datacenters-sign-multi-year-custom-electrical-solution-agreement)
- [Schneider Electric/Compass $3B Agreement](https://www.se.com/us/en/about-us/newsroom/news/press-releases/schneider-electric-and-compass-datacenters-expand-partnership-with-3-billion-multi-year-data-center-technology-agreement-654c72aea7ee7277290da24e)
- [Eaton/Siemens Energy Joint Platform](https://www.eaton.com/us/en-us/company/news-insights/news-releases/2025/eaton-and-siemens-energy-join-forces-to-provide-power-and-technology.html)
- [NEMA US 80017-2023 (PDF)](https://www.nema.org/docs/default-source/nema-documents-libraries/nema-us-80017-2023-design-considerations-for-transformers-in-data-center-applications.pdf)
- [McKinsey - Scaling Data Centers with Smarter Designs](https://www.mckinsey.com/industries/private-capital/our-insights/scaling-bigger-faster-cheaper-data-centers-with-smarter-designs)
- [ON.energy 5GW Transformer Deal](https://www.morningstar.com/news/business-wire/20251211998584/onenergy-signs-largest-dedicated-transformer-deal-in-the-us-for-data-center-and-renewable-applications)

### Effect on Learning Curve Hypothesis
**Strongly supports the hypothesis.** This is the single most important finding across all six questions. The multi-year, multi-billion-dollar procurement agreements with standardized modular designs directly satisfy two of Potter's five conditions for learning curves:
- **Identical units** -- 1,500 identical Siemens skids, 400+/year Schneider power centers.
- **Continuous production** -- 5-year guaranteed contracts eliminate stop-start ordering.

The scale is unprecedented for grid hardware. Compass alone is deploying standardized power blocks across multiple campuses. This is the Model 3/Y moment for transformers -- the volume that justifies manufacturing innovation.

### Suggested Next Steps
1. Obtain the NEMA US 80017-2023 standard to understand the specific electrical parameters being standardized.
2. Track how many unique transformer configurations Compass, Microsoft, Google, and Amazon are actually ordering -- the 80,000 global figure is historical; the relevant number is configurations ordered by hyperscalers in 2024-2026.
3. Map the Schneider Electric West Chester, OH facility's production ramp as a real-time learning curve data source.
4. Investigate whether the standardized designs use GOES or amorphous cores -- this intersects with Question 2.

---

## Question 4: Cleveland-Cliffs as Leading Indicator

**What does the Weirton plant tell us about who believes in standardized volume?**

### Key Findings

**Project Details:**
- **Investment:** $150 million total ($50M forgivable loan from West Virginia, $100M from Cleveland-Cliffs).
- **Location:** Former Half Moon Warehouse at the idled Weirton tinplate mill, Weirton, WV.
- **Product:** Three-phase distribution transformers for electric power distribution systems.
- **Timeline:** Expected online H1 2026. As of March 2025, "plans remain in place" despite "a few hurdles."
- **Employment:** 600 USW-represented workers (reemployed from the idled tinplate mill).

**Vertical Integration Strategy:**
This is the critical detail. Cleveland-Cliffs is the **sole U.S. producer of Grain-Oriented Electrical Steel (GOES)**, manufactured at Butler Works in Butler, PA. The Weirton transformer plant creates a vertically integrated supply chain:
- **GOES** from Butler Works, PA
- **Stainless and carbon steel** from Cliffs plants in Ohio, Michigan, and Indiana
- **Transformer assembly** at Weirton, WV

This means Cleveland-Cliffs controls the entire value chain from raw steel to finished transformer. This vertical integration eliminates the GOES supply chain bottleneck that has been a primary constraint on U.S. transformer manufacturing.

**Target Market -- Broader Than Data Centers:**
CEO Lourenco Goncalves framed the investment around the "critical shortage of distribution transformers that is stifling economic growth across the United States." The rationale is grid modernization broadly -- not AI/data center demand specifically. However, the three-phase distribution transformer product category is exactly the segment that overlaps with data center and renewable energy demand (three-phase pad-mounted units are what data centers and solar/wind installations need).

**Context -- NREL's demand projection** of 160-260% distribution transformer capacity growth by 2050 is the macro backdrop. Cleveland-Cliffs is betting on total addressable market growth, not just one demand driver.

### Relevant Data Sources
- [Cleveland-Cliffs Press Release](https://www.clevelandcliffs.com/news/news-releases/detail/644/cleveland-cliffs-announces-its-new-state-of-the-art)
- [Utility Dive - $150M Plant Analysis](https://www.utilitydive.com/news/cleveland-cliffs-confirms-150-million-electric-transformer-weirton-plant/723363/)
- [Renewable Energy World - Weirton Mill Reborn](https://www.renewableenergyworld.com/power-grid/idled-west-virginia-mill-gets-new-life-as-a-transformer-plant/)
- [Weirton Daily Times - 2026 Timeline Confirmation](https://www.weirtondailytimes.com/news/local-news/2025/03/weirton-transformer-facility-still-eyed-for-2026/)
- [Plant Services - Investment Details](https://www.plantservices.com/industry-news/news/55141006/cleveland-cliffs-invests-150-million-to-establish-electrical-distribution-transformer-manufacturing-plant-in-west-virginia)

### Effect on Learning Curve Hypothesis
**Strong supporting signal, with important nuance.** Cleveland-Cliffs' decision to vertically integrate from GOES production into transformer manufacturing is a powerful revealed-preference signal. A steel company does not invest $150M to enter a new product category unless it believes sustained, high-volume demand is coming. The vertical integration also eliminates one of the key cost components -- GOES sourcing friction -- that has historically kept transformer manufacturing fragmented.

The nuance: Goncalves is not betting on data center demand alone. He's betting on total grid modernization demand (IRA, EV charging, renewable interconnection, aging infrastructure replacement). This is actually *more* bullish for the learning curve hypothesis because it means the volume driver is diversified -- even if AI demand plateaus, the other demand sources persist.

The plant's focus on three-phase distribution transformers positions it directly in the standardizable segment identified in DD-001's scorecard.

### Suggested Next Steps
1. Track the Weirton plant's actual production start date and initial output volumes -- this becomes a real-time test of the learning curve hypothesis.
2. Research whether Cleveland-Cliffs is producing to standardized specs (NEMA 80017-2023) or custom utility specs -- this determines whether the plant enables or perpetuates fragmentation.
3. Monitor Cleveland-Cliffs' quarterly earnings calls for commentary on order book, customer mix, and production ramp.
4. Investigate whether other GOES-integrated transformer manufacturers exist globally -- is this vertical integration strategy replicable?

---

## Question 5: Solid-State Transformer Wildcard

**Could SSTs leapfrog the traditional manufacturing question?**

### Key Findings

**Current State of Technology:**

Multiple companies are approaching commercial deployment:

1. **Amperesand ($80M Series A, 2025):**
   - Piloted Generation I medium-voltage AC SSTs at 500 kW and 1.5 MW, 3-phase.
   - Plans to deliver **30 MW of commercial systems in 2026** to hyperscale AI data center customers.
   - First commercial units delivering early 2026 to Port of Singapore (PSA International pilot).
   - Claims **80%+ reduction in electrical equipment footprint** vs. traditional infrastructure.
   - Funded by Walden Catalyst and Temasek (oversubscribed Series A).

2. **Eaton / Resilient Power Systems (acquired August 2025):**
   - Eaton paid $55M upfront + up to $95M in earnouts for Resilient Power Systems.
   - Medium-voltage SST technology targeting data centers, energy storage, EV charging, and distribution.
   - Eaton -- already a major traditional transformer manufacturer -- is hedging both sides.

3. **WattEV (2026):**
   - Proprietary SST for heavy-duty electric truck charging.
   - Production-ready units expected 2026.

**Market Size:**
- SST market valued at $181M (2025), projected to reach $379M by 2031 (13% CAGR).
- For comparison, the traditional data center transformer market alone is $9.45B (2025).
- **SSTs are ~2% the size of the traditional market.** This is early-stage.

**Cost/Performance Tradeoffs:**
- **SSTs cost up to 10x more** than traditional transformers. A 50 kVA SST costs $60,000-$100,000 vs. $6,000-$10,000 for traditional.
- Traditional transformers: $7-$25 per kVA. SSTs: orders of magnitude higher.
- SSTs are ~20% more efficient than traditional transformers.
- SSTs offer dramatic footprint reduction (80%+), simplified installation (50% labor reduction), and 10x faster time-to-power.
- SSTs use silicon carbide (SiC) and gallium nitride (GaN) power semiconductors -- both on steep cost decline curves of their own.

**The Leapfrog Assessment:**

SSTs will NOT leapfrog traditional transformers in the near term (2025-2030) for the following reasons:
- **10x cost premium** is prohibitive for grid-scale deployment.
- **$181M market vs. $9.45B** -- two orders of magnitude smaller.
- **First commercial units** are just now shipping (2026). Grid-scale deployment is years away.

However, SSTs *could* leapfrog in the medium term (2030-2035) IF:
- SiC/GaN semiconductor costs continue declining (they follow Wright's Law themselves, ~20-30% learning rates).
- Hyperscalers value footprint reduction and deployment speed enough to pay the premium (data center land costs and time-to-revenue may justify 10x transformer cost).
- Eaton's dual strategy (traditional + SST) suggests the transition timeline is uncertain -- they're hedging.

**The more likely scenario:** SSTs create a premium parallel market (like Tesla's EV batteries initially) while traditional transformers serve the volume market. This is *complementary* to the learning curve hypothesis, not destructive to it.

### Relevant Data Sources
- [Amperesand $80M Series A](https://www.businesswire.com/news/home/20251118244299/en/Amperesand-Raises-$80M-Series-A-Co-led-by-Walden-Catalyst-Ventures-and-Temasek-to-Redefine-Power-Infrastructure-for-AI-Data-Centers)
- [Eaton Acquires Resilient Power Systems](https://www.eaton.com/us/en-us/company/news-insights/news-releases/2025/eaton-completes-acquisition-of-resilient-power-systems-inc---str.html)
- [Canary Media - SST Overview](https://www.canarymedia.com/articles/distributed-energy-resources/solid-state-transformers-dgmatrix-resilient-power)
- [Patsnap - SST vs Conventional Cost Analysis](https://eureka.patsnap.com/article/solid-state-transformer-vs-conventional-transformer-is-the-extra-cost-worth-it)
- [Navitas Semi - GaN and SiC for Data Centers (PDF)](https://navitassemi.com/wp-content/uploads/2025/10/Redefining-Data-Center-Power-GaN-and-SiC-Technologies-for-Next-Gen-800-VDC-Infrastructure.pdf)
- [NPC Electric - SSTs in Data Centers](https://www.npcelectric.com/news/the-future-of-data-center-power-solid-state-transformers-explained.html)

### Effect on Learning Curve Hypothesis
**Does not invalidate the hypothesis in the relevant timeframe.** SSTs are a 2030+ technology for grid-scale impact. The learning curve analysis in DD-001 covers the 2015-2030 period where traditional transformers dominate. SSTs should be modeled as a potential regime change in the Markov switching model (DD-004) -- a low-probability, high-impact scenario where the entire traditional manufacturing question becomes moot.

Interestingly, SSTs have their *own* learning curve story (SiC/GaN semiconductors follow Wright's Law aggressively). A future analysis could model the two competing learning curves and identify the crossover point where SST costs fall below traditional transformer costs.

### Suggested Next Steps
1. Track SiC and GaN power semiconductor pricing curves (CAGR data from Yole, SEMI) as a leading indicator for SST cost trajectory.
2. Monitor Amperesand's 2026 commercial deployments for real-world cost and performance data.
3. Model SSTs as a scenario in DD-004 (Markov regime switching) -- what probability should be assigned to an SST disruption scenario by 2030? By 2035?
4. Investigate Casey Handmer's "Direct Current Data Centers" thesis -- DC architecture could accelerate SST adoption by eliminating AC/DC conversion stages.

---

## Question 6: Who Captures the Benefit?

**Are hyperscalers capturing cost declines while socializing infrastructure costs?**

### Key Findings

**The Union of Concerned Scientists' Analysis:**

The UCS published a detailed analysis identifying a major cost allocation problem in the PJM Interconnection region (the largest U.S. grid operator, covering 13 states plus DC):

- **$4.3 billion in data center connection costs** were passed to general ratepayers in 2024 across seven PJM states (Illinois, Maryland, New Jersey, Ohio, Pennsylvania, Virginia, West Virginia).
- Between 2022 and 2024, utilities initiated **150+ local transmission projects** specifically to serve data center connections.
- Individual connection projects cost **$25M-$100M** each.
- **~95% of connection costs** were rolled into general transmission charges and recovered from all retail ratepayers. Only ~5% was directly allocated to the data centers requesting the connections.
- This is described as a "connection costs loophole" -- existing FERC rate formulas did not anticipate individual customers creating such concentrated, high-cost demand.

**The Mechanism:**
The cost socialization works through FERC formula rates. When a utility builds transmission infrastructure to connect a data center, the cost is classified as a general transmission upgrade and spread across all customers. State regulators receive utility rate filings that do *not* distinguish data center connection costs from other transmission costs. The result: residential and commercial ratepayers subsidize hyperscaler grid connections without knowing it.

**FERC's Response (2025-2026):**

FERC has begun addressing this:

1. **February 2025:** FERC initiated a show-cause proceeding into PJM's tariff provisions governing co-location of generation with large loads (including data centers).
2. **December 18, 2025:** FERC ordered PJM to develop new rules for co-locating data centers at power plants. Key provisions:
   - Created **three new transmission service options**.
   - Reformed behind-the-meter generation rules.
   - **Critical provision:** Generators cannot remove capacity from the grid to serve co-located loads until all transmission upgrades needed for reliability are in service, with **100% of upgrade costs allocated to the generator/large load customer** (not ratepayers).
   - Compliance deadlines starting January 2026.

**Broader Context:**
- Michigan analysis (January 2026): Data centers "poised to push up energy costs and challenge climate goals."
- Canada is proactively considering policies to "keep data centre costs off household power bills."
- The UCS September 2025 policy brief explicitly calls for closing the connection costs loophole.

### Relevant Data Sources
- [UCS Blog - Data Centers Increasing Your Energy Bills](https://blog.ucs.org/mike-jacobs/data-centers-are-already-increasing-your-energy-bills/)
- [UCS Policy Brief - Connection Costs Loophole (PDF)](https://www.ucs.org/sites/default/files/2025-09/PJM%20Data%20Center%20Issue%20Brief%20-%20Sep%202025.pdf)
- [UCS - Everyone Agrees Data Centers Should Cover Costs](https://blog.ucs.org/mike-jacobs/finally-something-everyone-agrees-on-data-centers-should-cover-their-own-costs/)
- [Utility Dive - $4.4B PJM Transmission Costs](https://www.utilitydive.com/news/pjm-data-center-transmission-costs-ratepayers/761579/)
- [Data Center Frontier - $4B Cost Shift Study](https://www.datacenterfrontier.com/energy/article/55321163/study-finds-4b-in-data-center-grid-costs-shifted-to-consumers-across-pjm-region)
- [FERC Fact Sheet - PJM Co-Location Rules](https://www.ferc.gov/news-events/news/fact-sheet-ferc-directs-nations-largest-grid-operator-create-new-rules-embrace)
- [FERC Co-Location Order](https://www.ferc.gov/news-events/news/ferc-directs-nations-largest-grid-operator-create-new-rules-embrace-innovation-and)
- [UCS Data Center Power Play Report (PDF)](https://www.ucs.org/sites/default/files/2026-01/Data-Center-Power-Play-report-final.pdf)

### Effect on Learning Curve Hypothesis
**Complicates the "AI modernizes the grid" narrative but does not invalidate the learning curve hypothesis itself.**

The learning curve hypothesis (DD-001) asks: "Is AI demand driving manufacturing efficiency improvements in transformer production?" The answer to that question is independent of who captures the resulting cost savings. However, the distributional question matters enormously for the *systems dynamics* implications:

- **If hyperscalers capture cost declines** through private procurement (standardized modular contracts with Schneider, Siemens, Eaton) while **ratepayers bear the grid connection costs** ($4.3B/year in PJM alone), then learning curve benefits flow to tech companies while infrastructure costs are socialized.
- **FERC's 2025-2026 reforms** are beginning to close this gap by requiring co-located loads to bear 100% of their grid upgrade costs.
- The policy environment is shifting. The question for the systems dynamics model is whether policy correction happens fast enough to change investment incentives.

This creates an important feedback loop for the DD-002 causal loop diagram: **cost socialization enables faster hyperscaler deployment** (because they don't bear the full cost), which **drives transformer volume** (supporting learning curves), but **generates political backlash** (ratepayer resistance), which **triggers regulatory correction** (FERC reforms), which **slows deployment or increases hyperscaler costs**.

### Suggested Next Steps
1. Build the cost socialization feedback loop explicitly into DD-002's causal loop diagram.
2. Quantify the $4.3B/year figure relative to total transformer procurement spending -- is the socialized grid cost larger or smaller than private transformer procurement?
3. Track FERC's compliance deadlines (January 2026 onwards) for evidence that cost allocation is actually shifting.
4. Monitor PJM interconnection queue data for changes in data center application rates post-FERC reform.
5. Download and analyze the UCS "Data Center Power Play" report (January 2026) for the most current data.

---

## Synthesis: Cross-Cutting Implications for DD-001 Hypothesis

### The Weight of Evidence

| Question | Finding | Net Effect on Hypothesis |
| :--- | :--- | :--- |
| 1. Segment data | NREL confirms distinct, trackable distribution segment; public pricing still aggregated | Neutral (data gap persists but path to resolution is clear) |
| 2. DOE regulatory ratchet | One-time step-change, NOT ongoing escalation; 75% GOES preserved | **Positive** (nuclear analogy does not apply) |
| 3. Hyperscaler spec convergence | $3B+ in standardized multi-year contracts; 1,500+ identical units ordered | **Strongly positive** (Potter conditions 1 and 3 satisfied) |
| 4. Cleveland-Cliffs | Vertically integrated GOES-to-transformer; betting on broad grid modernization | **Positive** (revealed-preference signal for sustained volume) |
| 5. Solid-state wildcard | 10x cost premium; 2% market share; 2030+ for grid-scale impact | **Neutral** (not a near-term threat to the hypothesis) |
| 6. Cost socialization | $4.3B/year socialized; FERC reforming; creates political feedback loop | **Complicating** (does not invalidate learning curves but affects who benefits) |

### Updated Assessment of Potter's Five Conditions (Distribution Transformers)

| Condition | DD-001 Assessment | Updated Assessment |
| :--- | :--- | :--- |
| Identical units | Partial pass | **Passing** -- Compass/Siemens (1,500 units), Compass/Schneider (400+/yr), NEMA standard |
| Stable environment | Pass | **Pass confirmed** -- factory-built modular units, prefab power blocks |
| Continuous production | Passing | **Strong pass** -- multi-year $3B+ contracts, guaranteed order books |
| No regulatory ratcheting | Risk | **Manageable risk** -- DOE final rule is step-change, not ratchet; 75% GOES preserved |
| Decreasing complexity | Uncertain | **Trending positive** -- standardization simplifies; NEMA 80017 formalizes specs |

### Priority for DD-002 (Causal Loop Diagram)

Based on this research, the causal loop diagram should include these feedback loops:

1. **Volume-Learning Loop** (reinforcing): AI demand -> standardized procurement -> continuous production -> manufacturing learning -> cost reduction -> more demand
2. **Regulatory Step-Change Loop** (balancing): DOE efficiency mandate -> material cost increase -> temporary price increase -> absorbed over time
3. **Cost Socialization Loop** (reinforcing then balancing): Hyperscaler demand -> grid connection costs -> socialized to ratepayers -> political backlash -> FERC reform -> cost allocation to hyperscalers -> slower deployment
4. **Vertical Integration Loop** (reinforcing): Demand signal -> supply chain investment (Cleveland-Cliffs) -> reduced GOES bottleneck -> faster production -> lower costs
5. **Technology Disruption Loop** (potential regime change): SST cost decline -> crossover with traditional costs -> market shift (2030+ scenario)
