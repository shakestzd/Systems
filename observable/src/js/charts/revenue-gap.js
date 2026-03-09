// ── Chart: Revenue vs capex gap (absolute $B, quarterly) ──────────────────
// Returns { node, update } for use with mountScrollChart.
// Steps: 0 = revenue lines draw | 1 = capex lines appear | 2 = gap bands shade

import * as d3 from "npm:d3@7";
import { INK, INK_LIGHT, RULE } from "../design.js";
import { cc, cl } from "../design.js";
import { showTip, moveTip, hideTip } from "../tooltip.js";
import { dateToQ, qNum } from "../utils.js";

export function createRevenueGap(capex, cloudRev) {
  const T3 = ["AMZN", "GOOGL", "MSFT"];

  const qCapex = {};
  T3.forEach(t => { qCapex[t] = {}; });
  capex.quarterly.filter(d => T3.includes(d.ticker)).forEach(d => {
    const q = dateToQ(d.date);
    qCapex[d.ticker][q] = (qCapex[d.ticker][q] ?? 0) + d.capex_bn;
  });

  const allQs = [...new Set(cloudRev.map(d => d.quarter))].sort();
  const series = [];
  T3.forEach(ticker => {
    allQs.forEach(q => {
      const rev = cloudRev.find(d => d.ticker === ticker && d.quarter === q)?.revenue_bn;
      const cap = qCapex[ticker]?.[q];
      if (rev != null) series.push({ ticker, q, x: qNum(q), value: rev, type: "revenue" });
      if (cap != null) series.push({ ticker, q, x: qNum(q), value: cap, type: "capex" });
    });
  });

  const W = Math.min(820, (document.body?.clientWidth ?? 820) - 40);
  const H = 364;
  const ml = 50, mr = 95, mt = 52, mb = 74;

  const xExt = d3.extent(series, d => d.x);
  const x = d3.scaleLinear().domain([xExt[0] - 0.05, xExt[1] + 0.08]).range([ml, W - mr]);
  const y = d3.scaleLinear().domain([0, d3.max(series, d => d.value) * 1.15]).range([H - mb, mt]);
  const lineGen = d3.line().x(d => x(d.x)).y(d => y(d.value)).curve(d3.curveMonotoneX);

  const svg = d3.create("svg").attr("width", "100%").attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif");

  // ── Title + subtitle ────────────────────────────────────────────────────
  svg.append("text").attr("x", ml).attr("y", 16)
    .attr("fill", INK).attr("font-size", "13").attr("font-weight", "700")
    .text("Revenue is rising, but capex is rising faster");
  svg.append("text").attr("x", ml).attr("y", 30)
    .attr("fill", INK_LIGHT).attr("font-size", "10.5")
    .text("Quarterly cloud revenue (solid) and capex (dashed) · Amazon, Alphabet, Microsoft");

  svg.append("line").attr("x1", ml).attr("x2", W - mr).attr("y1", H - mb).attr("y2", H - mb)
    .attr("stroke", RULE).attr("stroke-width", 1);

  // Gap bands (AMZN and GOOGL) — inserted before paths so they render behind
  const gapBands = [];
  ["AMZN", "GOOGL"].forEach(ticker => {
    const revData = series.filter(d => d.ticker === ticker && d.type === "revenue").sort((a,b) => a.x - b.x);
    const capData = series.filter(d => d.ticker === ticker && d.type === "capex").sort((a,b) => a.x - b.x);
    // Build area data for quarters where capex > revenue
    const areaData = revData.reduce((acc, rd) => {
      const cd = capData.find(c => c.q === rd.q);
      if (cd && cd.value > rd.value) acc.push({ x: rd.x, rev: rd.value, cap: cd.value });
      return acc;
    }, []);
    if (areaData.length < 2) { gapBands.push(null); return; }
    const areaGen = d3.area()
      .x(d => x(d.x)).y0(d => y(d.rev)).y1(d => y(d.cap))
      .curve(d3.curveMonotoneX);
    const band = svg.append("path").datum(areaData)
      .attr("fill", cc(ticker)).attr("opacity", 0).attr("d", areaGen);
    gapBands.push(band);
  });

  const revPaths = [], capGroups = [];

  T3.forEach(ticker => {
    const color   = cc(ticker);
    const revData = series.filter(d => d.ticker === ticker && d.type === "revenue").sort((a,b) => a.x - b.x);
    const capData = series.filter(d => d.ticker === ticker && d.type === "capex").sort((a,b) => a.x - b.x);

    if (revData.length) {
      const revPath = svg.append("path").datum(revData)
        .attr("fill", "none").attr("stroke", color).attr("stroke-width", 2.2)
        .attr("d", lineGen).attr("stroke-dasharray", "0,99999");
      revPaths.push(revPath);

      revData.forEach(d => {
        const g = svg.append("g");
        g.append("circle").attr("cx", x(d.x)).attr("cy", y(d.value)).attr("r", 3.5)
          .attr("fill", color).attr("stroke", "white").attr("stroke-width", 1.5);
        g.append("circle").attr("cx", x(d.x)).attr("cy", y(d.value)).attr("r", 12).attr("fill", "transparent").style("cursor","crosshair")
          .on("mouseover", (e) => showTip(e, `${cl(ticker)} · ${d.q}`, `Revenue: $${d.value.toFixed(1)}B`))
          .on("mousemove", moveTip).on("mouseout", hideTip);
      });
    }

    if (capData.length) {
      const capG = svg.append("g").attr("opacity", 0);
      capG.append("path").datum(capData)
        .attr("fill", "none").attr("stroke", color)
        .attr("stroke-width", 1.8).attr("stroke-dasharray", "6,4").attr("d", lineGen);
      capData.forEach(d => {
        const g = capG.append("g").style("cursor","crosshair");
        g.append("rect").attr("x", x(d.x) - 3).attr("y", y(d.value) - 3).attr("width", 6).attr("height", 6)
          .attr("fill", color).attr("stroke", "white").attr("stroke-width", 1.5)
          .attr("transform", `rotate(45, ${x(d.x)}, ${y(d.value)})`);
        g.append("circle").attr("cx", x(d.x)).attr("cy", y(d.value)).attr("r", 12).attr("fill", "transparent")
          .on("mouseover", (e) => showTip(e, `${cl(ticker)} · ${d.q}`, `Capex: $${d.value.toFixed(1)}B`))
          .on("mousemove", moveTip).on("mouseout", hideTip);
      });
      capGroups.push(capG);
    }
  });

  // End labels — name only, no "cloud rev" subtitle (legend already distinguishes line types)
  const labelH = 18; // single-line label height for collision check
  const labels = T3.map(ticker => {
    const revData = series.filter(d => d.ticker === ticker && d.type === "revenue").sort((a,b) => a.x - b.x);
    if (!revData.length) return null;
    const last = revData[revData.length - 1];
    return { ticker, lx: x(last.x) + 7, adjY: y(last.value) + 4 };
  }).filter(Boolean);

  labels.sort((a, b) => a.adjY - b.adjY);
  for (let i = 1; i < labels.length; i++) {
    if (labels[i].adjY - labels[i - 1].adjY < labelH)
      labels[i].adjY = labels[i - 1].adjY + labelH;
  }

  labels.forEach(({ ticker, lx, adjY }) => {
    svg.append("text").attr("x", lx).attr("y", adjY)
      .attr("fill", cc(ticker)).attr("font-size", "11").attr("font-weight", "700")
      .text(cl(ticker));
  });

  // X labels
  [2023, 2024, 2025].forEach(yr => {
    svg.append("text").attr("x", x(yr)).attr("y", H - mb + 16)
      .attr("text-anchor", "middle").attr("fill", INK_LIGHT).attr("font-size", "11").text(yr);
  });

  // Y axis
  [0, 25, 50, 75, 100].filter(v => v <= d3.max(series, d => d.value) * 1.05).forEach(v => {
    svg.append("text").attr("x", ml - 6).attr("y", y(v) + 4)
      .attr("text-anchor", "end").attr("fill", INK_LIGHT).attr("font-size", "11").text(`$${v}B`);
  });

  // Legend — top right, opposite the callout
  const legX = W - mr - 10;
  [{ dash: null, text: "Cloud revenue" }, { dash: "6,4", text: "Capital expenditure" }]
    .forEach((l, i) => {
      const ly = mt + 4 + i * 16;
      svg.append("line").attr("x1", legX - 24).attr("x2", legX - 4)
        .attr("y1", ly).attr("y2", ly)
        .attr("stroke", INK_LIGHT).attr("stroke-width", 2).attr("stroke-dasharray", l.dash ?? null);
      svg.append("text").attr("x", legX - 28).attr("y", ly + 3.5)
        .attr("text-anchor", "end").attr("fill", INK_LIGHT).attr("font-size", "10").text(l.text);
    });

  svg.append("text").attr("x", ml).attr("y", H - 3)
    .attr("fill", INK_LIGHT).attr("font-size", "9.5")
    .text("Source: SEC 10-K/10-Q filings via yfinance");

  // ── Step annotation — inline text replaces floating callout ───────────────
  const STEP_ANNOTS = [
    "Cloud revenue rising steadily for all three companies, 2023\u20132025",
    "Capex rising faster \u2014 the lines are crossing",
    "For Alphabet and Amazon, capex now exceeds what cloud earns. The gap is widening.",
  ];
  const stepAnnot = svg.append("text")
    .attr("x", ml).attr("y", H - mb + 32)
    .attr("fill", INK).attr("font-size", "11")
    .attr("font-style", "italic").attr("opacity", 0);

  // ── Step control ──────────────────────────────────────────────────────────
  function update(step) {
    if (step === 0) {
      // Animate revenue lines from scratch; hide capex and gap bands
      revPaths.forEach(p => p.interrupt().attr("stroke-dasharray", "0,99999").attr("opacity", 1));
      revPaths.forEach((p, i) =>
        p.transition().delay(200 + i * 180).duration(1050).ease(d3.easeLinear)
          .attrTween("stroke-dasharray", function() {
            const l = this.getTotalLength();
            return d3.interpolate(`0,${l}`, `${l},${l}`);
          }));
      capGroups.forEach(g => g.interrupt().attr("opacity", 0));
      gapBands.forEach(b => b && b.interrupt().attr("opacity", 0));

    } else if (step === 1) {
      // Revenue lines fully drawn; capex lines appear
      revPaths.forEach(p => {
        const l = p.node().getTotalLength();
        p.interrupt().attr("stroke-dasharray", `${l},${l}`).attr("opacity", 1);
      });
      capGroups.forEach((g, i) =>
        g.interrupt().attr("opacity", 0)
          .transition().delay(200 + i * 120).duration(500).attr("opacity", 1));
      gapBands.forEach(b => b && b.interrupt().attr("opacity", 0));

    } else {
      // step >= 2: everything shown; gap bands appear
      revPaths.forEach(p => {
        const l = p.node().getTotalLength();
        p.interrupt().attr("stroke-dasharray", `${l},${l}`).attr("opacity", 1);
      });
      capGroups.forEach(g => g.attr("opacity", 1));
      gapBands.forEach(b =>
        b && b.interrupt().attr("opacity", 0)
          .transition().delay(step === 2 ? 300 : 0).duration(600).attr("opacity", 0.12));
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
