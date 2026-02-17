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
    "notebooks/dd001_capital_reality/99_methods_and_sources.py"
    "notebooks/dd002_grid_modernization/01_whats_getting_built.py"
    "notebooks/dd002_grid_modernization/02_who_benefits.py"
    "notebooks/dd002_grid_modernization/99_methods_and_sources.py"
    "notebooks/dd002_grid_modernization/03_feedback_architecture.py"
    "notebooks/dd004_utility_regulation/01_pe_utility_acquisitions.py"
    "notebooks/dd004_utility_regulation/02_data_center_community_impact.py"
    "notebooks/dd004_utility_regulation/03_cost_liability_map.py"
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
        passed=$((passed + 1))
    else
        echo "FAIL"
        failed=$((failed + 1))
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
