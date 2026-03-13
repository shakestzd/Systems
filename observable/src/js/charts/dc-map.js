// ── Chart: Data center map (choropleth + bubble overlay) ────────────────────
// Returns { node, update } for use with mountScrollChart.
// Steps: 0 = base geography | 1 = choropleth fills | 2 = bubbles appear |
//        3 = highlight NoVA cluster | 4 = top state label

import * as d3 from "npm:d3@7";
import * as topojson from "npm:topojson-client@3";
import { INK, INK_LIGHT, ACCENT, CONTEXT, RULE, PAPER, OCC_TECH, chartW } from "../design.js";
import { cc, cl } from "../design.js";
import { showTip, moveTip, hideTip } from "../tooltip.js";

// Operator colors for bubbles — known tickers get company colors, others get accent
function operatorColor(ticker) {
  if (!ticker) return CONTEXT;
  return cc(ticker);
}

export function createDcMap(topoData, qcewStates, dcLocations, stats) {
  const W = chartW(780);
  const H = 480;
  const ml = 8, mr = 8, mt = 8, mb = 36;

  const svg = d3.create("svg")
    .attr("width", "100%")
    .attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif");

  // ── Geography ─────────────────────────────────────────────────────────────
  const states = topojson.feature(topoData, topoData.objects.states);
  const statemesh = topojson.mesh(topoData, topoData.objects.states, (a, b) => a !== b);

  const projection = d3.geoAlbersUsa().fitSize([W - ml - mr, H - mt - mb], states);
  const path = d3.geoPath(projection);

  // Build employment lookup by state ID
  const emplByStateId = new Map();
  qcewStates.forEach(d => {
    if (d.stateId != null) {
      emplByStateId.set(d.stateId, d.employment);
    }
  });

  const maxEmpl = d3.max(qcewStates, d => d.employment) || 1;
  const colorScale = d3.scaleSequential()
    .domain([0, maxEmpl])
    .interpolator(d3.interpolate(PAPER, OCC_TECH));

  // State paths — start with no fill (paper bg)
  const statePaths = svg.append("g")
    .selectAll("path")
    .data(states.features)
    .join("path")
    .attr("d", path)
    .attr("fill", PAPER)
    .attr("stroke", RULE)
    .attr("stroke-width", 0.5);

  // State borders
  svg.append("path")
    .datum(statemesh)
    .attr("d", path)
    .attr("fill", "none")
    .attr("stroke", RULE)
    .attr("stroke-width", 0.5);

  // ── Choropleth legend ─────────────────────────────────────────────────────
  const legendG = svg.append("g")
    .attr("transform", `translate(${W - 200}, ${H - mb - 50})`)
    .attr("opacity", 0);

  const legendW = 160, legendH = 10;
  const defs = svg.append("defs");
  const gradId = "empl-gradient";
  const grad = defs.append("linearGradient").attr("id", gradId);
  grad.append("stop").attr("offset", "0%").attr("stop-color", PAPER);
  grad.append("stop").attr("offset", "100%").attr("stop-color", OCC_TECH);

  legendG.append("rect")
    .attr("width", legendW).attr("height", legendH)
    .attr("fill", `url(#${gradId})`).attr("stroke", RULE).attr("stroke-width", 0.5);
  legendG.append("text")
    .attr("y", legendH + 12).attr("fill", INK_LIGHT).attr("font-size", "9").text("0");
  legendG.append("text")
    .attr("x", legendW).attr("y", legendH + 12)
    .attr("text-anchor", "end").attr("fill", INK_LIGHT).attr("font-size", "9")
    .text(`${(maxEmpl/1000).toFixed(0)}K`);
  legendG.append("text")
    .attr("y", -4).attr("fill", INK_LIGHT).attr("font-size", "9")
    .text("NAICS 518210 employment");

  // ── Data center bubbles ───────────────────────────────────────────────────
  const bubbleScale = d3.scaleSqrt()
    .domain([0, d3.max(dcLocations, d => d.mw) || 1000])
    .range([3, 18]);

  const bubbleG = svg.append("g").attr("opacity", 0);

  // Filter to locations that project onto the map
  const validLocs = dcLocations.filter(d => projection([d.lon, d.lat]) != null);

  validLocs.forEach(d => {
    const [cx, cy] = projection([d.lon, d.lat]);
    const r = bubbleScale(d.mw);
    const color = operatorColor(d.ticker);

    const g = bubbleG.append("g");

    g.append("circle")
      .attr("cx", cx).attr("cy", cy).attr("r", r)
      .attr("fill", color).attr("opacity", 0.65)
      .attr("stroke", "white").attr("stroke-width", 0.8);

    // Invisible hit target
    g.append("circle")
      .attr("cx", cx).attr("cy", cy).attr("r", Math.max(r, 10))
      .attr("fill", "transparent").style("cursor", "crosshair")
      .on("mouseover", (e) => {
        showTip(e,
          d.name,
          `Operator: ${d.operator || "Unknown"}`,
          `Capacity: ${d.mw} MW`,
          `Status: ${d.status}`
        );
      })
      .on("mousemove", moveTip)
      .on("mouseout", hideTip);
  });

  // ── NoVA highlight circle ─────────────────────────────────────────────────
  const novaCoords = projection([-77.45, 39.0]);
  const novaHighlight = svg.append("g").attr("opacity", 0);
  if (novaCoords) {
    novaHighlight.append("circle")
      .attr("cx", novaCoords[0]).attr("cy", novaCoords[1])
      .attr("r", 35)
      .attr("fill", "none")
      .attr("stroke", ACCENT).attr("stroke-width", 2)
      .attr("stroke-dasharray", "4,3");
    novaHighlight.append("text")
      .attr("x", novaCoords[0] + 38).attr("y", novaCoords[1] - 6)
      .attr("fill", ACCENT).attr("font-size", "11").attr("font-weight", "600")
      .text("Loudoun County");
    novaHighlight.append("text")
      .attr("x", novaCoords[0] + 38).attr("y", novaCoords[1] + 8)
      .attr("fill", ACCENT).attr("font-size", "10")
      .text("Data Center Alley");
  }

  // ── Top state annotation ──────────────────────────────────────────────────
  const topAnnotation = svg.append("g").attr("opacity", 0);
  if (stats.top_state && stats.top_count) {
    topAnnotation.append("text")
      .attr("x", W / 2).attr("y", mt + 22)
      .attr("text-anchor", "middle").attr("fill", INK).attr("font-size", "13").attr("font-weight", "600")
      .text(`${stats.top_state}: ${(stats.top_count).toLocaleString()} workers in NAICS 518210`);
  }

  // ── Bubble legend ─────────────────────────────────────────────────────────
  const bubLegG = svg.append("g")
    .attr("transform", `translate(${ml + 10}, ${H - mb - 55})`)
    .attr("opacity", 0);
  [200, 500, 1000].forEach((mw, i) => {
    const r = bubbleScale(mw);
    bubLegG.append("circle")
      .attr("cx", 10).attr("cy", i * 22)
      .attr("r", r).attr("fill", CONTEXT).attr("opacity", 0.5)
      .attr("stroke", RULE).attr("stroke-width", 0.5);
    bubLegG.append("text")
      .attr("x", 28).attr("y", i * 22 + 4)
      .attr("fill", INK_LIGHT).attr("font-size", "9")
      .text(`${mw} MW`);
  });
  bubLegG.append("text")
    .attr("y", -8).attr("fill", INK_LIGHT).attr("font-size", "9")
    .text("Data center capacity");

  // Source
  svg.append("text")
    .attr("x", ml).attr("y", H - 4)
    .attr("fill", CONTEXT).attr("font-size", "9")
    .text("Source: BLS QCEW (NAICS 518210); data center locations from public filings");

  // ── Step control ──────────────────────────────────────────────────────────
  function update(step) {
    if (step === 0) {
      // Base geography only — all states paper-colored
      statePaths.transition().duration(400).attr("fill", PAPER);
      legendG.transition().duration(200).attr("opacity", 0);
      bubbleG.transition().duration(200).attr("opacity", 0);
      bubLegG.transition().duration(200).attr("opacity", 0);
      novaHighlight.transition().duration(200).attr("opacity", 0);
      topAnnotation.transition().duration(200).attr("opacity", 0);
    } else if (step === 1) {
      // Choropleth fills in
      statePaths.transition().duration(600)
        .attr("fill", d => {
          const empl = emplByStateId.get(d.id);
          return empl != null ? colorScale(empl) : PAPER;
        });
      legendG.transition().delay(300).duration(400).attr("opacity", 1);
      bubbleG.transition().duration(200).attr("opacity", 0);
      bubLegG.transition().duration(200).attr("opacity", 0);
      novaHighlight.transition().duration(200).attr("opacity", 0);
      topAnnotation.transition().duration(200).attr("opacity", 0);
    } else if (step === 2) {
      // Bubbles appear
      statePaths.transition().duration(300)
        .attr("fill", d => {
          const empl = emplByStateId.get(d.id);
          return empl != null ? colorScale(empl) : PAPER;
        });
      legendG.attr("opacity", 1);
      bubbleG.transition().delay(200).duration(500).attr("opacity", 1);
      bubLegG.transition().delay(400).duration(300).attr("opacity", 1);
      novaHighlight.transition().duration(200).attr("opacity", 0);
      topAnnotation.transition().duration(200).attr("opacity", 0);
    } else if (step === 3) {
      // Highlight NoVA
      statePaths.transition().duration(300)
        .attr("fill", d => {
          const empl = emplByStateId.get(d.id);
          return empl != null ? colorScale(empl) : PAPER;
        });
      legendG.attr("opacity", 1);
      bubbleG.attr("opacity", 1);
      bubLegG.attr("opacity", 1);
      novaHighlight.transition().delay(200).duration(400).attr("opacity", 1);
      topAnnotation.transition().duration(200).attr("opacity", 0);
    } else {
      // step >= 4: Show top state annotation
      statePaths.transition().duration(300)
        .attr("fill", d => {
          const empl = emplByStateId.get(d.id);
          return empl != null ? colorScale(empl) : PAPER;
        });
      legendG.attr("opacity", 1);
      bubbleG.attr("opacity", 1);
      bubLegG.attr("opacity", 1);
      novaHighlight.attr("opacity", 1);
      topAnnotation.transition().delay(200).duration(400).attr("opacity", 1);
    }
  }

  return { node: svg.node(), update };
}
