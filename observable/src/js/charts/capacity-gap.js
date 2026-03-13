// ── Chart: Capacity Gap (Cleveland dot plot / dumbbell) — DD-002 ──────────
// Shows nameplate vs energy-equivalent capacity per fuel type.
// The gap between dots IS the story: how much nameplate overstates contribution.
// Steps: 0 = all appear | 1 = solar gap highlight | 2 = gas CC highlight | 3 = labels

import * as d3 from "npm:d3@7";
import { INK, INK_LIGHT, ACCENT, CONTEXT, RULE, FUEL, FUEL_LABEL, chartW } from "../design.js";
import { showTip, moveTip, hideTip } from "../tooltip.js";

export function createCapacityGap(eia) {
  const data = (eia.cap_factor || [])
    .filter(d => d.nameplate > 0)
    .sort((a, b) => b.nameplate - a.nameplate);

  if (data.length === 0) {
    const el = document.createElement("div");
    el.textContent = "No capacity factor data available.";
    return { node: el, update: () => {} };
  }

  const W = chartW(720);
  const H = 74 + data.length * 56 + 60;
  const ml = 110, mr = 60, mt = 64, mb = 60;

  const x = d3.scaleLinear()
    .domain([0, d3.max(data, d => d.nameplate) * 1.15])
    .range([ml, W - mr]);

  const y = d3.scaleBand()
    .domain(data.map(d => d.fuel))
    .range([mt, H - mb])
    .padding(0.35);

  const svg = d3.create("svg")
    .attr("width", "100%")
    .attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif");

  // ── Title + subtitle ────────────────────────────────────────────────────
  svg.append("text").attr("x", ml).attr("y", 16)
    .attr("fill", INK).attr("font-size", "13").attr("font-weight", "700")
    .text("Nameplate capacity overstates solar's energy contribution by 3×");
  svg.append("text").attr("x", ml).attr("y", 30)
    .attr("fill", INK_LIGHT).attr("font-size", "10.5")
    .text("Left dot = nameplate GW · right dot = energy-equivalent output · gap = overstatement");

  // X-axis gridlines
  const ticks = x.ticks(5);
  ticks.forEach(v => {
    svg.append("line")
      .attr("x1", x(v)).attr("x2", x(v))
      .attr("y1", mt).attr("y2", H - mb)
      .attr("stroke", RULE).attr("stroke-width", 0.5).attr("opacity", 0.4);
    svg.append("text")
      .attr("x", x(v)).attr("y", H - mb + 16)
      .attr("text-anchor", "middle").attr("fill", INK_LIGHT).attr("font-size", "10")
      .text(`${v} GW`);
  });

  // Baseline
  svg.append("line")
    .attr("x1", ml).attr("x2", W - mr)
    .attr("y1", H - mb).attr("y2", H - mb)
    .attr("stroke", RULE);

  // Column headers
  svg.append("text").attr("x", x(d3.max(data, d => d.nameplate) * 0.55)).attr("y", mt - 8)
    .attr("text-anchor", "middle").attr("fill", INK_LIGHT).attr("font-size", "10")
    .attr("font-weight", "600").text("Nameplate                     Effective");

  // Row groups
  const rows = data.map(d => {
    const cy = y(d.fuel) + y.bandwidth() / 2;
    const g = svg.append("g");

    // Fuel label
    g.append("text")
      .attr("x", ml - 10).attr("y", cy + 4)
      .attr("text-anchor", "end").attr("fill", INK).attr("font-size", "12")
      .attr("font-weight", "500")
      .text(FUEL_LABEL[d.fuel] || d.fuel);

    // Connecting line (the gap)
    const line = g.append("line")
      .attr("x1", x(d.effective)).attr("x2", x(d.nameplate))
      .attr("y1", cy).attr("y2", cy)
      .attr("stroke", FUEL[d.fuel] || CONTEXT)
      .attr("stroke-width", 3).attr("stroke-linecap", "round")
      .attr("opacity", 0.35);

    // Effective dot (smaller, filled)
    const effDot = g.append("circle")
      .attr("cx", x(d.effective)).attr("cy", cy).attr("r", 6)
      .attr("fill", FUEL[d.fuel] || CONTEXT)
      .attr("stroke", "white").attr("stroke-width", 1.5);

    // Nameplate dot (larger, open)
    const nameDot = g.append("circle")
      .attr("cx", x(d.nameplate)).attr("cy", cy).attr("r", 7)
      .attr("fill", "white")
      .attr("stroke", FUEL[d.fuel] || CONTEXT)
      .attr("stroke-width", 2.5);

    // Gap label (appears on step 3)
    const gapLabel = g.append("text")
      .attr("x", x(d.nameplate) + 10).attr("y", cy + 4)
      .attr("fill", INK_LIGHT).attr("font-size", "10")
      .attr("opacity", 0)
      .text(`${Math.round((1 - d.cf) * 100)}% gap`);

    // Invisible hit targets
    const hitW = Math.abs(x(d.nameplate) - x(d.effective)) + 20;
    g.append("rect")
      .attr("x", x(d.effective) - 10).attr("y", cy - 14)
      .attr("width", hitW).attr("height", 28)
      .attr("fill", "transparent").style("cursor", "crosshair")
      .on("mouseover", (e) => showTip(e,
        FUEL_LABEL[d.fuel] || d.fuel,
        `Nameplate: ${d.nameplate} GW | Effective: ${d.effective} GW | CF: ${Math.round(d.cf * 100)}%`
      ))
      .on("mousemove", moveTip)
      .on("mouseout", hideTip);

    return { g, line, effDot, nameDot, gapLabel, fuel: d.fuel };
  });

  // Legend
  const legendY = H - mb + 34;
  // Nameplate legend
  svg.append("circle").attr("cx", ml + 6).attr("cy", legendY).attr("r", 5)
    .attr("fill", "white").attr("stroke", CONTEXT).attr("stroke-width", 2);
  svg.append("text").attr("x", ml + 16).attr("y", legendY + 4)
    .attr("fill", INK_LIGHT).attr("font-size", "10").text("Nameplate capacity");
  // Effective legend
  svg.append("circle").attr("cx", ml + 140).attr("cy", legendY).attr("r", 4.5)
    .attr("fill", CONTEXT);
  svg.append("text").attr("x", ml + 150).attr("y", legendY + 4)
    .attr("fill", INK_LIGHT).attr("font-size", "10").text("Effective (capacity-factor-adjusted)");

  // Source
  svg.append("text").attr("x", ml).attr("y", H - 3)
    .attr("fill", CONTEXT).attr("font-size", "9")
    .text("Source: EIA Form 860 (2024); capacity factors from EIA national averages");

  // ── Step control ────────────────────────────────────────────────────────
  function setFocus(fuel) {
    rows.forEach(r => {
      const isFocus = fuel === null || r.fuel === fuel;
      const op = isFocus ? 1 : 0.15;
      r.g.transition().duration(300).attr("opacity", op);
    });
  }

  function update(step) {
    // Reset gap labels
    rows.forEach(r => r.gapLabel.transition().duration(200).attr("opacity", 0));

    if (step === 0) {
      setFocus(null);
    } else if (step === 1) {
      setFocus("solar");
    } else if (step === 2) {
      setFocus("gas_cc");
    } else if (step === 3) {
      setFocus(null);
      rows.forEach(r => r.gapLabel.transition().delay(200).duration(400).attr("opacity", 1));
    }
  }

  return { node: svg.node(), update };
}
