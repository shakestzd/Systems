// ── Shared tooltip — singleton DOM element ────────────────────────────────
// ES modules are singletons: the DOM node is created once per page load
// and shared across every chart that imports this module.

import { INK } from "./design.2d3db129.js";

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
/** Compute tooltip position: above cursor normally, below when near the viewport top. */
function _pos(e) {
  const aboveRoom = e.clientY > 60;
  return {
    left: (e.clientX + 14) + "px",
    top:  aboveRoom ? (e.clientY - 36) + "px" : (e.clientY + 16) + "px",
  };
}

export const showTip = (e, label, ...lines) => {
  _tip.textContent = "";
  const b = document.createElement("b");
  b.textContent = label;
  _tip.appendChild(b);
  if (lines.length) {
    _tip.appendChild(document.createTextNode("\n" + lines.join("\n")));
  }
  _tip.style.opacity = "1";
  const p = _pos(e);
  _tip.style.left = p.left;
  _tip.style.top  = p.top;
};

/** Move the tooltip to follow the mouse. */
export const moveTip = (e) => {
  const p = _pos(e);
  _tip.style.left = p.left;
  _tip.style.top  = p.top;
};

/** Hide the tooltip. */
export const hideTip = () => { _tip.style.opacity = "0"; };
