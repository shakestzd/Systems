# DD-001 Draft Prose Sections — NYT Article Integration
## For: `notebooks/dd001_capital_reality/01_capex_vs_reality.py`

*Each section below is a draft Marimo markdown cell. Placement markers show where
it integrates into the existing notebook. Data references use `stats['key']` format
matching the source_citations CSV — these need to be wired into the stats computation
cell before the prose will render.*

---

## SECTION 1: Off-Balance-Sheet Caveat
**Placement:** Insert after the capex acceleration chart caption cell (the one ending
"Sources: SEC 10-K/10-Q filings via yfinance; guidance from Q4 2025 earnings calls.")

**Purpose:** The current notebook measures *disclosed* capex. The NYT risk-offloading
article documents a parallel capital channel that doesn't appear in these figures.

```python
@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    > **What these numbers miss: off-balance-sheet infrastructure commitments.**
    > The capex figures above capture capital expenditures as reported in SEC filings.
    > They exclude a parallel — and growing — channel: leased and SPV-financed
    > infrastructure that shows up as operating expenses, not capital investments.
    >
    > In September–November 2025 alone, Microsoft signed over $50B in 3-5 year
    > neocloud leases (Nebius $17B, Nscale $23B, Iren $10B, Lambda multi-billion) —
    > none of which appears in its capex line (NYT, Dec 2025). Meta structured
    > ~$30B in Louisiana data center financing through a special purpose vehicle
    > (Beignet Investor LLC), with Blue Owl Capital providing 80% of the funding
    > and Pimco selling the underlying bonds. The deal is classified as an operating
    > lease, keeping the debt off Meta's balance sheet.
    >
    > This means the true infrastructure commitment is **materially higher** than
    > the ~\\${stats['capex_2025']:.0f}B in reported capex. It also means the risk
    > distribution is different from what the balance sheets show — a dynamic traced
    > in the risk distribution section below.
    >
    > *Sources: NYT, "How Tech's Biggest Companies Are Offloading the Risks of the
    > A.I. Boom," Dec 15, 2025 (Weise & Tan).*
    """)
    return
```

---

## SECTION 2: Risk Distribution Layer (NEW SECTION)
**Placement:** Insert as a new section after the durability taxonomy ("What Persists")
section and before the "Where This Research Goes Next" section.

**Purpose:** The existing notebook asks "what persists?" but doesn't ask "who holds the
downside?" — the risk-offloading article fills this gap and adds a distributional
dimension that strengthens the analytical frame.

```python
@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    ---

    ## Who Holds the Downside? Risk Distribution in the AI Buildout

    The durability taxonomy above classifies *what* persists. This section traces
    *who bears the downside* when long-lived assets outlast the demand thesis that
    justified them. The answer has shifted significantly through 2025: the companies
    making the investment decisions have systematically moved financial exposure to
    entities further from the decision.

    The mechanisms fall into three categories:

    **1. Special Purpose Vehicles (SPVs)**

    Meta's Louisiana data center is the clearest case. Meta created Beignet Investor
    LLC and worked with Blue Owl Capital to borrow ~$30B for the project. Blue Owl
    provided 80% of the financing; Pimco sold bonds maturing in **2049** to its
    clients — insurers, pension funds, endowments, and financial advisers. Meta
    agreed to "rent" the facility through a series of 4-year leases, classifying the
    arrangement as operating cost rather than debt.

    The risk asymmetry: Meta can walk away as early as 2033. The bondholders are
    committed through 2049. If AI demand underwhelms, the data center's value
    depreciates — and that loss lands on pension fund portfolios and insurance
    company balance sheets, not Meta's.

    A Columbia Business School accounting professor drew explicit parallels to the
    off-balance-sheet vehicles that preceded the dot-com bust (NYT, Dec 2025). The
    comparison is directional, not exact — Meta has provided protections that future
    deals may not require — but the structural pattern is recognizable.

    **2. Neocloud Leases**

    Microsoft signed over $50B in 3-5 year data center leases in a single quarter
    (Sep–Nov 2025), spread across at least four neocloud providers. These shorter
    contracts give Microsoft flexibility: computing power that shows up as day-to-day
    operating expense rather than decades-long capital commitment.

    The counterparties — Nebius (ex-Yandex founder), Nscale (privately held, British),
    Iren (former bitcoin miner), Lambda — are building the data centers with their
    own capital. If Microsoft's demand shifts after the lease terms end, these
    smaller companies and their lenders absorb the stranded-asset risk.

    The pattern mirrors how large retailers use franchise and lease structures to
    maintain optionality while franchisees bear the capital risk. The difference is
    scale: these are multi-billion-dollar infrastructure assets with 20-40 year
    physical lifetimes financed against 3-5 year demand commitments.

    **3. Downstream Concentration: The CoreWeave–OpenAI Chain**

    CoreWeave, the largest neocloud, has tied its future to OpenAI — borrowing
    billions at 10%+ interest rates to build capacity that OpenAI has committed to
    purchase (up to $22.4B). Microsoft and Google also supply OpenAI computing,
    partly through CoreWeave. OpenAI has separately promised to route $250B in
    computing through Microsoft.

    This creates a dependency chain: CoreWeave's viability depends on OpenAI's
    growth, which depends on consumer and enterprise adoption of AI products that
    — as the revenue section documented — haven't yet generated returns matching
    the infrastructure investment. CoreWeave maintains that no single customer
    represents more than 35% of future contracted revenue, but declined to disclose
    how much capacity ultimately serves OpenAI (NYT, Dec 2025).

    ### What This Means for the Analysis

    The risk distribution pattern has a directional implication for the durability
    question: **the entities best positioned to evaluate AI demand (the tech giants)
    are systematically reducing their exposure, while entities with less visibility
    into demand trajectories (private credit, pension funds, neocloud startups)
    are absorbing it.**

    This doesn't mean the investments are wrong. It means the market structure is
    pricing risk asymmetrically — and if the demand thesis proves incorrect, the
    consequences will be distributed across the financial system in ways that the
    companies' own balance sheets won't fully reflect.

    | Risk bearer | Mechanism | Exposure window | Visibility into AI demand |
    | :--- | :--- | :--- | :--- |
    | Tech giants (Meta, MSFT) | SPVs, short-term leases | 3-5 years (can exit) | **High** (own the products) |
    | Neoclouds (CoreWeave, Nebius) | Debt-funded capacity build | 10-20 years (debt terms) | Medium (contracted, not owned) |
    | Private credit / bondholders | Bond purchases, loans | 20-25 years (bond maturity) | **Low** (financial instruments) |
    | Pension funds / endowments | Bond portfolios | Indefinite (asset allocation) | **None** (downstream investors) |
    | Rural communities | Tax incentives, grid load | **Permanent** (infrastructure) | **None** |

    *Sources: NYT, "How Tech's Biggest Companies Are Offloading the Risks of the
    A.I. Boom," Dec 15, 2025 (Weise & Tan); CoreWeave S-1 filing (2025); S&P Global
    Ratings (Beignet bond analysis).*
    """)
    return
```

---

## SECTION 3: Revenue Question Enhancement
**Placement:** Insert at the end of the existing "Revenue Question" section, before
the revenue gap chart cell. Adds the demand-thesis diversity dimension from the
"What Are They Building" article.

**Purpose:** The current section asks "does revenue justify capex?" The NYT guide
reveals that the companies are hedging across at least six different demand scenarios —
which changes the nature of the revenue question.

```python
@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    ### The Demand Thesis Diversity Problem

    The revenue gap is compounded by a structural issue: the companies building this
    infrastructure cannot articulate a single demand thesis that justifies the spend.
    A September 2025 industry survey (NYT, Metz & Weise) identified at least six
    overlapping visions being pursued simultaneously:

    1. **Better search** — replacing Google's $54B/quarter ad engine with chatbots
       (but fewer than 6% of ChatGPT's 700M+ users pay, and chatbot economics
       don't naturally support advertising)
    2. **Productivity tools** — AI for office workers, code generation, document
       summarization (but McKinsey found ~80% of businesses that tried gen AI
       reported no significant bottom-line impact)
    3. **Everything assistant** — AI embedded in glasses, smart speakers, shopping
       (Meta's AI glasses remain a niche product; Alexa has been a money-loser
       for over a decade)
    4. **AI companions** — synthetic friends on social networks ($300/month
       subscription, growing criticism of social harms)
    5. **Scientific breakthroughs** — drug discovery, materials science (real but
       narrow; Google's AlphaFold won a Nobel Prize but revenue model is indirect)
    6. **AGI / superintelligence** — matching or exceeding human cognition (no
       articulated revenue model; timeline is decades, not years)

    Each vision implies a different revenue trajectory, infrastructure requirement,
    and risk profile. The capex figures aggregate across all six. The revenue figures
    currently reflect mainly #1 and #2 — productivity and search. If #3-#6 don't
    materialize as revenue-generating products, the infrastructure built for them
    becomes capacity in search of demand.

    Amazon's CEO offered the most concrete breakdown: roughly 10% of AI
    infrastructure is used for training (building) AI systems, while 80-90% is
    for delivering them to customers (NYT, Sep 2025). That split implies the
    buildout is demand-driven, not research-driven — which makes the revenue
    question even more central to whether the infrastructure gets utilized.

    One Sequoia Capital partner described the dynamic as a chess game among a
    handful of executives with implications for everyone else (NYT, Sep 2025).
    The Allen Institute's founding CEO offered a simpler explanation for the
    spending: FOMO.

    *Sources: NYT, "What Exactly Are A.I. Companies Trying to Build?" Sep 16, 2025
    (Metz & Weise); McKinsey Global Survey on AI (2025); OpenAI public statements.*
    """)
    return
```

---

## SECTION 4: Project Rainier Case Study
**Placement:** Insert within the "Announcements vs. Physical Reality" section, after
the Stargate bullet point. This grounds the abstract queue/conversion discussion in
a specific, documented facility.

**Purpose:** The Amazon data center article provides the most detailed public account
of what AI infrastructure conversion actually looks like on the ground — timelines,
costs, grid impact, community externalities.

```python
@app.cell(hide_code=True)
def _(mo, stats):
    mo.md(f"""
    ### Case Study: Project Rainier (Amazon/Anthropic, Indiana)

    The most detailed public record of AI infrastructure conversion comes from
    Amazon's Project Rainier campus near New Carlisle, Indiana — a facility built
    specifically for Anthropic and documented by the NYT in June 2025.

    **Scale and timeline:**
    - 1,200 acres of former cornfield, 15 miles west of South Bend
    - 2.2 GW planned capacity — enough to power a million homes
    - ~30 data centers planned; 7 built by June 2025 (each larger than a football
      stadium), with four construction firms working simultaneously
    - ~4,000 construction workers on site weekly
    - Hundreds of thousands of Amazon Trainium 2 chips, connected by hundreds of
      thousands of miles of fiber

    **Public subsidy and cost:**
    - Indiana legislature: 50-year sales tax break (~$4B, per Citizens Action
      Coalition estimate)
    - County property/technology tax breaks: ~$4B additional over 35 years
    - Total public subsidy: **~$8B** for one campus
    - Amazon committed $11B in the tax deal for 16 buildings; now plans nearly
      double that
    - Amazon paid $7M for road improvements + $120K for traffic enforcement overtime

    **Grid impact (the DD-002 connection):**
    - AEP (local utility) told regulators that data centers will more than double
      Indiana's peak power demand: from 2.8 GW (2024) to 7+ GW by ~2030
    - **Amazon's campus alone accounts for about half of the additional load**
    - AEP plans to meet ~75% of additional power demand with natural gas — directly
      connecting AI infrastructure to fossil fuel expansion
    - The facility will use millions of gallons of water annually for cooling

    **Community externalities:**
    - State investigating whether Amazon's dewatering (2.2M gallons/hour for 730
      days to install underground infrastructure) caused neighbors' wells to run dry
    - Increased traffic congestion and accidents
    - Community opposition to construction on a 10-acre wetland
    - A retired mail carrier described watching the wetlands being prepared for
      burial under construction fill

    **The conversion lesson:** Project Rainier shows what "announcement → infrastructure"
    actually requires: utility negotiations begun months after ChatGPT launched
    (early 2023), land acquired by early 2024, first buildings up by mid-2025. That's
    roughly a 2-year timeline from site selection to initial operation — and the
    campus is still less than a quarter built. The constraint isn't capital. It's the
    physical sequence: land → permits → utility interconnection → construction →
    equipment installation → energization.

    Amazon's chip strategy adds a wrinkle to the equipment-tier durability analysis:
    Trainium 2 chips are less powerful individually than Nvidia's latest but pack at
    2× density per data center. If training demand shifts, Amazon's VP stated the
    facility can pivot from training to inference delivery — but the 2.2 GW grid
    interconnection and the natural gas plants built to serve it remain regardless
    of what the chips do.

    *Source: NYT, "At Amazon's Biggest Data Center, Everything Is Supersized for
    A.I.," Jun 24, 2025 (Weise & Metz).*
    """)
    return
```

---

## SECTION 5: Grid-Impact Bridge to DD-002
**Placement:** Within the "Where This Research Goes Next" section, expanding the
DD-002 bullet point with concrete data from the Amazon article.

**Purpose:** The existing DD-002 teaser is abstract. Project Rainier gives it teeth.

```python
# REPLACE the existing DD-002 bullet in the "Where This Research Goes Next" section:
#
# Old:
#   - **DD-002: Grid Modernization** (active) — What generation mix is getting
#     built? Which fuel types? Where geographically? ...
#
# New (expanded):

"""
- **DD-002: Grid Modernization** (active) — What generation mix is getting
  built? Which fuel types? Where geographically? Who benefits from the
  cost allocation? What feedback loops shape the buildout trajectory?
  The Project Rainier case provides an anchor: one campus in Indiana
  accounts for ~half of the state's projected load growth through 2030,
  with the utility planning 75% natural gas to meet that demand. Meta's
  Louisiana data center (2 GW) and OpenAI's Texas facility (1.2 GW)
  are comparable in scale. DD-002 traces whether these facility-level
  patterns aggregate into a grid-wide shift in generation mix and
  emissions trajectory.
"""
```

---

## SECTION 6: Updated Source Block
**Placement:** Append to the existing sources footnote at the bottom of the notebook.

```
NYT, "How Tech's Biggest Companies Are Offloading the Risks of the A.I. Boom,"
Dec 15, 2025 (Karen Weise & Eli Tan).
NYT, "What Exactly Are A.I. Companies Trying to Build? Here's a Guide,"
Sep 16, 2025 (Cade Metz & Karen Weise).
NYT, "At Amazon's Biggest Data Center, Everything Is Supersized for A.I.,"
Jun 24, 2025 (Karen Weise & Cade Metz).
```

---

## INTEGRATION NOTES

### Stats cell additions needed
The following keys from `nyt_source_citations_update.csv` should be loaded into
the stats computation cell for dynamic rendering:

**From risk-offloading article (Dec 2025):**
- `meta_beignet_financing_bn` → used in Section 2 (risk distribution)
- `msft_neocloud_total_bn` → used in Sections 1 and 2
- `openai_coreweave_commitment_bn` → used in Section 2
- `coreweave_interest_rate_pct` → used in Section 2
- `beignet_bond_maturity` → used in Section 2
- `meta_beignet_exit_year` → used in Section 2

**From "What Are They Building" (Sep 2025):**
- `chatgpt_monthly_users_m` → used in Section 3
- `openai_paid_subscriber_pct` → used in Section 3
- `google_search_ad_rev_qtr_bn` → used in Section 3
- `mckinsey_no_impact_pct` → used in Section 3

**From Amazon data center article (Jun 2025):**
- `rainier_gw` → used in Section 4
- `rainier_dc_planned` → used in Section 4
- `rainier_dc_built_jun2025` → used in Section 4
- `rainier_tax_break_sales_bn` + `rainier_tax_break_property_bn` → combined for ~$8B
- `aep_indiana_peak_2024_gw` / `aep_indiana_peak_2030_gw` → Section 4
- `aep_gas_share_pct` → Section 4 and DD-002 bridge
- `rainier_workers_weekly` → Section 4

### Framing refinement summary
The revised analytical frame becomes:

| Layer | Question | Notebook Section |
|:---|:---|:---|
| **1. Scale** | How much capital? | Existing (capex charts) + Section 1 (off-book caveat) |
| **2. Conversion** | Does it become infrastructure? | Existing (queue) + Section 4 (Rainier case) |
| **3. Revenue justification** | What demand model supports it? | Existing + Section 3 (demand diversity) |
| **4. Risk distribution** | Who holds the downside? | **NEW** — Section 2 |
| **5. Durability** | What outlasts the cycle? | Existing (taxonomy, decomposition) |

The key narrative shift: from "is there a gap?" (yes, documented) to "when the gap
resolves — through demand growth or demand disappointment — where do the
consequences land?" That question connects the financial analysis to the grid,
labor, and community impacts traced in DD-002 and DD-003.
