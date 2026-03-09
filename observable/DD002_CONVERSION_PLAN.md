# DD-002 Conversion Plan: AI Capital and Grid Modernization

**Observable Framework Interactive Article**

---

## 1. Narrative Arc

### Source Structure (Marimo)

Three separate notebooks with distinct questions:

| Notebook | Question | Charts |
| :--- | :--- | :--- |
| `01_whats_getting_built.py` | What generation capacity is AI demand driving? Clean or dirty? | 8 charts + 2 maps |
| `02_who_benefits.py` | Does AI grid investment modernize infrastructure for everyone? | 7 charts + 2 maps + Monte Carlo + interactive sliders |
| `03_feedback_architecture.py` | Does the system tip toward shared or private infrastructure? | 3 charts (CLD, baseline simulation, sensitivity heatmap) + interactive sliders |

### Target Structure (Observable)

One long-form scrollable article: `dd002.md`

**Opening hook:** The fundamental mismatch. AI demand forecasts span 3 years. The infrastructure those forecasts are buying lasts 25-50 years. Every capital decision being made today creates a 40-year infrastructure consequence from a 3-year demand thesis. That is the entire article in one frame.

**Throughline:** COMMIT (what capital goes in) -> CONVERT (what physical infrastructure it becomes) -> LAND (where it lands, who pays) -> DISTRIBUTE (who benefits or bears the cost, what feedback loops determine the outcome).

**Section flow:**

```
1. THE MISMATCH (hook)
   - Asset timeline chart (horizontal bars: AI forecast vs infrastructure life)

2. WHAT'S GETTING BUILT
   - Generation mix stacked bar (fuel types since 2020)
   - Capacity factor comparison (nameplate vs energy-equivalent)
   - Generation spectrum scatter (grid benefit vs asset life)
   - Plant map (where renewables and gas are being built)
   - Data center map (where frontier AI facilities are landing)
   - Energy prices (gas + electricity PPI)
   - Hyperscaler PPAs (contracted renewable capacity)

3. THE BOTTLENECK
   - Queue size callout cards (2,600 GW, 5+ years, 21% completion)
   - Queue funnel visualization (NEW: animated funnel)
   - ISO queue map (choropleth + bubble overlay)
   - Queue composition stacked bar (clean energy dominates)
   - Queue-to-service lag proxy (company-region exposure)

4. WHO PAYS
   - Cost allocation waterfall ($4.36B socialized)
   - Virginia bill impact projection (line + fill)
   - Monte Carlo fan chart (probabilistic cost forecast)
   - Three spillover scenarios (narrative cards)

5. THE FEEDBACK ARCHITECTURE
   - Causal loop diagram (interactive force-directed graph)
   - Baseline simulation (4-panel time-series)
   - Sensitivity heatmap (BTM cost vs regulatory favorability)
   - Interactive scenario explorer (sliders + live chart)

6. SOURCES & METHODOLOGY
```

---

## 2. Chart-by-Chart Conversion Map

### Chart 1: Asset Timeline (Horizontal Bars)

**Marimo cell:** `_fig_timeline` in `01_whats_getting_built.py`
**What it currently shows:** Horizontal bar chart showing asset lifetimes (3-50 years) with a shaded band for the AI forecast horizon (2024-2027).

**Observable chart type:** Horizontal bars with scroll-driven progressive reveal. Opening chart establishing the central tension.

**Scroll steps (4):**
1. "AI demand forecasts span about 3 years. That is the dark band."
2. "Battery storage and gas peakers last 25 years. Solar and wind: 30."
3. "Nuclear restarts and transmission lines: 50 years."
4. "Every bar to the right of the dark band is an infrastructure commitment that outlasts the forecast that funded it."

**Animation:** Bars grow from left (the 2024 anchor) on entry. The AI forecast band pulses briefly on step 1.

**Module:** `js/charts/asset-timeline.js`

---

### Chart 2: Generation Mix (Stacked Bars)

**Marimo cell:** `fig_mix` in `01_whats_getting_built.py`
**What it currently shows:** Stacked bar chart of new U.S. generation capacity by fuel type, 2018-2024. IRA annotation at 2022.

**Observable chart type:** Stacked bars with scroll-driven fuel highlighting.

**Scroll steps (4):**
1. "Since 2020, the U.S. has added over 200 GW of new generation capacity."
2. "Solar dominates. It is the largest single source of new capacity."
3. "Battery storage is the fastest-growing category."
4. "Gas combined cycle remains significant but is a shrinking share."

**Module:** `js/charts/gen-mix.js`

---

### Chart 3: Capacity Factor Comparison -- UPGRADE to Cleveland Dot Plot

**Marimo cell:** `fig_capfactor` in `01_whats_getting_built.py`
**Current:** Grouped bar chart comparing nameplate vs energy-equivalent capacity by fuel type.
**Observable:** Cleveland dot plot (dumbbell chart). Two dots per fuel connected by a line. The line length IS the story (how much nameplate overstates contribution).

**Scroll steps (3):**
1. "Nameplate capacity tells you what is installed. It does not tell you how much energy it actually produces."
2. "Solar leads in nameplate. But when adjusted for capacity factor, gas CC closes the gap."
3. "The line between each pair of dots is the overstatement."

**Module:** `js/charts/capacity-gap.js`
**Pattern:** Reuse DD-001's `scenarios.js` dumbbell pattern. Use `{ callout: "above" }`.

---

### Chart 4: Generation Spectrum (Bubble Scatter)

**Marimo cell:** `fig_spectrum` in `01_whats_getting_built.py`
**Current:** Bubble scatter: x = asset lifetime, y = grid benefit, bubble size = capacity, color by technology. Quadrant labels.
**Observable:** Interactive bubble scatter with quadrant annotations. Hover reveals tech details.

**Scroll steps (4):**
1. "Not all AI-driven generation creates equal value."
2. "Gas peakers behind-the-meter: bottom-left. Short-lived, private, no spillover."
3. "Solar+storage PPAs and nuclear restarts: upper-right. Long-lived, high grid benefit."
4. "The green zone is where policy should steer AI capital."

**Module:** `js/charts/gen-spectrum.js`

---

### Charts 5+6: Plant Map + Data Center Map -- COMBINE INTO ONE

**Marimo cells:** `fig_plant_map` and `fig_dc_map` in `01_whats_getting_built.py`
**Observable:** Single D3-geo map with toggleable layers via scroll steps.

**Scroll steps (4):**
1. "Every circle is a power plant that came online since 2020."
2. "Solar concentrates in the Sun Belt. Wind follows the Great Plains."
3. "Now overlay frontier AI data centers." (stars appear)
4. "The overlap is the geographic story."

**Module:** `js/charts/plant-map.js`

**D3 pattern:** `d3-geo` with `geoAlbersUsa()`, TopoJSON from `npm:us-atlas@3/states-10m.json`.

---

### Chart 7: Energy Prices -- REPLACE Dual-Axis with Small Multiples

**Marimo cell:** `fig_gas` in `01_whats_getting_built.py`
**Current:** Dual-axis line chart (gas price + electricity PPI). SWD anti-pattern.
**Observable:** Small multiples (2 vertically stacked panels) sharing an x-axis.

**Module:** `js/charts/energy-prices.js`

---

### Chart 8: Hyperscaler PPAs (Horizontal Bars)

**Marimo cell:** `fig_ppa` in `01_whats_getting_built.py`
**Observable:** Horizontal bars with SWD gray+accent pattern. Keep as-is.

**Module:** `js/charts/hyperscaler-ppa.js`

---

### Chart 9: Queue Size Callout Cards

**Marimo source:** `mo.hstack` of three `mo.callout` widgets in `02_who_benefits.py`
**Observable:** Animated counter cards. Three large numbers counting up from zero on viewport entry.

**Module:** `js/charts/queue-counters.js`

---

### Chart 10: Queue by Region (Horizontal Bars)

**Marimo cell:** `fig_queue` in `02_who_benefits.py`
**Observable:** Horizontal bars with highlight pattern. PJM highlighted.

**Module:** `js/charts/queue-region.js`

---

### Chart 11: ISO Queue Map -- SHOWCASE MAP

**Marimo cell:** `fig_map` in `02_who_benefits.py`
**Current:** US choropleth by ISO/RTO territory, sqrt-scaled bubbles.
**Observable:** D3-geo choropleth + bubbles. Click an ISO region to zoom into detail panel with queue composition.

**Scroll steps (4):**
1. "Each color is one grid operator's territory."
2. "The bubbles show how much generation is waiting to connect. PJM: 520 GW."
3. "Northern Virginia's Loudoun County is the epicenter."
4. "Click any region to see its queue composition."

**Module:** `js/charts/iso-queue-map.js`

---

### Chart 12: Queue Composition (Stacked Bars or Area)

**Marimo cell:** `fig_comp` in `02_who_benefits.py`
**Observable:** Stacked bars or stacked area. Clean energy dominance story.

**Module:** `js/charts/queue-composition.js`

---

### Chart 13: Cost Allocation Waterfall

**Marimo cell:** `fig_cost` in `02_who_benefits.py`
**Observable:** Waterfall chart. Bars build up sequentially. $4.36B cumulative.

**Module:** `js/charts/cost-waterfall.js`

---

### Chart 14: Virginia Bill Impact (Line + Fill)

**Marimo cell:** `fig_virginia` in `02_who_benefits.py`
**Observable:** Line chart with area fill. Bill projection through 2040.

**Module:** `js/charts/virginia-bills.js`

---

### Chart 15: Queue-to-Service Lag Proxy

**Marimo cell:** `fig_lag` in `02_who_benefits.py`
**Observable:** Horizontal bars with highlight pattern.

**Module:** `js/charts/capex-lag.js`

---

### Chart 16: Causal Loop Diagram -- NOVEL: Interactive Force-Directed Graph

**Marimo cell:** `fig_cld` in `03_feedback_architecture.py`
**Current:** Static matplotlib CLD with 11 nodes, colored edges for 5 loops.
**Observable:** Interactive force-directed graph. Nodes draggable. Click loop label to isolate that loop's edges.

**Scroll steps (5):**
1. "Five feedback loops determine whether AI capital modernizes the grid or bypasses it."
2. "R1 (blue): Grid Investment Cycle." (R1 highlighted)
3. "R2 (green): Renewable Learning." (R2 highlighted)
4. "B2 (red): BTM Bypass." (B2 highlighted)
5. "The critical variable is Regulatory Environment." (node pulses)

**Design decision:** Use fixed initial positions from matplotlib layout with moderate force anchoring (strength 0.3). Preserves designed layout while enabling drag exploration.

**Module:** `js/charts/cld-graph.js`

---

### Chart 17: Baseline Simulation (4-Panel Time-Series)

**Marimo cell:** `fig_baseline` in `03_feedback_architecture.py`
**Observable:** Small multiples (2x2). Lines draw via stroke-dasharray.

**Module:** `js/charts/baseline-sim.js`

---

### Chart 18: Sensitivity Heatmap -- Interactive with Draggable Marker

**Marimo cell:** `fig_sensitivity` in `03_feedback_architecture.py`
**Current:** Static contour heatmap.
**Observable:** Interactive heatmap. Hover shows crosshair + exact spillover index. Draggable "current estimate" marker.

**Module:** `js/charts/sensitivity-heatmap.js`

---

### Chart 19: Interactive Scenario Explorer

**Marimo source:** Sliders + reactive chart in `03_feedback_architecture.py`
**Observable:** HTML sliders (Observable `Inputs.range()`) + reactive D3 chart. PySD model (5 stocks, ~20 params) ported to JavaScript for client-side simulation. No Python round-trip.

**Module:** `js/charts/scenario-explorer.js`

---

## 3. Novel Visualizations to ADD

### NEW-1: Sankey Diagram -- Capital Flow from Tech to Grid

Left nodes: Amazon, Alphabet, Microsoft, Meta, xAI. Middle: Grid connection, Behind-the-meter, Renewable PPA. Right: Shared grid benefit, Private infrastructure, Ratepayer cost. Width = dollar magnitude.

**Module:** `js/charts/capital-sankey.js`

### NEW-2: Spillover Scenario Cards

Three scenarios (Pure Spillover, Captured Benefit, Cost Shifting) as interactive cards linked to sensitivity heatmap regions.

**Module:** `js/charts/spillover-scenarios.js`

### NEW-3: Queue Funnel (Animated)

Data-driven animated funnel: 2,600 GW enters, 21% emerges. Particles flow through stages.

**Module:** `js/charts/queue-funnel.js`

---

## 4. Data Loader Requirements

| Loader | Content |
|:-------|:--------|
| `dd002_stats.json.py` | Combined stats from all three notebooks |
| `dd002_eia.json.py` | EIA Form 860 generation data |
| `dd002_queue.json.py` | Queue data (region, composition, lag) |
| `dd002_prices.json.py` | FRED energy price series |
| `dd002_simulation.json.py` | Pre-computed PySD results (baseline + sensitivity sweep) |
| `us_states.json.py` | TopoJSON state boundaries |
| `dd002_datacenters.json.py` | Frontier AI data center locations |

---

## 5. Module Structure

```
observable/src/
  dd002.md
  data/
    dd002_stats.json.py
    dd002_eia.json.py
    dd002_queue.json.py
    dd002_prices.json.py
    dd002_simulation.json.py
    dd002_datacenters.json.py
    us_states.json.py
  js/
    charts/
      asset-timeline.js       # Chart 1
      gen-mix.js              # Chart 2
      capacity-gap.js         # Chart 3 (Cleveland dot plot)
      gen-spectrum.js         # Chart 4
      plant-map.js            # Charts 5+6 (combined)
      energy-prices.js        # Chart 7 (small multiples)
      hyperscaler-ppa.js      # Chart 8
      queue-counters.js       # Chart 9 (animated counters)
      queue-region.js         # Chart 10
      iso-queue-map.js        # Chart 11 (showcase map)
      queue-composition.js    # Chart 12
      cost-waterfall.js       # Chart 13
      virginia-bills.js       # Chart 14
      capex-lag.js            # Chart 15
      cld-graph.js            # Chart 16 (force-directed CLD)
      baseline-sim.js         # Chart 17
      sensitivity-heatmap.js  # Chart 18 (draggable marker)
      scenario-explorer.js    # Chart 19 (JS simulation)
      capital-sankey.js       # NEW-1
      spillover-scenarios.js  # NEW-2
```

### Design token additions (`js/design.js`)

```js
export const FUEL = {
  solar: "#D4943A", wind: "#4477AA", battery: "#55BBCC",
  gas_cc: "#CC6677", gas_ct: "#BB4444", nuclear: "#AA3377",
  hydro: "#228833", coal: "#999999",
};

export const ISO_COLOR = {
  PJM: "#4477AA", MISO: "#66CCEE", ERCOT: "#228833",
  CAISO: "#CCBB44", SPP: "#EE6677", NYISO: "#AA3377",
  "ISO-NE": "#BBBBBB",
};

export const LOOP = {
  R1: "#4477AA", R2: "#228833", B1: "#CCBB44",
  B2: "#CC3311", B3: "#AA3377",
};
```

---

## 6. Implementation Priority

### Phase 1: Foundation
1. Data loaders: `dd002_stats`, `dd002_eia`, `us_states`
2. Design tokens: FUEL, ISO_COLOR, LOOP
3. Article skeleton: `dd002.md`
4. Chart 1 (`asset-timeline.js`) -- opening hook
5. Chart 2 (`gen-mix.js`) -- first stacked bar
6. Charts 5+6 (`plant-map.js`) -- first D3-geo map

### Phase 2: Queue Story
7. `dd002_queue.json.py`
8. Chart 9 (`queue-counters.js`)
9-12. Queue charts

### Phase 3: Who Pays
13-16. Cost waterfall, Virginia bills, energy prices, lag proxy

### Phase 4: Feedback Architecture (most complex)
17. `dd002_simulation.json.py`
18. Chart 16 (`cld-graph.js`) -- force-directed CLD
19-21. Baseline sim, sensitivity heatmap, scenario explorer

### Phase 5: Novel Additions
22-24. Sankey, spillover cards, capacity gap, spectrum, PPAs

---

## 7. Complexity Estimates

| Module | Complexity |
| :--- | :--- |
| `asset-timeline.js` | Low |
| `gen-mix.js` | Low |
| `capacity-gap.js` | Low |
| `gen-spectrum.js` | Medium |
| `plant-map.js` | **High** |
| `energy-prices.js` | Medium |
| `iso-queue-map.js` | **High** |
| `cost-waterfall.js` | Medium |
| `cld-graph.js` | **Very High** |
| `sensitivity-heatmap.js` | **High** |
| `scenario-explorer.js` | **High** |
| `capital-sankey.js` | Medium |

**Total chart modules:** 21 (vs 9 for DD-001)
**Highest-risk:** `cld-graph.js`, `iso-queue-map.js`, `scenario-explorer.js`

---

## 8. Key Design Decisions

- **Combined vs separate maps:** 4 notebook maps consolidated to 2 Observable maps
- **Dual-axis elimination:** Energy prices becomes small multiples (SWD compliance)
- **Grouped bars to Cleveland dot plot:** Gap between dots = the overstatement
- **Interactive simulation in browser:** PySD ported to JS (5 stocks, ~20 params)
- **CLD layout:** Force-directed with fixed initial positions + moderate anchoring

---

## 9. Research References

- [Force-directed graph / D3 | Observable](https://observablehq.com/@d3/force-directed-graph/2)
- [U.S. Map / D3 | Observable](https://observablehq.com/@d3/u-s-map)
- [Choropleth / D3 | Observable](https://observablehq.com/@d3/choropleth/2)
- [Sankey | D3 Graph Gallery](https://d3-graph-gallery.com/sankey.html)
- [Cleveland dot plot | D3 Graph Gallery](https://d3-graph-gallery.com/graph/lollipop_cleveland.html)
- [Heatmap | D3 Graph Gallery](https://d3-graph-gallery.com/heatmap)
- [Waterfall chart (GitHub Gist)](https://gist.github.com/rprioul/f9b34dac50e19330115a9508d4c91931)
- [How to implement scrollytelling (Pudding)](https://pudding.cool/process/how-to-implement-scrollytelling/)
- [d3-geo documentation](https://d3js.org/d3-geo)
- [topojson/us-atlas](https://github.com/topojson/us-atlas)
