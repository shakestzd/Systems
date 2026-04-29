// ── Chart: 2026 guidance vs 2025 actual + uncertainty band ────────────────
// Returns { node, update } for use with mountScrollChart.
// Steps: 0 = actual bars | 1 = guidance dots | 2 = error bands

import * as d3 from "../../../_npm/d3@7.9.0/e324157d.js";
import { INK, INK_LIGHT, ACCENT, CONTEXT, RULE, svgTitle, svgStepAnnot, svgSource, chartW, svgLegend } from "../design.2d3db129.js";
import { showTip, moveTip, hideTip } from "../tooltip.40aee997.js";

export function createGuidance(stats) {
  const companies = [
    { ticker: "AMZN", actual: stats.amzn_2025,  guidance: stats.amzn_2026g,  label: "Amazon" },
    { ticker: "GOOGL", actual: stats.googl_2025, guidance: stats.googl_2026g, label: "Alphabet" },
    { ticker: "MSFT", actual: stats.msft_2025,   guidance: stats.msft_2026g,  label: "Microsoft" },
    { ticker: "META", actual: stats.meta_2025,   guidance: stats.meta_2026g,  label: "Meta" },
  ];

  const band = stats.guidance_band_pct / 100;
  companies.forEach(d => {
    d.g_low  = d.guidance * (1 - band);
    d.g_high = d.guidance * (1 + band);
  });

  const W = chartW(720);
  const H = 398;
  const ml = 55, mr = 20, mt = 54, mb = 112;

  const x = d3.scaleBand().domain(companies.map(d => d.label)).range([ml, W - mr]).padding(0.35);
  const yMax = d3.max(companies, d => d.g_high) * 1.15;
  const y = d3.scaleLinear().domain([0, yMax]).range([H - mb, mt]);

  const svg = d3.create("svg").attr("width", "100%").attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif");

  // ── Title + subtitle ────────────────────────────────────────────────────
  svgTitle(svg, W, {
    title: "2026 guidance: another step up for all four companies",
    subtitle: "Gray = 2025 actual capex · orange dot = 2026 guidance · whiskers = historical revision range",
  });

  svg.append("line").attr("x1", ml).attr("x2", W - mr).attr("y1", H - mb).attr("y2", H - mb)
    .attr("stroke", RULE).attr("stroke-width", 1);

  const bars = [], dotCircles = [], errBands = [], labEls = [];

  companies.forEach((d, ci) => {
    const bx = x(d.label);
    const bw = x.bandwidth();
    const mid = bx + bw / 2;
    const finalBarY = y(d.actual), finalBarH = y(0) - y(d.actual);
    const delay = ci * 100;

    // 2025 actual bar
    const bar = svg.append("rect")
      .attr("x", bx).attr("y", H - mb).attr("width", bw).attr("height", 0)
      .attr("fill", CONTEXT).attr("opacity", 0.7);
    bars.push({ bar, finalY: finalBarY, finalH: finalBarH, delay });

    // Guidance dot — separate from error band
    const dotCircle = svg.append("circle")
      .attr("cx", mid).attr("cy", y(d.guidance)).attr("r", 6)
      .attr("fill", ACCENT).attr("opacity", 0);
    dotCircles.push({ dotCircle, delay });

    // Error band (stem + whiskers) — separate group, hidden initially
    const errBand = svg.append("g").attr("opacity", 0);
    errBand.append("line")
      .attr("x1", mid).attr("x2", mid)
      .attr("y1", y(d.g_low)).attr("y2", y(d.g_high))
      .attr("stroke", ACCENT).attr("stroke-width", 2).attr("opacity", 0.55);
    [d.g_low, d.g_high].forEach(v => {
      errBand.append("line")
        .attr("x1", mid - 6).attr("x2", mid + 6).attr("y1", y(v)).attr("y2", y(v))
        .attr("stroke", ACCENT).attr("stroke-width", 1.5).attr("opacity", 0.55);
    });
    errBands.push({ errBand, delay });

    // Hit area
    svg.append("rect").attr("x", bx).attr("y", mt).attr("width", bw).attr("height", H - mb - mt)
      .attr("fill", "transparent").style("cursor", "crosshair")
      .on("mouseover", (e) => showTip(e, d.label,
        `2025 actual: $${d.actual.toFixed(0)}B`,
        `2026 guidance: $${d.guidance.toFixed(0)}B`,
        `Range: $${d.g_low.toFixed(0)}–$${d.g_high.toFixed(0)}B`))
      .on("mousemove", moveTip).on("mouseout", hideTip);

    // Actual bar label (inside bar, white)
    const actLab = svg.append("text").attr("x", mid).attr("y", finalBarY + 16)
      .attr("text-anchor", "middle").attr("fill", "white").attr("font-size", "11").attr("font-weight", "600")
      .attr("opacity", 0).text(`$${d.actual.toFixed(0)}B`);

    // Guidance label (above dot)
    const gdnLab = svg.append("text").attr("x", mid + 10).attr("y", y(d.guidance) - 8)
      .attr("fill", ACCENT).attr("font-size", "10.5").attr("font-weight", "700")
      .attr("opacity", 0).text(`$${d.guidance.toFixed(0)}B`);
    labEls.push({ actLab, gdnLab, delay });

    // Company name label
    svg.append("text").attr("x", mid).attr("y", H - mb + 18)
      .attr("text-anchor", "middle").attr("fill", INK_LIGHT).attr("font-size", "12").text(d.label);
  });

  // Y axis
  [0, 50, 100, 150, 200, 250].filter(v => v <= yMax).forEach(v => {
    svg.append("text").attr("x", ml - 6).attr("y", y(v) + 4)
      .attr("text-anchor", "end").attr("fill", INK_LIGHT).attr("font-size", "11").text(`$${v}B`);
  });

  // Legend — stack vertically on mobile to prevent text clipping
  const legendY = H - mb + 70;
  svgLegend(svg, [
    { type: "rect", fill: CONTEXT, text: "2025 actual capex" },
    { type: "circle", fill: ACCENT, text: `2026 guidance ± ${stats.guidance_band_pct}% band` },
  ], { y: legendY, ml, W, gap: 215 });

  svgSource(svg, W, H, "Source: SEC filings; Q4 2025 earnings calls  ·  Uncertainty band based on largest single-year guidance revision in 2020–2025 period");

  // ── Step annotation — inline text replaces floating callout ───────────────
  const STEP_ANNOTS = [
    "What each company actually spent in 2025",
    "What each company plans to spend in 2026 \u2014 all higher",
    `\u00b1${stats.guidance_band_pct}% historical revision band \u2014 previous plans shifted by this much in a single year`,
  ];
  const annot = svgStepAnnot(svg, { y: H - mb + 30, W, ml });

  // ── Step control ──────────────────────────────────────────────────────────
  function update(step) {
    if (step === 0) {
      // Animate actual bars from scratch; hide guidance elements
      bars.forEach(({ bar, finalY, finalH, delay }) =>
        bar.interrupt().attr("y", H - mb).attr("height", 0)
          .transition().delay(200 + delay).duration(850).ease(d3.easeQuadOut)
          .attr("y", finalY).attr("height", finalH));
      labEls.forEach(({ actLab, gdnLab }) => {
        actLab.interrupt().attr("opacity", 0)
          .transition().delay(800).duration(300).attr("opacity", 1);
        gdnLab.interrupt().attr("opacity", 0);
      });
      dotCircles.forEach(({ dotCircle }) => dotCircle.interrupt().attr("opacity", 0));
      errBands.forEach(({ errBand }) => errBand.interrupt().attr("opacity", 0));

    } else if (step === 1) {
      // Bars fully drawn; guidance dots appear
      bars.forEach(({ bar, finalY, finalH }) =>
        bar.interrupt().attr("y", finalY).attr("height", finalH));
      labEls.forEach(({ actLab }) => actLab.attr("opacity", 1));
      // Animate dots in
      dotCircles.forEach(({ dotCircle, delay }) =>
        dotCircle.interrupt().attr("opacity", 0)
          .transition().delay(200 + delay).duration(350).attr("opacity", 1));
      labEls.forEach(({ gdnLab, delay }) =>
        gdnLab.interrupt().attr("opacity", 0)
          .transition().delay(400 + delay).duration(300).attr("opacity", 1));
      // Error bands hidden
      errBands.forEach(({ errBand }) => errBand.interrupt().attr("opacity", 0));

    } else {
      // step >= 2: everything shown; error bands appear
      bars.forEach(({ bar, finalY, finalH }) =>
        bar.interrupt().attr("y", finalY).attr("height", finalH));
      labEls.forEach(({ actLab, gdnLab }) => {
        actLab.attr("opacity", 1);
        gdnLab.attr("opacity", 1);
      });
      dotCircles.forEach(({ dotCircle }) => dotCircle.attr("opacity", 1));
      errBands.forEach(({ errBand, delay }) =>
        errBand.interrupt().attr("opacity", 0)
          .transition().delay(step === 2 ? 200 + delay : 0).duration(400).attr("opacity", 1));
    }

    // Step annotation
    annot.update(step, STEP_ANNOTS);
  }

  return { node: svg.node(), update };
}
