# AGENTS.md - Codex Guide for Systems

## Purpose

This repository studies how AI capital expenditure maps to durable physical
infrastructure (grid equipment, power systems, materials, labor).

Primary references for full context:
- `CLAUDE.md` (project rules, workflow, quality standards)
- `PROJECT_STATUS.md` (auto-generated current status)
- `research-framework.md` (methodology and case-study design)

## Non-Negotiable Rules

- Use `uv` for all Python operations.
- Use Marimo notebooks (`.py` in `notebooks/`), never `.ipynb`.
- Do not edit `PROJECT_STATUS.md` by hand.
- Prefer reusable code in `src/` over copy-paste notebook logic.
- Leave user-existing unrelated git changes untouched.

## Setup

```bash
uv sync
```

## Daily Commands

```bash
# Run tests
uv run pytest

# Lint + format + type checks
uv run ruff check src/ notebooks/ tests/
uv run ruff format src/ notebooks/ tests/
uv run mypy src/

# Run one notebook
uv run marimo run notebooks/dd002_grid_modernization/01_whats_getting_built.py

# Open notebook editor
uv run marimo edit notebooks/dd002_grid_modernization/01_whats_getting_built.py

# Execute active notebooks headlessly
bash scripts/test_notebooks.sh
```

## Project-Specific Workflows

### Regenerate project status
`PROJECT_STATUS.md` is generated from filesystem + `research/deep_dives.csv`:

```bash
uv run python scripts/sync_project_status.py
```

### Notebook validation gate
When changing `src/` or notebook code:
1. `uv run ruff check src/ notebooks/`
2. `bash scripts/test_notebooks.sh`
3. Visually review generated notebook charts where relevant

## Repository Map

- `src/` - reusable Python modules (data, dynamics, plotting, notebook helpers)
- `notebooks/` - Marimo analysis notebooks
- `scripts/` - tooling (`test_notebooks.sh`, `sync_project_status.py`)
- `research/deep_dives.csv` - canonical case-study metadata
- `data/` - local datasets (not committed)

## Codex Session Tracking (HtmlGraph)

If HtmlGraph tracking is needed in this repo:

```bash
$htmlgraph-status
$htmlgraph-feature start <feature-id>
$htmlgraph-session list
```

Use the Codex HtmlGraph skill at:
`/Users/shakes/.codex/skills/codex-skill/SKILL.md`
