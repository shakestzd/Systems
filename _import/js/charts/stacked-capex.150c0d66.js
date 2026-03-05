// ── Chart: Cumulative capex stacked bar ───────────────────────────────────
// Returns { node, update } for use with mountScrollChart.
// Steps: 0 = all bars grow | 1 = Amazon highlight | 2 = Meta highlight |
//        3 = 2026 uncertainty + totals

import * as d3 from "../../../_npm/d3@7.9.0/e324157d.js";
import { INK, INK_LIGHT, ACCENT, RULE } from "../design.254ccef8.js";
import { cl } from "../design.254ccef8.js";
import { showTip, moveTip, hideTip } from "../tooltip.1f3faffb.js";

export function createStackedCapex(capex, stats) {
  const T6    = ["AMZN", "GOOGL", "MSFT", "META", "ORCL", "NVDA"];
  const YEARS = [2022, 2023, 2024, 2025, 2026];

  const ann = {};
  T6.forEach(t => { ann[t] = {}; });
  capex.annual.filter(d => T6.includes(d.ticker)).forEach(d => { ann[d.ticker][d.year] = d.capex_bn; });
  capex.guidance.filter(d => T6.includes(d.ticker)).forEach(d => { ann[d.ticker][2026] = d.capex_bn; });

  const pivot = T6.map(t => {
    const row = { ticker: t };
    YEARS.forEach(y => { row[y] = ann[t][y] ?? 0; });
    row.total = YEARS.reduce((s, y) => s + row[y], 0);
    return row;
  }).sort((a, b) => b.total - a.total);

  const tickers = pivot.map(r => r.ticker);
  const stack = d3.stack().keys(YEARS)(pivot);

  const W = Math.min(820, (document.body?.clientWidth ?? 820) - 40);
  const H = 320;
  const ml = 50, mr = 20, mt = 20, mb = 65;

  const x = d3.scaleBand().domain(tickers).range([ml, W - mr]).padding(0.3);
  const yMax = d3.max(pivot, r => r.total);
  const y = d3.scaleLinear().domain([0, yMax * 1.14]).range([H - mb, mt]);

  const yearColors = {
    2022: "#c8c2b8", 2023: "#b0aba4",
    2024: "#8a847c", 2025: "#6b6560", 2026: ACCENT,
  };

  const svg = d3.create("svg").attr("width", "100%").attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif");

  svg.append("line").attr("x1", ml).attr("x2", W - mr).attr("y1", H - mb).attr("y2", H - mb)
    .attr("stroke", RULE).attr("stroke-width", 1);

  // Clip path: bars sweep upward from baseline
  const defs = svg.append("defs");
  const cpRect = defs.append("clipPath").attr("id", "cp-stk")
    .append("rect").attr("x", ml).attr("y", H - mb).attr("width", W - ml - mr).attr("height", 0);
  const barsG = svg.append("g").attr("clip-path", "url(#cp-stk)");

  // Track per-company rects for highlighting
  const companyRects = {};
  T6.forEach(t => { companyRects[t] = []; });

  stack.forEach(layer => {
    const yr = layer.key;
    layer.forEach((seg, i) => {
      const ticker = tickers[i];
      const g = barsG.append("g");
      const bx = x(ticker);
      const bw = x.bandwidth();
      const y0 = y(seg[0]), y1 = y(seg[1]);
      const bh = y0 - y1;

      const rect = g.append("rect")
        .attr("x", bx).attr("y", y1).attr("width", bw).attr("height", Math.max(bh, 0))
        .attr("fill", yearColors[yr]).attr("stroke", "white").attr("stroke-width", 0.8);

      companyRects[ticker].push(rect);

      if (yr === 2026) {
        rect.attr("opacity", 0.8);
        const pid = `hatch-${ticker}`;
        const pat = defs.append("pattern").attr("id", pid).attr("width", 6).attr("height", 6)
          .attr("patternUnits", "userSpaceOnUse").attr("patternTransform", "rotate(45)");
        pat.append("line").attr("x1", 0).attr("y1", 0).attr("x2", 0).attr("y2", 6)
          .attr("stroke", "white").attr("stroke-width", 2).attr("opacity", 0.5);
        barsG.append("rect").attr("x", bx).attr("y", y1).attr("width", bw).attr("height", Math.max(bh, 0))
          .attr("fill", `url(#${pid})`);
      }

      const val = (seg[1] - seg[0]).toFixed(0);
      g.style("cursor", "crosshair")
        .on("mouseover", (e) => { rect.attr("opacity", yr === 2026 ? 1 : 0.75); showTip(e, `${cl(ticker)} · ${yr}`, `$${val}B capex`); })
        .on("mousemove", moveTip)
        .on("mouseout",  () => { rect.attr("opacity", yr === 2026 ? 0.8 : 1); hideTip(); });
    });
  });

  // Total labels — start invisible
  const totLabels = [];
  pivot.forEach(r => {
    totLabels.push(
      svg.append("text")
        .attr("x", x(r.ticker) + x.bandwidth()/2).attr("y", y(r.total) - 5)
        .attr("text-anchor", "middle").attr("fill", INK).attr("font-size", "11.5").attr("font-weight", "700")
        .attr("opacity", 0).text(`$${r.total.toFixed(0)}B`)
    );
  });

  // Ticker labels
  tickers.forEach(t => {
    svg.append("text")
      .attr("x", x(t) + x.bandwidth()/2).attr("y", H - mb + 14)
      .attr("text-anchor", "middle").attr("fill", INK_LIGHT).attr("font-size", "12")
      .text(cl(t));
  });

  // Y axis
  [0, 100, 200, 300, 400, 500].filter(v => v <= yMax).forEach(v => {
    svg.append("text").attr("x", ml - 6).attr("y", y(v) + 4)
      .attr("text-anchor", "end").attr("fill", INK_LIGHT).attr("font-size", "11")
      .text(`$${v}B`);
  });

  // Legend
  YEARS.forEach((yr, i) => {
    const lx = ml + i * 74;
    svg.append("rect").attr("x", lx).attr("y", H - 42).attr("width", 12).attr("height", 12)
      .attr("fill", yearColors[yr]).attr("rx", 1).attr("opacity", yr === 2026 ? 0.8 : 1);
    svg.append("text").attr("x", lx + 15).attr("y", H - 31)
      .attr("fill", INK_LIGHT).attr("font-size", "10.5")
      .text(yr === 2026 ? "2026 guidance*" : String(yr));
  });

  svg.append("text").attr("x", ml).attr("y", H - 16)
    .attr("fill", INK_LIGHT).attr("font-size", "9.5")
    .text("*2026 guidance ± " + stats.guidance_band_pct + "% band based on largest single-year revision (2020–2025)");
  svg.append("text").attr("x", ml).attr("y", H - 5)
    .attr("fill", INK_LIGHT).attr("font-size", "9.5")
    .text("Source: SEC 10-K filings via yfinance");

  // ── Step control ──────────────────────────────────────────────────────────
  function setHighlight(focusTicker) {
    // focusTicker = null means all equal opacity
    tickers.forEach(t => {
      const opacity = focusTicker === null || t === focusTicker ? 1 : 0.2;
      companyRects[t].forEach(r =>
        r.transition().duration(300).attr("opacity", opacity));
    });
  }

  function update(step) {
    // Step 0: reset and grow bars
    totLabels.forEach(t => t.interrupt().attr("opacity", 0));

    if (step === 0) {
      cpRect.interrupt().attr("y", H - mb).attr("height", 0);
      setHighlight(null);
      cpRect.transition().delay(200).duration(1300).ease(d3.easeQuadOut)
        .attr("y", mt).attr("height", H - mb - mt);
    } else {
      // Already grown
      cpRect.interrupt().attr("y", mt).attr("height", H - mb - mt);

      if (step === 1) {
        setHighlight("AMZN");
      } else if (step === 2) {
        setHighlight("META");
      } else {
        // step >= 3: all equal, totals appear
        setHighlight(null);
        totLabels.forEach((t, i) =>
          t.transition().delay(i * 70).duration(350).attr("opacity", 1));
      }
    }
  }

  return { node: svg.node(), update };
}
