---
title: "Who Holds the Downside"
sidebar: "Who Holds the Downside"
---

```js
// ── Data ──────────────────────────────────────────────────────────────────
const stats = await FileAttachment("data/dd001_risk_stats.json").json();
```

<div class="byline">Thandolwethu Zwelakhe Dlamini · TZD Labs Systems Research</div>

# Who Holds the Downside?

<div class="prose-lead">

The [first article](/Systems/dd001) documented about $${stats.capex_2025.toFixed(0)}B in infrastructure spending. The [second](/Systems/dd001-conversion) showed how slowly it converts to working infrastructure.

</div>

Neoclouds borrow against projected lease renewals they have no contractual guarantee of receiving. Those loans reach pension funds and endowments through bond offerings. Utilities build substations and transmission lines to serve the load, recovering the cost from ratepayers over forty-year depreciation schedules.


## Demand forecasts run 3–5 years. The assets last 25–50.

```js
import { createAssetGap } from "./js/charts/asset-gap.js";
import { mountScrollChart } from "./js/animate.js";

const gapChart = createAssetGap();
display(mountScrollChart(gapChart.node, gapChart.update, [
  {}, {}, {}, {},
], { callout: "none" }));
```

## Exposure Grows With Distance From the Decision

The bond offerings describe AI infrastructure as a growth investment backed by a lease renewal the tech company has no legal obligation to provide. Rural communities extended tax incentives and grid capacity for facilities whose operating decisions are made elsewhere.

```js
import { createRiskTimeline } from "./js/charts/risk-timeline.js";

const timelineChart = createRiskTimeline(stats);
display(mountScrollChart(timelineChart.node, timelineChart.update, [
  {}, {}, {}, {}, {},
], { callout: "none" }));
```


## The Beignet Pattern: Meta's Shell Financing Structure

Meta created Beignet Investor LLC to borrow $${stats.meta_beignet_financing_bn}B for a ${stats.meta_louisiana_dc_gw}-gigawatt data center in Richland Parish, Louisiana. Blue Owl Capital provided 80% of the financing. Pimco and BlackRock sold bonds maturing in **${stats.beignet_bond_maturity}** to pension funds, endowments, insurers, and financial advisers.

Meta leased the facility back through ${stats.meta_beignet_lease_years}-year terms, recording the payments as an operating cost.

```js
import { createSpvChain } from "./js/charts/spv-chain.js";

const spvChart = createSpvChain(stats);
display(mountScrollChart(spvChart.node, spvChart.update, [
  {}, {}, {}, {},
], { callout: "none" }));
```

A Columbia Business School professor drew explicit parallels to the off-balance-sheet vehicles that preceded the dot-com bust.


## Neocloud Leases

In Childress County, Rennesøy, and Mäntsälä, grid operators built or upgraded infrastructure for data centers that did not exist three years ago. In a single quarter, Sep-Nov 2025, Microsoft committed over $${stats.msft_neocloud_total_bn}B in leases to Nebius (Mäntsälä, Finland), Nscale (Rennesøy, Norway), Iren (Childress, Texas and Prince George, British Columbia), and Lambda (colocation). Each lease runs three to five years. The grid infrastructure built to support them runs twenty to fifty.

```js
import { createNeocloudLeases } from "./js/charts/neocloud-leases.js";

const neocloudChart = createNeocloudLeases(stats);
display(mountScrollChart(neocloudChart.node, neocloudChart.update, [
  {}, {}, {},
], { callout: "none" }));
```

## The CoreWeave Chain

CoreWeave borrowed at ${stats.coreweave_interest_rate_pct}%+ to build capacity that OpenAI committed to purchase (up to $${stats.openai_coreweave_commitment_bn.toFixed(0)}B). Microsoft is CoreWeave's dominant customer — about 62% of 2024 revenue *(CoreWeave IPO prospectus, March 2025)*. OpenAI separately committed to route $${stats.openai_msft_compute_promise_bn}B in computing through Microsoft.

```js
import { createCoreweaveCallout } from "./js/charts/coreweave-callout.js";
display(createCoreweaveCallout(stats));
```


## FERC hasn't decided who pays for grid upgrades — utilities are building anyway

The Federal Energy Regulatory Commission opened docket AD24-11 in May 2024, asking whether large electricity users like AI data centers should pay for the grid upgrades they require, or whether those costs spread across all ratepayers.

```js
import { createFercAllocation } from "./js/charts/ferc-allocation.js";

const fercChart = createFercAllocation();
display(mountScrollChart(fercChart.node, fercChart.update, [
  {}, {}, {},
], { callout: "none" }));
```

The docket is a Notice of Inquiry, a comment period that carries no obligation to result in a rule.

---

In Richland Parish, Meta's exit right runs to ${stats.meta_beignet_exit_year}. The bonds Pimco and BlackRock sold against that campus mature in ${stats.beignet_bond_maturity}.

[DD-002](/Systems/dd002) asks whether the grid modernization that AI infrastructure requires creates shared capacity or private bypass.


## Sources & Methodology

**SPV structure (Beignet).** NYT, "How Tech's Biggest Companies Are Offloading the Risks of the A.I. Boom," Dec 15, 2025 (Weise & Tan). Blue Owl Capital project financing terms. Bond maturity dates from SEC filings.

**Neocloud leases.** Deal amounts (Nebius $${stats.msft_nebius_deal_bn}B, Nscale $${stats.msft_nscale_deal_bn}B, Iren $${stats.msft_iren_deal_bn}B) from NYT, Dec 15, 2025 (Weise & Tan) and individual company announcements. Community locations: IREN Limited, FY2025 Annual Report (ASX: IDA) — Childress, TX and Prince George, BC campuses; Nebius Group, 6-K filings (Nasdaq: NBIS) — Mäntsälä, Finland data center; Nscale company disclosures — Rennesøy, Norway campus; Lambda Labs, infrastructure documentation — colocation model (no owned facilities). Note: the specific Sep–Nov 2025 Microsoft deal set as a group has not been independently confirmed from SEC filings; amounts from NYT reporting.

**CoreWeave.** S-1/A filing, March 2025 (SEC EDGAR CIK 0001956029). Table of Remaining Performance Obligations. Interest rates from S&P credit analysis.

**FERC AD24-11.** Notice of Inquiry, May 2024 (ferc.gov eLibrary). FERC Order 2023 (July 2023) governs generator interconnection reform; it does not apply to large-load data center interconnection.

**Risk exposure timeline.** Author's analysis based on SEC filings, CoreWeave S-1, CRS reports, and company announcements. Exit dates and bond maturities from primary documents.

*All data from public, freely accessible sources. Analysis: TZD Labs, February 2026.*
