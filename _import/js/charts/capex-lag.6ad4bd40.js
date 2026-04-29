// ── Chart: Capex-to-Service Lag Proxy (horizontal bars) — DD-002 ──────────
// Shows implied queue-to-service lag by company+region combination.
// Longer bars = more queue congestion per unit of in-service capacity.
// Steps: 0 = all bars grow | 1 = PJM highlight | 2 = all with labels

import * as d3 from "../../../_npm/d3@7.9.0/e324157d.js";
import { INK, INK_LIGHT, ACCENT, CONTEXT, RULE, CO, cl, ISO_COLOR, chartW } from "../design.2d3db129.js";
import { showTip, moveTip, hideTip } from "../tooltip.40aee997.js";

export function createCapexLag(queue) {
  const raw = (queue.lag || []).slice(0, 12); // top 12 entries

  if (raw.length === 0) {
    const el = document.createElement("div");
    el.textContent = "No lag data available.";
    return { node: el, update: () => {} };
  }

  const W = chartW(720);
  const H = 64 + raw.length * 34 + 55;
  const ml = 140, mr = 60, mt = 58, mb = 50;

  const x = d3.scaleLinear()
    .domain([0, d3.max(raw, d => d.implied_lag_years) * 1.15])
    .range([ml, W - mr]);

  const y = d3.scaleBand()
    .domain(raw.map((_, i) => i))
    .range([mt, H - mb])
    .padding(0.25);

  const svg = d3.create("svg")
    .attr("width", "100%")
    .attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif");

  // ── Title + subtitle ────────────────────────────────────────────────────
  svg.append("text").attr("x", ml).attr("y", 16)
    .attr("fill", INK).attr("font-size", "13").attr("font-weight", "700")
    .text("PJM carries the longest queue-to-service lag for every major hyperscaler");
  svg.append("text").attr("x", ml).attr("y", 30)
    .attr("fill", INK_LIGHT).attr("font-size", "10.5")
    .text("Implied years from queue submission to in-service operation · by company and grid region");

  // Baseline
  svg.append("line")
    .attr("x1", ml).attr("x2", W - mr)
    .attr("y1", H - mb).attr("y2", H - mb)
    .attr("stroke", RULE);

  // X-axis ticks
  x.ticks(4).forEach(v => {
    svg.append("text")
      .attr("x", x(v)).attr("y", H - mb + 14)
      .attr("text-anchor", "middle").attr("fill", INK_LIGHT).attr("font-size", "10")
      .text(`${v} yrs`);
    if (v > 0) {
      svg.append("line")
        .attr("x1", x(v)).attr("x2", x(v))
        .attr("y1", mt).attr("y2", H - mb)
        .attr("stroke", RULE).attr("stroke-width", 0.5).attr("opacity", 0.3);
    }
  });

  // Clip for animation
  const defs = svg.append("defs");
  const cpRect = defs.append("clipPath").attr("id", "cp-lag")
    .append("rect").attr("x", ml).attr("y", mt)
    .attr("width", 0).attr("height", H - mt - mb);
  const barsG = svg.append("g").attr("clip-path", "url(#cp-lag)");

  // Bars
  const barEls = raw.map((d, i) => {
    const cy = y(i) + y.bandwidth() / 2;
    const barColor = d.region === "PJM" ? ACCENT : (ISO_COLOR[d.region] || CONTEXT);

    // Row label
    svg.append("text")
      .attr("x", ml - 6).attr("y", cy + 4)
      .attr("text-anchor", "end").attr("fill", INK).attr("font-size", "11")
      .text(`${cl(d.ticker)} / ${d.region}`);

    const bar = barsG.append("rect")
      .attr("x", ml).attr("y", y(i))
      .attr("width", Math.max(x(d.implied_lag_years) - ml, 0))
      .attr("height", y.bandwidth())
      .attr("fill", barColor)
      .attr("rx", 2);

    // Value label (appears on step 2)
    const label = barsG.append("text")
      .attr("x", x(d.implied_lag_years) + 4).attr("y", cy + 4)
      .attr("fill", INK_LIGHT).attr("font-size", "10")
      .attr("opacity", 0)
      .text(`${d.implied_lag_years} yrs`);

    // Invisible hit target
    barsG.append("rect")
      .attr("x", ml).attr("y", y(i))
      .attr("width", Math.max(x(d.implied_lag_years) - ml, 4))
      .attr("height", y.bandwidth())
      .attr("fill", "transparent").style("cursor", "crosshair")
      .on("mouseover", (e) => showTip(e,
        `${cl(d.ticker)} in ${d.region}`,
        `Queue: ${d.queue_gw} GW | Capex: $${d.capex_bn}B | Lag: ${d.implied_lag_years} yrs`
      ))
      .on("mousemove", moveTip)
      .on("mouseout", hideTip);

    return { bar, label, region: d.region };
  });

  // Source
  svg.append("text").attr("x", ml).attr("y", H - 5)
    .attr("fill", CONTEXT).attr("font-size", "9")
    .text("Source: LBNL queue data; EIA in-service capacity; hyperscaler capex filings");

  // ── Step control ────────────────────────────────────────────────────────
  function update(step) {
    if (step === 0) {
      cpRect.interrupt().attr("width", 0);
      barEls.forEach(b => {
        b.bar.attr("opacity", 1);
        b.label.attr("opacity", 0);
      });
      cpRect.transition().delay(100).duration(800).ease(d3.easeQuadOut)
        .attr("width", W - ml - mr);
    } else if (step === 1) {
      cpRect.interrupt().attr("width", W - ml - mr);
      barEls.forEach(b => {
        const isPJM = b.region === "PJM";
        b.bar.transition().duration(300).attr("opacity", isPJM ? 1 : 0.15);
        b.label.transition().duration(300).attr("opacity", isPJM ? 1 : 0);
      });
    } else {
      cpRect.interrupt().attr("width", W - ml - mr);
      barEls.forEach(b => {
        b.bar.transition().duration(300).attr("opacity", 1);
        b.label.transition().delay(200).duration(400).attr("opacity", 1);
      });
    }
  }

  return { node: svg.node(), update };
}
