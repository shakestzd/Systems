// ── Chart: FERC AD24-11 — two cost-allocation paths ──────────────────────
// Side-by-side comparison showing who pays transmission upgrade costs and
// who bears stranded-asset risk under each regulatory outcome.
// Steps: 0 = headers + "who pays" row | 1 = "if demand disappoints" row |
//        2 = FERC status note (no final rule)

import * as d3 from "../../../_npm/d3@7.9.0/e324157d.js";
import { INK, INK_LIGHT, CONTEXT, RULE, NEGATIVE, POSITIVE, PAPER, svgTitle, svgStepAnnot, svgSource, chartW } from "../design.2d3db129.js";

export function createFercAllocation() {
  const W = chartW(820);
  const H = 348;
  const pad = 16, mt = 50, mb = 110;
  const colW = (W - pad * 2) / 2 - 6;
  const leftX  = pad;
  const rightX = pad + colW + 12;

  const ROW_H = 72;

  const svg = d3.create("svg")
    .attr("width", "100%").attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif")
    .style("overflow", "visible");

  // ── Title + subtitle ────────────────────────────────────────────────────
  svgTitle(svg, W, {
    x: pad,
    title: "FERC AD24-11 — Two regulatory paths, opposite loss distributions",
    subtitle: "Beneficiary-pays vs. socialized cost recovery for transmission upgrades",
  });

  function makeColumn(anchorX, title, headerColor, rows) {
    const headerBox = svg.append("rect")
      .attr("x", anchorX).attr("y", mt)
      .attr("width", colW).attr("height", 28)
      .attr("fill", headerColor).attr("rx", 3).attr("opacity", 0);

    const headerText = svg.append("text")
      .attr("x", anchorX + colW / 2).attr("y", mt + 18)
      .attr("text-anchor", "middle").attr("fill", "white")
      .attr("font-size", "11").attr("font-weight", "600").attr("opacity", 0)
      .text(title);

    const rowEls = rows.map((row, ri) => {
      const ry = mt + 28 + ri * ROW_H;

      const box = svg.append("rect")
        .attr("x", anchorX).attr("y", ry)
        .attr("width", colW).attr("height", ROW_H - 2)
        .attr("fill", PAPER).attr("stroke", headerColor).attr("stroke-width", 0.8)
        .attr("rx", 0).attr("opacity", 0);

      const rowCap = svg.append("text")
        .attr("x", anchorX + 8).attr("y", ry + 15)
        .attr("fill", INK_LIGHT).attr("font-size", "8.5").attr("font-weight", "700")
        .attr("letter-spacing", "0.04em").attr("opacity", 0)
        .text(row.cap.toUpperCase());

      const line1 = svg.append("text")
        .attr("x", anchorX + 8).attr("y", ry + 31)
        .attr("fill", INK).attr("font-size", "10.5")
        .attr("opacity", 0).text(row.line1);

      const line2 = svg.append("text")
        .attr("x", anchorX + 8).attr("y", ry + 46)
        .attr("fill", INK).attr("font-size", "10.5")
        .attr("opacity", 0).text(row.line2);

      const outcome = svg.append("text")
        .attr("x", anchorX + 8).attr("y", ry + ROW_H - 10)
        .attr("fill", headerColor).attr("font-size", "9.5").attr("font-weight", "600")
        .attr("opacity", 0).text(row.outcome);

      return { box, rowCap, line1, line2, outcome };
    });

    return { headerBox, headerText, rowEls };
  }

  const leftCol = makeColumn(leftX, "Beneficiary-pays", POSITIVE, [
    {
      cap: "Who pays",
      line1: "Hyperscalers fund transmission",
      line2: "upgrades their load triggers",
      outcome: "→ Decision-maker holds the cost",
    },
    {
      cap: "If AI demand disappoints",
      line1: "Tech giants absorb stranded",
      line2: "transmission investment",
      outcome: "→ Ratepayers are protected",
    },
  ]);

  const rightCol = makeColumn(rightX, "Public-benefit / socialized", NEGATIVE, [
    {
      cap: "Who pays",
      line1: "Transmission costs spread across",
      line2: "all regional ratepayers",
      outcome: "→ Ratepayers fund private buildout",
    },
    {
      cap: "If AI demand disappoints",
      line1: "Ratepayers absorb stranded grid",
      line2: "capacity built for data centers",
      outcome: "→ Communities bear the loss",
    },
  ]);

  // (FERC status note retired — folded into the step annotation strip below.)

  // ── Source ──────────────────────────────────────────────────────────────
  svgSource(svg, W, H, "Source: FERC AD24-11 (ferc.gov eLibrary); FERC Order 2023; author’s analysis");

  // ── Step annotation — bottom strip (article narrative) ──────────────────
  const STEP_ANNOTS = [
    "Under beneficiary-pays, tech giants fund the transmission upgrades their load triggers. If they don't build, the cost sits with them.",
    "Under the current default, costs spread across all ratepayers. If AI demand disappoints, communities absorb stranded grid capacity built for data centers.",
    "FERC opened AD24-11 in May 2024. No Final Rule has been issued. Utilities building for Rainier-class loads are recovering costs under the pre-AD24-11 default.",
  ];
  const stepAnnot = svgStepAnnot(svg, { y: H - mb + 30, W, ml: pad });

  function update(step) {
    // Step 0: both headers + row 0
    [leftCol, rightCol].forEach(col => {
      col.headerBox.transition().duration(350).attr("opacity", step >= 0 ? 1 : 0);
      col.headerText.transition().duration(350).attr("opacity", step >= 0 ? 1 : 0);
    });

    [leftCol, rightCol].forEach(col => {
      col.rowEls.forEach((row, ri) => {
        const revealAt = ri;   // row 0 at step 0, row 1 at step 1
        const vis = step >= revealAt ? 1 : 0;
        const delay = step === revealAt ? 80 : 0;
        [row.box, row.rowCap, row.line1, row.line2].forEach(el =>
          el.transition().delay(delay).duration(300).attr("opacity", vis));
        row.outcome.transition().delay(step === revealAt ? delay + 180 : 0)
          .duration(300).attr("opacity", vis);
      });
    });

    // Step annotation strip carries the narrative including the FERC status note at step 2
    stepAnnot.update(step, STEP_ANNOTS);
  }

  return { node: svg.node(), update };
}
