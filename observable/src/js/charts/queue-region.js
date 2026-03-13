// ── Chart: Queue by Region (horizontal bars) — DD-002 ───────────────────
// Horizontal bar chart of interconnection queue backlog by ISO/RTO.
// PJM and other major DC regions highlighted.
// Steps: 0 = bars grow | 1 = PJM highlight | 2 = all with labels

import * as d3 from "npm:d3@7";
import { INK, INK_LIGHT, ACCENT, CONTEXT, RULE, ISO_COLOR, chartW } from "../design.js";
import { showTip, moveTip, hideTip } from "../tooltip.js";

export function createQueueRegion(queue) {
  const data = queue.region;

  const W = chartW(820);
  const H = Math.max(314, data.length * 38 + 94);
  const ml = 130, mr = 70, mt = 46, mb = 36;

  const x = d3.scaleLinear()
    .domain([0, d3.max(data, d => d.queue_gw) * 1.15])
    .range([ml, W - mr]);
  const y = d3.scaleBand()
    .domain(data.map(d => d.region))
    .range([mt, H - mb]).padding(0.25);

  const svg = d3.create("svg").attr("width", "100%").attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif");

  // ── Title + subtitle ────────────────────────────────────────────────────
  svg.append("text").attr("x", ml).attr("y", 16)
    .attr("fill", INK).attr("font-size", "13").attr("font-weight", "700")
    .text("PJM carries the largest share of the grid connection backlog");
  svg.append("text").attr("x", ml).attr("y", 30)
    .attr("fill", INK_LIGHT).attr("font-size", "10.5")
    .text("Interconnection queue by ISO/RTO (GW) · orange = data center concentration zones");

  // X axis
  svg.append("line").attr("x1", ml).attr("x2", W - mr)
    .attr("y1", H - mb).attr("y2", H - mb).attr("stroke", RULE);

  // Bars
  const bars = data.map(d => {
    const color = d.is_dc_region ? ACCENT : (ISO_COLOR[d.region] || CONTEXT);

    const rect = svg.append("rect")
      .attr("x", ml).attr("y", y(d.region)).attr("width", 0)
      .attr("height", y.bandwidth())
      .attr("fill", color).attr("rx", 2).attr("opacity", 0.85);

    // Value label
    const label = svg.append("text")
      .attr("x", ml).attr("y", y(d.region) + y.bandwidth() / 2 + 4)
      .attr("fill", INK).attr("font-size", "11").attr("font-weight", "600")
      .attr("opacity", 0).text(`${d.queue_gw} GW`);

    // Y label
    svg.append("text")
      .attr("x", ml - 8).attr("y", y(d.region) + y.bandwidth() / 2 + 4)
      .attr("text-anchor", "end").attr("fill", INK_LIGHT).attr("font-size", "12")
      .text(d.region);

    // Hit target
    svg.append("rect")
      .attr("x", 0).attr("y", y(d.region)).attr("width", W).attr("height", y.bandwidth())
      .attr("fill", "transparent").style("cursor", "crosshair")
      .on("mouseover", (e) => {
        rect.attr("opacity", 1);
        showTip(e, d.region, `Queue backlog: ${d.queue_gw} GW`,
          d.is_dc_region ? "Major data center region" : "");
      })
      .on("mousemove", moveTip)
      .on("mouseout", () => { rect.attr("opacity", 0.85); hideTip(); });

    return { rect, label, d };
  });

  // Source
  svg.append("text").attr("x", ml).attr("y", H - 3)
    .attr("fill", CONTEXT).attr("font-size", "9")
    .text("Source: LBNL 'Queued Up' 2025 Edition");

  // ── Step control ────────────────────────────────────────────────────────
  function update(step) {
    if (step === 0) {
      bars.forEach((b, i) => {
        b.rect.transition().delay(i * 40).duration(600).ease(d3.easeQuadOut)
          .attr("width", x(b.d.queue_gw) - ml);
        b.label.attr("opacity", 0);
      });
    } else if (step === 1) {
      bars.forEach(b => {
        const isPJM = b.d.region === "PJM";
        b.rect.transition().duration(300)
          .attr("width", x(b.d.queue_gw) - ml)
          .attr("opacity", isPJM ? 1 : 0.2);
        b.label.transition().duration(300)
          .attr("x", x(b.d.queue_gw) + 6)
          .attr("opacity", isPJM ? 1 : 0);
      });
    } else {
      bars.forEach((b, i) => {
        b.rect.transition().duration(300)
          .attr("width", x(b.d.queue_gw) - ml)
          .attr("opacity", 0.85);
        b.label.transition().delay(i * 30).duration(300)
          .attr("x", x(b.d.queue_gw) + 6)
          .attr("opacity", 1);
      });
    }
  }

  return { node: svg.node(), update };
}
