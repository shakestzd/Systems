// review_callouts.mjs — Screenshot every mountScrollChart callout across all articles.
// Usage: node scripts/review_callouts.mjs [article_slug]
//   e.g. node scripts/review_callouts.mjs dd001_risk   (single article)
//        node scripts/review_callouts.mjs              (all articles)
//
// Prerequisites:
//   - Observable dev server running: cd observable && npm run dev
//   - Playwright installed at /tmp/node_modules/@playwright/test
//
// Output: /tmp/callout_review/<article>_<NN>_<heading>.png
//   Screenshots show the chart+callout exactly as rendered, with callout active.

import pkg from "/tmp/node_modules/@playwright/test/index.js";
const { chromium } = pkg;
import { mkdirSync } from "fs";
import path from "path";

// ── Articles ─────────────────────────────────────────────────────────────────
const ALL_ARTICLES = [
  { url: "http://localhost:3000/dd001",            slug: "dd001" },
  { url: "http://localhost:3000/dd001-conversion", slug: "dd001_conversion" },
  { url: "http://localhost:3000/dd001-risk",       slug: "dd001_risk" },
  { url: "http://localhost:3000/dd002",            slug: "dd002" },
  { url: "http://localhost:3000/dd003",            slug: "dd003" },
  { url: "http://localhost:3000/dd004",            slug: "dd004" },
];

const OUT_DIR = "/tmp/callout_review";
mkdirSync(OUT_DIR, { recursive: true });

// Filter to a single article if slug passed as CLI arg
const filterSlug = process.argv[2];
const articles = filterSlug
  ? ALL_ARTICLES.filter(a => a.slug === filterSlug)
  : ALL_ARTICLES;

if (articles.length === 0) {
  console.error(`No article matching "${filterSlug}". Available: ${ALL_ARTICLES.map(a => a.slug).join(", ")}`);
  process.exit(1);
}

// ── Browser ───────────────────────────────────────────────────────────────────
const browser = await chromium.launch({
  executablePath: process.env.PLAYWRIGHT_CHROMIUM_PATH || undefined,
});

for (const article of articles) {
  console.log(`\n── ${article.slug} ──────────────────────────────────────`);
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });

  try {
    await page.goto(article.url, { waitUntil: "networkidle", timeout: 45000 });
    // Let all charts finish rendering (data loaders + D3)
    await page.waitForTimeout(3000);

    // ── Find all scroll chart sections and their nearest heading ─────────────
    const sections = await page.evaluate(() => {
      const els = [...document.querySelectorAll(".msc-section")];
      return els.map((el, i) => {
        // Walk backwards from the section to find the nearest preceding h2/h3
        let heading = `chart_${String(i + 1).padStart(2, "0")}`;
        let node = el.previousElementSibling;
        for (let attempts = 0; attempts < 10 && node; attempts++) {
          if (/^H[23]$/.test(node.tagName)) {
            heading = node.textContent.trim()
              .toLowerCase()
              .replace(/[^a-z0-9]+/g, "_")
              .replace(/^_|_$/g, "")
              .slice(0, 40);
            break;
          }
          node = node.previousElementSibling;
        }
        const hasCallout = !!el.querySelector(".msc-callout");
        const rect = el.getBoundingClientRect();
        return { index: i, heading, hasCallout, top: rect.top + window.scrollY };
      });
    });

    console.log(`  Found ${sections.length} scroll sections`);

    for (const sec of sections) {
      // ── Scroll the msc-content (sticky chart area) into view ───────────────
      await page.evaluate((idx) => {
        const content = document.querySelectorAll(".msc-content")[idx];
        if (content) content.scrollIntoView({ behavior: "instant", block: "center" });
      }, sec.index);

      // Give IntersectionObserver time to fire and attach the scroll listener
      await page.waitForTimeout(600);

      // Manually trigger onScroll so mountScrollChart activates step 0
      await page.evaluate(() => window.dispatchEvent(new Event("scroll")));
      await page.waitForTimeout(500);

      // ── Screenshot the msc-content element (chart + callout, not the tall
      //    scroll-space wrapper) ───────────────────────────────────────────────
      const content = page.locator(".msc-content").nth(sec.index);
      const box = await content.boundingBox();

      if (!box) {
        console.log(`  [skip] ${sec.heading} — element not visible`);
        continue;
      }

      const label = sec.hasCallout ? "" : "_no_callout";
      const filename = `${article.slug}_${String(sec.index + 1).padStart(2, "0")}_${sec.heading}${label}.png`;
      const filepath = path.join(OUT_DIR, filename);

      await content.screenshot({ path: filepath });
      console.log(`  ${sec.hasCallout ? "✓" : "○"} ${filename}`);
    }
  } catch (err) {
    console.error(`  ERROR: ${err.message}`);
  }

  await page.close();
}

await browser.close();
console.log(`\nAll screenshots saved to: ${OUT_DIR}`);
console.log("Review with: open " + OUT_DIR);
