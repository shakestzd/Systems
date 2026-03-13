# Marimo → Observable Conversion Guide

Reference for AI agents converting Marimo notebook charts to Observable Framework
interactive articles. Based on the DD-001 conversion (9 charts).

---

## Architecture

```
Marimo (analysis workbench)          Observable (publication layer)
─────────────────────────────        ──────────────────────────────
Python SQL query                     data/*.json.py (Python loaders)
   ↓                                    ↓
pandas DataFrame                     FileAttachment().json()
   ↓                                    ↓
matplotlib figure                    createXxxChart(data) → { node, update }
   ↓                                    ↓
save_fig() → static PNG              mountScrollChart(node, update, steps)
                                        ↓
                                     display() → DOM (scroll-animated)
```

Both systems query the same DuckDB database. The Observable data loaders
(`src/data/*.json.py`) mirror the Marimo `stats` cell — same SQL, same numbers.

---

## Design System Mapping

| Concept | Marimo (`src/plotting.py`) | Observable (`js/design.js`) |
|---------|---------------------------|----------------------------|
| Accent | `COLORS["accent"]` = `#b84c2a` | `ACCENT = "#b84c2a"` (identical) |
| Non-focus gray | `CONTEXT` = `#c0c0c0` | `CONTEXT = "#b0aba4"` (darker for cream bg) |
| Text color | `COLORS["text_dark"]` = `#1a1917` | `INK = "#1a1917"` |
| Label color | — | `INK_LIGHT = "#6b6560"` |
| Axis rules | — | `RULE = "#c8c2b8"` |
| Background | white | `PAPER = "#f5f1eb"` (cream) |
| Company colors | `company_color(ticker)` | `cc(ticker)` |
| Company labels | `company_label(ticker)` | `cl(ticker)` |
| Font | `FONTS["body"]` | `'DM Sans', sans-serif` |

**Rule:** Never hardcode hex values in chart modules. Import from `design.js`.

---

## Chart Module Contract

Every chart module exports a create function that returns `{ node, update }`:

```js
// js/charts/example.js
import * as d3 from "npm:d3@7";
import { INK, INK_LIGHT, ACCENT, CONTEXT, RULE } from "../design.js";
import { showTip, moveTip, hideTip } from "../tooltip.js";

export function createExample(data, stats) {
  const W = Math.min(820, (document.body?.clientWidth ?? 820) - 40);
  const H = 300;
  const ml = 50, mr = 24, mt = 18, mb = 44;

  const svg = d3.create("svg")
    .attr("width", "100%")
    .attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif");

  // ... build chart elements ...

  function update(step) {
    // step 0, 1, 2, ... controls progressive reveal
  }

  return { node: svg.node(), update };
}
```

Mount in the markdown article:

```js
import { createExample } from "./js/charts/example.js";
import { mountScrollChart } from "./js/animate.js";

const chart = createExample(data, stats);
display(mountScrollChart(chart.node, chart.update, [
  { prose: "First insight — chart begins animating." },
  { prose: "Second insight — next layer appears." },
  { prose: "Final insight — full picture revealed." },
]));
```

---

## Scroll System (`mountScrollChart`)

### How it works

Wraps the chart in a `<div class="msc-section">`. As the user scrolls, progress
maps to step indices:

- **Start:** section top hits 50% of viewport height → step 0
- **End:** section top reaches 5% of viewport height → last step
- Progress is linear between those points, divided equally among steps

Each step calls `updateFn(stepIndex)`, which the chart uses to show/hide elements.

### Callout positioning

By default, `pickCalloutPosition(chartEl)` scans the SVG for data elements (circles,
rects) and places the callout in the emptier half (top-left or top-right). Bottom
positions are never used (axis labels, legend, source text live there).

**Per-step position overrides** are available for charts where the callout should
point at specific data:

```js
{ prose: "This row specifically.",
  position: { top: "30%", left: "17%", maxWidth: "28ch" } }
```

### When overlay doesn't work

For charts where data spans the full width (horizontal dumbbells, dense scatter),
use `{ callout: "above" }` to place the callout above the chart in normal flow:

```js
display(mountScrollChart(chart.node, chart.update, steps, { callout: "above" }));
```

This was needed for the scenarios chart (DD-001) because dumbbell bars span the
full plot width, leaving no horizontal zone for an overlay callout.

### SVG-native scroll annotations

For scroll annotation patterns, use `/observable-scroll-annotations` — it documents
the `svgStepAnnot` bottom-strip pattern from `design.js`, responsive positioning,
and Safari `foreignObject` workarounds. All DD-001 charts now use this SVG-native
pattern instead of CSS overlay callouts.

---

## Animation Patterns

### Line reveal (stroke-dasharray)

```js
path.attr("stroke-dasharray", "0,99999")  // hidden
  .transition().duration(1050).ease(d3.easeLinear)
  .attrTween("stroke-dasharray", function() {
    const l = this.getTotalLength();
    return d3.interpolate(`0,${l}`, `${l},${l}`);
  });
```

Used by: capex-history, revenue-ratio, revenue-gap.

### Bar grow (clip-path)

```js
const clip = svg.append("clipPath").append("rect")
  .attr("y", H - mb).attr("height", 0);  // starts collapsed

clip.transition().duration(600).ease(d3.easeQuadOut)
  .attr("y", mt).attr("height", H - mt - mb);  // grows upward
```

Used by: stacked-capex, off-balance, guidance.

### Dot spring bounce

```js
dot.attr("r", 0)
  .transition().duration(280).ease(d3.easeBackOut.overshoot(1.4))
  .attr("r", DOT_R);
```

Used by: scenarios (dumbbell dots).

### Opacity fade

```js
element.attr("opacity", 0)
  .transition().delay(200).duration(300)
  .attr("opacity", 1);
```

Used everywhere for labels, gap bands, secondary elements.

### Dim/highlight pattern

Most multi-series charts use this for focus:

```js
function update(step) {
  series.forEach((s, i) => {
    if (i === activeIdx) {
      s.path.attr("opacity", 1).attr("stroke-width", 2.8);
    } else {
      s.path.attr("opacity", 0.15).attr("stroke-width", 1.5);
    }
  });
}
```

Used by: revenue-ratio, stacked-capex.

---

## Tooltip Pattern

All charts share a singleton tooltip from `tooltip.js`. Usage:

```js
import { showTip, moveTip, hideTip } from "../tooltip.js";

// Visible element (small circle)
g.append("circle").attr("r", 3.5).attr("fill", color);

// Invisible hit target (larger radius for easy hover)
g.append("circle").attr("r", 12).attr("fill", "transparent")
  .style("cursor", "crosshair")
  .on("mouseover", (e) => {
    visibleCircle.attr("r", 5);  // grow on hover
    showTip(e, "Bold Label", "Detail line 1", "Detail line 2");
  })
  .on("mousemove", moveTip)
  .on("mouseout", () => {
    visibleCircle.attr("r", 3.5);  // reset
    hideTip();
  });
```

**Always** use a transparent hit-target circle (r=12) around small data marks.
Hovering a 3px dot is frustrating without it.

---

## DD-001 Chart Map

| # | Marimo cell | Observable module | Chart type | Steps | Callout |
|---|-------------|-------------------|------------|-------|---------|
| 1 | `_fig_mktcap` | `valuation.js` | Horizontal bars (scrollytelling) | 7 (custom sync) | N/A (sticky) |
| 2 | `_fig_capex_ratio` | `capex-history.js` | Line chart (2015–2025) | 4 | overlay |
| 3 | `_fig_capex` | `stacked-capex.js` | Stacked bars by company | 4 | overlay |
| 4 | `_fig_obs` | `off-balance.js` | Grouped bars (reported + hidden) | 3 | overlay |
| 5 | `_fig_ratio_slope` | `revenue-ratio.js` | Multi-line ratio chart | 4 | overlay |
| 6 | `_fig_rev` | `revenue-gap.js` | Dual-series (solid + dashed) | 3 | overlay |
| 7 | `_fig_guidance` | `guidance.js` | Bars + dot/whisker | 3 | overlay |
| 8 | `_fig_scenarios` | `scenarios.js` | Horizontal dumbbell | 5 | **above** |
| 9 | `_fig_rt` | `demand-thesis.js` | Card grid + flow diagram | scroll-expand | N/A |

### DD-001/02 Conversion Reality (dd001-conversion.md)

| # | Marimo cell | Observable module | Chart type | Steps | Callout |
|---|-------------|-------------------|------------|-------|---------|
| 10 | `fig_decomp` | `capex-decomp.js` | Horizontal bars (lifetime) | 4 | overlay |
| 11 | `fig_constraints` | `constraint-phases.js` | Horizontal Gantt | 3 | overlay |
| 12 | `_fig_queue` | `queue-growth.js` | Stacked bars (GW) | 3 | overlay |
| 13 | `fig_rainier` | `rainier-progress.js` | Progress bar + timeline | 3 | **above** |

### DD-001/03 Risk and Durability (dd001-risk.md)

| # | Marimo cell | Observable module | Chart type | Steps | Callout |
|---|-------------|-------------------|------------|-------|---------|
| 14 | `_fig_matrix` | `thesis-matrix.js` | 2x2 quadrant | 4 | overlay |
| 15 | `fig_risk` | `risk-timeline.js` | Horizontal Gantt | 5 | **above** |
| 16 | `fig_spv` | `spv-chain.js` | Flow diagram (nodes + edges) | 4 | overlay |

### Special patterns

**Chart 1 (valuation):** Does NOT use `mountScrollChart`. Uses a custom sticky layout
with HTML prose steps (`<div class="scroll-step" data-company="NVDA">`) and
`IntersectionObserver` to sync scroll position to chart state. This is because the
prose is long-form (one paragraph per company) and lives in the markdown, not in a
JS array.

**Chart 9 (demand-thesis):** Does NOT use `mountScrollChart`. Uses `animateOnEntry`
for the flow paths, and a custom scroll-expand pattern for the 6 cards. Cards
expand when closest to viewport center. Returns a `<div>` wrapper, not a bare SVG node.

---

## Step Design Principles

1. **Start simple, add complexity.** Step 0 shows the least; final step shows everything.
2. **Each step should correspond to one sentence** in the callout prose.
3. **3–5 steps is the sweet spot.** Fewer feels static; more forces too-rapid scrolling.
4. **Dim, don't hide.** When highlighting one series, dim others to opacity 0.15–0.3
   rather than removing them. Context matters.
5. **Labels appear last.** Animate shapes first, then data labels, then annotations.
6. **Prose drives the step count.** Write the narrative first, then design the reveal
   sequence to match. Not the other way around.

---

## Conversion Checklist

When converting a Marimo chart to Observable:

- [ ] Read the Marimo cell — understand what data it uses and what story it tells
- [ ] Identify the chart type and which D3 pattern fits (line, bar, scatter, etc.)
- [ ] Create `js/charts/xxx.js` importing from `design.js` and `tooltip.js`
- [ ] Port the data transformations (pandas → JS array ops)
- [ ] Build the SVG with responsive width: `Math.min(820, clientWidth - 40)`
- [ ] Add hover tooltips with invisible hit-target circles
- [ ] Design the step sequence: what reveals at each scroll position?
- [ ] Write the `update(step)` function controlling the progressive reveal
- [ ] Write the prose array (one object per step, `{ prose: "..." }`)
- [ ] Add source text at the bottom of the SVG
- [ ] Mount via `mountScrollChart()` in the article markdown
- [ ] Decide callout mode: overlay (default) or `{ callout: "above" }` if chart is too dense
- [ ] Screenshot and verify: callout doesn't overlap data, all steps fire while chart visible
- [ ] After taking cross-viewport screenshots with `review_charts.cjs`, run the
  `tzd-labs:swd-reviewer` agent on the screenshots to check SWD compliance
  (gray+accent strategy, declutter, direct labeling, insight-driven titles)

---

## Legend Placement

- **Bottom of chart:** Default for bar charts with space below x-axis labels.
  Position at `y = H - mb + 30` (below axis, above source text).
- **Top-right of chart:** Use when the callout is positioned top-left and the chart
  has sparse upper-right area. Position at `y = mt + 4`, right-aligned.
  Used by: revenue-gap.
- **Inside chart area:** Avoid. Competes with data.

---

## Source Text

Every chart includes a source line at the bottom:

```js
svg.append("text")
  .attr("x", ml).attr("y", H - 3)
  .attr("fill", CONTEXT).attr("font-size", "9")
  .text("Source: SEC 10-K/10-Q filings via yfinance");
```

This replaces Marimo's `add_source(fig, "Source: ...")` call.

---

## File Structure

```
observable/src/
├── dd001.md                 ← DD-001/01 Markets & Money
├── dd001-conversion.md      ← DD-001/02 Conversion Reality
├── dd001-risk.md            ← DD-001/03 Risk & Durability
├── index.md                 ← homepage with article cards
├── style.css                ← design system CSS
├── data/
│   ├── stats.json.py        ← Python data loader (same SQL as Marimo)
│   ├── capex.json.py
│   ├── mktcap.json.py
│   ├── cloud_rev.json.py
│   ├── dd001_conversion_stats.json.py  ← conversion article stats
│   ├── dd001_risk_stats.json.py        ← risk article stats
│   └── deep_dives.json.py
└── js/
    ├── design.js            ← color tokens, company helpers, semantic colors
    ├── tooltip.js           ← shared hover tooltip singleton
    ├── animate.js           ← mountScrollChart + animateOnEntry
    ├── utils.js             ← dateToQ, qNum helpers
    └── charts/
        ├── valuation.js     ← custom sticky scrollytelling
        ├── capex-history.js
        ├── stacked-capex.js
        ├── off-balance.js
        ├── revenue-ratio.js
        ├── revenue-gap.js
        ├── guidance.js
        ├── scenarios.js
        ├── demand-thesis.js ← custom scroll-expand cards
        ├── capex-decomp.js  ← construction vs equipment lifetime
        ├── constraint-phases.js ← physical bottleneck Gantt
        ├── queue-growth.js  ← interconnection queue stacked bars
        ├── rainier-progress.js  ← Project Rainier progress + timeline
        ├── thesis-matrix.js ← 2x2 asset lifetime vs demand visibility
        ├── risk-timeline.js ← who holds risk, for how long
        └── spv-chain.js     ← Beignet SPV flow diagram
```
