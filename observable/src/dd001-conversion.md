---
title: "The Conversion Gap"
---

```js
// ── Data ──────────────────────────────────────────────────────────────────
const data  = await FileAttachment("data/dd001_conversion_stats.json").json();
const stats = data.stats;
```

<div class="byline">Thandolwethu Zwelakhe Dlamini · TZD Labs Systems Research</div>

# From Announcement to Infrastructure: The Conversion Gap

<div class="prose-lead">

The [previous article](/Systems/dd001) documented about $${stats.capex_2025.toFixed(0)}B in reported infrastructure spending (2025) and about $${stats.guidance_2026_point.toFixed(0)}B forecast for 2026.

</div>

The waiting list for grid connections holds ${stats.queue_total_gw.toLocaleString()} gigawatts of proposed capacity, but only ${stats.queue_completion_pct}% of projects on that list historically reach full operation. A single Amazon campus in Indiana accounts for roughly half of Indiana's projected electricity demand growth through 2030.

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
// Callout center-right — positioned between the two bars in the y-axis and to the
// right of where the short equipment bar ends (year 2030), before the construction bar passes.
display(mountScrollChart(decompChart.node, decompChart.update, [
  { prose: `Equipment depreciates quickly: servers and GPUs last about 6 years. That's $${(stats.capex_2025 * stats.decomp_equip_pct / 100).toFixed(0)}B of the annual spend.`, position: { top: "28%", left: "55%", maxWidth: "22ch" } },
  { prose: `But ${stats.decomp_const_pct}% of spending goes into long-lived assets — substations, building shells, transmission lines — with 20-40 year lifetimes.`, position: { top: "28%", left: "55%", maxWidth: "22ch" } },
  { prose: "The AI demand forecast horizon is 3-5 years. Most construction assets will outlast every demand projection that justified them.", position: { top: "28%", left: "55%", maxWidth: "22ch" } },
  { prose: "6-year equipment. 20-40 year construction assets. 3-5 year demand forecast. The exposure is built into the asset mix.", position: { top: "28%", left: "55%", maxWidth: "22ch" } },
]));
```

A gas plant built to power a data center campus was justified by AI demand at the time of the decision. Once built, it operates for 40 years regardless of whether the data center scales as planned.

## The Physical Bottleneck Stack

Of all phases, getting connected to the grid takes the longest: a national median of about 5 years from application to actually coming online, up from about 3 years a decade ago (Rand et al., Lawrence Berkeley National Laboratory, 2025).

```js
import { createConstraintPhases } from "./js/charts/constraint-phases.js";

const constraintChart = createConstraintPhases();
// Callout lower-right — below the Grid interconnection row and to the right of where
// the shorter bars end (Energization at month 36), in the empty zone from month 37-60.
display(mountScrollChart(constraintChart.node, constraintChart.update, [
  { prose: "Getting a grid connection takes 5 years median, up from 3 years a decade ago. Every other phase queues behind it.", position: { top: "62%", right: "6%", maxWidth: "22ch" } },
  { prose: "Even running all steps in parallel where possible, the fastest realistic timeline is about three years.", position: { top: "62%", right: "6%", maxWidth: "22ch" } },
  { prose: "Getting connected to the grid is the hardest part: 5 years median, and rising. No amount of money compresses this.", position: { top: "62%", right: "6%", maxWidth: "22ch" } },
]));
```

Of projects that joined early enough to have had time to complete, the share that actually did so has been falling: ${stats.queue_cohort_2000_2005_pct}% for projects that joined in 2000–2005, ${stats.queue_cohort_2006_2010_pct}% for 2006–2010, and ${stats.queue_cohort_2011_2015_pct}% for 2011–2015 (Lawrence Berkeley National Laboratory, 2025).

## The Queue Keeps Growing. Completion Doesn't.

Over ${stats.queue_total_gw.toLocaleString()} gigawatts of proposed generation and storage is now waiting for a grid connection — roughly three times total US installed capacity. Of all capacity on the list from 2000 to 2024, **${stats.queue_withdrawal_pct}% was abandoned** and only **${stats.queue_completion_pct}% reached full operation.**

```js
import { createQueueGrowth } from "./js/charts/queue-growth.js";

const queueChart = createQueueGrowth(data, stats);
// Callout upper-left — the 2018-2020 bars are the shortest, leaving the upper-left
// quadrant clear before the dramatic growth years dominate the right side.
display(mountScrollChart(queueChart.node, queueChart.update, [
  { prose: `The grid connection waiting list has tripled in five years. Solar and storage dominate, but natural gas requests have grown to ${stats.queue_gas_gw} GW — the largest share in the queue's recorded history.`, position: { top: "14%", left: "8%", maxWidth: "22ch" } },
  { prose: `Only ${stats.queue_completion_pct}% of projects on the list historically reach full operation. ${stats.queue_withdrawal_pct}% are abandoned.`, position: { top: "14%", left: "8%", maxWidth: "22ch" } },
  { prose: `The latest year alone added ${(stats.queue_total_gw - data.queue_ts[data.queue_ts.length - 2].total_gw).toLocaleString()} GW — the single largest annual addition since the queue's inception.`, position: { top: "14%", left: "8%", maxWidth: "22ch" } },
]));
```

The mix of projects waiting has shifted: natural gas requests grew to about ${stats.queue_gas_gw} gigawatts by end-2024. Solar remains dominant at about ${stats.queue_solar_gw.toLocaleString()} GW (${stats.queue_solar_pct}% of total), storage about ${stats.queue_storage_gw.toLocaleString()} GW (${stats.queue_storage_pct}%), wind about ${stats.queue_wind_gw} GW (${stats.queue_wind_pct}%).

## Case Study: Project Rainier

Amazon's Project Rainier campus near New Carlisle, Indiana — a ${stats.rainier_gw}-gigawatt facility built for Anthropic — is documented in a June 2025 New York Times investigation (Weise and Metz) and in AEP Indiana regulatory filings.

```js
import { createRainierProgress } from "./js/charts/rainier-progress.js";

const rainierChart = createRainierProgress(stats);
// Callout center-left — the large vertical gap between the progress bar (top third)
// and the milestone timeline dots (lower third) is the clearest open zone.
display(mountScrollChart(rainierChart.node, rainierChart.update, [
  { prose: `${stats.rainier_dc_built_jun2025} of ${stats.rainier_dc_planned} data center buildings complete after roughly two years of construction. Each is larger than a football stadium.`, position: { top: "44%", left: "22%", maxWidth: "24ch" } },
  { prose: "The timeline: utility talks began in early 2023. Land acquired early 2024. First buildings operating mid-2025. Full campus estimated 2027.", position: { top: "44%", left: "22%", maxWidth: "24ch" } },
  { prose: `At ${stats.rainier_gw} gigawatts, this single campus accounts for about half of Indiana's projected electricity demand growth. American Electric Power plans to meet ${stats.aep_gas_share_pct}% of that new demand with natural gas.`, position: { top: "44%", left: "22%", maxWidth: "24ch" } },
]));
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
