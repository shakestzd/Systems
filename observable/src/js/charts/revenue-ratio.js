// ── Chart: Capex-to-revenue ratio (quarterly) ─────────────────────────────
// Returns { node, update } for use with mountScrollChart.
// Steps: 0 = all lines draw | 1 = safe zone + dim | 2 = GOOGL highlight |
//        3 = AMZN highlight

import * as d3 from "npm:d3@7";
import { INK, INK_LIGHT, ACCENT, CONTEXT, RULE, svgTitle, svgStepAnnot, svgSource, chartW, isMobile as _isMobile } from "../design.js";
import { cc, cl } from "../design.js";
import { showTip, moveTip, hideTip } from "../tooltip.js";
import { dateToQ, qNum } from "../utils.js";

export function createRevenueRatio(capex, cloudRev) {
  const T3 = ["AMZN", "GOOGL", "MSFT"];

  const qCapex = {};
  T3.forEach(t => { qCapex[t] = {}; });
  capex.quarterly.filter(d => T3.includes(d.ticker)).forEach(d => {
    const q = dateToQ(d.date);
    qCapex[d.ticker][q] = (qCapex[d.ticker][q] ?? 0) + d.capex_bn;
  });

  const ratios = [];
  cloudRev.filter(d => T3.includes(d.ticker)).forEach(d => {
    const cap = qCapex[d.ticker]?.[d.quarter];
    if (cap != null && d.revenue_bn > 0) {
      ratios.push({ ticker: d.ticker, q: d.quarter, x: qNum(d.quarter), ratio: cap / d.revenue_bn });
    }
  });

  const W = chartW(700);
  const isMobile = _isMobile(W);
  const H = 344;
  const ml = 18, mr = isMobile ? 60 : 110, mt = 52, mb = 74;

  const xExt = d3.extent(ratios, d => d.x);
  const x = d3.scaleLinear().domain([xExt[0] - 0.1, xExt[1] + 0.6]).range([ml, W - mr]);
  const y = d3.scaleLinear().domain([0, d3.max(ratios, d => d.ratio) * 1.12]).range([H - mb, mt]);
  const lineGen = d3.line().x(d => x(d.x)).y(d => y(d.ratio)).curve(d3.curveMonotoneX);

  const svg = d3.create("svg").attr("width", "100%").attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif");

  // ── Title + subtitle ────────────────────────────────────────────────────
  svgTitle(svg, W, {
    title: "Capex relative to cloud revenue has crossed 1×",
    subtitle: "Quarterly capex ÷ cloud segment revenue · Amazon, Alphabet, Microsoft · 2023–2025",
  });

  svg.append("line").attr("x1", ml).attr("x2", W - mr).attr("y1", H - mb).attr("y2", H - mb)
    .attr("stroke", RULE).attr("stroke-width", 1);

  // Safe zone — below parity line, revealed at step 1
  const safeZone = svg.append("rect")
    .attr("x", ml).attr("y", y(1))
    .attr("width", W - ml - mr).attr("height", H - mb - y(1))
    .attr("fill", CONTEXT).attr("opacity", 0);

  // Parity reference
  svg.append("line").attr("x1", ml).attr("x2", W - mr).attr("y1", y(1)).attr("y2", y(1))
    .attr("stroke", CONTEXT).attr("stroke-width", 1).attr("stroke-dasharray", "4,3");
  svg.append("text").attr("x", W - mr + 4).attr("y", y(1) + 4)
    .attr("fill", INK_LIGHT).attr("font-size", "10.5").text("Spending = Revenue");

  // T3-indexed paths: 0=AMZN, 1=GOOGL, 2=MSFT
  const paths = [];

  T3.forEach(ticker => {
    const td = ratios.filter(d => d.ticker === ticker).sort((a, b) => a.x - b.x);
    if (!td.length) return;

    const path = svg.append("path").datum(td)
      .attr("fill", "none").attr("stroke", cc(ticker)).attr("stroke-width", 2.2)
      .attr("d", lineGen).attr("stroke-dasharray", "0,99999");
    paths.push({ path, ticker });

    td.forEach(d => {
      const g = svg.append("g").style("cursor", "crosshair");
      const circ = g.append("circle").attr("cx", x(d.x)).attr("cy", y(d.ratio)).attr("r", 4)
        .attr("fill", cc(ticker)).attr("stroke", "white").attr("stroke-width", 1.5);
      g.append("circle").attr("cx", x(d.x)).attr("cy", y(d.ratio)).attr("r", 12).attr("fill", "transparent")
        .on("mouseover", (e) => { circ.attr("r", 6); showTip(e, `${cl(ticker)} · ${d.q}`, `Capex/Revenue: ${d.ratio.toFixed(2)}×`); })
        .on("mousemove", moveTip)
        .on("mouseout",  () => { circ.attr("r", 4); hideTip(); });
    });

    const last = td[td.length - 1];
    svg.append("text").attr("x", x(last.x) + 9).attr("y", y(last.ratio))
      .attr("fill", cc(ticker)).attr("font-size", "11.5").attr("font-weight", "600").text(cl(ticker));
    svg.append("text").attr("x", x(last.x) + 9).attr("y", y(last.ratio) + 14)
      .attr("fill", cc(ticker)).attr("font-size", "11").text(`${last.ratio.toFixed(1)}×`);
  });

  // X labels
  [2023, 2024, 2025].forEach(yr => {
    svg.append("text").attr("x", x(yr)).attr("y", H - mb + 16)
      .attr("text-anchor", "middle").attr("fill", INK_LIGHT).attr("font-size", "11").text(yr);
  });

  svgSource(svg, W, H, "Quarterly capex ÷ quarterly cloud revenue (AWS, Azure, Google Cloud), 2023–2025  ·  Source: SEC 10-K/10-Q filings");

  // ── Step annotation — foreignObject for wrapping ───────────────────────────
  const STEP_ANNOTS = [
    "The 1.0\u00d7 line is parity \u2014 capex equals what the cloud division earns.",
    "Through 2023, all three stayed below 1.0\u00d7: spending less each quarter than their cloud divisions earned.",
    "Alphabet crossed in 2024 \u2014 spending more on infrastructure than Google Cloud earns.",
    "Amazon followed in 2025. Microsoft is approaching the line.",
  ];
  const annot = svgStepAnnot(svg, { y: H - mb + 20, W, ml });

  // ── Step control ──────────────────────────────────────────────────────────
  // paths[0] = AMZN, paths[1] = GOOGL, paths[2] = MSFT
  function setOpacity(focusTicker) {
    paths.forEach(({ path, ticker }) => {
      const isActive = focusTicker === null || ticker === focusTicker;
      const len = path.node().getTotalLength();
      path.attr("stroke-dasharray", `${len},${len}`)
        .transition().duration(300)
        .attr("opacity", isActive ? 1 : 0.2)
        .attr("stroke-width", isActive ? (focusTicker ? 2.8 : 2.2) : 1.6);
    });
  }

  function update(step) {
    if (step === 0) {
      // Animate all lines from scratch; safe zone hidden
      paths.forEach(({ path }) =>
        path.interrupt().attr("stroke-dasharray", "0,99999").attr("opacity", 1).attr("stroke-width", 2.2));
      paths.forEach(({ path }, i) =>
        path.transition().delay(200 + i * 220).duration(1000).ease(d3.easeLinear)
          .attrTween("stroke-dasharray", function() {
            const l = this.getTotalLength();
            return d3.interpolate(`0,${l}`, `${l},${l}`);
          }));
      safeZone.transition().duration(300).attr("opacity", 0);

    } else if (step === 1) {
      // All lines drawn, all dimmed, safe zone visible
      setOpacity(null);
      paths.forEach(({ path }) =>
        path.transition().duration(300).attr("opacity", 0.4).attr("stroke-width", 2.0));
      safeZone.transition().duration(500).attr("opacity", 0.07);

    } else if (step === 2) {
      // Highlight GOOGL (index 1)
      safeZone.attr("opacity", 0.07);
      paths.forEach(({ path, ticker }) => {
        const len = path.node().getTotalLength();
        const isGoogl = ticker === "GOOGL";
        path.attr("stroke-dasharray", `${len},${len}`)
          .transition().duration(300)
          .attr("opacity", isGoogl ? 1 : 0.15)
          .attr("stroke-width", isGoogl ? 2.8 : 1.6);
      });

    } else {
      // step >= 3: highlight AMZN
      safeZone.attr("opacity", 0.07);
      paths.forEach(({ path, ticker }) => {
        const len = path.node().getTotalLength();
        const isAmzn = ticker === "AMZN";
        path.attr("stroke-dasharray", `${len},${len}`)
          .transition().duration(300)
          .attr("opacity", isAmzn ? 1 : (ticker === "MSFT" ? 0.35 : 0.15))
          .attr("stroke-width", isAmzn ? 2.8 : 1.6);
      });
    }

    // Step annotation + left rule
    annot.update(step, STEP_ANNOTS);
  }

  return { node: svg.node(), update };
}
