// ── Liability Taxonomy: Asset lifetime vs. liability holder ─────────────────
// The most important chart in DD-004. Horizontal bars ordered by asset life.
// Two vertical reference lines: AI forecast horizon (3yr) and PE fund lifecycle (7-10yr).
// Scroll reveals: hyperscaler-owned → ratepayer-owned → public → PE band → AI horizon.

import * as d3 from "npm:d3@7";
import { INK, INK_LIGHT, ACCENT, CONTEXT, RULE, RATEPAYER, PUBLIC, PAPER, NEGATIVE, chartW } from "../design.js";
import { showTip, moveTip, hideTip } from "../tooltip.js";

export function createLiabilityTaxonomy(stats) {
  const W = chartW(820);
  const H = 414;
  const ml = 170, mr = 90, mt = 58, mb = 50;

  const assets = [
    { label: "Server hardware (IT)", life: 6, holder: "Hyperscaler", color: ACCENT, group: "hyperscaler" },
    { label: "Network equipment", life: 8, holder: "Hyperscaler", color: ACCENT, group: "hyperscaler" },
    { label: "Data center building", life: 40, holder: "Hyperscaler", color: ACCENT, group: "hyperscaler" },
    { label: `Gas CTs (${(stats.gas_ct_mw ?? 1650).toLocaleString()} MW)`, life: 28, holder: "All ratepayers", color: RATEPAYER, group: "ratepayer" },
    { label: `Oregon NGCC (${stats.oregon_mw ?? 870} MW)`, life: 32, holder: "All ratepayers", color: RATEPAYER, group: "ratepayer" },
    { label: "Substation upgrades", life: 35, holder: "All ratepayers", color: RATEPAYER, group: "ratepayer" },
    { label: "Transmission lines", life: 40, holder: "All ratepayers", color: RATEPAYER, group: "ratepayer" },
    { label: "Tax abatements", life: 15, holder: "Public (sunk)", color: PUBLIC, group: "public" },
  ];

  const x = d3.scaleLinear().domain([0, 50]).range([ml, W - mr]);
  const y = d3.scaleBand().domain(assets.map((_, i) => i)).range([mt, H - mb]).padding(0.28);

  const svg = d3.create("svg")
    .attr("width", "100%")
    .attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif");

  // ── Title + subtitle ────────────────────────────────────────────────────
  svg.append("text").attr("x", ml).attr("y", 16)
    .attr("fill", INK).attr("font-size", "13").attr("font-weight", "700")
    .text("Short-lived assets sit on hyperscaler books. Long-lived ones sit on yours.");
  svg.append("text").attr("x", ml).attr("y", 30)
    .attr("fill", INK_LIGHT).attr("font-size", "10.5")
    .text("Asset lifetime (years) · orange = hyperscaler-owned · teal = all ratepayers · gray = public subsidy");

  // X axis
  svg.append("g")
    .attr("transform", `translate(0,${H - mb})`)
    .call(d3.axisBottom(x).ticks(6).tickSize(0))
    .call(g => g.select(".domain").attr("stroke", RULE))
    .call(g => g.selectAll("text").attr("fill", INK_LIGHT).attr("font-size", 11));

  svg.append("text")
    .attr("x", (ml + W - mr) / 2).attr("y", H - 8)
    .attr("text-anchor", "middle").attr("fill", INK_LIGHT).attr("font-size", 11)
    .text("Asset Lifetime (years)");

  // PE fund lifecycle band (7-10 years) — initially hidden
  const peBand = svg.append("rect")
    .attr("x", x(7)).attr("y", mt)
    .attr("width", x(10) - x(7)).attr("height", H - mt - mb)
    .attr("fill", ACCENT).attr("opacity", 0);

  const peLabel = svg.append("text")
    .attr("x", x(8.5)).attr("y", mt - 4)
    .attr("text-anchor", "middle").attr("fill", ACCENT).attr("font-size", 10)
    .attr("font-weight", 500).attr("opacity", 0)
    .text("PE fund lifecycle (7\u201310 yr)");

  // AI forecast horizon line — initially hidden
  const aiLine = svg.append("line")
    .attr("x1", x(3)).attr("x2", x(3))
    .attr("y1", mt).attr("y2", H - mb)
    .attr("stroke", NEGATIVE).attr("stroke-width", 1.5)
    .attr("stroke-dasharray", "5,3").attr("opacity", 0);

  const aiLabel = svg.append("text")
    .attr("x", x(3) + 4).attr("y", mt + 12)
    .attr("fill", NEGATIVE).attr("font-size", 10).attr("opacity", 0)
    .text("AI forecast horizon (3 yr)");

  // Bars
  const barGroups = svg.selectAll(".bar-group")
    .data(assets).join("g")
    .attr("class", "bar-group")
    .attr("opacity", 0);

  barGroups.append("rect")
    .attr("x", ml)
    .attr("y", (_, i) => y(i))
    .attr("width", d => x(d.life) - ml)
    .attr("height", y.bandwidth())
    .attr("fill", d => d.color)
    .attr("rx", 2);

  // Y-axis labels
  barGroups.append("text")
    .attr("x", ml - 8)
    .attr("y", (_, i) => y(i) + y.bandwidth() / 2)
    .attr("text-anchor", "end").attr("dominant-baseline", "central")
    .attr("fill", INK).attr("font-size", 11)
    .text(d => d.label);

  // End labels: "Xyr — Holder"
  const endLabels = barGroups.append("text")
    .attr("x", d => x(d.life) + 5)
    .attr("y", (_, i) => y(i) + y.bandwidth() / 2)
    .attr("dominant-baseline", "central")
    .attr("fill", INK_LIGHT).attr("font-size", 10)
    .text(d => `${d.life} yr — ${d.holder}`);

  // Invisible hit targets for tooltips
  barGroups.append("rect")
    .attr("x", ml)
    .attr("y", (_, i) => y(i))
    .attr("width", d => Math.max(x(d.life) - ml, 40))
    .attr("height", y.bandwidth())
    .attr("fill", "transparent")
    .style("cursor", "crosshair")
    .on("mouseover", (e, d) => {
      showTip(e, d.label, `Lifetime: ${d.life} years`, `Liability: ${d.holder}`);
    })
    .on("mousemove", moveTip)
    .on("mouseout", hideTip);

  // Source text
  svg.append("text")
    .attr("x", ml).attr("y", H - 3)
    .attr("fill", CONTEXT).attr("font-size", 9)
    .text("Source: IURC Cause 46097, 46217, 46301; industry standard depreciation schedules");

  // ── Update function ─────────────────────────────────────────────────────
  function update(step) {
    const t = svg.transition().duration(450);

    // Step 0: Hyperscaler-owned assets only
    barGroups.transition(t)
      .attr("opacity", (d) => {
        if (step === 0) return d.group === "hyperscaler" ? 1 : 0;
        if (step === 1) return 1;
        return 1;
      });

    // Step 1: All asset bars visible
    // Step 2: Tax abatement highlighted
    if (step >= 2) {
      barGroups.select("rect:first-child").transition(t)
        .attr("opacity", d => d.group === "public" ? 1 : 0.7);
    } else {
      barGroups.select("rect:first-child").transition(t).attr("opacity", 1);
    }

    // Step 3: PE fund lifecycle band
    peBand.transition(t).attr("opacity", step >= 3 ? 0.12 : 0);
    peLabel.transition(t).attr("opacity", step >= 3 ? 1 : 0);

    // Step 4: AI forecast horizon line
    aiLine.transition(t).attr("opacity", step >= 4 ? 0.9 : 0);
    aiLabel.transition(t).attr("opacity", step >= 4 ? 1 : 0);
  }

  return { node: svg.node(), update };
}
