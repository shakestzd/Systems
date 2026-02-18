#!/usr/bin/env bash
# deploy.sh — Build the site locally and push to the gh-pages branch.
#
# Usage:
#   bash scripts/deploy.sh
#
# What it does:
#   1. Runs the build (exports all notebooks to _site/)
#   2. Force-pushes _site/ to the gh-pages branch on origin
#   3. GitHub Pages serves gh-pages directly — no CI rebuild needed
#
# The gh-pages branch has no meaningful history (it's always regenerated),
# so --force is intentional.

set -euo pipefail

ROOT=$(git rev-parse --show-toplevel)
cd "$ROOT"

# ---------------------------------------------------------------------------
# 1. Build
# ---------------------------------------------------------------------------
echo "==> Building site..."
uv run python .github/scripts/build.py

# ---------------------------------------------------------------------------
# 2. Capture the source commit for the deploy message
# ---------------------------------------------------------------------------
SOURCE_SHA=$(git rev-parse --short HEAD)
SOURCE_MSG=$(git log -1 --format="%s")
DEPLOY_MSG="Deploy ${SOURCE_SHA}: ${SOURCE_MSG}"

# ---------------------------------------------------------------------------
# 3. Push _site/ → gh-pages branch
# ---------------------------------------------------------------------------
REMOTE=$(git remote get-url origin)

echo ""
echo "==> Pushing to gh-pages..."
(
  cd _site

  # Initialize a throw-away git repo in _site/ each time.
  # gh-pages has no meaningful history — it's always regenerated.
  rm -rf .git
  git init -b gh-pages
  git remote add origin "$REMOTE"
  git add -A
  if git diff --cached --quiet; then
    echo "Nothing changed in _site/ — skipping push."
    exit 0
  fi
  git commit -m "$DEPLOY_MSG"
  git push --force origin gh-pages
)

echo ""
echo "==> Done."
echo "    Site: https://shakes-tzd.github.io/Systems/"
echo "    Source: ${SOURCE_SHA} — ${SOURCE_MSG}"
