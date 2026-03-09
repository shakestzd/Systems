// Chart visual review across mobile / tablet / desktop screen sizes
// Runs Playwright headless to screenshot every chart section in an Observable article.
//
// Usage:
//   node scripts/review_charts.cjs [url] [output_dir]
//
// Defaults:
//   url         = http://localhost:3000/dd001
//   output_dir  = /tmp/chart_review
//
// Output files: {output_dir}/{viewport}_{label}.png
//   e.g. mobile_chart_0.png, tablet_valuation.png, desktop_chart_3.png
//
// Limitations: scroll-triggered animations (IntersectionObserver) do not fire
//   in headless. Layout, positioning, and text can still be verified.
//
// Prerequisites:
//   - Playwright chromium: node /tmp/node_modules/.bin/playwright install chromium
//   - Observable dev server running: cd observable && npm run dev

const { chromium } = require("/tmp/node_modules/playwright-core/index.js");
const path = require("path");
const fs   = require("fs");

const URL = process.argv[2] || "http://localhost:3000/dd001";
const OUT = process.argv[3] || "/tmp/chart_review";

const CHROMIUM_PATH =
  "/Users/shakes/Library/Caches/ms-playwright/chromium_headless_shell-1208" +
  "/chrome-headless-shell-mac-arm64/chrome-headless-shell";

const VIEWPORTS = [
  { name: "mobile",  width: 390,  height: 844  },
  { name: "tablet",  width: 768,  height: 1024 },
  { name: "desktop", width: 1200, height: 800  },
];

(async () => {
  fs.mkdirSync(OUT, { recursive: true });

  const browser = await chromium.launch({ executablePath: CHROMIUM_PATH });

  for (const vp of VIEWPORTS) {
    console.log(`\n── ${vp.name} (${vp.width}×${vp.height}) ──`);
    const page = await browser.newPage({ viewport: { width: vp.width, height: vp.height } });
    await page.goto(URL, { waitUntil: "networkidle" });
    await page.waitForTimeout(2500);

    // Full-page top (orientation)
    await page.screenshot({ path: `${OUT}/${vp.name}_00_top.png` });

    // Find all chart sections + the valuation scroll-hero
    const sections = await page.evaluate(() => {
      const items = [];
      const hero = document.querySelector(".scroll-hero");
      if (hero) {
        const r = hero.getBoundingClientRect();
        items.push({ label: "valuation", top: Math.round(r.top + window.scrollY) });
      }
      document.querySelectorAll(".msc-section").forEach((el, i) => {
        const r = el.getBoundingClientRect();
        items.push({ label: `chart_${i}`, top: Math.round(r.top + window.scrollY) });
      });
      return items;
    });

    for (const { label, top } of sections) {
      await page.evaluate((y) => window.scrollTo(0, Math.max(0, y - 20)), top);
      await page.waitForTimeout(350);
      await page.screenshot({ path: `${OUT}/${vp.name}_${label}.png` });
      console.log(`  ${label} @ scroll=${top}`);
    }

    await page.close();
  }

  await browser.close();
  console.log(`\nDone — screenshots in ${OUT}/`);
  console.log("Next: use the Read tool to inspect each screenshot before committing.");
})();
