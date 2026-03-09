// ── Chart: Capex decomposition — construction vs equipment lifetime ──────
// Horizontal bars showing that ~42% of capex creates 20-40 year assets
// while the rest depreciates in under 6 years.
// Steps: 0 = equipment bar draws | 1 = construction bar draws |
//        2 = demand horizon overlay | 3 = lifetime labels

import * as d3 from "npm:d3@7";
import { INK, INK_LIGHT, ACCENT, CONTEXT, RULE } from "../design.js";
import { showTip, moveTip, hideTip } from "../tooltip.js";

export function createCapexDecomp(stats) {
  const totalCapex = Math.round(stats.capex_2025);
  const equipPct = stats.decomp_equip_pct;
  const constPct = stats.decomp_const_pct;
  const equip = totalCapex * equipPct / 100;
  const constr = totalCapex * constPct / 100;
  const equipLife = 6;   // years
  const constLife = 40;  // years

  const W = Math.min(820, (document.body?.clientWidth ?? 820) - 40);
  const isMobile = W < 500;
  const H = 274;
  const ml = 16, mr = 90, mt = 54, mb = 44;

  const x = d3.scaleLinear().domain([2024, 2072]).range([ml, W - mr]);
  const svg = d3.create("svg")
    .attr("width", "100%").attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif");

  // ── Title + subtitle ────────────────────────────────────────────────────
  svg.append("text").attr("x", ml).attr("y", 16)
    .attr("fill", INK).attr("font-size", "13").attr("font-weight", "700")
    .text("Short-lived equipment dominates spending. Long-lived assets bear the cost.");
  svg.append("text").attr("x", ml).attr("y", 30)
    .attr("fill", INK_LIGHT).attr("font-size", "10.5")
    .text("2025 capex by asset class ($B) · bar length = useful life");

  // X axis baseline
  svg.append("line").attr("x1", ml).attr("x2", W - mr)
    .attr("y1", H - mb).attr("y2", H - mb)
    .attr("stroke", RULE).attr("stroke-width", 1);

  // X axis ticks — every 10 years on mobile to avoid crowding
  const tickYears = isMobile
    ? [2025, 2035, 2045, 2055, 2065]
    : [2025, 2030, 2035, 2040, 2045, 2050, 2055, 2060, 2065];
  tickYears.forEach(yr => {
    if (x(yr) > ml && x(yr) < W - mr) {
      svg.append("text").attr("x", x(yr)).attr("y", H - mb + 16)
        .attr("text-anchor", "middle").attr("fill", INK_LIGHT).attr("font-size", "10")
        .text(yr);
    }
  });

  // Bar dimensions
  const barH1 = 46;  // equipment
  const barH2 = 56;  // construction (taller = more capital)
  const y1 = mt + 20;        // equipment bar y
  const y2 = y1 + barH1 + 18; // construction bar y

  // Equipment bar (gray) — starts with 0 width
  const equipBar = svg.append("rect")
    .attr("x", x(2025)).attr("y", y1)
    .attr("width", 0).attr("height", barH1)
    .attr("fill", CONTEXT).attr("rx", 2).attr("opacity", 0.85)
    .style("cursor", "crosshair");
  equipBar
    .on("mouseover", (e) => showTip(e, "Equipment class", `$${equip.toFixed(0)}B`, `~${equipLife} year useful life`, "Servers, GPUs, network gear"))
    .on("mousemove", moveTip)
    .on("mouseout", hideTip);

  // Construction bar (accent) — starts with 0 width
  const constBar = svg.append("rect")
    .attr("x", x(2025)).attr("y", y2)
    .attr("width", 0).attr("height", barH2)
    .attr("fill", ACCENT).attr("rx", 2).attr("opacity", 0.85)
    .style("cursor", "crosshair");
  constBar
    .on("mouseover", (e) => showTip(e, "Construction class", `$${constr.toFixed(0)}B`, "20-40 year useful life", "Substations, shells, transmission"))
    .on("mousemove", moveTip)
    .on("mouseout", hideTip);

  // Inner labels — start hidden
  const equipLabel = svg.append("text")
    .attr("x", x(2025) + (x(2025 + equipLife) - x(2025)) / 2)
    .attr("y", y1 + barH1 / 2 + 5)
    .attr("text-anchor", "middle").attr("fill", INK)
    .attr("font-size", "12").attr("font-weight", "600")
    .attr("opacity", 0).text(`Equipment  $${equip.toFixed(0)}B`);

  const constLabel = svg.append("text")
    .attr("x", x(2025) + (x(2025 + constLife) - x(2025)) / 2)
    .attr("y", y2 + barH2 / 2 + 5)
    .attr("text-anchor", "middle").attr("fill", "white")
    .attr("font-size", "13").attr("font-weight", "600")
    .attr("opacity", 0).text(`Construction  $${constr.toFixed(0)}B`);

  // AI demand horizon overlay — starts hidden
  const horizonRect = svg.append("rect")
    .attr("x", x(2025)).attr("y", mt)
    .attr("width", x(2028) - x(2025))
    .attr("height", H - mt - mb)
    .attr("fill", ACCENT).attr("opacity", 0);
  const horizonLabel = svg.append("text")
    .attr("x", x(2026.5)).attr("y", mt + 12)
    .attr("text-anchor", "center").attr("fill", ACCENT)
    .attr("font-size", "10").attr("opacity", 0)
    .text("AI demand forecast horizon");

  // Equipment end marker
  const equipEndLine = svg.append("line")
    .attr("x1", x(2025 + equipLife)).attr("x2", x(2025 + equipLife))
    .attr("y1", mt).attr("y2", H - mb)
    .attr("stroke", CONTEXT).attr("stroke-width", 1)
    .attr("stroke-dasharray", "4,3").attr("opacity", 0);
  const equipEndLabel = svg.append("text")
    .attr("x", x(2025 + equipLife) + 4).attr("y", y1 - 4)
    .attr("fill", INK_LIGHT).attr("font-size", "10")
    .attr("opacity", 0).text("Equipment fully replaced");

  // Lifetime end labels — start hidden
  const equipLifeLabel = svg.append("text")
    .attr("x", x(2025 + equipLife) + 6).attr("y", y1 + barH1 / 2 + 4)
    .attr("fill", INK_LIGHT).attr("font-size", "12").attr("font-weight", "600")
    .attr("opacity", 0).text(`~${equipLife} yr life`);
  const constLifeLabel = svg.append("text")
    .attr("x", x(2025 + constLife) + 6).attr("y", y2 + barH2 / 2 + 4)
    .attr("fill", ACCENT).attr("font-size", "12").attr("font-weight", "600")
    .attr("opacity", 0).text("20\u201340 yr life");

  // Source
  svg.append("text").attr("x", ml).attr("y", H - 4)
    .attr("fill", CONTEXT).attr("font-size", "9")
    .text("Source: SEC 10-K filings (FY2024 property schedules); SemiAnalysis");

  // ── Step control ──────────────────────────────────────────────────────────
  function update(step) {
    // Step 0: equipment bar draws
    equipBar.interrupt();
    if (step === 0) {
      equipBar.attr("width", 0)
        .transition().delay(200).duration(700).ease(d3.easeQuadOut)
        .attr("width", x(2025 + equipLife) - x(2025));
      equipLabel.transition().delay(600).duration(300).attr("opacity", 1);
    } else {
      equipBar.attr("width", x(2025 + equipLife) - x(2025));
      equipLabel.attr("opacity", 1);
    }

    // Step 1: construction bar draws
    constBar.interrupt();
    if (step >= 1) {
      if (step === 1) {
        constBar.attr("width", 0)
          .transition().delay(200).duration(900).ease(d3.easeQuadOut)
          .attr("width", x(2025 + constLife) - x(2025));
        constLabel.transition().delay(700).duration(300).attr("opacity", 1);
      } else {
        constBar.attr("width", x(2025 + constLife) - x(2025));
        constLabel.attr("opacity", 1);
      }
    } else {
      constBar.attr("width", 0);
      constLabel.attr("opacity", 0);
    }

    // Step 2: demand horizon overlay
    horizonRect.transition().duration(400).attr("opacity", step >= 2 ? 0.06 : 0);
    horizonLabel.transition().duration(400).attr("opacity", step >= 2 ? 0.7 : 0);
    equipEndLine.transition().duration(400).attr("opacity", step >= 2 ? 0.5 : 0);
    equipEndLabel.transition().duration(400).attr("opacity", step >= 2 ? 0.7 : 0);

    // Step 3: lifetime labels
    equipLifeLabel.transition().duration(350).attr("opacity", step >= 3 ? 1 : 0);
    constLifeLabel.transition().duration(350).attr("opacity", step >= 3 ? 1 : 0);
  }

  return { node: svg.node(), update };
}
