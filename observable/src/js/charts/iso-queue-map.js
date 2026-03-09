// ── Chart: ISO Queue Map (choropleth + bubbles) — DD-002 ────────────────
// D3-geo map showing ISO/RTO territories with queue backlog bubbles.
// Steps: 0 = state boundaries | 1 = ISO territory colors | 2 = queue bubbles
//        3 = Loudoun County annotation

import * as d3 from "npm:d3@7";
import * as topojson from "npm:topojson-client@3";
import { INK, INK_LIGHT, ACCENT, CONTEXT, RULE, PAPER, ISO_COLOR } from "../design.js";
import { showTip, moveTip, hideTip } from "../tooltip.js";

// State FIPS to ISO mapping
const stateToISO = {
  "VA":"PJM","MD":"PJM","PA":"PJM","OH":"PJM","WV":"PJM","DE":"PJM",
  "NJ":"PJM","IL":"PJM","IN":"PJM","MI":"PJM","NC":"PJM","KY":"PJM",
  "TN":"PJM","DC":"PJM",
  "MN":"MISO","WI":"MISO","IA":"MISO","MO":"MISO","AR":"MISO","LA":"MISO",
  "ND":"MISO","SD":"MISO","MS":"MISO",
  "TX":"ERCOT", "CA":"CAISO",
  "KS":"SPP","NE":"SPP","OK":"SPP",
  "NY":"NYISO",
  "CT":"ISO-NE","MA":"ISO-NE","ME":"ISO-NE","NH":"ISO-NE","RI":"ISO-NE","VT":"ISO-NE",
  "AL":"Non-ISO Southeast","FL":"Non-ISO Southeast","GA":"Non-ISO Southeast","SC":"Non-ISO Southeast",
  "AZ":"Non-ISO West","CO":"Non-ISO West","ID":"Non-ISO West","NV":"Non-ISO West",
  "NM":"Non-ISO West","OR":"Non-ISO West","UT":"Non-ISO West","WA":"Non-ISO West",
  "WY":"Non-ISO West","MT":"Non-ISO West",
};

// FIPS to state postal code
const fipsToPostal = {
  "01":"AL","02":"AK","04":"AZ","05":"AR","06":"CA","08":"CO","09":"CT","10":"DE",
  "11":"DC","12":"FL","13":"GA","15":"HI","16":"ID","17":"IL","18":"IN","19":"IA",
  "20":"KS","21":"KY","22":"LA","23":"ME","24":"MD","25":"MA","26":"MI","27":"MN",
  "28":"MS","29":"MO","30":"MT","31":"NE","32":"NV","33":"NH","34":"NJ","35":"NM",
  "36":"NY","37":"NC","38":"ND","39":"OH","40":"OK","41":"OR","42":"PA","44":"RI",
  "45":"SC","46":"SD","47":"TN","48":"TX","49":"UT","50":"VT","51":"VA","53":"WA",
  "54":"WV","55":"WI","56":"WY",
};

// ISO centroids for bubble placement
const isoCentroids = {
  "PJM": [-81.0, 39.5], "MISO": [-90.0, 43.0], "ERCOT": [-98.0, 31.0],
  "CAISO": [-119.5, 36.5], "SPP": [-97.0, 38.0], "NYISO": [-75.5, 42.6],
  "ISO-NE": [-72.0, 43.5], "Non-ISO Southeast": [-85.0, 33.0],
  "Non-ISO West": [-114.0, 43.0],
};

export function createISOQueueMap(geoData, queue) {
  const W = Math.min(820, (document.body?.clientWidth ?? 820) - 40);
  const H = 500;

  // Filter out AK, HI, territories
  const excludeFips = new Set(["02", "15", "60", "66", "69", "72", "78"]);
  const states = topojson.feature(geoData, geoData.objects.states);
  states.features = states.features.filter(f => !excludeFips.has(f.id));

  const projection = d3.geoAlbersUsa().fitSize([W - 20, H - 60], states);
  const path = d3.geoPath(projection);

  const svg = d3.create("svg").attr("width", "100%").attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif");

  // Build queue GW lookup
  const queueGW = {};
  queue.region.forEach(d => { queueGW[d.region] = d.queue_gw; });
  const maxGW = d3.max(queue.region, d => d.queue_gw);

  // State paths — initially gray, colored by ISO on step 1
  const statePaths = svg.append("g").selectAll("path")
    .data(states.features)
    .join("path")
      .attr("d", path)
      .attr("fill", PAPER)
      .attr("stroke", "white")
      .attr("stroke-width", 0.6);

  // Queue bubbles — initially hidden
  const bubblesG = svg.append("g");

  const isoKeys = Object.keys(isoCentroids);
  const bubbles = isoKeys.map(iso => {
    const coord = isoCentroids[iso];
    const proj = projection(coord);
    if (!proj) return null;

    const gw = queueGW[iso] || 0;
    const r = Math.sqrt(gw / maxGW) * 42;

    const g = bubblesG.append("g").attr("opacity", 0);

    g.append("circle")
      .attr("cx", proj[0]).attr("cy", proj[1]).attr("r", r)
      .attr("fill", "white").attr("opacity", 0.55)
      .attr("stroke", INK).attr("stroke-width", 1);

    g.append("text")
      .attr("x", proj[0]).attr("y", proj[1] - 2)
      .attr("text-anchor", "middle").attr("fill", INK).attr("font-size", "11")
      .attr("font-weight", "700").text(`${gw}`);

    g.append("text")
      .attr("x", proj[0]).attr("y", proj[1] + 11)
      .attr("text-anchor", "middle").attr("fill", INK_LIGHT).attr("font-size", "9")
      .text("GW");

    // Hit target
    g.append("circle")
      .attr("cx", proj[0]).attr("cy", proj[1]).attr("r", Math.max(r, 20))
      .attr("fill", "transparent").style("cursor", "crosshair")
      .on("mouseover", (e) => showTip(e, iso, `Queue backlog: ${gw} GW`))
      .on("mousemove", moveTip)
      .on("mouseout", hideTip);

    return { g, iso };
  }).filter(Boolean);

  // Loudoun County annotation — initially hidden
  const loudounG = svg.append("g").attr("opacity", 0);
  const loudounCoord = projection([-77.63, 39.08]);
  if (loudounCoord) {
    loudounG.append("path")
      .attr("d", d3.symbol(d3.symbolStar, 180)())
      .attr("transform", `translate(${loudounCoord[0]},${loudounCoord[1]})`)
      .attr("fill", ACCENT).attr("stroke", "white").attr("stroke-width", 0.8);

    loudounG.append("text")
      .attr("x", loudounCoord[0] - 15).attr("y", loudounCoord[1] - 14)
      .attr("text-anchor", "end").attr("fill", ACCENT).attr("font-size", "10")
      .attr("font-weight", "600").text("Loudoun Co. (N. Virginia)");
  }

  // Legend
  const legendG = svg.append("g").attr("transform", `translate(${10}, ${H - 120})`);
  const legendItems = Object.entries(ISO_COLOR);
  legendItems.forEach(([iso, color], i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const lx = col * 140;
    const ly = row * 16;
    legendG.append("rect").attr("x", lx).attr("y", ly).attr("width", 10).attr("height", 10)
      .attr("fill", color).attr("opacity", 0.6).attr("rx", 1);
    legendG.append("text").attr("x", lx + 14).attr("y", ly + 9)
      .attr("fill", INK_LIGHT).attr("font-size", "9.5").text(iso);
  });
  legendG.attr("opacity", 0);

  // Source
  svg.append("text").attr("x", 10).attr("y", H - 4)
    .attr("fill", CONTEXT).attr("font-size", "9")
    .text("Source: LBNL 'Queued Up' 2025; ISO/RTO territory boundaries");

  // ── Step control ────────────────────────────────────────────────────────
  function update(step) {
    // Step 0: just gray boundaries
    if (step === 0) {
      statePaths.transition().duration(400).attr("fill", PAPER).attr("stroke", RULE);
      legendG.transition().duration(300).attr("opacity", 0);
      bubbles.forEach(b => b.g.transition().duration(300).attr("opacity", 0));
      loudounG.transition().duration(300).attr("opacity", 0);
    }

    // Step 1: ISO territory colors
    if (step >= 1) {
      statePaths.transition().duration(600)
        .attr("fill", (d) => {
          const postal = fipsToPostal[d.id];
          const iso = stateToISO[postal];
          return iso ? (ISO_COLOR[iso] || CONTEXT) : PAPER;
        })
        .attr("fill-opacity", 0.45)
        .attr("stroke", "white");
      legendG.transition().duration(300).attr("opacity", 1);
    }

    // Step 2: queue bubbles
    if (step >= 2) {
      bubbles.forEach((b, i) => {
        b.g.transition().delay(i * 50).duration(400)
          .attr("opacity", 1);
      });
    } else {
      bubbles.forEach(b => b.g.transition().duration(300).attr("opacity", 0));
    }

    // Step 3: Loudoun annotation
    loudounG.transition().duration(300).attr("opacity", step >= 3 ? 1 : 0);
  }

  return { node: svg.node(), update };
}
