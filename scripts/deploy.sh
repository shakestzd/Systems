#!/usr/bin/env bash
# deploy.sh — Build the Observable site and push to the gh-pages branch.
#
# Usage:
#   bash scripts/deploy.sh
#
# What it does:
#   1. Builds the Observable Framework site (observable/dist/)
#   2. Force-pushes dist/ to the gh-pages branch on origin
#   3. GitHub Pages serves gh-pages directly — no CI rebuild needed
#
# The gh-pages branch has no meaningful history (it's always regenerated),
# so --force is intentional.

set -euo pipefail

ROOT=$(git rev-parse --show-toplevel)
cd "$ROOT"

# ---------------------------------------------------------------------------
# 1. Build Observable site
# ---------------------------------------------------------------------------
echo "==> Building Observable site..."
cd observable
npm run build
cd "$ROOT"

DIST_DIR="$ROOT/observable/dist"

if [ ! -d "$DIST_DIR" ]; then
  echo "ERROR: dist/ not found. Build may have failed."
  exit 1
fi

# ---------------------------------------------------------------------------
# 1b. Generate stable articles.json for portfolio cross-site sync
# ---------------------------------------------------------------------------
echo "==> Generating articles.json..."
python3 -c "
import csv, json, pathlib, re

ROOT = pathlib.Path('.')
SRC = ROOT / 'observable' / 'src'
csv_path = ROOT / 'research' / 'deep_dives.csv'

def parse_fm(md):
    m = re.match(r'^---\n(.*?)\n---', md.read_text(), re.DOTALL)
    if not m: return {}
    fm = {}
    for line in m.group(1).splitlines():
        kv = re.match(r'^(\w+):\s*\"?(.+?)\"?\s*$', line)
        if kv: fm[kv.group(1)] = kv.group(2)
    return fm

# Discover published articles from frontmatter
published = {}
for md in sorted(SRC.glob('dd*.md')):
    if not re.match(r'^dd\d{3}$', md.stem): continue
    fm = parse_fm(md)
    if fm.get('id'):
        published[fm['id']] = fm

# Build articles list using CSV for ordering, frontmatter for metadata
articles = []
for row in csv.DictReader(csv_path.open()):
    rid = row['ID']
    if rid in published:
        fm = published[rid]
        articles.append({
            'id': rid,
            'title': fm.get('title', row['Topic']),
            'focus': fm.get('focus', row['Focus Area']),
            'question': fm.get('question', row['Core Question']),
            'status': 'Active',
            'url': '/' + [m.stem for m in SRC.glob('dd*.md') if re.match(r'^dd\d{3}$', m.stem) and parse_fm(m).get('id') == rid][0],
            'updated': row['Last Updated'],
        })

pathlib.Path('$DIST_DIR/articles.json').write_text(json.dumps(articles, indent=2))
print(f'  {len(articles)} published articles written')
"

# ---------------------------------------------------------------------------
# 2. Capture the source commit for the deploy message
# ---------------------------------------------------------------------------
SOURCE_SHA=$(git rev-parse --short HEAD)
SOURCE_MSG=$(git log -1 --format="%s")
DEPLOY_MSG="Deploy ${SOURCE_SHA}: ${SOURCE_MSG}"

# ---------------------------------------------------------------------------
# 3. Push dist/ → gh-pages branch
# ---------------------------------------------------------------------------
REMOTE=$(git remote get-url origin)

echo ""
echo "==> Pushing to gh-pages..."
(
  cd "$DIST_DIR"

  # .nojekyll tells GitHub Pages not to process with Jekyll
  touch .nojekyll

  # Initialize a throw-away git repo in dist/ each time.
  # gh-pages has no meaningful history — it's always regenerated.
  rm -rf .git
  git init -b gh-pages
  git remote add origin "$REMOTE"
  git add -A
  if git diff --cached --quiet; then
    echo "Nothing changed in dist/ — skipping push."
    exit 0
  fi
  git commit -m "$DEPLOY_MSG"
  git push --force origin gh-pages
)

echo ""
echo "==> Done."
echo "    Site: https://shakestzd.github.io/Systems/"
echo "    Source: ${SOURCE_SHA} — ${SOURCE_MSG}"
