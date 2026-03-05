// ── Design tokens — single source of truth ────────────────────────────────
// Import from here everywhere. Never declare these values in article files.

export const PAPER     = "#f5f1eb";
export const INK       = "#1a1917";
export const INK_LIGHT = "#6b6560";
export const ACCENT    = "#b84c2a";
export const CONTEXT   = "#b0aba4";
export const RULE      = "#c8c2b8";

// Company color palette — hue-aligned with Marimo COMPANY_COLORS but adapted for
// the paper background (#f5f1eb). Three primary companies use maximally distinct hues:
//   AMZN = orange  (Marimo: #ff9900)
//   GOOGL = green  (Marimo: #34a853) — NOT blue; must match Marimo for cross-chart consistency
//   MSFT = blue    (Marimo: #00a4ef)
export const CO = {
  AMZN:  "#c96b28",
  GOOGL: "#2a7d42",
  MSFT:  "#3a6fa8",
  META:  "#BB5566",
  NVDA:  "#1a6b2a",
  ORCL:  "#CCBB44",
  TSLA:  "#AA3377",
  AAPL:  "#44BB99",
};

export const LABEL = {
  AMZN: "Amazon",
  GOOGL: "Alphabet",
  MSFT: "Microsoft",
  META: "Meta",
  NVDA: "Nvidia",
  ORCL: "Oracle",
  TSLA: "Tesla",
  AAPL: "Apple",
};

/** Color by ticker — falls back to INK_LIGHT for unknown tickers */
export const cc = t => CO[t] ?? INK_LIGHT;

/** Display label by ticker — falls back to the ticker string itself */
export const cl = t => LABEL[t] ?? t;
