// ── Regulatory Timeline: Horizontal timeline with jurisdiction-colored events ─
// Events as circles, sized by significance, colored by jurisdiction.
// FERC = blue, IURC = accent, PJM = green.

import * as d3 from "npm:d3@7";
import { INK, INK_LIGHT, ACCENT, CONTEXT, RULE, ISO_COLOR, chartW } from "../design.js";
import { showTip, moveTip, hideTip } from "../tooltip.js";

const JURISDICTION_COLORS = {
  "FERC": ISO_COLOR.PJM,      // blue — federal regulator
  "IURC": ACCENT,             // accent — state regulator (focus)
  "PJM":  ISO_COLOR.ERCOT,    // green — grid operator
  "State": ISO_COLOR.CAISO,   // yellow — other state actions
};

export function createRegulatoryTimeline(events) {
  const W = chartW(820);
  const H = 280;
  const ml = 40, mr = 40, mt = 40, mb = 50;

  const parseDate = d3.timeParse("%Y-%m-%d");
  const evts = events.map(d => ({
    ...d,
    dateObj: parseDate(d.date),
  })).filter(d => d.dateObj != null).sort((a, b) => a.dateObj - b.dateObj);

  const x = d3.scaleTime()
    .domain(d3.extent(evts, d => d.dateObj))
    .range([ml, W - mr]);

  const svg = d3.create("svg")
    .attr("width", "100%")
    .attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif");

  // ── Title + subtitle ────────────────────────────────────────────────────
  svg.append("text").attr("x", ml).attr("y", 16)
    .attr("fill", INK).attr("font-size", "13").attr("font-weight", "700")
    .text("The regulatory landscape is moving. Outcomes determine who pays.");
  svg.append("text").attr("x", ml).attr("y", 30)
    .attr("fill", INK_LIGHT).attr("font-size", "10.5")
    .text("FERC · IURC · PJM decisions on grid cost allocation, 2023–2026");

  // Timeline axis
  const midY = H / 2 + 10;
  svg.append("line")
    .attr("x1", ml).attr("x2", W - mr)
    .attr("y1", midY).attr("y2", midY)
    .attr("stroke", RULE).attr("stroke-width", 1.5);

  // Year ticks
  svg.append("g")
    .attr("transform", `translate(0,${midY})`)
    .call(d3.axisBottom(x).ticks(d3.timeYear.every(1)).tickSize(6).tickFormat(d3.timeFormat("%Y")))
    .call(g => g.select(".domain").remove())
    .call(g => g.selectAll("text").attr("fill", INK_LIGHT).attr("font-size", 10));

  // Event circles
  // Stagger vertically to avoid overlap
  evts.forEach((evt, i) => {
    const above = i % 2 === 0;
    const cy = above ? midY - 30 - (i % 3) * 16 : midY + 30 + (i % 3) * 16;
    const cx = x(evt.dateObj);
    const color = JURISDICTION_COLORS[evt.jurisdiction] ?? CONTEXT;

    // Stem line
    svg.append("line")
      .attr("x1", cx).attr("x2", cx)
      .attr("y1", midY).attr("y2", cy)
      .attr("stroke", RULE).attr("stroke-width", 0.8);

    // Visible circle
    svg.append("circle")
      .attr("cx", cx).attr("cy", cy)
      .attr("r", evt.status === "final_order" ? 6 : evt.status === "policy_statement" ? 5 : 4)
      .attr("fill", color).attr("fill-opacity", 0.8)
      .attr("stroke", "white").attr("stroke-width", 0.8);

    // Short label
    const labelText = evt.name.length > 30 ? evt.name.slice(0, 28) + "\u2026" : evt.name;
    svg.append("text")
      .attr("x", cx)
      .attr("y", above ? cy - 10 : cy + 14)
      .attr("text-anchor", "middle")
      .attr("fill", INK_LIGHT).attr("font-size", 9)
      .text(labelText);

    // Hit target
    svg.append("circle")
      .attr("cx", cx).attr("cy", cy)
      .attr("r", 12).attr("fill", "transparent")
      .style("cursor", "crosshair")
      .on("mouseover", (e) => {
        showTip(e, evt.name,
          `${evt.jurisdiction} \u00b7 ${evt.docket}`,
          evt.description || "",
          `Date: ${evt.date}`
        );
      })
      .on("mousemove", moveTip)
      .on("mouseout", hideTip);
  });

  // Jurisdiction legend
  const legendG = svg.append("g").attr("transform", `translate(${ml}, ${mt - 20})`);
  Object.entries(JURISDICTION_COLORS).forEach(([key, color], i) => {
    legendG.append("circle")
      .attr("cx", i * 70).attr("cy", 0)
      .attr("r", 5).attr("fill", color).attr("fill-opacity", 0.8);
    legendG.append("text")
      .attr("x", i * 70 + 10).attr("y", 4)
      .attr("fill", INK_LIGHT).attr("font-size", 10)
      .text(key);
  });

  // Source
  svg.append("text")
    .attr("x", ml).attr("y", H - 4)
    .attr("fill", CONTEXT).attr("font-size", 9)
    .text("Source: FERC docket filings; IURC final orders; PJM committee minutes");

  function update(step) {
    // Timeline is static — no progressive reveal needed
  }

  return { node: svg.node(), update };
}
