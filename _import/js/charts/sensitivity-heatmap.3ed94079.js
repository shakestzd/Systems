// ── Chart: Sensitivity Heatmap — DD-002 ─────────────────────────────────
// BTM cost advantage x Regulatory favorability -> spillover index at 2035.
// Interactive: hover shows crosshair + exact value. "Current estimate" marker.
// Steps: 0 = heatmap appears | 1 = 0.5 threshold line | 2 = regime labels +
//        current estimate marker

import * as d3 from "../../../_npm/d3@7.9.0/e324157d.js";
import { INK, INK_LIGHT, ACCENT, CONTEXT, RULE, PAPER, chartW } from "../design.2d3db129.js";
import { showTip, moveTip, hideTip } from "../tooltip.40aee997.js";

export function createSensitivityHeatmap(sim) {
  const { btm_range, reg_range, spillover } = sim.sensitivity;

  const W = chartW(820);
  const H = 474;
  const ml = 60, mr = 80, mt = 52, mb = 50;

  const x = d3.scaleBand().domain(btm_range).range([ml, W - mr]).padding(0.02);
  const y = d3.scaleBand().domain([...reg_range].reverse()).range([mt, H - mb]).padding(0.02);

  // Color scale: red (low spillover) to green (high spillover)
  const color = d3.scaleSequential(d3.interpolateRdYlGn).domain([0.3, 1.0]);

  const svg = d3.create("svg").attr("width", "100%").attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif");

  // ── Title + subtitle ────────────────────────────────────────────────────
  svg.append("text").attr("x", ml).attr("y", 16)
    .attr("fill", INK).attr("font-size", "13").attr("font-weight", "700")
    .text("Ratepayer spillover depends on two variables regulators control");
  svg.append("text").attr("x", ml).attr("y", 30)
    .attr("fill", INK_LIGHT).attr("font-size", "10.5")
    .text("Behind-the-meter cost advantage (x) × regulatory favorability (y) → spillover index at 2035");

  // Heatmap cells — start invisible
  const cells = [];
  reg_range.forEach((reg, ri) => {
    btm_range.forEach((btm, bi) => {
      const val = spillover[ri][bi];
      const rect = svg.append("rect")
        .attr("x", x(btm)).attr("y", y(reg))
        .attr("width", x.bandwidth()).attr("height", y.bandwidth())
        .attr("fill", color(val)).attr("opacity", 0)
        .attr("rx", 1);

      // Hit target for tooltip
      svg.append("rect")
        .attr("x", x(btm)).attr("y", y(reg))
        .attr("width", x.bandwidth()).attr("height", y.bandwidth())
        .attr("fill", "transparent").style("cursor", "crosshair")
        .on("mouseover", (e) => {
          showTip(e, `Spillover: ${val.toFixed(2)}`,
            `BTM cost: ${btm.toFixed(1)}`,
            `Reg. favorability: ${reg.toFixed(2)}`);
        })
        .on("mousemove", moveTip)
        .on("mouseout", hideTip);

      cells.push(rect);
    });
  });

  // X axis
  svg.append("line").attr("x1", ml).attr("x2", W - mr)
    .attr("y1", H - mb).attr("y2", H - mb).attr("stroke", RULE);

  btm_range.filter((_, i) => i % 3 === 0).forEach(v => {
    svg.append("text").attr("x", x(v) + x.bandwidth() / 2).attr("y", H - mb + 14)
      .attr("text-anchor", "middle").attr("fill", INK_LIGHT).attr("font-size", "10")
      .text(v.toFixed(1));
  });

  svg.append("text")
    .attr("x", (ml + W - mr) / 2).attr("y", H - mb + 30)
    .attr("text-anchor", "middle").attr("fill", INK_LIGHT).attr("font-size", "11")
    .text("BTM Cost Advantage");

  // Y axis
  reg_range.filter((_, i) => i % 4 === 0).forEach(v => {
    svg.append("text").attr("x", ml - 6).attr("y", y(v) + y.bandwidth() / 2 + 3)
      .attr("text-anchor", "end").attr("fill", INK_LIGHT).attr("font-size", "10")
      .text(v.toFixed(1));
  });

  svg.append("text")
    .attr("transform", "rotate(-90)").attr("x", -(mt + (H - mb - mt) / 2)).attr("y", 14)
    .attr("text-anchor", "middle").attr("fill", INK_LIGHT).attr("font-size", "11")
    .text("Regulatory Favorability");

  // Color legend (vertical bar)
  const legendW = 14, legendH = H - mt - mb;
  const legendX = W - mr + 20;
  const defs = svg.append("defs");
  const gradient = defs.append("linearGradient")
    .attr("id", "spill-grad").attr("x1", 0).attr("y1", 1).attr("x2", 0).attr("y2", 0);
  gradient.append("stop").attr("offset", "0%").attr("stop-color", color(0.3));
  gradient.append("stop").attr("offset", "50%").attr("stop-color", color(0.65));
  gradient.append("stop").attr("offset", "100%").attr("stop-color", color(1.0));

  svg.append("rect").attr("x", legendX).attr("y", mt).attr("width", legendW)
    .attr("height", legendH).attr("fill", "url(#spill-grad)").attr("rx", 2);

  [1.0, 0.7, 0.5, 0.3].forEach(v => {
    const ly = mt + (1 - (v - 0.3) / 0.7) * legendH;
    svg.append("text").attr("x", legendX + legendW + 6).attr("y", ly + 3)
      .attr("fill", INK_LIGHT).attr("font-size", "9").text(v.toFixed(1));
  });

  svg.append("text").attr("x", legendX + legendW / 2).attr("y", mt - 6)
    .attr("text-anchor", "middle").attr("fill", INK_LIGHT).attr("font-size", "9")
    .text("Spillover");

  // 0.5 threshold contour approximation — horizontal line where spillover = 0.5
  // Find the boundary by checking each column
  const thresholdLine = svg.append("path")
    .attr("fill", "none").attr("stroke", INK).attr("stroke-width", 2)
    .attr("stroke-dasharray", "6,3").attr("opacity", 0);

  const thresholdPoints = [];
  btm_range.forEach((btm, bi) => {
    for (let ri = 0; ri < reg_range.length - 1; ri++) {
      const v1 = spillover[ri][bi], v2 = spillover[ri + 1][bi];
      if ((v1 >= 0.5 && v2 < 0.5) || (v1 < 0.5 && v2 >= 0.5)) {
        const frac = (0.5 - v1) / (v2 - v1);
        const regVal = reg_range[ri] + frac * (reg_range[ri + 1] - reg_range[ri]);
        thresholdPoints.push([
          x(btm) + x.bandwidth() / 2,
          y(reg_range[ri]) + y.bandwidth() * frac,
        ]);
        break;
      }
    }
  });

  if (thresholdPoints.length > 1) {
    const lineGen = d3.line().curve(d3.curveMonotoneX);
    thresholdLine.attr("d", lineGen(thresholdPoints));
  }

  // Regime labels
  const gridLabel = svg.append("text")
    .attr("x", x(btm_range[2]) + x.bandwidth() / 2)
    .attr("y", y(reg_range[reg_range.length - 3]) + y.bandwidth() / 2)
    .attr("text-anchor", "middle").attr("fill", "white").attr("font-size", "12")
    .attr("font-weight", "700").attr("opacity", 0)
    .text("GRID MODERNIZATION");

  const privateLabel = svg.append("text")
    .attr("x", x(btm_range[btm_range.length - 3]) + x.bandwidth() / 2)
    .attr("y", y(reg_range[2]) + y.bandwidth() / 2)
    .attr("text-anchor", "middle").attr("fill", "white").attr("font-size", "12")
    .attr("font-weight", "700").attr("opacity", 0)
    .text("PRIVATE INFRA");

  // Current estimate marker
  const markerG = svg.append("g").attr("opacity", 0);
  // Current estimate: BTM = 1.2, Reg = 0.5
  const closestBTM = btm_range.reduce((a, b) => Math.abs(b - 1.2) < Math.abs(a - 1.2) ? b : a);
  const closestReg = reg_range.reduce((a, b) => Math.abs(b - 0.5) < Math.abs(a - 0.5) ? b : a);
  const mx = x(closestBTM) + x.bandwidth() / 2;
  const my = y(closestReg) + y.bandwidth() / 2;

  markerG.append("path")
    .attr("d", d3.symbol(d3.symbolStar, 220)())
    .attr("transform", `translate(${mx},${my})`)
    .attr("fill", INK).attr("stroke", "white").attr("stroke-width", 1.5);

  markerG.append("text")
    .attr("x", mx + 18).attr("y", my + 4)
    .attr("fill", INK).attr("font-size", "10").attr("font-weight", "600")
    .text("Current estimate");

  // Source
  svg.append("text").attr("x", ml).attr("y", H - 3)
    .attr("fill", CONTEXT).attr("font-size", "9")
    .text("Source: PySD sensitivity sweep; parameter ranges in methods");

  // ── Step control ────────────────────────────────────────────────────────
  function update(step) {
    // Step 0: cells fade in
    cells.forEach((c, i) => {
      c.transition().delay(step === 0 ? Math.random() * 400 : 0).duration(400)
        .attr("opacity", step >= 0 ? 1 : 0);
    });

    // Step 1: threshold line
    thresholdLine.transition().duration(400).attr("opacity", step >= 1 ? 0.8 : 0);

    // Step 2: labels + marker
    gridLabel.transition().duration(300).attr("opacity", step >= 2 ? 0.7 : 0);
    privateLabel.transition().duration(300).attr("opacity", step >= 2 ? 0.7 : 0);
    markerG.transition().duration(300).attr("opacity", step >= 2 ? 1 : 0);
  }

  return { node: svg.node(), update };
}
