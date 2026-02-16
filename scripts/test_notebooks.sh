#!/usr/bin/env bash
# Test all active marimo notebooks by exporting them headlessly.
# `marimo export html` executes every cell and exits non-zero on failure.
#
# Usage:
#   uv run bash scripts/test_notebooks.sh           # test all active notebooks
#   uv run bash scripts/test_notebooks.sh notebooks/dd001_capital_reality/01_capex_vs_reality.py  # test one

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Active notebooks — add new notebooks here as they are created.
# Archived notebooks (notebooks/_archive/) are excluded.
NOTEBOOKS=(
    "notebooks/dd001_capital_reality/01_capex_vs_reality.py"
    "notebooks/dd002_grid_modernization/01_whats_getting_built.py"
    "notebooks/dd002_grid_modernization/02_who_benefits.py"
    "notebooks/dd002_grid_modernization/03_feedback_architecture.py"
)

# Allow testing a single notebook by passing it as an argument.
if [[ $# -gt 0 ]]; then
    NOTEBOOKS=("$@")
fi

passed=0
failed=0
failures=()

for nb in "${NOTEBOOKS[@]}"; do
    path="$REPO_ROOT/$nb"
    if [[ ! -f "$path" ]]; then
        echo "SKIP  $nb (file not found)"
        continue
    fi

    printf "TEST  %-60s " "$nb"
    if uv run marimo export html "$path" > /dev/null 2>&1; then
        echo "OK"
        ((passed++))
    else
        echo "FAIL"
        ((failed++))
        failures+=("$nb")
    fi
done

echo ""
echo "Results: $passed passed, $failed failed (${#NOTEBOOKS[@]} total)"

if [[ $failed -gt 0 ]]; then
    echo ""
    echo "Failures:"
    for f in "${failures[@]}"; do
        echo "  - $f"
    done
    exit 1
fi
