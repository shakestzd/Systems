// ── Date / quarter helpers ────────────────────────────────────────────────

/**
 * Convert a quarter-end date string to a quarter label.
 * @param {string} s — e.g. "2022-03-31"
 * @returns {string} — e.g. "2022-Q1"
 */
export const dateToQ = s => {
  const d = new Date(s + "T00:00:00");
  return `${d.getFullYear()}-Q${Math.floor(d.getMonth() / 3) + 1}`;
};

/**
 * Convert a quarter label to a numeric position for x-axis scaling.
 * @param {string} q — e.g. "2022-Q1"
 * @returns {number} — e.g. 2022.0
 */
export const qNum = q => {
  const [yr, qi] = q.split("-Q");
  return +yr + (+qi - 1) * 0.25;
};
