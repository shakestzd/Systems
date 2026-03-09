// ── DD-004 US Data Center Siting Map: Bubble map with scroll-driven reveal ──
// geoAlbersUsa projection, operator-colored bubbles sized by MW.
// Scroll: empty outline -> all facilities -> Virginia cluster -> distressed counties.

import * as d3 from "npm:d3@7";
import * as topojson from "npm:topojson-client@3";
import { INK, INK_LIGHT, ACCENT, CONTEXT, RULE, PAPER } from "../design.js";
import { showTip, moveTip, hideTip } from "../tooltip.js";

const OP_COLORS = {
  "Meta":      "#BB5566",
  "Google":    "#2a7d42",
  "Amazon":    "#c96b28",
  "Microsoft": "#3a6fa8",
  "Apple":     "#44BB99",
  "Oracle":    "#CCBB44",
  "Digital Realty": "#AA3377",
  "QTS Realty":     "#66CCEE",
};

export function createDD004DCMap(topoData, locations) {
  const W = Math.min(820, (document.body?.clientWidth ?? 820) - 40);
  const H = 500;

  const states = topojson.feature(topoData, topoData.objects.states);
  const projection = d3.geoAlbersUsa().fitSize([W - 20, H - 60], states);
  const path = d3.geoPath(projection);

  const svg = d3.create("svg")
    .attr("width", "100%")
    .attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif");

  // State boundaries
  svg.selectAll("path.state")
    .data(states.features).join("path")
    .attr("class", "state")
    .attr("d", path)
    .attr("fill", PAPER).attr("stroke", RULE).attr("stroke-width", 0.5);

  // Facility bubbles
  const facilities = locations.facilities
    .filter(d => d.lat && d.lon)
    .map(d => {
      const proj = projection([d.lon, d.lat]);
      return proj ? { ...d, px: proj[0], py: proj[1] } : null;
    })
    .filter(d => d !== null);

  const mwExtent = d3.extent(facilities, d => d.announced_mw ?? 200);
  const rScale = d3.scaleSqrt().domain([0, mwExtent[1] ?? 500]).range([3, 16]);

  const bubbles = svg.selectAll("g.bubble")
    .data(facilities).join("g")
    .attr("class", "bubble")
    .attr("transform", d => `translate(${d.px},${d.py})`)
    .attr("opacity", 0);

  // Visible circle
  const visCircles = bubbles.append("circle")
    .attr("r", d => rScale(d.announced_mw ?? 200))
    .attr("fill", d => OP_COLORS[d.operator] ?? CONTEXT)
    .attr("fill-opacity", 0.7)
    .attr("stroke", "white")
    .attr("stroke-width", 0.5);

  // Invisible hit target
  bubbles.append("circle")
    .attr("r", 12)
    .attr("fill", "transparent")
    .style("cursor", "crosshair")
    .on("mouseover", (e, d) => {
      showTip(e, d.name || d.operator,
        `${d.operator} \u00b7 ${d.county}, ${d.state}`,
        d.announced_mw ? `${d.announced_mw} MW` : "",
        d.median_household_income ? `Median income: $${(d.median_household_income / 1000).toFixed(0)}K` : "",
        d.poverty_rate != null ? `Poverty: ${(d.poverty_rate * 100).toFixed(1)}%` : ""
      );
    })
    .on("mousemove", moveTip)
    .on("mouseout", hideTip);

  // Legend
  const legendG = svg.append("g").attr("transform", `translate(${W - 160}, ${H - 130})`);
  const ops = [...new Set(facilities.map(d => d.operator))].sort();
  ops.forEach((op, i) => {
    legendG.append("circle")
      .attr("cx", 6).attr("cy", i * 16)
      .attr("r", 5).attr("fill", OP_COLORS[op] ?? CONTEXT).attr("fill-opacity", 0.7);
    legendG.append("text")
      .attr("x", 16).attr("y", i * 16 + 4)
      .attr("fill", INK_LIGHT).attr("font-size", 10)
      .text(op);
  });

  // Source
  svg.append("text")
    .attr("x", 10).attr("y", H - 4)
    .attr("fill", CONTEXT).attr("font-size", 9)
    .text("Source: Company press releases, state economic development announcements, 2010\u20132025");

  // ── Update ──────────────────────────────────────────────────────────────
  function update(step) {
    const t = svg.transition().duration(500);

    if (step === 0) {
      bubbles.transition(t).attr("opacity", 0);
    } else if (step === 1) {
      // All facilities spring in
      bubbles.transition(t).attr("opacity", 1);
      visCircles
        .attr("fill", d => OP_COLORS[d.operator] ?? CONTEXT)
        .transition().duration(350).ease(d3.easeBackOut.overshoot(1.4))
        .attr("r", d => rScale(d.announced_mw ?? 200));
    } else if (step === 2) {
      // Dim all except Virginia
      visCircles.attr("fill", d => OP_COLORS[d.operator] ?? CONTEXT);
      bubbles.transition(t)
        .attr("opacity", d => d.state === "VA" ? 1 : 0.15);
    } else if (step === 3) {
      // Highlight distressed (poverty > 15%)
      bubbles.transition(t)
        .attr("opacity", d => (d.poverty_rate != null && d.poverty_rate > 0.15) ? 1 : 0.15);
      visCircles.transition(t)
        .attr("fill", d => (d.poverty_rate != null && d.poverty_rate > 0.15) ? ACCENT : (OP_COLORS[d.operator] ?? CONTEXT));
    }
  }

  return { node: svg.node(), update };
}
