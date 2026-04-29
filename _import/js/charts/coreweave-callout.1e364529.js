// ── Chart: CoreWeave concentration — three-number stat display ────────────
// Shows three key risk metrics for the CoreWeave chain:
// customer concentration (62% Microsoft), borrowing cost, and total
// OpenAI compute commitment. Static display — no scroll steps.

import * as d3 from "../../../_npm/d3@7.9.0/e324157d.js";
import { INK, INK_LIGHT, CONTEXT, RULE, NEGATIVE, PAPER, chartW } from "../design.2d3db129.js";

export function createCoreweaveCallout(stats) {
  const MSFT_SHARE_PCT = 62;  // CoreWeave S-1/A, March 2025

  const metrics = [
    {
      value: `${MSFT_SHARE_PCT}%`,
      label: "of 2024 revenue from",
      label2: "one customer (Microsoft)",
      sub: "CoreWeave S-1/A, March 2025",
      highlight: true,
    },
    {
      value: `${stats.coreweave_interest_rate_pct}%+`,
      label: "borrowing cost on",
      label2: "new high-yield debt",
      sub: "GPU-backed financing, S&P analysis",
      highlight: false,
    },
    {
      value: `$${stats.openai_coreweave_commitment_bn.toFixed(0)}B`,
      label: "OpenAI compute",
      label2: "commitment (up to)",
      sub: "CoreWeave S-1/A, Table of RPOs",
      highlight: false,
    },
  ];

  const W = chartW(820);
  const H = 138;
  const pad = 16;
  const colW = (W - pad * 2) / 3;

  const svg = d3.create("svg")
    .attr("width", "100%").attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif");

  metrics.forEach((m, i) => {
    const x0 = pad + colW * i + 5;
    const cx = pad + colW * i + colW / 2;

    // Box
    svg.append("rect")
      .attr("x", x0).attr("y", 8)
      .attr("width", colW - 10).attr("height", H - 16)
      .attr("fill", m.highlight ? "#fdf0ee" : PAPER)
      .attr("stroke", m.highlight ? NEGATIVE : RULE)
      .attr("stroke-width", m.highlight ? 1.5 : 1)
      .attr("rx", 4);

    // Big number
    svg.append("text").attr("x", cx).attr("y", 55)
      .attr("text-anchor", "middle")
      .attr("fill", m.highlight ? NEGATIVE : INK)
      .attr("font-size", "30").attr("font-weight", "700")
      .text(m.value);

    // Label line 1
    svg.append("text").attr("x", cx).attr("y", 73)
      .attr("text-anchor", "middle")
      .attr("fill", INK).attr("font-size", "10.5")
      .text(m.label);

    // Label line 2
    svg.append("text").attr("x", cx).attr("y", 87)
      .attr("text-anchor", "middle")
      .attr("fill", INK).attr("font-size", "10.5")
      .text(m.label2);

    // Source sub-label
    svg.append("text").attr("x", cx).attr("y", 106)
      .attr("text-anchor", "middle")
      .attr("fill", INK_LIGHT).attr("font-size", "8.5")
      .text(m.sub);
  });

  // Source line
  svg.append("text").attr("x", pad).attr("y", H - 3)
    .attr("fill", CONTEXT).attr("font-size", "8.5")
    .text("Source: CoreWeave S-1/A, March 2025 (SEC EDGAR CIK\u00A00001956029); S&P credit analysis");

  return svg.node();
}
