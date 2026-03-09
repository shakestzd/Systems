// ── Chart: Thesis matrix — 2x2 risk quadrant ────────────────────────────
// Asset lifetime (x) vs demand thesis durability (y).
// AI infrastructure occupies the structural risk zone: long-lived assets,
// short demand visibility.
// Steps: 0 = empty grid | 1 = safe quadrants dim | 2 = risk zone highlights |
//        3 = asset examples appear

import * as d3 from "npm:d3@7";
import { INK, INK_LIGHT, ACCENT, CONTEXT, RULE, NEGATIVE, POSITIVE } from "../design.js";

const QUADS = [
  { xi: 0, yi: 0, color: CONTEXT,  alpha: 0.25,
    title: "Aligned \u2014 Agile",
    items: "GPU server leases\nCloud compute contracts" },
  { xi: 1, yi: 0, color: NEGATIVE, alpha: 0.55,
    title: "Risk Zone",
    items: "AI-dedicated substations\nData center shells\nTransmission upgrades" },
  { xi: 0, yi: 1, color: CONTEXT,  alpha: 0.15,
    title: "Mismatch \u2014 Oversized",
    items: "(unusual in practice)" },
  { xi: 1, yi: 1, color: POSITIVE, alpha: 0.35,
    title: "Aligned \u2014 Durable",
    items: "Baseload power plants\nTelecom fiber backbone" },
];

export function createThesisMatrix() {
  const W = Math.min(560, (document.body?.clientWidth ?? 560) - 40);
  const H = 434;
  const ml = 60, mr = 20, mt = 54, mb = 50;
  const plotW = W - ml - mr;
  const plotH = H - mt - mb;

  const svg = d3.create("svg")
    .attr("width", "100%").attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif");

  // ── Title + subtitle ────────────────────────────────────────────────────
  svg.append("text").attr("x", ml).attr("y", 16)
    .attr("fill", INK).attr("font-size", "13").attr("font-weight", "700")
    .text("AI infrastructure sits in the structural risk zone");
  svg.append("text").attr("x", ml).attr("y", 30)
    .attr("fill", INK_LIGHT).attr("font-size", "10.5")
    .text("Asset lifetime (x) vs. demand thesis durability (y) · risk zone = long assets, short demand visibility");

  // Quadrant backgrounds — start at low opacity
  const quadEls = QUADS.map((q) => {
    const qx = ml + q.xi * (plotW / 2);
    const qy = mt + (1 - q.yi) * (plotH / 2); // flip y: yi=1 is top

    const rect = svg.append("rect")
      .attr("x", qx + 1).attr("y", qy + 1)
      .attr("width", plotW / 2 - 2).attr("height", plotH / 2 - 2)
      .attr("fill", q.color).attr("opacity", 0).attr("rx", 3);

    const title = svg.append("text")
      .attr("x", qx + plotW / 4).attr("y", qy + plotH / 4 - 10)
      .attr("text-anchor", "middle").attr("fill", INK)
      .attr("font-size", "12").attr("font-weight", "700")
      .attr("opacity", 0).text(q.title);

    const items = q.items.split("\n");
    const itemEls = items.map((item, li) =>
      svg.append("text")
        .attr("x", qx + plotW / 4)
        .attr("y", qy + plotH / 4 + 6 + li * 14)
        .attr("text-anchor", "middle").attr("fill", INK_LIGHT)
        .attr("font-size", "10").attr("opacity", 0).text(item)
    );

    return { rect, title, itemEls, ...q };
  });

  // Axis dividers
  svg.append("line")
    .attr("x1", ml + plotW / 2).attr("x2", ml + plotW / 2)
    .attr("y1", mt).attr("y2", mt + plotH)
    .attr("stroke", CONTEXT).attr("stroke-width", 0.8).attr("opacity", 0.5);
  svg.append("line")
    .attr("x1", ml).attr("x2", ml + plotW)
    .attr("y1", mt + plotH / 2).attr("y2", mt + plotH / 2)
    .attr("stroke", CONTEXT).attr("stroke-width", 0.8).attr("opacity", 0.5);

  // Axis labels
  svg.append("text").attr("x", ml + plotW / 4).attr("y", mt + plotH + 16)
    .attr("text-anchor", "middle").attr("fill", INK_LIGHT).attr("font-size", "10")
    .text("Short (3\u20135 yr)");
  svg.append("text").attr("x", ml + 3 * plotW / 4).attr("y", mt + plotH + 16)
    .attr("text-anchor", "middle").attr("fill", INK_LIGHT).attr("font-size", "10")
    .text("Long (25\u201350 yr)");
  svg.append("text").attr("x", ml + plotW / 2).attr("y", mt + plotH + 32)
    .attr("text-anchor", "middle").attr("fill", INK).attr("font-size", "11")
    .text("Asset Lifetime");

  // Y axis labels (rotated)
  svg.append("text")
    .attr("transform", `translate(${ml - 38}, ${mt + 3 * plotH / 4}) rotate(-90)`)
    .attr("text-anchor", "middle").attr("fill", INK_LIGHT).attr("font-size", "10")
    .text("Short (3\u20135 yr)");
  svg.append("text")
    .attr("transform", `translate(${ml - 38}, ${mt + plotH / 4}) rotate(-90)`)
    .attr("text-anchor", "middle").attr("fill", INK_LIGHT).attr("font-size", "10")
    .text("Long (20+ yr)");
  svg.append("text")
    .attr("transform", `translate(${ml - 52}, ${mt + plotH / 2}) rotate(-90)`)
    .attr("text-anchor", "middle").attr("fill", INK).attr("font-size", "11")
    .text("Demand Thesis Durability");

  // Source
  svg.append("text").attr("x", ml).attr("y", H - 4)
    .attr("fill", CONTEXT).attr("font-size", "9")
    .text("Source: Author\u2019s risk framework; SEC filings; industry research");

  // ── Step control ──────────────────────────────────────────────────────────
  function update(step) {
    quadEls.forEach((q) => {
      const isRisk = q.xi === 1 && q.yi === 0; // bottom-right = Risk Zone

      // Step 0: show grid with faint quadrant tints
      if (step === 0) {
        q.rect.transition().duration(300).attr("opacity", 0.12);
        q.title.transition().duration(300).attr("opacity", 0);
        q.itemEls.forEach(el => el.transition().duration(300).attr("opacity", 0));
      }
      // Step 1: safe quadrants fill in with labels
      else if (step === 1) {
        q.rect.transition().duration(400).attr("opacity", isRisk ? 0.1 : q.alpha);
        q.title.transition().duration(400).attr("opacity", isRisk ? 0 : 1);
        q.itemEls.forEach(el => el.transition().duration(400).attr("opacity", isRisk ? 0 : 0.8));
      }
      // Step 2: risk zone highlights strongly
      else if (step === 2) {
        q.rect.transition().duration(400).attr("opacity", isRisk ? q.alpha : q.alpha * 0.4);
        q.title.transition().duration(400).attr("opacity", isRisk ? 1 : 0.35);
        q.itemEls.forEach(el => el.transition().duration(400).attr("opacity", isRisk ? 1 : 0.25));
      }
      // Step 3: all visible
      else {
        q.rect.transition().duration(300).attr("opacity", q.alpha);
        q.title.transition().duration(300).attr("opacity", 1);
        q.itemEls.forEach((el, i) =>
          el.transition().delay(step === 3 ? i * 80 : 0).duration(300).attr("opacity", 1));
      }
    });
  }

  return { node: svg.node(), update };
}
