# AI Valuations vs. Physical Infrastructure Reality

*Research compiled: 2026-02-16*
*For: DD-002 Grid Modernization analysis*

---

## Core Question

AI company valuations keep rising and hyperscaler capex commitments are accelerating.
But how much of the announced capital is actually converting to physical infrastructure?
What does the grid get from the portion that does?

---

## 1. Hyperscaler Capital Expenditure (2023-2025)

Source: SEC filings (10-K, 10-Q), earnings call transcripts via SEC EDGAR.

| Company | 2023 Capex | 2024 Capex | 2025 Guidance | YoY (24-25) |
|---------|-----------|-----------|---------------|-------------|
| Microsoft | ~$32B | ~$53-56B | ~$80B | +43-51% |
| Amazon | ~$48B | ~$78B | ~$100B+ | +28% |
| Alphabet/Google | ~$32B | ~$53B | ~$75B | +43% |
| Meta | ~$28B | ~$39B | ~$60-65B | +54-67% |
| Oracle | ~$7B | ~$7B | ~$16B+ | +129% |
| **Total Big 5** | **~$147B** | **~$230B** | **~$331-336B** | **~44%** |

Notes:
- These are total corporate capex figures, not AI-specific. Management commentary
  attributes the incremental increase primarily to AI/cloud infrastructure.
- Microsoft has stated "virtually all" new capex is AI-related. Others are less specific.
- Microsoft's approximate split: 50% buildings/infrastructure, 50% servers/GPUs.
- Apple is notably absent from AI infrastructure spending at this scale.

### Capex Decomposition (industry estimates)

Of the ~$300B+ annual hyperscaler capex:
- ~30-40% goes to physical construction (buildings, power infrastructure)
- ~50-60% goes to equipment (servers, GPUs, networking)
- ~10% to other costs (land, permits, professional services)

This decomposition matters: physical construction is durable (20-40 year assets),
while equipment depreciates in 3-6 years.

---

## 2. The Three-Layer Disconnect

### Layer 1: Valuations vs. Capex

| Company | Jan 2023 Mkt Cap | Jan 2025 Mkt Cap | Gain |
|---------|-----------------|-----------------|------|
| Nvidia | ~$360B | ~$3.4T | +$3.0T |
| Microsoft | ~$1.8T | ~$3.1T | +$1.3T |
| Alphabet | ~$1.1T | ~$2.4T | +$1.3T |
| Amazon | ~$860B | ~$2.3T | +$1.4T |
| Meta | ~$320B | ~$1.6T | +$1.3T |
| Apple | ~$2.1T | ~$3.4T | +$1.3T |
| **"Mag 7" Total** | **~$8.5T** | **~$18T** | **~$9.5T** |

The combined market cap growth of ~$10T dwarfs the ~$300B annual capex being deployed.
Markets are pricing AI returns at ~30x the infrastructure investment.

### Layer 2: Capex vs. Revenue (The "$600B Question")

- Sequoia Capital (David Cahn, September 2024): Estimated the AI industry needs
  ~$600B in annual revenue to justify the infrastructure buildout. Actual AI revenue
  (excluding Nvidia hardware sales) was ~$100B, creating a "$500B hole."
- Bernstein (Toni Sacconaghi): AI-related revenue was ~$20-30B in 2024 against
  $200B+ in AI-related capex. Capex-to-revenue ratio of 7-10x vs. normal
  infrastructure ratio of 1-2x.
- Goldman Sachs (Jim Covello, June 2024): Argued AI is "too expensive" and
  "unreliable" for many use cases. MIT economist Daron Acemoglu (cited) estimated
  AI would boost US GDP by only 0.9-1.1% over 10 years, far below the 15%+
  projections that would justify current spending.
- Elliott Management (July 2024): Called AI stocks "overhyped" and in a "bubble."
  Described many use cases as "never going to be cost-efficient."

**Counterargument:** AI revenue is growing rapidly. Microsoft's AI-related revenue
reportedly exceeded $10B quarterly run rate by late 2024. Google Cloud grew 35% YoY.
But much of this is hyperscalers selling AI services to each other or to VC-funded
startups burning investor capital (circular spending).

### Layer 3: Announcements vs. Physical Reality

- Stargate Project: $500B announced (Jan 2025); $100B initially committed; first
  building under construction in Abilene, TX. SoftBank's balance sheet had ~$30-40B
  deployable capital, not $500B. Financial structure is opaque.
- PJM Interconnection queue: ~90 GW of data center requests. Historical attrition
  rate: 75-80% of queued projects never reach commercial operation.
- ERCOT large load requests: ~60 GW pending (includes data centers and crypto).
- Industry estimates: Only 20-30% of announced data center projects proceed to
  construction within the initially announced timeline.
- Binding constraint: Power availability. Average time from interconnection request
  to energized service has stretched to 3-5 years in some regions (up from 1-2 years).
- As of early 2025: No major hyperscaler project cancellations reported. Pattern
  is delays and site relocation, not outright cancellation.

---

## 3. DeepSeek and the Jevons Paradox

DeepSeek's R1 model (January 2025) demonstrated competitive AI performance at
reportedly much lower training costs. Nvidia lost ~$600B in market cap in a single day.

**However, hyperscaler capex plans did not decrease.** In subsequent earnings calls:
- Microsoft: Maintained $80B+ guidance
- Meta: *Increased* 2025 guidance to $60-65B
- Alphabet: Announced $75B (above consensus)
- Amazon: Maintained $100B+ trajectory

Management teams invoked the Jevons paradox: cheaper AI inference increases adoption
and ultimately increases total compute demand. Historical precedent (LED lighting,
Moore's Law) supports this, but it is not guaranteed to apply.

---

## 4. AI Infrastructure as Share of US Investment

Source: Bureau of Economic Analysis (BEA) NIPA tables.

- Total US private nonresidential fixed investment: ~$3.5T annually (2024)
  - Structures: ~$750B
  - Equipment: ~$1.4T
  - Intellectual property: ~$1.4T
- Hyperscaler capex (~$300B) represents ~8-9% of total US private nonresidential
  fixed investment -- a significant and rapidly growing share.
- Data center construction is not separately reported in Census Bureau C30 data.
  Industry estimates (JLL, CBRE): $30-50B annually in US data center construction.

---

## 5. Power Demand Projections

| Source | Current DC Share | 2030 Projection | Type |
|--------|-----------------|-----------------|------|
| EIA | ~4% of US electricity | 15-20% demand growth by 2030 | Gov't projection |
| EPRI (May 2024) | ~4% | 4.6-9.1% of US generation | Research estimate |
| Goldman Sachs | ~3% (2022) | ~8% | Sell-side projection |

EPRI central scenario: data centers consuming 300-390 TWh annually by 2030
(roughly doubling from current levels).

---

## 6. Durability Analysis

Applying the project's durability taxonomy:

**Structural (persists regardless of AI's outcome):**
- Grid infrastructure upgrades (substations, transmission lines)
- Physical data center buildings (20-40 year life, repurposable for general cloud)
- Utility-scale solar and wind built to serve data center load
- Labor market effects if training pipelines are established

**Policy-dependent:**
- Nuclear restarts and SMR development (NRC approval, IRA credits)
- Utility rate structures and cost allocation rules
- Grid interconnection reform (FERC Order 2023)

**Demand-thesis-dependent:**
- GPU clusters and AI-specific equipment (3-6 year depreciation)
- AI-optimized cooling systems with limited alternative use
- Inference-optimized server designs
- Behind-the-meter gas generation (xAI model)

Key insight: Physical construction is ~30-40% of capex but creates the most durable
assets. Equipment is ~50-60% but depreciates rapidly. The grid gets lasting
infrastructure even if the AI demand thesis falters.

---

## 7. Contradictory Evidence / Bull Case

1. **Revenue IS growing:** Microsoft AI quarterly run rate >$10B; Google Cloud +35%
   YoY; Nvidia data center revenue $15B to $90B+ in one year.
2. **Historical precedent:** Fiber overbuild of 1998-2001 was called a bubble but
   built the backbone of the modern internet. AWS was criticized as wasteful but
   created market dominance.
3. **Prisoner's dilemma:** No hyperscaler can cut AI capex if competitors continue.
   Meta's stock rose when it increased capex guidance. The competitive dynamics
   sustain spending regardless of short-term returns.
4. **Inference demand could justify it:** Agentic AI applications (autonomous
   systems running continuously) could create persistent demand.

---

## 8. Key Data Gaps

1. No clean separation of "AI capex" vs. "general cloud capex" in public data.
2. No government statistical series tracks data center construction separately
   (Census C30, BEA NIPA tables lack the category).
3. No comprehensive database of announced vs. completed AI data center projects.
4. Stargate financial structure is opaque — $500B not substantiated by public filings.
5. OpenAI financials are private (reported $3.4B revenue, $5B+ losses in 2024).
6. AI-specific electricity consumption at facility level not systematically reported.
7. Supply chain bottleneck data (transformers, switchgear, backup generators) is
   anecdotal, not systematically quantified.

---

## 9. Primary Sources

### Free / Open Access
- SEC EDGAR (10-K, 10-Q filings): https://www.sec.gov/cgi-bin/browse-edgar
- EIA Annual Energy Outlook: https://www.eia.gov/outlooks/aeo/
- EIA Short-Term Energy Outlook: https://www.eia.gov/outlooks/steo/
- PJM Interconnection Queue: https://www.pjm.com/planning/services-requests/interconnection-queues
- ERCOT Grid Info: https://www.ercot.com/gridinfo/resource
- LBNL Interconnection Queue Studies: https://emp.lbl.gov/queues
- BEA NIPA Tables: https://apps.bea.gov/iTable/
- Census Bureau C30 (Construction Put in Place): https://www.census.gov/construction/c30/c30index.html
- Sequoia Capital "$600B Question": https://www.sequoiacap.com/article/ais-600b-question/

### Paywalled (findings available via press coverage)
- Goldman Sachs "Too Much, Too Soon?" (June 2024)
- Bernstein AI capex-to-revenue analysis (2024-2025)
- Elliott Management investor letter (July 2024)
- EPRI full data center power demand report (May 2024; summary free)
- S&P Global Market Intelligence data center tracker

---

## 10. Recommended Next Steps for DD-002

1. Pull PJM and ERCOT interconnection queue data directly — both publish
   downloadable datasets. Analyze the pipeline of data center power requests.
2. Download hyperscaler 10-K filings from SEC EDGAR for FY2024 to get audited
   capex figures (not just earnings call guidance).
3. Review LBNL annual interconnection queue study for attrition rates and
   time-to-completion data.
4. Create a "capex conversion funnel" analysis: announced -> permitted ->
   under construction -> energized. This is a novel analytical contribution.
5. Model the capex-to-revenue ratio over time to test whether the gap is
   narrowing or widening.
6. Investigate circular spending: how much "AI revenue" is hyperscalers
   selling to each other or to VC-funded startups burning investor capital.
