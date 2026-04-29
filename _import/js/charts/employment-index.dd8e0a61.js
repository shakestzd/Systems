// ── Chart: Employment index (multi-line, indexed to Jan 2020 = 100) ─────────
// Returns { node, update } for use with mountScrollChart.
// Steps: 0 = all lines draw | 1 = pause: ChatGPT marker | 2 = tech highlight |
//        3 = construction highlight

import * as d3 from "../../../_npm/d3@7.9.0/e324157d.js";
import { INK, INK_LIGHT, ACCENT, CONTEXT, RULE, OCC_TECH, chartW } from "../design.2d3db129.js";
import { showTip, moveTip, hideTip } from "../tooltip.40aee997.js";

const SERIES_CONFIG = {
  "Computer Systems Design": { color: ACCENT, lw: 2.5, zorder: 4 },
  "Construction":            { color: OCC_TECH, lw: 2.0, zorder: 3 },
  "Information":             { color: CONTEXT, lw: 1.4, zorder: 2 },
  "Manufacturing":           { color: CONTEXT, lw: 1.4, zorder: 2 },
};

export function createEmploymentIndex(data, stats) {
  const W = chartW(720);
  const H = 334;
  const ml = 42, mr = 24, mt = 52, mb = 44;

  // Group data by series label
  const byLabel = d3.group(data, d => d.label);

  // Scales
  const parseDate = d3.timeParse("%Y-%m-%d");
  const allDates = data.map(d => parseDate(d.date));
  const x = d3.scaleTime()
    .domain(d3.extent(allDates))
    .range([ml, W - mr]);
  const y = d3.scaleLinear()
    .domain([
      d3.min(data, d => d.value) * 0.98,
      d3.max(data, d => d.value) * 1.04
    ])
    .range([H - mb, mt]);

  const lineGen = d3.line()
    .x(d => x(parseDate(d.date)))
    .y(d => y(d.value))
    .curve(d3.curveMonotoneX);

  const svg = d3.create("svg")
    .attr("width", "100%")
    .attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif");

  // ── Title + subtitle ────────────────────────────────────────────────────
  svg.append("text").attr("x", ml).attr("y", 16)
    .attr("fill", INK).attr("font-size", "13").attr("font-weight", "700")
    .text("Tech employment accelerated after 2023. Construction followed.");
  svg.append("text").attr("x", ml).attr("y", 30)
    .attr("fill", INK_LIGHT).attr("font-size", "10.5")
    .text("Employment index, January 2020 = 100 · four sectors, seasonally adjusted");

  // Axis baseline
  svg.append("line")
    .attr("x1", ml).attr("x2", W - mr)
    .attr("y1", H - mb).attr("y2", H - mb)
    .attr("stroke", RULE).attr("stroke-width", 1);

  // Y gridlines
  const yTicks = y.ticks(5);
  yTicks.forEach(v => {
    svg.append("line")
      .attr("x1", ml).attr("x2", W - mr)
      .attr("y1", y(v)).attr("y2", y(v))
      .attr("stroke", RULE).attr("stroke-width", 0.5).attr("opacity", 0.4);
    svg.append("text")
      .attr("x", ml - 6).attr("y", y(v) + 3.5)
      .attr("text-anchor", "end").attr("fill", INK_LIGHT).attr("font-size", "10")
      .text(v === 100 ? "100" : Math.round(v));
  });

  // Baseline = 100 reference
  svg.append("line")
    .attr("x1", ml).attr("x2", W - mr)
    .attr("y1", y(100)).attr("y2", y(100))
    .attr("stroke", CONTEXT).attr("stroke-width", 1).attr("stroke-dasharray", "4,3");

  // ChatGPT/capex marker (Jan 2023)
  const capexDate = new Date(2023, 0, 1);
  const capexMarker = svg.append("g").attr("opacity", 0);
  capexMarker.append("line")
    .attr("x1", x(capexDate)).attr("x2", x(capexDate))
    .attr("y1", mt).attr("y2", H - mb)
    .attr("stroke", INK_LIGHT).attr("stroke-width", 1).attr("stroke-dasharray", "3,3");
  capexMarker.append("text")
    .attr("x", x(capexDate) + 5).attr("y", mt + 12)
    .attr("fill", INK_LIGHT).attr("font-size", "10").text("ChatGPT / AI capex surge");

  // Build series paths and endpoint dots
  const seriesPaths = [];
  const endLabels = [];

  for (const [label, cfg] of Object.entries(SERIES_CONFIG)) {
    const sd = byLabel.get(label);
    if (!sd) continue;
    const sorted = [...sd].sort((a, b) => a.date.localeCompare(b.date));

    const path = svg.append("path").datum(sorted)
      .attr("fill", "none")
      .attr("stroke", cfg.color)
      .attr("stroke-width", cfg.lw)
      .attr("d", lineGen)
      .attr("stroke-dasharray", "0,99999");

    seriesPaths.push({ path, label, color: cfg.color });

    // End dot + label
    const last = sorted[sorted.length - 1];
    const lastDate = parseDate(last.date);
    const endG = svg.append("g").attr("opacity", 0);

    const circ = endG.append("circle")
      .attr("cx", x(lastDate)).attr("cy", y(last.value))
      .attr("r", 3.5).attr("fill", cfg.color);

    // Invisible hit target
    endG.append("circle")
      .attr("cx", x(lastDate)).attr("cy", y(last.value))
      .attr("r", 12).attr("fill", "transparent")
      .style("cursor", "crosshair")
      .on("mouseover", (e) => {
        circ.attr("r", 5);
        showTip(e, label, `Index: ${last.value.toFixed(1)}`, `${last.date}`);
      })
      .on("mousemove", moveTip)
      .on("mouseout", () => { circ.attr("r", 3.5); hideTip(); });

    // Direct end-label for non-CONTEXT series
    if (cfg.color !== CONTEXT) {
      endG.append("text")
        .attr("x", x(lastDate) + 8).attr("y", y(last.value) + 4)
        .attr("fill", cfg.color).attr("font-size", "11").attr("font-weight", "600")
        .text(`${last.value.toFixed(0)}`);
    }

    endLabels.push(endG);
  }

  // X-axis labels
  [2019, 2020, 2021, 2022, 2023, 2024, 2025].forEach(yr => {
    const d = new Date(yr, 0, 1);
    if (x(d) >= ml && x(d) <= W - mr) {
      svg.append("text")
        .attr("x", x(d)).attr("y", H - mb + 16)
        .attr("text-anchor", "middle").attr("fill", INK_LIGHT).attr("font-size", "11")
        .text(yr);
    }
  });

  // Source
  svg.append("text")
    .attr("x", ml).attr("y", H - 4)
    .attr("fill", CONTEXT).attr("font-size", "9")
    .text("Employment index (Jan 2020 = 100)  ·  Source: BLS CES via FRED");

  // ── Step control ──────────────────────────────────────────────────────────
  function animateLines() {
    seriesPaths.forEach(({ path }, i) => {
      path.interrupt()
        .attr("stroke-dasharray", "0,99999")
        .attr("opacity", 1)
        .attr("stroke-width", SERIES_CONFIG[seriesPaths[i].label]?.lw ?? 2);
      path.transition().delay(150 + i * 180).duration(900).ease(d3.easeLinear)
        .attrTween("stroke-dasharray", function () {
          const l = this.getTotalLength();
          return d3.interpolate(`0,${l}`, `${l},${l}`);
        });
    });
  }

  function highlightSeries(targetLabel) {
    seriesPaths.forEach(({ path, label }) => {
      const len = path.node().getTotalLength();
      const isActive = targetLabel === null || label === targetLabel;
      path.attr("stroke-dasharray", `${len},${len}`)
        .transition().duration(300)
        .attr("opacity", isActive ? 1 : 0.15)
        .attr("stroke-width", isActive && targetLabel ? 3 : (SERIES_CONFIG[label]?.lw ?? 1.5));
    });
  }

  function update(step) {
    if (step === 0) {
      // Draw all lines, show endpoint labels
      animateLines();
      capexMarker.transition().duration(300).attr("opacity", 0);
      endLabels.forEach(g => g.transition().delay(700).duration(300).attr("opacity", 1));
    } else if (step === 1) {
      // Show ChatGPT marker, all lines visible but dimmed
      seriesPaths.forEach(({ path }) => {
        const len = path.node().getTotalLength();
        path.attr("stroke-dasharray", `${len},${len}`);
      });
      highlightSeries(null);
      seriesPaths.forEach(({ path }) =>
        path.transition().duration(300).attr("opacity", 0.4));
      capexMarker.transition().duration(400).attr("opacity", 1);
      endLabels.forEach(g => g.transition().duration(200).attr("opacity", 0.4));
    } else if (step === 2) {
      // Highlight Computer Systems Design
      capexMarker.attr("opacity", 1);
      highlightSeries("Computer Systems Design");
      endLabels.forEach((g, i) => {
        const isActive = seriesPaths[i]?.label === "Computer Systems Design";
        g.transition().duration(300).attr("opacity", isActive ? 1 : 0.15);
      });
    } else {
      // step >= 3: Highlight Construction
      capexMarker.attr("opacity", 0.5);
      highlightSeries("Construction");
      endLabels.forEach((g, i) => {
        const isActive = seriesPaths[i]?.label === "Construction";
        g.transition().duration(300).attr("opacity", isActive ? 1 : 0.15);
      });
    }
  }

  return { node: svg.node(), update };
}
