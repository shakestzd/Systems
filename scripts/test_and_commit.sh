#!/usr/bin/env bash
# Pre-commit validation: lint, type-check, and test notebooks.
# Run this before committing changes to src/ or notebooks/.
#
# Usage:
#   bash scripts/test_and_commit.sh          # validate only
#   bash scripts/test_and_commit.sh --commit # validate, then commit staged changes
#   bash scripts/test_and_commit.sh --commit -m "message"  # validate + commit with message

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

DO_COMMIT=false
COMMIT_MSG=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --commit) DO_COMMIT=true; shift ;;
        -m) COMMIT_MSG="$2"; shift 2 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

passed=0
failed=0
failures=()

run_step() {
    local name="$1"
    shift
    printf "%-40s " "$name"
    if "$@" > /dev/null 2>&1; then
        echo "OK"
        passed=$((passed + 1))
    else
        echo "FAIL"
        failed=$((failed + 1))
        failures+=("$name")
    fi
}

echo "=== Pre-commit validation ==="
echo ""

# Step 1: Lint
run_step "ruff check src/ notebooks/" uv run ruff check src/ notebooks/

# Step 2: Format check
run_step "ruff format --check src/ notebooks/" uv run ruff format --check src/ notebooks/

# Step 3: Notebook structural check
run_step "marimo check notebooks/" uv run marimo check notebooks/dd001_capital_reality/*.py notebooks/dd002_grid_modernization/*.py

# Step 4: Notebook execution tests
echo ""
echo "--- Notebook execution tests ---"
bash scripts/test_notebooks.sh
notebook_exit=$?
if [[ $notebook_exit -eq 0 ]]; then
    passed=$((passed + 1))
else
    failed=$((failed + 1))
    failures+=("notebook execution")
fi

# Summary
echo ""
echo "=== Summary: $passed passed, $failed failed ==="

if [[ $failed -gt 0 ]]; then
    echo ""
    echo "Failures:"
    for f in "${failures[@]}"; do
        echo "  - $f"
    done
    echo ""
    echo "Fix the above issues before committing."
    exit 1
fi

# Commit if requested
if [[ "$DO_COMMIT" == true ]]; then
    echo ""
    if [[ -z "$COMMIT_MSG" ]]; then
        echo "Error: --commit requires -m \"message\""
        exit 1
    fi
    echo "All checks passed. Committing..."
    git add -A
    git commit -m "$COMMIT_MSG"
    echo "Committed successfully."
else
    echo ""
    echo "All checks passed. Ready to commit."
fi
