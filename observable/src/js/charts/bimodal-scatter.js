// ── Bimodal Scatter: Income vs. Poverty for data center host counties ───────
// Quadrant scatter with animated crosshair reveal.
// Scroll: all points -> median income line -> median poverty line -> highlight distressed.

import * as d3 from "npm:d3@7";
import { INK, INK_LIGHT, ACCENT, CONTEXT, RULE, PAPER } from "../design.js";
import { showTip, moveTip, hideTip } from "../tooltip.js";

export function createBimodalScatter(locations) {
  const W = Math.min(820, (document.body?.clientWidth ?? 820) - 40);
  const H = 454;
  const ml = 60, mr = 24, mt = 52, mb = 50;

  const facs = locations.facilities.filter(d =>
    d.median_household_income != null && d.poverty_rate != null
  );

  const usMedianIncome = locations.us_median_income;
  const usMedianPoverty = locations.us_median_poverty;

  const x = d3.scaleLinear()
    .domain([
      d3.min(facs, d => d.median_household_income / 1000) * 0.9,
      d3.max(facs, d => d.median_household_income / 1000) * 1.05
    ])
    .range([ml, W - mr]);

  const y = d3.scaleLinear()
    .domain([0, d3.max(facs, d => d.poverty_rate * 100) * 1.15])
    .range([H - mb, mt]);

  const svg = d3.create("svg")
    .attr("width", "100%")
    .attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif");

  // ── Title + subtitle ────────────────────────────────────────────────────
  svg.append("text").attr("x", ml).attr("y", 16)
    .attr("fill", INK).attr("font-size", "13").attr("font-weight", "700")
    .text("Data center host counties split into two distinct groups");
  svg.append("text").attr("x", ml).attr("y", 30)
    .attr("fill", INK_LIGHT).attr("font-size", "10.5")
    .text("Each point = one data center host county · x = median household income · y = poverty rate");

  // Axes
  svg.append("g")
    .attr("transform", `translate(0,${H - mb})`)
    .call(d3.axisBottom(x).ticks(6).tickSize(0))
    .call(g => g.select(".domain").attr("stroke", RULE))
    .call(g => g.selectAll("text").attr("fill", INK_LIGHT).attr("font-size", 11));

  svg.append("g")
    .attr("transform", `translate(${ml},0)`)
    .call(d3.axisLeft(y).ticks(5).tickSize(0))
    .call(g => g.select(".domain").attr("stroke", RULE))
    .call(g => g.selectAll("text").attr("fill", INK_LIGHT).attr("font-size", 11));

  // Axis labels
  svg.append("text")
    .attr("x", (ml + W - mr) / 2).attr("y", H - 6)
    .attr("text-anchor", "middle").attr("fill", INK_LIGHT).attr("font-size", 11)
    .text("Median Household Income ($K)");

  svg.append("text")
    .attr("transform", `translate(14,${(mt + H - mb) / 2}) rotate(-90)`)
    .attr("text-anchor", "middle").attr("fill", INK_LIGHT).attr("font-size", 11)
    .text("Poverty Rate (%)");

  // Crosshair lines (initially hidden)
  const incomeLine = svg.append("line")
    .attr("x1", x(usMedianIncome / 1000)).attr("x2", x(usMedianIncome / 1000))
    .attr("y1", mt).attr("y2", H - mb)
    .attr("stroke", CONTEXT).attr("stroke-width", 1.5)
    .attr("stroke-dasharray", "5,3").attr("opacity", 0);

  const incomeLabel = svg.append("text")
    .attr("x", x(usMedianIncome / 1000) + 4).attr("y", mt + 12)
    .attr("fill", CONTEXT).attr("font-size", 10).attr("opacity", 0)
    .text(`US median $${(usMedianIncome / 1000).toFixed(0)}K`);

  const povertyLine = svg.append("line")
    .attr("x1", ml).attr("x2", W - mr)
    .attr("y1", y(usMedianPoverty * 100)).attr("y2", y(usMedianPoverty * 100))
    .attr("stroke", CONTEXT).attr("stroke-width", 1.5)
    .attr("stroke-dasharray", "5,3").attr("opacity", 0);

  const povertyLabel = svg.append("text")
    .attr("x", W - mr - 4).attr("y", y(usMedianPoverty * 100) - 5)
    .attr("text-anchor", "end").attr("fill", CONTEXT).attr("font-size", 10).attr("opacity", 0)
    .text(`US median ${(usMedianPoverty * 100).toFixed(1)}%`);

  // Data points
  const dots = svg.selectAll("g.dot")
    .data(facs).join("g")
    .attr("class", "dot")
    .attr("transform", d => `translate(${x(d.median_household_income / 1000)},${y(d.poverty_rate * 100)})`);

  const visibleDots = dots.append("circle")
    .attr("r", 5)
    .attr("fill", ACCENT)
    .attr("fill-opacity", 0.6)
    .attr("stroke", "none");

  // Hit targets
  dots.append("circle")
    .attr("r", 12)
    .attr("fill", "transparent")
    .style("cursor", "crosshair")
    .on("mouseover", (e, d) => {
      showTip(e, `${d.county}, ${d.state}`,
        `Operator: ${d.operator}`,
        `Income: $${(d.median_household_income / 1000).toFixed(0)}K`,
        `Poverty: ${(d.poverty_rate * 100).toFixed(1)}%`
      );
    })
    .on("mousemove", moveTip)
    .on("mouseout", hideTip);

  // Labels for extreme points
  const topIncome = [...facs].sort((a, b) => b.median_household_income - a.median_household_income).slice(0, 2);
  const topPoverty = [...facs].sort((a, b) => b.poverty_rate - a.poverty_rate).slice(0, 2);

  const labeled = [...topIncome, ...topPoverty];
  const labelTexts = svg.selectAll("text.label")
    .data(labeled).join("text")
    .attr("class", "label")
    .attr("x", d => x(d.median_household_income / 1000) + 7)
    .attr("y", d => y(d.poverty_rate * 100) - 4)
    .attr("fill", INK).attr("font-size", 10)
    .text(d => d.county);

  // Source
  svg.append("text")
    .attr("x", ml).attr("y", H - 3)
    .attr("fill", CONTEXT).attr("font-size", 9)
    .text("Source: U.S. Census Bureau, ACS 5-Year Estimates (2023); company announcements 2010\u20132025");

  // ── Update ──────────────────────────────────────────────────────────────
  function update(step) {
    const t = svg.transition().duration(400);

    // Step 0: All points, no crosshairs
    incomeLine.transition(t).attr("opacity", step >= 1 ? 0.8 : 0);
    incomeLabel.transition(t).attr("opacity", step >= 1 ? 1 : 0);

    povertyLine.transition(t).attr("opacity", step >= 2 ? 0.8 : 0);
    povertyLabel.transition(t).attr("opacity", step >= 2 ? 1 : 0);

    // Step 3: Highlight distressed
    if (step >= 3) {
      visibleDots.transition(t)
        .attr("fill", d => d.poverty_rate > 0.15 ? ACCENT : CONTEXT)
        .attr("fill-opacity", d => d.poverty_rate > 0.15 ? 0.9 : 0.3)
        .attr("r", d => d.poverty_rate > 0.15 ? 7 : 4);
    } else {
      visibleDots.transition(t)
        .attr("fill", ACCENT)
        .attr("fill-opacity", 0.6)
        .attr("r", 5);
    }
  }

  return { node: svg.node(), update };
}
