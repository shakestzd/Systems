// ── Chart: Off-balance-sheet commitments ──────────────────────────────────
// Returns { node, update } for use with mountScrollChart.
// Steps: 0 = reported bars only | 1 = off-balance bars appear | 2 = totals

import * as d3 from "npm:d3@7";
import { INK, INK_LIGHT, ACCENT, CONTEXT, RULE } from "../design.js";
import { showTip, moveTip, hideTip } from "../tooltip.js";

export function createOffBalance(stats) {
  const obsData = [
    { company: "Microsoft", reported: stats.msft_2025, offbs: stats.msft_neocloud_total_bn ?? 50 },
    { company: "Meta",      reported: stats.meta_2025, offbs: stats.meta_beignet_financing_bn ?? 30 },
  ];

  const W = Math.min(520, (document.body?.clientWidth ?? 520) - 40);
  const H = 384;
  const ml = 55, mr = 40, mt = 58, mb = 120;
  const isMobile = W < 380;

  const yMax = Math.max(...obsData.map(d => d.reported + d.offbs)) * 1.18;
  const x = d3.scaleBand().domain(obsData.map(d => d.company)).range([ml, W - mr]).padding(0.45);
  const y = d3.scaleLinear().domain([0, yMax]).range([H - mb, mt]);

  const svg = d3.create("svg").attr("width", "100%").attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif");

  // ── Title + subtitle ────────────────────────────────────────────────────
  svg.append("text").attr("x", ml).attr("y", 16)
    .attr("fill", INK).attr("font-size", "13").attr("font-weight", "700")
    .text("Reported capex understates actual commitments");
  svg.append("text").attr("x", ml).attr("y", 30)
    .attr("fill", INK_LIGHT).attr("font-size", "10.5")
    .text("2025 reported capex plus off-balance-sheet lease and SPV commitments, Sep–Nov 2025");

  svg.append("line").attr("x1", ml).attr("x2", W - mr).attr("y1", H - mb).attr("y2", H - mb)
    .attr("stroke", RULE).attr("stroke-width", 1);

  const defs = svg.append("defs");
  const rBars = [], oBars = [], labGs = [];

  obsData.forEach(d => {
    const bx = x(d.company);
    const bw = x.bandwidth();
    const rFinalY = y(d.reported), rFinalH = y(0) - y(d.reported);
    const oFinalY = y(d.reported + d.offbs), oFinalH = y(d.reported) - y(d.reported + d.offbs);

    // Reported bar
    const rBar = svg.append("rect")
      .attr("x", bx).attr("y", H - mb).attr("width", bw).attr("height", 0)
      .attr("fill", CONTEXT).style("cursor", "crosshair");
    rBar.on("mouseover", (e) => { rBar.attr("opacity", 0.75); showTip(e, `${d.company} · reported capex`, `$${d.reported.toFixed(0)}B (2025)`); })
        .on("mousemove", moveTip).on("mouseout", () => { rBar.attr("opacity", 1); hideTip(); });
    rBars.push({ bar: rBar, finalY: rFinalY, finalH: rFinalH });

    // Off-balance bar — start hidden (height 0)
    const oBar = svg.append("rect")
      .attr("x", bx).attr("y", oFinalY).attr("width", bw).attr("height", 0)
      .attr("fill", ACCENT).attr("opacity", 0.8).style("cursor", "crosshair");
    oBar.on("mouseover", (e) => { oBar.attr("opacity", 1); showTip(e, `${d.company} · off-balance-sheet`, `$${d.offbs.toFixed(0)}B in leases / SPVs`); })
        .on("mousemove", moveTip).on("mouseout", () => { oBar.attr("opacity", 0.8); hideTip(); });
    oBars.push({ bar: oBar, finalY: oFinalY, finalH: oFinalH });

    // Hatch overlay
    const pid = `h-${d.company.replace(" ", "")}`;
    const pat = defs.append("pattern").attr("id", pid).attr("width", 6).attr("height", 6)
      .attr("patternUnits", "userSpaceOnUse").attr("patternTransform", "rotate(45)");
    pat.append("line").attr("x1", 0).attr("y1", 0).attr("x2", 0).attr("y2", 6)
      .attr("stroke", "white").attr("stroke-width", 2.5).attr("opacity", 0.4);
    const hatchRect = svg.append("rect")
      .attr("x", bx).attr("y", oFinalY).attr("width", bw).attr("height", Math.max(oFinalH, 0))
      .attr("fill", `url(#${pid})`).attr("opacity", 0);

    // Reported inner label
    const labG1 = svg.append("g").attr("opacity", 0);
    labG1.append("text").attr("x", bx + bw/2).attr("y", y(d.reported/2)).attr("dominant-baseline", "middle")
      .attr("text-anchor", "middle").attr("fill", "white").attr("font-size", "12").attr("font-weight", "700")
      .text(`$${d.reported.toFixed(0)}B`);
    labG1.append("text").attr("x", bx + bw/2).attr("y", y(d.reported/2) + 14).attr("dominant-baseline", "middle")
      .attr("text-anchor", "middle").attr("fill", "white").attr("font-size", "10.5").text(isMobile ? "reported" : "reported capex");

    // Off-balance inner label
    const labG2 = svg.append("g").attr("opacity", 0);
    labG2.append("text").attr("x", bx + bw/2).attr("y", y(d.reported + d.offbs/2)).attr("dominant-baseline", "middle")
      .attr("text-anchor", "middle").attr("fill", "white").attr("font-size", "12").attr("font-weight", "700")
      .text(`+$${d.offbs.toFixed(0)}B`);
    labG2.append("text").attr("x", bx + bw/2).attr("y", y(d.reported + d.offbs/2) + 14).attr("dominant-baseline", "middle")
      .attr("text-anchor", "middle").attr("fill", "white").attr("font-size", "10.5").text(isMobile ? "off-balance" : "off-balance-sheet");

    // Total label above both bars
    const totalT = svg.append("text").attr("x", bx + bw/2).attr("y", oFinalY - 7)
      .attr("text-anchor", "middle").attr("fill", INK).attr("font-size", "12.5").attr("font-weight", "700")
      .attr("opacity", 0).text(`$${(d.reported + d.offbs).toFixed(0)}B total`);

    svg.append("text").attr("x", bx + bw/2).attr("y", H - mb + 14)
      .attr("text-anchor", "middle").attr("fill", INK_LIGHT).attr("font-size", "12").text(d.company);

    labGs.push({ labG1, labG2, totalT, hatchRect });
  });

  // Y axis
  [0, 50, 100, 150].filter(v => v <= yMax).forEach(v => {
    svg.append("text").attr("x", ml - 6).attr("y", y(v) + 4)
      .attr("text-anchor", "end").attr("fill", INK_LIGHT).attr("font-size", "11")
      .text(`$${v}B`);
  });

  // Legend
  [{ fill: CONTEXT, text: "Reported 2025 capex" },
   { fill: ACCENT,  text: "Off-balance-sheet commitments (Sep–Nov 2025)" }]
    .forEach((l, i) => {
      svg.append("rect").attr("x", ml).attr("y", H - 62 + i * 22).attr("width", 12).attr("height", 12)
        .attr("fill", l.fill).attr("rx", 1);
      svg.append("text").attr("x", ml + 16).attr("y", H - 51 + i * 22)
        .attr("fill", INK_LIGHT).attr("font-size", "10").text(l.text);
    });

  svg.append("text").attr("x", ml).attr("y", H - 12)
    .attr("fill", INK_LIGHT).attr("font-size", "9")
    .text("Source: NYT Dec 15, 2025 (Weise & Tan); company announcements");

  // ── Step annotation — inline text replaces floating callout ───────────────
  const STEP_ANNOTS = [
    "Reported capex as disclosed in 2025 SEC filings",
    "Long-term leases and SPV financing add billions not disclosed in filings",
    `True 2025 commitment: $${(obsData[0].reported + obsData[0].offbs).toFixed(0)}B (Microsoft), $${(obsData[1].reported + obsData[1].offbs).toFixed(0)}B (Meta)`,
  ];
  const stepAnnot = svg.append("text")
    .attr("x", ml).attr("y", H - mb + 32)
    .attr("fill", INK).attr("font-size", "11")
    .attr("font-style", "italic").attr("opacity", 0);

  // ── Step control ──────────────────────────────────────────────────────────
  function update(step) {
    if (step === 0) {
      // Animate reported bars from scratch
      rBars.forEach(({ bar, finalY, finalH }) =>
        bar.interrupt().attr("y", H - mb).attr("height", 0)
          .transition().delay(200).duration(800).ease(d3.easeQuadOut)
          .attr("y", finalY).attr("height", finalH));
      labGs.forEach(({ labG1 }) =>
        labG1.interrupt().attr("opacity", 0)
          .transition().delay(700).duration(300).attr("opacity", 1));
      // Reset off-balance elements
      oBars.forEach(({ bar, finalY }) => bar.interrupt().attr("y", finalY).attr("height", 0));
      labGs.forEach(({ labG2, hatchRect, totalT }) =>
        [labG2, hatchRect, totalT].forEach(el => el.interrupt().attr("opacity", 0)));

    } else if (step === 1) {
      // Reported bars fully drawn
      rBars.forEach(({ bar, finalY, finalH }) =>
        bar.interrupt().attr("y", finalY).attr("height", finalH));
      labGs.forEach(({ labG1 }) => labG1.attr("opacity", 1));
      // Animate off-balance bars
      oBars.forEach(({ bar, finalY, finalH }) =>
        bar.interrupt().attr("y", finalY).attr("height", 0)
          .transition().delay(200).duration(650).ease(d3.easeQuadOut)
          .attr("height", finalH));
      labGs.forEach(({ labG2, hatchRect }) => {
        labG2.transition().delay(600).duration(300).attr("opacity", 1);
        hatchRect.transition().delay(600).duration(300).attr("opacity", 1);
      });
      // No totals yet
      labGs.forEach(({ totalT }) => totalT.interrupt().attr("opacity", 0));

    } else {
      // step >= 2: everything drawn, total labels appear
      rBars.forEach(({ bar, finalY, finalH }) =>
        bar.interrupt().attr("y", finalY).attr("height", finalH));
      oBars.forEach(({ bar, finalY, finalH }) =>
        bar.interrupt().attr("y", finalY).attr("height", finalH));
      labGs.forEach(({ labG1, labG2, hatchRect }) =>
        [labG1, labG2, hatchRect].forEach(el => el.attr("opacity", 1)));
      labGs.forEach(({ totalT }) =>
        totalT.interrupt().attr("opacity", 0)
          .transition().delay(200).duration(400).attr("opacity", 1));
    }

    // Step annotation
    if (step >= 0 && step < STEP_ANNOTS.length) {
      stepAnnot.text(STEP_ANNOTS[step]).transition().duration(350).attr("opacity", 0.85);
    } else {
      stepAnnot.interrupt().attr("opacity", 0);
    }
  }

  return { node: svg.node(), update };
}
