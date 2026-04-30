// ── Chart: Virginia Bill Impact (line + fill) — DD-002 ──────────────────
// Projection of residential electricity bill increase under high DC growth.
// Steps: 0 = line draws | 1 = reference line | 2 = endpoint annotation

import * as d3 from "../../../_npm/d3@7.9.0/e324157d.js";
import { INK, INK_LIGHT, ACCENT, CONTEXT, RULE, PAPER, chartW } from "../design.2d3db129.js";
import { showTip, moveTip, hideTip } from "../tooltip.40aee997.js";

export function createVirginiaBills(stats) {
  const endpoint = stats.va_bill_annual;
  const years = d3.range(2024, 2041);
  // t^1.5 trajectory (matches Marimo notebook)
  const data = years.map(yr => ({
    year: yr,
    bill: endpoint * Math.pow((yr - 2024) / (2040 - 2024), 1.5),
  }));

  const W = chartW(820);
  const H = 334;
  const ml = 52, mr = 24, mt = 52, mb = 44;

  const x = d3.scaleLinear().domain([2024, 2040]).range([ml, W - mr]);
  const y = d3.scaleLinear().domain([0, 520]).range([H - mb, mt]);

  const svg = d3.create("svg").attr("width", "100%").attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif");

  // ── Title + subtitle ────────────────────────────────────────────────────
  svg.append("text").attr("x", ml).attr("y", 16)
    .attr("fill", INK).attr("font-size", "13").attr("font-weight", "700")
    .text("Grid upgrade costs could add hundreds to annual Virginia electricity bills");
  svg.append("text").attr("x", ml).attr("y", 30)
    .attr("fill", INK_LIGHT).attr("font-size", "10.5")
    .text("Projected residential bill increase under high data center growth scenario, 2024–2040 ($)");

  // X axis
  svg.append("line").attr("x1", ml).attr("x2", W - mr)
    .attr("y1", H - mb).attr("y2", H - mb).attr("stroke", RULE);

  d3.range(2024, 2042, 4).forEach(yr => {
    svg.append("text").attr("x", x(yr)).attr("y", H - mb + 14)
      .attr("text-anchor", "middle").attr("fill", INK_LIGHT).attr("font-size", "10")
      .text(yr);
  });

  // Y axis
  [0, 100, 200, 300, 400, 500].forEach(v => {
    svg.append("text").attr("x", ml - 6).attr("y", y(v) + 4)
      .attr("text-anchor", "end").attr("fill", INK_LIGHT).attr("font-size", "10")
      .text(`$${v}`);
    if (v > 0) {
      svg.append("line").attr("x1", ml).attr("x2", W - mr)
        .attr("y1", y(v)).attr("y2", y(v))
        .attr("stroke", RULE).attr("stroke-width", 0.5).attr("opacity", 0.3);
    }
  });

  // Area fill
  const area = d3.area()
    .x(d => x(d.year)).y0(y(0)).y1(d => y(d.bill));

  const areaPath = svg.append("path")
    .datum(data).attr("d", area)
    .attr("fill", ACCENT).attr("opacity", 0);

  // Line
  const line = d3.line().x(d => x(d.year)).y(d => y(d.bill));
  const linePath = svg.append("path")
    .datum(data).attr("d", line)
    .attr("fill", "none").attr("stroke", ACCENT).attr("stroke-width", 2.5)
    .attr("stroke-dasharray", function() { return this.getTotalLength() + "," + this.getTotalLength(); })
    .attr("stroke-dashoffset", function() { return this.getTotalLength(); });

  // 10% reference line
  const refY = stats.avg_bill_10pct;
  const refLine = svg.append("line")
    .attr("x1", ml).attr("x2", W - mr)
    .attr("y1", y(refY)).attr("y2", y(refY))
    .attr("stroke", CONTEXT).attr("stroke-dasharray", "6,3").attr("stroke-width", 1)
    .attr("opacity", 0);

  const refLabel = svg.append("text")
    .attr("x", ml + 4).attr("y", y(refY) - 6)
    .attr("fill", INK_LIGHT).attr("font-size", "10")
    .attr("opacity", 0)
    .text(`~10% of avg U.S. bill (~$${stats.avg_monthly_bill}/mo)`);

  // Endpoint annotation
  const endAnnotation = svg.append("g").attr("opacity", 0);
  endAnnotation.append("circle")
    .attr("cx", x(2040)).attr("cy", y(endpoint)).attr("r", 4)
    .attr("fill", ACCENT);
  endAnnotation.append("text")
    .attr("x", x(2040) - 10).attr("y", y(endpoint) - 14)
    .attr("text-anchor", "end").attr("fill", ACCENT).attr("font-size", "12")
    .attr("font-weight", "700")
    .text(`$${endpoint}/yr ($${stats.va_bill_monthly}/mo)`);

  // Tooltip dots along line
  data.filter(d => d.year % 2 === 0).forEach(d => {
    svg.append("circle")
      .attr("cx", x(d.year)).attr("cy", y(d.bill)).attr("r", 12)
      .attr("fill", "transparent").style("cursor", "crosshair")
      .on("mouseover", (e) => showTip(e, String(d.year), `+$${d.bill.toFixed(0)}/year`))
      .on("mousemove", moveTip)
      .on("mouseout", hideTip);
  });

  // Source
  svg.append("text").attr("x", ml).attr("y", H - 3)
    .attr("fill", CONTEXT).attr("font-size", "9")
    .text("Source: JLARC/E3 December 2024; projection model");

  // Y axis label
  svg.append("text")
    .attr("transform", `rotate(-90)`).attr("x", -(mt + (H - mb - mt) / 2)).attr("y", 14)
    .attr("text-anchor", "middle").attr("fill", INK_LIGHT).attr("font-size", "10")
    .text("Annual bill increase ($)");

  // ── Step control ────────────────────────────────────────────────────────
  function update(step) {
    // Step 0: line draws
    const totalLen = linePath.node().getTotalLength();
    if (step >= 0) {
      linePath.transition().duration(1200).ease(d3.easeLinear)
        .attr("stroke-dashoffset", 0);
      areaPath.transition().delay(600).duration(600).attr("opacity", 0.15);
    }

    // Step 1: reference line
    refLine.transition().duration(300).attr("opacity", step >= 1 ? 0.7 : 0);
    refLabel.transition().duration(300).attr("opacity", step >= 1 ? 1 : 0);

    // Step 2: endpoint
    endAnnotation.transition().duration(300).attr("opacity", step >= 2 ? 1 : 0);
  }

  return { node: svg.node(), update };
}
