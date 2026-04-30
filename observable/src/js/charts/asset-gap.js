// ── Chart: Asset gap / dumbbell — demand visibility vs asset lifetime ────────
// Rows group into three categories: Agile, Durable, Risk Zone.
// Left dot = demand visibility (years). Right dot = asset lifetime (years).
// Connecting line length = structural risk.
// Steps:
//   0 — all rows muted; risk-row gaps collapsed (right dot at demand x)
//   1 — Agile + Durable rows highlighted; risk rows dimmed to 0.15
//   2 — Risk rows pop; gaps animate open; gap labels appear; ref line brightens
//   3 — All rows full opacity; all gap labels visible
//
// Returns { node, update } for use with mountScrollChart({ callout: "above" }).

import * as d3 from "npm:d3@7";
import { INK, INK_LIGHT, CONTEXT, RULE, POSITIVE, NEGATIVE, svgTitle, svgStepAnnot, svgSource, chartW } from "../design.js";
import { showTip, moveTip, hideTip } from "../tooltip.js";

// ── Data ─────────────────────────────────────────────────────────────────────

const SECTIONS = [
  {
    label: "ALIGNED — AGILE",
    color: CONTEXT,
    rows: [
      { name: "GPU server lease",        demand: 3,  life: 3  },
      { name: "Cloud compute contract",  demand: 2,  life: 3  },
    ],
  },
  {
    label: "ALIGNED — DURABLE",
    color: POSITIVE,
    rows: [
      { name: "Telecom fiber backbone",  demand: 20, life: 25 },
      { name: "Baseload power plant",    demand: 25, life: 35 },
    ],
  },
  {
    label: "RISK ZONE",
    color: NEGATIVE,
    rows: [
      { name: "Undersea cable (AI)",     demand: 5,  life: 25 },
      { name: "Data center shell",       demand: 4,  life: 40 },
      { name: "AI-dedicated substation", demand: 3,  life: 45 },
      { name: "Transmission upgrade",    demand: 3,  life: 50 },
    ],
  },
];

// Flatten rows, tagging each with its section
const ROWS = SECTIONS.flatMap(sec =>
  sec.rows.map(r => ({ ...r, color: sec.color, isRisk: sec.label === "RISK ZONE" }))
);

// ── Layout constants ──────────────────────────────────────────────────────────

const DOT_R     = 6;    // visible dot radius
const HIT_R     = 12;   // invisible hit-target radius
const ROW_H     = 34;   // vertical spacing per data row
const SEC_GAP   = 36;   // extra space above each section header (wider for inline annotations)
const SEC_HDR_H = 20;   // height reserved for section header text
const X_DOMAIN  = [0, 55];
const AI_HORIZON = 5;   // years: dashed reference line position

export function createAssetGap() {
  const W  = chartW(780);
  const ml = 170;   // left margin: label column
  const mr = 72;    // right margin: gap label column
  const mt = 52;    // top margin: title + subtitle/legend rows
  const mb = 130;   // bottom margin: x-axis + step annotation + source text

  // Compute total height from row count + section headers
  const nRows = ROWS.length;
  const nSecs = SECTIONS.length;
  const dataH = nRows * ROW_H + nSecs * (SEC_GAP + SEC_HDR_H);
  const H = mt + dataH + mb;

  // x scale (linear: 0 to 55 years)
  const x = d3.scaleLinear().domain(X_DOMAIN).range([ml, W - mr]);

  // Assign y positions: walk through sections then rows
  const rowYMap = new Map();    // name -> cy
  const secYMap = new Map();    // label -> y of header text
  let curY = mt;

  SECTIONS.forEach(sec => {
    curY += SEC_GAP;
    secYMap.set(sec.label, curY + SEC_HDR_H * 0.75);
    curY += SEC_HDR_H;
    sec.rows.forEach(r => {
      curY += ROW_H;
      rowYMap.set(r.name, curY - ROW_H * 0.5);
    });
  });

  // ── SVG ──────────────────────────────────────────────────────────────────

  const svg = d3.create("svg")
    .attr("width", "100%")
    .attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif")
    .style("overflow", "visible");

  // Add aria-label for accessibility (replaces svgTitle's role since the
  // chart's title with inline dot glyphs is hand-rolled below).
  svg.attr("role", "img").attr("aria-label", "Long-lived assets, short demand visibility");

  // ── X axis ───────────────────────────────────────────────────────────────

  const axisY = mt + dataH;

  svg.append("line")
    .attr("x1", ml).attr("x2", W - mr)
    .attr("y1", axisY).attr("y2", axisY)
    .attr("stroke", RULE).attr("stroke-width", 0.8);

  [0, 10, 20, 30, 40, 50].forEach(v => {
    svg.append("text")
      .attr("x", x(v)).attr("y", axisY + 14)
      .attr("text-anchor", "middle")
      .attr("fill", INK_LIGHT).attr("font-size", "10")
      .text(`${v} yr`);
  });

  svg.append("text")
    .attr("x", ml + (W - ml - mr) / 2).attr("y", axisY + 30)
    .attr("text-anchor", "middle")
    .attr("fill", INK_LIGHT).attr("font-size", "10.5")
    .text("Years");

  // ── Chart title + subtitle (always visible) ──────────────────────────────
  // Title states the insight; subtitle explains the encoding.
  // Both stay in view at every scroll step, giving the chart self-contained
  // context even after the markdown section heading has scrolled off.

  svg.append("text")
    .attr("x", ml).attr("y", 16)
    .attr("fill", INK)
    .attr("font-size", "13.5").attr("font-weight", "700")
    .text("Long-lived assets, short demand visibility");

  // Subtitle with inline dot glyphs — replaces the standalone dot legend
  const subY = 34;
  svg.append("circle")
    .attr("cx", ml).attr("cy", subY - 3).attr("r", DOT_R - 1)
    .attr("fill", CONTEXT).attr("stroke", CONTEXT).attr("stroke-width", 1.5);
  svg.append("text")
    .attr("x", ml + 11).attr("y", subY + 1)
    .attr("fill", INK_LIGHT).attr("font-size", "10.5")
    .text("demand horizon");

  svg.append("circle")
    .attr("cx", ml + 118).attr("cy", subY - 3).attr("r", DOT_R)
    .attr("fill", INK_LIGHT).attr("stroke", INK_LIGHT).attr("stroke-width", 1.5).attr("opacity", 0.6);
  svg.append("text")
    .attr("x", ml + 129).attr("y", subY + 1)
    .attr("fill", INK_LIGHT).attr("font-size", "10.5")
    .text("asset retirement age");

  svg.append("text")
    .attr("x", ml + 265).attr("y", subY + 1)
    .attr("fill", INK_LIGHT).attr("font-size", "10.5")
    .text("· line = years at risk");

  // ── AI demand horizon reference line ─────────────────────────────────────

  const refLine = svg.append("line")
    .attr("x1", x(AI_HORIZON)).attr("x2", x(AI_HORIZON))
    .attr("y1", mt).attr("y2", axisY)
    .attr("stroke", NEGATIVE)
    .attr("stroke-width", 1.2)
    .attr("stroke-dasharray", "3,3")
    .attr("opacity", 0.45);

  const refLabel = svg.append("text")
    .attr("x", x(AI_HORIZON) + 4).attr("y", mt + 11)
    .attr("fill", NEGATIVE).attr("font-size", "9.5")
    .attr("font-style", "italic")
    .attr("opacity", 0.8)
    .text("AI demand horizon");

  // ── Section headers ───────────────────────────────────────────────────────
  // Each section gets a thin separator rule spanning the full chart width so
  // section boundaries remain legible at all scroll steps (even when row
  // content in a section is dimmed). Font-size bumped to 11 for readability.

  SECTIONS.forEach(sec => {
    const hy = secYMap.get(sec.label);
    // Separator line — spans full plot width, always at full opacity
    svg.append("line")
      .attr("x1", ml).attr("x2", W - mr)
      .attr("y1", hy - 10).attr("y2", hy - 10)
      .attr("stroke", sec.color)
      .attr("stroke-width", 1)
      .attr("opacity", 0.3);
    // CONTEXT (#b0aba4) is too low-contrast for text on paper — use INK_LIGHT
    // for the AGILE header while keeping CONTEXT for the decorative separator line.
    const headerColor = sec.color === CONTEXT ? INK_LIGHT : sec.color;
    svg.append("text")
      .attr("x", ml - 8).attr("y", hy)
      .attr("text-anchor", "end")
      .attr("fill", headerColor)
      .attr("font-size", "11")
      .attr("font-weight", "700")
      .attr("letter-spacing", "0.06em")
      .text(sec.label);
  });

  // ── Rows (dots + lines + labels + hit targets) ────────────────────────────

  const rowEls = ROWS.map((row, i) => {
    const cy      = rowYMap.get(row.name);
    const xDemand = x(row.demand);
    const xLife   = x(row.life);
    const gap     = row.life - row.demand;
    const isRisk  = row.isRisk;
    const col     = row.color;

    // Y-axis row label — INK for full contrast (primary navigation labels)
    svg.append("text")
      .attr("x", ml - 10).attr("y", cy + 4)
      .attr("text-anchor", "end")
      .attr("fill", INK).attr("font-size", "11.5")
      .text(row.name);

    // Connector line — starts at xDemand for risk rows (zero-length), xLife for safe
    const connLine = svg.append("line")
      .attr("x1", xDemand + DOT_R).attr("x2", isRisk ? xDemand + DOT_R : xLife - DOT_R)
      .attr("y1", cy).attr("y2", cy)
      .attr("stroke", col)
      .attr("stroke-width", isRisk ? 2.5 : 1.8)
      .attr("opacity", isRisk ? 0 : 0.5);

    // Left dot: demand visibility
    const leftDot = svg.append("circle")
      .attr("cx", xDemand).attr("cy", cy).attr("r", DOT_R)
      .attr("fill", CONTEXT)
      .attr("stroke", col).attr("stroke-width", 1.5)
      .attr("opacity", 0.5);

    // Left dot hit target
    svg.append("circle")
      .attr("cx", xDemand).attr("cy", cy).attr("r", HIT_R)
      .attr("fill", "transparent").style("cursor", "crosshair")
      .on("mouseover", (e) => {
        leftDot.attr("r", DOT_R + 2);
        showTip(e,
          row.name,
          `Demand visibility: ${row.demand} yr`,
          `Asset lifetime: ${row.life} yr`,
          gap > 0 ? `Gap: ${gap} yr` : "Aligned"
        );
      })
      .on("mousemove", moveTip)
      .on("mouseout", () => { leftDot.attr("r", DOT_R); hideTip(); });

    // Right dot: asset lifetime — starts at xDemand for risk rows
    const rightDot = svg.append("circle")
      .attr("cx", isRisk ? xDemand : xLife).attr("cy", cy).attr("r", DOT_R)
      .attr("fill", col)
      .attr("opacity", isRisk ? 0 : 0.85);

    // Right dot hit target
    const rightHit = svg.append("circle")
      .attr("cx", isRisk ? xDemand : xLife).attr("cy", cy).attr("r", HIT_R)
      .attr("fill", "transparent").style("cursor", "crosshair")
      .on("mouseover", (e) => {
        rightDot.attr("r", DOT_R + 2);
        showTip(e,
          row.name,
          `Asset lifetime: ${row.life} yr`,
          `Demand visibility: ${row.demand} yr`,
          gap > 0 ? `Gap: ${gap} yr` : "Aligned"
        );
      })
      .on("mousemove", moveTip)
      .on("mouseout", () => { rightDot.attr("r", DOT_R); hideTip(); });

    // Gap label — right of right dot, hidden until step 2/3
    const gapLabel = gap > 0
      ? svg.append("text")
          .attr("x", xLife + DOT_R + 5).attr("y", cy + 4)
          .attr("fill", col)
          .attr("font-size", "10").attr("font-weight", "600")
          .attr("opacity", 0)
          .text(`${gap} yr gap`)
      : null;

    // Row wrapper group opacity — used for dim/highlight
    // We return individual elements instead of a group to control independently

    return { row, cy, xDemand, xLife, connLine, leftDot, rightDot, rightHit, gapLabel, col, isRisk };
  });

  // ── Inline section annotations ───────────────────────────────────────────
  // Positioned in the inter-section gap space created by the wider SEC_GAP.
  // annotAligned: below last DURABLE row, in the gap before RISK ZONE header.
  // annotRisk:    midpoint between RISK ZONE header and first risk row.

  const annotAlignedY = rowYMap.get("Baseload power plant") + 16;
  const annotRiskY    = Math.round(
    (secYMap.get("RISK ZONE") + rowYMap.get("Undersea cable (AI)")) / 2
  );

  // Both annotations start after the AI demand horizon dashed line to avoid
  // visual interference where the vertical rule cuts through text.
  const annotX = x(AI_HORIZON) + 8;

  const annotAligned = svg.append("text")
    .attr("x", annotX).attr("y", annotAlignedY)
    .attr("fill", INK).attr("font-size", "10.5")
    .attr("font-style", "italic").attr("opacity", 0)
    .text("Short gaps — aligned assets stay within their demand window");

  const annotRisk = svg.append("text")
    .attr("x", annotX).attr("y", annotRiskY)
    .attr("fill", INK).attr("font-size", "10.5")
    .attr("font-style", "italic").attr("opacity", 0)
    .text("");

  // ── Source ───────────────────────────────────────────────────────────────

  svgSource(svg, W, H, "Source: Author’s risk framework; EIA; industry estimates; SEC filings");

  // ── Step annotation — bottom strip (article narrative) ───────────────────
  const STEP_ANNOTS = [
    "Each row shows two numbers: how long demand forecasts hold, and how long the asset lasts. The line between them is the exposure gap.",
    "Aligned assets have short or no gaps — demand forecasts and asset life move together.",
    "Demand forecasts run 3–5 years out. Asset lifetimes run 25–50 years.",
    "The substation serving a 3-year lease has a 40-year service life. Every row in this chart shows that gap.",
  ];
  const stepAnnot = svgStepAnnot(svg, { y: axisY + 50, W, ml });

  // ── Step control ──────────────────────────────────────────────────────────

  // Helpers: set an individual row's visual state
  function setRowOpacity(el, op) {
    el.connLine.transition().duration(200).attr("opacity", op * (el.isRisk ? 0.85 : 0.5));
    el.leftDot.transition().duration(200).attr("opacity", op);
    el.rightDot.transition().duration(200).attr("opacity", op * 0.85);
    if (el.gapLabel) el.gapLabel.transition().duration(200).attr("opacity", 0);
  }

  function setRowFull(el) {
    el.connLine.transition().duration(200).attr("opacity", el.isRisk ? 0.85 : 0.5);
    el.leftDot.transition().duration(200).attr("opacity", 1);
    el.rightDot.transition().duration(200).attr("opacity", 0.85);
    if (el.gapLabel) el.gapLabel.transition().duration(200).attr("opacity", 1);
  }

  // Animate a risk row's gap opening (right dot + line grow from demand x to life x)
  function animateRiskGap(el, delay) {
    el.connLine.interrupt()
      // Ensure the connector starts correctly positioned before animating
      .attr("x1", el.xDemand + DOT_R)
      .attr("x2", el.xDemand + DOT_R)
      .attr("opacity", 0.85)
      .transition().delay(delay).duration(700).ease(d3.easeQuadOut)
      .attr("x2", el.xLife - DOT_R);

    el.rightDot.interrupt()
      .attr("cx", el.xDemand)
      .attr("opacity", 1)
      .transition().delay(delay).duration(700).ease(d3.easeQuadOut)
      .attr("cx", el.xLife);

    el.rightHit.interrupt()
      .attr("cx", el.xDemand)
      .transition().delay(delay).duration(700).ease(d3.easeQuadOut)
      .attr("cx", el.xLife);

    if (el.gapLabel) {
      el.gapLabel.interrupt()
        .attr("opacity", 0)
        .transition().delay(delay + 600).duration(300)
        .attr("opacity", 1);
    }
  }

  // Collapse a risk row's gap back to zero-length (for step 0 reset)
  function collapseRiskGap(el) {
    el.connLine.interrupt()
      .attr("x1", el.xDemand + DOT_R)
      .attr("x2", el.xDemand + DOT_R)
      .attr("opacity", 0.4);
    el.rightDot.interrupt().attr("cx", el.xDemand).attr("opacity", 0.4);
    el.rightHit.interrupt().attr("cx", el.xDemand);
    if (el.gapLabel) el.gapLabel.interrupt().attr("opacity", 0);
  }

  function update(step) {
    if (step === 0) {
      // All rows muted; risk gaps collapsed
      rowEls.forEach(el => {
        if (el.isRisk) {
          collapseRiskGap(el);
          el.leftDot.transition().duration(200).attr("opacity", 0.5);
        } else {
          setRowOpacity(el, 0.5);
        }
      });
      refLine.transition().duration(300).attr("opacity", 0.45);
      refLabel.transition().duration(300).attr("opacity", 0.8);
      annotAligned.interrupt().attr("opacity", 0);
      annotRisk.interrupt().attr("opacity", 0);

    } else if (step === 1) {
      // Agile + Durable at full opacity; risk rows dimmed 0.15; gaps still collapsed
      rowEls.forEach(el => {
        if (el.isRisk) {
          collapseRiskGap(el);
          el.leftDot.transition().duration(200).attr("opacity", 0.15);
        } else {
          el.connLine.transition().duration(200).attr("opacity", 0.5);
          el.leftDot.transition().duration(200).attr("opacity", 1);
          el.rightDot.transition().duration(200).attr("opacity", 0.85);
          if (el.gapLabel) el.gapLabel.transition().duration(200).attr("opacity", 1);
        }
      });
      refLine.transition().duration(300).attr("opacity", 0.45);
      refLabel.transition().duration(300).attr("opacity", 0.8);
      annotAligned.transition().duration(400).attr("opacity", 0.85);
      annotRisk.interrupt().attr("opacity", 0);

    } else if (step === 2) {
      // Risk rows pop with animated gap reveal; safe rows dim to 0.22
      const riskRows = rowEls.filter(el => el.isRisk);
      rowEls.forEach(el => {
        if (!el.isRisk) {
          el.connLine.transition().duration(200).attr("opacity", 0.22);
          el.leftDot.transition().duration(200).attr("opacity", 0.22);
          el.rightDot.transition().duration(200).attr("opacity", 0.22);
          if (el.gapLabel) el.gapLabel.transition().duration(200).attr("opacity", 0);
        }
      });
      riskRows.forEach((el, i) => {
        el.leftDot.transition().duration(200).attr("opacity", 1);
        animateRiskGap(el, i * 80);
      });
      refLine.transition().duration(300).attr("opacity", 0.85);
      refLabel.transition().duration(300).attr("opacity", 0.9);
      annotAligned.transition().duration(300).attr("opacity", 0.3);
      annotRisk
        .text("3\u20135 yr demand horizon, 25\u201350 yr assets \u2014 the gap is structural")
        .transition().duration(400).attr("opacity", 0.85);

    } else {
      // step 3: all rows full opacity; all gaps revealed
      rowEls.forEach(el => {
        if (el.isRisk) {
          el.leftDot.interrupt().attr("opacity", 1);
          el.connLine.interrupt()
            .attr("x1", el.xDemand + DOT_R)
            .attr("x2", el.xLife - DOT_R)
            .attr("opacity", 0.85);
          el.rightDot.interrupt().attr("cx", el.xLife).attr("opacity", 0.85);
          el.rightHit.interrupt().attr("cx", el.xLife);
          if (el.gapLabel) el.gapLabel.interrupt().attr("opacity", 1);
        } else {
          setRowFull(el);
        }
      });
      refLine.transition().duration(300).attr("opacity", 0.85);
      refLabel.transition().duration(300).attr("opacity", 0.9);
      annotAligned.transition().duration(300).attr("opacity", 0.7);
      annotRisk
        .text("Substations, data centers, and transmission will outlast every forecast that justified them")
        .transition().duration(300).attr("opacity", 0.85);
    }

    stepAnnot.update(step, STEP_ANNOTS);
  }

  return { node: svg.node(), update };
}
