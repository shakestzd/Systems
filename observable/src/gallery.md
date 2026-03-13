---
title: Chart Gallery
sidebar: "Chart Gallery"
toc: false
---

```js
const stats    = await FileAttachment("data/stats.json").json();
const capex    = await FileAttachment("data/capex.json").json();
const mktcap   = await FileAttachment("data/mktcap.json").json();
const cloudRev = await FileAttachment("data/cloud_rev.json").json();

const byTicker = Object.fromEntries(mktcap.map(r => [r.ticker, r]));
```

<div class="byline">TZD Labs · Systems Research</div>

# Chart Gallery

Every chart from the research, without the narrative. Click through to the articles for context and analysis.

---

## Market Value vs. Infrastructure Spending

Seven US tech companies added $${mktcap.reduce((s, r) => s + r.gain_t, 0).toFixed(1)} trillion in market value since January 2023. The vertical line marks what they spent on infrastructure in 2025.

<div id="scroll-section" class="scroll-hero">
  <div id="sticky-valuation" class="scroll-hero-chart">
    <!-- interactive bar chart mounts here -->
  </div>
  <div class="scroll-steps">

<div class="scroll-step is-active" data-company="NVDA">

<strong>Nvidia added +$${(byTicker.NVDA?.gain_t ?? 0).toFixed(1)}T</strong> — the largest gain of the seven. Nvidia doesn't own a data center or run a cloud; it makes the chips the others buy. Its valuation rests on demand for those chips continuing to grow.

</div>

<div class="scroll-step" data-company="GOOGL">

<strong>Alphabet added +$${(byTicker.GOOGL?.gain_t ?? 0).toFixed(1)}T</strong> while spending more on infrastructure than Google Cloud earns. Its AI bet is partly funded from search advertising — $${stats.google_search_ad_rev_qtr_bn}B per quarter.

</div>

<div class="scroll-step" data-company="AAPL">

<strong>Apple added +$${(byTicker.AAPL?.gain_t ?? 0).toFixed(1)}T</strong> with almost none of the infrastructure spend. Apple spent $${stats.apple_capex_2024_bn}B on infrastructure in 2024 and routes AI tasks to OpenAI and Google.

</div>

<div class="scroll-step" data-company="META">

<strong>Meta added +$${(byTicker.META?.gain_t ?? 0).toFixed(1)}T</strong> after laying off roughly a quarter of its workforce in 2022–2023. It now plans to spend $${stats.meta_2026g}B in 2026.

</div>

<div class="scroll-step" data-company="AMZN">

<strong>Amazon added +$${(byTicker.AMZN?.gain_t ?? 0).toFixed(1)}T</strong> and crossed the line in 2025 where infrastructure spending exceeds what AWS earns.

</div>

<div class="scroll-step" data-company="MSFT">

<strong>Microsoft added +$${(byTicker.MSFT?.gain_t ?? 0).toFixed(1)}T</strong>. In three months (Sep–Nov 2025) it signed over $${stats.msft_neocloud_total_bn}B in off-balance-sheet leases with neocloud operators.

</div>

<div class="scroll-step" data-company="TSLA">

<strong>Tesla added +$${(byTicker.TSLA?.gain_t ?? 0).toFixed(1)}T</strong> on AI expectations rather than the car business. Investors pay about 160× expected earnings per share, versus 6× for a typical auto company.

</div>

<div class="scroll-step" data-company="all">

<strong>Combined, the seven added $${mktcap.reduce((s, r) => s + r.gain_t, 0).toFixed(1)}T</strong> against $${stats.capex_2025.toFixed(0)}B in 2025 infrastructure spending.

</div>

  </div><!-- .scroll-steps -->
</div><!-- .scroll-hero -->

```js
import { mountValuation } from "./js/charts/valuation.js";
const teardown = mountValuation(document.getElementById("scroll-section"), { mktcap, stats });
invalidation.then(teardown);
```

*From [Markets & Money](/Systems/dd001). Source: Yahoo Finance; SEC 10-K filings.*

---

## Spending Doubled in Two Years

```js
import { createCapexHistory } from "./js/charts/capex-history.js";
import { mountScrollChart } from "./js/animate.js";

const capexHistoryChart = createCapexHistory(capex, stats);
display(mountScrollChart(capexHistoryChart.node, capexHistoryChart.update, [
  { prose: "Seven years of steady growth — doubling roughly every cycle.", position: { top: "18%", left: "20%", maxWidth: "22ch" } },
  { prose: "2022: the inflection. ChatGPT launches. A new spending race begins.", position: { top: "18%", left: "20%", maxWidth: "22ch" } },
  { prose: "Two years to double what took six. The fastest acceleration in the industry's history.", position: { top: "18%", left: "20%", maxWidth: "22ch" } },
  { prose: `$${stats.capex_4co_2025.toFixed(0)}B in 2025 — ${stats.capex_4co_multiple}× the 2019 baseline.`, position: { top: "18%", left: "20%", maxWidth: "22ch" } },
]));
```

*From [Markets & Money](/Systems/dd001). Source: SEC 10-K filings via yfinance.*

---

## Cumulative Capex by Company, 2022–2026

```js
import { createStackedCapex } from "./js/charts/stacked-capex.js";

const stackedCapexChart = createStackedCapex(capex, stats);
display(mountScrollChart(stackedCapexChart.node, stackedCapexChart.update, [
  { prose: "Amazon, Alphabet, Microsoft, Meta, Oracle, and Nvidia — what each spent, year by year since 2022.", position: { top: "14%", right: "4%", maxWidth: "22ch" } },
  { prose: "Amazon has spent more than everyone else since 2022.", position: { top: "14%", right: "4%", maxWidth: "22ch" } },
  { prose: `Meta barely participated in 2022. They now plan to spend $${stats.meta_2026g}B in 2026.`, position: { top: "14%", right: "4%", maxWidth: "22ch" } },
  { prose: `Together, the six companies plan to spend $${stats.guidance_2026_point.toFixed(0)}B in 2026. Those plans have moved by ±${stats.guidance_band_pct}% in a single year before.`, position: { top: "14%", right: "4%", maxWidth: "22ch" } },
]));
```

*From [Markets & Money](/Systems/dd001). Source: SEC 10-K filings; Q4 2025 earnings calls.*

---

## Off-Balance-Sheet Infrastructure Commitments

```js
import { createOffBalance } from "./js/charts/off-balance.js";

const offBalanceChart = createOffBalance(stats);
display(mountScrollChart(offBalanceChart.node, offBalanceChart.update, [
  { prose: `The six companies' 2025 annual reports show a combined $${stats.capex_2025.toFixed(0)}B in direct infrastructure spending.`, position: { top: "14%", left: "40%", maxWidth: "18ch" } },
  { prose: "Long-term leases and off-balance-sheet financing vehicles add infrastructure commitments not captured in that total.", position: { top: "14%", left: "40%", maxWidth: "18ch" } },
  { prose: `Microsoft: $${stats.msft_2025.toFixed(0)}B reported. Neocloud leases add $${stats.msft_neocloud_total_bn}B not in that figure.`, position: { top: "14%", left: "40%", maxWidth: "18ch" } },
]));
```

*From [Markets & Money](/Systems/dd001). Source: Company announcements; NYT, Dec 15, 2025.*

---

## Capex-to-Revenue Ratio: Who Spends More Than They Earn?

```js
import { createRevenueRatio } from "./js/charts/revenue-ratio.js";

const revenueRatioChart = createRevenueRatio(capex, cloudRev);
display(mountScrollChart(revenueRatioChart.node, revenueRatioChart.update, [
  {}, {}, {}, {}
], { callout: "none" }));
```

*From [Markets & Money](/Systems/dd001). Source: SEC 10-K/10-Q filings via yfinance.*

---

## The Revenue Gap Widens

```js
import { createRevenueGap } from "./js/charts/revenue-gap.js";

const revenueGapChart = createRevenueGap(capex, cloudRev);
display(mountScrollChart(revenueGapChart.node, revenueGapChart.update, [
  { prose: "In early 2023, infrastructure spending and cloud revenue were roughly in sync.", position: { top: "18%", left: "8%", maxWidth: "24ch" } },
  { prose: "By 2024, infrastructure spending was growing faster than the cloud revenue it was built to serve.", position: { top: "18%", left: "8%", maxWidth: "24ch" } },
  { prose: "For Alphabet and Amazon, infrastructure spending now exceeds what their cloud businesses earn.", position: { top: "18%", left: "8%", maxWidth: "24ch" } },
]));
```

*From [Markets & Money](/Systems/dd001). Source: SEC 10-Q filings via yfinance.*

---

## Six Demand Theses, One Spending Line

```js
import { createDemandThesis } from "./js/charts/demand-thesis.js";
display(createDemandThesis(stats));
```

*From [Markets & Money](/Systems/dd001). Source: NYT, Sep 2025 (Metz & Weise); company earnings calls.*

---

## 2026 Guidance Uncertainty

```js
import { createGuidance } from "./js/charts/guidance.js";

const guidanceChart = createGuidance(stats);
display(mountScrollChart(guidanceChart.node, guidanceChart.update, [
  { prose: `The six companies spent a combined $${stats.capex_2025.toFixed(0)}B on infrastructure in 2025.`, position: { top: "12%", right: "4%", maxWidth: "22ch" } },
  { prose: `Their combined 2026 guidance: $${stats.guidance_2026_point.toFixed(0)}B.`, position: { top: "12%", right: "4%", maxWidth: "22ch" } },
  { prose: `Spending plans have shifted by ±${stats.guidance_band_pct}% in a single year before — Meta cut by roughly a third in 2022; Microsoft raised by roughly a third in FY2025.`, position: { top: "12%", right: "4%", maxWidth: "22ch" } },
]));
```

*From [Markets & Money](/Systems/dd001). Source: Q4 2025 earnings calls; SEC filings.*

---

## Three Scenarios for the Capex-Revenue Gap

```js
import { createScenarios } from "./js/charts/scenarios.js";

const scenariosChart = createScenarios(stats);
display(mountScrollChart(scenariosChart.node, scenariosChart.update, [
  {}, {}, {}, {}, {}
], { callout: "none" }));
```

*From [Markets & Money](/Systems/dd001). Source: TZD Labs analysis.*

---

*All charts from [How Capital Becomes Infrastructure](/Systems/). Data from public, freely accessible sources.*
