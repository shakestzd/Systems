// ── Chart: Labor feedback loop (animated causal loop diagram) ───────────────
// Returns { node, update } for use with mountScrollChart.
// Steps: 0 = AI Capex node | 1 = DC Construction | 2 = Electrician Demand +
//        Shortage | 3 = Full loop closes back to Capex (deployment lag)

import * as d3 from "../../../_npm/d3@7.9.0/e324157d.js";
import { INK, INK_LIGHT, ACCENT, CONTEXT, RULE, PAPER, OCC_TECH, OCC_TRADES, chartW } from "../design.2d3db129.js";

export function createLaborFeedback(stats) {
  const W = chartW(680);
  const H = 394;

  const svg = d3.create("svg")
    .attr("width", "100%")
    .attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif");

  // ── Title + subtitle ────────────────────────────────────────────────────
  svg.append("text").attr("x", 16).attr("y", 16)
    .attr("fill", INK).attr("font-size", "13").attr("font-weight", "700")
    .text("Electrician shortages feed back into deployment timelines");
  svg.append("text").attr("x", 16).attr("y", 30)
    .attr("fill", INK_LIGHT).attr("font-size", "10.5")
    .text("Causal loop: AI capex → data center construction → electrician demand → shortage → deployment lag");

  // ── Node positions (clockwise from top) ───────────────────────────────────
  const cx = W / 2;
  const cy = H / 2 - 10;
  const rx = 200;
  const ry = 120;

  const nodes = [
    { id: "capex",     label: "AI Capex",                 angle: -Math.PI/2,    color: OCC_TECH,   step: 0 },
    { id: "construct", label: "Data Center\nConstruction", angle: 0,             color: OCC_TRADES, step: 1 },
    { id: "demand",    label: "Electrician\nDemand",       angle: Math.PI/2,     color: ACCENT,     step: 2 },
    { id: "shortage",  label: "Electrician\nShortage",     angle: Math.PI * 0.8, color: ACCENT,     step: 2 },
    { id: "lag",       label: "Deployment\nLag",           angle: Math.PI,       color: INK_LIGHT,  step: 3 },
  ];

  // Position nodes on ellipse
  nodes.forEach(n => {
    n.x = cx + rx * Math.cos(n.angle);
    n.y = cy + ry * Math.sin(n.angle);
  });

  // ── Arrow paths (connecting nodes) ────────────────────────────────────────
  const arrows = [
    { from: "capex",     to: "construct", step: 1, label: "funds" },
    { from: "construct", to: "demand",    step: 2, label: "requires" },
    { from: "demand",    to: "shortage",  step: 2, label: "exceeds\nsupply" },
    { from: "shortage",  to: "lag",       step: 3, label: "causes" },
    { from: "lag",       to: "capex",     step: 3, label: "slows" },
  ];

  const nodeMap = new Map(nodes.map(n => [n.id, n]));

  // ── Draw elements ─────────────────────────────────────────────────────────
  // Arrow group (behind nodes)
  const arrowEls = [];
  arrows.forEach(a => {
    const from = nodeMap.get(a.from);
    const to = nodeMap.get(a.to);

    const g = svg.append("g").attr("opacity", 0);

    // Curved arrow path
    const dx = to.x - from.x;
    const dy = to.y - from.y;
    const dist = Math.sqrt(dx * dx + dy * dy);
    // Shorten by node radius
    const nodeR = 36;
    const ratio = nodeR / dist;
    const sx = from.x + dx * ratio;
    const sy = from.y + dy * ratio;
    const ex = to.x - dx * ratio;
    const ey = to.y - dy * ratio;

    // Control point for slight curve
    const midX = (sx + ex) / 2;
    const midY = (sy + ey) / 2;
    const perpX = -(ey - sy) * 0.15;
    const perpY = (ex - sx) * 0.15;

    const pathD = `M${sx},${sy} Q${midX + perpX},${midY + perpY} ${ex},${ey}`;

    const pathEl = g.append("path")
      .attr("d", pathD)
      .attr("fill", "none")
      .attr("stroke", a.from === "lag" ? ACCENT : CONTEXT)
      .attr("stroke-width", a.from === "lag" ? 2 : 1.5)
      .attr("marker-end", "url(#arrowhead)");

    // Animate with stroke-dasharray
    const totalLen = pathEl.node().getTotalLength();
    pathEl.attr("stroke-dasharray", `0,${totalLen}`);

    // Edge label
    const labelLines = a.label.split("\n");
    labelLines.forEach((line, i) => {
      g.append("text")
        .attr("x", midX + perpX * 0.5)
        .attr("y", midY + perpY * 0.5 - 4 + i * 12)
        .attr("text-anchor", "middle")
        .attr("fill", INK_LIGHT).attr("font-size", "9").attr("font-style", "italic")
        .text(line);
    });

    arrowEls.push({ g, pathEl, totalLen, step: a.step });
  });

  // Arrowhead marker
  const defs = svg.append("defs");
  defs.append("marker")
    .attr("id", "arrowhead")
    .attr("viewBox", "0 0 10 10")
    .attr("refX", 8).attr("refY", 5)
    .attr("markerWidth", 6).attr("markerHeight", 6)
    .attr("orient", "auto-start-reverse")
    .append("path")
    .attr("d", "M 0 0 L 10 5 L 0 10 z")
    .attr("fill", CONTEXT);

  // Node circles + labels (on top)
  const nodeEls = [];
  nodes.forEach(n => {
    const g = svg.append("g").attr("opacity", 0);

    g.append("circle")
      .attr("cx", n.x).attr("cy", n.y)
      .attr("r", 36)
      .attr("fill", PAPER)
      .attr("stroke", n.color).attr("stroke-width", 2);

    const lines = n.label.split("\n");
    lines.forEach((line, i) => {
      g.append("text")
        .attr("x", n.x).attr("y", n.y - (lines.length - 1) * 6 + i * 13 + 1)
        .attr("text-anchor", "middle")
        .attr("fill", n.color).attr("font-size", "10.5").attr("font-weight", "600")
        .text(line);
    });

    nodeEls.push({ g, step: n.step, id: n.id });
  });

  // Loop label (center)
  const loopLabel = svg.append("g").attr("opacity", 0);
  loopLabel.append("text")
    .attr("x", cx).attr("y", cy - 6)
    .attr("text-anchor", "middle").attr("fill", ACCENT)
    .attr("font-size", "14").attr("font-weight", "700")
    .text("B");
  loopLabel.append("text")
    .attr("x", cx).attr("y", cy + 10)
    .attr("text-anchor", "middle").attr("fill", INK_LIGHT)
    .attr("font-size", "10")
    .text("Balancing loop");

  // Apprenticeship annotation
  const apprenticeNote = svg.append("g").attr("opacity", 0);
  const noteX = nodeMap.get("shortage").x - 60;
  const noteY = nodeMap.get("shortage").y + 52;
  apprenticeNote.append("text")
    .attr("x", noteX).attr("y", noteY)
    .attr("fill", ACCENT).attr("font-size", "10").attr("font-weight", "500")
    .text("4-5 year apprenticeship pipeline");
  apprenticeNote.append("text")
    .attr("x", noteX).attr("y", noteY + 13)
    .attr("fill", INK_LIGHT).attr("font-size", "9")
    .text("91% of AGC firms report electrician shortage");

  // Source
  svg.append("text")
    .attr("x", 8).attr("y", H - 4)
    .attr("fill", CONTEXT).attr("font-size", "9")
    .text("Source: TZD Labs systems analysis; AGC workforce survey 2024; IBEW pipeline data");

  // ── Step control ──────────────────────────────────────────────────────────
  function update(step) {
    // Show nodes up to current step
    nodeEls.forEach(n => {
      const show = n.step <= step;
      n.g.transition().duration(show ? 500 : 200)
        .attr("opacity", show ? 1 : 0);
    });

    // Show and animate arrows up to current step
    arrowEls.forEach(a => {
      const show = a.step <= step;
      if (show) {
        a.g.transition().duration(200).attr("opacity", 1);
        a.pathEl.transition().duration(800).ease(d3.easeLinear)
          .attr("stroke-dasharray", `${a.totalLen},${a.totalLen}`);
      } else {
        a.g.transition().duration(200).attr("opacity", 0);
        a.pathEl.attr("stroke-dasharray", `0,${a.totalLen}`);
      }
    });

    // Loop label at final step
    loopLabel.transition().duration(step >= 3 ? 600 : 200)
      .attr("opacity", step >= 3 ? 1 : 0);

    // Apprenticeship note at step 2+
    apprenticeNote.transition().duration(step >= 2 ? 400 : 200)
      .delay(step >= 2 ? 300 : 0)
      .attr("opacity", step >= 2 ? 1 : 0);
  }

  return { node: svg.node(), update };
}
