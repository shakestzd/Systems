// ── Chart: Neocloud lease duration mismatch ───────────────────────────────
// Microsoft signs 3-5 year operating leases. The neoclouds borrow against
// those leases for 10+ years. When Microsoft walks, the neocloud doesn't.
// Steps: 0 = Microsoft bars | 1 = neocloud exposure bars | 2 = end labels

import * as d3 from "../../../_npm/d3@7.9.0/e324157d.js";
import { INK, INK_LIGHT, CONTEXT, RULE, NEGATIVE, PAPER, chartW } from "../design.2d3db129.js";
import { showTip, moveTip, hideTip } from "../tooltip.40aee997.js";

export function createNeocloudLeases(stats) {
  const deals = [
    { label: "Nebius",  value: `$${stats.msft_nebius_deal_bn}B`, msftEnd: 2030, ncEnd: 2038 },
    { label: "Nscale",  value: `$${stats.msft_nscale_deal_bn}B`, msftEnd: 2030, ncEnd: 2038 },
    { label: "Iren",    value: `$${stats.msft_iren_deal_bn}B`,   msftEnd: 2030, ncEnd: 2037 },
    { label: "Lambda",  value: null,                               msftEnd: 2030, ncEnd: 2038 },
  ];

  const n = deals.length;
  const W = chartW(820);
  const H = 300;
  const ml = 100, mr = 52, mt = 44, mb = 84;

  const x = d3.scaleLinear().domain([2025, 2042]).range([ml, W - mr]);
  const rowH = (H - mt - mb) / n;
  const barH = 14;

  const svg = d3.create("svg")
    .attr("width", "100%").attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif");

  // Title
  svg.append("text").attr("x", ml).attr("y", 16)
    .attr("fill", INK).attr("font-size", "12").attr("font-weight", "600")
    .text("Microsoft's leases end. The neoclouds' obligations don't.");

  // Subtitle
  svg.append("text").attr("x", ml).attr("y", 30)
    .attr("fill", INK_LIGHT).attr("font-size", "10")
    .text("Four deals signed Sep–Nov 2025 — each a 3-5 year operating lease against capital committed for 10+ years");

  // X axis
  svg.append("line").attr("x1", ml).attr("x2", W - mr)
    .attr("y1", H - mb).attr("y2", H - mb)
    .attr("stroke", RULE).attr("stroke-width", 1);

  [2025, 2030, 2035, 2040].forEach(yr => {
    svg.append("text").attr("x", x(yr)).attr("y", H - mb + 14)
      .attr("text-anchor", "middle").attr("fill", INK_LIGHT).attr("font-size", "9.5")
      .text(yr);
    if (yr > 2025) {
      svg.append("line").attr("x1", x(yr)).attr("x2", x(yr))
        .attr("y1", mt).attr("y2", H - mb)
        .attr("stroke", RULE).attr("stroke-width", 0.5).attr("stroke-dasharray", "3,3");
    }
  });

  // Row labels
  deals.forEach((d, i) => {
    const ry = mt + rowH * i + rowH / 2;
    svg.append("text")
      .attr("x", ml - 8).attr("y", ry - 2)
      .attr("text-anchor", "end").attr("dominant-baseline", "middle")
      .attr("fill", INK).attr("font-size", "10.5").attr("font-weight", "600")
      .text(d.label);
    if (d.value) {
      svg.append("text")
        .attr("x", ml - 8).attr("y", ry + 11)
        .attr("text-anchor", "end").attr("fill", INK_LIGHT).attr("font-size", "9")
        .text(d.value);
    }
  });

  // Bars per deal
  const msftBars = [], ncBars = [], endLabels = [];

  deals.forEach((d, i) => {
    const ry = mt + rowH * i + rowH / 2;

    // Microsoft bar (top)
    const msftW = x(d.msftEnd) - x(2025);
    const msftBar = svg.append("rect")
      .attr("x", x(2025)).attr("y", ry - barH - 2)
      .attr("width", 0).attr("height", barH)
      .attr("fill", CONTEXT).attr("opacity", 0.65).attr("rx", 2)
      .style("cursor", "crosshair");
    msftBar
      .on("mouseover", ev => showTip(ev, `MSFT ↔ ${d.label}`, "3-5 yr operating lease", "Classified as OpEx. Can walk away at term end."))
      .on("mousemove", moveTip).on("mouseout", hideTip);

    // Neocloud bar (bottom)
    const ncW = x(d.ncEnd) - x(2025);
    const ncBar = svg.append("rect")
      .attr("x", x(2025)).attr("y", ry + 2)
      .attr("width", 0).attr("height", barH)
      .attr("fill", NEGATIVE).attr("opacity", 0.75).attr("rx", 2)
      .style("cursor", "crosshair");
    ncBar
      .on("mouseover", ev => showTip(ev, d.label, `${d.ncEnd - 2025}-yr capital obligation`, "Built against Microsoft's lease. No equivalent exit option."))
      .on("mousemove", moveTip).on("mouseout", hideTip);

    // End-year label for neocloud bar (appears at step 2)
    const ncEndLbl = svg.append("text")
      .attr("x", x(d.ncEnd) + 4).attr("y", ry + 2 + barH / 2 + 4)
      .attr("fill", NEGATIVE).attr("font-size", "9.5").attr("font-weight", "600")
      .attr("opacity", 0).text(`~${d.ncEnd}`);

    // End-year label for microsoft bar (appears at step 0)
    const msftEndLbl = svg.append("text")
      .attr("x", x(d.msftEnd) + 4).attr("y", ry - barH - 2 + barH / 2 + 4)
      .attr("fill", INK_LIGHT).attr("font-size", "9").attr("opacity", 0)
      .text("exits ~2030");

    msftBars.push({ bar: msftBar, lbl: msftEndLbl, w: msftW });
    ncBars.push({ bar: ncBar, w: ncW });
    endLabels.push(ncEndLbl);
  });

  // ── Step annotation — inline text replaces floating callout ────────────
  const STEP_ANNOTS = [
    "3\u20135 year leases, booked as OpEx \u2014 Microsoft can walk away at term end",
    "Neocloud debt runs 8\u201313 years past the lease \u2014 no equivalent exit",
    "When the lease ends in 2030, the neocloud\u2019s capital obligation keeps running",
  ];
  // y = H-mb+32: sits 18px below axis tick labels (which live at H-mb+14)
  const stepAnnot = svg.append("text")
    .attr("x", ml).attr("y", H - mb + 32)
    .attr("fill", INK).attr("font-size", "11")
    .attr("font-style", "italic").attr("opacity", 0);

  // Legend
  const legY = H - mb + 52;
  [
    { color: CONTEXT, alpha: 0.65, label: "Microsoft lease (3-5 yr, operating expense — can exit)" },
    { color: NEGATIVE, alpha: 0.75, label: "Neocloud capital obligation (locked in)" },
  ].forEach((l, i) => {
    svg.append("rect").attr("x", ml + i * 290).attr("y", legY - 7)
      .attr("width", 10).attr("height", 10).attr("fill", l.color)
      .attr("opacity", l.alpha).attr("rx", 1);
    svg.append("text").attr("x", ml + i * 290 + 14).attr("y", legY + 2)
      .attr("fill", INK_LIGHT).attr("font-size", "9").text(l.label);
  });

  // Source
  svg.append("text").attr("x", ml).attr("y", H - 3)
    .attr("fill", CONTEXT).attr("font-size", "8.5")
    .text("Source: Company announcements; NYT Dec 2025; author\u2019s analysis");

  function update(step) {
    msftBars.forEach(({ bar, lbl, w }, i) => {
      bar.interrupt();
      if (step >= 0) {
        if (step === 0) {
          bar.attr("width", 0)
            .transition().delay(i * 70).duration(500).ease(d3.easeQuadOut)
            .attr("width", w);
          lbl.transition().delay(i * 70 + 420).duration(250).attr("opacity", 1);
        } else {
          bar.attr("width", w);
          lbl.attr("opacity", 1);
        }
      } else {
        bar.attr("width", 0); lbl.attr("opacity", 0);
      }
    });

    ncBars.forEach(({ bar, w }, i) => {
      bar.interrupt();
      if (step >= 1) {
        if (step === 1) {
          bar.attr("width", 0)
            .transition().delay(i * 80).duration(600).ease(d3.easeQuadOut)
            .attr("width", w);
        } else {
          bar.attr("width", w);
        }
      } else {
        bar.attr("width", 0);
      }
    });

    endLabels.forEach((lbl, i) => {
      lbl.interrupt();
      lbl.transition().delay(step === 2 ? i * 60 : 0).duration(300)
        .attr("opacity", step >= 2 ? 1 : 0);
    });

    // Step annotation
    if (step >= 0 && step < STEP_ANNOTS.length) {
      stepAnnot.text(STEP_ANNOTS[step])
        .transition().duration(350).attr("opacity", 0.85);
    } else {
      stepAnnot.interrupt().attr("opacity", 0);
    }
  }

  return { node: svg.node(), update };
}
