// ── PJM Zone Demand: Small multiples sparkline grid ──────────────────────────
// One sparkline per PJM zone. AEP and DOM highlighted in accent colors.
// Replaces Altair interactive legend selection with immediate visual comparison.

import * as d3 from "../../../_npm/d3@7.9.0/e324157d.js";
import { INK, INK_LIGHT, ACCENT, CONTEXT, RULE, DOM_ZONE, AEP_ZONE, chartW } from "../design.2d3db129.js";
import { showTip, moveTip, hideTip } from "../tooltip.40aee997.js";

export function createPjmDemand(data) {
  const W = chartW(820);

  // Group by zone, exclude PJM RTO (aggregate)
  const byZone = d3.group(data.filter(d => d.zone !== "PJM RTO"), d => d.zone);
  const zones = [...byZone.keys()].sort((a, b) => {
    // Sort by 2030 demand descending
    const a2030 = byZone.get(a)?.find(d => d.year === 2030)?.mw ?? 0;
    const b2030 = byZone.get(b)?.find(d => d.year === 2030)?.mw ?? 0;
    return b2030 - a2030;
  });

  const nCols = 4;
  const nRows = Math.ceil(zones.length / nCols);
  const cellW = (W - 20) / nCols;
  const cellH = 80;
  const H = nRows * cellH + 94;

  const svg = d3.create("svg")
    .attr("width", "100%")
    .attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif");

  // ── Title + subtitle ────────────────────────────────────────────────────
  svg.append("text").attr("x", 10).attr("y", 16)
    .attr("fill", INK).attr("font-size", "13").attr("font-weight", "700")
    .text("AEP and DOM zones face the sharpest demand growth from AI load");
  svg.append("text").attr("x", 10).attr("y", 30)
    .attr("fill", INK_LIGHT).attr("font-size", "10.5")
    .text("PJM zone demand requests 2026–2046 (MW) · AEP = Indiana/Ohio · DOM = Virginia");

  const yearExtent = d3.extent(data, d => d.year);
  const mwMax = d3.max(data.filter(d => d.zone !== "PJM RTO"), d => d.mw) || 1;

  zones.forEach((zone, idx) => {
    const col = idx % nCols;
    const row = Math.floor(idx / nCols);
    const gx = 10 + col * cellW;
    const gy = 44 + row * cellH;

    const g = svg.append("g").attr("transform", `translate(${gx},${gy})`);

    const series = byZone.get(zone) || [];
    const isHighlight = zone === "AEP" || zone === "DOM";
    const color = zone === "AEP" ? AEP_ZONE : zone === "DOM" ? DOM_ZONE : CONTEXT;

    const xScale = d3.scaleLinear().domain(yearExtent).range([4, cellW - 20]);
    const yScale = d3.scaleLinear().domain([0, mwMax]).range([cellH - 22, 8]);

    // Zone label
    g.append("text")
      .attr("x", 4).attr("y", 6)
      .attr("fill", isHighlight ? color : INK_LIGHT)
      .attr("font-size", 10)
      .attr("font-weight", isHighlight ? 600 : 400)
      .text(zone);

    // Sparkline
    const line = d3.line()
      .x(d => xScale(d.year))
      .y(d => yScale(d.mw));

    g.append("path")
      .datum(series)
      .attr("d", line)
      .attr("fill", "none")
      .attr("stroke", color)
      .attr("stroke-width", isHighlight ? 2 : 1.2)
      .attr("opacity", isHighlight ? 1 : 0.6);

    // End dot
    const last = series[series.length - 1];
    if (last) {
      g.append("circle")
        .attr("cx", xScale(last.year)).attr("cy", yScale(last.mw))
        .attr("r", 2.5).attr("fill", color);
    }

    // 2030 value label if significant
    const val2030 = series.find(d => d.year === 2030);
    if (val2030 && val2030.mw > 100) {
      g.append("text")
        .attr("x", xScale(2030) + 4).attr("y", yScale(val2030.mw) + 3)
        .attr("fill", isHighlight ? color : INK_LIGHT)
        .attr("font-size", 9)
        .text(`${(val2030.mw / 1000).toFixed(1)} GW`);
    }

    // Hit target for whole cell
    g.append("rect")
      .attr("width", cellW - 10).attr("height", cellH - 6)
      .attr("fill", "transparent")
      .style("cursor", "crosshair")
      .on("mouseover", (e) => {
        const vals = series.map(d => `${d.year}: ${d.mw.toLocaleString()} MW`).join("\n");
        showTip(e, zone, vals);
      })
      .on("mousemove", moveTip)
      .on("mouseout", hideTip);
  });

  // Source
  svg.append("text")
    .attr("x", 10).attr("y", H - 4)
    .attr("fill", CONTEXT).attr("font-size", 9)
    .text("Source: PJM LAS Large Load Adjustment Requests (Sep 2025); submitted by EDC/LSE, not final PJM-accepted");

  function update(step) {
    // No progressive reveal needed — the small multiples are self-explanatory
    // But we can highlight AEP/DOM on step 1
  }

  return { node: svg.node(), update };
}
