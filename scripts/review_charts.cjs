// Visual regression review for Observable Framework charts.
//
// Takes Playwright screenshots at 3 viewport sizes (mobile, tablet, desktop),
// then optionally compares them against a stored baseline using pixel diffing.
//
// Usage:
//   # Save baseline (run once from a known-good state)
//   node scripts/review_charts.cjs http://localhost:3000/dd001 --baseline
//
//   # Compare against baseline (run after changes)
//   node scripts/review_charts.cjs http://localhost:3000/dd001
//
//   # Custom threshold (fraction of pixels; default 0.005 = 0.5%)
//   node scripts/review_charts.cjs http://localhost:3000/dd001 --threshold 0.01
//
//   # Custom output directory
//   node scripts/review_charts.cjs http://localhost:3000/dd001 --out /tmp/my_review
//
// Prerequisites:
//   npm install --prefix /tmp playwright-core pixelmatch pngjs
//
// Environment:
//   CHROMIUM_PATH — path to chromium/chrome-headless-shell binary
//   Falls back to a known local path if unset.
//
// Output:
//   {out}/                     Runtime screenshots
//   {out}/baseline/            Baseline screenshots (--baseline mode)
//   {out}/diff/                Pixel diff images (comparison mode)
//
// Limitations:
//   Scroll-triggered animations (IntersectionObserver) do not fire in headless.
//   Layout, positioning, and text can still be verified.

const { chromium } = require("/tmp/node_modules/playwright-core/index.js");
const { PNG } = require("/tmp/node_modules/pngjs");
const path = require("path");
const fs = require("fs");

// ---------------------------------------------------------------------------
// CLI argument parsing
// ---------------------------------------------------------------------------

const args = process.argv.slice(2);

function flagValue(name, fallback) {
  const idx = args.indexOf(name);
  if (idx === -1) return fallback;
  return args[idx + 1];
}

function hasFlag(name) {
  return args.indexOf(name) !== -1;
}

// First positional arg (not starting with --) is the URL
const positionalArgs = args.filter((a) => !a.startsWith("--"));
const URL = positionalArgs[0] || "http://localhost:3000/dd001";

const SAVE_BASELINE = hasFlag("--baseline");
const THRESHOLD = parseFloat(flagValue("--threshold", "0.005")); // 0.5% default
const OUT = flagValue("--out", "/tmp/chart_review");
const BASELINE_DIR = path.join(OUT, "baseline");
const DIFF_DIR = path.join(OUT, "diff");

const CHROMIUM_PATH =
  process.env.CHROMIUM_PATH ||
  "/Users/shakes/Library/Caches/ms-playwright/chromium_headless_shell-1208" +
    "/chrome-headless-shell-mac-arm64/chrome-headless-shell";

// ---------------------------------------------------------------------------
// Viewport definitions
// ---------------------------------------------------------------------------

const VIEWPORTS = [
  { name: "mobile", width: 390, height: 844 },
  { name: "tablet", width: 768, height: 1024 },
  { name: "desktop", width: 1200, height: 800 },
];

// ---------------------------------------------------------------------------
// PNG helpers
// ---------------------------------------------------------------------------

/** Read a PNG file into { data, width, height }. */
function readPng(filePath) {
  const buf = fs.readFileSync(filePath);
  const png = PNG.sync.read(buf);
  return { data: png.data, width: png.width, height: png.height };
}

/** Write RGBA pixel data to a PNG file. */
function writePng(filePath, data, width, height) {
  const png = new PNG({ width, height });
  png.data = Buffer.from(data.buffer);
  const buf = PNG.sync.write(png);
  fs.writeFileSync(filePath, buf);
}

// ---------------------------------------------------------------------------
// Screenshot capture — reuses the existing section-finding logic
// ---------------------------------------------------------------------------

/**
 * Capture screenshots for all viewports.
 * Returns an array of { name, filePath } for each screenshot taken.
 */
async function captureScreenshots(targetDir) {
  fs.mkdirSync(targetDir, { recursive: true });

  const browser = await chromium.launch({ executablePath: CHROMIUM_PATH });
  const captured = [];

  for (const vp of VIEWPORTS) {
    console.log(`\n── ${vp.name} (${vp.width}x${vp.height}) ──`);
    const page = await browser.newPage({
      viewport: { width: vp.width, height: vp.height },
    });
    await page.goto(URL, { waitUntil: "networkidle" });
    await page.waitForTimeout(2500);

    // Full-page top (orientation shot)
    const topFile = path.join(targetDir, `${vp.name}_00_top.png`);
    await page.screenshot({ path: topFile });
    captured.push({ name: `${vp.name}_00_top`, filePath: topFile });

    // Find chart sections and the valuation scroll-hero
    const sections = await page.evaluate(() => {
      const items = [];
      const hero = document.querySelector(".scroll-hero");
      if (hero) {
        const r = hero.getBoundingClientRect();
        items.push({
          label: "valuation",
          top: Math.round(r.top + window.scrollY),
        });
      }
      document.querySelectorAll(".msc-section").forEach((el, i) => {
        const r = el.getBoundingClientRect();
        items.push({
          label: `chart_${i}`,
          top: Math.round(r.top + window.scrollY),
        });
      });
      return items;
    });

    for (const { label, top } of sections) {
      await page.evaluate(
        (y) => window.scrollTo(0, Math.max(0, y - 20)),
        top
      );
      await page.waitForTimeout(350);
      const fname = path.join(targetDir, `${vp.name}_${label}.png`);
      await page.screenshot({ path: fname });
      captured.push({ name: `${vp.name}_${label}`, filePath: fname });
      console.log(`  ${label} @ scroll=${top}`);
    }

    await page.close();
  }

  await browser.close();
  return captured;
}

// ---------------------------------------------------------------------------
// Pixel comparison
// ---------------------------------------------------------------------------

/**
 * Compare a screenshot against its baseline.
 * Returns { diffCount, totalPixels, pctChanged, diffPath } or null if
 * the baseline file doesn't exist or dimensions mismatch.
 */
async function compareImage(currentPath, baselinePath, diffPath, pixelmatch) {
  if (!fs.existsSync(baselinePath)) {
    return { error: "no baseline", diffCount: 0, totalPixels: 0, pctChanged: 0 };
  }

  const current = readPng(currentPath);
  const baseline = readPng(baselinePath);

  // Dimension mismatch — treat as 100% changed
  if (current.width !== baseline.width || current.height !== baseline.height) {
    return {
      error: `dimension mismatch: current ${current.width}x${current.height} vs baseline ${baseline.width}x${baseline.height}`,
      diffCount: current.width * current.height,
      totalPixels: current.width * current.height,
      pctChanged: 1.0,
    };
  }

  const { width, height } = current;
  const totalPixels = width * height;
  const diffData = new Uint8Array(width * height * 4);

  const diffCount = pixelmatch(
    current.data,
    baseline.data,
    diffData,
    width,
    height,
    {
      threshold: 0.1, // per-pixel color distance threshold (pixelmatch default)
      alpha: 0.1, // opacity of original image in diff
      diffColor: [255, 0, 0], // changed pixels in red
      diffColorAlt: [0, 180, 0], // dark-on-light diffs in green
    }
  );

  // Write diff image only if there are differences
  if (diffCount > 0) {
    writePng(diffPath, diffData, width, height);
  }

  return {
    diffCount,
    totalPixels,
    pctChanged: diffCount / totalPixels,
    diffPath: diffCount > 0 ? diffPath : null,
  };
}

// ---------------------------------------------------------------------------
// Summary formatting
// ---------------------------------------------------------------------------

function formatPct(pct) {
  return (pct * 100).toFixed(3) + "%";
}

function statusIcon(pct, threshold) {
  if (pct === 0) return "  OK ";
  if (pct <= threshold) return " LOW ";
  return " FAIL";
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

(async () => {
  // Dynamic import for ESM-only pixelmatch
  const { default: pixelmatch } = await import("/tmp/node_modules/pixelmatch/index.js");

  if (SAVE_BASELINE) {
    // ── Baseline mode ──────────────────────────────────────────────────
    console.log("MODE: saving baseline screenshots");
    console.log(`URL:  ${URL}`);
    console.log(`DIR:  ${BASELINE_DIR}\n`);

    const captured = await captureScreenshots(BASELINE_DIR);

    console.log(`\nBaseline saved: ${captured.length} screenshots in ${BASELINE_DIR}/`);
    console.log(
      "Run without --baseline to compare future screenshots against this reference."
    );
    process.exit(0);
  }

  // ── Comparison mode ────────────────────────────────────────────────
  console.log("MODE: capture + compare against baseline");
  console.log(`URL:       ${URL}`);
  console.log(`DIR:       ${OUT}`);
  console.log(`BASELINE:  ${BASELINE_DIR}`);
  console.log(`THRESHOLD: ${formatPct(THRESHOLD)}\n`);

  // Check baseline exists
  if (!fs.existsSync(BASELINE_DIR)) {
    console.error(
      `ERROR: No baseline found at ${BASELINE_DIR}\n` +
        "Run with --baseline first to create one:\n" +
        `  node scripts/review_charts.cjs ${URL} --baseline`
    );
    process.exit(1);
  }

  // Capture current screenshots
  const captured = await captureScreenshots(OUT);

  // Prepare diff directory
  fs.mkdirSync(DIFF_DIR, { recursive: true });

  // Compare each screenshot
  console.log("\n══════════════════════════════════════════════════════════");
  console.log("  VISUAL REGRESSION REPORT");
  console.log("══════════════════════════════════════════════════════════\n");

  const results = [];
  let failures = 0;

  for (const { name, filePath } of captured) {
    const baselinePath = path.join(BASELINE_DIR, path.basename(filePath));
    const diffPath = path.join(DIFF_DIR, `diff_${path.basename(filePath)}`);

    const result = await compareImage(filePath, baselinePath, diffPath, pixelmatch);
    result.name = name;
    results.push(result);

    const icon = statusIcon(result.pctChanged, THRESHOLD);
    const pctStr = formatPct(result.pctChanged).padStart(8);

    if (result.error === "no baseline") {
      console.log(`  [NEW ] ${name}  — no baseline to compare`);
    } else if (result.error) {
      console.log(`  [ERR ] ${name}  — ${result.error}`);
      failures++;
    } else if (result.diffCount === 0) {
      console.log(`  [ OK ] ${name}  — identical`);
    } else {
      console.log(
        `  [${icon}] ${name}  — ${result.diffCount.toLocaleString()} px changed (${pctStr})`
      );
      if (result.pctChanged > THRESHOLD) failures++;
    }
  }

  // Summary
  const changed = results.filter((r) => r.diffCount > 0 && !r.error);
  const newScreenshots = results.filter((r) => r.error === "no baseline");
  const errors = results.filter((r) => r.error && r.error !== "no baseline");

  console.log("\n──────────────────────────────────────────────────────────");
  console.log(`  Total:     ${results.length} screenshots`);
  console.log(`  Identical: ${results.length - changed.length - newScreenshots.length - errors.length}`);
  console.log(`  Changed:   ${changed.length}`);
  console.log(`  New:       ${newScreenshots.length}`);
  console.log(`  Errors:    ${errors.length}`);
  console.log(`  Threshold: ${formatPct(THRESHOLD)}`);
  console.log(`  Failures:  ${failures}`);
  console.log("──────────────────────────────────────────────────────────");

  if (changed.length > 0) {
    console.log("\n  Diff images saved to:");
    for (const r of changed) {
      if (r.diffPath) {
        console.log(`    ${r.diffPath}`);
      }
    }
  }

  if (failures > 0) {
    console.log(
      `\nFAILED: ${failures} screenshot(s) exceed the ${formatPct(THRESHOLD)} threshold.`
    );
    console.log("Review the diff images above, then either:");
    console.log("  1. Fix the regression and re-run");
    console.log("  2. Update the baseline: node scripts/review_charts.cjs <url> --baseline");
    process.exit(1);
  } else {
    console.log("\nPASSED: all screenshots within threshold.");
    process.exit(0);
  }
})();
