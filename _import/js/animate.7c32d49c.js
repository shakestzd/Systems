// ── Scroll-triggered animation — bidirectional, per chart ─────────────────
// Tracks each chart's in/out state. When a chart enters the viewport (in
// either scroll direction) animate() fires. When it exits, reset() fires so
// the next entry starts fresh. This makes every chart responsive to scroll
// in both directions, matching the valuation scrollytelling chart's behavior.
//
// ES module singleton: the scroll listener is added once per page load.

const registry = [];

const checkEntry = (entry) => {
  const r = entry.el.getBoundingClientRect();
  const nowIn = r.bottom > 0 && r.top < window.innerHeight;
  if (nowIn && !entry.inView) {
    entry.inView = true;
    entry.animate();
  } else if (!nowIn && entry.inView) {
    entry.inView = false;
    if (entry.reset) entry.reset();
  }
};

const checkAll = () => { for (const e of registry) checkEntry(e); };
window.addEventListener("scroll", checkAll, { passive: true });

/**
 * Fire `animate` each time `el` enters the viewport; fire `reset` each time
 * it exits, so the next entry starts from the initial state.
 *
 * Call this after the SVG node is inserted (i.e. after display(svg.node())).
 * The requestAnimationFrame delay guarantees display() has completed.
 *
 * @param {Element}  el      — the SVG/DOM element to watch
 * @param {Function} animate — called on every viewport entry
 * @param {Function} [reset] — called on every viewport exit (optional)
 */
export const animateOnEntry = (el, animate, reset) => {
  const entry = { el, animate, reset: reset ?? null, inView: false };
  registry.push(entry);
  // rAF ensures display() has inserted the element into the DOM first
  requestAnimationFrame(() => checkEntry(entry));
};

/**
 * Scan an SVG chart and return CSS position properties that place a callout
 * in the quadrant with the fewest visible data elements.
 */
function pickCalloutPosition(chartEl) {
  const svg = chartEl.querySelector?.("svg") ?? (chartEl.tagName === "svg" ? chartEl : null);
  if (!svg) return { top: "5%", left: "14%" };

  // Collect centroids of visible data elements (circles, rects, diamonds)
  const pts = [];
  svg.querySelectorAll("circle, rect").forEach(el => {
    const fill = el.getAttribute("fill");
    if (fill === "transparent" || fill === "none") return;
    // Skip large invisible hit-target circles
    if (el.tagName === "circle" && +(el.getAttribute("r") ?? 0) > 8) return;

    let cx, cy;
    if (el.tagName === "circle") {
      cx = +el.getAttribute("cx");
      cy = +el.getAttribute("cy");
    } else {
      const w = +el.getAttribute("width"), h = +el.getAttribute("height");
      if (w < 2 || h < 2) return; // decorative hairlines
      cx = +el.getAttribute("x") + w / 2;
      cy = +el.getAttribute("y") + h / 2;
    }
    if (!isNaN(cx) && !isNaN(cy)) pts.push([cx, cy]);
  });

  if (pts.length === 0) return { top: "5%", left: "14%" };

  // Use data bounding box center to split left vs right
  const xs = pts.map(p => p[0]);
  const midX = (Math.min(...xs) + Math.max(...xs)) / 2;

  // Only consider top positions — bottom always has axis labels, legend, source
  let leftCount = 0, rightCount = 0;
  pts.forEach(([cx]) => { if (cx < midX) leftCount++; else rightCount++; });

  return leftCount <= rightCount
    ? { top: "5%", left: "14%" }    // left side emptier
    : { top: "5%", right: "12%" };  // right side emptier
}

/**
 * Wrap a chart in a scroll-driven section with a callout tooltip overlay.
 * The step text appears directly on the chart so the reader's eyes stay in
 * one place. Callout auto-positions in the emptiest quadrant of the chart.
 *
 * @param {Element}  chartEl   — SVG/DOM element returned by the chart
 * @param {Function} updateFn  — called with (stepIndex) on active-step change
 * @param {Array}    steps     — array of { prose: string } objects
 * @param {Object}   [opts]    — options: { callout: "above" } places callout
 *                                above the chart in normal flow (no overlay)
 * @returns {Element} — section container (pass to display())
 */
export function mountScrollChart(chartEl, updateFn, steps, opts = {}) {
  const N = steps.length;
  // On mobile, overlay callouts cover data — promote them to above-chart flow
  const isMobile  = window.innerWidth < 500;
  const above     = opts.callout === "above" || (isMobile && opts.callout !== "none");
  const noCallout = opts.callout === "none";

  // ── Build DOM ──────────────────────────────────────────────────────────────
  const section = document.createElement("div");
  section.className = "msc-section";

  const content = document.createElement("div");
  content.className = "msc-content";

  let callout = null;
  let defaultPos = null;

  if (noCallout) {
    // Inline-annotated charts — no external callout; the chart handles its own labels.
    content.appendChild(chartEl);
  } else if (above) {
    // Flow-positioned callout above the chart — no overlay, no interference
    callout = document.createElement("div");
    callout.textContent = steps[0].prose;
    callout.className = "msc-callout msc-callout-above";
    content.appendChild(callout);
    content.appendChild(chartEl);
  } else {
    // Default: absolutely positioned overlay on the chart
    callout = document.createElement("div");
    callout.textContent = steps[0].prose;
    defaultPos = pickCalloutPosition(chartEl);
    callout.className = "msc-callout";
    Object.assign(callout.style, steps[0].position ?? defaultPos);
    content.appendChild(chartEl);
    content.appendChild(callout);
  }

  section.appendChild(content);

  // ── Scroll tracking ────────────────────────────────────────────────────────
  let activeStep = -1;

  const setActive = (next) => {
    if (next === activeStep) return;
    activeStep = next;
    if (callout) {
      callout.textContent = steps[activeStep].prose;
      if (!above) {
        // Clear all positional + sizing overrides, then apply step-specific or default
        callout.style.top = callout.style.right = callout.style.bottom = callout.style.left = "";
        callout.style.maxWidth = "";
        Object.assign(callout.style, steps[activeStep].position ?? defaultPos);
      }
    }
    updateFn(activeStep);
  };

  const onScroll = () => {
    const r = section.getBoundingClientRect();
    const vh = window.innerHeight;
    const H = r.bottom - r.top;   // actual section height (adapts to callout + chart)
    // startY: r.top value when the section bottom just touches viewport bottom
    //         → the section is fully in view for the first time
    // endY:   r.top value when the section top is 5% from the viewport top
    //         → the section is nearly scrolled off
    const startY = vh - H;
    const endY   = vh * 0.05;
    // Guard: section taller than the usable interaction window (e.g. on mobile
    // landscape where the viewport is shorter than most above-callout sections).
    // Fall back to firing the last step when the section center crosses the
    // viewport center, so at least something happens.
    if (startY <= endY) {
      setActive(r.top < (startY + endY) / 2 ? N - 1 : 0);
      return;
    }
    const progress = (startY - r.top) / (startY - endY);
    if (progress < 0) { setActive(0); return; }
    if (progress >= 1) { setActive(N - 1); return; }
    setActive(Math.min(Math.floor(progress * N), N - 1));
  };

  let listening = false;
  const observer = new IntersectionObserver(entries => {
    const visible = entries[0].isIntersecting;
    if (visible && !listening) {
      listening = true;
      window.addEventListener("scroll", onScroll, { passive: true });
      onScroll();
    } else if (!visible && listening) {
      listening = false;
      window.removeEventListener("scroll", onScroll);
    }
  }, { threshold: 0 });

  requestAnimationFrame(() => observer.observe(section));

  return section;
}
