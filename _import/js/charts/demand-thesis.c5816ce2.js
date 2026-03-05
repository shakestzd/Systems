// ── Chart: Six demand theses — risk landscape (2D scatter) ────────────────
// X axis = time to payback. Y axis = revenue certainty.
// Pattern A: returns a container element for Observable's display().

import * as d3 from "../../../_npm/d3@7.9.0/e324157d.js";
import { INK, INK_LIGHT, RULE } from "../design.254ccef8.js";
import { animateOnEntry } from "../animate.48305260.js";

export function createDemandThesis(stats) {
  const near   = { stroke: "#2a7d42", fill: "#e8f5ee", glyph: "●●●", tag: "NEAR-TERM · PROVEN REVENUE"  };
  const medium = { stroke: "#c17a2a", fill: "#fef3e2", glyph: "●●○", tag: "MEDIUM-TERM · SPECULATIVE"   };
  const long_  = { stroke: "#b84c2a", fill: "#fde8e4", glyph: "●○○", tag: "LONG-TERM · NO MODEL YET"    };

  const ga = stats.google_search_ad_rev_qtr_bn ?? 54;
  const cu = stats.chatgpt_monthly_users_m ?? 700;

  const theses = [
    { id: "search",     z: near,   col: 0, row: 0,
      title: "Better search",
      preview: `Justifies current $${ga}B/quarter ad pricing — or disrupts it.`,
      desc: `AI-enhanced search that justifies current ad pricing. Google Search earns $${ga}B per quarter from an engine that AI could improve — or disrupt.` },

    { id: "enterprise", z: near,   col: 0, row: 1,
      title: "Enterprise productivity tools",
      preview: "Copilot converts existing client relationships to AI revenue.",
      desc: "Copilot subscriptions for Microsoft 365 and GitHub. The only product line with a clear conversion path from existing relationships to AI revenue." },

    { id: "agents",     z: medium, col: 1, row: 0,
      title: "AI agents",
      preview: "Autonomous workflows — adoption pace is the key unknown.",
      desc: "Software agents that handle multi-step workflows autonomously. The market size depends on how quickly businesses can retrain workers and redesign processes around AI output." },

    { id: "apps",       z: medium, col: 1, row: 1,
      title: "AI-native consumer apps",
      preview: `${cu}M users, a fraction pay. Conversion is the entire bet.`,
      desc: `ChatGPT has ${cu}M monthly users. Only a fraction pay. Converting free users to paid subscriptions is the largest unvalidated assumption in AI revenue forecasting.` },

    { id: "agi",        z: long_,  col: 2, row: 0,
      title: "AGI / reasoning infrastructure",
      preview: "Revenue model — what to sell, to whom, at what price — unknown.",
      desc: "Infrastructure bets on AI achieving general reasoning capability. The revenue model — what will be sold, to whom, at what price — does not exist yet." },

    { id: "physical",   z: long_,  col: 2, row: 1,
      title: "Physical world automation",
      preview: "Hardware cycles are long; deployment at scale is unproven.",
      desc: "Robotics, autonomous vehicles, industrial AI. Long hardware-software development cycles; the interaction between software progress and physical deployment at scale is untested." },
  ];

  // ── Dimensions ────────────────────────────────────────────────────────
  const W        = Math.min(820, (document.body?.clientWidth ?? 820) - 40);
  const H        = 860;
  const CW       = 180;   // card width (collapsed)
  const CW_EXP   = 300;   // card width (expanded) — height stays CH; horizontal only
  const CH       = 110;   // card height — constant; expansion is width-only
  const CARD_GAP = 12;    // vertical gap between the two cards in each group
  const COL_STEP = 16;    // extra vertical drop between column groups (diagonal step)

  // Column x positions; second card in each group is staggered right by COL_DX
  const COL_X  = [88,  316, 538];
  const COL_DX = [22,  22,  22];

  // Y positions — derived so no two cards ever overlap vertically
  const baseY = 48;
  const ys = (() => {
    const r = [];
    r[0] = baseY;                           // near,   row 0
    r[1] = r[0] + CH + CARD_GAP;            // near,   row 1
    r[2] = r[1] + CH + COL_STEP;            // medium, row 0
    r[3] = r[2] + CH + CARD_GAP;            // medium, row 1
    r[4] = r[3] + CH + COL_STEP;            // long,   row 0
    r[5] = r[4] + CH + CARD_GAP;            // long,   row 1
    return r;
  })();

  const positions = [
    { x: COL_X[0],              y: ys[0] },
    { x: COL_X[0] + COL_DX[0], y: ys[1] },
    { x: COL_X[1],              y: ys[2] },
    { x: COL_X[1] + COL_DX[1], y: ys[3] },
    { x: COL_X[2],              y: ys[4] },
    { x: COL_X[2] + COL_DX[2], y: ys[5] },
  ];
  theses.forEach((d, i) => {
    d.nx = positions[i].x;
    d.ny = positions[i].y;
    d.cx = d.nx + CW / 2;
    d.cy = d.ny + CH / 2;
  });

  // Source node — vertically centered across all cards
  const srcX = 36;
  const srcY = (ys[0] + CH / 2 + ys[5] + CH / 2) / 2;
  const srcR = 42;

  // Pixel-accurate word-wrap using Canvas 2D measurement.
  // Uses Arial as measurement font — available in all browser contexts including headless.
  // DM Sans and Arial have similar x-heights; measurements are within ~5% of each other.
  // Returns array of line strings (max maxLines). Appends "…" on last line if truncated.
  function wrapPx(text, maxPx, fontSize, weight = "400", maxLines = 2) {
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");
    ctx.font = `${weight} ${fontSize}px Arial, sans-serif`;
    const words = text.split(" ");
    const lines = [];
    let cur = "";
    for (const w of words) {
      const test = cur ? `${cur} ${w}` : w;
      if (ctx.measureText(test).width > maxPx && cur) {
        lines.push(cur);
        cur = w;
        if (lines.length >= maxLines) { cur = ""; break; }
      } else {
        cur = test;
      }
    }
    if (lines.length < maxLines && cur) lines.push(cur);
    // If we had to stop early, trim last line to fit with ellipsis
    if (cur && lines.length === maxLines) {
      let last = lines[maxLines - 1];
      while (last.length > 0 && ctx.measureText(last + "…").width > maxPx) last = last.slice(0, -1).trimEnd();
      lines[maxLines - 1] = last + "…";
    }
    return lines;
  }

  // Character-count wrap (used for title only, where font is larger)
  function wrapChars(text, maxChars) {
    const words = text.split(" ");
    const lines = [];
    let cur = "";
    for (const w of words) {
      const test = cur ? `${cur} ${w}` : w;
      if (test.length > maxChars && cur) { lines.push(cur); cur = w; }
      else cur = test;
    }
    if (cur) lines.push(cur);
    return lines.slice(0, 2);
  }

  // ── Container ─────────────────────────────────────────────────────────
  const wrap = document.createElement("div");
  wrap.style.cssText = "font-family:'DM Sans',sans-serif;";

  const svg = d3.select(wrap).append("svg")
    .attr("width", "100%")
    .attr("viewBox", `0 0 ${W} ${H}`)
    .style("display", "block")
    .style("overflow", "visible");

  // Arrowhead marker (used by the vertical certainty axis)
  const defs = svg.append("defs");
  const marker = defs.append("marker")
    .attr("id", "arr-dn").attr("markerWidth", 6).attr("markerHeight", 6)
    .attr("refX", 3).attr("refY", 3).attr("orient", "auto");
  marker.append("path").attr("d", "M0,0 L0,6 L6,3 z").attr("fill", RULE);

  // ── Y axis: certainty labels + arrow ──────────────────────────────────
  ["Proven", "revenue", "model"].forEach((t, i) =>
    svg.append("text").attr("x", 4).attr("y", ys[0] + CH / 2 + i * 11 - 8)
      .attr("fill", near.stroke).attr("font-size", "8.5").attr("font-weight", "700")
      .attr("letter-spacing", "0.04em").text(t));

  ["No", "model", "yet"].forEach((t, i) =>
    svg.append("text").attr("x", 4).attr("y", ys[5] + CH / 2 + i * 11 - 8)
      .attr("fill", long_.stroke).attr("font-size", "8.5").attr("font-weight", "700")
      .attr("letter-spacing", "0.04em").text(t));

  svg.append("line")
    .attr("x1", 12).attr("y1", ys[0] + CH / 2 + 24)
    .attr("x2", 12).attr("y2", ys[5] + CH / 2 - 14)
    .attr("stroke", RULE).attr("stroke-width", 1)
    .attr("marker-end", "url(#arr-dn)");

  // ── X axis: time horizon labels at top ────────────────────────────────
  [
    { x: positions[0].x + CW / 2, label: "NEAR-TERM",   z: near   },
    { x: positions[2].x + CW / 2, label: "MEDIUM-TERM", z: medium },
    { x: positions[4].x + CW / 2, label: "LONG-TERM",   z: long_  },
  ].forEach(({ x, label, z }) => {
    svg.append("text").attr("x", x).attr("y", 18)
      .attr("text-anchor", "middle").attr("fill", z.stroke)
      .attr("font-size", "9").attr("font-weight", "700").attr("letter-spacing", "0.06em")
      .text(label);
    svg.append("line").attr("x1", x).attr("y1", 22).attr("x2", x).attr("y2", 38)
      .attr("stroke", z.stroke).attr("stroke-width", 1).attr("opacity", 0.35)
      .attr("stroke-dasharray", "2,3");
  });

  // ── Zone group labels — above each group's first card ─────────────────
  theses.filter(d => d.row === 0).forEach(d => {
    svg.append("text")
      .attr("x", d.nx).attr("y", d.ny - 8)
      .attr("fill", d.z.stroke).attr("font-size", "8").attr("font-weight", "700")
      .attr("letter-spacing", "0.06em").text(d.z.tag);
  });

  // ── Flow lines: source right edge → each card's left center ───────────
  const flowPaths = [];
  theses.forEach(d => {
    const sx = srcX + srcR, sy = srcY;
    const ex = d.nx,        ey = d.cy;
    const c1x = sx + (ex - sx) * 0.45;
    const p = svg.append("path")
      .attr("d", `M ${sx} ${sy} C ${c1x} ${sy} ${c1x} ${ey} ${ex} ${ey}`)
      .attr("fill", "none")
      .attr("stroke", d.z.stroke).attr("stroke-width", 1.6)
      .attr("opacity", 0.45)
      .attr("stroke-dasharray", "0,9999");
    flowPaths.push(p);
  });

  // ── Source node (drawn after paths so it sits on top) ─────────────────
  const srcG = svg.append("g");
  srcG.append("circle").attr("cx", srcX).attr("cy", srcY).attr("r", srcR).attr("fill", INK);
  srcG.append("text").attr("x", srcX).attr("y", srcY - 14)
    .attr("text-anchor", "middle").attr("fill", "rgba(255,255,255,0.55)")
    .attr("font-size", "7.5").attr("font-weight", "700").attr("letter-spacing", "0.07em")
    .text("ONE POOL");
  srcG.append("text").attr("x", srcX).attr("y", srcY + 4)
    .attr("text-anchor", "middle").attr("fill", "white")
    .attr("font-size", "16").attr("font-weight", "700")
    .text(`$${Math.round(stats.guidance_2026_point ?? 320)}B`);
  srcG.append("text").attr("x", srcX).attr("y", srcY + 18)
    .attr("text-anchor", "middle").attr("fill", "rgba(255,255,255,0.45)")
    .attr("font-size", "8").text("capex 2026");

  // ── Thesis cards ───────────────────────────────────────────────────────
  const allCards = [];

  theses.forEach(d => {
    const g = svg.append("g");

    // Card background
    const bg = g.append("rect")
      .attr("x", d.nx).attr("y", d.ny)
      .attr("width", CW).attr("height", CH).attr("rx", 6)
      .attr("fill", "white")
      .attr("stroke", d.z.stroke).attr("stroke-width", 1.5).attr("stroke-opacity", 0.5);

    // Left accent bar
    const accentBar = g.append("rect")
      .attr("x", d.nx).attr("y", d.ny)
      .attr("width", 4).attr("height", CH).attr("rx", 3)
      .attr("fill", d.z.stroke).attr("opacity", 0.7);

    // Certainty glyph (top-right)
    const glyph = g.append("text")
      .attr("x", d.nx + CW - 8).attr("y", d.ny + 14)
      .attr("text-anchor", "end")
      .attr("fill", d.z.stroke).attr("font-size", "9").attr("letter-spacing", "1px")
      .attr("opacity", 0.8).text(d.z.glyph);

    // Title — word-wrapped by char count (font-size 12.5, ~22 chars/line fits CW=180)
    const titleLines = wrapChars(d.title, 22);
    const tY0 = titleLines.length > 1 ? d.ny + 30 : d.ny + 38;
    titleLines.forEach((ln, li) =>
      g.append("text").attr("x", d.nx + 12).attr("y", tY0 + li * 15)
        .attr("fill", INK).attr("font-size", "12.5").attr("font-weight", "700").text(ln));

    // Preview — pixel-accurate wrap so text never exceeds card width
    const PAD_L = 12, PAD_R = 10;
    const prevMaxPx = CW - PAD_L - PAD_R;
    const titleBottom = tY0 + (titleLines.length - 1) * 15 + 6;
    const prevY0 = Math.max(titleBottom + 14, d.ny + 72);
    const prevLines = wrapPx(d.preview, prevMaxPx, 9.5);
    const prevEls = prevLines.map((ln, li) =>
      g.append("text").attr("x", d.nx + PAD_L).attr("y", prevY0 + li * 14)
        .attr("fill", INK_LIGHT).attr("font-size", "9.5").text(ln));

    // Store descStart for use in expandCard (just below title, no preview gap)
    const descStart = titleBottom + 10;

    // Clamp expanded left edge so right edge never exceeds W (rightmost cards expand leftward)
    const expandX = Math.min(d.nx, W - CW_EXP);

    allCards.push({ d, g, bg, accentBar, glyph, prevEls, descStart, expandX });
  });

  // ── Scroll-driven expand / collapse ────────────────────────────────────
  let activeId = null;

  function collapseAll() {
    activeId = null;
    allCards.forEach(({ d, g, bg, accentBar, glyph, prevEls }) => {
      // Restore bg to collapsed position and size
      bg.transition().duration(220).ease(d3.easeCubicOut)
        .attr("x", d.nx).attr("width", CW).attr("fill", "white").attr("stroke-opacity", 0.5);
      accentBar.transition().duration(220).ease(d3.easeCubicOut).attr("x", d.nx);
      glyph.transition().duration(220).ease(d3.easeCubicOut).attr("x", d.nx + CW - 8);
      // Restore preview text
      prevEls.forEach(el => el.transition().duration(180).attr("opacity", 1));
      // Remove desc overlay
      g.selectAll(".tc-expand").transition().duration(100).attr("opacity", 0).remove();
    });
  }

  function expandCard({ d, g, bg, accentBar, glyph, prevEls, descStart, expandX }) {
    // Move to SVG front for correct z-ordering over adjacent column cards
    svg.node().appendChild(g.node());

    // Expand width; shift left edge if needed so right edge never exceeds W
    bg.transition().duration(260).ease(d3.easeCubicOut)
      .attr("x", expandX).attr("width", CW_EXP)
      .attr("fill", d.z.fill).attr("stroke-opacity", 1);

    accentBar.transition().duration(260).ease(d3.easeCubicOut).attr("x", expandX);

    glyph.transition().duration(260).ease(d3.easeCubicOut).attr("x", expandX + CW_EXP - 8);

    // Fade out preview (desc replaces it in the same vertical space)
    prevEls.forEach(el => el.transition().duration(160).attr("opacity", 0));

    // Desc text — fits within CH; maxLines computed from available space
    // lineH=12 → floor(51px / 12) = 4 lines for 2-line title cards (covers all descs ≤204 chars)
    const descMaxPx = CW_EXP - 24;
    const availPx   = CH - (descStart - d.ny) - 4;   // 4px bottom padding
    const lineH     = 12;
    const maxLines  = Math.max(4, Math.floor(availPx / lineH));
    const descLines = wrapPx(d.desc, descMaxPx, 9.5, "400", maxLines);

    descLines.forEach((ln, li) => {
      g.append("text")
        .attr("class", "tc-expand")
        .attr("x", expandX + 12).attr("y", descStart + li * lineH)
        .attr("fill", INK).attr("font-size", "9.5")
        .text(ln)
        .attr("opacity", 0)
        .transition().delay(140 + li * 16).duration(200).attr("opacity", 1);
    });
  }

  // Determine which card center is closest to the viewport center.
  // Only fires when the SVG is intersecting the viewport (managed by observer below).
  function onScroll() {
    const vCenter = window.scrollY + window.innerHeight / 2;
    const svgEl   = svg.node();
    const svgRect = svgEl.getBoundingClientRect();
    const svgTop  = svgRect.top + window.scrollY;
    const scale   = svgRect.width / W;
    const threshold = window.innerHeight * 0.38;

    let closest = null;
    let closestDist = Infinity;

    allCards.forEach(card => {
      const cardCenterY = svgTop + (card.d.ny + CH / 2) * scale;
      const dist = Math.abs(cardCenterY - vCenter);
      if (dist < threshold && dist < closestDist) {
        closestDist = dist;
        closest = card;
      }
    });

    if (closest && closest.d.id !== activeId) {
      collapseAll();
      activeId = closest.d.id;
      expandCard(closest);
    } else if (!closest && activeId !== null) {
      collapseAll();
    }
  }

  // Start scroll tracking only while SVG is visible; stop and collapse when it leaves.
  let _scrollHandler = null;
  const obs = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        _scrollHandler = onScroll;
        window.addEventListener("scroll", _scrollHandler, { passive: true });
        onScroll();
      } else {
        if (_scrollHandler) {
          window.removeEventListener("scroll", _scrollHandler);
          _scrollHandler = null;
        }
        collapseAll();
      }
    });
  }, { threshold: 0 });
  obs.observe(svg.node());

  // ── Bottom annotations — positioned relative to last card bottom, not H ──
  const lastCardBottom = ys[5] + CH;
  svg.append("text").attr("x", positions[0].x + CW / 2).attr("y", lastCardBottom + 28)
    .attr("fill", INK_LIGHT).attr("font-size", "9.5")
    .text("← shorter time to payback");
  svg.append("text").attr("x", positions[5].x + CW).attr("y", lastCardBottom + 28)
    .attr("text-anchor", "end").attr("fill", INK_LIGHT).attr("font-size", "9.5")
    .text("longer time to payback, higher risk →");

  svg.append("text").attr("x", srcX - srcR).attr("y", lastCardBottom + 48)
    .attr("fill", INK_LIGHT).attr("font-size", "9.5")
    .text("Source: NYT, Metz & Weise, Sep 2025");

  // ── Animation ──────────────────────────────────────────────────────────
  const animate = () => {
    flowPaths.forEach((p, i) =>
      p.transition().delay(120 + i * 90).duration(520).ease(d3.easeQuadOut)
        .attrTween("stroke-dasharray", function() {
          const l = this.getTotalLength();
          return d3.interpolate(`0,${l}`, `${l},${l}`);
        })
    );
  };

  const reset = () => {
    flowPaths.forEach(p => p.interrupt().attr("stroke-dasharray", "0,9999"));
  };

  animateOnEntry(svg.node(), animate, reset);

  return wrap;
}
