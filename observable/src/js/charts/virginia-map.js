// ── Virginia County Map: Three-tier choropleth ──────────────────────────────
// Loudoun (ACCENT), NoVA suburbs (lighter), rest of Virginia (CONTEXT gray).
// Shows cost geography: benefits concentrate, costs distribute.

import * as d3 from "npm:d3@7";
import * as topojson from "npm:topojson-client@3";
import { INK, INK_LIGHT, ACCENT, CONTEXT, RULE, PAPER, RATEPAYER, NEUTRAL } from "../design.js";
import { showTip, moveTip, hideTip } from "../tooltip.js";

const LOUDOUN_FIPS = "51107";
const NOVA_FIPS = new Set([
  "51059",  // Fairfax
  "51153",  // Prince William
  "51013",  // Arlington
  "51510",  // Alexandria city
  "51610",  // Falls Church city
]);

export function createVirginiaMap(topoData, stats) {
  const W = Math.min(820, (document.body?.clientWidth ?? 820) - 40);
  const H = 420;
  const ml = 10, mr = 10, mt = 10, mb = 36;

  const counties = topojson.feature(topoData, topoData.objects.counties);
  const projection = d3.geoMercator().fitSize([W - ml - mr, H - mt - mb], counties);
  const path = d3.geoPath(projection);

  const svg = d3.create("svg")
    .attr("width", "100%")
    .attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif");

  function tierColor(id) {
    if (id === LOUDOUN_FIPS) return ACCENT;
    if (NOVA_FIPS.has(id)) return NEUTRAL;  // warm tan
    return CONTEXT;
  }

  function tierLabel(id) {
    if (id === LOUDOUN_FIPS) return "Data center hub";
    if (NOVA_FIPS.has(id)) return "NoVA suburbs (partial benefit)";
    return "Rest of Virginia (pays grid costs)";
  }

  // County paths
  const countyPaths = svg.selectAll("path.county")
    .data(counties.features).join("path")
    .attr("class", "county")
    .attr("d", path)
    .attr("fill", d => tierColor(d.id))
    .attr("fill-opacity", d => d.id === LOUDOUN_FIPS ? 0.85 : 0.6)
    .attr("stroke", "white")
    .attr("stroke-width", d => d.id === LOUDOUN_FIPS ? 1.5 : 0.4);

  // Tooltips on counties
  countyPaths
    .style("cursor", "crosshair")
    .on("mouseover", (e, d) => {
      showTip(e, d.properties?.name || `FIPS ${d.id}`, tierLabel(d.id));
    })
    .on("mousemove", moveTip)
    .on("mouseout", hideTip);

  // Loudoun annotation
  const loudounFeature = counties.features.find(f => f.id === LOUDOUN_FIPS);
  if (loudounFeature) {
    const [cx, cy] = path.centroid(loudounFeature);
    svg.append("circle")
      .attr("cx", cx).attr("cy", cy).attr("r", 6)
      .attr("fill", "white").attr("stroke", ACCENT).attr("stroke-width", 2);

    const annoG = svg.append("g").attr("opacity", 0).attr("class", "loudoun-anno");
    annoG.append("line")
      .attr("x1", cx + 8).attr("y1", cy)
      .attr("x2", cx + 60).attr("y2", cy - 30)
      .attr("stroke", ACCENT).attr("stroke-width", 1.2);

    annoG.append("text")
      .attr("x", cx + 64).attr("y", cy - 34)
      .attr("fill", ACCENT).attr("font-size", 11).attr("font-weight", 600)
      .text("Loudoun County");
    annoG.append("text")
      .attr("x", cx + 64).attr("y", cy - 20)
      .attr("fill", ACCENT).attr("font-size", 10)
      .text("~35% of VA data center capacity");
  }

  // Cost inset box
  const costBox = svg.append("g")
    .attr("transform", `translate(${W - 220}, 20)`)
    .attr("opacity", 0);

  costBox.append("rect")
    .attr("width", 200).attr("height", 70)
    .attr("rx", 3)
    .attr("fill", "white").attr("stroke", RULE);

  costBox.append("text")
    .attr("x", 10).attr("y", 20)
    .attr("fill", ACCENT).attr("font-size", 13).attr("font-weight", 600)
    .text(`$${(stats.va_tax_savings_m ?? 928).toLocaleString()}M/year`);

  costBox.append("text")
    .attr("x", 10).attr("y", 36)
    .attr("fill", INK_LIGHT).attr("font-size", 10)
    .text("in sales tax exemptions (FY2023)");

  costBox.append("text")
    .attr("x", 10).attr("y", 56)
    .attr("fill", INK_LIGHT).attr("font-size", 10)
    .text("Grid upgrade costs socialized statewide");

  // Legend
  const legendG = svg.append("g").attr("transform", `translate(12, ${H - mb - 60})`);
  const legendItems = [
    { color: ACCENT, alpha: 0.85, label: "Loudoun County \u2014 data center hub" },
    { color: NEUTRAL, alpha: 0.6, label: "Northern VA \u2014 partial benefit" },
    { color: CONTEXT, alpha: 0.6, label: "Rest of Virginia \u2014 pays grid costs" },
  ];
  legendItems.forEach((item, i) => {
    legendG.append("rect")
      .attr("y", i * 18).attr("width", 14).attr("height", 12)
      .attr("fill", item.color).attr("fill-opacity", item.alpha);
    legendG.append("text")
      .attr("x", 20).attr("y", i * 18 + 10)
      .attr("fill", INK_LIGHT).attr("font-size", 10)
      .text(item.label);
  });

  // Source
  svg.append("text")
    .attr("x", 10).attr("y", H - 4)
    .attr("fill", CONTEXT).attr("font-size", 9)
    .text("Source: JLARC Report 598 (Dec 2024); U.S. Census Bureau TIGER/Line 2024");

  // ── Update ──────────────────────────────────────────────────────────────
  function update(step) {
    const t = svg.transition().duration(400);

    svg.select(".loudoun-anno").transition(t).attr("opacity", step >= 1 ? 1 : 0);
    costBox.transition(t).attr("opacity", step >= 2 ? 1 : 0);
  }

  return { node: svg.node(), update };
}
