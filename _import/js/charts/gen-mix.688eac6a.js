// ── Chart: Generation Mix (stacked bars) — DD-002 ──────────────────────
// Stacked bar chart of new U.S. generation capacity by fuel type, 2018-2024.
// Steps: 0 = bars grow | 1 = solar highlight | 2 = battery highlight |
//        3 = gas highlight | 4 = full + IRA annotation

import * as d3 from "../../../_npm/d3@7.9.0/e324157d.js";
import { INK, INK_LIGHT, ACCENT, CONTEXT, RULE, FUEL, FUEL_LABEL, chartW } from "../design.2d3db129.js";
import { showTip, moveTip, hideTip } from "../tooltip.40aee997.js";

export function createGenMix(eia) {
  const fuelOrder = ["solar", "wind", "battery", "gas_cc", "gas_ct", "nuclear", "hydro", "coal"];
  const fuelLabels = fuelOrder.map(f => FUEL_LABEL[f] || f);

  // Pivot: { year, solar, wind, ... }
  const years = [...new Set(eia.gen_mix.map(d => d.year))].sort();
  const pivot = years.map(yr => {
    const row = { year: yr };
    fuelOrder.forEach(f => { row[f] = 0; });
    eia.gen_mix.filter(d => d.year === yr).forEach(d => {
      if (fuelOrder.includes(d.fuel)) row[d.fuel] = d.gw;
    });
    return row;
  });

  const W = chartW(820);
  const H = 374;
  const ml = 48, mr = 20, mt = 52, mb = 80;

  const x = d3.scaleBand().domain(years).range([ml, W - mr]).padding(0.25);
  const stack = d3.stack().keys(fuelOrder)(pivot);
  const yMax = d3.max(stack[stack.length - 1], d => d[1]);
  const y = d3.scaleLinear().domain([0, yMax * 1.1]).range([H - mb, mt]);

  const svg = d3.create("svg").attr("width", "100%").attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif");

  // ── Title + subtitle ────────────────────────────────────────────────────
  svg.append("text").attr("x", ml).attr("y", 16)
    .attr("fill", INK).attr("font-size", "13").attr("font-weight", "700")
    .text("Solar dominates new U.S. generation since 2018");
  svg.append("text").attr("x", ml).attr("y", 30)
    .attr("fill", INK_LIGHT).attr("font-size", "10.5")
    .text("New generation capacity added 2018–2024, by fuel type (GW nameplate)");

  // X axis
  svg.append("line").attr("x1", ml).attr("x2", W - mr)
    .attr("y1", H - mb).attr("y2", H - mb).attr("stroke", RULE).attr("stroke-width", 1);

  years.forEach(yr => {
    svg.append("text").attr("x", x(yr) + x.bandwidth() / 2).attr("y", H - mb + 14)
      .attr("text-anchor", "middle").attr("fill", INK_LIGHT).attr("font-size", "11")
      .text(yr);
  });

  // Y axis
  const yTicks = y.ticks(5);
  yTicks.forEach(v => {
    svg.append("text").attr("x", ml - 6).attr("y", y(v) + 4)
      .attr("text-anchor", "end").attr("fill", INK_LIGHT).attr("font-size", "10")
      .text(`${v.toFixed(0)} GW`);
    if (v > 0) {
      svg.append("line").attr("x1", ml).attr("x2", W - mr)
        .attr("y1", y(v)).attr("y2", y(v))
        .attr("stroke", RULE).attr("stroke-width", 0.5).attr("opacity", 0.4);
    }
  });

  // Clip path for bar animation
  const defs = svg.append("defs");
  const cpRect = defs.append("clipPath").attr("id", "cp-genmix")
    .append("rect").attr("x", ml).attr("y", H - mb).attr("width", W - ml - mr).attr("height", 0);
  const barsG = svg.append("g").attr("clip-path", "url(#cp-genmix)");

  // Track rects by fuel for highlighting
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
        .attr("fill", FUEL[fuel] || CONTEXT)
        .attr("stroke", "white").attr("stroke-width", 0.5);

      fuelRects[fuel].push(rect);

      const val = (seg[1] - seg[0]).toFixed(1);
      g.style("cursor", "crosshair")
        .on("mouseover", (e) => {
          rect.attr("opacity", 0.75);
          showTip(e, `${FUEL_LABEL[fuel] || fuel} · ${yr}`, `${val} GW`);
        })
        .on("mousemove", moveTip)
        .on("mouseout", () => { rect.attr("opacity", 1); hideTip(); });
    });
  });

  // IRA annotation (appears in later steps)
  const iraG = svg.append("g").attr("opacity", 0);
  if (years.includes(2022)) {
    const iraX = x(2022) + x.bandwidth() * 0.6;
    iraG.append("line").attr("x1", iraX).attr("x2", iraX)
      .attr("y1", mt + 10).attr("y2", H - mb)
      .attr("stroke", INK).attr("stroke-dasharray", "4,3").attr("stroke-width", 1);
    iraG.append("text").attr("x", iraX).attr("y", mt + 6)
      .attr("text-anchor", "middle").attr("fill", INK).attr("font-size", "10")
      .attr("font-weight", "600").text("IRA signed Aug 2022");
  }

  // Legend
  const legendY = H - mb + 28;
  const colW = Math.min(110, (W - ml - mr) / 4);
  fuelOrder.slice(0, 8).forEach((f, i) => {
    const col = i % 4;
    const row = Math.floor(i / 4);
    const lx = ml + col * colW;
    const ly = legendY + row * 16;
    svg.append("rect").attr("x", lx).attr("y", ly).attr("width", 10).attr("height", 10)
      .attr("fill", FUEL[f] || CONTEXT).attr("rx", 1);
    svg.append("text").attr("x", lx + 14).attr("y", ly + 9)
      .attr("fill", INK_LIGHT).attr("font-size", "10").text(FUEL_LABEL[f] || f);
  });

  // Source
  svg.append("text").attr("x", ml).attr("y", H - 3)
    .attr("fill", CONTEXT).attr("font-size", "9")
    .text("Source: EIA Form 860M, monthly capacity additions");

  // ── Step control ────────────────────────────────────────────────────────
  function setFuelFocus(focusFuels) {
    fuelOrder.forEach(f => {
      const op = focusFuels === null || focusFuels.includes(f) ? 1 : 0.15;
      fuelRects[f].forEach(r => r.transition().duration(300).attr("opacity", op));
    });
  }

  function update(step) {
    if (step === 0) {
      cpRect.interrupt().attr("y", H - mb).attr("height", 0);
      setFuelFocus(null);
      iraG.attr("opacity", 0);
      cpRect.transition().delay(150).duration(1000).ease(d3.easeQuadOut)
        .attr("y", mt).attr("height", H - mb - mt);
    } else {
      cpRect.interrupt().attr("y", mt).attr("height", H - mb - mt);

      if (step === 1) {
        setFuelFocus(["solar"]);
        iraG.transition().duration(300).attr("opacity", 0);
      } else if (step === 2) {
        setFuelFocus(["battery"]);
        iraG.transition().duration(300).attr("opacity", 0);
      } else if (step === 3) {
        setFuelFocus(["gas_cc", "gas_ct"]);
        iraG.transition().duration(300).attr("opacity", 1);
      }
    }
  }

  return { node: svg.node(), update };
}
