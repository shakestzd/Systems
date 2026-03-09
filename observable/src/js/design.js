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
  NVDA:  "#2b7e87",
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

// Semantic colors — risk/outcome encoding (mirrors Marimo COLORS["positive/negative"])
export const POSITIVE = "#4c8c5c";  // aligned / safe / can exit
export const NEGATIVE = "#c44e52";  // risk-bearing / locked in
export const NEUTRAL  = "#8c8278";  // mechanism / intermediate

// Occupation group colors — DD-003 labor market analysis
export const OCC_TECH   = "#4477AA";   // muted blue — tech/software occupations
export const OCC_TRADES = ACCENT;      // warm accent — construction trades

/** Color by ticker — falls back to INK_LIGHT for unknown tickers */
export const cc = t => CO[t] ?? INK_LIGHT;

/** Display label by ticker — falls back to the ticker string itself */
export const cl = t => LABEL[t] ?? t;

// ── DD-002 tokens: fuel types, ISO regions, feedback loops ──────────────────

/** Fuel type colors — adapted from Marimo FUEL_COLORS for paper background */
export const FUEL = {
  solar:   "#D4943A",
  wind:    "#4477AA",
  battery: "#55BBCC",
  gas_cc:  "#CC6677",
  gas_ct:  "#BB4444",
  nuclear: "#AA3377",
  hydro:   "#228833",
  coal:    "#999999",
};

/** ISO/RTO territory colors — Paul Tol qualitative palette */
export const ISO_COLOR = {
  PJM:    "#4477AA",
  MISO:   "#66CCEE",
  ERCOT:  "#228833",
  CAISO:  "#CCBB44",
  SPP:    "#EE6677",
  NYISO:  "#AA3377",
  "ISO-NE": "#BBBBBB",
  "Non-ISO Southeast": "#CC6677",
  "Non-ISO West": "#999999",
};

/** Feedback loop colors (CLD diagram) */
export const LOOP = {
  R1: "#4477AA",   // Grid Investment Cycle
  R2: "#228833",   // Renewable Learning
  B1: "#CCBB44",   // Regulatory Uncertainty
  B2: "#CC3311",   // BTM Bypass
  B3: "#AA3377",   // Stranded Asset Risk
};

/** Fuel label helper */
export const FUEL_LABEL = {
  solar:   "Solar",
  wind:    "Wind",
  battery: "Battery Storage",
  gas_cc:  "Gas (CC)",
  gas_ct:  "Gas (CT)",
  nuclear: "Nuclear",
  hydro:   "Hydro",
  coal:    "Coal",
};

// ── DD-004 tokens: utility regulation / cost allocation ─────────────────────
export const RATEPAYER = "#8c8279";   // warm gray — ratepayer-held liability
export const PUBLIC    = "#e8c97e";   // warm yellow — public/sunk cost
export const DOM_ZONE  = "#3a6fa8";   // Dominion Virginia zone
export const AEP_ZONE  = ACCENT;     // AEP Indiana zone (same as accent)
