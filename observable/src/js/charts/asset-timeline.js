// ── Chart: Asset Timeline (horizontal bars) — DD-002 opening hook ────────
// Shows the mismatch: AI forecasts span 3 years, infrastructure lasts 25-50.
// Returns { node, update } for use with mountScrollChart.
// Steps: 0 = AI forecast band | 1 = medium-life assets | 2 = long-life | 3 = full view

import * as d3 from "npm:d3@7";
import { INK, INK_LIGHT, ACCENT, CONTEXT, RULE, PAPER, FUEL, chartW } from "../design.js";
import { showTip, moveTip, hideTip } from "../tooltip.js";

export function createAssetTimeline() {
  const data = [
    { tech: "AI demand forecast", life: 3, color: INK },
    { tech: "Gas peaker (BTM)", life: 25, color: FUEL.gas_ct },
    { tech: "Battery storage", life: 25, color: FUEL.battery },
    { tech: "Solar PPA", life: 30, color: FUEL.solar },
    { tech: "Wind farm", life: 30, color: FUEL.wind },
    { tech: "Gas CC (grid)", life: 35, color: FUEL.gas_cc },
    { tech: "Nuclear restart", life: 50, color: FUEL.nuclear },
    { tech: "Transmission line", life: 50, color: FUEL.hydro },
  ];

  const W = chartW(820);
  const H = 354;
  const ml = 140, mr = 55, mt = 52, mb = 36;
  const barH = 26;

  const x = d3.scaleLinear().domain([0, 56]).range([ml, W - mr]);
  const y = d3.scaleBand().domain(data.map(d => d.tech)).range([mt, H - mb]).padding(0.28);

  const svg = d3.create("svg")
    .attr("width", "100%").attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif");

  // ── Title + subtitle ────────────────────────────────────────────────────
  svg.append("text").attr("x", ml).attr("y", 16)
    .attr("fill", INK).attr("font-size", "13").attr("font-weight", "700")
    .text("AI forecasts span 3 years. The infrastructure they fund lasts 25 to 50.");
  svg.append("text").attr("x", ml).attr("y", 30)
    .attr("fill", INK_LIGHT).attr("font-size", "10.5")
    .text("Useful life of energy and infrastructure assets (years) · dark band = AI demand forecast horizon");

  // AI forecast band (always visible, pulsing on step 0)
  const band = svg.append("rect")
    .attr("x", x(0)).attr("y", mt).attr("width", x(3) - x(0)).attr("height", H - mt - mb)
    .attr("fill", INK).attr("opacity", 0.07);

  const bandLine = svg.append("line")
    .attr("x1", x(3)).attr("x2", x(3)).attr("y1", mt).attr("y2", H - mb)
    .attr("stroke", INK).attr("stroke-dasharray", "4,3").attr("stroke-width", 1.2).attr("opacity", 0.5);

  svg.append("text")
    .attr("x", x(1.5)).attr("y", H - mb + 14)
    .attr("text-anchor", "middle").attr("fill", INK_LIGHT).attr("font-size", "10")
    .text("AI forecast horizon");

  // X axis baseline
  svg.append("line")
    .attr("x1", ml).attr("x2", W - mr).attr("y1", H - mb).attr("y2", H - mb)
    .attr("stroke", RULE).attr("stroke-width", 1);

  // X axis labels
  [0, 10, 20, 30, 40, 50].forEach(v => {
    svg.append("text").attr("x", x(v)).attr("y", H - mb + 14)
      .attr("text-anchor", "middle").attr("fill", INK_LIGHT).attr("font-size", "10")
      .text(`${v} yrs`);
  });

  // Y axis labels
  data.forEach(d => {
    svg.append("text")
      .attr("x", ml - 8).attr("y", y(d.tech) + y.bandwidth() / 2 + 4)
      .attr("text-anchor", "end").attr("fill", INK_LIGHT).attr("font-size", "12")
      .text(d.tech);
  });

  // Bars — start at width 0 for animation
  const bars = data.map(d => {
    const rect = svg.append("rect")
      .attr("x", x(0)).attr("y", y(d.tech)).attr("width", 0).attr("height", y.bandwidth())
      .attr("fill", d.color).attr("rx", 2).attr("opacity", 0.85);

    // Value label
    const label = svg.append("text")
      .attr("x", x(d.life) + 6).attr("y", y(d.tech) + y.bandwidth() / 2 + 4)
      .attr("fill", INK).attr("font-size", "11").attr("font-weight", "600")
      .attr("opacity", 0).text(`${d.life} yrs`);

    // Tooltip hit target
    svg.append("rect")
      .attr("x", x(0)).attr("y", y(d.tech)).attr("width", W - ml - mr).attr("height", y.bandwidth())
      .attr("fill", "transparent").style("cursor", "crosshair")
      .on("mouseover", (e) => showTip(e, d.tech, `Asset lifetime: ${d.life} years`))
      .on("mousemove", moveTip)
      .on("mouseout", hideTip);

    return { rect, label, life: d.life };
  });

  // Source text
  svg.append("text").attr("x", ml).attr("y", H - 3)
    .attr("fill", CONTEXT).attr("font-size", "9")
    .text("Source: EIA; industry average asset lifetimes");

  // ── Step control ────────────────────────────────────────────────────────
  function growBars(subset, delay = 0) {
    subset.forEach((b, i) => {
      b.rect.transition().delay(delay + i * 60).duration(600).ease(d3.easeQuadOut)
        .attr("width", x(b.life) - x(0));
      b.label.transition().delay(delay + i * 60 + 400).duration(300)
        .attr("opacity", 1);
    });
  }

  function dimBars(subset) {
    subset.forEach(b => {
      b.rect.transition().duration(200).attr("opacity", 0.15);
      b.label.transition().duration(200).attr("opacity", 0);
    });
  }

  function brightBars(subset) {
    subset.forEach(b => {
      b.rect.transition().duration(200).attr("opacity", 0.85);
      b.label.transition().duration(200).attr("opacity", 1);
    });
  }

  let initialized = false;

  function update(step) {
    if (!initialized) {
      // Grow all bars on first render
      growBars(bars, 100);
      initialized = true;
    }

    if (step === 0) {
      // Highlight AI forecast row, dim others
      brightBars([bars[0]]);
      dimBars(bars.slice(1));
      band.transition().duration(300).attr("opacity", 0.12);
    } else if (step === 1) {
      // Medium-life: gas peaker, battery, solar, wind
      dimBars([bars[0]]);
      brightBars(bars.slice(1, 5));
      dimBars(bars.slice(5));
      band.transition().duration(300).attr("opacity", 0.07);
    } else if (step === 2) {
      // Long-life: gas CC, nuclear, transmission
      dimBars(bars.slice(0, 5));
      brightBars(bars.slice(5));
      band.transition().duration(300).attr("opacity", 0.07);
    } else {
      // Full view
      brightBars(bars);
      band.transition().duration(300).attr("opacity", 0.07);
    }
  }

  return { node: svg.node(), update };
}
