// ── Bill Calculator: Interactive residential electricity bill impact ─────────
// Two side-by-side bill representations with sliders.
// Left: "Current rules (costs socialized)" — Right: "Cost-causation (direct-assigned)"
// Reader adjusts data center load % and monthly usage; sees real-time cost difference.

import * as d3 from "../../../_npm/d3@7.9.0/e324157d.js";
import { INK, INK_LIGHT, ACCENT, CONTEXT, RULE, RATEPAYER, PAPER, PUBLIC, chartW } from "../design.2d3db129.js";

export function createBillCalculator(stats) {
  const W = chartW(820);

  const container = d3.create("div")
    .style("font-family", "'DM Sans', sans-serif")
    .style("max-width", `${W}px`)
    .style("margin", "0 auto");

  // ── Disclaimer ────────────────────────────────────────────────────────
  container.append("div")
    .style("background", `color-mix(in srgb, ${PUBLIC} 15%, transparent)`)
    .style("border-left", `3px solid ${PUBLIC}`)
    .style("padding", "0.5rem 0.8rem")
    .style("margin-bottom", "1.2rem")
    .style("font-size", "12px")
    .style("color", INK_LIGHT)
    .style("border-radius", "0 3px 3px 0")
    .html("<strong>Simplified illustration.</strong> Actual rate impacts depend on utility-specific cost structures, regulatory proceedings, and load factor assumptions. This model uses representative parameters from Indiana Michigan Power (IURC Cause 46097).");

  // ── Sliders row ───────────────────────────────────────────────────────
  const sliderRow = container.append("div")
    .style("display", "grid")
    .style("grid-template-columns", "1fr 1fr")
    .style("gap", "1.5rem")
    .style("margin-bottom", "1.5rem");

  // Base parameters
  const BASE_RATE_KWH = 0.12;        // $/kWh average residential rate
  const GRID_UPGRADE_ANNUAL_M = 180;  // $M annual grid upgrade costs (from stats)
  const TOTAL_RESIDENTIAL_GWH = 40000; // approximate residential consumption GWh

  let dcLoadPct = 15;
  let monthlyKwh = 900;

  function makeSlider(parent, label, min, max, step, value, unit, onChange) {
    const wrap = parent.append("div");
    wrap.append("label")
      .style("font-size", "12px")
      .style("font-weight", 500)
      .style("color", INK_LIGHT)
      .style("text-transform", "uppercase")
      .style("letter-spacing", "0.05em")
      .style("display", "block")
      .style("margin-bottom", "0.3rem")
      .text(label);

    const valueDisplay = wrap.append("span")
      .style("font-size", "18px")
      .style("font-weight", 600)
      .style("color", INK)
      .text(`${value}${unit}`);

    const input = wrap.append("input")
      .attr("type", "range")
      .attr("min", min).attr("max", max).attr("step", step)
      .attr("value", value)
      .style("width", "100%")
      .style("margin-top", "0.3rem")
      .style("accent-color", ACCENT);

    input.on("input", function() {
      const v = +this.value;
      valueDisplay.text(`${v}${unit}`);
      onChange(v);
    });

    return { input, valueDisplay };
  }

  makeSlider(sliderRow, "Data center load share", 0, 30, 1, dcLoadPct, "%", (v) => {
    dcLoadPct = v;
    recalc();
  });

  makeSlider(sliderRow, "Your monthly usage", 300, 2000, 50, monthlyKwh, " kWh", (v) => {
    monthlyKwh = v;
    recalc();
  });

  // ── Bill comparison cards ─────────────────────────────────────────────
  const cardRow = container.append("div")
    .style("display", "grid")
    .style("grid-template-columns", "1fr 1fr")
    .style("gap", "1.25rem")
    .style("margin-bottom", "1rem");

  function makeCard(parent, title, borderColor) {
    const card = parent.append("div")
      .style("border", `1px solid ${RULE}`)
      .style("border-top", `3px solid ${borderColor}`)
      .style("border-radius", "4px")
      .style("padding", "1rem 1.2rem");

    card.append("div")
      .style("font-size", "11px")
      .style("text-transform", "uppercase")
      .style("letter-spacing", "0.06em")
      .style("color", INK_LIGHT)
      .style("font-weight", 500)
      .style("margin-bottom", "0.6rem")
      .text(title);

    const amount = card.append("div")
      .style("font-size", "2rem")
      .style("font-weight", 600)
      .style("color", INK)
      .style("font-family", "'Cormorant Garamond', Georgia, serif")
      .text("$0");

    const subtitle = card.append("div")
      .style("font-size", "12px")
      .style("color", INK_LIGHT)
      .style("margin-top", "0.2rem")
      .text("per month");

    const breakdown = card.append("div")
      .style("margin-top", "0.8rem")
      .style("font-size", "12px")
      .style("color", INK_LIGHT)
      .style("line-height", "1.6");

    return { amount, subtitle, breakdown };
  }

  const leftCard = makeCard(cardRow, "Current rules (costs socialized)", RATEPAYER);
  const rightCard = makeCard(cardRow, "Cost-causation (direct-assigned)", ACCENT);

  // ── Difference readout ────────────────────────────────────────────────
  const diffRow = container.append("div")
    .style("text-align", "center")
    .style("padding", "0.8rem")
    .style("background", `color-mix(in srgb, ${ACCENT} 8%, transparent)`)
    .style("border-radius", "4px")
    .style("margin-bottom", "0.5rem");

  const diffText = diffRow.append("div")
    .style("font-size", "16px")
    .style("font-weight", 600)
    .style("color", ACCENT);

  const diffSub = diffRow.append("div")
    .style("font-size", "12px")
    .style("color", INK_LIGHT)
    .style("margin-top", "0.2rem");

  // ── Source ────────────────────────────────────────────────────────────
  container.append("div")
    .style("font-size", "9px")
    .style("color", CONTEXT)
    .style("margin-top", "0.8rem")
    .text("Source: Illustrative model based on IURC Cause 46097 parameters; EIA average residential rates");

  // ── Calculation engine ────────────────────────────────────────────────
  function recalc() {
    // Under socialized rules: grid upgrade costs spread across all ratepayers
    // proportional to consumption. Data center load means residential share of
    // grid costs is smaller in absolute terms but the cost per kWh rises.
    const dcShareFrac = dcLoadPct / 100;

    // Grid upgrade cost per kWh for residential (socialized)
    // Total cost = GRID_UPGRADE_ANNUAL_M * 1e6
    // Spread across total system consumption including DC load
    const totalSystemGwh = TOTAL_RESIDENTIAL_GWH / (1 - dcShareFrac);
    const gridCostPerKwh_socialized = (GRID_UPGRADE_ANNUAL_M * 1e6) / (totalSystemGwh * 1e6);

    // Under cost-causation: DC pays its own grid upgrades, residential pays only
    // the residential share
    const residentialGridCost = GRID_UPGRADE_ANNUAL_M * 1e6 * (1 - dcShareFrac * 2); // DC drives disproportionate upgrades
    const gridCostPerKwh_causation = Math.max(0, residentialGridCost / (TOTAL_RESIDENTIAL_GWH * 1e6));

    const monthlySocialized = monthlyKwh * (BASE_RATE_KWH + gridCostPerKwh_socialized);
    const monthlyCausation = monthlyKwh * (BASE_RATE_KWH + gridCostPerKwh_causation);

    const monthlyDiff = monthlySocialized - monthlyCausation;
    const annualDiff = monthlyDiff * 12;

    leftCard.amount.text(`$${monthlySocialized.toFixed(0)}`);
    rightCard.amount.text(`$${monthlyCausation.toFixed(0)}`);

    leftCard.breakdown.html(
      `Base rate: $${(monthlyKwh * BASE_RATE_KWH).toFixed(0)}<br>` +
      `Grid upgrades (your share): $${(monthlyKwh * gridCostPerKwh_socialized).toFixed(0)}<br>` +
      `<span style="color:${INK};">Data centers share the cost pool</span>`
    );

    rightCard.breakdown.html(
      `Base rate: $${(monthlyKwh * BASE_RATE_KWH).toFixed(0)}<br>` +
      `Grid upgrades (your share): $${(monthlyKwh * gridCostPerKwh_causation).toFixed(0)}<br>` +
      `<span style="color:${ACCENT};">Data centers pay their own upgrades</span>`
    );

    if (monthlyDiff > 0.5) {
      diffText.text(`You pay $${annualDiff.toFixed(0)} more per year under current rules`);
      diffSub.text(`$${monthlyDiff.toFixed(0)}/month in grid upgrade costs socialized from data center load`);
    } else {
      diffText.text("Minimal difference at this data center load share");
      diffSub.text("Increase data center load % to see the cost shift");
    }
  }

  recalc();

  return { node: container.node() };
}
