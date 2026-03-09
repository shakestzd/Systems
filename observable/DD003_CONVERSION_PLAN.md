# DD-003 Conversion Plan: AI Capital and the Labor Market

**Observable Framework Interactive Article**

---

## 1. Narrative Arc

### The Core Tension

The AI-and-jobs debate lives in software. The AI-and-capital story lives in concrete, copper, and conduit. DD-003's job is to make the reader feel this gap viscerally.

### Opening Hook

The first thing the reader sees is not a chart about data scientists or software developers. Instead, the opening scrollytelling sequence asks: **"Who actually builds the AI economy?"** and reveals occupation by occupation that the single largest employment category created by AI capital is not software engineering -- it is construction trades. Electricians, specifically.

### Narrative Structure (5 acts)

| Act | Section | Core Question |
|-----|---------|---------------|
| 1 | **The Reveal** | Who actually gets hired when AI capital lands? |
| 2 | **Two Labor Markets** | How fast is each growing, and from what base? |
| 3 | **The Wage Signal** | What are wages telling us about supply and demand? |
| 4 | **Where It Lands** | Which counties absorb this demand? |
| 5 | **The Feedback Loop** | How does labor constraint feed back into capital deployment? |

### Scroll-Driven Storytelling Strategy

- **Act 1:** Custom sticky scrollytelling (like DD-001's `valuation.js`) -- force-directed unit chart morphing across scroll steps
- **Acts 2-4:** Standard `mountScrollChart()` for the three data charts
- **Act 5:** Closing flow diagram (like DD-001's `demand-thesis.js` cards) showing the feedback loop

---

## 2. Chart-by-Chart Conversion Map

### Chart 1: Employment Index (Line Chart)

**Marimo cell:** `_fig_empl` / `dd003_employment_index.png`
**Current:** Multi-line time series, 4 sectors indexed to Jan 2020 = 100.
**Observable:** Multi-line with scroll-driven dim/highlight.

**Scroll steps (4):**
1. "Four sectors, indexed to January 2020. Same starting point."
2. "Then ChatGPT launched. AI capex surged. Watch what happens next."
3. "Computer Systems Design: +{tech_change}% since 2020."
4. "Construction: +{const_change}%. Aggregate hides the signal."

**Module:** `js/charts/employment-index.js`
**Pattern:** Same as DD-001's `revenue-ratio.js` -- multi-line with dim/highlight per step.

---

### Chart 2: OEWS Wage Trajectories -- UPGRADE to Slope Chart

**Marimo cell:** `_fig_wages` / `dd003_oews_wages.png`
**Current:** Spaghetti line chart with 15+ occupations, 6 data points each.
**Observable:** **Slope chart.** 2019 on left, 2024 on right, connecting lines. Cleaner than spaghetti for sparse time points.

**Why slope chart:** Makes the absolute wage gap AND the growth rate simultaneously visible. Software Developers ($105K to $132K) vs Electricians ($60K to $73K) -- the vertical space is the gap, the angle is the growth rate.

**Scroll steps (4):**
1. "15 occupations in the AI labor stack. Every one saw wages rise."
2. "Software Developers: $105K to $132K. The headline occupation."
3. "Electricians: $60K to $73K. Not in the debate. Should be."
4. "The gap: a software developer earns roughly 2x an electrician."

**Module:** `js/charts/wage-slopes.js`

---

### Chart 3: QCEW State Employment -- UPGRADE to US Map

**Marimo cell:** `_fig_qcew` / `dd003_qcew_dc_states.png`
**Current:** Horizontal bar chart, top 15 states by NAICS 518210 employment.
**Observable:** **US state choropleth + data center bubble overlay.** Uses existing `data/external/data_center_locations.csv` (64 records with lat/lon).

**Why map:** Bar chart obscures geography. The entire story is about WHERE labor demand concentrates. A map makes the geographic concentration visceral.

**Scroll steps (5):**
1. "The data center industry employs hundreds of thousands. Where?"
2. "Five states absorb the majority." (choropleth fills in)
3. "64 hyperscaler campuses." (bubbles appear, colored by operator)
4. "Loudoun County, Virginia. Data Center Alley." (zoom/highlight)
5. "{top_state} leads with {top_count} workers."

**Module:** `js/charts/dc-map.js`
**Pattern:** `d3-geo` with `geoAlbersUsa()`, TopoJSON, operator colors via `cc(ticker)`.

---

### NEW Chart 4: The Reveal (Workforce Unit Chart) -- OPENING HOOK

**Not in Marimo.** Force-directed unit chart inspired by The Pudding. Each dot = ~1,000 workers.

**Scroll steps (6):**
1. Small cluster of blue dots: ~150 dots (Software Developers, ~150K employed)
2. Add Data Scientists: ~50 dots
3. Add ML Engineers, Network Admins, DB Architects: full tech stack ~300 dots
4. **Pause. All tech dots dim. A much larger swarm of accent-colored dots begins flowing in.**
5. Full construction trades: Electricians, Laborers, Plumbers, HVAC. **500+ accent dots.**
6. Both groups visible. "One capital flow. Two labor markets."

**Module:** `js/charts/workforce-reveal.js`
**Pattern:** Custom sticky scrollytelling. `d3.forceSimulation` with `forceX`/`forceY` targets that change per step. Cap at ~1000 dots for performance. Freeze simulation after convergence.

---

### NEW Chart 5: The Feedback Loop (Flow Diagram)

**Not in Marimo.** Closing visualization for Act 5.

```
AI Capex --> Data Center Construction --> Electrician Demand
    ^                                          |
    |                                          v
    +--- Deployment Lag <--- Electrician Shortage
```

**Scroll steps (4):**
1. "AI capital flows into data center construction."
2. "Every data center requires 300-600 electricians for 24-36 months."
3. "The pipeline is constrained. Apprenticeship takes 4-5 years."
4. "The loop closes. Labor constraints slow buildout."

**Module:** `js/charts/labor-feedback.js`

---

## 3. Novel Visualizations Assessment

### Recommended (implement)

| Viz | Type | Why | Complexity |
|-----|------|-----|------------|
| **Workforce Reveal** | Force-directed unit chart | Opening hook; makes tech-vs-trades gap visceral | High |
| **US Map** | Choropleth + bubbles | Geographic story is core; uses existing data | Medium-high |
| **Slope Chart** | Connected slopes | Cleaner than spaghetti for 6-year wage data | Medium |
| **Feedback Loop** | Animated flow diagram | Closes article; connects to DD-002 | Medium |

### Deferred

| Viz | Why deferred |
|-----|-------------|
| **3D Wage Topography** | Gratuitous; adds WebGL dependency for one chart |
| **Labor Flow Sankey** | Intermediate quantities are estimated, not measured |
| **Occupation Adjacency Network** | No BLS data for skill adjacency |
| **WebGL Particle System** | Doesn't encode measured data |
| **Animated Migration Arcs** | No public occupation-level migration data |

---

## 4. Data Loader Requirements

| Loader | Content |
|:-------|:--------|
| `dd003_stats.json.py` | Computed stats for prose interpolation |
| `dd003_employment.json.py` | FRED employment series, indexed to Jan 2020 |
| `dd003_wages.json.py` | OEWS wage data, 15 SOC codes, 2019-2024 |
| `dd003_qcew_states.json.py` | NAICS 518210 state employment |
| `dd003_dc_locations.json.py` | Data center lat/lon from CSV |
| `us_states.json.py` | TopoJSON state boundaries |

---

## 5. Module Structure

```
observable/src/
  dd003.md
  data/
    dd003_stats.json.py
    dd003_employment.json.py
    dd003_wages.json.py
    dd003_qcew_states.json.py
    dd003_dc_locations.json.py
    us_states.json.py
  js/
    charts/
      workforce-reveal.js      # NEW: force-directed unit chart (opening)
      employment-index.js      # CONVERTED: multi-line time series
      wage-slopes.js           # NEW: slope chart (occupational wages)
      dc-map.js                # NEW: choropleth + bubble map
      labor-feedback.js        # NEW: causal loop flow diagram
```

### Design token additions (`js/design.js`)

```js
export const OCC_TECH = "#4477AA";   // muted blue
export const OCC_TRADES = ACCENT;    // "#b84c2a"
```

---

## 6. Article Structure (`dd003.md`)

```
---
title: "AI Capital and the Labor Market"
---

[Data loads]
<byline>

# AI Capital and the Labor Market
Opening: The AI jobs debate asks whether software will displace workers.
That is not where the signal is clearest.

## Who Gets Hired (Act 1)
[mount workforce-reveal.js -- sticky scrollytelling, 6 steps]

## Two Labor Markets, One Capital Flow (Act 2)
[mount employment-index.js via mountScrollChart, 4 steps]

## The Wage Signal (Act 3)
[mount wage-slopes.js via mountScrollChart, 4 steps]

## Where It Lands (Act 4)
[mount dc-map.js via mountScrollChart, 5 steps]

## The Feedback Loop (Act 5)
[mount labor-feedback.js]

## Sources & Methodology
```

---

## 7. Implementation Sequence

| Order | Task | Complexity |
|-------|------|-----------|
| 1 | Create all 6 data loaders | Medium |
| 2 | Add OCC_TECH/OCC_TRADES to design.js | Low |
| 3 | `employment-index.js` | Medium (validates pipeline) |
| 4 | `wage-slopes.js` | Medium (novel chart type) |
| 5 | `dc-map.js` | High (map) |
| 6 | `workforce-reveal.js` | High (most complex, force layout) |
| 7 | `labor-feedback.js` | Medium |
| 8 | Write `dd003.md` article | Medium |
| 9 | Config + CSS updates | Low |
| 10 | Screenshot and verify | Medium |

---

## 8. Key Implementation Patterns

### Slope chart

```js
// Two columns: xLeft (2019), xRight (2024)
// y = d3.scaleLinear for wage ($0 to maxWage)
// Each occupation: line from (xLeft, y(wage2019)) to (xRight, y(wage2024))
// Focus: 2.5px stroke, accent/blue. Context: 1.2px, gray at opacity 0.2
// Labels on right after endpoint
```

### Force simulation (workforce reveal)

```js
const sim = d3.forceSimulation(dots)
    .force("x", d3.forceX(d => targetX(d)).strength(0.15))
    .force("y", d3.forceY(d => targetY(d)).strength(0.15))
    .force("collide", d3.forceCollide(DOT_R + 0.5))
    .alphaTarget(0.3);
// targetX/targetY change per scroll step
// Cap at ~1000 dots for performance
// Freeze after convergence: alphaTarget(0) after 200 ticks
```

### Map with bubble overlay

```js
const projection = d3.geoAlbersUsa().fitSize([W, H], states);
// State choropleth: sequential color by employment
// Bubbles: sized by sqrt(MW), colored by cc(ticker)
// Scroll reveal: states first, bubbles at step 2
```

---

## 9. Risks

| Risk | Mitigation |
|------|-----------|
| Force simulation performance | Cap ~1000 dots, forceCollide small radius, freeze after convergence |
| OEWS data download fails | Cache as parquet in data/raw/bls/ |
| SOC 15-1252 renamed in 2021 | Exempt focus codes from completeness filter |
| Slope chart cluttered with 15 occs | Dim/highlight aggressively; reduce to top 8 if needed |
| TopoJSON size | Use states-10m.json (35KB) not counties |

---

## 10. Research References

- [Observable D3 Choropleth](https://observablehq.com/@d3/choropleth)
- [D3 Beeswarm](https://observablehq.com/@d3/beeswarm)
- [D3 Graph Gallery: Choropleth](https://d3-graph-gallery.com/choropleth.html)
- [D3 Graph Gallery: Sankey](https://d3-graph-gallery.com/sankey.html)
- [Pudding: Scrollytelling](https://pudding.cool/process/how-to-implement-scrollytelling/)
- [Pudding: Responsive scrollytelling](https://pudding.cool/process/responsive-scrollytelling/)
- [Visual Capitalist: States by AI Data Center Jobs](https://www.visualcapitalist.com/ranked-states-by-ai-data-center-jobs/)
- [Census: Data Center Employment Growth](https://www.census.gov/library/stories/2025/01/data-centers.html)
- [FlowingData: Animated Transitions](https://flowingdata.com/2013/01/17/how-to-animate-transitions-between-multiple-charts/)
