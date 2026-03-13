// ── Chart: SPV (Beignet) risk chain — flow diagram ──────────────────────
// Shows how Meta offloads financial exposure through a special purpose
// vehicle: Meta → Beignet LLC → Blue Owl → Pimco → pension funds.
// Built as connected D3 node boxes with animated path edges.
// Steps: 0 = Meta node | 1 = SPV path | 2 = credit path | 3 = lock-in label

import * as d3 from "npm:d3@7";
import { INK, INK_LIGHT, ACCENT, CONTEXT, RULE, NEGATIVE, NEUTRAL, chartW } from "../design.js";
import { showTip, moveTip, hideTip } from "../tooltip.js";

export function createSpvChain(stats) {
  const W = chartW(820);
  const H = 360;
  const ml = 16, mr = 16, mt = 20, mb = 32;

  const svg = d3.create("svg")
    .attr("width", "100%").attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif");

  // ── Title + subtitle ────────────────────────────────────────────────────
  svg.append("text").attr("x", ml).attr("y", 14)
    .attr("fill", INK).attr("font-size", "13").attr("font-weight", "700")
    .text("How Meta moves risk downstream");

  svg.append("text").attr("x", ml).attr("y", 28)
    .attr("fill", INK_LIGHT).attr("font-size", "10")
    .text("A shell company keeps the debt off Meta\u2019s books while pension funds absorb the long-term exposure");

  // Node positions — arranged left to right
  const nodes = [
    { id: "meta",  x: 0.08, y: 0.28, w: 0.14, h: 0.22,
      label: "Meta\n(Tech Giant)", color: CONTEXT, textColor: INK,
      tip: `Can exit ~${stats.meta_beignet_exit_year} via ${stats.meta_beignet_lease_years}-yr lease terms` },
    { id: "spv",   x: 0.30, y: 0.28, w: 0.14, h: 0.22,
      label: "Beignet\nInvestor LLC\n(SPV)", color: NEUTRAL, textColor: "white",
      tip: "Ring-fenced project entity" },
    { id: "bo",    x: 0.52, y: 0.28, w: 0.14, h: 0.22,
      label: "Blue Owl\nCapital\n80% financing", color: NEUTRAL, textColor: "white",
      tip: "Provided 80% of project financing" },
    { id: "pimco", x: 0.74, y: 0.28, w: 0.14, h: 0.22,
      label: "Pimco\nBlackRock\nbond underwriters", color: NEUTRAL, textColor: "white",
      tip: "Sold bonds to institutional investors" },
    { id: "inst",  x: 0.74, y: 0.62, w: 0.14, h: 0.18,
      label: "Pension Funds\nEndowments\nInsurers", color: NEGATIVE, textColor: "white",
      tip: `Bonds locked to ${stats.beignet_bond_maturity}` },
    { id: "dc",    x: 0.08, y: 0.62, w: 0.22, h: 0.18,
      label: `Louisiana DC\n${stats.meta_louisiana_dc_gw} GW \u00B7 $${stats.meta_beignet_financing_bn}B`, color: "white",
      textColor: INK, stroke: CONTEXT,
      tip: "Physical data center asset in Richland Parish, LA" },
  ];

  // Convert fractional positions to pixel positions
  const px = (frac) => ml + frac * (W - ml - mr);
  const py = (frac) => mt + frac * (H - mt - mb);

  // Draw nodes — all start at opacity 0
  const nodeEls = {};
  nodes.forEach(n => {
    const g = svg.append("g").attr("opacity", 0).style("cursor", "crosshair");
    const rx = px(n.x), ry = py(n.y);
    const rw = (W - ml - mr) * n.w, rh = (H - mt - mb) * n.h;

    g.append("rect")
      .attr("x", rx).attr("y", ry)
      .attr("width", rw).attr("height", rh)
      .attr("fill", n.color).attr("rx", 4)
      .attr("stroke", n.stroke ?? "none").attr("stroke-width", n.stroke ? 1.5 : 0);

    const lines = n.label.split("\n");
    lines.forEach((line, li) => {
      g.append("text")
        .attr("x", rx + rw / 2)
        .attr("y", ry + rh / 2 + (li - (lines.length - 1) / 2) * 13)
        .attr("text-anchor", "middle").attr("dominant-baseline", "middle")
        .attr("fill", n.textColor).attr("font-size", "10.5")
        .text(line);
    });

    g.on("mouseover", (e) => showTip(e, n.label.split("\n")[0], n.tip))
      .on("mousemove", moveTip).on("mouseout", hideTip);

    nodeEls[n.id] = { g, cx: rx + rw / 2, cy: ry + rh / 2, rx, ry, rw, rh };
  });

  // Edge paths
  function edgePath(fromId, toId, label, opts = {}) {
    const from = nodeEls[fromId];
    const to = nodeEls[toId];

    let x1, y1, x2, y2;
    // Determine connection points
    if (opts.vertical) {
      x1 = from.cx; y1 = from.ry + from.rh;
      x2 = to.cx;   y2 = to.ry;
    } else {
      x1 = from.rx + from.rw; y1 = from.cy;
      x2 = to.rx;              y2 = to.cy;
    }

    const path = svg.append("line")
      .attr("x1", x1).attr("y1", y1).attr("x2", x1).attr("y2", y1) // start collapsed
      .attr("stroke", opts.color ?? CONTEXT)
      .attr("stroke-width", opts.dashed ? 1.2 : 1.8)
      .attr("stroke-dasharray", opts.dashed ? "4,3" : "none")
      .attr("opacity", 0);

    const midX = (x1 + x2) / 2;
    const midY = (y1 + y2) / 2;
    const lbl = label ? svg.append("text")
      .attr("x", midX).attr("y", midY - 6)
      .attr("text-anchor", "middle").attr("fill", opts.color ?? INK_LIGHT)
      .attr("font-size", "9").attr("opacity", 0).text(label) : null;

    return { path, lbl, x1, y1, x2, y2 };
  }

  const edges = [
    edgePath("meta", "spv", `$${stats.meta_beignet_financing_bn}B`),
    edgePath("spv", "bo", null),
    edgePath("bo", "pimco", "bonds sold to"),
    edgePath("pimco", "inst", null, { vertical: true }),
    edgePath("meta", "dc", `${stats.meta_beignet_lease_years}-yr leases`, { vertical: true, dashed: true }),
    edgePath("spv", "dc", "builds & owns", { vertical: true, dashed: true }),
  ];

  // Lock-in annotation — starts hidden
  const lockLabel = svg.append("text")
    .attr("x", px(0.74) + (W - ml - mr) * 0.07)
    .attr("y", py(0.85) + 10)
    .attr("text-anchor", "middle").attr("fill", NEGATIVE)
    .attr("font-size", "10").attr("font-weight", "600")
    .attr("opacity", 0).text(`Bonds locked to ${stats.beignet_bond_maturity}`);

  // Source
  svg.append("text").attr("x", ml).attr("y", H - 4)
    .attr("fill", CONTEXT).attr("font-size", "9")
    .text("Source: SEC filings; CoreWeave S-1; project finance documents; NYT Dec 2025");

  // ── Step control ──────────────────────────────────────────────────────────
  function animateEdge({ path, lbl, x2, y2 }, delay) {
    path.interrupt().attr("opacity", 0.7)
      .transition().delay(delay).duration(500).ease(d3.easeQuadOut)
      .attr("x2", x2).attr("y2", y2);
    if (lbl) lbl.transition().delay(delay + 300).duration(250).attr("opacity", 1);
  }

  function showEdge({ path, lbl, x2, y2 }) {
    path.attr("x2", x2).attr("y2", y2).attr("opacity", 0.7);
    if (lbl) lbl.attr("opacity", 1);
  }

  function hideEdge({ path, lbl, x1, y1 }) {
    path.attr("x2", x1).attr("y2", y1).attr("opacity", 0);
    if (lbl) lbl.attr("opacity", 0);
  }

  function update(step) {
    // Step 0: Meta node appears
    nodeEls.meta.g.transition().duration(350).attr("opacity", step >= 0 ? 1 : 0);
    nodeEls.dc.g.transition().duration(350).attr("opacity", step >= 0 ? 1 : 0);

    // Step 1: SPV path (Meta → SPV → Blue Owl)
    nodeEls.spv.g.transition().duration(350).attr("opacity", step >= 1 ? 1 : 0);
    nodeEls.bo.g.transition().duration(350).attr("opacity", step >= 1 ? 1 : 0);
    if (step === 1) {
      animateEdge(edges[0], 200);
      animateEdge(edges[1], 400);
      animateEdge(edges[4], 600); // meta → dc
      animateEdge(edges[5], 700); // spv → dc
    } else if (step > 1) {
      [0, 1, 4, 5].forEach(i => showEdge(edges[i]));
    } else {
      [0, 1, 4, 5].forEach(i => hideEdge(edges[i]));
    }

    // Step 2: credit path (Blue Owl → Pimco → Institutions)
    nodeEls.pimco.g.transition().duration(350).attr("opacity", step >= 2 ? 1 : 0);
    nodeEls.inst.g.transition().duration(350).attr("opacity", step >= 2 ? 1 : 0);
    if (step === 2) {
      animateEdge(edges[2], 200);
      animateEdge(edges[3], 500);
    } else if (step > 2) {
      [2, 3].forEach(i => showEdge(edges[i]));
    } else {
      [2, 3].forEach(i => hideEdge(edges[i]));
    }

    // Step 3: lock-in label
    lockLabel.transition().duration(350).attr("opacity", step >= 3 ? 1 : 0);
  }

  return { node: svg.node(), update };
}
