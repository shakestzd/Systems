// ── Chart: Cost Allocation Waterfall — DD-002 ───────────────────────────
// Waterfall chart showing $4.36B in PJM grid costs socialized to ratepayers.
// Steps: 0 = bars build sequentially | 1 = connector lines | 2 = total bar

import * as d3 from "../../../_npm/d3@7.9.0/e324157d.js";
import { INK, INK_LIGHT, ACCENT, CONTEXT, RULE, chartW } from "../design.2d3db129.js";
import { showTip, moveTip, hideTip } from "../tooltip.40aee997.js";

export function createCostWaterfall(queue) {
  const items = queue.waterfall.filter(d => !d.is_total);
  const total = queue.waterfall.find(d => d.is_total);

  const W = chartW(820);
  const H = 354;
  const ml = 48, mr = 20, mt = 52, mb = 60;

  // Build cumulative positions
  let running = 0;
  const bars = items.map(d => {
    const start = running;
    running += d.cost_bn;
    return { ...d, start, end: running };
  });

  const allLabels = items.map(d => d.category.replace(/ /g, "\n"));
  allLabels.push("Total\nsocialized");

  const x = d3.scaleBand().domain(allLabels).range([ml, W - mr]).padding(0.3);
  const yMax = running * 1.2;
  const y = d3.scaleLinear().domain([0, yMax]).range([H - mb, mt]);

  const svg = d3.create("svg").attr("width", "100%").attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif");

  // ── Title + subtitle ────────────────────────────────────────────────────
  svg.append("text").attr("x", ml).attr("y", 16)
    .attr("fill", INK).attr("font-size", "13").attr("font-weight", "700")
    .text("Grid upgrade costs are socialized across all ratepayers");
  svg.append("text").attr("x", ml).attr("y", 30)
    .attr("fill", INK_LIGHT).attr("font-size", "10.5")
    .text("Annual PJM transmission cost components recovered from ratepayers ($B)");

  // X axis baseline
  svg.append("line").attr("x1", ml).attr("x2", W - mr)
    .attr("y1", H - mb).attr("y2", H - mb).attr("stroke", RULE);

  // Y axis
  const yTicks = y.ticks(5);
  yTicks.forEach(v => {
    svg.append("text").attr("x", ml - 6).attr("y", y(v) + 4)
      .attr("text-anchor", "end").attr("fill", INK_LIGHT).attr("font-size", "10")
      .text(`$${v.toFixed(1)}B`);
    if (v > 0) {
      svg.append("line").attr("x1", ml).attr("x2", W - mr)
        .attr("y1", y(v)).attr("y2", y(v))
        .attr("stroke", RULE).attr("stroke-width", 0.5).attr("opacity", 0.3);
    }
  });

  // X axis labels
  allLabels.forEach(lbl => {
    svg.append("text")
      .attr("x", x(lbl) + x.bandwidth() / 2).attr("y", H - mb + 10)
      .attr("text-anchor", "middle").attr("fill", INK_LIGHT).attr("font-size", "10")
      .selectAll("tspan")
      .data(lbl.split("\n"))
      .join("tspan")
        .attr("x", x(lbl) + x.bandwidth() / 2)
        .attr("dy", (_, i) => i === 0 ? 0 : 12)
        .text(d => d);
  });

  // Incremental bars — start at height 0
  const waterfallBars = bars.map((d, i) => {
    const lbl = allLabels[i];
    const bx = x(lbl);
    const bw = x.bandwidth();

    const rect = svg.append("rect")
      .attr("x", bx).attr("y", y(d.end)).attr("width", bw).attr("height", 0)
      .attr("fill", ACCENT).attr("rx", 2).attr("opacity", 0.85);

    const valLabel = svg.append("text")
      .attr("x", bx + bw / 2).attr("y", y(d.end) - 6)
      .attr("text-anchor", "middle").attr("fill", INK).attr("font-size", "11")
      .attr("font-weight", "600").attr("opacity", 0)
      .text(`$${d.cost_bn.toFixed(2)}B`);

    // Tooltip hit target
    svg.append("rect")
      .attr("x", bx).attr("y", mt).attr("width", bw).attr("height", H - mt - mb)
      .attr("fill", "transparent").style("cursor", "crosshair")
      .on("mouseover", (e) => showTip(e, d.category, `$${d.cost_bn.toFixed(2)}B`))
      .on("mousemove", moveTip)
      .on("mouseout", hideTip);

    return { rect, valLabel, d };
  });

  // Connector lines between bars
  const connectors = bars.slice(0, -1).map((d, i) => {
    const lbl1 = allLabels[i], lbl2 = allLabels[i + 1];
    return svg.append("line")
      .attr("x1", x(lbl1) + x.bandwidth()).attr("x2", x(lbl2))
      .attr("y1", y(d.end)).attr("y2", y(d.end))
      .attr("stroke", INK_LIGHT).attr("stroke-dasharray", "3,2")
      .attr("stroke-width", 1).attr("opacity", 0);
  });

  // Total bar — different color
  const totalLbl = "Total\nsocialized";
  const totalRect = svg.append("rect")
    .attr("x", x(totalLbl)).attr("y", y(running)).attr("width", x.bandwidth())
    .attr("height", 0).attr("fill", INK).attr("rx", 2).attr("opacity", 0);

  const totalValLabel = svg.append("text")
    .attr("x", x(totalLbl) + x.bandwidth() / 2).attr("y", y(running) - 6)
    .attr("text-anchor", "middle").attr("fill", INK).attr("font-size", "12")
    .attr("font-weight", "700").attr("opacity", 0)
    .text(`$${total ? total.cost_bn.toFixed(2) : running.toFixed(2)}B`);

  // Source
  svg.append("text").attr("x", ml).attr("y", H - 3)
    .attr("fill", CONTEXT).attr("font-size", "9")
    .text("Source: UCS, 'Data Center Demand and the Grid' (September 2025)");

  // ── Step control ────────────────────────────────────────────────────────
  function update(step) {
    // Step 0: bars build sequentially
    waterfallBars.forEach((b, i) => {
      const targetH = y(b.d.start) - y(b.d.end);
      if (step >= 0) {
        b.rect.transition().delay(i * 150).duration(500).ease(d3.easeQuadOut)
          .attr("height", targetH);
        b.valLabel.transition().delay(i * 150 + 400).duration(300).attr("opacity", 1);
      }
    });

    // Step 1: connector lines
    connectors.forEach((c, i) => {
      c.transition().delay(step >= 1 ? i * 100 : 0).duration(300)
        .attr("opacity", step >= 1 ? 0.6 : 0);
    });

    // Step 2: total bar
    const totalH = y(0) - y(running);
    totalRect.transition().delay(step >= 2 ? 200 : 0).duration(500)
      .attr("height", step >= 2 ? totalH : 0)
      .attr("opacity", step >= 2 ? 0.85 : 0);
    totalValLabel.transition().delay(step >= 2 ? 600 : 0).duration(300)
      .attr("opacity", step >= 2 ? 1 : 0);
  }

  return { node: svg.node(), update };
}
