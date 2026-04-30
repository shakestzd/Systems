// ── Chart: Project Rainier progress — progress bar + timeline ────────────
// Shows the Amazon/Anthropic campus: 7 of 30 buildings complete.
// Top half: horizontal stacked bar. Bottom half: milestone dots.
// Steps: 0 = progress bar draws | 1 = milestones appear | 2 = grid impact

import * as d3 from "npm:d3@7";
import { INK, INK_LIGHT, ACCENT, CONTEXT, RULE, svgTitle, svgStepAnnot, svgSource, chartW } from "../design.js";
import { showTip, moveTip, hideTip } from "../tooltip.js";

export function createRainierProgress(stats) {
  const built = stats.rainier_dc_built_jun2025;
  const planned = stats.rainier_dc_planned;
  const remaining = planned - built;
  const pctDone = Math.round(built / planned * 100);

  const W = chartW(720);
  const H = 414;
  const ml = 16, mr = 80, mt = 54, mb = 132;

  const svg = d3.create("svg")
    .attr("width", "100%").attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif")
    .style("overflow", "visible");

  // ── Title + subtitle ────────────────────────────────────────────────────
  svgTitle(svg, W, {
    title: `Project Rainier: ${built} of ${planned} buildings complete, two years in`,
    subtitle: "Amazon / Anthropic campus, New Carlisle, Indiana · as of June 2025",
  });

  // ── Top: progress bar ───────────────────────────────────────────────────
  const barY = mt + 20;
  const barH = 36;
  const barW = W - ml - mr - 80;
  const builtW = barW * (built / planned);
  const remainW = barW - builtW;

  // Background (full)
  svg.append("rect")
    .attr("x", ml).attr("y", barY)
    .attr("width", barW).attr("height", barH)
    .attr("fill", CONTEXT).attr("opacity", 0.15).attr("rx", 3);

  // Built portion — starts at 0 width
  const builtBar = svg.append("rect")
    .attr("x", ml).attr("y", barY)
    .attr("width", 0).attr("height", barH)
    .attr("fill", ACCENT).attr("rx", 3).style("cursor", "crosshair");
  builtBar
    .on("mouseover", (e) => showTip(e, `${built} buildings built`, `As of June 2025`, `Each larger than a football stadium`))
    .on("mousemove", moveTip).on("mouseout", hideTip);

  // "Built" label inside the bar
  const builtLabel = svg.append("text")
    .attr("x", ml + builtW / 2).attr("y", barY + barH / 2 + 5)
    .attr("text-anchor", "middle").attr("fill", "white")
    .attr("font-size", "12").attr("font-weight", "600")
    .attr("opacity", 0).text(`${built} built`);

  // "Remaining" label
  const remainLabel = svg.append("text")
    .attr("x", ml + builtW + remainW / 2).attr("y", barY + barH / 2 + 5)
    .attr("text-anchor", "middle").attr("fill", CONTEXT)
    .attr("font-size", "11").attr("opacity", 0)
    .text(`${remaining} remaining`);

  // Pct complete label at right
  const pctLabel = svg.append("text")
    .attr("x", ml + barW + 10).attr("y", barY + barH / 2 + 5)
    .attr("fill", INK).attr("font-size", "12").attr("font-weight", "600")
    .attr("opacity", 0).text(`${pctDone}%`);

  // ── Bottom: milestone timeline ──────────────────────────────────────────
  const timeY = barY + barH + 56;
  const milestones = [
    { year: 2023.0, label: "ChatGPT launches\nutility talks begin", active: false },
    { year: 2024.0, label: "Land acquired\nsite cleared",         active: false },
    { year: 2025.5, label: `${built} of ${planned} DCs\noperating (Jun 2025)`, active: true },
    { year: 2027.0, label: "Full campus\nestimated",              active: false },
  ];

  const tx = d3.scaleLinear().domain([2022.5, 2028]).range([ml, W - mr - 40]);

  // Timeline line
  svg.append("line")
    .attr("x1", tx(2022.5)).attr("x2", tx(2028))
    .attr("y1", timeY).attr("y2", timeY)
    .attr("stroke", CONTEXT).attr("stroke-width", 2).attr("opacity", 0.3);

  const mileEls = milestones.map(m => {
    const dot = svg.append("circle")
      .attr("cx", tx(m.year)).attr("cy", timeY)
      .attr("r", m.active ? 7 : 5)
      .attr("fill", m.active ? ACCENT : CONTEXT)
      .attr("opacity", 0);

    const lines = m.label.split("\n");
    const labelG = svg.append("g").attr("opacity", 0);
    lines.forEach((line, li) => {
      labelG.append("text")
        .attr("x", tx(m.year)).attr("y", timeY - 14 - (lines.length - 1 - li) * 12)
        .attr("text-anchor", "middle")
        .attr("fill", m.active ? ACCENT : INK_LIGHT)
        .attr("font-size", "9.5")
        .attr("font-weight", m.active ? "600" : "normal")
        .text(line);
    });

    return { dot, labelG };
  });

  // Grid impact annotation — starts hidden
  const gridImpact = svg.append("g").attr("opacity", 0);
  gridImpact.append("text")
    .attr("x", tx(2027)).attr("y", timeY + 22)
    .attr("text-anchor", "middle").attr("fill", ACCENT)
    .attr("font-size", "10").attr("font-weight", "600")
    .text(`${stats.rainier_gw} GW campus = ~half of Indiana\u2019s projected load growth`);
  gridImpact.append("text")
    .attr("x", tx(2027)).attr("y", timeY + 36)
    .attr("text-anchor", "middle").attr("fill", INK_LIGHT)
    .attr("font-size", "9")
    .text(`AEP plans ${stats.aep_gas_share_pct}% gas to meet the additional demand`);

  // ── Source ──────────────────────────────────────────────────────────────
  svgSource(svg, W, H, "Source: NYT, Jun 24, 2025 (Weise & Metz); AEP Indiana filings");

  // ── Step annotation — bottom strip ─────────────────────────────────────────
  const STEP_ANNOTS = [
    `${built} of ${planned} data center buildings complete after roughly two years of construction. Each is larger than a football stadium.`,
    "The timeline: utility talks began in early 2023. Land acquired early 2024. First buildings operating mid-2025. Full campus estimated 2027.",
    `At ${stats.rainier_gw} gigawatts, this single campus accounts for about half of Indiana's projected electricity demand growth. American Electric Power plans to meet ${stats.aep_gas_share_pct}% of that new demand with natural gas.`,
  ];
  const annot = svgStepAnnot(svg, { y: H - mb + 50, W, ml });

  // ── Step control ──────────────────────────────────────────────────────────
  function update(step) {
    // Step 0: progress bar
    builtBar.interrupt();
    if (step === 0) {
      builtBar.attr("width", 0)
        .transition().delay(200).duration(800).ease(d3.easeQuadOut)
        .attr("width", builtW);
      builtLabel.transition().delay(600).duration(300).attr("opacity", 1);
      remainLabel.transition().delay(800).duration(300).attr("opacity", 1);
      pctLabel.transition().delay(900).duration(300).attr("opacity", 1);
    } else {
      builtBar.attr("width", builtW);
      builtLabel.attr("opacity", 1);
      remainLabel.attr("opacity", 1);
      pctLabel.attr("opacity", 1);
    }

    // Step 1: milestones
    mileEls.forEach(({ dot, labelG }, i) => {
      dot.transition().delay(step === 1 ? i * 150 : 0).duration(300)
        .attr("opacity", step >= 1 ? 1 : 0);
      labelG.transition().delay(step === 1 ? i * 150 + 100 : 0).duration(300)
        .attr("opacity", step >= 1 ? 1 : 0);
    });

    // Step 2: grid impact
    gridImpact.transition().duration(400).attr("opacity", step >= 2 ? 1 : 0);

    annot.update(step, STEP_ANNOTS);
  }

  return { node: svg.node(), update };
}
