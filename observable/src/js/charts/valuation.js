// ── Chart: Valuation disconnect (scrollytelling) ──────────────────────────
// Pattern B: anchored mount — mounts into a pre-existing container element.
// The scroll-step prose lives in dd001.md; this module wires the chart and
// the scroll-lock / step-advance logic.

import * as d3 from "npm:d3@7";
import { INK, INK_LIGHT, ACCENT, CONTEXT } from "../design.js";
import { cc, cl } from "../design.js";

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
  let locked       = false;
  let justUnlocked = false; // suppresses immediate re-lock after unlock nudge
  let wheelAccum   = 0;
  let placeholder  = null;
  const THRESH = 60;

  const lock = () => {
    if (locked || justUnlocked) return;
    locked = true;
    wheelAccum = 0;
    stepIndex  = 0;
    activateStep(0);

    const rect = stickyEl.getBoundingClientRect();

    placeholder = document.createElement("div");
    placeholder.style.cssText = `height:${stickyEl.offsetHeight}px;width:100%;flex-shrink:0;`;
    stickyEl.parentNode.insertBefore(placeholder, stickyEl);

    stickyEl.style.cssText = [
      "position:fixed",
      `top:${rect.top}px`,
      `left:${rect.left}px`,
      `width:${rect.width}px`,
      "z-index:50",
      "background:var(--paper)",
    ].join(";");

    // Freeze page scroll — overflow:hidden on <html> stops all scrolling
    // without touching body layout or causing the sidebar to shift.
    document.documentElement.style.overflow = "hidden";

    window.addEventListener("wheel",      onWheel,      { passive: false });
    window.addEventListener("touchstart", onTouchStart, { passive: true  });
    window.addEventListener("touchmove",  onTouchMove,  { passive: false });
  };

  const unlock = (dir) => {
    if (!locked) return;
    locked = false;

    // Restore page scroll
    document.documentElement.style.overflow = "";

    stickyEl.style.cssText = "";
    if (placeholder) { placeholder.remove(); placeholder = null; }

    window.removeEventListener("wheel",      onWheel);
    window.removeEventListener("touchstart", onTouchStart);
    window.removeEventListener("touchmove",  onTouchMove);
    wheelAccum = 0;

    if (dir === "down") {
      // Suppress re-lock during the nudge scroll
      justUnlocked = true;
      window.scrollBy({ top: 80 });
      requestAnimationFrame(() => { justUnlocked = false; });
    }
  };

  const advance = (delta) => {
    if (delta > 0) {
      if (stepIndex < steps.length - 1) { activateStep(stepIndex + 1); }
      else { unlock("down"); }
    } else {
      if (stepIndex > 0) { activateStep(stepIndex - 1); }
      else { unlock("up"); }
    }
  };

  const onWheel = (e) => {
    e.preventDefault();
    wheelAccum += e.deltaY;
    if (Math.abs(wheelAccum) >= THRESH) {
      advance(wheelAccum);
      wheelAccum = 0;
    }
  };

  let touchY = 0;
  const onTouchStart = (e) => { touchY = e.touches[0].clientY; };
  const onTouchMove  = (e) => {
    e.preventDefault();
    const dy = touchY - e.touches[0].clientY;
    touchY = e.touches[0].clientY;
    wheelAccum += dy;
    if (Math.abs(wheelAccum) >= THRESH) {
      advance(wheelAccum);
      wheelAccum = 0;
    }
  };

  // ── Lock trigger via IntersectionObserver ─────────────────────────────────
  // Fires precisely when the chart center crosses a narrow band at the
  // viewport midpoint — not subject to RAF timing gaps on fast scroll.
  const vpH = window.innerHeight;
  // Detection band: a window centred at 50vh, tall enough to fit the chart.
  // threshold:1 means the entire chart must be inside the band before firing.
  const chartH  = stickyEl.offsetHeight;
  const margin  = Math.max(0, Math.floor((vpH - chartH) / 2) - 10);
  const observer = new IntersectionObserver(
    (entries) => {
      if (entries[0].isIntersecting && !locked && !justUnlocked) lock();
    },
    {
      rootMargin: `-${margin}px 0px -${margin}px 0px`,
      threshold: 1, // full chart must be inside the band
    }
  );
  observer.observe(stickyEl);

  // ── Teardown ──────────────────────────────────────────────────────────────
  // Observable re-runs this cell on hot reload. Return a cleanup function so
  // the caller can pass it to invalidation.then() to remove all listeners
  // before the next run stacks duplicates on top.
  return () => {
    observer.disconnect();
    if (locked) unlock(null);
    // wheel/touch listeners are already removed by unlock; nothing else to clean
  };
}
