// ── Capital Intensity: Investment per permanent job ──────────────────────────
// Horizontal bars with progressive reveal. Data center at top, 55x annotation.

import * as d3 from "npm:d3@7";
import { INK, INK_LIGHT, ACCENT, CONTEXT, RULE } from "../design.js";
import { showTip, moveTip, hideTip } from "../tooltip.js";

export function createCapitalIntensity() {
  const W = Math.min(820, (document.body?.clientWidth ?? 820) - 40);
  const H = 294;
  const ml = 140, mr = 80, mt = 52, mb = 44;

  const industries = [
    { label: "Hyperscale Data Center", value: 5.0, focus: true },
    { label: "Semiconductor Fab", value: 2.8, focus: false },
    { label: "EV Assembly Plant", value: 0.60, focus: false },
    { label: "Conventional Auto", value: 0.25, focus: false },
    { label: "Warehouse / Distribution", value: 0.09, focus: false },
  ];

  const x = d3.scaleLinear().domain([0, 6.5]).range([ml, W - mr]);
  const y = d3.scaleBand().domain(industries.map((_, i) => i)).range([mt, H - mb]).padding(0.3);

  const svg = d3.create("svg")
    .attr("width", "100%")
    .attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif");

  // ── Title + subtitle ────────────────────────────────────────────────────
  svg.append("text").attr("x", ml).attr("y", 16)
    .attr("fill", INK).attr("font-size", "13").attr("font-weight", "700")
    .text("A data center creates 55× more investment per job than a warehouse");
  svg.append("text").attr("x", ml).attr("y", 30)
    .attr("fill", INK_LIGHT).attr("font-size", "10.5")
    .text("Capital investment per permanent job created ($M) · selected industries");

  // X axis
  svg.append("g")
    .attr("transform", `translate(0,${H - mb})`)
    .call(d3.axisBottom(x).ticks(5).tickSize(0))
    .call(g => g.select(".domain").attr("stroke", RULE))
    .call(g => g.selectAll("text").attr("fill", INK_LIGHT).attr("font-size", 11));

  svg.append("text")
    .attr("x", (ml + W - mr) / 2).attr("y", H - 6)
    .attr("text-anchor", "middle").attr("fill", INK_LIGHT).attr("font-size", 11)
    .text("Capital Investment per Permanent Job ($M)");

  // Bars
  const barGroups = svg.selectAll("g.bar")
    .data(industries).join("g").attr("class", "bar");

  barGroups.append("rect")
    .attr("x", ml)
    .attr("y", (_, i) => y(i))
    .attr("width", d => x(d.value) - ml)
    .attr("height", y.bandwidth())
    .attr("fill", d => d.focus ? ACCENT : CONTEXT)
    .attr("rx", 2);

  // Y labels
  barGroups.append("text")
    .attr("x", ml - 8)
    .attr("y", (_, i) => y(i) + y.bandwidth() / 2)
    .attr("text-anchor", "end").attr("dominant-baseline", "central")
    .attr("fill", INK).attr("font-size", 11)
    .text(d => d.label);

  // Value labels
  barGroups.append("text")
    .attr("x", d => x(d.value) + 5)
    .attr("y", (_, i) => y(i) + y.bandwidth() / 2)
    .attr("dominant-baseline", "central")
    .attr("fill", d => d.focus ? ACCENT : INK_LIGHT)
    .attr("font-size", 11)
    .attr("font-weight", d => d.focus ? 600 : 400)
    .text(d => `$${d.value.toFixed(2)}M`);

  // 55x annotation
  const annotation = svg.append("g").attr("opacity", 0);
  const dcY = y(0) + y.bandwidth() / 2;
  const whY = y(4) + y.bandwidth() / 2;
  annotation.append("line")
    .attr("x1", x(5.0) + 40).attr("x2", x(5.0) + 40)
    .attr("y1", dcY).attr("y2", whY)
    .attr("stroke", ACCENT).attr("stroke-width", 1.5);
  annotation.append("text")
    .attr("x", x(5.0) + 48).attr("y", (dcY + whY) / 2 + 4)
    .attr("fill", ACCENT).attr("font-size", 13).attr("font-weight", 700)
    .text("55x");

  // Hit targets
  barGroups.append("rect")
    .attr("x", ml)
    .attr("y", (_, i) => y(i))
    .attr("width", d => Math.max(x(d.value) - ml, 30))
    .attr("height", y.bandwidth())
    .attr("fill", "transparent")
    .style("cursor", "crosshair")
    .on("mouseover", (e, d) => {
      showTip(e, d.label, `$${d.value.toFixed(2)}M per permanent job`);
    })
    .on("mousemove", moveTip)
    .on("mouseout", hideTip);

  // Source
  svg.append("text")
    .attr("x", ml).attr("y", H - 3)
    .attr("fill", CONTEXT).attr("font-size", 9)
    .text("Source: JLARC Report 598 (2024); TSMC filings; BLS industry data");

  function update(step) {
    const t = svg.transition().duration(400);
    annotation.transition(t).attr("opacity", step >= 1 ? 1 : 0);
  }

  return { node: svg.node(), update };
}
