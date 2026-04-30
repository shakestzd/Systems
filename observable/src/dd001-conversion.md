---
title: "Only 14% of Grid Connection Requests Reach Operation"
sidebar: "The Conversion Gap"
---

```js
// ── Data ──────────────────────────────────────────────────────────────────
const data  = await FileAttachment("data/dd001_conversion_stats.json").json();
const stats = data.stats;
```

<div class="byline">Thandolwethu Zwelakhe Dlamini · TZD Labs Systems Research</div>

# Only ${stats.queue_completion_pct}% of grid connection requests reach operation

<div class="prose-lead">

The [previous article](/Systems/dd001) documented about $${stats.capex_2025.toFixed(0)}B in reported infrastructure spending (2025) and about $${stats.guidance_2026_point.toFixed(0)}B forecast for 2026.

</div>

The waiting list for grid connections holds ${stats.queue_total_gw.toLocaleString()} gigawatts of proposed capacity. A single Amazon campus in Indiana accounts for roughly half of Indiana's projected electricity demand growth through 2030.

---

## What Gets Built Lasts Longer Than the Outlook


| Category | What Gets Built | Life | Persists? |
| :--- | :--- | :--- | :--- |
| **Structural** | Grid upgrades, substations, DC shells | 20-50 yr | Yes |
| **Policy-dependent** | Nuclear restarts, SMR, rate structures | Varies | If regime holds |
| **Demand-thesis** | GPU clusters, AI cooling, inference hardware | 3-6 yr | No |

Companies' 2024 annual reports show about ${stats.decomp_const_pct}% of physical assets on their books are long-lived construction assets (land, buildings, permanent improvements, construction in progress) and about ${stats.decomp_equip_pct}% are equipment (servers, network gear, machinery). The range across companies with clear disclosure is ${stats.decomp_const_low}–${stats.decomp_const_high}%.

```js
import { createCapexDecomp } from "./js/charts/capex-decomp.js";
import { mountScrollChart } from "./js/animate.js";

const decompChart = createCapexDecomp(stats);
display(mountScrollChart(decompChart.node, decompChart.update, [
  {}, {}, {}, {},
], { callout: "none" }));
```

A gas plant built to power a data center campus was justified by AI demand at the time of the decision. Once built, it operates for 40 years regardless of whether the data center scales as planned.

## Grid connection takes 5 years median — up from 3 a decade ago

Of all phases, getting connected to the grid takes the longest: a national median of about 5 years from application to actually coming online (Rand et al., Lawrence Berkeley National Laboratory, 2025).

```js
import { createConstraintPhases } from "./js/charts/constraint-phases.js";

const constraintChart = createConstraintPhases();
display(mountScrollChart(constraintChart.node, constraintChart.update, [
  {}, {}, {},
], { callout: "none" }));
```

Of projects that joined early enough to have had time to complete, the share that actually did so has been falling: ${stats.queue_cohort_2000_2005_pct}% for projects that joined in 2000–2005, ${stats.queue_cohort_2006_2010_pct}% for 2006–2010, and ${stats.queue_cohort_2011_2015_pct}% for 2011–2015 (Lawrence Berkeley National Laboratory, 2025).

## The Queue Keeps Growing. Completion Doesn't.

Over ${stats.queue_total_gw.toLocaleString()} gigawatts of proposed generation and storage is now waiting for a grid connection — roughly three times total US installed capacity. Of all capacity on the list from 2000 to 2024, **${stats.queue_withdrawal_pct}% was abandoned** and only **${stats.queue_completion_pct}% reached full operation.**

```js
import { createQueueGrowth } from "./js/charts/queue-growth.js";

const queueChart = createQueueGrowth(data, stats);
display(mountScrollChart(queueChart.node, queueChart.update, [
  {}, {}, {},
], { callout: "none" }));
```

The mix of projects waiting has shifted: natural gas requests grew to about ${stats.queue_gas_gw} gigawatts by end-2024. Solar remains dominant at about ${stats.queue_solar_gw.toLocaleString()} GW (${stats.queue_solar_pct}% of total), storage about ${stats.queue_storage_gw.toLocaleString()} GW (${stats.queue_storage_pct}%), wind about ${stats.queue_wind_gw} GW (${stats.queue_wind_pct}%).

## Case Study: Project Rainier

Amazon's Project Rainier campus near New Carlisle, Indiana — a ${stats.rainier_gw}-gigawatt facility built for Anthropic — is documented in a June 2025 New York Times investigation (Weise and Metz) and in AEP Indiana regulatory filings.

```js
import { createRainierProgress } from "./js/charts/rainier-progress.js";

const rainierChart = createRainierProgress(stats);
display(mountScrollChart(rainierChart.node, rainierChart.update, [
  {}, {}, {},
], { callout: "none" }));
```

**Public subsidy:** Indiana granted a 50-year sales tax break (about $${stats.rainier_tax_break_sales_bn}B) plus county property tax breaks (about $${stats.rainier_tax_break_property_bn}B) — roughly $${stats.rainier_tax_break_sales_bn + stats.rainier_tax_break_property_bn}B in public support for one campus. About ${stats.rainier_workers_weekly.toLocaleString()} construction workers are on site weekly.

Rainier is a special case: Amazon negotiated directly with the local power company (American Electric Power Indiana) and bypassed the standard grid connection waiting list. Most AI data centers cannot do this — they join the standard queue and face the same drop-out rates documented above.

## Announced Is Not Delivered

A White House press conference on January 21, 2025 declared $${stats.stargate_announced_bn}B in AI infrastructure investment. In practice, only $${stats.stargate_initial_bn}B of Phase 1 is committed and under active deployment. The remaining $${stats.stargate_announced_bn - stats.stargate_initial_bn}B depends on SoftBank raising additional debt and finding co-investors — the financial structure and timeline remain unspecified.

Of the $${stats.stargate_announced_bn}B declared at the White House, $${stats.stargate_announced_bn - stats.stargate_initial_bn}B has no committed financial structure.

---

Those questions are the subject of [DD-002](/Systems/dd002) (Grid Modernization). The question of *who holds the financial loss* when long-lived assets outlast the demand forecast that justified them is answered in the [next article](/Systems/dd001-risk).

---

## Sources & Methodology

**PP&E decomposition.** FY2024 10-K property schedules from SEC EDGAR for Amazon, Alphabet, Microsoft, and Meta. Categories classified as construction-class (land, buildings, leasehold improvements, CIP) or equipment-class (servers, network equipment, machinery).

**Interconnection queue.** Rand et al., "Queued Up: Characteristics of Power Plants Seeking Transmission Interconnection -- As of the End of 2024," LBNL, April 2025 (emp.lbl.gov/queues). Cohort completion rates from LBNL Table 3.

**Physical constraint timelines.** LBNL Queued Up 2025 (interconnection median); TSMC quarterly reports (CoWoS packaging lead times); CS-1 Transformer Manufacturing analysis; industry construction benchmarks.

**Project Rainier.** NYT, "At Amazon's Biggest Data Center, Everything Is Supersized for A.I.," Jun 24, 2025 (Weise & Metz). AEP Indiana regulatory filings. Citizens Action Coalition subsidy estimates.

**Stargate.** White House announcement, Jan 21, 2025; FT analysis of SoftBank balance sheet.

*All data from public, freely accessible sources. Analysis: TZD Labs, February 2026.*
