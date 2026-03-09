// ── Chart: Baseline Simulation (2x2 small multiples) — DD-002 ───────────
// Four panels: Grid vs BTM capacity, Queue backlog, Renewable cost, Spillover.
// Steps: 0 = panel 1 draws | 1 = panel 2 | 2 = panel 3 | 3 = panel 4 (spillover)

import * as d3 from "npm:d3@7";
import { INK, INK_LIGHT, ACCENT, CONTEXT, RULE, LOOP } from "../design.js";
import { showTip, moveTip, hideTip } from "../tooltip.js";

export function createBaselineSim(sim) {
  const data = sim.baseline;

  const W = Math.min(820, (document.body?.clientWidth ?? 820) - 40);
  const H = 514;
  const panels = [
    {
      title: "Capacity (GW)",
      series: [
        { key: "grid_capacity", color: LOOP.R1, label: "Grid" },
        { key: "btm_capacity", color: LOOP.B2, label: "BTM", dash: "6,3" },
      ],
      yDomain: [0, d3.max(data, d => Math.max(d.grid_capacity, d.btm_capacity)) * 1.15],
    },
    {
      title: "Queue Backlog (GW)",
      series: [{ key: "queue_backlog", color: LOOP.B1, label: "Queue" }],
      yDomain: [0, d3.max(data, d => d.queue_backlog) * 1.1],
    },
    {
      title: "Renewable Cost ($/MWh)",
      series: [{ key: "renewable_cost", color: LOOP.R2, label: "LCOE" }],
      yDomain: [0, d3.max(data, d => d.renewable_cost) * 1.15],
    },
    {
      title: "Grid Spillover Index",
      series: [{ key: "spillover", color: LOOP.B3, label: "Spillover" }],
      yDomain: [0, 1],
    },
  ];

  const cols = 2, rows = 2;
  const pw = (W - 60) / cols;
  const ph = (H - 104) / rows;
  const pm = { l: 44, r: 10, t: 22, b: 26 };

  const svg = d3.create("svg").attr("width", "100%").attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif");

  // ── Title + subtitle ────────────────────────────────────────────────────
  svg.append("text").attr("x", 20).attr("y", 16)
    .attr("fill", INK).attr("font-size", "13").attr("font-weight", "700")
    .text("All four feedback loops activate under the baseline: investment rises, then stalls");
  svg.append("text").attr("x", 20).attr("y", 30)
    .attr("fill", INK_LIGHT).attr("font-size", "10.5")
    .text("PySD simulation output · grid capacity, queue backlog, renewable cost, spillover index over time");

  const xDomain = d3.extent(data, d => d.time);
  const xRange = [pm.l, pw - pm.r];

  const panelGroups = panels.map((panel, pi) => {
    const col = pi % cols;
    const row = Math.floor(pi / cols);
    const tx = 20 + col * pw;
    const ty = 44 + row * ph;

    const g = svg.append("g").attr("transform", `translate(${tx},${ty})`);

    const x = d3.scaleLinear().domain(xDomain).range(xRange);
    const y = d3.scaleLinear().domain(panel.yDomain).range([ph - pm.b, pm.t]);

    // Panel title
    g.append("text").attr("x", pm.l).attr("y", pm.t - 6)
      .attr("fill", INK).attr("font-size", "11").attr("font-weight", "600")
      .text(panel.title);

    // Axes
    g.append("line").attr("x1", pm.l).attr("x2", pw - pm.r)
      .attr("y1", ph - pm.b).attr("y2", ph - pm.b).attr("stroke", RULE);

    // X ticks
    const xTicks = x.ticks(4);
    xTicks.forEach(v => {
      g.append("text").attr("x", x(v)).attr("y", ph - pm.b + 12)
        .attr("text-anchor", "middle").attr("fill", INK_LIGHT).attr("font-size", "9")
        .text(v.toFixed(0));
    });

    // Y ticks
    const yTicks = y.ticks(4);
    yTicks.forEach(v => {
      g.append("text").attr("x", pm.l - 4).attr("y", y(v) + 3)
        .attr("text-anchor", "end").attr("fill", INK_LIGHT).attr("font-size", "9")
        .text(panel.yDomain[1] <= 1 ? v.toFixed(1) : v.toFixed(0));
      g.append("line").attr("x1", pm.l).attr("x2", pw - pm.r)
        .attr("y1", y(v)).attr("y2", y(v))
        .attr("stroke", RULE).attr("stroke-width", 0.4).attr("opacity", 0.3);
    });

    // Lines
    const paths = panel.series.map(s => {
      const line = d3.line().x(d => x(d.time)).y(d => y(d[s.key]));
      const p = g.append("path")
        .datum(data).attr("d", line)
        .attr("fill", "none").attr("stroke", s.color).attr("stroke-width", 2)
        .attr("stroke-dasharray", s.dash || "none");

      // Stroke-dasharray animation prep
      const totalLen = p.node().getTotalLength();
      p.attr("stroke-dasharray", `0,${totalLen}`);

      // End value label
      const lastPt = data[data.length - 1];
      const val = lastPt[s.key];
      const label = g.append("text")
        .attr("x", x(lastPt.time) + 4).attr("y", y(val) + 3)
        .attr("fill", s.color).attr("font-size", "10").attr("font-weight", "600")
        .attr("opacity", 0)
        .text(panel.yDomain[1] <= 1 ? val.toFixed(2) : val.toFixed(0));

      return { path: p, label, totalLen, color: s.color, seriesLabel: s.label };
    });

    // Legend inside panel
    panel.series.forEach((s, si) => {
      const lx = pm.l + si * 80;
      g.append("line").attr("x1", lx).attr("x2", lx + 14)
        .attr("y1", ph - pm.b + 22).attr("y2", ph - pm.b + 22)
        .attr("stroke", s.color).attr("stroke-width", 2)
        .attr("stroke-dasharray", s.dash || "none");
      g.append("text").attr("x", lx + 18).attr("y", ph - pm.b + 25)
        .attr("fill", INK_LIGHT).attr("font-size", "9").text(s.label);
    });

    return { paths, panelIndex: pi };
  });

  // Source
  svg.append("text").attr("x", 20).attr("y", H - 3)
    .attr("fill", CONTEXT).attr("font-size", "9")
    .text("Source: PySD simulation; grid_modernization.mdl");

  // ── Step control ────────────────────────────────────────────────────────
  function update(step) {
    panelGroups.forEach(({ paths, panelIndex }) => {
      const active = step >= panelIndex;
      paths.forEach(({ path, label, totalLen }) => {
        if (active) {
          path.transition().duration(1000).ease(d3.easeLinear)
            .attrTween("stroke-dasharray", function() {
              return d3.interpolate(`0,${totalLen}`, `${totalLen},${totalLen}`);
            });
          label.transition().delay(900).duration(300).attr("opacity", 1);
        } else {
          path.attr("stroke-dasharray", `0,${totalLen}`);
          label.attr("opacity", 0);
        }
      });
    });
  }

  return { node: svg.node(), update };
}
