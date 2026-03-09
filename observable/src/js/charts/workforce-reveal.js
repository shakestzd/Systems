// ── Chart: Workforce reveal (force-directed unit chart) ─────────────────────
// Opening hook for DD-003. Each dot represents ~1,000 workers.
// Pattern: Custom sticky scrollytelling (like DD-001's valuation.js).
// The scroll-step prose lives in dd003.md; this module wires the chart
// and scroll-sync logic.

import * as d3 from "npm:d3@7";
import { INK, INK_LIGHT, ACCENT, CONTEXT, PAPER, OCC_TECH, OCC_TRADES } from "../design.js";

// ── Occupation buckets ──────────────────────────────────────────────────────
const TECH_OCCS = [
  { label: "Software Developers", count: 150 },
  { label: "Data Scientists & ML Engineers", count: 50 },
  { label: "Network Admins, DB Architects, Other", count: 100 },
];
const TRADES_OCCS = [
  { label: "Electricians", count: 200 },
  { label: "Construction Laborers", count: 150 },
  { label: "Plumbers, HVAC, Pipefitters", count: 100 },
  { label: "Supervisors & Other Trades", count: 50 },
];

/**
 * Mount the workforce reveal scrollytelling chart.
 * @param {Element} container — the #workforce-scroll section element
 */
export function mountWorkforceReveal(container) {
  const stickyEl = container.querySelector(".scroll-hero-chart");
  const steps = [...container.querySelectorAll(".scroll-step")];

  const W = Math.min(680, (document.body?.clientWidth ?? 680) - 40);
  const H = 340;
  const DOT_R = 3.2;
  const DOT_PAD = 0.6;

  // ── Build dots array ────────────────────────────────────────────────────
  const dots = [];
  let techTotal = 0;
  TECH_OCCS.forEach(occ => {
    for (let i = 0; i < occ.count; i++) {
      dots.push({
        id: dots.length,
        group: "tech",
        occ: occ.label,
        step: techTotal === 0 ? 0 : (occ.label.includes("Data") ? 1 : 2),
        x: W / 3 + (Math.random() - 0.5) * 100,
        y: H / 2 + (Math.random() - 0.5) * 100,
      });
      techTotal++;
    }
  });

  TRADES_OCCS.forEach(occ => {
    for (let i = 0; i < occ.count; i++) {
      dots.push({
        id: dots.length,
        group: "trades",
        occ: occ.label,
        step: 4,
        x: W * 2 / 3 + (Math.random() - 0.5) * 100,
        y: H / 2 + (Math.random() - 0.5) * 100,
      });
    }
  });

  // ── SVG ─────────────────────────────────────────────────────────────────
  const svg = d3.create("svg")
    .attr("width", "100%")
    .attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif");

  // Legend labels (hidden initially)
  const techLabel = svg.append("text")
    .attr("x", W / 3).attr("y", 22)
    .attr("text-anchor", "middle").attr("fill", OCC_TECH)
    .attr("font-size", "12").attr("font-weight", "600")
    .attr("opacity", 0).text("Tech / Software");
  const tradesLabel = svg.append("text")
    .attr("x", W * 2 / 3).attr("y", 22)
    .attr("text-anchor", "middle").attr("fill", OCC_TRADES)
    .attr("font-size", "12").attr("font-weight", "600")
    .attr("opacity", 0).text("Construction Trades");

  // Count labels
  const techCount = svg.append("text")
    .attr("x", W / 3).attr("y", H - 10)
    .attr("text-anchor", "middle").attr("fill", OCC_TECH)
    .attr("font-size", "13").attr("font-weight", "700")
    .attr("opacity", 0);
  const tradesCount = svg.append("text")
    .attr("x", W * 2 / 3).attr("y", H - 10)
    .attr("text-anchor", "middle").attr("fill", OCC_TRADES)
    .attr("font-size", "13").attr("font-weight", "700")
    .attr("opacity", 0);

  // Source
  svg.append("text")
    .attr("x", 8).attr("y", H - 4)
    .attr("fill", CONTEXT).attr("font-size", "9")
    .text("Each dot = ~1,000 workers  ·  Source: BLS OES national estimates");

  // Dot elements — all start invisible
  const dotEls = svg.selectAll("circle.dot")
    .data(dots)
    .join("circle")
    .attr("class", "dot")
    .attr("r", 0)
    .attr("cx", d => d.x)
    .attr("cy", d => d.y)
    .attr("fill", d => d.group === "tech" ? OCC_TECH : OCC_TRADES)
    .attr("opacity", 0);

  // ── Force simulation ──────────────────────────────────────────────────
  let currentStep = -1;

  function targetX(d) {
    if (currentStep >= 5) {
      return d.group === "tech" ? W / 3 : W * 2 / 3;
    }
    return W / 2;
  }

  function targetY() {
    return H / 2;
  }

  const sim = d3.forceSimulation(dots)
    .force("x", d3.forceX(d => targetX(d)).strength(0.08))
    .force("y", d3.forceY(d => targetY(d)).strength(0.08))
    .force("collide", d3.forceCollide(DOT_R + DOT_PAD))
    .alphaTarget(0)
    .alphaDecay(0.02)
    .on("tick", () => {
      dotEls.attr("cx", d => d.x).attr("cy", d => d.y);
    });

  sim.stop();

  // ── Step transitions ──────────────────────────────────────────────────
  function setStep(step) {
    if (step === currentStep) return;
    currentStep = step;

    // Which dots are visible at this step
    const visibleDots = step <= 2
      ? dots.filter(d => d.group === "tech" && d.step <= step)
      : step === 3
        ? dots.filter(d => d.group === "tech")
        : dots;

    const visibleIds = new Set(visibleDots.map(d => d.id));

    // Update force targets
    sim.force("x", d3.forceX(d => targetX(d)).strength(step >= 5 ? 0.12 : 0.08));
    sim.alpha(0.6).restart();

    // After convergence, calm down
    setTimeout(() => sim.alphaTarget(0), 2000);

    // Dot visibility and color
    dotEls.transition().duration(400)
      .attr("r", d => visibleIds.has(d.id) ? DOT_R : 0)
      .attr("opacity", d => {
        if (!visibleIds.has(d.id)) return 0;
        // At step 3 (dimming tech), dim tech dots
        if (step === 3 && d.group === "tech") return 0.25;
        return 0.85;
      });

    // Labels
    const showBothLabels = step >= 5;
    const showTechLabel = step <= 2 || showBothLabels;
    const showTradesLabel = step >= 4;

    techLabel.transition().duration(300).attr("opacity", showBothLabels ? 1 : 0);
    tradesLabel.transition().duration(300).attr("opacity", showBothLabels ? 1 : 0);

    // Count labels at final step
    if (step >= 5) {
      const techN = TECH_OCCS.reduce((s, o) => s + o.count, 0);
      const tradesN = TRADES_OCCS.reduce((s, o) => s + o.count, 0);
      techCount.text(`~${techN}K workers`);
      tradesCount.text(`~${tradesN}K workers`);
      techCount.transition().delay(500).duration(400).attr("opacity", 1);
      tradesCount.transition().delay(500).duration(400).attr("opacity", 1);
    } else {
      techCount.transition().duration(200).attr("opacity", 0);
      tradesCount.transition().duration(200).attr("opacity", 0);
    }
  }

  svg.node(); // ensure creation
  stickyEl.appendChild(svg.node());

  // ── Scroll sync ───────────────────────────────────────────────────────
  let lastActive = null;
  const syncSteps = () => {
    const chartBottom = stickyEl.getBoundingClientRect().bottom;
    const viewBottom = window.innerHeight;
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

    if (allAbove) active = steps[steps.length - 1];
    else if (!active) active = lastCandidate || steps[0];

    if (active !== lastActive) {
      lastActive = active;
      steps.forEach(s => s.classList.toggle("is-active", s === active));
      const idx = steps.indexOf(active);
      setStep(idx);
    }
  };

  let rafPending = false;
  window.addEventListener("scroll", () => {
    if (rafPending) return;
    rafPending = true;
    requestAnimationFrame(() => { rafPending = false; syncSteps(); });
  }, { passive: true });

  setStep(0);
  syncSteps();
}
