// ── Chart: Queue Composition (stacked bars by fuel) — DD-002 ────────────
// Shows that the interconnection queue is overwhelmingly clean energy.
// Steps: 0 = bars grow | 1 = solar+battery highlight | 2 = gas shrinking

import * as d3 from "npm:d3@7";
import { INK, INK_LIGHT, ACCENT, CONTEXT, RULE, FUEL, FUEL_LABEL, chartW } from "../design.js";
import { showTip, moveTip, hideTip } from "../tooltip.js";

export function createQueueComposition(queue) {
  const fuelOrder = ["solar", "battery", "wind", "gas", "other"];
  const fuelColors = {
    solar: FUEL.solar, battery: FUEL.battery, wind: FUEL.wind,
    gas: CONTEXT, other: RULE,
  };
  const fuelLabels = {
    solar: "Solar", battery: "Battery Storage", wind: "Wind",
    gas: "Gas", other: "Other",
  };

  // Pivot
  const years = [...new Set(queue.composition.map(d => d.year))].sort();
  const pivot = years.map(yr => {
    const row = { year: yr };
    fuelOrder.forEach(f => { row[f] = 0; });
    queue.composition.filter(d => d.year === yr).forEach(d => {
      if (fuelOrder.includes(d.fuel)) row[d.fuel] = d.gw;
    });
    return row;
  });

  const W = chartW(820);
  const H = 354;
  const ml = 48, mr = 20, mt = 52, mb = 70;

  const x = d3.scaleBand().domain(years).range([ml, W - mr]).padding(0.25);
  const stack = d3.stack().keys(fuelOrder)(pivot);
  const yMax = d3.max(stack[stack.length - 1], d => d[1]);
  const y = d3.scaleLinear().domain([0, yMax * 1.1]).range([H - mb, mt]);

  const svg = d3.create("svg").attr("width", "100%").attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif");

  // ── Title + subtitle ────────────────────────────────────────────────────
  svg.append("text").attr("x", ml).attr("y", 16)
    .attr("fill", INK).attr("font-size", "13").attr("font-weight", "700")
    .text("The interconnection queue is overwhelmingly clean energy — but gas is growing");
  svg.append("text").attr("x", ml).attr("y", 30)
    .attr("fill", INK_LIGHT).attr("font-size", "10.5")
    .text("U.S. interconnection queue by fuel type (GW) · 2018–2024");

  // Axes
  svg.append("line").attr("x1", ml).attr("x2", W - mr)
    .attr("y1", H - mb).attr("y2", H - mb).attr("stroke", RULE);

  years.forEach(yr => {
    svg.append("text").attr("x", x(yr) + x.bandwidth() / 2).attr("y", H - mb + 14)
      .attr("text-anchor", "middle").attr("fill", INK_LIGHT).attr("font-size", "11").text(yr);
  });

  y.ticks(5).forEach(v => {
    svg.append("text").attr("x", ml - 6).attr("y", y(v) + 4)
      .attr("text-anchor", "end").attr("fill", INK_LIGHT).attr("font-size", "10")
      .text(`${v.toFixed(0)} GW`);
  });

  // Clip for bar animation
  const defs = svg.append("defs");
  const cpRect = defs.append("clipPath").attr("id", "cp-qcomp")
    .append("rect").attr("x", ml).attr("y", H - mb).attr("width", W - ml - mr).attr("height", 0);
  const barsG = svg.append("g").attr("clip-path", "url(#cp-qcomp)");

  const fuelRects = {};
  fuelOrder.forEach(f => { fuelRects[f] = []; });

  stack.forEach(layer => {
    const fuel = layer.key;
    layer.forEach((seg, i) => {
      const yr = years[i];
      const y0 = y(seg[0]), y1 = y(seg[1]);
      const g = barsG.append("g");
      const rect = g.append("rect")
        .attr("x", x(yr)).attr("y", y1).attr("width", x.bandwidth())
        .attr("height", Math.max(y0 - y1, 0))
        .attr("fill", fuelColors[fuel] || CONTEXT).attr("stroke", "white").attr("stroke-width", 0.5);
      fuelRects[fuel].push(rect);

      const val = (seg[1] - seg[0]).toFixed(0);
      g.style("cursor", "crosshair")
        .on("mouseover", (e) => { showTip(e, `${fuelLabels[fuel] || fuel} · ${yr}`, `${val} GW`); })
        .on("mousemove", moveTip)
        .on("mouseout", hideTip);
    });
  });

  // Legend
  const legendY = H - mb + 28;
  fuelOrder.forEach((f, i) => {
    const lx = ml + i * Math.min(120, (W - ml) / fuelOrder.length);
    svg.append("rect").attr("x", lx).attr("y", legendY).attr("width", 10).attr("height", 10)
      .attr("fill", fuelColors[f]).attr("rx", 1);
    svg.append("text").attr("x", lx + 14).attr("y", legendY + 9)
      .attr("fill", INK_LIGHT).attr("font-size", "10").text(fuelLabels[f] || f);
  });

  // Source
  svg.append("text").attr("x", ml).attr("y", H - 3)
    .attr("fill", CONTEXT).attr("font-size", "9")
    .text("Source: LBNL 'Queued Up' 2025 Edition; annual queue composition");

  // Step control
  function setFuelFocus(fuels) {
    fuelOrder.forEach(f => {
      const op = fuels === null || fuels.includes(f) ? 1 : 0.15;
      fuelRects[f].forEach(r => r.transition().duration(300).attr("opacity", op));
    });
  }

  function update(step) {
    if (step === 0) {
      cpRect.interrupt().attr("y", H - mb).attr("height", 0);
      setFuelFocus(null);
      cpRect.transition().delay(150).duration(900).ease(d3.easeQuadOut)
        .attr("y", mt).attr("height", H - mb - mt);
    } else {
      cpRect.interrupt().attr("y", mt).attr("height", H - mb - mt);
      if (step === 1) setFuelFocus(["solar", "battery"]);
      else if (step === 2) setFuelFocus(["gas"]);
      else setFuelFocus(null);
    }
  }

  return { node: svg.node(), update };
}
