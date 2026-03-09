// ── Chart: Risk exposure timeline — horizontal Gantt ─────────────────────
// Shows who holds risk and for how long. Tech giants can exit in years;
// communities are exposed for decades.
// Steps: 0 = tech giant bar | 1 = neoclouds | 2 = credit + pension |
//        3 = communities | 4 = all + "Today" marker

import * as d3 from "npm:d3@7";
import { INK, INK_LIGHT, ACCENT, CONTEXT, RULE, NEGATIVE, POSITIVE } from "../design.js";
import { showTip, moveTip, hideTip } from "../tooltip.js";

export function createRiskTimeline(stats) {
  const entities = [
    { label: "Tech giants\n(Meta, MSFT)",           start: 2025, end: 2030,
      kind: "exit",      note: "3-5 yr leases, can walk away",
      annot: "3\u20135 yr operating leases \u2014 can walk away by early 2030s" },
    { label: "Neoclouds\n(CoreWeave, Nebius)",       start: 2025, end: 2035,
      kind: "locked",    note: "Debt-funded capacity, 10-20 yr exposure",
      annot: "Debt-funded capacity \u2014 10\u201320 yr exposure, no early exit" },
    { label: "Private credit\n(Pimco, Blue Owl)",    start: 2025, end: stats.beignet_bond_maturity,
      kind: "locked",    note: `Bond maturity: ${stats.beignet_bond_maturity}`,
      annot: `Bonds mature ${stats.beignet_bond_maturity} \u2014 no visibility into AI demand` },
    { label: "Pension funds\n& endowments",          start: 2025, end: 2055,
      kind: "locked",    note: "Indefinite exposure via bond portfolios",
      annot: "Indefinite bond portfolio exposure \u2014 furthest from the investment decision" },
    { label: "Rural communities\n(Indiana, LA\u2026)", start: 2025, end: 2070,
      kind: "permanent", note: "Tax incentives, grid load \u2014 permanent",
      annot: "Tax incentives, grid infrastructure, land-use commitments \u2014 no exit" },
  ];

  const n = entities.length;
  const W = Math.min(820, (document.body?.clientWidth ?? 820) - 40);
  const H = 424;   // extra height for title, subtitle, and per-bar annotation rows
  const ml = 120, mr = 50, mt = 52, mb = 56;

  const x = d3.scaleLinear().domain([2024, 2076]).range([ml, W - mr]);
  const rowH = (H - mt - mb) / n;
  const barH = 28;

  const svg = d3.create("svg")
    .attr("width", "100%").attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif");

  // ── Title + subtitle ────────────────────────────────────────────────────
  svg.append("text").attr("x", ml).attr("y", 16)
    .attr("fill", INK).attr("font-size", "13.5").attr("font-weight", "700")
    .text("Tech giants can exit. Communities cannot.");

  svg.append("text").attr("x", ml).attr("y", 32)
    .attr("fill", INK_LIGHT).attr("font-size", "10.5")
    .text("Gray = short-term lease, can walk away · Red = locked in by debt, bonds, or grid infrastructure");

  // Baseline
  svg.append("line").attr("x1", ml).attr("x2", W - mr)
    .attr("y1", H - mb).attr("y2", H - mb)
    .attr("stroke", RULE).attr("stroke-width", 1);

  // X axis ticks
  [2025, 2030, 2035, 2040, 2045, 2050, 2055, 2060, 2065, 2070].forEach(yr => {
    if (x(yr) >= ml && x(yr) <= W - mr) {
      svg.append("text").attr("x", x(yr)).attr("y", H - mb + 14)
        .attr("text-anchor", "middle").attr("fill", INK_LIGHT).attr("font-size", "9.5")
        .text(yr);
    }
  });

  // "Today" marker placeholders — actual elements appended after bars so they
  // render on top. Variables declared here, elements created after barGroups loop.
  let todayHalo, todayLine, todayLabel;

  // Row labels (always visible)
  entities.forEach((e, i) => {
    const ry = mt + rowH * i + rowH / 2;
    const lines = e.label.split("\n");
    lines.forEach((line, li) => {
      svg.append("text")
        .attr("x", ml - 8).attr("y", ry + (li - (lines.length - 1) / 2) * 12)
        .attr("text-anchor", "end").attr("fill", INK)
        .attr("font-size", "10.5").text(line);
    });
  });

  // Build bars per entity
  const barGroups = [];
  entities.forEach((e, i) => {
    const ry = mt + rowH * i + rowH / 2;
    const dur = e.end - e.start;
    const color = e.kind === "exit" ? CONTEXT : NEGATIVE;
    const alpha = e.kind === "exit" ? 0.5 : (e.kind === "permanent" ? 1.0 : 0.8);

    // Bar
    const bar = svg.append("rect")
      .attr("x", x(e.start)).attr("y", ry - barH / 2)
      .attr("width", 0).attr("height", barH)
      .attr("fill", color).attr("opacity", alpha)
      .attr("rx", 2).style("cursor", "crosshair");
    bar
      .on("mouseover", (ev) => showTip(ev, e.label.replace("\n", " "), `${e.start}–${e.kind === "permanent" ? "2070+" : e.end}`, e.annot))
      .on("mousemove", moveTip)
      .on("mouseout", hideTip);

    // End-year label — starts hidden
    const endText = e.kind !== "permanent" ? String(e.end) : "2070+";
    const endLabel = svg.append("text")
      .attr("x", x(e.end) + 4).attr("y", ry + 4)
      .attr("fill", e.kind === "exit" ? INK_LIGHT : NEGATIVE)
      .attr("font-size", "10.5").attr("font-weight", "600")
      .attr("opacity", 0).text(endText);

    // Duration label inside bar (for bars > 8 years)
    const durLabel = dur >= 8 ? svg.append("text")
      .attr("x", x(e.start) + (x(e.end) - x(e.start)) / 2)
      .attr("y", ry + 4)
      .attr("text-anchor", "middle")
      .attr("fill", e.kind === "exit" ? INK : "white")
      .attr("font-size", "9.5")
      .attr("opacity", 0).text(`${dur} yr`) : null;

    // Inline annotation — appears below the bar when it reveals
    const annotEl = svg.append("text")
      .attr("x", x(2027)).attr("y", ry + barH / 2 + 13)
      .attr("fill", INK).attr("font-size", "11")
      .attr("font-style", "italic").attr("opacity", 0)
      .text(e.annot);

    barGroups.push({
      bar, endLabel, durLabel, annotEl,
      width: x(e.end) - x(e.start),
      stepIdx: i <= 0 ? 0 : i <= 1 ? 1 : i <= 2 ? 2 : i <= 3 ? 2 : 3,
    });
  });

  // "Today" marker — appended AFTER bars so it always renders on top.
  // Halo (paper-colored, wider) + accent line on top gives visual separation
  // from bars even when colors are close (NEGATIVE bar vs ACCENT line).
  todayHalo = svg.append("line")
    .attr("x1", x(2026)).attr("x2", x(2026))
    .attr("y1", mt).attr("y2", H - mb)
    .attr("stroke", "#f5f1eb").attr("stroke-width", 4).attr("opacity", 0);
  todayLine = svg.append("line")
    .attr("x1", x(2026)).attr("x2", x(2026))
    .attr("y1", mt).attr("y2", H - mb)
    .attr("stroke", ACCENT).attr("stroke-width", 2).attr("opacity", 0);
  todayLabel = svg.append("text")
    .attr("x", x(2026) + 4).attr("y", mt + 10)
    .attr("fill", ACCENT).attr("font-size", "10").attr("font-weight", "600")
    .attr("opacity", 0).text("Today");

  // Meta exit annotation (between tech giants and neoclouds)
  const exitAnnot = svg.append("text")
    .attr("x", x(stats.meta_beignet_exit_year) + 4)
    .attr("y", mt + rowH * 0.5 + 18)
    .attr("fill", INK_LIGHT).attr("font-size", "11")
    .attr("opacity", 0).text(`Meta can exit ~${stats.meta_beignet_exit_year}`);

  // Legend
  const legY = H - mb + 28;
  [{ color: CONTEXT, alpha: 0.5, text: "Can exit (3-5 yr leases)" },
   { color: NEGATIVE, alpha: 0.9, text: "Locked in (debt / bond maturity)" }]
    .forEach((l, i) => {
      svg.append("rect").attr("x", ml + i * 230).attr("y", legY - 6)
        .attr("width", 10).attr("height", 10).attr("fill", l.color)
        .attr("opacity", l.alpha).attr("rx", 1);
      svg.append("text").attr("x", ml + i * 230 + 14).attr("y", legY + 3)
        .attr("fill", INK_LIGHT).attr("font-size", "10").text(l.text);
    });

  // Source
  svg.append("text").attr("x", ml).attr("y", H - 4)
    .attr("fill", CONTEXT).attr("font-size", "9")
    .text("Source: SEC filings; CoreWeave S-1; CRS reports; author\u2019s analysis");

  // ── Step control ──────────────────────────────────────────────────────────
  // Map entities to their reveal step
  const stepMap = [0, 1, 2, 2, 3]; // indices into entities for each step

  function update(step) {
    barGroups.forEach(({ bar, endLabel, durLabel, annotEl, width }, i) => {
      const revealAt = stepMap[i];
      bar.interrupt();

      if (step >= revealAt) {
        if (step === revealAt) {
          bar.attr("width", 0)
            .transition().delay(200).duration(700).ease(d3.easeQuadOut)
            .attr("width", width);
          endLabel.transition().delay(600).duration(300).attr("opacity", 1);
          if (durLabel) durLabel.transition().delay(500).duration(300).attr("opacity", 1);
          annotEl.transition().delay(750).duration(350).attr("opacity", 0.85);
        } else {
          bar.attr("width", width);
          endLabel.attr("opacity", 1);
          if (durLabel) durLabel.attr("opacity", 1);
          annotEl.attr("opacity", 0.85);
        }
      } else {
        bar.attr("width", 0);
        endLabel.attr("opacity", 0);
        if (durLabel) durLabel.attr("opacity", 0);
        annotEl.interrupt().attr("opacity", 0);
      }
    });

    // Meta exit annotation appears at step 1
    exitAnnot.transition().duration(300).attr("opacity", step >= 1 ? 1 : 0);

    // Today marker at step 4
    todayHalo.transition().duration(350).attr("opacity", step >= 4 ? 1 : 0);
    todayLine.transition().duration(350).attr("opacity", step >= 4 ? 1 : 0);
    todayLabel.transition().duration(350).attr("opacity", step >= 4 ? 1 : 0);
  }

  return { node: svg.node(), update };
}
