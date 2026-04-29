// ── Chart: Valuation disconnect (scrollytelling) ──────────────────────────
// Pattern B: anchored mount — mounts into a pre-existing container element.
// The scroll-step prose lives in dd001.md; this module wires the chart and
// the scroll-lock / step-advance logic.
//
// Lock mechanism: scroll listener on window detects when the container top
// crosses y=0 (chart is at the viewport top). At that point we freeze the
// page with overflow:hidden and intercept wheel/touch to advance steps.
// No IntersectionObserver, no position:fixed — the chart stays in place
// exactly where the browser put it (overflow:hidden prevents any movement).
//
// State machine:
//   idle → locked (container top crosses 0 while scrolling down)
//   locked → idle via unlock("down"): set completedDown, scrollBy nudge
//   locked → idle via unlock("up"):   scrollBy nudge upward
//   idle: completedDown cleared when container exits viewport in either dir

import * as d3 from "../../../_npm/d3@7.9.0/e324157d.js";
import { INK, INK_LIGHT, ACCENT, CONTEXT } from "../design.2d3db129.js";
import { cc } from "../design.2d3db129.js";

/**
 * Mount the valuation disconnect scrollytelling chart.
 * @param {Element} container — #scroll-section element
 * @param {{ mktcap: Array, stats: Object }} data
 * @returns {Function} teardown — call on invalidation to remove listeners
 */
export function mountValuation(container, { mktcap, stats }) {
  const stickyEl = container.querySelector("#sticky-valuation");
  const steps    = [...container.querySelectorAll(".scroll-step")];

  const sorted = [...mktcap].sort((a, b) => b.gain_t - a.gain_t);
  const total  = sorted.reduce((s, r) => s + r.gain_t, 0);
  const capexT = stats.capex_2025 / 1000;

  const W = 640, H = 134;
  const barH = 40, barY = 32;
  const ML = 8, MR = 80;
  const xSc = d3.scaleLinear().domain([0, total + 1]).range([ML, W - MR]);

  let acc = 0;
  const bars = sorted.map(r => { const b = { ...r, left: acc }; acc += r.gain_t; return b; });

  const svg = d3.create("svg")
    .attr("width", "100%").attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif");

  const draw = (active) => {
    svg.selectAll("*").remove();

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

  // ── Callout above chart ───────────────────────────────────────────────────
  const cloneStep = (step) => {
    const frag = document.createDocumentFragment();
    step.childNodes.forEach(n => frag.appendChild(n.cloneNode(true)));
    return frag;
  };

  const callout = document.createElement("div");
  callout.className = "msc-callout msc-callout-above val-callout";
  callout.appendChild(cloneStep(steps[0]));
  stickyEl.appendChild(callout);

  draw("NVDA");
  stickyEl.appendChild(svg.node());

  container.classList.add("val-callout-mode");

  // ── Step activation ───────────────────────────────────────────────────────
  let stepIndex = 0;

  const activateStep = (i) => {
    stepIndex = i;
    steps.forEach((s, j) => s.classList.toggle("is-active", j === i));
    callout.replaceChildren(cloneStep(steps[i]));
    draw(steps[i].dataset.company);
  };

  activateStep(0);

  // ── Scroll-lock state ─────────────────────────────────────────────────────
  let locked        = false;
  let completedDown = false; // true after user scrolls past all steps going down
  let wheelAccum    = 0;
  const THRESH      = 60;

  const lock = () => {
    if (locked) return;
    locked = true;
    wheelAccum = 0;
    activateStep(0);
    // Freeze page scroll — overflow:hidden on <html> is enough; the chart
    // is already at the viewport top (CSS sticky put it there), so no
    // position:fixed manipulation is needed.
    document.documentElement.style.overflow = "hidden";
    window.addEventListener("wheel",      onWheel,      { passive: false });
    window.addEventListener("touchstart", onTouchStart, { passive: true  });
    window.addEventListener("touchmove",  onTouchMove,  { passive: false });
  };

  const unlock = (dir) => {
    if (!locked) return;
    locked = false;
    document.documentElement.style.overflow = "";
    window.removeEventListener("wheel",      onWheel);
    window.removeEventListener("touchstart", onTouchStart);
    window.removeEventListener("touchmove",  onTouchMove);
    wheelAccum = 0;

    if (dir === "down") {
      // Mark complete BEFORE scrollBy so the scroll event from scrollBy
      // does not immediately re-trigger lock().
      completedDown = true;
      window.scrollBy({ top: 100 });
    } else if (dir === "up") {
      window.scrollBy({ top: -100 });
    }
  };

  const advance = (delta) => {
    if (delta > 0) {
      if (stepIndex < steps.length - 1) activateStep(stepIndex + 1);
      else unlock("down");
    } else {
      if (stepIndex > 0) activateStep(stepIndex - 1);
      else unlock("up");
    }
  };

  const onWheel = (e) => {
    e.preventDefault();
    wheelAccum += e.deltaY;
    if (Math.abs(wheelAccum) >= THRESH) { advance(wheelAccum); wheelAccum = 0; }
  };

  let touchY = 0;
  const onTouchStart = (e) => { touchY = e.touches[0].clientY; };
  const onTouchMove  = (e) => {
    e.preventDefault();
    const dy = touchY - e.touches[0].clientY;
    touchY = e.touches[0].clientY;
    wheelAccum += dy;
    if (Math.abs(wheelAccum) >= THRESH) { advance(wheelAccum); wheelAccum = 0; }
  };

  // ── Scroll-based lock trigger ─────────────────────────────────────────────
  // Fires on every page scroll. Lock when:
  //   • user is scrolling DOWN
  //   • container top has just crossed 0 (chart is at top of viewport)
  //   • container is still partially visible (hasn't scrolled off the top)
  //   • user hasn't already completed this pass going down
  //
  // completedDown resets when the container exits the viewport in either
  // direction, allowing a clean re-entry if the user scrolls back.
  let lastScrollY = window.scrollY;

  const onScrollForLock = () => {
    if (locked) return;

    const scrollY      = window.scrollY;
    const scrollingDown = scrollY >= lastScrollY;
    lastScrollY        = scrollY;

    const r  = container.getBoundingClientRect();
    const vh = window.innerHeight;

    // Reset completion when container has fully exited the viewport
    if (r.top > vh || r.bottom < 0) completedDown = false;

    // Lock: container top at or past viewport top, container still visible
    if (scrollingDown && r.top <= 0 && r.bottom > 50 && !completedDown) {
      lock();
    }
  };

  window.addEventListener("scroll", onScrollForLock, { passive: true });

  // If the page loads already scrolled past this section, mark as complete
  // so the chart doesn't lock when the user scrolls back through it.
  { const r = container.getBoundingClientRect(); if (r.bottom < 0) completedDown = true; }

  // ── Teardown ──────────────────────────────────────────────────────────────
  return () => {
    window.removeEventListener("scroll", onScrollForLock);
    if (locked) unlock(null);
  };
}
