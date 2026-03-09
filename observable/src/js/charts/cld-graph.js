// ── Chart: Causal Loop Diagram (force-directed) — DD-002 ────────────────
// Interactive force-directed graph. Nodes draggable. Scroll highlights loops.
// Steps: 0 = all loops | 1 = R1 (Grid Investment) | 2 = R2 (Renewable)
//        3 = B2 (BTM Bypass) | 4 = Regulatory node pulses

import * as d3 from "npm:d3@7";
import { INK, INK_LIGHT, ACCENT, CONTEXT, RULE, PAPER, LOOP } from "../design.js";
import { showTip, moveTip, hideTip } from "../tooltip.js";

const NODES = [
  { id: "AI\nDemand", fx: 0, fy: -140 },
  { id: "Grid\nInvestment", fx: -120, fy: -60 },
  { id: "Grid\nCapacity", fx: -170, fy: 30 },
  { id: "Energy\nCosts", fx: -120, fy: 100 },
  { id: "Renewable\nPPAs", fx: 120, fy: -60 },
  { id: "Renewable\nCost", fx: 170, fy: 30 },
  { id: "BTM\nCapacity", fx: 50, fy: 40 },
  { id: "Queue\nBacklog", fx: -30, fy: 10 },
  { id: "Regulatory\nEnvironment", fx: 0, fy: 130 },
  { id: "Ratepayer\nBurden", fx: -80, fy: 175 },
  { id: "Political\nSupport", fx: 80, fy: 175 },
];

const EDGES = [
  // R1: Grid Investment Cycle
  { source: "AI\nDemand", target: "Grid\nInvestment", polarity: "+", loop: "R1" },
  { source: "Grid\nInvestment", target: "Grid\nCapacity", polarity: "+", loop: "R1" },
  { source: "Grid\nCapacity", target: "Energy\nCosts", polarity: "-", loop: "R1" },
  { source: "Energy\nCosts", target: "AI\nDemand", polarity: "-", loop: "R1" },
  // R2: Renewable Learning
  { source: "AI\nDemand", target: "Renewable\nPPAs", polarity: "+", loop: "R2" },
  { source: "Renewable\nPPAs", target: "Renewable\nCost", polarity: "-", loop: "R2" },
  { source: "Renewable\nCost", target: "Renewable\nPPAs", polarity: "-", loop: "R2" },
  // B1: Regulatory Uncertainty
  { source: "Regulatory\nEnvironment", target: "Grid\nInvestment", polarity: "+", loop: "B1" },
  { source: "Regulatory\nEnvironment", target: "BTM\nCapacity", polarity: "-", loop: "B1" },
  // B2: BTM Bypass
  { source: "Queue\nBacklog", target: "BTM\nCapacity", polarity: "+", loop: "B2" },
  { source: "BTM\nCapacity", target: "Ratepayer\nBurden", polarity: "+", loop: "B2" },
  { source: "Ratepayer\nBurden", target: "Political\nSupport", polarity: "-", loop: "B2" },
  { source: "Political\nSupport", target: "Regulatory\nEnvironment", polarity: "+", loop: "B2" },
  // B3: Stranded Asset Risk
  { source: "Regulatory\nEnvironment", target: "Queue\nBacklog", polarity: "-", loop: "B3" },
];

export function createCLDGraph() {
  const W = Math.min(820, (document.body?.clientWidth ?? 820) - 40);
  const H = 500;
  const cx = W / 2, cy = H / 2 - 10;

  const svg = d3.create("svg").attr("width", "100%").attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif");

  // ── Title + subtitle ────────────────────────────────────────────────────
  svg.append("text").attr("x", 16).attr("y", 16)
    .attr("fill", INK).attr("font-size", "13").attr("font-weight", "700")
    .text("Four feedback loops shape the AI grid buildout");
  svg.append("text").attr("x", 16).attr("y", 30)
    .attr("fill", INK_LIGHT).attr("font-size", "10.5")
    .text("R1 = Grid Investment cycle · R2 = Renewable learning · B2 = BTM bypass · B3 = Stranded asset risk");

  // Background
  svg.append("rect").attr("width", W).attr("height", H).attr("fill", "transparent");

  // Build simulation-compatible node/edge data
  const nodeMap = {};
  const nodes = NODES.map(n => {
    const obj = { id: n.id, x: cx + n.fx, y: cy + n.fy, fx: cx + n.fx, fy: cy + n.fy };
    nodeMap[n.id] = obj;
    return obj;
  });

  const edges = EDGES.map(e => ({
    ...e,
    source: nodeMap[e.source],
    target: nodeMap[e.target],
  }));

  // Defs for arrow markers by loop
  const defs = svg.append("defs");
  Object.entries(LOOP).forEach(([key, color]) => {
    defs.append("marker")
      .attr("id", `arrow-${key}`).attr("viewBox", "0 0 10 10")
      .attr("refX", 28).attr("refY", 5).attr("markerWidth", 8).attr("markerHeight", 8)
      .attr("orient", "auto")
      .append("path").attr("d", "M0,0 L10,5 L0,10 Z").attr("fill", color);
  });

  // Edges (curved links)
  const edgeG = svg.append("g");
  const linkEls = edges.map(e => {
    const color = LOOP[e.loop] || CONTEXT;
    const path = edgeG.append("path")
      .attr("fill", "none").attr("stroke", color).attr("stroke-width", 2)
      .attr("marker-end", `url(#arrow-${e.loop})`)
      .attr("opacity", 0.7);

    // Polarity label at midpoint
    const label = edgeG.append("text")
      .attr("fill", color).attr("font-size", "12").attr("font-weight", "700")
      .attr("text-anchor", "middle").attr("opacity", 0.8);

    return { path, label, edge: e, color };
  });

  // Update link paths
  function updateLinks() {
    linkEls.forEach(({ path, label, edge }) => {
      const dx = edge.target.x - edge.source.x;
      const dy = edge.target.y - edge.source.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      const offset = 22; // Node radius
      const sx = edge.source.x + offset * dx / dist;
      const sy = edge.source.y + offset * dy / dist;
      const tx = edge.target.x - offset * dx / dist;
      const ty = edge.target.y - offset * dy / dist;

      // Slight curve
      const mx = (sx + tx) / 2 - dy * 0.08;
      const my = (sy + ty) / 2 + dx * 0.08;

      path.attr("d", `M${sx},${sy} Q${mx},${my} ${tx},${ty}`);
      label.attr("x", mx).attr("y", my - 6).text(edge.polarity);
    });
  }

  // Nodes
  const nodeG = svg.append("g");
  const nodeEls = nodes.map(n => {
    const g = nodeG.append("g").attr("transform", `translate(${n.x},${n.y})`);

    const circle = g.append("circle").attr("r", 22)
      .attr("fill", "white").attr("stroke", INK).attr("stroke-width", 1.8);

    g.append("text")
      .attr("text-anchor", "middle").attr("fill", INK)
      .attr("font-size", "9.5").attr("font-weight", "600")
      .selectAll("tspan")
      .data(n.id.split("\n"))
      .join("tspan")
        .attr("x", 0).attr("dy", (_, i) => i === 0 ? -4 : 12)
        .text(d => d);

    // Drag behavior
    const drag = d3.drag()
      .on("drag", (event) => {
        n.x = event.x; n.y = event.y;
        n.fx = event.x; n.fy = event.y;
        g.attr("transform", `translate(${n.x},${n.y})`);
        updateLinks();
      });

    g.call(drag).style("cursor", "grab");

    // Tooltip
    g.on("mouseover", (e) => showTip(e, n.id.replace("\n", " ")))
      .on("mousemove", moveTip)
      .on("mouseout", hideTip);

    return { g, circle, node: n };
  });

  updateLinks();

  // Loop labels
  const loopLabels = [
    { id: "R1", x: cx - 80, y: cy - 20 },
    { id: "R2", x: cx + 155, y: cy - 20 },
    { id: "B1", x: cx - 60, y: cy + 65 },
    { id: "B2", x: cx + 25, y: cy + 100 },
    { id: "B3", x: cx - 20, y: cy + 30 },
  ];

  const loopLabelEls = loopLabels.map(l => {
    const g = svg.append("g").attr("transform", `translate(${l.x},${l.y})`);
    g.append("circle").attr("r", 14)
      .attr("fill", "white").attr("stroke", LOOP[l.id]).attr("stroke-width", 1.5)
      .attr("opacity", 0.7);
    g.append("text").attr("text-anchor", "middle").attr("dy", 4)
      .attr("fill", LOOP[l.id]).attr("font-size", "11").attr("font-weight", "700")
      .text(l.id);
    return { g, id: l.id };
  });

  // Legend at bottom
  const legendY = H - 30;
  const loopNames = {
    R1: "Grid Investment", R2: "Renewable Learning",
    B1: "Reg. Uncertainty", B2: "BTM Bypass", B3: "Stranded Risk",
  };
  Object.entries(LOOP).forEach(([key, color], i) => {
    const lx = 10 + i * (W / 5.2);
    svg.append("rect").attr("x", lx).attr("y", legendY).attr("width", 12).attr("height", 3)
      .attr("fill", color);
    svg.append("text").attr("x", lx + 16).attr("y", legendY + 4)
      .attr("fill", INK_LIGHT).attr("font-size", "9.5").text(`${key}: ${loopNames[key]}`);
  });

  // Source
  svg.append("text").attr("x", 10).attr("y", H - 5)
    .attr("fill", CONTEXT).attr("font-size", "9")
    .text("Source: Author's causal loop diagram; PySD model");

  // ── Step control ────────────────────────────────────────────────────────
  function setLoopFocus(focusLoop) {
    linkEls.forEach(({ path, label, edge, color }) => {
      if (focusLoop === null || edge.loop === focusLoop) {
        path.transition().duration(300).attr("opacity", 0.7).attr("stroke-width", 2.5);
        label.transition().duration(300).attr("opacity", 0.8);
      } else {
        path.transition().duration(300).attr("opacity", 0.08).attr("stroke-width", 1);
        label.transition().duration(300).attr("opacity", 0.08);
      }
    });

    loopLabelEls.forEach(({ g, id }) => {
      g.transition().duration(300)
        .attr("opacity", focusLoop === null || id === focusLoop ? 1 : 0.15);
    });
  }

  function update(step) {
    // Reset node pulse
    nodeEls.forEach(({ circle }) => {
      circle.interrupt().attr("stroke-width", 1.8).attr("stroke", INK);
    });

    if (step === 0) {
      setLoopFocus(null);
    } else if (step === 1) {
      setLoopFocus("R1");
    } else if (step === 2) {
      setLoopFocus("R2");
    } else if (step === 3) {
      setLoopFocus("B2");
    } else if (step === 4) {
      setLoopFocus(null);
      // Pulse the Regulatory Environment node
      const regNode = nodeEls.find(n => n.node.id === "Regulatory\nEnvironment");
      if (regNode) {
        regNode.circle
          .transition().duration(400).attr("stroke-width", 4).attr("stroke", ACCENT)
          .transition().duration(400).attr("stroke-width", 2).attr("stroke", ACCENT)
          .transition().duration(400).attr("stroke-width", 4).attr("stroke", ACCENT)
          .transition().duration(400).attr("stroke-width", 2).attr("stroke", ACCENT);
      }
    }
  }

  return { node: svg.node(), update };
}
