// ── Chart: Wage slope chart (2019 → 2024) ───────────────────────────────────
// Returns { node, update } for use with mountScrollChart.
// Steps: 0 = all slopes draw | 1 = highlight SW devs | 2 = highlight electricians |
//        3 = show both + wage gap annotation

import * as d3 from "npm:d3@7";
import { INK, INK_LIGHT, ACCENT, CONTEXT, RULE, OCC_TECH, OCC_TRADES, chartW } from "../design.js";
import { showTip, moveTip, hideTip } from "../tooltip.js";

export function createWageSlopes(data, stats) {
  const W = chartW(720);
  const H = 454;
  const ml = 16, mr = 16, mt = 64, mb = 44;

  // Get first and last year per SOC
  const years = [...new Set(data.map(d => d.year))].sort();
  const firstYear = years[0];
  const lastYear = years[years.length - 1];

  // Build slope data: one entry per SOC with start and end wages
  const bySoc = d3.group(data, d => d.soc);
  const slopes = [];
  for (const [soc, records] of bySoc) {
    const first = records.find(r => r.year === firstYear);
    const last = records.find(r => r.year === lastYear);
    if (!first || !last) continue;
    slopes.push({
      soc,
      label: first.label,
      group: first.group,
      wage0: first.a_mean,
      wage1: last.a_mean,
      change_pct: ((last.a_mean / first.a_mean - 1) * 100),
    });
  }

  // Column positions
  const colLeft = ml + 110;
  const colRight = W - mr - 140;

  // Y scale: wage in dollars
  const maxWage = d3.max(slopes, d => Math.max(d.wage0, d.wage1));
  const minWage = d3.min(slopes, d => Math.min(d.wage0, d.wage1));
  const y = d3.scaleLinear()
    .domain([minWage * 0.92, maxWage * 1.06])
    .range([H - mb, mt]);

  const svg = d3.create("svg")
    .attr("width", "100%")
    .attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif");

  // ── Title + subtitle ────────────────────────────────────────────────────
  svg.append("text").attr("x", ml).attr("y", 16)
    .attr("fill", INK).attr("font-size", "13").attr("font-weight", "700")
    .text("Every occupation in the AI labor stack saw wages rise");
  svg.append("text").attr("x", ml).attr("y", 30)
    .attr("fill", INK_LIGHT).attr("font-size", "10.5")
    .text("Annual mean wage (national), selected occupations · left column = earlier year, right = 2023/2024");

  // Column headers
  svg.append("text")
    .attr("x", colLeft).attr("y", mt - 10)
    .attr("text-anchor", "middle").attr("fill", INK).attr("font-size", "12").attr("font-weight", "600")
    .text(firstYear);
  svg.append("text")
    .attr("x", colRight).attr("y", mt - 10)
    .attr("text-anchor", "middle").attr("fill", INK).attr("font-size", "12").attr("font-weight", "600")
    .text(lastYear);

  // Vertical dotted column lines
  [colLeft, colRight].forEach(cx => {
    svg.append("line")
      .attr("x1", cx).attr("x2", cx)
      .attr("y1", mt).attr("y2", H - mb)
      .attr("stroke", RULE).attr("stroke-width", 1).attr("stroke-dasharray", "2,3");
  });

  // Focus SOC codes
  const FOCUS_SW = "15-1252";
  const FOCUS_ELEC = "47-2111";

  function slopeColor(soc) {
    if (soc === FOCUS_SW) return OCC_TECH;
    if (soc === FOCUS_ELEC) return OCC_TRADES;
    return CONTEXT;
  }

  function slopeWidth(soc) {
    return (soc === FOCUS_SW || soc === FOCUS_ELEC) ? 2.5 : 1.2;
  }

  // Draw slopes — context first, focus on top
  const sortedSlopes = [...slopes].sort((a, b) => {
    const fa = [FOCUS_SW, FOCUS_ELEC].includes(a.soc) ? 1 : 0;
    const fb = [FOCUS_SW, FOCUS_ELEC].includes(b.soc) ? 1 : 0;
    return fa - fb;
  });

  const slopeEls = [];
  sortedSlopes.forEach(d => {
    const color = slopeColor(d.soc);
    const lw = slopeWidth(d.soc);
    const isFocus = d.soc === FOCUS_SW || d.soc === FOCUS_ELEC;

    const g = svg.append("g");

    // Slope line
    const line = g.append("line")
      .attr("x1", colLeft).attr("y1", y(d.wage0))
      .attr("x2", colRight).attr("y2", y(d.wage1))
      .attr("stroke", color).attr("stroke-width", lw)
      .attr("opacity", isFocus ? 1 : 0.35);

    // Left dot
    const dotL = g.append("circle")
      .attr("cx", colLeft).attr("cy", y(d.wage0))
      .attr("r", isFocus ? 4 : 2.5).attr("fill", color)
      .attr("opacity", isFocus ? 1 : 0.35);

    // Right dot
    const dotR = g.append("circle")
      .attr("cx", colRight).attr("cy", y(d.wage1))
      .attr("r", isFocus ? 4 : 2.5).attr("fill", color)
      .attr("opacity", isFocus ? 1 : 0.35);

    // Invisible hit target on right dot
    g.append("circle")
      .attr("cx", colRight).attr("cy", y(d.wage1))
      .attr("r", 12).attr("fill", "transparent")
      .style("cursor", "crosshair")
      .on("mouseover", (e) => {
        dotR.attr("r", isFocus ? 6 : 4);
        showTip(e,
          d.label,
          `${firstYear}: $${(d.wage0/1000).toFixed(0)}K`,
          `${lastYear}: $${(d.wage1/1000).toFixed(0)}K`,
          `Change: +${d.change_pct.toFixed(1)}%`
        );
      })
      .on("mousemove", moveTip)
      .on("mouseout", () => {
        dotR.attr("r", isFocus ? 4 : 2.5);
        hideTip();
      });

    // Labels for focus series
    const leftLabel = g.append("text")
      .attr("x", colLeft - 8).attr("y", y(d.wage0) + 4)
      .attr("text-anchor", "end").attr("fill", color)
      .attr("font-size", isFocus ? "11" : "9.5")
      .attr("font-weight", isFocus ? "600" : "400")
      .attr("opacity", 0)
      .text(isFocus ? `$${(d.wage0/1000).toFixed(0)}K` : "");

    const rightLabel = g.append("text")
      .attr("x", colRight + 8).attr("y", y(d.wage1) + 4)
      .attr("text-anchor", "start").attr("fill", color)
      .attr("font-size", isFocus ? "11" : "9.5")
      .attr("font-weight", isFocus ? "600" : "400")
      .attr("opacity", 0)
      .text(isFocus ? `${d.label} ($${(d.wage1/1000).toFixed(0)}K)` : d.label);

    slopeEls.push({
      soc: d.soc, label: d.label, group: d.group,
      line, dotL, dotR, leftLabel, rightLabel, g,
      isFocus,
    });
  });

  // Wage gap annotation (hidden initially)
  const sw = slopes.find(d => d.soc === FOCUS_SW);
  const el = slopes.find(d => d.soc === FOCUS_ELEC);
  const gapAnnotation = svg.append("g").attr("opacity", 0);
  if (sw && el) {
    const gapX = colRight + 100;
    gapAnnotation.append("line")
      .attr("x1", gapX).attr("x2", gapX)
      .attr("y1", y(sw.wage1)).attr("y2", y(el.wage1))
      .attr("stroke", INK_LIGHT).attr("stroke-width", 1.5).attr("stroke-dasharray", "3,2");
    gapAnnotation.append("text")
      .attr("x", gapX + 6).attr("y", (y(sw.wage1) + y(el.wage1)) / 2 + 4)
      .attr("fill", INK).attr("font-size", "11").attr("font-weight", "600")
      .text(`${(stats.wage_ratio ?? (sw.wage1 / el.wage1)).toFixed(1)}x gap`);
    // Arrow heads
    [y(sw.wage1), y(el.wage1)].forEach(yv => {
      gapAnnotation.append("circle")
        .attr("cx", gapX).attr("cy", yv)
        .attr("r", 2.5).attr("fill", INK_LIGHT);
    });
  }

  // Source
  svg.append("text")
    .attr("x", ml).attr("y", H - 4)
    .attr("fill", CONTEXT).attr("font-size", "9")
    .text("Annual mean wage, nominal USD  ·  Source: BLS OEWS national flat files");

  // ── Step control ──────────────────────────────────────────────────────────
  function setVisibility(focusSoc) {
    slopeEls.forEach(el => {
      const isActive = focusSoc === null || el.soc === focusSoc ||
        (focusSoc === "both" && el.isFocus);
      const showLabel = isActive && (el.isFocus || focusSoc === null);

      el.line.transition().duration(300)
        .attr("opacity", isActive ? 1 : 0.1)
        .attr("stroke-width", isActive && el.isFocus ? 2.8 : (isActive ? 1.5 : 1));
      el.dotL.transition().duration(300).attr("opacity", isActive ? 1 : 0.1);
      el.dotR.transition().duration(300).attr("opacity", isActive ? 1 : 0.1);
      el.leftLabel.transition().duration(300).attr("opacity", showLabel && el.isFocus ? 1 : 0);
      el.rightLabel.transition().duration(300)
        .attr("opacity", showLabel ? 1 : 0);
    });
  }

  function update(step) {
    if (step === 0) {
      // All slopes visible, focus highlighted, labels on focus only
      setVisibility(null);
      slopeEls.forEach(el => {
        el.line.attr("opacity", el.isFocus ? 1 : 0.3)
          .attr("stroke-width", el.isFocus ? 2.5 : 1.2);
        el.dotL.attr("opacity", el.isFocus ? 1 : 0.3);
        el.dotR.attr("opacity", el.isFocus ? 1 : 0.3);
        el.rightLabel.attr("opacity", el.isFocus ? 1 : 0);
        el.leftLabel.attr("opacity", el.isFocus ? 1 : 0);
      });
      gapAnnotation.transition().duration(200).attr("opacity", 0);
    } else if (step === 1) {
      // Highlight Software Developers
      setVisibility(FOCUS_SW);
      gapAnnotation.transition().duration(200).attr("opacity", 0);
    } else if (step === 2) {
      // Highlight Electricians
      setVisibility(FOCUS_ELEC);
      gapAnnotation.transition().duration(200).attr("opacity", 0);
    } else {
      // step >= 3: Both focus + gap annotation
      setVisibility("both");
      gapAnnotation.transition().delay(300).duration(400).attr("opacity", 1);
    }
  }

  return { node: svg.node(), update };
}
