// ── Chart: Interconnection queue growth — stacked bar ────────────────────
// Shows total GW in the US interconnection queue, split by generation
// and storage. Highlights that most projects never get built.
// Steps: 0 = bars grow | 1 = completion stat callout | 2 = gas growth note

import * as d3 from "../../../_npm/d3@7.9.0/e324157d.js";
import { INK, INK_LIGHT, ACCENT, CONTEXT, RULE, chartW } from "../design.2d3db129.js";
import { showTip, moveTip, hideTip } from "../tooltip.40aee997.js";

export function createQueueGrowth(data, stats) {
  const queue = data.queue_ts;

  const W = chartW(620);
  const H = 354;
  const ml = 50, mr = 24, mt = 52, mb = 70;

  const x = d3.scaleBand()
    .domain(queue.map(d => d.year))
    .range([ml, W - mr]).padding(0.35);
  const yMax = d3.max(queue, d => d.total_gw) * 1.18;
  const y = d3.scaleLinear().domain([0, yMax]).range([H - mb, mt]);

  const svg = d3.create("svg")
    .attr("width", "100%").attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif");

  // ── Title + subtitle ────────────────────────────────────────────────────
  svg.append("text").attr("x", ml).attr("y", 16)
    .attr("fill", INK).attr("font-size", "13").attr("font-weight", "700")
    .text("The grid connection waiting list tripled in five years");
  svg.append("text").attr("x", ml).attr("y", 30)
    .attr("fill", INK_LIGHT).attr("font-size", "10.5")
    .text("U.S. interconnection queue 2018–2024 (GW) · only 21% of projects historically reach operation");

  // Baseline
  svg.append("line").attr("x1", ml).attr("x2", W - mr)
    .attr("y1", H - mb).attr("y2", H - mb)
    .attr("stroke", RULE).attr("stroke-width", 1);

  // Y axis labels
  [0, 500, 1000, 1500, 2000, 2500, 3000].filter(v => v <= yMax).forEach(v => {
    svg.append("text").attr("x", ml - 6).attr("y", y(v) + 4)
      .attr("text-anchor", "end").attr("fill", INK_LIGHT).attr("font-size", "10")
      .text(`${(v / 1000).toFixed(v >= 1000 ? 1 : 0)}k`);
  });

  // X axis
  queue.forEach(d => {
    svg.append("text").attr("x", x(d.year) + x.bandwidth() / 2).attr("y", H - mb + 14)
      .attr("text-anchor", "middle").attr("fill", INK_LIGHT).attr("font-size", "10.5")
      .text(d.year);
  });

  // Stacked bars — generation (gray) + storage (accent)
  const genBars = [];
  const storageBars = [];
  const totalLabels = [];

  queue.forEach(d => {
    const bx = x(d.year);
    const bw = x.bandwidth();
    const genH = y(0) - y(d.generation_gw);
    const storH = y(0) - y(d.storage_gw);

    // Generation bar (bottom)
    const genBar = svg.append("rect")
      .attr("x", bx).attr("y", H - mb).attr("width", bw).attr("height", 0)
      .attr("fill", CONTEXT).attr("rx", 1).style("cursor", "crosshair");
    genBar
      .on("mouseover", (e) => showTip(e, `${d.year} Generation`, `${d.generation_gw.toLocaleString()} GW`))
      .on("mousemove", moveTip).on("mouseout", hideTip);
    genBars.push({ bar: genBar, finalY: y(d.generation_gw), finalH: genH });

    // Storage bar (top, stacked)
    const storBar = svg.append("rect")
      .attr("x", bx).attr("y", y(d.generation_gw)).attr("width", bw).attr("height", 0)
      .attr("fill", ACCENT).attr("rx", 1).style("cursor", "crosshair");
    storBar
      .on("mouseover", (e) => showTip(e, `${d.year} Storage`, `${d.storage_gw.toLocaleString()} GW`))
      .on("mousemove", moveTip).on("mouseout", hideTip);
    storageBars.push({ bar: storBar, finalY: y(d.total_gw), finalH: storH });

    // Total label above bar — starts hidden
    const tl = svg.append("text")
      .attr("x", bx + bw / 2).attr("y", y(d.total_gw) - 6)
      .attr("text-anchor", "middle").attr("fill", INK)
      .attr("font-size", "11").attr("font-weight", "600")
      .attr("opacity", 0).text(`${d.total_gw.toLocaleString()}`);
    totalLabels.push(tl);
  });

  // Completion stat callout — starts hidden
  const statBox = svg.append("g").attr("opacity", 0);
  const boxX = ml + 10;
  const boxY = mt + 10;
  statBox.append("rect")
    .attr("x", boxX).attr("y", boxY)
    .attr("width", 200).attr("height", 42)
    .attr("fill", "white").attr("stroke", CONTEXT)
    .attr("rx", 3).attr("opacity", 0.9);
  statBox.append("text")
    .attr("x", boxX + 10).attr("y", boxY + 16)
    .attr("fill", INK).attr("font-size", "10.5")
    .text(`Of all capacity queued 2000\u20132024:`);
  statBox.append("text")
    .attr("x", boxX + 10).attr("y", boxY + 32)
    .attr("fill", INK).attr("font-size", "10.5").attr("font-weight", "600")
    .text(`${stats.queue_withdrawal_pct}% withdrawn, ${stats.queue_completion_pct}% completed`);

  // Legend
  const legY = H - mb + 28;
  [{ fill: CONTEXT, text: "Generation" },
   { fill: ACCENT,  text: "Storage" }]
    .forEach((l, i) => {
      svg.append("rect").attr("x", ml + i * 120).attr("y", legY - 6)
        .attr("width", 10).attr("height", 10).attr("fill", l.fill).attr("rx", 1);
      svg.append("text").attr("x", ml + i * 120 + 14).attr("y", legY + 3)
        .attr("fill", INK_LIGHT).attr("font-size", "10").text(l.text);
    });

  // Source
  svg.append("text").attr("x", ml).attr("y", H - 4)
    .attr("fill", CONTEXT).attr("font-size", "9")
    .text("GW in queue at year-end  \u00B7  Source: LBNL \u201CQueued Up\u201D 2025 Edition");

  // ── Step control ──────────────────────────────────────────────────────────
  function update(step) {
    // Step 0: bars grow up
    genBars.forEach(({ bar, finalY, finalH }, i) => {
      bar.interrupt();
      if (step === 0) {
        bar.attr("y", H - mb).attr("height", 0)
          .transition().delay(200 + i * 100).duration(600).ease(d3.easeQuadOut)
          .attr("y", finalY).attr("height", finalH);
      } else {
        bar.attr("y", finalY).attr("height", finalH);
      }
    });
    storageBars.forEach(({ bar, finalY, finalH }, i) => {
      bar.interrupt();
      if (step === 0) {
        bar.attr("height", 0)
          .transition().delay(300 + i * 100).duration(600).ease(d3.easeQuadOut)
          .attr("y", finalY).attr("height", finalH);
      } else {
        bar.attr("y", finalY).attr("height", finalH);
      }
    });

    // Total labels appear with bars
    totalLabels.forEach((tl, i) => {
      tl.transition().delay(step === 0 ? 600 + i * 100 : 0).duration(300)
        .attr("opacity", step >= 0 ? 1 : 0);
    });

    // Step 1: completion stats
    statBox.transition().duration(400).attr("opacity", step >= 1 ? 1 : 0);

    // Step 2: highlight latest bar
    genBars.forEach(({ bar }, i) => {
      bar.transition().duration(300)
        .attr("opacity", step >= 2 && i < genBars.length - 1 ? 0.4 : 1);
    });
    storageBars.forEach(({ bar }, i) => {
      bar.transition().duration(300)
        .attr("opacity", step >= 2 && i < storageBars.length - 1 ? 0.4 : 1);
    });
  }

  return { node: svg.node(), update };
}
