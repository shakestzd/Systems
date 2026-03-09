# Scroll Pattern Reference

Each chart is rated on how well its scroll sequence guides reader attention.
Rate each chart 1–10 after reviewing it in the browser.

**Rating criteria:**
- 10 — Every step lands. Reader knows exactly what to look at. No step feels wasted.
- 7–9 — Mostly works. One step could be tighter or a transition is slightly off.
- 4–6 — The sequence is there but doesn't fully earn the scroll space.
- 1–3 — Scroll interaction adds noise rather than clarity.

---

## Valuation — Market Cap Horizontal Bar
**File:** `src/js/charts/valuation.js`
**Rating: 10/10**

**Why it works:**
Prose steps ARE the chart states. Each company paragraph highlights that company's bar
and dims the rest. The reader's eye is physically directed by the chart to the company
they're reading about. No step is decorative — every transition carries new information.
The sticky layout means the chart is always visible while prose scrolls past it.

**Pattern:** Prose-step driven. Chart is sticky. Each step = one company highlighted.
**Technique:** Gray + accent (SWD focus pattern). End labels appear when their company
step activates.

---

## Demand Thesis — Revenue Thesis Cards
**File:** `src/js/charts/demand-thesis.js`
**Rating: 10/10**

**Why it works:**
The chart responds to WHERE the reader is within it, not to prose below it. As you
scroll through the card section, the card closest to the viewport center auto-expands
showing the full description. Collapsing on exit means re-entry always starts fresh.
The IntersectionObserver start/stop means the listener only runs while the SVG is
visible — no wasted computation.

**Pattern:** Position-within-chart driven. No external prose steps needed.
**Technique:** Horizontal expansion (width only, height constant). Cards in other
columns clamp to prevent viewport overflow.

---

## Capex History — Line Chart (2015–2025)
**File:** `src/js/charts/capex-history.js`
**Rating:** ___/10
**Notes:** _(fill after reviewing)_

**Scroll sequence:**
| Step | Prose | Chart action |
|:-----|:------|:-------------|
| 0 | "Cloud infrastructure spending grew slowly for years — a reliable but predictable build." | Pre-2022 gray lines draw in |
| 1 | "Then 2022 happened." | Vertical inflection marker appears at 2022 |
| 2 | "Spending doubled in two years. No previous cycle moved this fast." | Post-2022 accent lines accelerate upward |
| 3 | "By 2025: $380B. Five times what these companies spent in 2019." | Magnitude label + multiplier badge fade in |

**Key attention signal:** Gray → color transition at 2022. The regime change is visual.

---

## Stacked Capex — Company Bar Chart by Year
**File:** `src/js/charts/stacked-capex.js`
**Rating:** ___/10
**Notes:** _(fill after reviewing)_

**Scroll sequence:**
| Step | Prose | Chart action |
|:-----|:------|:-------------|
| 0 | "Here's the full picture: who spent what, year by year since 2022." | All bars grow, grayscale |
| 1 | "Amazon has led cumulative spend from the start." | Amazon bar highlights, others dim |
| 2 | "Meta barely registered in 2022. Their 2026 guidance is $60B." | Meta bar highlights, 2026 hatched segment appears |
| 3 | "Across all six companies, 2026 guidance totals $710B. That number carries a ±33% revision history." | All 2026 segments appear with uncertainty hatching |

**Key attention signal:** Dim all but the highlighted company. 2026 hatching signals uncertainty.

---

## Off-Balance Sheet — Reported vs Hidden Capex
**File:** `src/js/charts/off-balance.js`
**Rating:** ___/10
**Notes:** _(fill after reviewing)_

**Scroll sequence:**
| Step | Prose | Chart action |
|:-----|:------|:-------------|
| 0 | "Here's what the 10-K filings report as capital expenditure." | Gray reported bars only, labels inside |
| 1 | "But operating leases and special-purpose vehicles hide billions more — commitments that flow through operating expenses, not capex lines." | Accent off-balance bars stack on top |
| 2 | "Microsoft's real 2025 infrastructure commitment: $110B. The filing says $60B." | Total label appears above each stack |

**Key attention signal:** The bar physically grows when the hidden layer appears. The gap is the message.

---

## Revenue Ratio — Capex ÷ Revenue Lines
**File:** `src/js/charts/revenue-ratio.js`
**Rating:** ___/10
**Notes:** _(fill after reviewing)_

**Scroll sequence:**
| Step | Prose | Chart action |
|:-----|:------|:-------------|
| 0 | "The 1.0× line is parity: spending equals what the cloud business earns." | All lines draw in, parity line labeled |
| 1 | "Through 2023, all three companies stayed below it. Spending less than you earn is sustainable." | All three lines visible but dimmed, safe zone shaded |
| 2 | "Alphabet crossed first, in 2024." | Alphabet line highlights, crossing annotated |
| 3 | "Amazon followed in 2025. Microsoft is approaching." | Amazon line highlights, crossing annotated; Microsoft line arrows toward line |

**Key attention signal:** The 1.0× line is the fixed reference. Crossing = structural shift.

---

## Revenue Gap — Absolute Revenue vs Capex Lines
**File:** `src/js/charts/revenue-gap.js`
**Rating:** ___/10
**Notes:** _(fill after reviewing)_

**Scroll sequence:**
| Step | Prose | Chart action |
|:-----|:------|:-------------|
| 0 | "In early 2023, infrastructure spending and cloud revenue were roughly in sync." | Both solid and dashed lines draw, clustered together |
| 1 | "Then capex started climbing faster than revenue." | Dashed (capex) lines curve upward, gap becomes visible |
| 2 | "For Alphabet and Amazon, capex now exceeds what their cloud businesses earn. The gap is widening." | Gap band shades between dashed and solid for Alphabet and Amazon |

**Key attention signal:** Shaded gap area appears only after prose names what it means.

---

## Guidance — 2025 Actual vs 2026 Forecast
**File:** `src/js/charts/guidance.js`
**Rating:** ___/10
**Notes:** _(fill after reviewing)_

**Scroll sequence:**
| Step | Prose | Chart action |
|:-----|:------|:-------------|
| 0 | "Here's what companies actually spent in 2025." | Gray actual bars with value labels |
| 1 | "And here's what management is claiming for 2026." | Guidance dots appear above bars |
| 2 | "The problem: guidance has swung by ±33% in a single year before. 2026 carries the same risk." | Error bands extend from each dot |

**Key attention signal:** Dot sits above the bar — the gap between them is the forward claim.
Error band makes the uncertainty concrete.

---

## Scenarios — Bull / Base / Bear Dumbbell
**File:** `src/js/charts/scenarios.js`
**Rating:** ___/10
**Notes:** _(fill after reviewing)_

**Scroll sequence:**
| Step | Prose | Chart action |
|:-----|:------|:-------------|
| 0 | "One spending line. Three possible worlds." | All rows visible but dimmed |
| 1 | "Bull case: demand validates. Revenue catches up to capex." | Bull row highlights, gap band shades |
| 2 | "Base case: current trajectory holds. The gap persists." | Base row highlights |
| 3 | "Bear case: guidance cut 33%, but revenue misses too. The gap barely closes." | Bear row highlights |
| 4 | "The connector length is the entire argument. Bear looks better on paper — but both ends move." | All three rows at full opacity, gap widths side by side |

**Key attention signal:** Connector length = gap size. Bear's counter-intuitive short
connector (both capex AND revenue drop) is the insight that earns the scroll space.

---

## Pattern Library

Techniques used across these charts, for future reference:

| Technique | When to use | Example |
|:---|:---|:---|
| **Gray + accent reveal** | Highlighting one element while others provide context | Stacked capex, revenue ratio |
| **Prose-step driven** | Narrative follows clear company/category sequence | Valuation |
| **Progressive line draw** | Time series with a clear before/after | Capex history |
| **Stacking reveal** | Two-layer comparison (reported vs hidden, actual vs forecast) | Off-balance, guidance |
| **Gap shading** | Show divergence between two related series | Revenue gap |
| **Threshold line** | Fixed reference point that elements cross | Revenue ratio (1.0×) |
| **Position-driven** | Chart responds to scroll position within itself | Demand thesis |
| **Row spotlight** | Multi-row chart; one row active at a time | Scenarios |
