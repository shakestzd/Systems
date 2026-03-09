// ── Chart: Annual capex history (4-company) ───────────────────────────────
// Returns { node, update } for use with mountScrollChart.
// Steps: 0 = pre-2022 draws in | 1 = AI era marker | 2 = post-2022 draws |
//        3 = end label + multiplier

import * as d3 from "npm:d3@7";
import { INK, INK_LIGHT, ACCENT, CONTEXT, RULE } from "../design.js";
import { showTip, moveTip, hideTip } from "../tooltip.js";

export function createCapexHistory(capex, stats) {
  const hist  = capex.history_4co;
  const v2019 = hist.find(d => d.year === 2019)?.capex_bn ?? 70.9;
  const v2025 = hist.find(d => d.year === 2025)?.capex_bn;
  const split = 2022;

  const W = Math.min(820, (document.body?.clientWidth ?? 820) - 40);
  const H = 364;
  const ml = 58, mr = 130, mt = 52, mb = 74;

  const x = d3.scaleLinear().domain([2014.5, 2026.5]).range([ml, W - mr]);
  const y = d3.scaleLinear().domain([0, d3.max(hist, d => d.capex_bn) * 1.18]).range([H - mb, mt]);
  const lineGen = d3.line().x(d => x(d.year)).y(d => y(d.capex_bn)).curve(d3.curveMonotoneX);

  const svg = d3.create("svg").attr("width", "100%").attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif");

  // ── Title + subtitle ────────────────────────────────────────────────────
  svg.append("text").attr("x", ml).attr("y", 16)
    .attr("fill", INK).attr("font-size", "13").attr("font-weight", "700")
    .text("This cycle doubled spending in two years");
  svg.append("text").attr("x", ml).attr("y", 30)
    .attr("fill", INK_LIGHT).attr("font-size", "10.5")
    .text("Annual capex, Amazon · Alphabet · Microsoft · Meta  ·  2015–2025 ($B)");

  // Baseline
  svg.append("line").attr("x1", ml).attr("x2", W - mr).attr("y1", y(0)).attr("y2", y(0))
    .attr("stroke", RULE).attr("stroke-width", 1);

  // 2019 reference — always visible
  svg.append("line").attr("x1", ml).attr("x2", W - mr)
    .attr("y1", y(v2019)).attr("y2", y(v2019))
    .attr("stroke", CONTEXT).attr("stroke-width", 1).attr("stroke-dasharray", "4,3");
  svg.append("text").attr("x", ml + 4).attr("y", y(v2019) - 5)
    .attr("fill", INK_LIGHT).attr("font-size", "11")
    .text(`2019 baseline: $${v2019.toFixed(0)}B`);

  // AI era marker — starts hidden, appears at step 1
  const aiLine = svg.append("line")
    .attr("x1", x(2022)).attr("x2", x(2022)).attr("y1", mt).attr("y2", H - mb)
    .attr("stroke", ACCENT).attr("stroke-width", 1).attr("stroke-dasharray", "4,3")
    .attr("opacity", 0);
  const aiLabel = svg.append("text")
    .attr("x", x(2022) + 5).attr("y", y(210))
    .attr("fill", ACCENT).attr("font-size", "11").attr("opacity", 0)
    .text("AI investment era");

  // Lines — start hidden
  const pre  = hist.filter(d => d.year <= split);
  const post = hist.filter(d => d.year >= split);

  const prePath = svg.append("path").datum(pre)
    .attr("fill", "none").attr("stroke", CONTEXT).attr("stroke-width", 2)
    .attr("d", lineGen).attr("stroke-dasharray", "0,99999");
  const postPath = svg.append("path").datum(post)
    .attr("fill", "none").attr("stroke", ACCENT).attr("stroke-width", 2.5)
    .attr("d", lineGen).attr("stroke-dasharray", "0,99999");

  // Dots — start invisible
  const dotCircs = [];
  hist.forEach(d => {
    const acc = d.year >= split;
    const g = svg.append("g").style("cursor", "crosshair");
    const circ = g.append("circle").attr("cx", x(d.year)).attr("cy", y(d.capex_bn))
      .attr("r", acc ? 5 : 4).attr("fill", acc ? ACCENT : CONTEXT)
      .attr("stroke", "white").attr("stroke-width", 1.5).attr("opacity", 0);
    dotCircs.push(circ);
    g.append("circle").attr("cx", x(d.year)).attr("cy", y(d.capex_bn))
      .attr("r", 14).attr("fill", "transparent")
      .on("mouseover", (e) => { circ.attr("r", 7); showTip(e, `${d.year}`, `$${d.capex_bn.toFixed(0)}B combined capex`); })
      .on("mousemove", moveTip)
      .on("mouseout",  () => { circ.attr("r", acc ? 5 : 4); hideTip(); });
  });

  // End labels — start hidden, appear at step 3
  const mult = v2025 ? (v2025 / v2019).toFixed(1) : null;
  const endLabel1 = v2025 ? svg.append("text")
    .attr("x", x(2025) + 10).attr("y", y(v2025) - 4)
    .attr("fill", ACCENT).attr("font-size", "12").attr("font-weight", "700")
    .attr("opacity", 0).text(`$${v2025.toFixed(0)}B`) : null;
  const endLabel2 = mult ? svg.append("text")
    .attr("x", x(2025) + 10).attr("y", y(v2025) + 11)
    .attr("fill", ACCENT).attr("font-size", "11")
    .attr("opacity", 0).text(`(${mult}× vs 2019)`) : null;

  // Y axis
  [0, 100, 200, 300, 400].forEach(v => {
    svg.append("text").attr("x", ml - 6).attr("y", y(v) + 4)
      .attr("text-anchor", "end").attr("fill", INK_LIGHT).attr("font-size", "11")
      .text(`$${v}B`);
  });

  // X axis — fewer ticks on narrow viewports to prevent label collision
  const isMobile = W < 450;
  const xTicks = isMobile ? [2016, 2020, 2024] : [2016, 2018, 2020, 2022, 2024];
  xTicks.forEach(yr => {
    svg.append("text").attr("x", x(yr)).attr("y", H - mb + 16)
      .attr("text-anchor", "middle").attr("fill", INK_LIGHT).attr("font-size", "11")
      .text(yr);
  });

  svg.append("text").attr("x", ml).attr("y", H - 4).attr("fill", INK_LIGHT).attr("font-size", "10")
    .text("Annual capex, Amazon + Alphabet + Microsoft + Meta, 2015–2025 ($B)  ·  Source: SEC 10-K filings (2022–2025); company annual reports (2015–2021)");

  // ── Step annotation — inline text replaces floating callout ───────────────
  const STEP_ANNOTS = [
    "2014\u20132021: steady growth, no dramatic acceleration",
    "The AI era begins in 2022",
    "Spending doubled in two years \u2014 faster than any previous cycle",
    v2025 && mult ? `$${v2025.toFixed(0)}B in 2025 \u2014 ${mult}\u00d7 the 2019 baseline` : "",
  ];
  const stepAnnot = svg.append("text")
    .attr("x", ml).attr("y", H - mb + 32)
    .attr("fill", INK).attr("font-size", "11")
    .attr("font-style", "italic").attr("opacity", 0);

  // ── Step control ──────────────────────────────────────────────────────────
  function update(step) {
    const preLen = prePath.node().getTotalLength();
    const postLen = postPath.node().getTotalLength();

    // Pre-2022 line: animate from scratch on step 0, fully drawn for step > 0
    prePath.interrupt();
    if (step === 0) {
      prePath.attr("stroke-dasharray", `0,${preLen}`)
        .transition().delay(200).duration(1400).ease(d3.easeLinear)
        .attr("stroke-dasharray", `${preLen},${preLen}`);
    } else {
      prePath.attr("stroke-dasharray", `${preLen},${preLen}`);
    }

    // AI era marker: step 1+
    aiLine.transition().duration(350).attr("opacity", step >= 1 ? 0.45 : 0);
    aiLabel.transition().duration(350).attr("opacity", step >= 1 ? 0.8 : 0);

    // Post-2022 line + dots: step 2 = animate; step > 2 = instant full; step < 2 = hidden
    postPath.interrupt();
    dotCircs.forEach(c => c.interrupt());
    if (step === 2) {
      postPath.attr("stroke-dasharray", `0,${postLen}`)
        .transition().delay(100).duration(1100).ease(d3.easeQuadOut)
        .attr("stroke-dasharray", `${postLen},${postLen}`);
      dotCircs.forEach((c, i) =>
        c.attr("opacity", 0).transition().duration(300).delay(350 + i * 70).attr("opacity", 1));
    } else if (step > 2) {
      postPath.attr("stroke-dasharray", `${postLen},${postLen}`);
      dotCircs.forEach(c => c.attr("opacity", 1));
    } else {
      postPath.attr("stroke-dasharray", `0,${postLen}`);
      dotCircs.forEach(c => c.attr("opacity", 0));
    }

    // End labels: step 3+
    if (endLabel1) endLabel1.transition().duration(400).attr("opacity", step >= 3 ? 1 : 0);
    if (endLabel2) endLabel2.transition().duration(400).attr("opacity", step >= 3 ? 1 : 0);

    // Step annotation
    if (step >= 0 && step < STEP_ANNOTS.length) {
      stepAnnot.text(STEP_ANNOTS[step]).transition().duration(350).attr("opacity", 0.85);
    } else {
      stepAnnot.interrupt().attr("opacity", 0);
    }
  }

  return { node: svg.node(), update };
}
