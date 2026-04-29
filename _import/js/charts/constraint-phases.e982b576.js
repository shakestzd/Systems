// ── Chart: Physical constraint phases — horizontal Gantt ─────────────────
// Shows the stacked physical bottlenecks preventing fast conversion of
// capital to operating infrastructure. Grid interconnection is the longest.
// Steps: 0 = bars draw in | 1 = 3-year minimum marker | 2 = all annotations

import * as d3 from "../../../_npm/d3@7.9.0/e324157d.js";
import { INK, INK_LIGHT, ACCENT, CONTEXT, RULE, chartW, isMobile as _isMobile } from "../design.2d3db129.js";
import { showTip, moveTip, hideTip } from "../tooltip.40aee997.js";

const PHASES = [
  { label: "GPU chip order\nto delivery",         start: 0,  end: 18, kind: "locked",
    note: "TSMC CoWoS packaging\nbottleneck (12-18 mo)" },
  { label: "Grid interconnection\nrequest to ops", start: 0,  end: 60, kind: "locked",
    note: "National median: ~5 yrs\n(LBNL Queued Up 2025)" },
  { label: "Transformer\nprocurement",             start: 6,  end: 30, kind: "locked",
    note: "Lead time: 2-3 yrs\n(CS-1 Transformer Mfg)" },
  { label: "Land + permits",                       start: 0,  end: 12, kind: "exit",
    note: "Site selection to\nground-break: 6-12 mo" },
  { label: "DC construction",                      start: 12, end: 30, kind: "exit",
    note: "18-30 mo per building\n(Project Rainier proxy)" },
  { label: "Energization",                          start: 30, end: 36, kind: "locked",
    note: "Final step: utility\nswitchgear install" },
];

export function createConstraintPhases() {
  const n = PHASES.length;
  const W = chartW(820);
  const isMobile = _isMobile(W);
  const H = 354;
  const ml = isMobile ? 100 : 120, mr = 24, mt = 52, mb = isMobile ? 62 : 44;

  const x = d3.scaleLinear().domain([0, 68]).range([ml, W - mr]);
  const rowH = (H - mt - mb) / n;

  const svg = d3.create("svg")
    .attr("width", "100%").attr("viewBox", `0 0 ${W} ${H}`)
    .style("font-family", "'DM Sans', sans-serif");

  // ── Title + subtitle ────────────────────────────────────────────────────
  svg.append("text").attr("x", 8).attr("y", 16)
    .attr("fill", INK).attr("font-size", "13").attr("font-weight", "700")
    .text(isMobile
      ? "Grid connection takes 5 years. Money doesn't help."
      : "Getting connected to the grid takes 5 years. Money does not help.");
  svg.append("text").attr("x", 8).attr("y", 30)
    .attr("fill", INK_LIGHT).attr("font-size", "10.5")
    .text(isMobile
      ? "Physical bottleneck phases (months)"
      : "Physical bottleneck phases from capital commitment to operating infrastructure (months)");

  // X axis
  svg.append("line").attr("x1", ml).attr("x2", W - mr)
    .attr("y1", H - mb).attr("y2", H - mb)
    .attr("stroke", RULE).attr("stroke-width", 1);

  [0, 12, 24, 36, 48, 60].forEach(mo => {
    svg.append("text").attr("x", x(mo)).attr("y", H - mb + 14)
      .attr("text-anchor", "middle").attr("fill", INK_LIGHT).attr("font-size", "10")
      .text(`${mo} mo`);
  });

  // Row labels (always visible) — smaller font on mobile to fit narrower margin
  PHASES.forEach((p, i) => {
    const ry = mt + rowH * i + rowH / 2;
    const lines = p.label.split("\n");
    lines.forEach((line, li) => {
      svg.append("text")
        .attr("x", ml - 8).attr("y", ry + (li - (lines.length - 1) / 2) * (isMobile ? 10 : 12))
        .attr("text-anchor", "end").attr("fill", INK)
        .attr("font-size", isMobile ? "9" : "10.5").text(line);
    });
  });

  // Bars + annotations — built per row
  const barEls = [];
  const noteEls = [];

  PHASES.forEach((p, i) => {
    const ry = mt + rowH * i + rowH / 2;
    const barH = 24;
    const dur = p.end - p.start;
    const color = p.kind === "locked" ? ACCENT : CONTEXT;
    const alpha = p.kind === "locked" ? 0.8 : 0.5;

    // Bar — starts with 0 width
    const bar = svg.append("rect")
      .attr("x", x(p.start)).attr("y", ry - barH / 2)
      .attr("width", 0).attr("height", barH)
      .attr("fill", color).attr("opacity", alpha)
      .attr("rx", 2).style("cursor", "crosshair");
    bar
      .on("mouseover", (e) => showTip(e, p.label.replace("\n", " "), `${dur} months`, p.note.replace("\n", " ")))
      .on("mousemove", moveTip)
      .on("mouseout", hideTip);

    barEls.push({ bar, width: x(p.end) - x(p.start), delay: i * 120 });

    // Note text — positioned inside bar (long) or right of bar (short)
    const shortBar = dur < 12;
    const noteX = shortBar ? x(p.end) + 4 : x(p.start) + (x(p.end) - x(p.start)) / 2;
    const noteAnchor = shortBar ? "start" : "middle";
    const noteColor = shortBar ? INK_LIGHT : (p.kind === "locked" ? "white" : INK);
    const noteLines = p.note.split("\n");

    const noteG = svg.append("g").attr("opacity", 0);
    noteLines.forEach((line, li) => {
      noteG.append("text")
        .attr("x", noteX).attr("y", ry + (li - (noteLines.length - 1) / 2) * 11)
        .attr("text-anchor", noteAnchor).attr("fill", noteColor)
        .attr("font-size", "9").text(line);
    });
    noteEls.push(noteG);
  });

  // 3-year minimum marker — starts hidden
  const minLine = svg.append("line")
    .attr("x1", x(36)).attr("x2", x(36))
    .attr("y1", mt).attr("y2", H - mb)
    .attr("stroke", ACCENT).attr("stroke-width", 1.5)
    .attr("stroke-dasharray", "4,3").attr("opacity", 0);
  const minLabel = svg.append("text")
    .attr("x", x(36) + 4).attr("y", mt + 10)
    .attr("fill", ACCENT).attr("font-size", "10").attr("font-weight", "600")
    .attr("opacity", 0).text("~3-year minimum");

  // Legend — stacked vertically on mobile (horizontal items overflow), side-by-side on desktop
  const legY = H - mb + 30;
  const legItems = [
    { color: ACCENT, alpha: 0.8, text: "Hard constraint (cannot compress)" },
    { color: CONTEXT, alpha: 0.5, text: "Manageable with capital" },
  ];
  if (isMobile) {
    legItems.forEach((l, i) => {
      const ly = legY + i * 16;
      svg.append("rect").attr("x", ml).attr("y", ly - 6)
        .attr("width", 10).attr("height", 10).attr("fill", l.color)
        .attr("opacity", l.alpha).attr("rx", 1);
      svg.append("text").attr("x", ml + 14).attr("y", ly + 3)
        .attr("fill", INK_LIGHT).attr("font-size", "9.5").text(l.text);
    });
  } else {
    legItems.forEach((l, i) => {
      svg.append("rect").attr("x", ml + i * 230).attr("y", legY - 6)
        .attr("width", 10).attr("height", 10).attr("fill", l.color)
        .attr("opacity", l.alpha).attr("rx", 1);
      svg.append("text").attr("x", ml + i * 230 + 14).attr("y", legY + 3)
        .attr("fill", INK_LIGHT).attr("font-size", "10").text(l.text);
    });
  }

  // Source
  svg.append("text").attr("x", ml).attr("y", H - 4)
    .attr("fill", CONTEXT).attr("font-size", "9")
    .text("Source: LBNL Queued Up 2025; industry sources; author\u2019s analysis");

  // ── Step control ──────────────────────────────────────────────────────────
  function update(step) {
    // Step 0: bars draw in
    barEls.forEach(({ bar, width, delay }) => {
      bar.interrupt();
      if (step === 0) {
        bar.attr("width", 0)
          .transition().delay(delay + 200).duration(600).ease(d3.easeQuadOut)
          .attr("width", width);
      } else {
        bar.attr("width", width);
      }
    });

    // Step 1: 3-year minimum marker
    minLine.transition().duration(350).attr("opacity", step >= 1 ? 0.6 : 0);
    minLabel.transition().duration(350).attr("opacity", step >= 1 ? 1 : 0);

    // Step 2: annotations appear
    noteEls.forEach((g, i) => {
      g.transition().delay(step === 2 ? i * 80 : 0).duration(300)
        .attr("opacity", step >= 2 ? 1 : 0);
    });
  }

  return { node: svg.node(), update };
}
