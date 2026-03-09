# DD-004 Conversion Plan: AI Capital and Who Pays for the Grid

**Observable Framework Interactive Article**

---

## 1. Narrative Arc

### Governing Question
*Through what regulatory mechanisms does AI infrastructure capital convert to ratepayer obligations, and who decides the allocation?*

### Published Title (Proposed)
**"Who Pays for the AI Grid?"**
Subtitle: *Data centers create 30-year infrastructure obligations. The capital that builds them is designed to exit in 7.*

### The Three-Part Story

| Act | Source | Question |
|-----|--------|----------|
| I | Notebook 01 (PE acquisitions) | Who is buying the utilities? |
| II | Notebook 02 (community impact) | Where do data centers land? |
| III | Notebook 03 (cost-liability map) | Who holds the bag? |

### Scroll Progression (geographic zoom)

1. Cold open: The structural mismatch (PE fund lifecycle vs. rate base asset life)
2. US map: Where data centers are actually landing
3. Bimodal scatter: The two Americas of data center siting
4. Capital intensity: What communities actually get (jobs per dollar)
5. Virginia deep dive: Zoom to one state, show the cost geography
6. Indiana case study: The regulatory laboratory
7. PJM demand: The scale of what is coming
8. Liability taxonomy: Who holds the bag for how long
9. Bill calculator: What this means for a residential ratepayer
10. FERC timeline: The regulatory decisions that will determine outcomes

---

## 2. Chart-by-Chart Conversion Map

### Chart 1: US Data Center Siting Map

**Marimo cell:** `fig_us_map`
**Observable:** Interactive D3 bubble map with scroll-driven reveal. `geoAlbersUsa()`, operator-colored bubbles sized by MW.

**Scroll steps (4):**
1. Empty US outline
2. All 64 facilities appear (spring bounce)
3. Dim all except Virginia cluster
4. Highlight distressed-county facilities (poverty > 15%)

**Module:** `js/charts/dc-map.js`
**Pattern:** `mountScrollChart()` with `{ callout: "above" }`

---

### Chart 2: Bimodal Scatter (Income vs. Poverty)

**Marimo cell:** `fig_bimodal`
**Observable:** Quadrant scatter with animated crosshair reveal.

**Scroll steps (4):**
1. All points visible, no crosshairs
2. US median income vertical line appears
3. US median poverty horizontal line. Quadrants visible.
4. Highlight points with poverty > 15% in ACCENT

**Module:** `js/charts/bimodal-scatter.js`

---

### Chart 3: Capital Intensity (Investment per Job)

**Marimo cell:** `fig_capint`
**Observable:** Horizontal bars with progressive reveal. DC at top, 55x annotation vs warehouse.

**Module:** `js/charts/capital-intensity.js`

---

### Chart 4: Virginia County Map

**Marimo cell:** `fig_va_map`
**Observable:** D3 county-level choropleth (STATEFP=51). Three-tier fill: Loudoun (ACCENT), NoVA suburbs, rest of Virginia. Dominion service territory overlay.

**Module:** `js/charts/virginia-map.js`

---

### Chart 5: Indiana Investment

**Marimo cell:** `fig_inv`
**Observable:** Stat cards (not bars). Amazon $11B, Microsoft $3.3B, Total. Below: single bar showing I&M peak load growth.

**Why cards:** Three bars for three data points is thin. Stat cards are more impactful for announcements of this magnitude.

---

### Chart 6: PJM Zone Demand -- UPGRADE to Small Multiples

**Marimo cell:** `fig_pjm` + Altair interactive
**Current:** Side-by-side bars + interactive legend selection.
**Observable:** **Small multiples sparkline grid.** One sparkline per PJM zone. AEP and DOM highlighted in ACCENT. Sort by 2030 demand on step 1.

**Why small multiples:** Provides equivalent comparison to Altair interactive without clicking. Each zone trajectory immediately visible.

**Module:** `js/charts/pjm-demand.js`

---

### Chart 7: Liability Taxonomy (Most important chart)

**Marimo cell:** `fig_liab`
**Observable:** Horizontal timeline bars, ordered shortest to longest. Two vertical reference lines: x=3 (AI forecast horizon) and x=7-10 (PE fund lifecycle).

**Scroll steps (5):**
1. Only hyperscaler-owned assets visible (ACCENT)
2. Ratepayer-owned assets appear (longer bars, CONTEXT)
3. Tax abatements bar appears
4. PE fund lifecycle band appears (x=7-10, shaded)
5. AI forecast horizon line (x=3)

**Module:** `js/charts/liability-taxonomy.js`
**Callout:** `{ callout: "above" }`

---

### Chart 8: Regulatory Timeline (NEW)

**Observable:** Interactive horizontal timeline. Events as circles, sized by significance, colored by jurisdiction (FERC = blue, IURC = ACCENT, PJM = green).

**Module:** `js/charts/regulatory-timeline.js`

---

## 3. Novel Visualizations to ADD

### Novel 1: The Bill Calculator (highest priority)

**What:** Interactive element. Reader adjusts sliders, sees how different cost allocation methods affect residential electricity bill.

**Design:**
- Two side-by-side bill representations
- Left: "Current rules (costs socialized)"
- Right: "Cost-causation (direct-assigned)"
- Slider 1: Data center load % (0-30%, default ~15%)
- Slider 2: Monthly usage (default 900 kWh)
- Real-time difference: "You pay $XX more per year under current rules"
- Disclaimer about simplified illustration

**Reference patterns:** NYT "How Much Hotter Is Your Hometown"; FiveThirtyEight tax calculators.

**Module:** `js/charts/bill-calculator.js`

---

### Novel 2: Ownership Chain Flow Diagram (Act I anchor)

**What:** Animated flow: PE Fund (7yr) --> HoldCo --> Regulated Utility (30-40yr assets) --> Ratepayers (indefinite)

**Scroll steps (4):**
1. PE Fund node only
2. Flow to HoldCo and Utility
3. Flow to Ratepayers
4. Exit arrow; ratepayer connection persists

**Module:** `js/charts/ownership-flow.js`

---

### Novel 3: Community Impact Dashboard (optional)

"Pick a county" dropdown -- updates dashboard: facility count, operator, MW, median income, poverty rate, grid cost share. Include only if time permits.

---

## 4. Data Loader Requirements

| Loader | Content |
|:-------|:--------|
| `dd004_stats.json.py` | Combined stats from all three notebooks |
| `dd004_locations.json.py` | Data center locations + ACS join |
| `dd004_pjm_demand.json.py` | PJM zone demand from CSV |
| `dd004_iurc_cases.json.py` | IURC regulatory cases |
| `dd004_ferc_events.json.py` | FERC/regulatory timeline events |
| `us_states_topo.json.py` | State boundaries TopoJSON |
| `virginia_counties_topo.json.py` | Virginia counties only (~50KB) |

---

## 5. Module Structure

```
observable/src/
  dd004.md
  data/
    dd004_stats.json.py
    dd004_locations.json.py
    dd004_pjm_demand.json.py
    dd004_iurc_cases.json.py
    dd004_ferc_events.json.py
    us_states_topo.json.py
    virginia_counties_topo.json.py
  js/
    charts/
      dc-map.js                # Chart 1: US bubble map
      bimodal-scatter.js       # Chart 2: Income vs poverty
      capital-intensity.js     # Chart 3: $M per job
      virginia-map.js          # Chart 4: County cost geography
      pjm-demand.js            # Chart 6: Small multiples sparklines
      liability-taxonomy.js    # Chart 7: Asset life vs liability
      regulatory-timeline.js   # Chart 8: FERC + IURC timeline
      ownership-flow.js        # Novel 2: PE -> utility -> ratepayer
      bill-calculator.js       # Novel 1: Interactive bill impact
```

### Design token additions (`js/design.js`)

```js
export const RATEPAYER = "#8c8279";   // warm gray
export const PUBLIC    = "#e8c97e";   // warm yellow
export const DOM_ZONE  = "#3a6fa8";   // Dominion Virginia
export const AEP_ZONE  = ACCENT;     // AEP Indiana
```

---

## 6. Article Structure (`dd004.md`)

```
---
title: "Who Pays for the AI Grid?"
---

[7 FileAttachment data loads]
[Byline]

# Who Pays for the AI Grid?
[Opening: structural mismatch]

---
## The buyers
[PE acquisition prose]
[Ownership flow diagram -- Novel 2]

---
## Where it lands
[US map -- Chart 1]
[Bimodal scatter -- Chart 2]
[Capital intensity -- Chart 3]

### The Virginia benchmark
[Virginia map -- Chart 4]

### The Indiana laboratory
[Indiana stat cards -- Chart 5]
[PJM demand -- Chart 6]

---
## Who holds the bag
[Liability taxonomy -- Chart 7]
[Bill calculator -- Novel 1]

### The FERC lever
[Regulatory timeline -- Chart 8]

---
## Sources & Methodology
```

---

## 7. Implementation Priority

### Phase 1: Core infrastructure
1. All 7 data loaders
2. `dd004.md` skeleton
3. Config + index.md updates

### Phase 2: Geographic charts (visual anchor)
4. `dc-map.js`
5. `virginia-map.js`
6. `bimodal-scatter.js`

### Phase 3: Analytical charts
7. `capital-intensity.js`
8. `pjm-demand.js`
9. `liability-taxonomy.js`

### Phase 4: Novel visualizations
10. `ownership-flow.js`
11. `bill-calculator.js`
12. `regulatory-timeline.js`

### Phase 5: Polish
13. Full prose
14. Scroll step sequences
15. Screenshot review
16. Mobile responsive testing

---

## 8. Technical Notes

- **Geographic data:** States TopoJSON ~700KB. Virginia counties filtered server-side to ~50KB.
- **Census pipeline:** `build_community_dataset()` from `src/data/census.py` does ACS join.
- **NaN handling:** `pd.DataFrame.to_json(orient="records")` outputs NaN as null.
- **Bill calculator:** Illustrative, not precise. Disclaimer required.
- **Scroll pacing:** 8-9 scroll-driven charts. 3rem minimum between sections.
- **Altair replacement:** PJM small multiples replace interactive legend selection.

---

## 9. Success Criteria

1. The "who pays" question feels personal by the end (bill calculator).
2. The geographic story is discoverable (US map invites exploration).
3. The liability mismatch is visceral (PE lifecycle vs ratepayer obligation).
4. Every chart earns its space.
5. 8-12 minutes comfortable scroll pacing.
6. All data verified against DuckDB.

---

## 10. Research References

- [D3 Graph Gallery: Bubble Map](https://d3-graph-gallery.com/bubblemap.html)
- [Observable D3 Choropleth](https://observablehq.com/@d3/choropleth/2)
- [D3 Graph Gallery: Scatter](https://d3-graph-gallery.com/scatter.html)
- [D3 Graph Gallery: Small Multiples](https://d3-graph-gallery.com/graph/smallmultiples.html)
- [d3-sankey (simplified for ownership flow)](https://github.com/d3/d3-sankey)
- [Observable Inputs](https://observablehq.com/@observablehq/inputs)
- [d3-timeline](https://github.com/denisemauldin/d3-timeline)
- [Pudding: Scrollytelling](https://pudding.cool/process/how-to-implement-scrollytelling/)
- [d3-geo documentation](https://d3js.org/d3-geo)
- [D3 Zoom module](https://d3js.org/d3-zoom)
