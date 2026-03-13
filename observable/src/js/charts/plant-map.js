// ── Chart: Power Plant + Data Center Map — DD-002 ────────────────────────
// D3-geo map showing new power plants (since 2020) as circles and data
// centers as stars. Scroll toggles fuel layers and data center overlay.
// Steps: 0 = base map | 1 = solar+wind | 2 = gas | 3 = data centers | 4 = all

import * as d3 from "npm:d3@7";
import * as topojson from "npm:topojson-client@3";
import { INK, INK_LIGHT, ACCENT, CONTEXT, RULE, PAPER, FUEL, FUEL_LABEL, CO, chartW } from "../design.js";
import { showTip, moveTip, hideTip } from "../tooltip.js";

export function createPlantMap(geoData, eia, dataCenters) {
  const W = chartW(820);
  const H = 500;

  const states = topojson.feature(geoData, geoData.objects.states);
  const projection = d3.geoAlbersUsa().fitSize([W - 20, H - 60], states);
  const path = d3.geoPath(projection);

  const svg = d3.create("svg")
    .attr("width", "100%")
    .attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif");

  // State boundaries
  svg.append("g")
    .selectAll("path")
    .data(states.features)
    .join("path")
    .attr("d", path)
    .attr("fill", PAPER)
    .attr("stroke", RULE)
    .attr("stroke-width", 0.5);

  // Radius scale for plant capacity
  const rScale = d3.scaleSqrt()
    .domain([50, d3.max(eia.plants, d => d.mw) || 500])
    .range([1.5, 8]);

  // Fuel groupings for scroll steps
  const cleanFuels = ["solar", "wind", "battery"];
  const gasFuels = ["gas_cc", "gas_ct"];

  // Plant circles
  const plantG = svg.append("g");
  const plantDots = (eia.plants || []).map(d => {
    const coords = projection([d.lon, d.lat]);
    if (!coords) return null;
    const fuel = d.fuel;
    const isSolar = fuel === "solar";
    const isWind = fuel === "wind";
    const isBattery = fuel === "battery";
    const isGas = gasFuels.includes(fuel);
    const isClean = cleanFuels.includes(fuel);

    const circle = plantG.append("circle")
      .attr("cx", coords[0]).attr("cy", coords[1])
      .attr("r", rScale(d.mw))
      .attr("fill", FUEL[fuel] || CONTEXT)
      .attr("fill-opacity", 0.6)
      .attr("stroke", "white")
      .attr("stroke-width", 0.3)
      .style("cursor", "crosshair")
      .on("mouseover", (e) => showTip(e,
        `${FUEL_LABEL[fuel] || fuel} · ${d.state}`,
        `${d.mw} MW · ${d.year}`
      ))
      .on("mousemove", moveTip)
      .on("mouseout", hideTip);

    return { circle, fuel, isClean, isGas };
  }).filter(Boolean);

  // Data center stars
  const dcG = svg.append("g").attr("opacity", 0);
  const star = d3.symbol().type(d3.symbolStar).size(80);
  const tickerColor = (t) => CO[t] || ACCENT;

  (dataCenters || []).forEach(d => {
    const coords = projection([d.lon, d.lat]);
    if (!coords) return;

    dcG.append("path")
      .attr("d", star())
      .attr("transform", `translate(${coords[0]},${coords[1]})`)
      .attr("fill", tickerColor(d.ticker))
      .attr("stroke", INK)
      .attr("stroke-width", 0.8)
      .style("cursor", "crosshair")
      .on("mouseover", (e) => showTip(e,
        `${d.name}`,
        `${d.operator} · ${d.state} · ${d.mw} MW · ${d.status}`
      ))
      .on("mousemove", moveTip)
      .on("mouseout", hideTip);
  });

  // Legend
  const legendY = H - 45;
  const fuelLegend = [
    { fuel: "solar", label: "Solar" },
    { fuel: "wind", label: "Wind" },
    { fuel: "battery", label: "Battery" },
    { fuel: "gas_cc", label: "Gas (CC)" },
    { fuel: "gas_ct", label: "Gas (CT)" },
  ];
  fuelLegend.forEach((f, i) => {
    const lx = 10 + i * Math.min(110, (W - 20) / fuelLegend.length);
    svg.append("circle").attr("cx", lx + 5).attr("cy", legendY).attr("r", 4)
      .attr("fill", FUEL[f.fuel]);
    svg.append("text").attr("x", lx + 13).attr("y", legendY + 4)
      .attr("fill", INK_LIGHT).attr("font-size", "9.5").text(f.label);
  });
  // DC star legend
  const dcLx = 10 + fuelLegend.length * Math.min(110, (W - 20) / fuelLegend.length);
  svg.append("path")
    .attr("d", d3.symbol().type(d3.symbolStar).size(50)())
    .attr("transform", `translate(${dcLx + 5},${legendY})`)
    .attr("fill", ACCENT).attr("stroke", INK).attr("stroke-width", 0.5);
  svg.append("text").attr("x", dcLx + 15).attr("y", legendY + 4)
    .attr("fill", INK_LIGHT).attr("font-size", "9.5").text("Data Center");

  // Source
  svg.append("text").attr("x", 10).attr("y", H - 5)
    .attr("fill", CONTEXT).attr("font-size", "9")
    .text("Source: EIA Form 860 (2024), plants >50 MW since 2020; data center locations from public filings");

  // ── Step control ────────────────────────────────────────────────────────
  function update(step) {
    if (step === 0) {
      // Base: show all plants dimmed
      plantDots.forEach(p => {
        p.circle.transition().duration(400).attr("fill-opacity", 0.3);
      });
      dcG.transition().duration(300).attr("opacity", 0);
    } else if (step === 1) {
      // Solar + wind highlighted
      plantDots.forEach(p => {
        p.circle.transition().duration(400)
          .attr("fill-opacity", p.isClean ? 0.7 : 0.08);
      });
      dcG.transition().duration(300).attr("opacity", 0);
    } else if (step === 2) {
      // Gas highlighted
      plantDots.forEach(p => {
        p.circle.transition().duration(400)
          .attr("fill-opacity", p.isGas ? 0.7 : 0.08);
      });
      dcG.transition().duration(300).attr("opacity", 0);
    } else if (step === 3) {
      // Data centers appear, plants dimmed
      plantDots.forEach(p => {
        p.circle.transition().duration(400).attr("fill-opacity", 0.15);
      });
      dcG.transition().duration(500).attr("opacity", 1);
    } else {
      // All visible
      plantDots.forEach(p => {
        p.circle.transition().duration(400).attr("fill-opacity", 0.5);
      });
      dcG.transition().duration(500).attr("opacity", 1);
    }
  }

  return { node: svg.node(), update };
}
