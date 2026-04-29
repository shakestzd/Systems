// ── Chart: Queue Counters (animated number cards) — DD-002 ──────────────
// Three large numbers that count up from zero on viewport entry.
// Uses animateOnEntry, not mountScrollChart (these are static callout cards).

import * as d3 from "../../../_npm/d3@7.9.0/e324157d.js";
import { INK, INK_LIGHT, ACCENT, RULE, PAPER, CO } from "../design.2d3db129.js";
import { animateOnEntry } from "../animate.7c32d49c.js";

export function createQueueCounters(stats) {
  const cards = [
    {
      value: stats.queue_total_gw,
      suffix: " GW",
      label: `Proposed projects in the queue — ${stats.queue_ratio}x U.S. installed capacity`,
      color: CO.AMZN,
    },
    {
      value: stats.median_years,
      suffix: "+ years",
      label: "Median time from request to commercial operation",
      color: ACCENT,
    },
    {
      value: stats.completion_pct,
      suffix: "%",
      label: "Of projects that enter the queue are ever built",
      color: INK,
    },
  ];

  const container = document.createElement("div");
  container.style.cssText = `
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin: 1.5rem 0;
    font-family: 'DM Sans', sans-serif;
  `;

  const valueEls = [];

  cards.forEach(card => {
    const el = document.createElement("div");
    el.style.cssText = `
      padding: 1.2rem 1rem;
      border-left: 3px solid ${card.color};
      border-radius: 0 3px 3px 0;
      background: rgba(255,255,255,0.5);
    `;

    const num = document.createElement("div");
    num.style.cssText = `
      font-size: 2.4rem;
      font-weight: 700;
      color: ${card.color};
      font-family: 'Cormorant Garamond', Georgia, serif;
      line-height: 1.1;
      margin-bottom: 0.4rem;
    `;
    num.textContent = "0" + card.suffix;

    const desc = document.createElement("div");
    desc.style.cssText = `
      font-size: 13px;
      color: ${INK_LIGHT};
      line-height: 1.5;
    `;
    desc.textContent = card.label;

    el.appendChild(num);
    el.appendChild(desc);
    container.appendChild(el);
    valueEls.push({ el: num, target: card.value, suffix: card.suffix });
  });

  // Responsive: stack on mobile
  const style = document.createElement("style");
  style.textContent = `
    @media (max-width: 640px) {
      .queue-counters-grid { grid-template-columns: 1fr !important; }
    }
  `;
  container.classList.add("queue-counters-grid");
  container.prepend(style);

  // Animate numbers on viewport entry
  function countUp() {
    valueEls.forEach(({ el, target, suffix }) => {
      const duration = 1200;
      const start = performance.now();
      const fmt = target >= 100 ? d3.format(",") : d3.format("");

      function tick(now) {
        const t = Math.min((now - start) / duration, 1);
        const eased = d3.easeQuadOut(t);
        const current = Math.round(eased * target);
        el.textContent = fmt(current) + suffix;
        if (t < 1) requestAnimationFrame(tick);
      }
      requestAnimationFrame(tick);
    });
  }

  function reset() {
    valueEls.forEach(({ el, suffix }) => {
      el.textContent = "0" + suffix;
    });
  }

  requestAnimationFrame(() => animateOnEntry(container, countUp, reset));

  return container;
}
