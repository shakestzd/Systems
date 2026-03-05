// ── Chart: Valuation disconnect (scrollytelling) ──────────────────────────
// Pattern B: anchored mount — mounts into a pre-existing container element.
// The scroll-step prose lives in dd001.md; this module wires the chart and
// the scroll-sync logic.

import * as d3 from "../../../_npm/d3@7.9.0/e324157d.js";
import { INK, INK_LIGHT, ACCENT, CONTEXT } from "../design.254ccef8.js";
import { cc, cl } from "../design.254ccef8.js";

/**
 * Mount the valuation disconnect scrollytelling chart.
 * @param {Element} container — #scroll-section element
 * @param {{ mktcap: Array, stats: Object }} data
 */
export function mountValuation(container, { mktcap, stats }) {
  const stickyEl = container.querySelector("#sticky-valuation");
  const steps    = [...container.querySelectorAll(".scroll-step")];

  const sorted = [...mktcap].sort((a, b) => b.gain_t - a.gain_t);
  const total  = sorted.reduce((s, r) => s + r.gain_t, 0);
  const capexT = stats.capex_2025 / 1000;

  const W = 640, H = 160;
  const barH = 40, barY = 56;
  const ML = 8, MR = 80;
  const xSc = d3.scaleLinear().domain([0, total + 1]).range([ML, W - MR]);

  let acc = 0;
  const bars = sorted.map(r => { const b = { ...r, left: acc }; acc += r.gain_t; return b; });

  const svg = d3.create("svg")
    .attr("width", "100%").attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif");

  const draw = (active) => {
    svg.selectAll("*").remove();

    svg.append("text").attr("x", ML).attr("y", 16)
      .attr("fill", INK).attr("font-size", "11.5").attr("font-weight", "600")
      .text("Market cap gain, Jan 2023 → Feb 2026");

    bars.forEach(r => {
      const bx = xSc(r.left);
      const bw = Math.max(xSc(r.left + r.gain_t) - bx - 1, 0);
      const isActive = active === "all" || active === "overview" || r.ticker === active;
      const fillColor = (active === "overview" || !isActive) ? CONTEXT : cc(r.ticker);
      const opacity   = active === "overview" ? 0.55 : isActive ? 1 : 0.3;

      svg.append("rect")
        .attr("x", bx).attr("y", barY).attr("width", bw).attr("height", barH)
        .attr("fill", fillColor).attr("rx", 2).attr("opacity", opacity);

      if (bw >= 36 && isActive && active !== "overview") {
        svg.append("text")
          .attr("x", bx + bw/2).attr("y", barY + barH/2 - 5)
          .attr("text-anchor", "middle").attr("fill", "white")
          .attr("font-size", "10.5").attr("font-weight", "700")
          .text(r.ticker);
        svg.append("text")
          .attr("x", bx + bw/2).attr("y", barY + barH/2 + 8)
          .attr("text-anchor", "middle").attr("fill", "white").attr("font-size", "10.5")
          .text(`+$${r.gain_t.toFixed(1)}T`);
      }
    });

    svg.append("text")
      .attr("x", xSc(total) + 5).attr("y", barY + barH/2 + 4)
      .attr("dominant-baseline", "middle")
      .attr("fill", INK).attr("font-size", "13").attr("font-weight", "700")
      .text(`$${total.toFixed(1)}T`);

    const cx = xSc(capexT);
    const capexOpacity = active === "all" ? 1 : 0.6;
    svg.append("line")
      .attr("x1", cx).attr("x2", cx)
      .attr("y1", barY - 5).attr("y2", barY + barH + 5)
      .attr("stroke", ACCENT).attr("stroke-width", 2.5).attr("opacity", capexOpacity);
    svg.append("text")
      .attr("x", cx + 4).attr("y", barY - 7)
      .attr("fill", ACCENT).attr("font-size", "10.5").attr("font-weight", "700")
      .attr("opacity", capexOpacity)
      .text(`2025 capex: $${stats.capex_2025.toFixed(0)}B`);

    [0, 3, 6, 9, 12].filter(v => v <= total + 0.5).forEach(v => {
      svg.append("text")
        .attr("x", xSc(v)).attr("y", barY + barH + 16)
        .attr("text-anchor", "middle").attr("fill", INK_LIGHT).attr("font-size", "10")
        .text(`$${v}T`);
    });

    svg.append("text")
      .attr("x", ML).attr("y", H - 5)
      .attr("fill", INK_LIGHT).attr("font-size", "9.5")
      .text("Source: Yahoo Finance; SEC 10-K filings");
  };

  draw("NVDA");
  stickyEl.appendChild(svg.node());

  // ── Scroll sync ──────────────────────────────────────────────────────────
  // Activate the topmost step with >12% visible in the reading zone.
  // Fallbacks: allAbove → last step; lastCandidate → partial-visibility step.
  let lastActive = null;
  const syncSteps = () => {
    const chartBottom = stickyEl.getBoundingClientRect().bottom;
    const viewBottom  = window.innerHeight;
    let active = null, allAbove = true, lastCandidate = null;

    for (let i = 0; i < steps.length; i++) {
      const r = steps[i].getBoundingClientRect();
      if (r.bottom <= chartBottom) continue;
      allAbove = false;
      if (r.top > viewBottom) break;
      lastCandidate = steps[i];
      const vis = Math.max(0, Math.min(r.bottom, viewBottom) - Math.max(r.top, chartBottom));
      if (vis / Math.max(r.height, 1) > 0.12) { active = steps[i]; break; }
    }

    if (allAbove)   active = steps[steps.length - 1];
    else if (!active) active = lastCandidate || steps[0];

    if (active !== lastActive) {
      lastActive = active;
      steps.forEach(s => s.classList.toggle("is-active", s === active));
      draw(active.dataset.company);
    }
  };

  let rafPending = false;
  window.addEventListener("scroll", () => {
    if (rafPending) return;
    rafPending = true;
    requestAnimationFrame(() => { rafPending = false; syncSteps(); });
  }, { passive: true });

  syncSteps();
}
