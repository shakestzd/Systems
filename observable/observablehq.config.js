// TZD Labs · Systems — Observable Framework configuration
import { readFileSync, readdirSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const srcDir = join(__dirname, "src");

// Auto-detect pages from .md files with a `sidebar` frontmatter field.
// Sort: base article (dd001) before its sub-articles (dd001-conversion),
// then by filename. Gallery sorts last.
function sortKey(f) {
  if (f === "gallery.md") return "zzz";
  // "dd001.md" → "dd001.0", "dd001-conversion.md" → "dd001.1-conversion"
  const base = f.replace(".md", "");
  const m = base.match(/^(dd\d+)(-.*)?$/);
  return m ? m[1] + (m[2] ? ".1" + m[2] : ".0") : base;
}

function discoverPages() {
  // In production deploys (DEPLOY=1), only show published articles in sidebar.
  // Local dev shows everything for full navigation during development.
  const isDeploy = process.env.DEPLOY === "1";
  const publishedParents = new Set();
  if (isDeploy) {
    for (const f of readdirSync(srcDir)) {
      if (!/^dd\d{3}\.md$/.test(f)) continue;
      const fm = readFileSync(join(srcDir, f), "utf-8").match(/^---\n([\s\S]*?)\n---/);
      if (fm && /^published:\s*true\s*$/m.test(fm[1])) {
        publishedParents.add(f.replace(".md", ""));
      }
    }
  }

  return readdirSync(srcDir)
    .filter((f) => f.endsWith(".md") && f !== "index.md")
    .sort((a, b) => sortKey(a).localeCompare(sortKey(b)))
    .map((f) => {
      const content = readFileSync(join(srcDir, f), "utf-8");
      const fm = content.match(/^---\n([\s\S]*?)\n---/);
      if (!fm) return null;
      const sidebarMatch = fm[1].match(/^sidebar:\s*["']?(.+?)["']?\s*$/m);
      if (!sidebarMatch) return null;
      const stem = f.replace(".md", "");
      if (isDeploy) {
        const parentMatch = stem.match(/^(dd\d{3})/);
        if (parentMatch && !publishedParents.has(parentMatch[1])) return null;
      }
      return { name: sidebarMatch[1], path: "/" + stem };
    })
    .filter(Boolean);
}

export default {
  root: "src",
  base: "/Systems/",
  // Use the project venv Python so data loaders find all packages
  interpreters: {
    ".py": ["/Users/shakes/DevProjects/Systems/.venv/bin/python3"],
  },
  title: "How Capital Becomes Infrastructure",
  theme: "air",
  toc: false,
  head: `
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,400&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="./style.css">
  `,
  pages: discoverPages(),
  footer: "TZD Labs · Systems Research — Technology Capital in the Physical Economy",
};
