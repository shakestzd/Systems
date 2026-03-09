// ── Chart: 2026 scenarios — horizontal dumbbell gap chart ─────────────────
// Returns { node, update } for use with mountScrollChart.
// Steps: 0 = all rows dimmed | 1 = Bull | 2 = Base | 3 = Bear | 4 = all full

import * as d3 from "npm:d3@7";
import { INK, INK_LIGHT, ACCENT, CONTEXT, RULE } from "../design.js";
import { showTip, moveTip, hideTip } from "../tooltip.js";

const REV_COLOR = "#3a6fa8";
const DOT_R     = 9;

export function createScenarios(stats) {
  const capexPoint = stats.guidance_2026_point;
  const revMid     = (stats.cloud_rev_2026_low + stats.cloud_rev_2026_high) / 2;

  const scenarios = [
    { name: "Bull", sub: "Demand validates",
      capex: capexPoint,  revenue: stats.cloud_rev_2026_high },
    { name: "Base", sub: "Current trajectory",
      capex: capexPoint,  revenue: revMid },
    { name: "Bear", sub: `Guidance cut −${stats.guidance_band_pct}%`,
      capex: capexPoint * (1 - stats.guidance_band_pct / 100),
      revenue: stats.cloud_rev_2026_low },
  ];
  scenarios.forEach(s => { s.ratio = s.capex / s.revenue; s.gap = s.capex - s.revenue; });

  const W   = Math.min(660, (document.body?.clientWidth ?? 660) - 40);
  const H   = 374;
  const mt  = 58;
  const mb  = 80;
  const ml  = 112;
  const mr  = 24;

  const plotH  = H - mt - mb;
  const rowH   = plotH / 3;
  const rowY   = (i) => mt + rowH * i + rowH / 2;

  const allVals = scenarios.flatMap(s => [s.capex, s.revenue]);
  const xDomLo  = d3.min(allVals) * 0.90;
  const xDomHi  = d3.max(allVals) * 1.05;
  const x = d3.scaleLinear().domain([xDomLo, xDomHi]).range([ml, W - mr]);

  const svg = d3.create("svg")
    .attr("width", "100%").attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif")
    .style("overflow", "visible");

  // ── Title + subtitle ────────────────────────────────────────────────────
  svg.append("text").attr("x", ml).attr("y", 16)
    .attr("fill", INK).attr("font-size", "13").attr("font-weight", "700")
    .text("Three 2026 scenarios: how the capex-revenue gap resolves");
  svg.append("text").attr("x", ml).attr("y", 30)
    .attr("fill", INK_LIGHT).attr("font-size", "10.5")
    .text("Left dot = cloud revenue · right dot = capex · band = gap between them");

  // Grid lines + tick labels
  const tickVals = [400, 500, 600, 700].filter(v => v >= xDomLo && v <= xDomHi);
  const axisY    = H - mb + 6;
  tickVals.forEach(v => {
    svg.append("line")
      .attr("x1", x(v)).attr("x2", x(v)).attr("y1", mt).attr("y2", H - mb)
      .attr("stroke", RULE).attr("stroke-width", 0.5).attr("opacity", 0.5);
    svg.append("text")
      .attr("x", x(v)).attr("y", axisY + 12)
      .attr("text-anchor", "middle").attr("fill", CONTEXT).attr("font-size", "9.5")
      .text(`$${v}B`);
  });

  svg.append("line")
    .attr("x1", ml).attr("x2", W - mr).attr("y1", H - mb).attr("y2", H - mb)
    .attr("stroke", RULE).attr("stroke-width", 0.8).attr("opacity", 0.6);

  // Per-scenario rows
  const animEls = [];

  scenarios.forEach((s, i) => {
    const ry   = rowY(i);
    const revX = x(s.revenue);
    const capX = x(s.capex);
    const midX = (revX + capX) / 2;
    const gapW = capX - revX - DOT_R * 2;

    // Scenario name — always visible
    svg.append("text")
      .attr("x", ml - 10).attr("y", ry - 7)
      .attr("text-anchor", "end").attr("fill", INK)
      .attr("font-size", "13").attr("font-weight", "700")
      .text(s.name);
    svg.append("text")
      .attr("x", ml - 10).attr("y", ry + 9)
      .attr("text-anchor", "end").attr("fill", INK_LIGHT)
      .attr("font-size", "9.5")
      .text(s.sub);

    // Shaded gap band
    const gapBand = svg.append("rect")
      .attr("x", revX + DOT_R).attr("y", ry - 14)
      .attr("width", 0).attr("height", 28).attr("rx", 2)
      .attr("fill", ACCENT).attr("opacity", 0.09);

    // Connector line
    const connector = svg.append("line")
      .attr("x1", revX + DOT_R).attr("x2", revX + DOT_R)
      .attr("y1", ry).attr("y2", ry)
      .attr("stroke", ACCENT).attr("stroke-width", 1.8).attr("opacity", 0.30);

    // Revenue dot
    const revDot = svg.append("circle")
      .attr("cx", revX).attr("cy", ry).attr("r", 0)
      .attr("fill", REV_COLOR).style("cursor", "crosshair");
    revDot
      .on("mouseover", e => { revDot.attr("r", DOT_R + 2); showTip(e, `${s.name} · Cloud Revenue`, `$${s.revenue.toFixed(0)}B`); })
      .on("mousemove", moveTip)
      .on("mouseout",  () => { revDot.attr("r", DOT_R); hideTip(); });

    // Capex dot
    const capDot = svg.append("circle")
      .attr("cx", capX).attr("cy", ry).attr("r", 0)
      .attr("fill", ACCENT).style("cursor", "crosshair");
    capDot
      .on("mouseover", e => { capDot.attr("r", DOT_R + 2); showTip(e, `${s.name} · Capex`, `$${s.capex.toFixed(0)}B`); })
      .on("mousemove", moveTip)
      .on("mouseout",  () => { capDot.attr("r", DOT_R); hideTip(); });

    // Labels — start hidden
    const revLab = svg.append("text")
      .attr("x", revX).attr("y", ry - DOT_R - 7)
      .attr("text-anchor", "middle").attr("fill", REV_COLOR)
      .attr("font-size", "11").attr("font-weight", "700")
      .attr("opacity", 0).text(`$${s.revenue.toFixed(0)}B`);

    const capLab = svg.append("text")
      .attr("x", capX).attr("y", ry - DOT_R - 7)
      .attr("text-anchor", "middle").attr("fill", ACCENT)
      .attr("font-size", "11").attr("font-weight", "700")
      .attr("opacity", 0).text(`$${s.capex.toFixed(0)}B`);

    const gapLab = svg.append("text")
      .attr("x", midX).attr("y", ry + DOT_R + 15)
      .attr("text-anchor", "middle").attr("fill", INK)
      .attr("font-size", "10.5").attr("font-weight", "600")
      .attr("opacity", 0).text(`$${Math.round(s.gap)}B gap`);

    const ratioLab = svg.append("text")
      .attr("x", midX).attr("y", ry + DOT_R + 28)
      .attr("text-anchor", "middle").attr("fill", INK_LIGHT)
      .attr("font-size", "9.5").attr("font-style", "italic")
      .attr("opacity", 0).text(`${s.ratio.toFixed(2)}× capex/rev`);

    animEls.push({
      connector, gapBand, revDot, capDot,
      revLab, capLab, gapLab, ratioLab,
      revX, capX, gapW
    });
  });

  // Legend
  const legY = H - mb + 30;
  [{ color: ACCENT,    text: "Capital expenditure" },
   { color: REV_COLOR, text: "Cloud revenue (AWS + Azure + Google Cloud)" }]
    .forEach((l, i) => {
      svg.append("circle").attr("cx", ml + i * 230).attr("cy", legY).attr("r", 5).attr("fill", l.color);
      svg.append("text").attr("x", ml + i * 230 + 14).attr("y", legY + 4)
        .attr("fill", INK_LIGHT).attr("font-size", "10.5").text(l.text);
    });

  svg.append("text")
    .attr("x", ml).attr("y", H - mb + 52)
    .attr("fill", CONTEXT).attr("font-size", "9")
    .text(`2026 projections: TZD Labs analysis · Cloud revenue $${stats.cloud_rev_2026_low}–$${stats.cloud_rev_2026_high}B · Capex: management guidance ± band`);

  // ── SVG-native step annotation ────────────────────────────────────────────
  // Positioned using the same D3 scale as the data — responsive at all viewports.
  // Bear's capex is the shortest (left-most right dot), so annotX sits in the
  // clear horizontal zone that exists at every step. Y tracks each active row.
  const bearCapX = animEls[2].capX;
  const annotX   = bearCapX + 22;          // 22 SVG units right of Bear capex dot
  const annotW   = W - mr - annotX - 6;   // remaining width to right margin
  const annotFS  = 11;                     // font-size in SVG units (scales with chart)
  const annotLH  = 15.5;                   // line height in SVG units

  // Y anchor per step: first text baseline position (SVG units, from rowY)
  //   Steps 0, 3, 4 → Bear row zone (right of Bear data, which stops at bearCapX)
  //   Step 1 Bull    → below Bull's ratioLab (rowY(0)+DOT_R+28 ≈ 134), Bear/Base labels hidden
  //   Step 2 Base    → below Base's ratioLab (rowY(1)+DOT_R+28 ≈ 213), Bear labels hidden
  function annotY(step) {
    return [
      rowY(2) + 6,    // 0: Bear row center, all labels dimmed
      rowY(0) + 52,   // 1: Bull — below Bull's ratioLab
      rowY(1) + 52,   // 2: Base — below Base's ratioLab
      rowY(2) + 6,    // 3: Bear — at Bear row center, right of capX
      rowY(2) + 6,    // 4: all full — same zone, horizontally clear
    ][step] ?? rowY(2) + 6;
  }

  const ANNOT_TEXTS = [
    `$${capexPoint.toFixed(0)}B guided for 2026. Three scenarios, three gap trajectories.`,
    "Bull: AI revenue accelerates. The capex-revenue gap starts to close.",
    "Base: revenue grows at current rates. The gap holds near its current level.",
    `Bear: capex cut ${stats.guidance_band_pct}%. Revenue disappoints too. Gap barely moves.`,
    "Revenue falls alongside spending — both sides shrink without closing the gap.",
  ];

  // Accent left-border rule (visual anchor matching the msc-callout style)
  const annotRule = svg.append("line")
    .attr("stroke", ACCENT).attr("stroke-width", 1)
    .attr("opacity", 0).style("pointer-events", "none");

  // Text element — tspans rebuilt per step
  const annotText = svg.append("text")
    .attr("font-family", "'DM Sans', sans-serif")
    .attr("font-size", String(annotFS))
    .attr("fill", INK)
    .attr("opacity", 0).style("pointer-events", "none");

  function showAnnot(step) {
    // On narrow screens the chart is compressed — Bear labels and row data
    // leave no room for an inline annotation. Suppress it; the article prose
    // immediately below the chart provides equivalent context.
    if (W < 440 || step < 0 || step >= ANNOT_TEXTS.length) {
      annotText.interrupt().attr("opacity", 0);
      annotRule.interrupt().attr("opacity", 0);
      return;
    }
    const text = ANNOT_TEXTS[step];
    const y0   = annotY(step);

    // Word-wrap with getComputedTextLength() — works because update() runs in-DOM
    annotText.selectAll("*").remove();
    const words = text.split(/\s+/);
    let line = [], lineNum = 0;
    let tspan = annotText.append("tspan").attr("x", annotX).attr("y", y0);
    for (const word of words) {
      line.push(word);
      tspan.text(line.join(" "));
      if (tspan.node().getComputedTextLength() > annotW && line.length > 1) {
        line.pop();
        tspan.text(line.join(" "));
        line = [word];
        lineNum++;
        tspan = annotText.append("tspan").attr("x", annotX).attr("dy", String(annotLH)).text(word);
      }
    }
    const totalH = lineNum * annotLH + annotFS;
    annotRule
      .attr("x1", annotX - 8).attr("x2", annotX - 8)
      .attr("y1", y0 - annotFS + 2).attr("y2", y0 + totalH - annotFS + 6);
    annotText.interrupt().attr("opacity", 0)
      .transition().delay(250).duration(320).attr("opacity", 1);
    annotRule.interrupt().attr("opacity", 0)
      .transition().delay(250).duration(320).attr("opacity", 0.9);
  }

  // ── Step control ──────────────────────────────────────────────────────────
  function animateRow({ connector, gapBand, revDot, capDot, revLab, capLab, gapLab, ratioLab, revX, capX, gapW }, delay = 0) {
    revDot.interrupt().attr("r", 0)
      .transition().delay(delay).duration(280).ease(d3.easeBackOut.overshoot(1.4)).attr("r", DOT_R);
    connector.interrupt().attr("x2", revX + DOT_R)
      .transition().delay(delay + 160).duration(640).ease(d3.easeQuadOut).attr("x2", capX - DOT_R);
    gapBand.interrupt().attr("width", 0)
      .transition().delay(delay + 160).duration(640).ease(d3.easeQuadOut).attr("width", gapW);
    capDot.interrupt().attr("r", 0)
      .transition().delay(delay + 620).duration(280).ease(d3.easeBackOut.overshoot(1.4)).attr("r", DOT_R);
    revLab.interrupt().attr("opacity", 0)
      .transition().delay(delay + 220).duration(250).attr("opacity", 1);
    capLab.interrupt().attr("opacity", 0)
      .transition().delay(delay + 720).duration(250).attr("opacity", 1);
    gapLab.interrupt().attr("opacity", 0)
      .transition().delay(delay + 820).duration(300).attr("opacity", 1);
    ratioLab.interrupt().attr("opacity", 0)
      .transition().delay(delay + 920).duration(300).attr("opacity", 1);
  }

  function resetRow({ connector, gapBand, revDot, capDot, revLab, capLab, gapLab, ratioLab, revX }) {
    connector.interrupt().attr("x2", revX + DOT_R);
    gapBand.interrupt().attr("width", 0);
    revDot.interrupt().attr("r", 0);
    capDot.interrupt().attr("r", 0);
    [revLab, capLab, gapLab, ratioLab].forEach(el => el.interrupt().attr("opacity", 0));
  }

  function setRowDimmed(row) {
    // Show dots and connector at reduced opacity, no labels
    const { connector, gapBand, revDot, capDot, revLab, capLab, gapLab, ratioLab, revX, capX, gapW } = row;
    revDot.attr("r", DOT_R).attr("opacity", 0.3);
    capDot.attr("r", DOT_R).attr("opacity", 0.3);
    connector.attr("x2", capX - DOT_R).attr("opacity", 0.15);
    gapBand.attr("width", gapW).attr("opacity", 0.04);
    [revLab, capLab, gapLab, ratioLab].forEach(el => el.attr("opacity", 0));
  }

  function setRowFull(row) {
    const { connector, gapBand, revDot, capDot, revLab, capLab, gapLab, ratioLab, capX, gapW } = row;
    revDot.attr("r", DOT_R).attr("opacity", 1);
    capDot.attr("r", DOT_R).attr("opacity", 1);
    connector.attr("x2", capX - DOT_R).attr("opacity", 0.30);
    gapBand.attr("width", gapW).attr("opacity", 0.09);
    revLab.attr("opacity", 1);
    capLab.attr("opacity", 1);
    gapLab.attr("opacity", 1);
    ratioLab.attr("opacity", 1);
  }

  function update(step) {
    if (step === 0) {
      // All rows dimmed — dots and connectors visible but faint, labels hidden
      animEls.forEach(row => {
        resetRow(row);
        // Small delay then show dimmed
        setTimeout(() => setRowDimmed(row), 200);
      });

    } else if (step >= 1 && step <= 3) {
      // Highlight the active row (step 1 = Bull, step 2 = Base, step 3 = Bear)
      const activeIdx = step - 1;
      animEls.forEach((row, i) => {
        if (i === activeIdx) {
          animateRow(row, 0);
          row.revDot.attr("opacity", 1);
          row.capDot.attr("opacity", 1);
        } else {
          setRowDimmed(row);
        }
      });

    } else {
      // step >= 4: all rows at full opacity
      animEls.forEach(row => setRowFull(row));
    }

    showAnnot(step);
  }

  return { node: svg.node(), update };
}
