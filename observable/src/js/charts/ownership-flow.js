// ── Ownership Flow: PE Fund → HoldCo → Utility → Ratepayers ────────────────
// Animated SVG path diagram showing capital flow right, exit arrow left.
// Scroll reveals: PE fund → flow to HoldCo/Utility → flow to Ratepayers → exit arrow.

import * as d3 from "npm:d3@7";
import { INK, INK_LIGHT, ACCENT, CONTEXT, RULE, RATEPAYER, PAPER, chartW } from "../design.js";

export function createOwnershipFlow() {
  const W = chartW(820);
  const H = 254;

  const svg = d3.create("svg")
    .attr("width", "100%")
    .attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif");

  // ── Title + subtitle ────────────────────────────────────────────────────
  svg.append("text").attr("x", 16).attr("y", 16)
    .attr("fill", INK).attr("font-size", "13").attr("font-weight", "700")
    .text("A PE fund acquires a utility. The ratepayer obligation outlasts the fund.");
  svg.append("text").attr("x", 16).attr("y", 30)
    .attr("fill", INK_LIGHT).attr("font-size", "10.5")
    .text("Capital flows right from fund to ratepayers · PE fund exits in 7–10 years · grid assets last 30–40");

  const nodes = [
    { label: "PE Fund", sub: "7\u201310 yr lifecycle", x: 0.1, color: ACCENT },
    { label: "HoldCo", sub: "Tax structure", x: 0.33, color: INK_LIGHT },
    { label: "Regulated\nUtility", sub: "30\u201340 yr assets", x: 0.56, color: RATEPAYER },
    { label: "Ratepayers", sub: "Indefinite", x: 0.80, color: RATEPAYER },
  ];

  const nodeY = H * 0.45;
  const boxW = 100, boxH = 52;

  // Node boxes
  const nodeGroups = nodes.map((n, i) => {
    const g = svg.append("g")
      .attr("transform", `translate(${n.x * W}, ${nodeY})`)
      .attr("opacity", 0);

    g.append("rect")
      .attr("x", -boxW / 2).attr("y", -boxH / 2)
      .attr("width", boxW).attr("height", boxH)
      .attr("rx", 4)
      .attr("fill", "white")
      .attr("stroke", n.color).attr("stroke-width", 2);

    const lines = n.label.split("\n");
    lines.forEach((line, li) => {
      g.append("text")
        .attr("y", -boxH / 2 + 18 + li * 14)
        .attr("text-anchor", "middle")
        .attr("fill", INK).attr("font-size", 12).attr("font-weight", 600)
        .text(line);
    });

    g.append("text")
      .attr("y", boxH / 2 + 14)
      .attr("text-anchor", "middle")
      .attr("fill", INK_LIGHT).attr("font-size", 10)
      .text(n.sub);

    return g;
  });

  // Flow arrows (right-pointing)
  const arrows = [];
  for (let i = 0; i < nodes.length - 1; i++) {
    const x1 = nodes[i].x * W + boxW / 2 + 4;
    const x2 = nodes[i + 1].x * W - boxW / 2 - 4;
    const arrowG = svg.append("g").attr("opacity", 0);

    arrowG.append("line")
      .attr("x1", x1).attr("y1", nodeY)
      .attr("x2", x2).attr("y2", nodeY)
      .attr("stroke", CONTEXT).attr("stroke-width", 2)
      .attr("marker-end", "url(#arrow)");

    // Label on arrow
    const flowLabel = i === 0 ? "Capital" : i === 1 ? "Rates" : "Bills";
    arrowG.append("text")
      .attr("x", (x1 + x2) / 2).attr("y", nodeY - 10)
      .attr("text-anchor", "middle")
      .attr("fill", INK_LIGHT).attr("font-size", 9)
      .text(flowLabel);

    arrows.push(arrowG);
  }

  // Exit arrow (left-pointing, dashed — PE exits)
  const exitArrow = svg.append("g").attr("opacity", 0);
  const exitY = nodeY - boxH / 2 - 24;
  exitArrow.append("path")
    .attr("d", `M${nodes[0].x * W},${exitY} L${nodes[0].x * W - 60},${exitY}`)
    .attr("stroke", ACCENT).attr("stroke-width", 2)
    .attr("stroke-dasharray", "5,3")
    .attr("marker-end", "url(#arrow-exit)");

  exitArrow.append("text")
    .attr("x", nodes[0].x * W - 30).attr("y", exitY - 8)
    .attr("text-anchor", "middle")
    .attr("fill", ACCENT).attr("font-size", 10).attr("font-weight", 500)
    .text("EXIT");

  // Ratepayer obligation persistence indicator
  const persist = svg.append("g").attr("opacity", 0);
  persist.append("text")
    .attr("x", nodes[3].x * W).attr("y", exitY)
    .attr("text-anchor", "middle")
    .attr("fill", RATEPAYER).attr("font-size", 10).attr("font-weight", 500)
    .text("Obligation persists");

  // Arrow markers
  const defs = svg.append("defs");
  defs.append("marker")
    .attr("id", "arrow").attr("viewBox", "0 0 10 6")
    .attr("refX", 9).attr("refY", 3)
    .attr("markerWidth", 8).attr("markerHeight", 6)
    .attr("orient", "auto")
    .append("path").attr("d", "M0,0 L10,3 L0,6 Z").attr("fill", CONTEXT);

  defs.append("marker")
    .attr("id", "arrow-exit").attr("viewBox", "0 0 10 6")
    .attr("refX", 1).attr("refY", 3)
    .attr("markerWidth", 8).attr("markerHeight", 6)
    .attr("orient", "auto")
    .append("path").attr("d", "M10,0 L0,3 L10,6 Z").attr("fill", ACCENT);

  // Source
  svg.append("text")
    .attr("x", 10).attr("y", H - 4)
    .attr("fill", CONTEXT).attr("font-size", 9)
    .text("Source: FERC filings; regulatory structure illustrative");

  // ── Update ──────────────────────────────────────────────────────────────
  function update(step) {
    const t = svg.transition().duration(400);

    // Step 0: PE Fund only
    nodeGroups[0].transition(t).attr("opacity", step >= 0 ? 1 : 0);

    // Step 1: HoldCo and Utility appear, first two arrows
    nodeGroups[1].transition(t).attr("opacity", step >= 1 ? 1 : 0);
    nodeGroups[2].transition(t).attr("opacity", step >= 1 ? 1 : 0);
    arrows[0].transition(t).attr("opacity", step >= 1 ? 1 : 0);
    arrows[1].transition(t).attr("opacity", step >= 1 ? 1 : 0);

    // Step 2: Ratepayers appear
    nodeGroups[3].transition(t).attr("opacity", step >= 2 ? 1 : 0);
    arrows[2].transition(t).attr("opacity", step >= 2 ? 1 : 0);

    // Step 3: Exit arrow + persistence
    exitArrow.transition(t).attr("opacity", step >= 3 ? 1 : 0);
    persist.transition(t).attr("opacity", step >= 3 ? 1 : 0);
  }

  return { node: svg.node(), update };
}
