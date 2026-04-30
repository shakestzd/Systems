// ── Design tokens — single source of truth ────────────────────────────────
// Import from here everywhere. Never declare these values in article files.

export const PAPER     = "#f5f1eb";
export const INK       = "#1a1917";
export const INK_LIGHT = "#6b6560";
export const ACCENT    = "#b84c2a";
export const CONTEXT   = "#b0aba4";
export const RULE      = "#c8c2b8";

// Company color palette — hue-aligned with Marimo COMPANY_COLORS but adapted for
// the paper background (#f5f1eb). Three primary companies use maximally distinct hues:
//   AMZN = orange  (Marimo: #ff9900)
//   GOOGL = green  (Marimo: #34a853) — NOT blue; must match Marimo for cross-chart consistency
//   MSFT = blue    (Marimo: #00a4ef)
export const CO = {
  AMZN:  "#c96b28",
  GOOGL: "#2a7d42",
  MSFT:  "#3a6fa8",
  META:  "#BB5566",
  NVDA:  "#2b7e87",
  ORCL:  "#CCBB44",
  TSLA:  "#AA3377",
  AAPL:  "#44BB99",
};

export const LABEL = {
  AMZN: "Amazon",
  GOOGL: "Alphabet",
  MSFT: "Microsoft",
  META: "Meta",
  NVDA: "Nvidia",
  ORCL: "Oracle",
  TSLA: "Tesla",
  AAPL: "Apple",
};

// Semantic colors — risk/outcome encoding (mirrors Marimo COLORS["positive/negative"])
export const POSITIVE = "#4c8c5c";  // aligned / safe / can exit
export const NEGATIVE = "#c44e52";  // risk-bearing / locked in
export const NEUTRAL  = "#8c8278";  // mechanism / intermediate

// Occupation group colors — DD-003 labor market analysis
export const OCC_TECH   = "#4477AA";   // muted blue — tech/software occupations
export const OCC_TRADES = ACCENT;      // warm accent — construction trades

// ── Responsive breakpoints ───────────────────────────────────────────────────
/** Responsive chart width — pass the chart's max desired width */
export const chartW = (maxW = 820) => Math.min(maxW, (document.body?.clientWidth ?? maxW) - 40);
export const MOBILE_BP = 500;
export const isMobile = (W) => W < MOBILE_BP;

// ── Responsive typography ────────────────────────────────────────────────────
// SVG viewBox width scales, but text font-size doesn't. These helpers return
// sizes proportional to the chart width so titles and subtitles don't clip.
export const titleSize = W => Math.max(10, Math.min(13, W * 0.022));
export const subtitleSize = W => Math.max(8.5, Math.min(10.5, W * 0.018));

/**
 * Append a wrapping title + subtitle block to an SVG using foreignObject.
 * Returns the foreignObject selection (height is set to `h` param).
 *
 *   svgTitle(svg, W, { title: "...", subtitle: "...", h: 42 });
 */
export function svgTitle(svg, W, { title, subtitle, x = 8, y = 0, h = 42 } = {}) {
  const fo = svg.append("foreignObject")
    .attr("x", x).attr("y", y).attr("width", W - x).attr("height", h);
  const div = fo.append("xhtml:div")
    .style("font-family", "'DM Sans', sans-serif")
    .style("line-height", "1.3");
  div.append("xhtml:div")
    .style("font-size", `${titleSize(W)}px`)
    .style("font-weight", "700")
    .style("color", INK)
    .text(title);
  if (subtitle) {
    div.append("xhtml:div")
      .style("font-size", `${subtitleSize(W)}px`)
      .style("color", INK_LIGHT)
      .style("margin-top", "2px")
      .text(subtitle);
  }
  // Accessibility
  svg.attr("role", "img").attr("aria-label", title);
  return fo;
}

/**
 * Append a legend row to an SVG. Auto-stacks vertically on mobile.
 * Items: [{ type: "circle"|"rect"|"line", fill, text }]
 */
export function svgLegend(svg, items, { y, ml = 0, W, gap = 200, mobileGap = 18 } = {}) {
  const mobile = W < MOBILE_BP;
  items.forEach((item, i) => {
    const lx = mobile ? ml : ml + i * gap;
    const ly = mobile ? y + i * mobileGap : y;
    if (item.type === "rect") {
      svg.append("rect").attr("x", lx).attr("y", ly - 10)
        .attr("width", 12).attr("height", 12).attr("fill", item.fill).attr("opacity", 0.7);
    } else if (item.type === "line") {
      svg.append("line").attr("x1", lx).attr("x2", lx + 12)
        .attr("y1", ly - 4).attr("y2", ly - 4)
        .attr("stroke", item.fill).attr("stroke-width", 2);
    } else {
      svg.append("circle").attr("cx", lx + 6).attr("cy", ly - 4)
        .attr("r", 5).attr("fill", item.fill);
    }
    svg.append("text").attr("x", lx + 17).attr("y", ly + 2)
      .attr("fill", INK_LIGHT).attr("font-size", "10.5").text(item.text);
  });
}

/**
 * Append a wrapping step-annotation block (foreignObject) to an SVG.
 * Returns { fo, div, rule, update(step, annots) }.
 * Call update(step, STEP_ANNOTS) from the chart's step handler.
 */
export function svgStepAnnot(svg, { x = 0, y, W, ml = 0 } = {}) {
  const g = svg.append("g").attr("transform", `translate(0, ${y})`).style("opacity", 0);
  g.append("line")
    .attr("x1", ml - 6).attr("x2", ml - 6)
    .attr("y1", 0).attr("y2", 18)
    .attr("stroke", ACCENT).attr("stroke-width", 2);
  const fo = g.append("foreignObject")
    .attr("x", ml).attr("y", 0).attr("width", W - ml - 8).attr("height", 50);
  const div = fo.append("xhtml:div")
    .style("font-family", "'DM Sans', sans-serif")
    .style("font-size", "11px").style("font-style", "italic")
    .style("color", INK).style("line-height", "1.3");
  function update(step, annots) {
    if (step >= 0 && step < annots.length) {
      div.text(annots[step]);
      g.transition().duration(350).style("opacity", "0.85");
    } else {
      g.interrupt().style("opacity", "0");
    }
  }
  return { fo, div, rule: g, update };
}

/**
 * Append a wrapping source line (foreignObject) at the bottom of an SVG.
 */
export function svgSource(svg, W, H, text) {
  const fo = svg.append("foreignObject")
    .attr("x", 0).attr("y", H - 18).attr("width", W).attr("height", 18);
  fo.append("xhtml:div")
    .style("font-family", "'DM Sans', sans-serif").style("font-size", "10px")
    .style("color", INK_LIGHT).style("padding", "0 8px")
    .text(text);
  return fo;
}

/** Color by ticker — falls back to INK_LIGHT for unknown tickers */
export const cc = t => CO[t] ?? INK_LIGHT;

/** Display label by ticker — falls back to the ticker string itself */
export const cl = t => LABEL[t] ?? t;

// ── DD-002 tokens: fuel types, ISO regions, feedback loops ──────────────────

/** Fuel type colors — adapted from Marimo FUEL_COLORS for paper background */
export const FUEL = {
  solar:   "#D4943A",
  wind:    "#4477AA",
  battery: "#55BBCC",
  gas_cc:  "#CC6677",
  gas_ct:  "#BB4444",
  nuclear: "#AA3377",
  hydro:   "#228833",
  coal:    "#999999",
};

/** ISO/RTO territory colors — Paul Tol qualitative palette */
export const ISO_COLOR = {
  PJM:    "#4477AA",
  MISO:   "#66CCEE",
  ERCOT:  "#228833",
  CAISO:  "#CCBB44",
  SPP:    "#EE6677",
  NYISO:  "#AA3377",
  "ISO-NE": "#BBBBBB",
  "Non-ISO Southeast": "#CC6677",
  "Non-ISO West": "#999999",
};

/** Feedback loop colors (CLD diagram) */
export const LOOP = {
  R1: "#4477AA",   // Grid Investment Cycle
  R2: "#228833",   // Renewable Learning
  B1: "#CCBB44",   // Regulatory Uncertainty
  B2: "#CC3311",   // BTM Bypass
  B3: "#AA3377",   // Stranded Asset Risk
};

/** Fuel label helper */
export const FUEL_LABEL = {
  solar:   "Solar",
  wind:    "Wind",
  battery: "Battery Storage",
  gas_cc:  "Gas (CC)",
  gas_ct:  "Gas (CT)",
  nuclear: "Nuclear",
  hydro:   "Hydro",
  coal:    "Coal",
};

// ── DD-004 tokens: utility regulation / cost allocation ─────────────────────
export const RATEPAYER = "#8c8279";   // warm gray — ratepayer-held liability
export const PUBLIC    = "#e8c97e";   // warm yellow — public/sunk cost
export const DOM_ZONE  = "#3a6fa8";   // Dominion Virginia zone
export const AEP_ZONE  = ACCENT;     // AEP Indiana zone (same as accent)
