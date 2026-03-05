// ── Shared tooltip — singleton DOM element ────────────────────────────────
// ES modules are singletons: the DOM node is created once per page load
// and shared across every chart that imports this module.

import { INK } from "./design.254ccef8.js";

const _tip = document.createElement("div");
Object.assign(_tip.style, {
  position: "fixed",
  pointerEvents: "none",
  zIndex: "9999",
  background: INK,
  color: "#fff",
  padding: "6px 10px",
  borderRadius: "3px",
  fontSize: "12px",
  lineHeight: "1.5",
  fontFamily: "'DM Sans', sans-serif",
  maxWidth: "220px",
  whiteSpace: "pre-line",
  opacity: "0",
  transition: "opacity 0.12s ease",
  boxShadow: "0 2px 8px rgba(0,0,0,0.18)",
});
document.body.appendChild(_tip);

/**
 * Show the tooltip near the mouse.
 * @param {MouseEvent} e
 * @param {string} label  — bold first line
 * @param {...string} lines — plain subsequent lines
 */
export const showTip = (e, label, ...lines) => {
  _tip.textContent = "";
  const b = document.createElement("b");
  b.textContent = label;
  _tip.appendChild(b);
  if (lines.length) {
    _tip.appendChild(document.createTextNode("\n" + lines.join("\n")));
  }
  _tip.style.opacity = "1";
  _tip.style.left = (e.clientX + 14) + "px";
  _tip.style.top  = (e.clientY - 36) + "px";
};

/** Move the tooltip to follow the mouse. */
export const moveTip = (e) => {
  _tip.style.left = (e.clientX + 14) + "px";
  _tip.style.top  = (e.clientY - 36) + "px";
};

/** Hide the tooltip. */
export const hideTip = () => { _tip.style.opacity = "0"; };
